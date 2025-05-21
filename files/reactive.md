# Mutiny 的 `chain` 方法介绍

Mutiny 是一个响应式编程库，主要用于 Java 的异步和事件驱动编程。`chain` 方法是 Mutiny API 中的一个重要方法，用于将多个操作串联起来形成处理流水线。

## 基本概念

`chain` 方法允许你将多个异步操作串联起来，形成一个连续的处理链。它类似于其他响应式库中的 `flatMap` 或 `then` 操作。

## 主要特点

1. **顺序执行**：`chain` 确保操作按顺序执行，前一个操作完成后才会执行下一个
2. **类型安全**：保持类型一致性，确保链中的每个步骤都正确处理数据类型
3. **错误传播**：如果链中任何一步失败，错误会沿着链传播

## 基本用法

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res))
    .chain(res -> thirdOperation(res));
```

## 与 `onItem().transform()` 的区别

- `transform` 是同步转换
- `chain` 用于异步操作，返回的是 `Uni` 或 `Multi`

## 示例

```java
Uni<String> fetchUser = getUserById(userId)
    .chain(user -> fetchUserDetails(user))
    .chain(details -> processDetails(details));
```

## 错误处理

可以在链中添加错误处理：

```java
Uni<String> result = operation()
    .chain(res -> nextStep(res))
    .onFailure().recoverWithItem(fallbackValue);
```

`chain` 方法是 Mutiny 中构建复杂异步流程的基础构建块，使得异步代码能够保持可读性和可维护性。

---

# 在 Mutiny 中处理链式操作中的运行时错误

在 Mutiny 的 `chain` 方法链中处理运行时错误是非常重要的，这样可以构建健壮的异步应用程序。以下是几种处理错误的方法：

## 1. 使用 `onFailure` 恢复机制

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res))
    .chain(res -> thirdOperation(res))
    .onFailure().recoverWithItem("fallback value"); // 提供默认值
```

## 2. 为每个步骤单独处理错误

```java
Uni<String> result = firstOperation()
    .onFailure().recoverWithItem("first fallback")
    .chain(res -> secondOperation(res)
        .onFailure().recoverWithItem("second fallback"))
    .chain(res -> thirdOperation(res)
        .onFailure().recoverWithItem("third fallback"));
```

## 3. 重试机制

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res)
        .onFailure().retry().atMost(3))
    .chain(res -> thirdOperation(res));
```

## 4. 转换错误类型

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res))
    .onFailure().transform(failure -> 
        new MyCustomException("Process failed", failure));
```

## 5. 条件恢复

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res))
    .onFailure(IOException.class).recoverWithItem("IO fallback")
    .onFailure(NumberFormatException.class).recoverWithItem("format fallback")
    .onFailure().recoverWithItem("generic fallback");
```

## 6. 记录错误但不中断流程

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res)
        .onFailure().invoke(failure -> 
            System.err.println("Error in second step: " + failure)))
    .chain(res -> thirdOperation(res));
```

## 7. 使用 `onItemOrFailure` 处理成功和失败

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res))
    .onItemOrFailure().transform((item, failure) -> {
        if (failure != null) {
            return "Recovered from: " + failure.getMessage();
        }
        return item;
    });
```

## 最佳实践建议

1. **尽早处理错误**：在可能出错的步骤后立即处理
2. **明确错误类型**：针对特定异常类型提供特定恢复逻辑
3. **保持可读性**：避免过长的链式调用，必要时拆分成方法
4. **记录错误**：即使恢复也建议记录错误信息
5. **考虑业务需求**：决定是恢复、重试还是完全失败

通过这些方法，你可以构建出既能处理预期错误又能优雅应对运行时异常的健壮异步流程。

---

# 在 Mutiny 中捕获和处理 RuntimeExceptions

你提出了一个很好的问题 - Mutiny 的 `onFailure()` 默认确实能捕获所有 Throwable（包括 RuntimeExceptions），但如果你发现某些 RuntimeExceptions 没有被捕获，可能有以下几种原因和解决方案：

## 为什么 RuntimeExceptions 可能"逃逸"

1. **在 lambda 表达式外部抛出**：如果在 `chain` 的 lambda 外部代码抛出异常
2. **在异步边界之前抛出**：在订阅前同步代码中抛出的异常
3. **使用了错误的操作符**：如误用了 `transform` 而不是 `chain`

## 确保捕获 RuntimeExceptions 的正确方法

### 方法1：使用 `onFailure()` 捕获所有异常

```java
Uni<String> result = Uni.createFrom().item(() -> {
        // 可能抛出RuntimeException的代码
        if (someCondition) {
            throw new RuntimeException("Oops!");
        }
        return "success";
    })
    .onFailure().recoverWithItem(e -> {
        System.out.println("Caught: " + e);
        return "fallback";
    });
```

### 方法2：包装可能抛出异常的代码

```java
Uni<String> riskyOperation = Uni.createFrom().item(() -> {
    try {
        return codeThatMightThrowRuntimeException();
    } catch (RuntimeException e) {
        throw new MyBusinessException(e);
    }
});

riskyOperation
    .chain(res -> nextStep(res))
    .onFailure(MyBusinessException.class).recoverWithItem("handled");
```

### 方法3：使用 `onFailure().recoverWithUni()`

```java
Uni<String> result = firstStep()
    .chain(res -> {
        if (res == null) {
            throw new NullPointerException();
        }
        return process(res);
    })
    .onFailure().recoverWithUni(failure -> {
        if (failure instanceof NullPointerException) {
            return Uni.createFrom().item("null handled");
        }
        return Uni.createFrom().failure(failure);
    });
```

### 方法4：使用 `eventually()` 确保资源清理

```java
Uni<Void> resourceOperation = acquireResource()
    .chain(resource -> useResource(resource)
    .eventually(() -> releaseResource()); // 无论成功失败都会执行
```

## 常见陷阱及解决方案

1. **Lambda 中直接抛出异常未被捕获**：
   ```java
   // 错误方式 - 异常可能在订阅前就抛出
   Uni<String> bad = Uni.createFrom().item("input")
       .chain(input -> {
           throw new RuntimeException("boom"); // 可能不被捕获
       });
   
   // 正确方式
   Uni<String> good = Uni.createFrom().item("input")
       .chain(input -> Uni.createFrom().emitter(em -> {
           try {
               em.complete(process(input));
           } catch (RuntimeException e) {
               em.fail(e);
           }
       }));
   ```

2. **同步代码中的异常**：
   ```java
   // 这段代码会在调用get()时直接抛出异常，而不是异步处理
   String result = Uni.createFrom().item(() -> { throw new RuntimeException(); })
       .onFailure().recoverWithItem("fallback")
       .await().indefinitely(); // 这里会直接抛出异常
   ```

## 最佳实践

1. 总是假设任何操作都可能抛出RuntimeException
2. 对于可能抛出异常的代码，使用`Uni.createFrom().item(() -> {...})`包装
3. 在关键步骤后添加错误处理
4. 考虑使用中央错误处理策略
5. 测试各种失败场景

通过以上方法，你可以确保即使是RuntimeExceptions也能被适当捕获和处理。

---

# Rust 中处理错误的等效模式

Rust 的错误处理与 Java/Mutiny 有显著不同，主要依靠 `Result` 类型和 `?` 操作符，而不是异常。以下是 Mutiny 错误处理模式在 Rust 中的对应实现：

## 1. 基本错误处理（对应 `onFailure().recoverWithItem`）

```rust
use std::error::Error;

fn risky_operation(some_condition: bool) -> Result<String, Box<dyn Error>> {
    if some_condition {
        Err("Oops!".into())
    } else {
        Ok("success".into())
    }
}

fn main() {
    let result = risky_operation(true)
        .unwrap_or_else(|e| {
            println!("Caught: {}", e);
            "fallback".to_string()
        });
    
    println!("Result: {}", result); // 输出: Result: fallback
}
```

## 2. 链式操作与错误传播（对应 `chain`）

```rust
fn step1() -> Result<String, Box<dyn Error>> {
    Ok("input".to_string())
}

fn step2(input: String) -> Result<String, Box<dyn Error>> {
    if input.is_empty() {
        Err("Empty input".into())
    } else {
        Ok(input.to_uppercase())
    }
}

fn main() -> Result<(), Box<dyn Error>> {
    let result = step1()
        .and_then(|res| step2(res))
        .unwrap_or_else(|_| "handled".to_string());
    
    println!("{}", result);
    Ok(())
}
```

## 3. 使用 `match` 处理特定错误（对应 `onFailure(MyBusinessException.class)`）

```rust
#[derive(Debug)]
enum MyError {
    NullError,
    OtherError(String),
}

fn process(input: Option<String>) -> Result<String, MyError> {
    let value = input.ok_or(MyError::NullError)?;
    if value == "error" {
        Err(MyError::OtherError("special case".into()))
    } else {
        Ok(value)
    }
}

fn main() {
    let input = Some("error".to_string());
    let result = match process(input) {
        Ok(val) => val,
        Err(MyError::NullError) => "null handled".to_string(),
        Err(MyError::OtherError(msg)) => format!("other error: {}", msg),
    };
    
    println!("{}", result); // 输出: other error: special case
}
```

## 4. 资源清理（对应 `eventually()`）

```rust
struct Resource;

impl Resource {
    fn acquire() -> Result<Resource, &'static str> {
        Ok(Resource)
    }
    
    fn use_resource(&self) -> Result<(), &'static str> {
        println!("Using resource");
        Ok(())
    }
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("Resource released");
    }
}

fn main() -> Result<(), &'static str> {
    let resource = Resource::acquire()?;
    resource.use_resource()?;
    // 资源会在作用域结束时自动释放
    Ok(())
}
```

## 5. 异步错误处理（使用 tokio/futures）

```rust
use tokio::runtime::Runtime;

async fn async_step1() -> Result<String, Box<dyn std::error::Error>> {
    Ok("async input".to_string())
}

async fn async_step2(input: String) -> Result<String, Box<dyn std::error::Error>> {
    if input.len() > 5 {
        Err("Too long".into())
    } else {
        Ok(input)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let rt = Runtime::new()?;
    let result = rt.block_on(async {
        async_step1()
            .and_then(|res| async_step2(res))
            .await
            .unwrap_or_else(|_| "fallback".to_string())
    });
    
    println!("{}", result);
    Ok(())
}
```

## Rust 错误处理最佳实践

1. **优先使用 `Result` 而不是 panic**：Rust 中 panic 类似于 Java 的 RuntimeException，但应尽量避免
2. **利用 `?` 操作符简化错误传播**：自动将错误向上传播
3. **定义明确的错误类型**：使用 `thiserror` 或 `anyhow` 库管理错误
4. **组合错误类型**：使用 `Box<dyn Error>` 或 `anyhow::Error` 处理多种错误
5. **资源清理使用 `Drop` trait**：确保资源释放

Rust 的错误处理更加显式和类型安全，虽然与 Java 的异常处理方式不同，但能提供更可靠的错误处理机制。

---

# Rust 错误处理详解

Rust 的错误处理机制与 Java 的异常处理有本质不同，它基于显式的 `Result` 类型和模式匹配，而不是隐式的异常抛出。下面我将详细解释 Rust 中处理错误的几种主要方式。

## 1. 基本错误处理模式

### 使用 `Result` 类型

Rust 使用 `Result<T, E>` 枚举类型来表示可能失败的操作：

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

### 示例：基本错误处理

```rust
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err(String::from("Cannot divide by zero"))
    } else {
        Ok(a / b)
    }
}

fn main() {
    match divide(10, 2) {
        Ok(result) => println!("Result: {}", result),
        Err(e) => println!("Error: {}", e),
    }
    
    match divide(10, 0) {
        Ok(result) => println!("Result: {}", result),
        Err(e) => println!("Error: {}", e), // 这会执行
    }
}
```

## 2. 错误传播

### 使用 `?` 操作符

`?` 操作符可以简化错误传播：

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_file(path: &str) -> Result<String, io::Error> {
    let mut file = File::open(path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}

fn main() {
    match read_file("hello.txt") {
        Ok(contents) => println!("File contents: {}", contents),
        Err(e) => println!("Error reading file: {}", e),
    }
}
```

## 3. 组合错误类型

### 使用 `Box<dyn Error>`

处理多种错误类型时：

```rust
use std::error::Error;
use std::fs::File;
use std::io::Read;

fn process_file(path: &str) -> Result<String, Box<dyn Error>> {
    let mut file = File::open(path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    if contents.is_empty() {
        Err("Empty file".into())
    } else {
        Ok(contents)
    }
}

fn main() -> Result<(), Box<dyn Error>> {
    let contents = process_file("hello.txt")?;
    println!("File contents: {}", contents);
    Ok(())
}
```

## 4. 自定义错误类型

### 使用 `thiserror` 库

```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum MyError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Empty content")]
    Empty,
    #[error("Parse error: {0}")]
    Parse(String),
}

fn process_data(data: &str) -> Result<(), MyError> {
    if data.is_empty() {
        return Err(MyError::Empty);
    }
    // 模拟其他操作
    Ok(())
}

fn main() -> Result<(), MyError> {
    process_data("")?; // 这会返回 MyError::Empty
    Ok(())
}
```

## 5. 错误转换

### 使用 `map_err`

```rust
use std::num::ParseIntError;

fn parse_and_double(number: &str) -> Result<i32, String> {
    number.parse::<i32>()
        .map(|n| n * 2)
        .map_err(|e: ParseIntError| format!("Parse error: {}", e))
}

fn main() {
    match parse_and_double("10") {
        Ok(n) => println!("Result: {}", n),
        Err(e) => println!("Error: {}", e),
    }
    
    match parse_and_double("abc") {
        Ok(n) => println!("Result: {}", n),
        Err(e) => println!("Error: {}", e), // 这会执行
    }
}
```

## 6. 异步错误处理

### 使用 tokio 和 anyhow

```rust
use anyhow::{Context, Result};
use tokio::fs::File;
use tokio::io::AsyncReadExt;

async fn read_async_file(path: &str) -> Result<String> {
    let mut file = File::open(path)
        .await
        .context(format!("Failed to open file {}", path))?;
    
    let mut contents = String::new();
    file.read_to_string(&mut contents)
        .await
        .context("Failed to read file")?;
    
    Ok(contents)
}

#[tokio::main]
async fn main() -> Result<()> {
    let contents = read_async_file("hello.txt").await?;
    println!("File contents: {}", contents);
    Ok(())
}
```

## 7. 错误恢复

### 使用 `unwrap_or` 和 `unwrap_or_else`

```rust
fn get_config_value(key: &str) -> Result<String, String> {
    if key == "timeout" {
        Ok("30".to_string())
    } else {
        Err(format!("Key {} not found", key))
    }
}

fn main() {
    let timeout = get_config_value("timeout")
        .unwrap_or("10".to_string()); // 默认值
    
    let retries = get_config_value("retries")
        .unwrap_or_else(|e| {
            println!("Warning: {}", e);
            "3".to_string() // 根据错误计算默认值
        });
    
    println!("Timeout: {}, Retries: {}", timeout, retries);
}
```

## 8. 错误链

### 使用 `anyhow` 的错误上下文

```rust
use anyhow::{Context, Result};
use std::fs;
use std::path::PathBuf;

fn find_and_read_config() -> Result<String> {
    let path = find_config_file().context("Could not find config file")?;
    fs::read_to_string(&path)
        .context(format!("Failed to read config file at {:?}", path))
}

fn find_config_file() -> Result<PathBuf, std::io::Error> {
    // 模拟查找配置文件
    Err(std::io::Error::new(
        std::io::ErrorKind::NotFound,
        "Config file not found",
    ))
}

fn main() -> Result<()> {
    let config = find_and_read_config()?;
    println!("Config: {}", config);
    Ok(())
}
```

## 总结对比

| Java/Mutiny 方式 | Rust 等效方式 |
|-----------------|--------------|
| `try-catch` 块 | `match` 表达式或 `?` 操作符 |
| `onFailure()` | `Result` 类型和错误处理组合子 |
| 异常传播 | `?` 操作符传播错误 |
| 异常类型检查 | 模式匹配不同的错误变体 |
| `recoverWithItem` | `unwrap_or` 或 `unwrap_or_else` |
| 链式错误处理 | `and_then` 或 `?` 操作符链 |

Rust 的错误处理更加显式和类型安全，虽然需要更多样板代码，但能提供更可靠的错误处理机制，编译器会强制你处理所有可能的错误情况。

---

# Rust 中的运行时异常处理

在 Rust 中，确实存在类似"uncaught runtime exception"的概念，但实现方式和处理哲学与 Java 完全不同。以下是详细解释：

## Rust 的两种"异常"机制

1. **可恢复错误 (Recoverable Errors)**
    - 使用 `Result<T, E>` 类型显式处理
    - 代表预期的、应该被处理的错误情况
    - 必须显式处理或传播

2. **不可恢复错误 (Unrecoverable Errors)**
    - 使用 `panic!` 宏触发
    - 类似于 Java 的 RuntimeExceptions
    - 表示程序遇到了无法继续执行的严重错误

## Rust 中的"Uncaught"情况

### 1. `panic!` 导致的线程崩溃

```rust
fn main() {
    panic!("This is an uncaught runtime panic!");
    // 程序会终止，打印错误信息和回溯
}
```

### 2. 未处理的 `Result` 错误

```rust
use std::fs::File;

fn main() {
    let _file = File::open("nonexistent.txt").unwrap();
    // 如果文件不存在，会 panic!
}
```

## 如何处理 Rust 的运行时问题

### 1. 捕获 panic (不推荐常规使用)

```rust
use std::panic;

fn main() {
    let result = panic::catch_unwind(|| {
        panic!("Oh no!");
    });
    
    match result {
        Ok(_) => println!("Everything fine"),
        Err(_) => println!("Caught a panic"),
    }
}
```

### 2. 正确处理 `Result`

```rust
use std::fs::File;

fn main() {
    match File::open("nonexistent.txt") {
        Ok(file) => println!("File opened: {:?}", file),
        Err(e) => println!("Failed to open file: {}", e),
    }
}
```

### 3. 设置自定义 panic 处理

```rust
use std::panic;

fn main() {
    panic::set_hook(Box::new(|panic_info| {
        println!("Custom panic handler: {}", panic_info);
    }));
    
    panic!("This will be handled by our custom handler");
}
```

## 与 Java 异常处理的关键区别

| 特性                | Java                         | Rust                        |
|---------------------|-----------------------------|----------------------------|
| 主要错误机制         | 异常 (Exceptions)           | Result 类型                |
| 未捕获异常           | 传播到线程未捕获异常处理器   | 导致线程 panic             |
| 编译时检查           | 只有 checked exceptions     | 所有 Result 必须处理       |
| 性能影响             | 抛出异常成本高              | Result 是零成本抽象       |
| 哲学                | "乐观"路径，异常处理特殊情况 | "悲观"路径，显式处理所有可能错误 |

## 最佳实践

1. **优先使用 `Result`**：将错误作为正常控制流的一部分
2. **谨慎使用 `unwrap/expect`**：只在确定不会出错或原型代码中使用
3. **合理使用 `panic!`**：仅用于不可恢复的程序状态
4. **库代码应避免 panic**：提供 `Result` 接口让调用者决定
5. **使用 `?` 操作符**：简化错误传播

Rust 的设计鼓励开发者提前考虑所有可能的错误情况，通过类型系统保证大多数运行时错误都能在编译期被发现，这是与 Java 异常处理最根本的区别。

---

# 使用 Tokio 和 Anyhow 实现链式操作

Tokio 和 Anyhow 是 Rust 异步编程和错误处理的两个重要库，结合使用可以构建清晰、健壮的异步操作链。以下是它们的链式操作方法：

## 1. 基本组合方式

### 依赖配置
```toml
[dependencies]
tokio = { version = "1.0", features = ["full"] }
anyhow = "1.0"
```

### 基础示例
```rust
use anyhow::{Context, Result};
use tokio::fs;

async fn process_file(path: &str) -> Result<String> {
    let content = fs::read_to_string(path)
        .await
        .context(format!("Failed to read file {}", path))?;
    
    let processed = process_content(&content)
        .context("Failed to process content")?;
    
    Ok(processed)
}

fn process_content(content: &str) -> Result<String> {
    if content.is_empty() {
        anyhow::bail!("Empty content");
    }
    Ok(content.to_uppercase())
}
```

## 2. 链式操作模式

### 使用 `and_then` 组合
```rust
use anyhow::Result;
use tokio::fs;

async fn pipeline() -> Result<()> {
    fs::read_to_string("input.txt")
        .await
        .and_then(|content| async move {
            let processed = transform(&content)?;
            save_result("output.txt", &processed).await
        })
        .context("Processing pipeline failed")
}

async fn save_result(path: &str, data: &str) -> Result<()> {
    tokio::fs::write(path, data).await?;
    Ok(())
}

fn transform(data: &str) -> Result<String> {
    // 转换逻辑
    Ok(data.to_uppercase())
}
```

## 3. 使用 `?` 操作符的链式处理

```rust
use anyhow::{Context, Result};
use tokio::{fs, net::TcpStream, io::AsyncWriteExt};

async fn send_file_contents(host: &str, port: u16, file_path: &str) -> Result<()> {
    let content = fs::read_to_string(file_path)
        .await
        .context("Failed to read file")?;
    
    let mut stream = TcpStream::connect(format!("{}:{}", host, port))
        .await
        .context("Connection failed")?;
    
    stream.write_all(content.as_bytes())
        .await
        .context("Failed to send data")?;
    
    Ok(())
}
```

## 4. 复杂管道组合

```rust
use anyhow::{Context, Result};
use tokio::{fs, time::{sleep, Duration}};

async fn complex_operation() -> Result<Vec<String>> {
    let file1 = fs::read_to_string("file1.txt")
        .await
        .context("Reading file1")?;
    
    sleep(Duration::from_secs(1)).await;
    
    let file2 = fs::read_to_string("file2.txt")
        .await
        .context("Reading file2")?;
    
    let processed = process_files(&file1, &file2)
        .context("Processing files")?;
    
    validate_result(&processed)?;
    
    Ok(processed)
}

fn process_files(f1: &str, f2: &str) -> Result<Vec<String>> {
    // 处理逻辑
    Ok(vec![f1.to_owned(), f2.to_owned()])
}

fn validate_result(data: &[String]) -> Result<()> {
    if data.iter().any(|s| s.is_empty()) {
        anyhow::bail!("Empty string in result");
    }
    Ok(())
}
```

## 5. 使用 `try_join!` 并行操作

```rust
use anyhow::Result;
use tokio::{fs, try_join};

async fn parallel_operations() -> Result<(String, String)> {
    let (res1, res2) = try_join!(
        fs::read_to_string("file1.txt"),
        fs::read_to_string("file2.txt")
    )?;
    
    Ok((res1, res2))
}
```

## 6. 错误处理与上下文添加

```rust
use anyhow::{Context, Result};
use tokio::fs;

async fn operation_with_context() -> Result<()> {
    let config = load_config("config.toml")
        .await
        .context("Loading configuration")?;
    
    let data = fetch_data(&config.url)
        .await
        .context("Fetching remote data")?;
    
    validate(&data)
        .context("Data validation")?;
    
    Ok(())
}
```

## 7. 自定义错误类型的高级用法

```rust
use thiserror::Error;
use anyhow::Result;
use tokio::fs;

#[derive(Error, Debug)]
enum ProcessingError {
    #[error("Invalid format: {0}")]
    InvalidFormat(String),
    #[error("IO error")]
    Io(#[from] std::io::Error),
}

async fn process_with_custom_error() -> Result<(), ProcessingError> {
    let content = fs::read_to_string("data.json").await?;
    
    if content.starts_with('{') {
        Ok(())
    } else {
        Err(ProcessingError::InvalidFormat("Expected JSON object".into()))
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    process_with_custom_error()
        .await
        .map_err(|e| anyhow::anyhow!("Custom error occurred: {}", e))?;
    
    Ok(())
}
```

## 最佳实践

1. **合理使用 `context()`**：为错误添加有意义的上下文信息
2. **保持错误类型一致**：在管道中使用相同的错误类型或 `anyhow::Error`
3. **适当拆分函数**：避免过长的链式调用，保持可读性
4. **利用 `?` 操作符**：简化错误传播
5. **考虑并行化**：对独立操作使用 `try_join!` 提高性能

这种组合方式既保持了 Rust 强大的类型安全性，又通过 Anyhow 提供了良好的错误上下文信息，同时利用 Tokio 实现了高效的异步操作。

---

# Java Reactor 响应式编程详解

Reactor 是 Spring 5 引入的响应式编程库，基于 Reactive Streams 规范，为 Java 提供了强大的异步数据流处理能力。

## 核心概念

### 1. 两种核心类型

- **Mono**: 表示0或1个元素的异步序列
- **Flux**: 表示0到N个元素的异步序列

### 2. 基本特性

- **非阻塞**: 不会阻塞调用线程
- **背压支持**: 消费者可以控制生产者速率
- **函数式风格**: 使用 lambda 表达式和函数组合

## 创建数据流

### 创建 Mono

```java
// 从值创建
Mono<String> mono1 = Mono.just("Hello");

// 从Callable创建
Mono<String> mono2 = Mono.fromCallable(() -> expensiveOperation());

// 空Mono
Mono<Void> mono3 = Mono.empty();

// 从Future创建
Mono<String> mono4 = Mono.fromFuture(CompletableFuture.supplyAsync(() -> "Async Result"));
```

### 创建 Flux

```java
// 从多个值创建
Flux<String> flux1 = Flux.just("A", "B", "C");

// 从集合创建
Flux<String> flux2 = Flux.fromIterable(Arrays.asList("A", "B", "C"));

// 范围创建
Flux<Integer> flux3 = Flux.range(1, 5); // 1,2,3,4,5

// 间隔创建
Flux<Long> flux4 = Flux.interval(Duration.ofSeconds(1)); // 0,1,2...每秒一个
```

## 操作符

### 转换操作

```java
Flux.range(1, 5)
    .map(i -> i * 2) // 1→2, 2→4...
    .flatMap(i -> Mono.just(i * 10)) // 展开
    .collectList() // 收集为List
    .subscribe(System.out::println);
```

### 过滤操作

```java
Flux.range(1, 10)
    .filter(i -> i % 2 == 0) // 只保留偶数
    .take(3) // 只取前3个
    .skip(1) // 跳过第1个
    .subscribe(System.out::println);
```

### 组合操作

```java
Flux<String> flux1 = Flux.just("A", "B");
Flux<String> flux2 = Flux.just("C", "D");

// 合并
Flux.merge(flux1, flux2).subscribe(System.out::println); // 顺序不确定

// 连接
Flux.concat(flux1, flux2).subscribe(System.out::println); // A,B,C,D

// Zip组合
Flux.zip(flux1, flux2, (a, b) -> a + b)
    .subscribe(System.out::println); // AC, BD
```

### 错误处理

```java
Flux.just(1, 2, 0, 4)
    .map(i -> 10 / i) // 除0会抛出异常
    .onErrorReturn(-1) // 出错返回-1
    .onErrorResume(e -> Flux.just(100, 200)) // 出错切换流
    .retry(1) // 重试1次
    .subscribe(System.out::println);
```

## 线程调度

```java
Flux.range(1, 5)
    .publishOn(Schedulers.parallel()) // 后续操作在并行线程
    .map(i -> {
        System.out.println("Map on " + Thread.currentThread().getName());
        return i * 2;
    })
    .subscribeOn(Schedulers.boundedElastic()) // 订阅在弹性线程池
    .subscribe(System.out::println);
```

## 背压处理

```java
Flux.range(1, 1000)
    .onBackpressureBuffer(10) // 缓冲区10个元素
    .subscribe(new BaseSubscriber<Integer>() {
        @Override
        protected void hookOnSubscribe(Subscription subscription) {
            request(5); // 初始请求5个
        }
        
        @Override
        protected void hookOnNext(Integer value) {
            System.out.println(value);
            if (value % 5 == 0) {
                request(5); // 每处理5个再请求5个
            }
        }
    });
```

## 实际应用示例

### WebFlux 控制器

```java
@RestController
public class UserController {
    
    @Autowired
    private UserRepository userRepository;
    
    @GetMapping("/users")
    public Flux<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    @GetMapping("/users/{id}")
    public Mono<User> getUserById(@PathVariable String id) {
        return userRepository.findById(id);
    }
    
    @PostMapping("/users")
    public Mono<User> createUser(@RequestBody User user) {
        return userRepository.save(user);
    }
}
```

### 数据库交互

```java
public interface UserRepository extends ReactiveCrudRepository<User, String> {
    
    Flux<User> findByAgeGreaterThan(int age);
    
    @Query("{ 'name': { $regex: ?0, $options: 'i' } }")
    Flux<User> findByNameRegex(String nameRegex);
}
```

## 与 Project Reactor 生态集成

- **Spring WebFlux**: 响应式Web框架
- **R2DBC**: 响应式关系数据库连接
- **Reactive MongoDB**: MongoDB响应式驱动
- **Reactive Kafka**: Kafka响应式客户端
- **Reactive Redis**: Redis响应式客户端

## 调试技巧

```java
// 启用调试模式
Hooks.onOperatorDebug();

Flux.just("a", "b")
    .checkpoint("after source")
    .map(s -> s.toUpperCase())
    .checkpoint("after map")
    .subscribe(System.out::println);
```

Reactor 提供了强大的响应式编程能力，特别适合高并发、低延迟的应用场景。通过 Flux 和 Mono 的组合，可以构建复杂的异步数据流处理管道，同时保持代码的可读性和可维护性。

---

# Mutiny 的 `subscribe().with()` 对 RuntimeExceptions 的处理机制

确实，Mutiny 的 `subscribe().with()` 方法在默认情况下不会捕获所有的 RuntimeExceptions，这与 Reactor 的行为有所不同。下面我将详细解释这一行为并提供解决方案。

## 问题本质

当使用 `subscribe().with()` 时：
```java
Uni.createFrom().item(() -> {
    throw new RuntimeException("Boom!");
})
.subscribe().with(
    item -> System.out.println("Item: " + item),
    failure -> System.out.println("Failure: " + failure)
);
```
**问题在于**：如果在订阅前（即在创建 Uni/Multi 的 lambda 中）就抛出异常，这个异常会直接抛出到调用线程，而不会进入 `failure` 回调。

## 原因分析

Mutiny 的这种行为设计是因为：
1. **同步与异步边界**：在创建阶段的异常被认为是同步错误
2. **明确性**：强制开发者明确处理可能的同步异常
3. **性能**：避免不必要的异常捕获开销

## 解决方案

### 1. 使用 `onFailure` 回调（推荐）

```java
Uni.createFrom().item(() -> {
        // 可能抛出RuntimeException的代码
        if (someCondition) {
            throw new RuntimeException("Oops!");
        }
        return "success";
    })
    .onFailure().invoke(e -> System.out.println("Error occurred: " + e))
    .onFailure().recoverWithItem("fallback")
    .subscribe().with(
        item -> System.out.println("Result: " + item),
        failure -> {} // 这里不会执行，因为错误已被上面处理
    );
```

### 2. 使用 `onItemOrFailure` 组合处理

```java
Uni.createFrom().item(() -> {
        throw new RuntimeException("Early error");
    })
    .onItemOrFailure().transform((item, failure) -> {
        if (failure != null) {
            return "Recovered from: " + failure.getMessage();
        }
        return item;
    })
    .subscribe().with(
        result -> System.out.println(result), // 输出: Recovered from: Early error
        failure -> {} // 不会执行
    );
```

### 3. 使用 `emitOn` 确保异步执行

```java
Uni.createFrom().item(() -> {
        throw new RuntimeException("Now it's async");
    })
    .emitOn(Infrastructure.getDefaultExecutor()) // 强制异步执行
    .subscribe().with(
        item -> {},
        failure -> System.out.println("Caught: " + failure) // 现在会被执行
    );
```

### 4. 使用 `catch` 包装同步代码

```java
Uni<String> uni = Uni.createFrom().emitter(em -> {
    try {
        String result = codeThatMightThrow();
        em.complete(result);
    } catch (RuntimeException e) {
        em.fail(e);
    }
});

uni.subscribe().with(
    item -> System.out.println(item),
    failure -> System.out.println("Caught: " + failure) // 会捕获异常
);
```

## 最佳实践

1. **对于已知可能抛出异常的同步代码**：
   ```java
   Uni.createFrom().item(() -> {
       try {
           return riskyOperation();
       } catch (RuntimeException e) {
           throw new MyBusinessException(e); // 转换为受控异常
       }
   })
   ```

2. **对于完全不可控的第三方代码**：
   ```java
   Uni.createFrom().emitter(em -> {
       try {
           em.complete(untrustedCode());
       } catch (Throwable t) {
           em.fail(t);
       }
   })
   ```

3. **全局错误处理**（Quarkus 环境中）：
   ```java
   @Inject MutinyHelper helper; // Quarkus 提供的工具
   
   helper.async(() -> riskyCode())
       .subscribe().with(...);
   ```

## 与 Reactor 的对比

| 场景                     | Reactor                          | Mutiny                          |
|--------------------------|----------------------------------|---------------------------------|
| 同步代码抛出异常          | 会被 onError 捕获                | 直接抛出，需显式处理            |
| 异步代码抛出异常          | 进入 onError                     | 进入 failure 回调               |
| 推荐处理方式              | onError* 操作符                  | onFailure* 操作符 + 显式 try-catch |

Mutiny 的这种设计虽然需要更多显式处理，但能带来：
- 更清晰的错误来源定位
- 更好的性能（减少不必要的异常捕获）
- 更明确的代码意图表达

在 Quarkus 应用中，通常建议通过 `@Transactional` 或其他拦截器来处理潜在异常，而不是依赖 `subscribe().with()` 的 failure 回调来捕获所有异常。
