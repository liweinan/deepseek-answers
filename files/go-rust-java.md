# Go vs Rust vs Java Virtual Threads 并发模型深度对比

## 引言

> "从 Go 过来学 Rust，有些地方特别别扭。Go 的并发模型，开个 goroutine 就完事了，runtime 帮你调度。Rust 不是这样——你得明确告诉它这个任务什么时候跑、在哪跑、数据归谁管。一开始我觉得这是 Rust 在折腾人，学了一阵子才明白，这其实是把 Go 藏在 runtime 里的复杂性给拎出来了。Go 的调度器确实优秀，但它帮你做的决定，你看不见也改不了。Rust 让你直面这些决定——累是累点，但出了问题你知道往哪查。"

这段话**基本准确**，但需要更细致的分析。本文档基于 Tokio 的实现，深入对比三种主流并发模型：**Go Goroutines**、**Rust Async (Tokio)** 和 **Java Virtual Threads (Project Loom)**。

**自学阅读建议**：先分别读 §2 Go 核心实现、§3 Rust 核心实现、§4 Java Virtual Threads 核心实现（核心 struct 与设计思路）；再读 §5 横向对比、§6 总结与参考资料。Go 源码以 [golang/go](https://github.com/golang/go) 主线为准，Java 以 [openjdk/loom](https://github.com/openjdk/loom) 为准，可克隆后按符号名搜索校订。

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

以下基于 OpenJDK Loom 源码（[openjdk/loom](https://github.com/openjdk/loom)），路径以 `loom/src/java.base/share/classes` 为根。

### 4.1 设计理念

Java Virtual Threads（虚拟线程）是 Java 19 引入、Java 21 稳定的特性，提供类似 Go goroutines 的轻量级并发，兼容传统 Thread API。核心：**虚拟线程**（用户态、栈由 Continuation 管理在堆上）、**Carrier Threads**（平台线程承载）、阻塞时**自动卸载**（Continuation.yield）。

#### VT、Thread、Executor、Scheduler 的核心关系

与 Go 的 GMP 类似，Java 虚拟线程模型也有清晰的层次与绑定关系：

**执行关系：VT ↔ Scheduler ↔ Carrier (Platform Thread)**

```
Java Virtual Threads 模型
│
├─ 用户层：ExecutorService / Thread API
│  ├─ Executors.newVirtualThreadPerTaskExecutor() → 每 submit 一个任务，创建一个 VT
│  ├─ Thread.ofVirtual().start(task) → 直接创建一个 VT 并调度
│  └─ 不池化 VT；VT 是轻量级，按任务创建即可
│
├─ VT 层：Virtual Thread (VT)
│  ├─ 轻量级执行单元，栈在堆上（Continuation）
│  ├─ 绑定一个 VirtualThreadScheduler（创建时指定，默认 built-in）
│  ├─ 挂载时绑定一个 Carrier（Platform Thread），即 carrierThread 字段
│  └─ 状态：NEW → STARTED → RUNNING（挂载）/ PARKED（卸载）/ BLOCKED（卸载）/ TERMINATED
│
├─ 调度层：VirtualThreadScheduler
│  ├─ 接口：onStart(VirtualThreadTask)、onContinue(VirtualThreadTask)
│  ├─ Built-in 实现：ForkJoinPool（BuiltinForkJoinPoolScheduler）
│  │   ├─ Worker 线程 = CarrierThread（即 Carrier）
│  │   ├─ parallelism = CPU 核心数（默认），可配 jdk.virtualThreadScheduler.parallelism
│  │   └─ onStart/onContinue 将 VT 的 runContinuation 作为 FJP 任务提交
│  └─ 可替换为自定义 Scheduler（实现 VirtualThreadScheduler）
│
└─ Carrier 层：Platform Thread (Carrier)
   ├─ 执行 VT 时 = CarrierThread（FJP 的 worker）
   ├─ 一个 Carrier 同时只执行一个 VT（mount 后 cur VT 即该 VT）
   ├─ 一个 VT 挂载时只在一个 Carrier 上；卸载后可由任意 Carrier 再次挂载
   └─ VT 阻塞时 yield 卸载，Carrier 去执行其他 VT 的 runContinuation
```

**关键约束：**

1. **Executor 与 VT 的关系：按任务创建，不池化**
   - **ExecutorService（newVirtualThreadPerTaskExecutor）**：每次 `submit(task)` 创建一个新的 VT，执行完即结束，不重用 VT。
   - **Thread.ofVirtual().start(task)**：同样创建一个 VT，交给默认 Scheduler 调度。
   - VT 创建成本低，设计上不池化；需要限流时用 Semaphore 等，而不是减少 VT 数量。

2. **VT 与 Scheduler 的关系：一对一绑定**
   - 每个 VT 在构造时绑定一个 **VirtualThreadScheduler**（可为 null，表示用默认 built-in）。
   - VT 的 `start()` 调用 `scheduler.onStart(runContinuation)`；阻塞后恢复调用 `scheduler.onContinue(runContinuation)`。
   - 默认 Scheduler 是单个全局 ForkJoinPool 实例（built-in），所有使用默认 Scheduler 的 VT 共享同一 FJP。

3. **Scheduler 与 Carrier（Platform Thread）的关系：一对多管理**
   - Built-in Scheduler（ForkJoinPool）拥有若干 **CarrierThread**（worker），数量由 parallelism/maxPoolSize 等决定。
   - Scheduler 把 VT 的 runContinuation 作为任务提交到 FJP；FJP 的 worker（Carrier）从队列取任务执行，即挂载并运行某个 VT。
   - 与 Go 的 P 管理多个 G 类似：一个 FJP 管理多个 VT 任务，一个 Carrier 同时只执行一个 VT。

4. **VT 与 Carrier 的关系：挂载时一对一，可迁移**
   - **挂载（mount）**：某 Carrier 执行某 VT 的 `runContinuation()` 时，该 VT 的 `carrierThread` 指向该 Carrier，VT 状态为 RUNNING/PINNED 等（mounted）。
   - **卸载（unmount）**：VT 阻塞时 `cont.yield()` 成功，VT 与 Carrier 解绑，`carrierThread` 清空，VT 状态变为 PARKED/BLOCKED 等（unmounted）；runContinuation 再次被 onContinue 提交后，可能被**任意** Carrier 取到并挂载。
   - 因此：**一个 VT 同一时刻至多在一个 Carrier 上**；**一个 Carrier 同一时刻至多执行一个 VT**；VT 在不同时刻可由不同 Carrier 执行（迁移）。

**数量关系：**

| 角色 | 数量 | 说明 |
|------|------|------|
| **VT** | 无上限 | 按任务创建，可成千上万 |
| **Scheduler（built-in）** | 通常 1 个 | 全局默认 ForkJoinPool，可配自定义 Scheduler |
| **Carrier（FJP worker）** | parallelism（默认 = CPU 核心数） | 可配 jdk.virtualThreadScheduler.parallelism、maxPoolSize |
| **Platform Thread（非 carrier）** | 用户创建 | 若用 Thread.ofPlatform() 或传统线程池，与 VT 的 carrier 池独立 |

**与 Go GMP 的类比（便于对照）：**

| Go | Java Virtual Threads |
|----|----------------------|
| G（goroutine） | VT（Virtual Thread） |
| P（逻辑处理器，本地队列） | Scheduler（FJP）+ FJP 的每个 worker 的本地队列 |
| M（OS 线程） | Carrier（Platform Thread，即 CarrierThread） |
| G 在 P 的 runq 中排队，M 绑定 P 后取 G 执行 | VT 的 runContinuation 在 FJP 队列中，Carrier 取任务执行即挂载 VT |
| G 阻塞时 M 可释放 P，P 被其他 M 接管 | VT 阻塞时卸载，runContinuation 再次入队，可被其他 Carrier 挂载 |

#### VT 与 Continuation 的关系；Continuation 的设计思路

**VT 与 Continuation 的关系**

- **VT 持有一个 Continuation**：每个 VirtualThread 在构造时创建一个 **VThreadContinuation**（继承 `Continuation`），其 `target` 是包装了用户 task 的 Runnable；VT 的 `cont` 字段即该实例。
- **VT 的“栈”由 Continuation 管理**：平台线程的栈在 OS 管理的栈上；虚拟线程没有自己的 OS 栈，执行时的栈帧在 **Continuation 的栈** 上。该栈在 **yield 时被保存到堆**（`StackChunk` 链表），再次 **run 时从堆恢复**，因此才有“栈在堆上”的说法。
- **执行与挂起**：Carrier 执行 VT 时调用 `runContinuation()` → `mount()` → `cont.run()`。`cont.run()` 要么首次执行 `target.run()`（用户代码），要么从上次 yield 点恢复。用户代码中发生阻塞（如 LockSupport.park、阻塞 I/O、monitor 进入）时，会调用 **Continuation.yield(scope)**；yield 将当前栈保存到堆并返回到 run() 的调用者，VT 随之卸载，Carrier 可去执行其他 VT。之后 scheduler 再次把该 VT 的 runContinuation 提交给某个 Carrier，再次 `cont.run()` 时从 yield 点继续执行。
- **小结**：VT 是“线程”的抽象（Thread API、状态、调度）；Continuation 是“可挂起/恢复的执行体”，负责保存与恢复 VT 的栈与执行点。**VT = Thread 语义 + Continuation 实现**。

**Continuation 的设计思路**

Loom 的 Continuation 是 **one-shot delimited continuation**（单次、有界延续）：

1. **Delimited（有界）**：延续有明确边界，由 **ContinuationScope** 界定。`Continuation(scope, target)` 表示“在 scope 内执行 target”；`yield(scope)` 表示“挂起到 scope 边界”。Virtual Thread 使用全局的 `VTHREAD_SCOPE`，因此 VT 的 yield 就是挂起整个 VT 的执行点。

2. **One-shot（单次）**：每个 Continuation 实例只支持“运行到结束”或“yield 后再 run 一次恢复”。不能对同一实例多次 run 到多次 yield；VT 的多次挂起/恢复是通过多次调用 run（每次 run 可能内部 yield 再被 scheduler 再次提交 run）实现的。

3. **栈在堆上（StackChunk）**：执行时 Continuation 的栈帧在 JVM 管理的 **StackChunk** 链上（堆上对象）。yield 时当前栈被完整保存到这些 chunk；恢复时从 chunk 恢复栈，再继续执行。这样 VT 的栈不占用 Carrier 的 OS 栈，可以存在任意多个 VT，且切换成本与栈大小相关而非固定 OS 栈大小。

   **什么是「栈在堆上」**：传统平台线程的「栈」是 OS 为每条线程预留的一块连续内存（栈段），用于存放调用栈——即方法调用链上的栈帧（局部变量、返回地址等）。「栈在堆上」指：虚拟线程没有自己的 OS 栈段，其调用栈数据存放在 **Java 堆** 里，用 `StackChunk` 等对象串成链表。挂载到 Carrier 时，JVM 可把栈帧拷到 Carrier 的 OS 栈上执行；阻塞/yield 时再拷回堆上的 StackChunk。这样每条 VT 不占一块固定的 OS 栈（通常 1MB 级），才能支持数十万级 VT；且 yield 时整栈可完整保存与恢复，实现 continuation。

   **与 Go 的相似性**：这种「栈在堆上」的设计与 **Go 的 goroutine 更接近**。Go 的 G 的栈也是 **堆上分配**（`stack stack` 指向 [lo, hi]，初始约 2KB、可分段增长），不占用 OS 线程的栈段，因此才能有大量 goroutine。二者都是「有栈」轻量级单元、栈在堆上、由运行时管理。Rust 的 async 任务则是 **栈无关（stackless）** 状态机：没有独立的调用栈，只在 `await` 点把局部变量放进状态机，不涉及「栈在堆上」或整栈拷贝，与 Java/Go 的栈式设计不同。

4. **Pinned**：当栈上有 **native 帧**、线程在 **critical section**（如持有 synchronized）或处于**异常**等状态时，JVM 无法安全地把栈拷贝到堆，此时 **yield 会失败**，Continuation 处于 Pinned 状态，VT 无法卸载，只能占用当前 Carrier 直到可 yield。因此 VT 内应避免 synchronized，改用 ReentrantLock 等，以便在阻塞时正常 yield 卸载。

**源码对应（节选）**

**文件：`jdk/internal/vm/Continuation.java`（约第 40-134 行）**

```java
/**
 * A one-shot delimited continuation.
 */
public class Continuation {
    private final Runnable target;           // ⭐ 延续体：首次 run 时执行
    private final ContinuationScope scope;   // ⭐ 有界范围，yield(scope) 时挂起到此边界
    private Continuation parent;
    private Continuation child;

    private StackChunk tail;                 // ⭐ yield 后栈帧保存在堆上的 chunk 链表
    private boolean done;                    // ⭐ 是否已执行完毕
    private volatile boolean mounted;         // 是否正挂在某条线程上
    private Object yieldInfo;                // yield 时携带的信息

    public Continuation(ContinuationScope scope, Runnable target) {
        this.scope = scope;
        this.target = target;
    }

    /**
     * Mounts and runs the continuation body. If suspended, continues from the last suspend point.
     */
    public final void run() {
        // mount；设置当前线程的 continuation；若未启动则执行 target，否则从上次 yield 点恢复
        // enterSpecial 为 native，内部会执行 target 或恢复栈后返回
        // 若发生 yield，栈被保存到 StackChunk，控制权返回到 run() 的调用者
    }
}
```

**文件：`java/lang/VirtualThread.java`（VThreadContinuation）**

```java
    private static class VThreadContinuation extends Continuation {
        VThreadContinuation(VirtualThread vthread, Runnable task) {
            super(VTHREAD_SCOPE, wrap(vthread, task));  // ⭐ scope 固定为 VT 的 scope，target 为包装了 task 的 Runnable
        }
        @Override
        protected void onPinned(Continuation.Pinned reason) { }  // yield 失败（Pinned）时的回调
    }
```

因此：**VT 的“轻量级”和“栈在堆上”** 都来自 Continuation：栈用堆上的 StackChunk 表示，yield 时保存、run 时恢复，从而可在少量 Carrier 上多路复用大量 VT。

#### Java Continuation 与 Rust 协程的对比

Loom 文档和 Foojay 等文章里把 Continuation 称为 **delimited continuation** 或 **coroutine**；Rust 里 `async fn` 被编译器变换成的也是 **coroutine**（状态机）。两者都实现“挂起—恢复”，但实现方式不同，对比如下。

| 维度 | Java Continuation (Loom) | Rust 协程（async/await 状态机） |
|------|---------------------------|----------------------------------|
| **实现方式** | **栈式（stackful）**：yield 时把**完整调用栈**保存到堆（StackChunk），恢复时从堆还原栈 | **栈无关（stackless）**：编译器把 `async fn` 变成**状态机**，每个 `await` 点对应一个状态，只保存该点需要的**局部变量**，不保存整栈 |
| **挂起点** | 任意阻塞点（JDK 在阻塞处插入 yield）：LockSupport.park、阻塞 I/O、Object.wait 等 | 仅 **`await` 点**：必须显式写 `await`，只有这些点会挂起并保存状态 |
| **栈从哪来** | VT 的栈在堆上（Continuation 的 StackChunk），挂载时帧可拷贝到 Carrier 栈，卸载时拷回堆 | 无“VT 自己的栈”：状态机本身在堆或栈上，执行时用**当前线程栈**，挂起时只保留状态机里的字段 |
| **与线程 API** | VT 是 `Thread` 的一种实现，沿用 `Thread` API；阻塞式代码可直接在 VT 里跑，由 JVM 在阻塞点 yield | 必须用 `async fn` + `await`，阻塞式代码不能直接写在 async 里，否则会占住线程；需“async 一路”或 `spawn_blocking` |
| **调度** | VT 阻塞 → yield Continuation → runContinuation 再次入队 → 任意 Carrier 可执行 | Future 在 `await` 返回 `Poll::Pending` → 运行时把 task 挂起 → 其他 task 被调度；恢复时从状态机当前状态继续 |
| **共性** | 都可挂起并在之后恢复；都用于在少量 OS 线程上多路复用大量逻辑任务（M:N） | 同上 |

**简要结论**：

- **概念上**：都是“可挂起、可恢复的执行体”，都算广义的 **coroutine**，也都用来做轻量级并发。
- **实现上**：Java 是 **栈式 continuation**（栈在堆上、任意阻塞点可挂起），Rust 是 **栈无关协程**（状态机、仅 await 点挂起）。Java 更接近“传统”的 fiber/有栈协程；Rust 更接近 generator/无栈协程，零成本抽象、无整栈拷贝。
- **使用体验**：Java VT 允许在虚拟线程里写阻塞式代码，由 JVM 在阻塞点自动 yield；Rust 必须在 async 里写非阻塞 + await，或把阻塞丢到 `spawn_blocking`。

更多 Loom/Continuation 的直观介绍可参考：[*The Basis of Virtual Threads: Continuations* (foojay.io)](https://foojay.io/today/the-basis-of-virtual-threads-continuations/)。

### 4.2 核心结构与调度

VirtualThread 是 JVM 调度的线程，不直接对应 OS 线程。下面给出 Loom 源码中的核心类与字段，便于自学时对照。

#### 4.2.1 VirtualThread 类核心字段（节选）

**文件：`java.base/share/classes/java/lang/VirtualThread.java`（约第 68-215 行）**

```java
/**
 * A thread that is scheduled by the Java virtual machine rather than the operating system.
 */
final class VirtualThread extends BaseVirtualThread {
    private static final ContinuationScope VTHREAD_SCOPE = new ContinuationScope("VirtualThreads");

    private static final VirtualThreadScheduler BUILTIN_SCHEDULER;
    private static final VirtualThreadScheduler DEFAULT_SCHEDULER;
    // ...

    // ⭐ scheduler and continuation
    private final VirtualThreadScheduler scheduler;
    private final Continuation cont;
    private final VirtualThreadTask runContinuation;

    // ⭐ virtual thread state, accessed by VM
    private volatile int state;

    // parking / blocking / yield 相关
    private volatile boolean parkPermit;
    private volatile boolean blockPermit;
    // ...

    // ⭐ carrier thread when mounted, accessed by VM
    private volatile Thread carrierThread;

    // termination when joining
    private volatile CountDownLatch termination;
    // ...
}
```

#### 4.2.2 VirtualThread 状态常量

**文件：`java.base/share/classes/java/lang/VirtualThread.java`（约第 156-184 行）**

```java
    private static final int NEW      = 0;
    private static final int STARTED  = 1;
    private static final int RUNNING  = 2;     // runnable-mounted

    // untimed and timed parking
    private static final int PARKING       = 3;
    private static final int PARKED        = 4;     // unmounted
    private static final int PINNED        = 5;     // mounted（cont.yield 失败，固定在 carrier）
    private static final int TIMED_PARKING = 6;
    private static final int TIMED_PARKED  = 7;     // unmounted
    private static final int TIMED_PINNED  = 8;     // mounted
    private static final int UNPARKED      = 9;     // unmounted but runnable

    // Thread.yield
    private static final int YIELDING = 10;
    private static final int YIELDED  = 11;         // unmounted but runnable

    // monitor enter
    private static final int BLOCKING  = 12;
    private static final int BLOCKED   = 13;        // unmounted
    private static final int UNBLOCKED = 14;         // unmounted but runnable

    // monitor wait / timed-wait
    private static final int WAITING       = 15;
    private static final int WAIT          = 16;
    private static final int TIMED_WAITING = 17;
    private static final int TIMED_WAIT    = 18;

    private static final int TERMINATED = 99;       // final state
```

**与调度流程的对应关系**：NEW → STARTED → RUNNING（挂载到 carrier）；RUNNING → PARKING → PARKED（yield 成功，已卸载）或 PINNED（yield 失败，留在 carrier）；RUNNING → BLOCKING → BLOCKED（monitor 阻塞，卸载）；RUNNING → YIELDING → YIELDED（Thread.yield 成功）；终态 TERMINATED。

#### 4.2.3 VThreadContinuation 与 runContinuation()

**文件：`java.base/share/classes/java/lang/VirtualThread.java`（约第 358-429 行）**

```java
    /** The continuation that a virtual thread executes. */
    private static class VThreadContinuation extends Continuation {
        VThreadContinuation(VirtualThread vthread, Runnable task) {
            super(VTHREAD_SCOPE, wrap(vthread, task));
        }
        @Override
        protected void onPinned(Continuation.Pinned reason) { }
        // wrap 内调用 vthread.run(task)
    }

    /**
     * Runs or continues execution on the current thread. The virtual thread is mounted
     * on the current thread before the task runs or continues. It unmounts when the
     * task completes or yields.
     */
    @ChangesCurrentThread
    private void runContinuation() {
        if (Thread.currentThread().isVirtual()) {
            throw new WrongThreadException();
        }
        // set state to RUNNING（从 STARTED/UNPARKED/UNBLOCKED/YIELDED 转换）
        // ...
        mount();
        try {
            cont.run();   // ⭐ 执行或恢复 Continuation
        } finally {
            unmount();
            if (cont.isDone()) {
                afterDone();
            } else {
                afterYield();   // ⭐ 调用 scheduler.onContinue(runContinuation)
            }
        }
    }
```

挂载/卸载在 `runContinuation()` 内完成：`mount()` → `cont.run()` → `unmount()`；yield 时 `cont.yield()` 成功则卸载，`afterYield()` 将 runContinuation 再次提交给 scheduler。

#### 4.2.4 Continuation 与 Pinned

**文件：`java.base/share/classes/jdk/internal/vm/Continuation.java`（约第 40-62 行）**

```java
/**
 * A one-shot delimited continuation.
 */
public class Continuation {
    private final Runnable target;
    private final ContinuationScope scope;
    // StackChunk tail 等栈相关字段
    // ...

    /** Reason for pinning（无法卸载的原因） */
    public enum Pinned {
        /** Native frame on stack */ NATIVE,
        /** In critical section */   CRITICAL_SECTION,
        /** Exception (OOME/SOE) */  EXCEPTION
    }
}
```

虚拟线程的栈由 Continuation 保存/恢复；`run()` 执行到 yield 时挂起，再次 `run()` 从挂起点继续。若栈上有 native 帧、在 critical section（如 synchronized）或异常，则 Pinned，无法卸载，只能在当前 carrier 上阻塞。

#### 4.2.5 CarrierThread

**文件：`java.base/share/classes/jdk/internal/misc/CarrierThread.java`（约第 36-60 行）**

```java
/**
 * A ForkJoinWorkerThread that can be used as a carrier thread.
 */
public class CarrierThread extends ForkJoinWorkerThread {
    // compensating state for blocking
    private int compensating;
    private long compensateValue;

    public CarrierThread(ForkJoinPool pool) {
        super(CARRIER_THREADGROUP, pool, true);
        // ...
    }

    /** Mark the start of a blocking operation. */
    public boolean beginBlocking() {
        // Continuation.pin(); 然后 FJP.tryCompensate 启动或激活备用线程
        compensateValue = ForkJoinPools.beginCompensatedBlock(getPool());
        // ...
    }
    // endBlocking() 对应 endCompensatedBlock
}
```

Built-in 调度器下的 carrier 即 FJP 的 worker 线程；`beginBlocking()` / `endBlocking()` 通过 FJP 的 compensated block 在 VT 阻塞时临时增加 worker，避免饿死。

#### 4.2.6 BuiltinForkJoinPoolScheduler

**文件：`java.base/share/classes/java/lang/VirtualThread.java`（约第 1538-1605 行）**

```java
    private static VirtualThreadScheduler createBuiltinScheduler(boolean wrapped) {
        int parallelism = Runtime.getRuntime().availableProcessors();  // 可配 jdk.virtualThreadScheduler.parallelism
        int maxPoolSize = Integer.max(parallelism, 256);               // 可配 jdk.virtualThreadScheduler.maxPoolSize
        int minRunnable = Integer.max(parallelism / 2, 1);             // 可配 jdk.virtualThreadScheduler.minRunnable
        // ...
        return new BuiltinForkJoinPoolScheduler(parallelism, maxPoolSize, minRunnable, wrapped);
    }

    /** The built-in ForkJoinPool scheduler. */
    private static class BuiltinForkJoinPoolScheduler
            extends ForkJoinPool implements VirtualThreadScheduler {

        BuiltinForkJoinPoolScheduler(int parallelism, int maxPoolSize, int minRunnable, boolean wrapped) {
            ForkJoinWorkerThreadFactory factory = wrapped
                    ? ForkJoinPool.defaultForkJoinWorkerThreadFactory
                    : CarrierThread::new;   // ⭐ worker 即 carrier
            boolean asyncMode = true;       // FIFO
            super(parallelism, factory, handler, asyncMode,
                    0, maxPoolSize, minRunnable, pool -> true, 30L, SECONDS);
        }

        @Override
        public void onStart(VirtualThreadTask task) {
            adaptAndExecute(task);   // execute(ForkJoinTask.adapt(task))
        }

        @Override
        public void onContinue(VirtualThreadTask task) {
            adaptAndExecute(task);
        }
    }
```

onStart/onContinue 均将 runContinuation 作为 FJP 任务提交；FJP 的 worker 由 CarrierThread 担任，工作窃取与本地队列与 Go 的 P 本地队列在概念上类似。

**创建与执行流程（高层）**：`Thread.ofVirtual().start(task)` → 创建 VirtualThread（scheduler、Continuation 包装 task）→ `start()` → `scheduler.onStart(runContinuation)` → FJP 某 worker 执行 `runContinuation.run()` → `mount()` → `cont.run()` 执行用户 task；阻塞时 `cont.yield()` 卸载，`afterYield()` 里 `scheduler.onContinue(runContinuation)` 再次入队；其他 worker 或本 worker 之后取到后再次 `runContinuation()` → `unmount()` 已由上次 yield 完成，再次 `cont.run()` 继续。

### 4.3 与 Executor、线程池的关系

`Executors.newVirtualThreadPerTaskExecutor()` 为每个 `submit` 的任务创建新的 VirtualThread，不池化 VT；carrier 池由 built-in 的 ForkJoinPool 提供（即上述 scheduler）。CPU 密集型应使用平台线程池（如 `ThreadPoolExecutor`），避免长时间占用 carrier。设计要点：VT 不池化、用 Semaphore 限流、避免在 VT 内使用 `synchronized`（会 pin，无法卸载）。

### 4.4 优势与局限

**优势**：API 与 Thread 一致、迁移成本低、I/O 密集场景下自动卸载、JFR/调试器支持好。**局限**：无 CPU 抢占（纯协作式）、`synchronized`/native 导致 pinning、依赖 JVM/GC、carrier 数量与策略可通过系统属性有限配置（如 `jdk.virtualThreadScheduler.parallelism`）。

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

#### Java：Virtual Thread 创建

```java
// 方式 1：Thread.ofVirtual()
Thread vt = Thread.ofVirtual().name("worker-", 0).start(() -> {
    process();
});

// 方式 2：Executors（每任务一 VT）
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 1000; i++) {
        final int id = i;
        executor.submit(() -> process(id));
    }
}
```

**特点**：API 与平台线程一致；VT 由 JVM 调度，阻塞时自动卸载，不占用 OS 线程；默认 carrier 池为 ForkJoinPool（parallelism = CPU 核心数）。

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

| 特性 | Go | Rust (Tokio) | Java Virtual Threads |
|------|-----|--------------|------------------------|
| **调度方式** | 抢占式（函数调用点） | 协作式（await 点） | 协作式（阻塞时卸载） |
| **抢占点** | 函数调用 + 异步信号 | 仅 await | 无 CPU 抢占；仅 I/O/锁/ park 时让出 |
| **阻塞风险** | 低（runtime 会抢占） | 高（必须主动 yield） | I/O 阻塞自动卸载；CPU 密集会占满 carrier |
| **性能开销** | 抢占检查有开销 | 零开销（只在 await 点切换） | 阻塞时 yield 有切换开销 |
| **可预测性** | 较低（抢占时机不确定） | 高（只在明确 await 点切换） | 高（仅在阻塞/ park 点切换） |

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

| 特性 | Go | Rust | Java Virtual Threads |
|------|-----|------|------------------------|
| **内存管理** | GC 自动管理 | 编译时检查，零运行时开销 | GC 自动管理 |
| **数据竞争** | 运行时检测（race detector） | 编译时防止 | 运行时可能发生（需同步） |
| **所有权** | 隐式（GC 管理） | 显式（编译时检查） | 隐式（GC 管理） |
| **性能** | GC 暂停可能影响性能 | 零 GC 开销 | GC 暂停可能影响性能 |

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

#### Java：部分可见

**Virtual Thread 的调度对用户部分可见：**

- **可见**：`Thread.ofVirtual()` / `Executors.newVirtualThreadPerTaskExecutor()`；可通过系统属性配置 carrier 池：`jdk.virtualThreadScheduler.parallelism`、`jdk.virtualThreadScheduler.maxPoolSize`、`jdk.virtualThreadScheduler.minRunnable`；`VirtualThreadSchedulerMXBean` 可观测调度器；JFR 有 VirtualThread 相关事件。
- **不可见**：具体在哪个 carrier 上执行、FJP 工作窃取细节、挂载/卸载时机由 JVM 决定；自定义 scheduler 需实现 `VirtualThreadScheduler` 接口（Loom 支持）。

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

#### Java 实现

```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<?>> futures = new ArrayList<>();
    for (int i = 0; i < 1000; i++) {
        final int id = i;
        futures.add(executor.submit(() -> process(id)));
    }
    for (Future<?> f : futures) f.get();
}
```

**特点：**
- ✅ API 与 Thread/Executor 一致，迁移成本低
- ✅ 每任务一 VT，阻塞时自动卸载
- ⚠️ CPU 密集时无抢占，会占满 carrier

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

#### Java 实现

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor();
     var server = ServerSocket.open(8080)) {
    while (true) {
        Socket conn = server.accept();
        executor.submit(() -> {
            try (conn) {
                handleConnection(conn);
            }
        });
    }
}
```

**Java 的优势：**
- ✅ 代码与平台线程写法一致
- ✅ I/O 阻塞时 VT 自动卸载，不占用 OS 线程
- ✅ 可创建大量 VT 处理并发连接

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

#### Java 实现

```java
// ⚠️ VT 无 CPU 抢占，CPU 密集会占满 carrier，应使用平台线程池
ExecutorService cpuExecutor = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors());
cpuExecutor.submit(() -> cpuIntensiveTask());
cpuExecutor.submit(() -> cpuIntensiveTask());
// 或：Thread.ofPlatform().start(() -> cpuIntensiveTask());
```

**Java 的局限：**
- ⚠️ Virtual Thread 无抢占，长时间 CPU 循环会阻塞 carrier
- ✅ CPU 密集应使用 `Executors.newFixedThreadPool` 或 `Thread.ofPlatform()`

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

| 操作 | Go | Rust (Tokio) | Java Virtual Threads |
|------|-----|--------------|------------------------|
| **创建任务** | ~200-300ns | ~100-200ns | ~几百 ns |
| **任务切换** | ~100-200ns | ~50-100ns | 阻塞时卸载/挂载，数百 ns 级 |
| **内存开销** | ~2KB/goroutine | ~200-300B/task | 栈在堆上，几 KB 级 |

#### 运行时开销

| 特性 | Go | Rust | Java Virtual Threads |
|------|-----|------|------------------------|
| **二进制/运行时** | +2-5MB (runtime) | 可选，可为零 | JVM 开销（较大） |
| **内存占用** | GC 需要额外内存 | 无 GC 开销 | GC 需要额外内存 |
| **延迟** | GC 暂停可能影响 | 无 GC 暂停 | GC 暂停可能影响 |

#### 实际性能

**网络 IO 密集型：**
- Go：优秀（netpoller 优化好）
- Rust：优秀（epoll/kqueue 直接使用）
- Java VT：优秀（阻塞时自动卸载，大量 VT 多路复用少量 carrier）

**CPU 密集型：**
- Go：良好（抢占式调度保证公平）
- Rust：需特殊处理（使用 `spawn_blocking`）
- Java VT：不推荐用 VT（无抢占）；应使用平台线程池

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

#### Java：JVM 工具与 JFR

**调试与观测：**
- JFR（Java Flight Recorder）有 VirtualThreadStart/End、VirtualThreadPark 等事件
- 调试器中 VT 显示为普通线程，栈追踪完整
- `VirtualThreadSchedulerMXBean` 可观测 carrier 池与调度器
- 线程转储（jstack）会列出虚拟线程

**局限：** carrier 调度细节由 JVM 决定，pinning 时需结合栈与锁分析。

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
- [OpenJDK Loom 源码](https://github.com/openjdk/loom)（`java.base/share/classes/java/lang/VirtualThread.java`、`jdk/internal/vm/Continuation.java`、`jdk/internal/misc/CarrierThread.java`）
- [Inside Java: Virtual Threads](https://inside.java/2023/10/30/sip086/)
- [The Basis of Virtual Threads: Continuations (foojay.io)](https://foojay.io/today/the-basis-of-virtual-threads-continuations/)

---

*本文档基于 Tokio 源代码、Go runtime 公开文档和 Java Virtual Threads 规范分析。实际实现可能因版本更新而有所变化。*
