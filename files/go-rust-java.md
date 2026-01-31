# Go vs Rust vs Java Virtual Threads 并发模型深度对比

## 引言

> "从 Go 过来学 Rust，有些地方特别别扭。Go 的并发模型，开个 goroutine 就完事了，runtime 帮你调度。Rust 不是这样——你得明确告诉它这个任务什么时候跑、在哪跑、数据归谁管。一开始我觉得这是 Rust 在折腾人，学了一阵子才明白，这其实是把 Go 藏在 runtime 里的复杂性给拎出来了。Go 的调度器确实优秀，但它帮你做的决定，你看不见也改不了。Rust 让你直面这些决定——累是累点，但出了问题你知道往哪查。"

这段话**基本准确**，但需要更细致的分析。本文档基于 Tokio 的实现，深入对比三种主流并发模型：**Go Goroutines**、**Rust Async (Tokio)** 和 **Java Virtual Threads (Project Loom)**。

**自学阅读建议**：先分别读 §2 Go 核心实现、§3 Rust 核心实现、§4 Java Virtual Threads 核心实现（核心 struct 与设计思路）；再读 §5 横向对比、§6 总结与参考资料。文中的源码路径与行号以 Go 主线为准，可克隆 [golang/go](https://github.com/golang/go) 后按符号名搜索校订。

## 1. 核心差异概览

| 维度 | Go (Goroutines) | Rust (Tokio) | Java (Virtual Threads) |
|------|-----------------|--------------|-------------------------|
| **任务创建** | `go func()` - 隐式调度 | `tokio::spawn()` - 显式运行时 | `Thread.ofVirtual().start()` - 类似传统线程 |
| **调度器** | 内置 GMP 模型，不可见 | 可选的运行时（Tokio/async-std），可见 | JVM 内置，部分可见 |
| **所有权** | GC 管理，自动处理 | 编译时检查，显式所有权 | GC 管理，自动处理 |
| **调度策略** | 抢占式（函数调用点 + 异步信号） | 协作式（必须主动 await） | 协作式（阻塞时自动让出） |
| **运行时开销** | 内置，无法移除（~2MB） | 可选，零成本抽象 | 内置 JVM，无法移除 |
| **可定制性** | 有限（GOMAXPROCS） | 高度可定制（运行时类型、调度器） | 有限（carrier thread pool 配置） |
| **API 兼容性** | 原生支持 | 需要 async/await | 兼容传统 Thread API |

## 2. Go 核心实现

### 2.1 简单但隐藏细节

**Go 代码示例：**

```go
func main() {
    // 开个 goroutine，就这么简单
    go fetchURL("https://example.com")
    go processData()
    
    // runtime 自动调度，你不需要关心
    time.Sleep(time.Second)
}
```

**Go 的"魔法"：**

1. **隐式运行时**：每个 Go 程序都内置 runtime，无法移除
2. **自动调度**：Goroutine 的调度完全由 runtime 管理
3. **GC 管理内存**：不需要关心数据的所有权
4. **抢占式调度**：runtime 可以在函数调用点抢占 goroutine

### 2.2 Go 调度器的复杂性（被隐藏）：GMP 模型详解

虽然用户代码简单，但 Go 的调度器实际上非常复杂，基于 **GMP（Goroutine-Machine-Processor）模型**：

#### GMP 模型架构

```
Go Runtime 调度器 (GMP 模型)
│
├─ G (Goroutine) - 轻量级协程
│  ├─ 栈空间（初始 2KB，可增长到 1GB）
│  ├─ 程序计数器（PC）
│  ├─ 调度上下文
│  └─ 状态：_Grunnable, _Grunning, _Gwaiting, _Gsyscall, _Gdead
│
├─ M (Machine) - OS 线程
│  ├─ 执行 Go 代码的实际工作线程
│  ├─ 必须绑定 P 才能执行 G
│  ├─ 数量动态变化（可创建新 M 处理阻塞）
│  └─ 包含 g0（调度器 goroutine）和 curg（当前执行的 goroutine）
│
├─ P (Processor) - 逻辑处理器
│  ├─ 本地运行队列（local run queue，每个 P 一个）
│  │  ├─ 环形缓冲区（256 个 G）
│  │  ├─ runnext：下一个要运行的 G（高优先级）
│  │  └─ head/tail 指针
│  ├─ 状态：idle, running, syscall
│  ├─ mcache：内存分配器缓存（每个 P 一个）
│  └─ 数量 = GOMAXPROCS（默认 CPU 核心数）
│
└─ 调度机制
   ├─ 工作窃取算法（Work Stealing）
   │  ├─ 本地队列（每个 P 一个）
   │  ├─ 全局队列（所有 P 共享）
   │  └─ 当本地队列空时，从其他 P 窃取一半任务
   ├─ 网络轮询器（netpoller）
   │  └─ 处理网络 IO，避免阻塞 M
   └─ 抢占式调度
      ├─ 函数调用点检查抢占标志
      ├─ 异步信号抢占（Go 1.14+）
      └─ 防止单个 G 长时间占用 CPU
```

#### 2.2.1 G (Goroutine) 结构体与状态

G 是调度单元，对应一个 goroutine。下面给出运行时中 G 的结构与状态定义，便于自学时对照源码。

**G 结构体核心字段（节选）**

**文件：`go/src/runtime/runtime2.go` (第 473-601 行)**

```go
type g struct {
	// ⭐ 栈
	stack       stack   // 栈范围 [stack.lo, stack.hi)
	stackguard0 uintptr // 栈增长/抢占比较用（可为 StackPreempt 触发抢占）
	stackguard1 uintptr

	_panic *_panic
	_defer *_defer
	m      *m      // ⭐ 当前绑定的 M（执行此 G 的 OS 线程）
	sched  gobuf   // ⭐ 调度上下文：保存/恢复运行现场

	syscallsp uintptr // _Gsyscall 时保存 sp
	syscallpc uintptr
	stktopsp  uintptr

	param        unsafe.Pointer
	atomicstatus atomic.Uint32 // ⭐ G 的状态（见下方常量）
	stackLock    uint32
	goid         uint64   // ⭐ goroutine ID
	schedlink    guintptr // ⭐ 链到下一个 G（如 runq、全局队列）
	waitsince    int64
	waitreason   waitReason // _Gwaiting 时的原因

	preempt       bool   // 抢占标记
	preemptStop   bool
	preemptShrink bool
	asyncSafePoint bool

	// ... 其他字段：panic/defer、信号、channel 等待、timer、GC、追踪等
	startpc  uintptr   // goroutine 入口函数 PC
	waiting  *sudog    // 等待的 channel/sync 对象
	timer    *timer    // time.Sleep 等
	gopc     uintptr  // 创建此 G 的 go 语句 PC
	// ...
}
```

**调度上下文 gobuf**

**文件：`go/src/runtime/runtime2.go` (第 303-323 行)**

```go
type gobuf struct {
	sp   uintptr // 栈指针
	pc   uintptr // 程序计数器
	g    guintptr
	ctxt unsafe.Pointer
	lr   uintptr
	bp   uintptr // 帧指针（若启用）
}
```

切换 goroutine 时，runtime 保存当前 G 的寄存器到 `g.sched`，再从目标 G 的 `sched` 恢复，实现协作/抢占切换。

**G 的状态常量**

**文件：`go/src/runtime/runtime2.go` (第 35-119 行)**

```go
const (
	_Gidle    = iota // 0：刚分配，未初始化
	_Grunnable       // 1：在运行队列中，未在执行用户代码
	_Grunning        // 2：正在执行用户代码，拥有栈，不在队列
	_Gsyscall        // 3：正在执行系统调用，可能没有 P
	_Gwaiting        // 4：在 runtime 中阻塞（如 channel、锁）
	_Gmoribund_unused
	_Gdead           // 6：未使用（刚退出、在空闲列表或未初始化）
	_Genqueue_unused
	_Gcopystack      // 8：栈正在被拷贝
	_Gpreempted      // 9：因抢占而暂停
	_Gleaked         // 10：泄漏后被 GC 发现
	_Gdeadextra      // 11：附着在 extra M 上的 _Gdead

	// _Gscan 与上述状态组合表示 GC 正在扫描该 G 的栈
	_Gscan          = 0x1000
	_Gscanrunnable  = _Gscan + _Grunnable
	_Gscanrunning   = _Gscan + _Grunning
	// ...
)
```

**与调度流程的对应关系**

| 状态        | 含义           | 典型场景                 |
|-------------|----------------|--------------------------|
| _Gidle      | 刚分配         | `malg` 分配新 G          |
| _Grunnable  | 可运行         | 在 P 的 runq 或全局 runq |
| _Grunning   | 正在运行       | 正被某个 M 执行          |
| _Gsyscall   | 系统调用中     | 进入 syscall，可能失去 P |
| _Gwaiting   | 阻塞等待       | channel 阻塞、锁、sleep  |
| _Gdead      | 已结束/可复用  | 放回 gFree 或即将退出    |

**创建 G 的入口**

**文件：`go/src/runtime/proc.go`**

- **`newproc(fn)`**（约第 5295 行）：`go fn()` 编译后的入口，会调 `newproc1`。
- **`newproc1`**（约第 5313 行）：从 P 的 gFree 或 `gfget` 取/分配 G（`malg`），设置入口 PC、栈等，然后放入当前 P 的 runq 或全局队列。
- **`malg(stacksize)`**（约第 5273 行）：分配并初始化一个 G。
- **`gfget(pp)`**（约第 5507 行）：从 P 的 gFree 获取可复用的 G。

自学时可从 `proc.go` 的 `newproc`/`newproc1` 和 `runtime2.go` 的 `type g struct`、G 状态常量对照阅读。

#### GMP 模型的核心关系

**执行关系：`G ↔ P ↔ M`**

```
┌─────────────────────────────────────────┐
│  执行 Go 代码必须满足：M + P + G        │
│                                         │
│  M (OS 线程) ──绑定──> P (逻辑处理器)  │
│       │                                  │
│       └──执行──> G (Goroutine)          │
└─────────────────────────────────────────┘
```

**关键约束：**

1. **M 和 P 的关系：一对一绑定**
    - **一个 M 同时只能绑定一个 P**
    - **一个 P 同时只能被一个 M 绑定**
    - **P 可以在不同的 M 之间转移**（当 M 阻塞时，P 会被释放，然后被其他 M 获取）

2. **P 和 G 的关系：一对多管理**
    - **一个 P 可以管理多个 G**（通过本地队列 `runq[256]`）
    - **一个 P 同时只能执行一个 G**（通过 M 执行）

3. **数量关系：**
    - **P 的数量 = GOMAXPROCS**：决定最大并行度（默认 CPU 核心数）
    - **M 的数量动态变化**：可以创建新 M 处理阻塞的 syscall
    - **G 的数量无限制**：可以创建任意数量的 goroutine

**关于线程池：Go 没有传统意义上的线程池**

**❌ Go 没有传统线程池：**
- ❌ 没有显式的线程池 API（不像 Java 的 `ThreadPoolExecutor`）
- ❌ M (OS 线程) 数量不是固定的池，而是动态创建和销毁
- ❌ 用户无法直接控制线程池大小

**✅ 但 Go 有类似的概念：**

1. **P (Processor) 可以看作"逻辑处理器池"**：
    - 数量固定 = `GOMAXPROCS`（默认 CPU 核心数）
    - 类似于线程池的"工作线程数"
    - 可以通过 `runtime.GOMAXPROCS()` 设置

2. **M (OS 线程) 是动态管理的**：
    - Runtime 会根据需要创建和销毁 M
    - 不是固定大小的池，而是动态调整
    - 通常 M 数量 ≈ P 数量（GOMAXPROCS）

**✅ 重要理解：Runtime 承担了线程池的角色**

虽然 Go 没有传统意义上的线程池 API，但 **Runtime 确实承担了线程池的工作**：

**Runtime 如何管理 M（类似线程池）：**

1. **M 的创建（newm）**：
    - 当需要新的 M 来执行 P 时，Runtime 创建新的 OS 线程
    - 例如：M 进入阻塞 syscall，需要新 M 来执行释放的 P

2. **M 的复用（mget/mput）**：
    - **idle M 列表**：`sched.midle` 存储空闲的 M
    - **free M 列表**：`sched.freem` 存储已退出但未销毁的 M
    - Runtime 优先复用空闲的 M，而不是创建新 M

3. **M 的销毁（mexit）**：
    - 当 M 不再需要时，Runtime 会销毁它
    - 但通常会保留一段时间，以便复用

**源代码证据：**

**文件：`go/src/runtime/runtime2.go` (第 940-971 行)**

```go
type schedt struct {
	// ... 其他字段
	
	// ⭐ M 的 idle 列表（类似线程池的空闲线程）
	midle        listHeadManual  // idle m's waiting for work
	nmidle       int32          // number of idle m's waiting for work
	nmidlelocked int32          // number of locked m's waiting for work
	
	// ⭐ M 的 free 列表（已退出但未销毁的 M）
	freem        *m             // ⭐ free m's linked list
	
	// ⭐ P 的 idle 列表
	pidle        puintptr       // idle p's
	npidle       atomic.Int32
	
	// ... 其他字段
}
```

**M 管理的函数：**

- **`newm(fn, pp, id)`**：创建新的 M（类似线程池创建新线程）
- **`mget()`**：从 idle 列表获取 M（类似线程池获取空闲线程）
- **`mput(mp)`**：将 M 放回 idle 列表（类似线程池回收线程）
- **`mexit()`**：M 退出（类似线程池销毁线程）

**对比传统线程池：**

| 特性 | 传统线程池 | Go Runtime M 管理 |
|------|-----------|-------------------|
| **线程创建** | 用户显式创建 | Runtime 自动创建（`newm`） |
| **线程复用** | 线程池管理 | Runtime 管理（`mget`/`mput`） |
| **线程销毁** | 用户显式销毁 | Runtime 自动销毁（`mexit`） |
| **空闲列表** | 线程池维护 | Runtime 维护（`sched.midle`） |
| **动态调整** | 通常固定大小 | 动态创建和销毁 |
| **用户控制** | 完全可控 | 隐藏，不可见 |

**关键区别：**

- ✅ **Runtime 承担了线程池的工作**：管理 M 的创建、复用、销毁
- ✅ **但对用户隐藏**：用户无法直接控制，也不需要关心
- ✅ **动态调整**：不是固定大小的池，而是根据需求动态调整
- ✅ **自动优化**：Runtime 会自动优化 M 的数量，避免资源浪费

**实际运行示例：**

```
初始状态（8 核 CPU，GOMAXPROCS=8）：
├─ 8 个 M（运行中）
├─ 8 个 P（绑定到 M）
└─ sched.midle = []（无空闲 M）

场景：多个 M 进入阻塞 syscall

T1: M1 进入阻塞 syscall
├─ M1 释放 P1
├─ handoffp(P1) 需要新 M
└─ Runtime 创建 M9（newm）
   ├─ M9 获取 P1
   └─ 现在有 9 个 M

T2: M1 的 syscall 完成
├─ M1 尝试获取 P
├─ 如果 P 都被占用，M1 进入 idle 列表
└─ sched.midle = [M1]

T3: 一段时间后，如果 M1 仍然空闲
└─ Runtime 可能销毁 M1（mexit）
   └─ 减少到 8 个 M（回到初始状态）
```

**总结：**

- ✅ **Runtime 确实承担了线程池的角色**：管理 M 的创建、复用、销毁
- ✅ **但对用户完全隐藏**：用户不需要关心 M 的管理
- ✅ **动态优化**：Runtime 会根据实际需求动态调整 M 的数量
- ✅ **自动管理**：无需用户手动管理，Runtime 自动处理所有细节

3. **GOMAXPROCS 的作用**：
   ```go
   // 设置最大并行度（类似线程池大小）
   runtime.GOMAXPROCS(8)  // 设置 8 个 P
   
   // 获取当前值
   procs := runtime.GOMAXPROCS(0)
   ```

**Go 的设计理念：**
- ✅ **不需要线程池**：因为 goroutine 很轻量（~2KB），可以创建大量 goroutine
- ✅ **自动管理**：Runtime 自动管理 M 的创建和销毁
- ✅ **通过 GOMAXPROCS 控制并行度**：而不是控制线程数

**如果需要限制并发，可以使用 goroutine 池（不推荐）：**

```go
// ⚠️ 不推荐：手动实现 goroutine 池
func workerPool(workers int, jobs <-chan Job) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                process(job)
            }
        }()
    }
    wg.Wait()
}

// ✅ 推荐：直接创建 goroutine，让 runtime 管理
for _, job := range jobs {
    go func(j Job) {
        process(j)
    }(job)
}
```

**对比其他语言：**

| 语言 | 线程池概念 | 控制方式 |
|------|-----------|---------|
| **Java** | ✅ 有（ThreadPoolExecutor） | 显式创建和管理线程池 |
| **Rust (Tokio)** | ✅ 有（Worker Thread Pool） | 可配置 worker_threads |
| **Go** | ❌ 无传统线程池 | 通过 GOMAXPROCS 控制并行度 |

**❌ 常见误解：**
- ❌ "一个 P 使用多个 M" → **错误**
- ✅ **正确理解**：一个 P 同时只能被一个 M 绑定，但一个 P 可以管理多个 G

**✅ 正确理解：**
- ✅ **一个 M 绑定一个 P**（一对一）
- ✅ **一个 P 管理多个 G**（一对多，通过本地队列）
- ✅ **多个 G 在同一个 P 上运行**（通过调度，轮流执行）

**源代码证据：**

**文件：`go/src/runtime/proc.go`（约第 6296 行起）**

```go
func wirep(pp *p) {
	gp := getg()
	
	// ⭐ 检查：如果 P 已经被其他 M 绑定，抛出错误
	if pp.m != 0 || pp.status != _Pidle {
		throw("wirep: invalid p state")
	}
	
	// ⭐ 建立双向关联（一对一）
	gp.m.p.set(pp)      // M -> P
	pp.m.set(gp.m)      // P -> M（一个 P 只能绑定一个 M）
	pp.status = _Prunning
}
```

**文件：`go/src/runtime/runtime2.go` (第 631, 641, 802-818 行)**

```go
type m struct {
	curg    *g         // ⭐ 当前执行的 goroutine（一个 M 一次只执行一个 G）
	p       puintptr   // ⭐ 绑定的 P（一个 M 只能绑定一个 P）
}

type p struct {
	m       muintptr   // ⭐ 绑定的 M（一个 P 只能绑定一个 M）
	runq    [256]guintptr  // ⭐ 本地队列：一个 P 可以管理多个 G（最多 256 个）
	runnext guintptr
}
```

**实际运行示例：**

```
场景：8 核 CPU（GOMAXPROCS=8）

运行时状态：
├─ M1 ──绑定──> P1 ──管理──> [G1, G2, G3, ...] (本地队列)
├─ M2 ──绑定──> P2 ──管理──> [G4, G5, G6, ...] (本地队列)
├─ M3 ──绑定──> P3 ──管理──> [G7, G8, G9, ...] (本地队列)
├─ ...
└─ M8 ──绑定──> P8 ──管理──> [G100, G101, ...] (本地队列)

全局队列：更多等待的 G

关键点：
- 8 个 M，8 个 P（一对一绑定）
- 每个 P 管理多个 G（本地队列 + 全局队列）
- 总共可能有数千个 G，但只有 8 个 M 在执行
```

#### GMP 调度流程

**1. Goroutine 创建：**
```go
go func() { ... }  // 创建 G
```
- 创建新的 G 结构体
- 将 G 放入当前 P 的本地队列
- 如果本地队列满（256 个），放入全局队列

**2. 调度执行：**
```
M 获取 P → P 从本地队列取 G → M 执行 G
```

**3. 工作窃取（Work Stealing）：G 在 P 之间转移**
```
P1 本地队列空
  ↓
P1 尝试从全局队列获取 G
  ↓
全局队列空 → P1 从 P2 窃取一半的 G（从尾部）
  ↓
G 从 P2 转移到 P1（G 可以转移）
```

**关键点：**
- ✅ **P 包含 G 的队列**：每个 P 有本地队列 `runq[256]`
- ✅ **G 可以转移**：通过工作窃取，G 可以从 P2 转移到 P1
- ✅ **转移机制**：`runqsteal` 函数实现 G 的转移

**4. 阻塞处理：P 在 M 之间转移**
```
G 执行阻塞 syscall
  ↓
M1 进入 syscall 状态
  ↓
M1 与 P1 解绑（releasep）
  ↓
P1 被放入 idle 列表（可以给其他 M 使用）
  ↓
M2 获取 P1（acquirep）
  ↓
P1 从 M1 转移到 M2（P 可以转移）
  ↓
syscall 完成
  ↓
M1 尝试重新获取 P（可能获取新的 P 或原来的 P1）
```

**关键点：**
- ✅ **P 可以转移到别的 M**：当 M 阻塞时，P 会被释放
- ✅ **P 转移机制**：通过 `handoffp` 函数实现 P 的转移
- ✅ **P 的复用**：释放的 P 可以被其他 M 获取，提高资源利用率

**5. 抢占式调度：**
```
长时间运行的 G（无函数调用）
  ↓
调度器设置抢占标志
  ↓
G 在函数调用点检查标志
  ↓
G 主动让出 CPU，进入队列
```

### 2.3 P、M、schedt 核心结构体与调度概要

**P (Processor)**（`runtime2.go`）：逻辑处理器，与 M 一对一绑定。核心字段：`runq[256]` 环形队列、`runnext` 高优先级 G、`m` 绑定的 M、`mcache` 每 P 内存缓存、状态 `_Pidle/_Prunning/_Pgcstop`。负责从本地队列或全局队列取 G 交给 M 执行。

**M (Machine)**（`runtime2.go`）：OS 线程。核心字段：`g0` 调度栈、`curg` 当前执行的 G、`p` 绑定的 P。必须绑定 P 才能执行用户 G；阻塞时通过 `handoffp(releasep())` 把 P 交给其他 M。

**schedt**（`runtime2.go`）：全局调度器。核心字段：`pidle` 空闲 P 列表、`midle` 空闲 M 列表、`runq` 全局 G 队列。调度逻辑：P 本地队列空时 `runqsteal` 从其他 P 窃取一半 G 或从 `runq` 取；M 阻塞时 P 进入 `pidle` 或被 `startm` 交给新 M。

**设计要点**：工作窃取负载均衡、抢占式调度（函数调用点 + 异步信号）、netpoller 处理网络 IO 避免阻塞 M。

### 2.4 创建与调度流程（高层）

`go fn()` → `newproc`/`newproc1` → 从 gFree 或 `malg` 得到 G → 放入当前 P 的 runq 或全局 runq。调度循环：M 绑定 P → `runqget` 从 P 取 G（优先 runnext）→ 执行 G；P 空时 `runqsteal` 窃取或从全局 runq 取；M 进 syscall 时 `releasep` + `handoffp`，P 可被其他 M 接管。

### 2.5 Go 优势与局限

**优势**：极简 API（`go func()`）、自动调度、抢占式保证公平、成熟稳定。

**局限**：运行时固定开销（~2MB）、GC 暂停、可定制性有限（GOMAXPROCS）、调度细节不可见难以调试。


## 3. Rust 核心实现

### 3.1 显式但可控

**Rust (Tokio) 代码示例：**

```rust
#[tokio::main]  // ⭐ 必须显式指定运行时
async fn main() {
    // 必须明确在哪个运行时上执行
    let handle1 = tokio::spawn(fetch_url("https://example.com"));
    let handle2 = tokio::spawn(process_data());
    
    // 必须显式等待
    let (_, _) = tokio::join!(handle1, handle2);
}
```

**Rust 的"显式"：**

1. **显式运行时**：必须选择运行时（Tokio/async-std）或自己实现
2. **显式调度**：需要理解 Future 和 `await` 机制
3. **显式所有权**：编译时检查，必须明确数据归谁管
4. **协作式调度**：必须主动 `await` 让出控制权

### 3.2 核心结构与设计

**Task**（Tokio `task/mod.rs`）：轻量级执行单元，类似 goroutine；由 Runtime 调度，在 `await` 点挂起/恢复，无独立栈（状态机）。

**Waker**：唤醒句柄；I/O 或定时器就绪时调用，将 Task 重新放入调度队列。

**Runtime**（Tokio）：包含 **I/O driver**（事件循环）、**scheduler**（在 worker 线程上执行 task）、**timer**。用户通过 `tokio::spawn` 提交 task，scheduler 在 worker 线程池上多路复用。

设计要点：协作式（仅在 await 点切换）、可选运行时（可零成本不用）、编译时所有权保证数据安全。

### 3.3 Rust 优势与挑战

**优势**：零成本抽象、编译时保证、可定制运行时（worker 数、栈大小等）、复杂性可见便于调试。

**挑战**：学习曲线陡峭（Future/async/await/所有权）、协作式需主动 yield、类型系统复杂。

## 4. Java Virtual Threads 核心实现

### 4.1 设计理念

Java Virtual Threads（虚拟线程）是 Java 19 引入、Java 21 稳定的特性，提供类似 Go goroutines 的轻量级并发，兼容传统 Thread API。核心：**虚拟线程**（用户态、栈在堆上）、**Carrier Threads**（平台线程承载）、阻塞时**自动卸载**。

### 4.2 架构与核心概念

**Virtual Thread (VT)**：轻量级执行单元，状态 NEW/RUNNABLE/BLOCKED/WAITING/TERMINATED。**Carrier Thread**：执行 VT 的 OS 线程，默认由 **ForkJoinPool** 提供（数量 = CPU 核心数）。调度：**挂载**（VT 绑定到 carrier）/ **卸载**（阻塞时让出 carrier）。与 Executor 关系：`Executors.newVirtualThreadPerTaskExecutor()` 每任务一 VT，不池化 VT；CPU 密集用 `ThreadPoolExecutor`（平台线程）。设计要点：VT 不应被池化、用 Semaphore 限流、避免在 VT 内用 `synchronized`（会 pin 住 carrier）。

### 4.3 优势与局限

**优势**：API 简单（类似 Thread）、迁移成本低、I/O 密集优秀、调试与 JVM 工具完善。**局限**：无 CPU 抢占、`synchronized` 导致 pinning、JVM/GC 开销、carrier 配置选项有限。

## 5. 横向对比

### 5.1 任务创建与调度

#### 任务创建（Go / Rust / Java）

#### Go：隐式创建

```go
func main() {
    // 就这么简单，runtime 自动处理
    go doWork()
    go doWork()
    go doWork()
    
    // runtime 自动决定：
    // - 在哪个线程上执行
    // - 何时调度
    // - 如何分配栈空间
}
```

#### Rust：显式创建

```rust
#[tokio::main]  // ⭐ 必须指定运行时
async fn main() {
    // 必须明确指定运行时
    let handle1 = tokio::spawn(do_work());
    let handle2 = tokio::spawn(do_work());
    let handle3 = tokio::spawn(do_work());
    
    // 必须显式等待
    tokio::join!(handle1, handle2, handle3);
    
    // 你可以控制：
    // - 使用哪个运行时（multi_thread/current_thread）
    // - 线程数量
    // - 调度策略
}
```

**文件：`tokio/src/task/mod.rs` (第 1-36 行)**

```rust
//! Asynchronous green-threads.
//!
//! A _task_ is a light weight, non-blocking unit of execution. A task is similar
//! to an OS thread, but rather than being managed by the OS scheduler, they are
//! managed by the [Tokio runtime][rt]. Another name for this general pattern is
//! [green threads]. If you are familiar with [Go's goroutines], [Kotlin's
//! coroutines], or [Erlang's processes], you can think of Tokio's tasks as
//! something similar.
```

#### 调度机制对比

#### Go：抢占式调度（部分）

```go
func longRunningTask() {
    for i := 0; i < 1000000; i++ {
        // Go runtime 可以在函数调用点抢占
        // 即使没有显式 yield，其他 goroutine 也能运行
        doSomething()
    }
}
```

**Go 的抢占机制：**
- 在函数调用点检查抢占标志
- 网络 IO 时自动让出
- 防止单个 goroutine 阻塞整个程序

#### Rust：协作式调度

```rust
async fn long_running_task() {
    for i in 0..1_000_000 {
        // ⚠️ 如果没有 await，会阻塞整个线程！
        do_something();
        
        // ✅ 必须主动让出控制权
        tokio::task::yield_now().await;
    }
}
```

**文件：`tokio/src/task/mod.rs` (第 20-28 行)**

```rust
//! * Tasks are scheduled **cooperatively**. Most operating systems implement
//!   _preemptive multitasking_. This is a scheduling technique where the
//!   operating system allows each thread to run for a period of time, and then
//!   _preempts_ it, temporarily pausing that thread and switching to another.
//!   Tasks, on the other hand, implement _cooperative multitasking_. In
//!   cooperative multitasking, a task is allowed to run until it _yields_,
//!   indicating to the Tokio runtime's scheduler that it cannot currently
//!   continue executing. When a task yields, the Tokio runtime switches to
//!   executing the next task.
```

**关键差异：**

| 特性 | Go | Rust (Tokio) |
|------|-----|--------------|
| **调度方式** | 抢占式（函数调用点） | 协作式（await 点） |
| **阻塞风险** | 低（runtime 会抢占） | 高（必须主动 yield） |
| **性能开销** | 抢占检查有开销 | 零开销（只在 await 点切换） |
| **可预测性** | 较低（抢占时机不确定） | 高（只在明确 await 点切换） |

#### 数据所有权

#### Go：GC 自动管理

```go
func main() {
    data := make([]byte, 1024)
    
    // 可以传递给多个 goroutine
    go process1(data)  // GC 保证安全
    go process2(data)  // GC 保证安全
    
    // 不需要关心：
    // - 数据何时释放
    // - 谁拥有数据
    // - 是否有数据竞争（需要 channel 或 mutex）
}
```

#### Rust：编译时检查

```rust
async fn main() {
    let data = vec![0u8; 1024];
    
    // ❌ 编译错误：data 被移动了
    // let handle1 = tokio::spawn(process1(data));
    // let handle2 = tokio::spawn(process2(data));  // 错误！
    
    // ✅ 方案 1：使用 Arc（共享所有权）
    let data = Arc::new(data);
    let handle1 = tokio::spawn(process1(data.clone()));
    let handle2 = tokio::spawn(process2(data.clone()));
    
    // ✅ 方案 2：使用 channel（转移所有权）
    let (tx1, rx1) = tokio::sync::oneshot::channel();
    let (tx2, rx2) = tokio::sync::oneshot::channel();
    tokio::spawn(async move { process1(data, tx1).await });
}
```

**关键差异：**

| 特性 | Go | Rust |
|------|-----|------|
| **内存管理** | GC 自动管理 | 编译时检查，零运行时开销 |
| **数据竞争** | 运行时检测（race detector） | 编译时防止 |
| **所有权** | 隐式（GC 管理） | 显式（编译时检查） |
| **性能** | GC 暂停可能影响性能 | 零 GC 开销 |

### 5.2 运行时可见性对比

#### Go：隐藏的复杂性

**Go 的运行时是"黑盒"：**

```go
// 用户代码
func main() {
    go doWork()  // 就这么简单
}

// 但实际发生的事（用户看不到）：
// 1. runtime 创建 G（goroutine）
// 2. 调度器决定在哪个 M（线程）上执行
// 3. 如果 M 不够，创建新的 M
// 4. 工作窃取算法分配任务
// 5. 网络 IO 时，使用 netpoller
// 6. GC 在后台运行
```

**用户无法控制：**
- Goroutine 的栈大小（默认 2KB，可增长到 1GB）
- 调度器的具体算法
- GC 的触发时机
- 网络 IO 的调度细节

#### Rust：可见的复杂性

**Tokio 的运行时是"白盒"：**

```rust
// 用户代码
#[tokio::main]
async fn main() {
    tokio::spawn(do_work()).await;
}

// 你可以看到和控制的：
// 1. 运行时类型（multi_thread/current_thread）
// 2. 线程数量配置
// 3. 调度器实现（可以自定义）
// 4. IO driver 的配置
```

**文件：`tokio/src/runtime/builder.rs`**

```rust
impl Builder {
    pub fn new_multi_thread() -> Builder {
        Builder {
            kind: Kind::Threaded,
            worker_threads: None,  // ⭐ 可以配置
            max_blocking_threads: 512,  // ⭐ 可以配置
            // ... 更多可配置项
        }
    }
    
    pub fn worker_threads(&mut self, val: usize) -> &mut Self {
        self.worker_threads = Some(val);  // ⭐ 用户控制
        self
    }
}
```

**用户可以控制：**
- 运行时类型和配置
- 线程数量和栈大小
- 调度器策略（可以自定义）
- IO driver 的行为

### 5.3 实际场景对比

#### 场景 1：简单并发任务

#### Go 实现

```go
func main() {
    var wg sync.WaitGroup
    
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            process(id)
        }(i)
    }
    
    wg.Wait()
}
```

**特点：**
- ✅ 代码简洁
- ✅ 不需要关心调度细节
- ⚠️ 无法控制 goroutine 的调度策略

#### Rust 实现

```rust
#[tokio::main]
async fn main() {
    let mut handles = Vec::new();
    
    for i in 0..1000 {
        let handle = tokio::spawn(async move {
            process(i).await
        });
        handles.push(handle);
    }
    
    // 必须显式等待
    for handle in handles {
        handle.await.unwrap();
    }
}
```

**特点：**
- ⚠️ 代码稍显冗长
- ✅ 可以控制运行时配置
- ✅ 编译时保证安全性

#### 场景 2：网络服务器

#### Go 实现

```go
func handleConnection(conn net.Conn) {
    defer conn.Close()
    // 处理连接
}

func main() {
    ln, _ := net.Listen("tcp", ":8080")
    for {
        conn, _ := ln.Accept()
        go handleConnection(conn)  // 就这么简单
    }
}
```

**Go 的优势：**
- 代码极简
- runtime 自动处理网络 IO 调度
- 抢占式调度防止阻塞

#### Rust 实现

```rust
async fn handle_connection(mut stream: TcpStream) {
    // 处理连接
}

#[tokio::main]
async fn main() {
    let listener = TcpListener::bind("127.0.0.1:8080").await.unwrap();
    
    loop {
        let (stream, _) = listener.accept().await.unwrap();
        tokio::spawn(handle_connection(stream));  // 必须显式 spawn
    }
}
```

**Rust 的优势：**
- 可以精确控制并发数（使用 semaphore）
- 可以自定义调度策略
- 编译时保证内存安全

#### 场景 3：CPU 密集型任务

#### Go 实现

```go
func cpuIntensiveTask() {
    // 长时间 CPU 计算
    for i := 0; i < 1000000000; i++ {
        compute()
    }
}

func main() {
    // runtime 会在函数调用点抢占
    go cpuIntensiveTask()
    go cpuIntensiveTask()
    // 其他 goroutine 仍能运行
}
```

**Go 的优势：**
- 抢占式调度保证公平性
- 不需要手动 yield

#### Rust 实现

```rust
async fn cpu_intensive_task() {
    // ⚠️ 危险：如果没有 await，会阻塞整个线程！
    for i in 0..1_000_000_000 {
        compute();
        // ✅ 必须定期 yield
        if i % 10000 == 0 {
            tokio::task::yield_now().await;
        }
    }
}

#[tokio::main]
async fn main() {
    // 或者使用专门的线程池
    tokio::task::spawn_blocking(|| {
        cpu_intensive_task_sync()
    });
}
```

**Rust 的挑战：**
- 必须主动 yield，否则会阻塞
- 需要使用 `spawn_blocking` 处理 CPU 密集型任务

### 5.4 性能对比

#### 任务创建开销

| 操作 | Go | Rust (Tokio) |
|------|-----|--------------|
| **创建任务** | ~200-300ns | ~100-200ns |
| **任务切换** | ~100-200ns | ~50-100ns |
| **内存开销** | ~2KB/goroutine | ~200-300B/task |

**Rust 的优势：**
- 任务更轻量
- 切换开销更低（协作式）

#### 运行时开销

| 特性 | Go | Rust |
|------|-----|------|
| **二进制大小** | +2-5MB (runtime) | 可选，可为零 |
| **内存占用** | GC 需要额外内存 | 无 GC 开销 |
| **延迟** | GC 暂停可能影响 | 无 GC 暂停 |

#### 实际性能

**网络 IO 密集型：**
- Go：优秀（netpoller 优化好）
- Rust：优秀（epoll/kqueue 直接使用）

**CPU 密集型：**
- Go：良好（抢占式调度保证公平）
- Rust：需要特殊处理（使用 `spawn_blocking`）

### 5.5 调试和问题排查

#### Go：隐藏复杂性带来的挑战

**问题场景：**
```go
func main() {
    go task1()  // 为什么这个 goroutine 执行慢？
    go task2()  // 为什么这个 goroutine 没有被调度？
}
```

**调试困难：**
- 无法直接看到调度器的决策
- 需要工具（如 `go tool trace`）来分析
- GC 暂停的影响难以预测

#### Rust：可见复杂性带来的优势

**问题场景：**
```rust
#[tokio::main]
async fn main() {
    tokio::spawn(task1());  // 可以追踪到具体的运行时
    tokio::spawn(task2());  // 可以看到调度器的实现
}
```

**调试优势：**
- 可以查看运行时的源代码
- 可以自定义调度器来调试
- 编译时错误帮助提前发现问题

## 6. 总结与参考资料

### 6.1 那段话的准确性分析

#### 准确的部分

1. ✅ **"Go 的并发模型，开个 goroutine 就完事了"** - 准确
2. ✅ **"runtime 帮你调度"** - 准确
3. ✅ **"Rust 不是这样——你得明确告诉它这个任务什么时候跑、在哪跑"** - 准确
4. ✅ **"把 Go 藏在 runtime 里的复杂性给拎出来了"** - 准确
5. ✅ **"Go 的调度器确实优秀，但它帮你做的决定，你看不见也改不了"** - 基本准确

#### 需要补充的部分

1. **"数据归谁管"** - 这更多是 Rust 所有权系统的问题，不仅仅是并发模型
2. **"出了问题你知道往哪查"** - 这需要补充：Rust 的编译时检查能防止很多问题，但运行时问题可能更难调试（因为复杂性暴露了）

#### 更准确的表述

> "Go 的并发模型通过隐藏复杂性提供了极简的 API，但这也意味着用户对调度细节的控制有限。Rust 的异步模型通过暴露复杂性，让用户能够精确控制任务的生命周期和调度策略，但这也带来了更高的学习成本和显式管理的负担。两种模型各有优劣：Go 适合快速开发和简单场景，Rust 适合需要精确控制和零成本抽象的场景。"

### 6.2 三种模型的本质差异

#### 设计哲学

| 模型 | 设计哲学 | 核心特点 |
|------|---------|---------|
| **Go** | 隐藏复杂性，提供极简 API | GMP 模型自动调度，抢占式保证公平 |
| **Rust** | 暴露复杂性，提供精确控制 | 可选运行时，协作式调度，零成本抽象 |
| **Java VT** | 兼容性优先，渐进式改进 | 类似传统线程 API，协作式调度（阻塞时） |

#### 适用场景总结

**Go Goroutines：**
- ✅ 快速开发，高并发 I/O
- ✅ CPU 密集型（抢占式优势）
- ❌ 需要零运行时开销的场景

**Rust Async：**
- ✅ 极致性能，资源受限环境
- ✅ 需要编译时安全保证
- ❌ 快速原型，团队学习成本高

**Java Virtual Threads：**
- ✅ 现有 Java 代码库升级
- ✅ I/O 密集型，需要简单 API
- ❌ CPU 密集型（无抢占）
- ❌ 需要零 GC 暂停的场景

#### 那段话的准确性（更新版）

原话基本准确，但需要补充 Java Virtual Threads 的视角：

> "Go 的并发模型通过隐藏复杂性（GMP 模型）提供了极简的 API，但这也意味着用户对调度细节的控制有限。Rust 的异步模型通过暴露复杂性，让用户能够精确控制任务的生命周期和调度策略，但这也带来了更高的学习成本和显式管理的负担。Java Virtual Threads 试图在两者之间找到平衡：保持 API 的简单性（类似传统线程），同时提供轻量级并发能力，但受限于 JVM 生态和协作式调动的局限性。三种模型各有优劣：Go 适合快速开发和需要抢占式调度的场景，Rust 适合需要精确控制和零成本抽象的场景，Java Virtual Threads 适合现有 Java 代码库的渐进式升级。"

### 6.3 参考资料

- [Tokio 文档 - Tasks](https://docs.rs/tokio/latest/tokio/task/index.html)
- [Tokio 文档 - Runtime](https://docs.rs/tokio/latest/tokio/runtime/index.html)
- [Go 调度器设计文档](https://docs.google.com/document/d/1TTj4T2JO42uD5ID9e89oa0sLKhJYD0Y_kqxDv3I3XMw/edit)
- [Go Runtime Hacking Guide](https://go.dev/src/runtime/HACKING.md)
- [Rust 异步编程指南](https://rust-lang.github.io/async-book/)
- [Java Virtual Threads (Project Loom)](https://openjdk.org/jeps/444)
- [Inside Java: Virtual Threads](https://inside.java/2023/10/30/sip086/)

---

*本文档基于 Tokio 源代码、Go runtime 公开文档和 Java Virtual Threads 规范分析。实际实现可能因版本更新而有所变化。*
