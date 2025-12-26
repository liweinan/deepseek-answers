# **# Tokio Waker 注入机制分析**

基于你提供的 `AsyncTimerFuture` 例子，本文档详细分析 tokio 是如何注入 waker 的。

**## 核心流程概览**

```
1\. 调度器调用 task.run()
   ↓
2\. Harness::poll() → poll_inner()
   ↓
3\. 创建 waker_ref → 创建 Context → 调用 poll_future()
   ↓
4\. Core::poll() → future.poll(cx)  ← 这里 cx 包含 waker
   ↓
5\. Future 的 poll() 方法中通过 cx.waker() 获取 waker
```

**## 详细代码流程**

**### 1. 任务调度入口**

当 tokio 调度器决定执行一个任务时，会调用 `task.run()`：

****文件：`tokio/src/runtime/scheduler/multi_thread/worker.rs`****

```rust
fn run_task(&self, task: Notified, mut core: Box<Core>) -> RunResult {
    // ... 省略其他代码 ...
    
    // 运行任务
    task.run();  // ← 这里开始执行任务
    
    // ... 省略其他代码 ...
}
```

**### 2. 任务执行的核心：Harness::poll()**

`task.run()` 最终会调用 `Harness::poll()`：

****文件：`tokio/src/runtime/task/harness.rs` (第 153-177 行)****

```rust
pub(super) fn poll(self) {
    // 将引用计数传递给 poll_inner
    match self.poll_inner() {
        PollFuture::Notified => {
            // 任务返回 Pending，重新调度
            self.core()
                .scheduler
                .yield_now(Notified(self.get_new_task()));
            self.drop_reference();
        }
        PollFuture::Complete => {
            self.complete();
        }
        // ... 其他情况 ...
    }
}
```

**### 3. Waker 创建和注入的关键代码**

****文件：`tokio/src/runtime/task/harness.rs` (第 193-232 行)****

这是****最关键的代码片段****，展示了 waker 的创建和注入：

```rust
fn poll_inner(&self) -> PollFuture {
    use super::state::{TransitionToIdle, TransitionToRunning};

    match self.state().transition_to_running() {
        TransitionToRunning::Success => {
            let header_ptr = self.header_ptr();
            
            // ⭐ 步骤 1：从任务头部创建 waker 引用
            // waker_ref 是一个轻量级的引用，不会增加引用计数
            let waker_ref = waker_ref::<S>(&header_ptr);
            
            // ⭐ 步骤 2：从 waker 创建 Context
            // Context::from_waker() 将 waker 包装成 Context
            let cx = Context::from_waker(&waker_ref);
            
            // ⭐ 步骤 3：使用 Context 调用 poll_future
            // 这个 Context 会被传递给 future 的 poll() 方法
            let res = poll_future(self.core(), cx);

            if res == Poll::Ready(()) {
                return PollFuture::Complete;
            }

            let transition_res = self.state().transition_to_idle();
            // ... 处理状态转换 ...
        }
        // ... 其他情况 ...
    }
}
```

**### 4. Waker 引用的创建**

****文件：`tokio/src/runtime/task/waker.rs` (第 16-34 行)****

```rust
/// 返回一个 WakerRef，避免不必要地增加引用计数
pub(super) fn waker_ref<S>(header: &NonNull<Header>) -> WakerRef<'_, S>
where
    S: Schedule,
{
    // 从任务的 Header 创建一个 RawWaker
    // 这个 waker 指向任务本身，当调用 wake() 时会唤醒这个任务
    let waker = unsafe { ManuallyDrop::new(Waker::from_raw(raw_waker(*header))) };

    WakerRef {
        waker,
        _p: PhantomData,
    }
}
```

****文件：`tokio/src/runtime/task/waker.rs` (第 121-124 行)****

```rust
fn raw_waker(header: NonNull<Header>) -> RawWaker {
    let ptr = header.as_ptr() as *const ();
    // 创建 RawWaker，包含指向任务头部的指针和 vtable
    RawWaker::new(ptr, &WAKER_VTABLE)
}
```

**### 5. 调用 Future 的 poll 方法**

****文件：`tokio/src/runtime/task/harness.rs` (第 519-557 行)****

```rust
/// 轮询 future。如果 future 完成，输出会被写入 stage 字段。
fn poll_future<T: Future, S: Schedule>(core: &Core<T, S>, cx: Context<'_>) -> Poll<()> {
    // 轮询 future
    let output = panic::catch_unwind(panic::AssertUnwindSafe(|| {
        // ... 省略 guard 代码 ...
        
        // ⭐ 这里调用 Core::poll()，传入 Context
        let res = guard.core.poll(cx);
        // ... 省略其他代码 ...
        res
    }));

    // ... 处理结果 ...
}
```

****文件：`tokio/src/runtime/task/core.rs` (第 361-383 行)****

```rust
pub(super) fn poll(&self, mut cx: Context<'_>) -> Poll<T::Output> {
    let res = {
        self.stage.stage.with_mut(|ptr| {
            // 获取 future
            let future = match unsafe { &mut *ptr } {
                Stage::Running(future) => future,
                _ => unreachable!("unexpected stage"),
            };

            // 将 future 固定（pin）
            let future = unsafe { Pin::new_unchecked(future) };

            let _guard = TaskIdGuard::enter(self.task_id);
            
            // ⭐ 最终调用 future 的 poll() 方法
            // 此时 cx 包含 waker，future 可以通过 cx.waker() 获取
            future.poll(&mut cx)
        })
    };

    if res.is_ready() {
        self.drop_future_or_output();
    }

    res
}
```

**## 与你的例子的对应关系**

在你的 `AsyncTimerFuture` 例子中：

```rust
fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
    let mut state = self.shared_state.lock().unwrap();
    
    if state.completed {
        Poll::Ready("异步操作完成！")
    } else {
        // ⭐ 这里：从 Context 中获取 waker 并保存
        // 这个 cx 就是 tokio 通过上面的流程注入的
        state.waker = Some(cx.waker().clone());
        Poll::Pending
    }
}
```

****对应关系：****

1\. ****tokio 的 `Harness::poll_inner()`**** 创建了 `Context`（包含 waker）
2\. ****tokio 的 `Core::poll()`**** 调用 `future.poll(&mut cx)`
3\. ****你的 `AsyncTimerFuture::poll()`**** 通过 `cx.waker()` 获取 waker 并保存
4\. ****后台线程**** 调用 `waker.wake()` 时，会触发 tokio 重新调度任务

**## Waker 的唤醒机制**

当你的代码调用 `waker.wake()` 时，会触发以下流程：

****文件：`tokio/src/runtime/task/waker.rs` (第 93-103 行)****

```rust
unsafe fn wake_by_val(ptr: *const ()) {
    // 从指针恢复 Header
    let ptr = unsafe { NonNull::new_unchecked(ptr as *mut Header) };
    
    // 转换为 RawTask
    let raw = unsafe { RawTask::from_raw(ptr) };
    
    // ⭐ 唤醒任务：将任务重新加入调度队列
    raw.wake_by_val();
}
```

****文件：`tokio/src/runtime/task/harness.rs` (第 68-91 行)****

```rust
pub(super) fn wake_by_val(&self) {
    use super::state::TransitionToNotifiedByVal;

    match self.state().transition_to_notified_by_val() {
        TransitionToNotifiedByVal::Submit => {
            // ⭐ 将任务提交到调度器
            // 调度器会在下次循环时重新 poll 这个任务
            self.schedule();
            self.drop_reference();
        }
        // ... 其他情况 ...
    }
}
```

**## 关键点总结**

1\. ****Waker 创建时机****：每次 `poll()` 调用时，tokio 都会创建一个新的 `waker_ref`，然后包装成 `Context`
2\. ****Waker 来源****：Waker 指向任务本身（通过 `Header` 指针），调用 `wake()` 会重新调度该任务
3\. ****Context 传递****：通过调用链 `Harness::poll_inner()` → `poll_future()` → `Core::poll()` → `future.poll(cx)` 传递
4\. ****每次 poll 都更新****：你的代码中每次 `poll()` 都更新 `waker` 是正确的做法，因为任务可能在不同线程间移动
5\. ****轻量级设计****：`waker_ref` 使用 `ManuallyDrop` 避免不必要的引用计数操作

**## 完整调用链**

```
调度器 (worker.rs)
  ↓ task.run()
Harness::poll() (harness.rs:153)
  ↓ poll_inner()
Harness::poll_inner() (harness.rs:193)
  ↓ waker_ref::<S>(&header_ptr)  ← 创建 waker 引用
  ↓ Context::from_waker(&waker_ref)  ← 创建 Context
  ↓ poll_future(core, cx)
poll_future() (harness.rs:521)
  ↓ core.poll(cx)
Core::poll() (core.rs:361)
  ↓ future.poll(&mut cx)  ← 你的 Future 在这里获取 waker
AsyncTimerFuture::poll() (你的代码)
  ↓ cx.waker().clone()  ← 保存 waker
  ↓ Poll::Pending

[后台线程完成操作]
  ↓ waker.wake()
RawTask::wake_by_val() (harness.rs:68)
  ↓ schedule()  ← 重新调度任务
调度器重新 poll 任务
```

**## 参考资料**

- `tokio/src/runtime/task/harness.rs` - 任务执行的核心逻辑
- `tokio/src/runtime/task/waker.rs` - Waker 的创建和管理
- `tokio/src/runtime/task/core.rs` - Future 的 poll 调用
- `tokio/src/runtime/scheduler/multi_thread/worker.rs` - 多线程调度器

