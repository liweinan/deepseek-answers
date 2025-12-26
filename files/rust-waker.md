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

---

# **# Rust 编译器如何将 async/await 编译成 Future 并调用 waker.wake()**

**## 概述**

当你写一个 `async fn` 时，Rust 编译器会将其转换为一个实现了 `Future` trait 的状态机。这个状态机通过 `poll()` 方法推进执行，当遇到 `await` 时返回 `Poll::Pending`，并保存 `waker`。当异步操作完成时，会调用 `waker.wake()` 来通知运行时重新 poll。

**## 编译转换过程**

**### 1. async 函数 → 状态机（Coroutine）**

****文件：`compiler/rustc_mir_transform/src/coroutine.rs`****

Rust 编译器将 `async fn` 转换为一个状态机（coroutine），其结构如下：

```rust
// 编译器生成的 Future 结构（简化版）
struct AsyncFuture {
    // 1. 捕获的变量（upvars）
    upvars: ...,
    
    // 2. 状态字段
    state: u32,  // 0 = 未开始, 1 = 完成, 2 = 已销毁, 3+ = 暂停点
    
    // 3. 跨暂停点存活的局部变量
    saved_locals: ...,
}
```

**### 2. await 点 → yield 点**

****文件：`compiler/rustc_mir_transform/src/coroutine.rs` (第 34-36 行)****

```rust
//! It also rewrites `return x` and `yield y` as setting a new coroutine state and returning
//! `CoroutineState::Complete(x)` and `CoroutineState::Yielded(y)`,
//! or `Poll::Ready(x)` and `Poll::Pending` respectively.
```

当遇到 `await` 时，编译器会：

1\. ****保存当前状态****：将状态设置为对应的暂停点编号
2\. ****保存跨暂停点的局部变量****：将这些变量移动到状态机结构中
3\. ****返回 `Poll::Pending`****：表示 future 尚未就绪

****代码实现（第 280-295 行）：****

```rust
fn make_coroutine_state_rvalue(
    &mut self,
    val: Operand<'tcx>,
    source_info: SourceInfo,
    is_return: bool,
    statements: &mut Vec<Statement<'tcx>>,
) {
    const ZERO: VariantIdx = VariantIdx::ZERO;
    const ONE: VariantIdx = VariantIdx::from_usize(1);
    let rvalue = match self.coroutine_kind {
        CoroutineKind::Desugared(CoroutineDesugaring::Async, _) => {
            let poll_def_id = self.tcx.require_lang_item(LangItem::Poll, source_info.span);
            let args = self.tcx.mk_args(&[self.old_ret_ty.into()]);
            let (variant_idx, operands) = if is_return {
                (ZERO, indexvec![val]) // Poll::Ready(val)  ← 完成时
            } else {
                (ONE, IndexVec::new()) // Poll::Pending      ← await 时
            };
            make_aggregate_adt(poll_def_id, variant_idx, args, operands)
        }
        // ...
    }
}
```

**### 3. Context 的注入**

****文件：`compiler/rustc_mir_transform/src/coroutine.rs` (第 570-622 行)****

编译器会处理 `Context` 的注入：

```rust
/// Transforms the coroutine body:
///
/// - Eliminates all the `get_context` calls that async lowering created.
/// - Replace all `Local` `ResumeTy` types with `&mut Context<'_>` (`context_mut_ref`).
fn transform_async_context<'tcx>(tcx: TyCtxt<'tcx>, body: &mut Body<'tcx>) -> Ty<'tcx> {
    let context_mut_ref = Ty::new_task_context(tcx);

    // 替换 resume 参数的类型为 &mut Context<'_>
    replace_resume_ty_local(tcx, body, CTX_ARG, context_mut_ref);

    // 处理所有 yield 点（await 点）
    for bb in body.basic_blocks.indices() {
        match &bb_data.terminator().kind {
            TerminatorKind::Yield { resume_arg, .. } => {
                // ⭐ 将 yield 点的 resume_arg 类型替换为 &mut Context<'_>
                replace_resume_ty_local(tcx, body, resume_arg.local, context_mut_ref);
            }
            // ...
        }
    }
    context_mut_ref
}
```

**### 4. 生成的 poll() 方法**

编译器会生成类似这样的 `poll()` 方法：

```rust
impl Future for AsyncFuture {
    type Output = T;
    
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        // ⭐ 从 Context 中获取 waker
        let waker = cx.waker();
        
        // 状态机匹配
        match self.state {
            0 => {
                // 首次调用，开始执行
                // ... 执行到第一个 await 点 ...
                // 保存 waker 到某个地方（通过调用子 future 的 poll）
                // 设置状态为暂停点编号
                // 返回 Poll::Pending
            }
            1 => {
                // 已完成
                Poll::Ready(result)
            }
            2 => {
                // 已销毁，panic
                panic!("polled after completion")
            }
            n => {
                // 从暂停点 n 继续执行
                // ... 恢复保存的局部变量 ...
                // ... 继续执行到下一个 await 或 return ...
            }
        }
    }
}
```

**## 实际例子：async 函数编译后的代码**

**### 源代码**

```rust
async fn example() -> i32 {
    let x = async_operation().await;  // ← await 点 1
    let y = another_operation().await; // ← await 点 2
    x + y
}
```

**### 编译器生成的代码（简化版）**

```rust
// 状态机结构
struct ExampleFuture {
    state: u32,
    // 捕获的变量
    // 跨暂停点存活的局部变量
    x: Option<i32>,
    y: Option<i32>,
    // 子 future
    async_op: Option<AsyncOperationFuture>,
    another_op: Option<AnotherOperationFuture>,
}

impl Future for ExampleFuture {
    type Output = i32;
    
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<i32> {
        let this = unsafe { self.get_unchecked_mut() };
        
        loop {
            match this.state {
                0 => {
                    // 开始执行
                    this.async_op = Some(async_operation());
                    this.state = 1; // 进入 await 点 1
                }
                1 => {
                    // await 点 1：等待 async_operation 完成
                    let mut fut = this.async_op.as_mut().unwrap();
                    match fut.poll(cx) {  // ⭐ 传递 Context（包含 waker）
                        Poll::Ready(val) => {
                            this.x = Some(val);
                            this.async_op = None;
                            this.another_op = Some(another_operation());
                            this.state = 2; // 进入 await 点 2
                        }
                        Poll::Pending => {
                            // ⭐ 子 future 已经保存了 waker
                            // 当 async_operation 完成时，会调用 waker.wake()
                            return Poll::Pending;
                        }
                    }
                }
                2 => {
                    // await 点 2：等待 another_operation 完成
                    let mut fut = this.another_op.as_mut().unwrap();
                    match fut.poll(cx) {  // ⭐ 传递 Context（包含 waker）
                        Poll::Ready(val) => {
                            this.y = Some(val);
                            this.another_op = None;
                            this.state = 3; // 准备返回
                        }
                        Poll::Pending => {
                            // ⭐ 子 future 已经保存了 waker
                            return Poll::Pending;
                        }
                    }
                }
                3 => {
                    // 完成，返回结果
                    return Poll::Ready(this.x.unwrap() + this.y.unwrap());
                }
                _ => unreachable!(),
            }
        }
    }
}
```

**## waker.wake() 的调用机制**

**### 1. Waker 的创建（标准库）**

****文件：`library/core/src/task/wake.rs` (第 438-449 行)****

```rust
impl Waker {
    /// Wakes up the task associated with this `Waker`.
    #[inline]
    pub fn wake(self) {
        // 实际的唤醒调用通过虚函数表委托给运行时实现
        let this = ManuallyDrop::new(self);
        
        // ⭐ 调用 vtable 中的 wake 函数
        // 这个函数由运行时（如 tokio）提供
        unsafe { (this.waker.vtable.wake)(this.waker.data) };
    }
    
    /// Wakes up the task without consuming the `Waker`.
    #[inline]
    pub fn wake_by_ref(&self) {
        unsafe { (self.waker.vtable.wake_by_ref)(self.waker.data) }
    }
}
```

**### 2. 子 Future 如何保存和调用 Waker**

当你在 `async fn` 中使用 `await` 时：

```rust
async fn my_async() {
    let result = some_operation().await;
    // ...
}
```

编译后的代码会：

1\. ****调用子 future 的 poll()****：`some_operation().poll(cx)`
2\. ****子 future 保存 waker****：如果返回 `Poll::Pending`，子 future 会保存 `cx.waker().clone()`
3\. ****异步操作完成时调用 waker.wake()****：当 `some_operation` 完成时（如 I/O 就绪、定时器到期），会调用保存的 `waker.wake()`
4\. ****运行时重新调度****：`waker.wake()` 会通知运行时（如 tokio）重新 poll 这个 future

**### 3. 完整的调用链**

```
1\. 运行时调用 future.poll(cx)
   ↓
2\. 编译器生成的 poll() 方法
   ↓
3\. 遇到 await，调用子 future.poll(cx)
   ↓
4\. 子 future 返回 Poll::Pending，保存 cx.waker().clone()
   ↓
5\. 编译器生成的 poll() 返回 Poll::Pending
   ↓
6\. [异步操作完成]
   ↓
7\. 子 future 调用 waker.wake()
   ↓
8\. 运行时收到通知，重新调用 future.poll(cx)
   ↓
9\. 编译器生成的 poll() 从上次暂停点继续执行
```

**## 关键点总结**

1\. ****async 函数被编译成状态机****：每个 `await` 点对应一个状态
2\. ****Context 通过参数传递****：编译器生成的 `poll()` 方法接收 `&mut Context<'_>`
3\. ****Waker 在 await 时保存****：子 future 的 `poll()` 会保存 `cx.waker()`
4\. ****Waker 在操作完成时调用****：异步操作完成时调用 `waker.wake()` 通知运行时
5\. ****运行时负责重新调度****：`waker.wake()` 会触发运行时重新 poll future

**## 与你的例子的对比**

**### 你的例子（手动实现）**

```rust
impl Future for AsyncTimerFuture {
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        // 手动保存 waker
        state.waker = Some(cx.waker().clone());
        Poll::Pending
    }
}

// 手动调用 wake
thread::spawn(move || {
    thread::sleep(duration);
    waker.wake();  // ← 手动调用
});
```

**### 编译器生成的代码（async/await）**

```rust
// 编译器自动生成类似的代码
async fn example() {
    let result = some_operation().await;  // ← 编译器自动处理
    // ...
}

// 编译器生成的 poll() 方法：
// 1. 自动调用子 future.poll(cx)
// 2. 子 future 自动保存 waker
// 3. 子 future 完成时自动调用 waker.wake()
// 4. 运行时自动重新调度
```

**## 参考资料**

- `compiler/rustc_mir_transform/src/coroutine.rs` - 状态机转换的核心实现
- `library/core/src/task/wake.rs` - Waker 的标准库实现
- `library/core/src/future/future.rs` - Future trait 的定义

---

# **# Tokio 中 Waker.wake() 的实际调用机制**

**## 问题**

在你的 `AsyncTimerFuture` 例子中，你使用了 `thread::spawn()` 在独立线程中调用 `waker.wake()`。但在实际的异步运行时（如 tokio）中，****并不是这样工作的****。

**## 实际机制：事件驱动**

在实际的异步运行时中，`waker.wake()` 是通过****事件驱动****机制调用的，而不是独立线程。主要有以下几种方式：

**### 1. I/O 事件驱动（epoll/kqueue/IOCP）**

当 I/O 操作就绪时（如 socket 可读/可写），操作系统会通过事件通知机制（Linux 的 epoll、macOS 的 kqueue、Windows 的 IOCP）通知 tokio 的 I/O 驱动。

**#### 流程**

```
1\. Future 调用 poll()，返回 Pending，并保存 waker
   ↓
2\. I/O 驱动通过 epoll/kqueue/IOCP 等待 I/O 事件
   ↓
3\. 操作系统检测到 I/O 就绪，唤醒 I/O 驱动
   ↓
4\. I/O 驱动处理事件，调用 waker.wake()
   ↓
5\. 任务重新被调度，再次 poll()
```

**#### 代码实现**

****文件：`tokio/src/runtime/io/driver.rs` (第 179-223 行)****

```rust
fn turn(&mut self, handle: &Handle, max_wait: Option<Duration>) {
    // ... 省略其他代码 ...
    
    // ⭐ 步骤 1：阻塞等待 I/O 事件（使用 epoll/kqueue/IOCP）
    // 这里会阻塞，直到有 I/O 事件发生
    match self.poll.poll(events, max_wait) {
        Ok(()) => {}
        // ... 错误处理 ...
    }

    // ⭐ 步骤 2：处理所有到达的事件
    for event in events.iter() {
        let token = event.token();
        
        if token == TOKEN_WAKEUP {
            // 用于唤醒 I/O 驱动本身
        } else if token == TOKEN_SIGNAL {
            self.signal_ready = true;
        } else {
            // ⭐ 步骤 3：从 token 恢复 ScheduledIo
            let ready = Ready::from_mio(event);
            let ptr = super::EXPOSE_IO.from_exposed_addr(token.0);
            let io: &ScheduledIo = unsafe { &*ptr };

            // ⭐ 步骤 4：设置就绪状态并唤醒等待的任务
            io.set_readiness(Tick::Set, |curr| curr | ready);
            io.wake(ready);  // ← 这里调用 waker.wake()
        }
    }
}
```

****文件：`tokio/src/runtime/io/scheduled_io.rs` (第 238-288 行)****

```rust
pub(super) fn wake(&self, ready: Ready) {
    let mut wakers = WakeList::new();
    let mut waiters = self.waiters.lock();

    // ⭐ 收集所有等待此 I/O 就绪的 waker
    if ready.is_readable() {
        if let Some(waker) = waiters.reader.take() {
            wakers.push(waker);
        }
    }

    if ready.is_writable() {
        if let Some(waker) = waiters.writer.take() {
            wakers.push(waker);
        }
    }

    // 从等待列表中收集更多 waker
    'outer: loop {
        let mut iter = waiters.list.drain_filter(|w| ready.satisfies(w.interest));

        while wakers.can_push() {
            match iter.next() {
                Some(waiter) => {
                    let waiter = unsafe { &mut *waiter.as_ptr() };
                    if let Some(waker) = waiter.waker.take() {
                        waiter.is_ready = true;
                        wakers.push(waker);
                    }
                }
                None => break 'outer,
            }
        }

        drop(waiters);
        
        // ⭐ 批量唤醒所有等待的 waker
        wakers.wake_all();  // ← 这里调用每个 waker.wake()

        waiters = self.waiters.lock();
    }

    drop(waiters);
    wakers.wake_all();
}
```

**### 2. 定时器驱动**

定时器到期时，定时器驱动会检查哪些定时器已到期，然后唤醒对应的任务。

**#### 流程**

```
1\. Future 调用 poll()，返回 Pending，并保存 waker 到定时器条目
   ↓
2\. 定时器驱动在 park/park_timeout 中等待
   ↓
3\. 定时器到期，定时器驱动被唤醒
   ↓
4\. 定时器驱动检查到期的定时器，调用 waker.wake()
   ↓
5\. 任务重新被调度，再次 poll()
```

**#### 代码实现**

****文件：`tokio/src/runtime/time/mod.rs` (第 296-337 行)****

```rust
pub(self) fn process_at_time(&self, mut now: u64) {
    let mut waker_list = WakeList::new();
    let mut lock = self.inner.lock();

    // ⭐ 步骤 1：从时间轮中取出所有到期的定时器
    while let Some(entry) = lock.wheel.poll(now) {
        debug_assert!(unsafe { entry.is_pending() });

        // ⭐ 步骤 2：触发定时器，获取保存的 waker
        // SAFETY: We hold the driver lock, and just removed the entry from any linked lists.
        if let Some(waker) = unsafe { entry.fire(Ok(())) } {
            waker_list.push(waker);

            if !waker_list.can_push() {
                // ⭐ 步骤 3：批量唤醒 waker（避免死锁，先释放锁）
                drop(lock);
                waker_list.wake_all();  // ← 这里调用 waker.wake()
                lock = self.inner.lock();
            }
        }
    }

    // ... 更新下次唤醒时间 ...

    drop(lock);
    
    // ⭐ 步骤 4：唤醒剩余的 waker
    waker_list.wake_all();  // ← 这里调用 waker.wake()
}
```

****文件：`tokio/src/runtime/time/entry.rs` (第 211-231 行)****

```rust
/// 触发定时器，返回保存的 waker
/// SAFETY: The driver lock must be held.
unsafe fn fire(&self, result: TimerResult) -> Option<Waker> {
    let cur_state = self.state.load(Ordering::Relaxed);
    if cur_state == STATE_DEREGISTERED {
        return None;
    }

    // 设置定时器结果
    unsafe { self.result.with_mut(|p| *p = result) };
    self.state.store(STATE_DEREGISTERED, Ordering::Release);

    // ⭐ 取出并返回保存的 waker
    // 这个 waker 是在 Future 的 poll() 中通过 entry.poll() 注册的
    self.waker.take_waker()
}
```

**### 3. 其他异步原语**

其他异步原语（如 channel、mutex、semaphore 等）也会在条件满足时调用 `waker.wake()`。

例如，在 `tokio::sync::mpsc` 中：
- 当发送端发送数据时，会唤醒接收端的 waker
- 当接收端接收数据后，会唤醒发送端的 waker（如果缓冲区有空间）

**## 关键区别**

**### 你的例子（独立线程）**

```rust
thread::spawn(move || {
    thread::sleep(duration);  // ← 阻塞线程
    waker.wake();             // ← 在独立线程中调用
});
```

****问题：****
- 每个异步操作都需要一个独立线程
- 线程资源消耗大
- 无法扩展到大量并发操作

**### 实际异步运行时（事件驱动）**

```rust
// I/O 驱动
self.poll.poll(events, max_wait);  // ← 阻塞等待事件（使用 epoll/kqueue）
for event in events.iter() {
    io.wake(ready);  // ← 在事件循环中调用
}

// 定时器驱动
while let Some(entry) = lock.wheel.poll(now) {
    if let Some(waker) = entry.fire(Ok(())) {
        waker.wake();  // ← 在定时器处理中调用
    }
}
```

****优势：****
- 单个线程可以处理大量并发操作
- 资源消耗低
- 可扩展到百万级并发

**## 完整示例对比**

**### 你的例子（教学用途）**

```rust
pub struct AsyncTimerFuture {
    shared_state: Arc<Mutex<SharedState>>,
}

impl Future for AsyncTimerFuture {
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let mut state = self.shared_state.lock().unwrap();
        
        if state.completed {
            Poll::Ready("完成")
        } else {
            // 保存 waker
            state.waker = Some(cx.waker().clone());
            
            // ⚠️ 在独立线程中调用 wake
            thread::spawn(move || {
                thread::sleep(duration);
                waker.wake();  // ← 独立线程
            });
            
            Poll::Pending
        }
    }
}
```

**### 实际 tokio 的实现（Sleep）**

```rust
// tokio::time::Sleep 的实现（简化版）
impl Future for Sleep {
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        // ⭐ 将 waker 注册到定时器驱动
        self.entry.poll(cx.waker());
        
        // 检查定时器是否已到期
        if self.entry.is_elapsed() {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}

// 定时器驱动在后台运行（在运行时线程中）
// 当定时器到期时，驱动会调用 waker.wake()
```

**## 总结**

1\. ****不是独立线程****：实际的异步运行时不使用独立线程来调用 `waker.wake()`
2\. ****事件驱动****：通过操作系统的事件机制（epoll/kqueue/IOCP）和定时器驱动来触发唤醒
3\. ****集中管理****：所有异步操作都由运行时的事件循环统一管理
4\. ****高效扩展****：单个线程可以处理大量并发操作

你的例子是为了****教学目的****，展示了 waker 的基本工作原理。在实际使用中，tokio 等运行时会自动处理这些细节，你只需要使用 `tokio::time::sleep()` 等高级 API 即可。

