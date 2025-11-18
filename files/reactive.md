# Mutiny's `chain` Method Introduction

Mutiny is a reactive programming library primarily used for asynchronous and event-driven programming in Java. The `chain` method is an important method in the Mutiny API, used to chain multiple operations together to form a processing pipeline.

## Basic Concepts

The `chain` method allows you to chain multiple asynchronous operations together, forming a continuous processing chain. It's similar to `flatMap` or `then` operations in other reactive libraries.

## Main Features

1. **Sequential execution**: `chain` ensures operations execute in order, the next operation only starts after the previous one completes
2. **Type safety**: Maintains type consistency, ensuring each step in the chain correctly handles data types
3. **Error propagation**: If any step in the chain fails, the error propagates along the chain

## Basic Usage

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res))
    .chain(res -> thirdOperation(res));
```

## Difference from `onItem().transform()`

- `transform` is for synchronous transformation
- `chain` is for asynchronous operations, returning `Uni` or `Multi`

## Example

```java
Uni<String> fetchUser = getUserById(userId)
    .chain(user -> fetchUserDetails(user))
    .chain(details -> processDetails(details));
```

## Error Handling

You can add error handling in the chain:

```java
Uni<String> result = operation()
    .chain(res -> nextStep(res))
    .onFailure().recoverWithItem(fallbackValue);
```

The `chain` method is a fundamental building block in Mutiny for constructing complex asynchronous flows, making asynchronous code maintainable and readable.

---

# Handling Runtime Errors in Mutiny Chain Operations

Handling runtime errors in Mutiny's `chain` method chain is very important for building robust asynchronous applications. Here are several ways to handle errors:

## 1. Using `onFailure` Recovery Mechanism

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res))
    .chain(res -> thirdOperation(res))
    .onFailure().recoverWithItem("fallback value"); // Provide default value
```

## 2. Handling Errors for Each Step Separately

```java
Uni<String> result = firstOperation()
    .onFailure().recoverWithItem("first fallback")
    .chain(res -> secondOperation(res)
        .onFailure().recoverWithItem("second fallback"))
    .chain(res -> thirdOperation(res)
        .onFailure().recoverWithItem("third fallback"));
```

## 3. Retry Mechanism

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res)
        .onFailure().retry().atMost(3))
    .chain(res -> thirdOperation(res));
```

## 4. Transform Error Types

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res))
    .onFailure().transform(failure -> 
        new MyCustomException("Process failed", failure));
```

## 5. Conditional Recovery

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res))
    .onFailure(IOException.class).recoverWithItem("IO fallback")
    .onFailure(NumberFormatException.class).recoverWithItem("format fallback")
    .onFailure().recoverWithItem("generic fallback");
```

## 6. Log Errors Without Interrupting Flow

```java
Uni<String> result = firstOperation()
    .chain(res -> secondOperation(res)
        .onFailure().invoke(failure -> 
            System.err.println("Error in second step: " + failure)))
    .chain(res -> thirdOperation(res));
```

## 7. Using `onItemOrFailure` to Handle Success and Failure

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

## Best Practices

1. **Handle errors early**: Handle them immediately after steps that might fail
2. **Be specific about error types**: Provide specific recovery logic for specific exception types
3. **Maintain readability**: Avoid overly long chain calls, split into methods when necessary
4. **Log errors**: Even when recovering, it's recommended to log error information
5. **Consider business requirements**: Decide whether to recover, retry, or fail completely

Through these methods, you can build robust asynchronous flows that handle both expected errors and gracefully deal with runtime exceptions.

---

# Catching and Handling RuntimeExceptions in Mutiny

You raise a good question - Mutiny's `onFailure()` can indeed catch all Throwables (including RuntimeExceptions) by default, but if you find some RuntimeExceptions aren't being caught, there might be several reasons and solutions:

## Why RuntimeExceptions Might "Escape"

1. **Thrown outside lambda expressions**: If exceptions are thrown in code outside the `chain` lambda
2. **Thrown before async boundary**: Exceptions in synchronous code before subscription
3. **Using wrong operators**: Like mistakenly using `transform` instead of `chain`

## Correct Ways to Ensure RuntimeExceptions Are Caught

### Method 1: Use `onFailure()` to catch all exceptions

```java
Uni<String> result = Uni.createFrom().item(() -> {
        // Code that might throw RuntimeException
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

### Method 2: Wrap potentially exception-throwing code

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

### Method 3: Use `onFailure().recoverWithUni()`

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

### Method 4: Use `eventually()` to ensure resource cleanup

```java
Uni<Void> resourceOperation = acquireResource()
    .chain(resource -> useResource(resource)
    .eventually(() -> releaseResource()); // Executes regardless of success or failure
```

## Common Pitfalls and Solutions

1. **Lambda directly throwing exceptions not caught**:
   ```java
   // Wrong way - exception might be thrown before subscription
   Uni<String> bad = Uni.createFrom().item("input")
       .chain(input -> {
           throw new RuntimeException("boom"); // Might not be caught
       });
   
   // Correct way
   Uni<String> good = Uni.createFrom().item("input")
       .chain(input -> Uni.createFrom().emitter(em -> {
           try {
               em.complete(process(input));
           } catch (RuntimeException e) {
               em.fail(e);
           }
       }));
   ```

2. **Exceptions in synchronous code**:
   ```java
   // This code will throw exception directly when calling get(), not handled asynchronously
   String result = Uni.createFrom().item(() -> { throw new RuntimeException(); })
       .onFailure().recoverWithItem("fallback")
       .await().indefinitely(); // Will throw exception directly here
   ```

## Best Practices

1. Always assume any operation might throw RuntimeException
2. For code that might throw exceptions, use `Uni.createFrom().item(() -> {...})` wrapper
3. Add error handling after critical steps
4. Consider using centralized error handling strategies
5. Test various failure scenarios

Through the above methods, you can ensure that even RuntimeExceptions are properly caught and handled.

---

# Equivalent Patterns for Error Handling in Rust

Rust's error handling is significantly different from Java/Mutiny, mainly relying on the `Result` type and `?` operator rather than exceptions. Here's the corresponding implementation of Mutiny error handling patterns in Rust:

## 1. Basic Error Handling (equivalent to `onFailure().recoverWithItem`)

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
    
    println!("Result: {}", result); // Output: Result: fallback
}
```

## 2. Chaining Operations and Error Propagation (equivalent to `chain`)

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

## 3. Using `match` to Handle Specific Errors (equivalent to `onFailure(MyBusinessException.class)`)

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
    
    println!("{}", result); // Output: other error: special case
}
```

## 4. Resource Cleanup (equivalent to `eventually()`)

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
    // Resource will be automatically released when scope ends
    Ok(())
}
```

## 5. Asynchronous Error Handling (using tokio/futures)

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

## Rust Error Handling Best Practices

1. **Prioritize `Result` over panic**: In Rust, panic is similar to Java's RuntimeException, but should be avoided
2. **Utilize `?` operator to simplify error propagation**: Automatically propagates errors upward
3. **Define clear error types**: Use `thiserror` or `anyhow` libraries to manage errors
4. **Combine error types**: Use `Box<dyn Error>` or `anyhow::Error` to handle multiple errors
5. **Resource cleanup uses `Drop` trait**: Ensures resource release

Rust's error handling is more explicit and type-safe. Although different from Java's exception handling, it can provide more reliable error handling mechanisms.

---

# Detailed Explanation of Rust Error Handling

Rust's error handling mechanism is fundamentally different from Java's exception handling. It's based on explicit `Result` types and pattern matching rather than implicit exception throwing. Below I'll explain the main ways to handle errors in Rust in detail.

## 1. Basic Error Handling Patterns

### Using `Result` Type

Rust uses the `Result<T, E>` enum type to represent operations that might fail:

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

### Example: Basic Error Handling

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
        Err(e) => println!("Error: {}", e), // This will execute
    }
}
```

## 2. Error Propagation

### Using `?` Operator

The `?` operator can simplify error propagation:

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

## 3. Combining Error Types

### Using `Box<dyn Error>`

When handling multiple error types:

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

## 4. Custom Error Types

### Using `thiserror` Library

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
    // Simulate other operations
    Ok(())
}

fn main() -> Result<(), MyError> {
    process_data("")?; // This will return MyError::Empty
    Ok(())
}
```

## 5. Error Transformation

### Using `map_err`

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
        Err(e) => println!("Error: {}", e), // This will execute
    }
}
```

## 6. Asynchronous Error Handling

### Using tokio and anyhow

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

## 7. Error Recovery

### Using `unwrap_or` and `unwrap_or_else`

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
        .unwrap_or("10".to_string()); // Default value
    
    let retries = get_config_value("retries")
        .unwrap_or_else(|e| {
            println!("Warning: {}", e);
            "3".to_string() // Calculate default based on error
        });
    
    println!("Timeout: {}, Retries: {}", timeout, retries);
}
```

## 8. Error Chains

### Using `anyhow` Error Context

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
    // Simulate finding config file
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

## Summary Comparison

| Java/Mutiny Approach | Rust Equivalent |
|---------------------|-----------------|
| `try-catch` blocks | `match` expressions or `?` operator |
| `onFailure()` | `Result` type and error handling combinators |
| Exception propagation | `?` operator for error propagation |
| Exception type checking | Pattern matching different error variants |
| `recoverWithItem` | `unwrap_or` or `unwrap_or_else` |
| Chained error handling | `and_then` or `?` operator chains |

Rust's error handling is more explicit and type-safe. Although it requires more boilerplate code, it provides more reliable error handling mechanisms, and the compiler forces you to handle all possible error cases.

---

# Runtime Exception Handling in Rust

In Rust, there is indeed a concept similar to "uncaught runtime exception", but the implementation and handling philosophy are completely different from Java. Here's a detailed explanation:

## Rust's Two "Exception" Mechanisms

1. **Recoverable Errors**
    - Use `Result<T, E>` type for explicit handling
    - Represent expected, handleable error situations
    - Must be explicitly handled or propagated

2. **Unrecoverable Errors**
    - Triggered using `panic!` macro
    - Similar to Java's RuntimeExceptions
    - Represent serious errors where the program cannot continue execution

## Rust's "Uncaught" Situations

### 1. Thread Panic from `panic!`

```rust
fn main() {
    panic!("This is an uncaught runtime panic!");
    // Program terminates, prints error info and backtrace
}
```

### 2. Unhandled `Result` Errors

```rust
use std::fs::File;

fn main() {
    let _file = File::open("nonexistent.txt").unwrap();
    // If file doesn't exist, will panic!
}
```

## How to Handle Runtime Issues in Rust

### 1. Catch panic (not recommended for regular use)

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

### 2. Properly Handle `Result`

```rust
use std::fs::File;

fn main() {
    match File::open("nonexistent.txt") {
        Ok(file) => println!("File opened: {:?}", file),
        Err(e) => println!("Failed to open file: {}", e),
    }
}
```

### 3. Set Custom Panic Handler

```rust
use std::panic;

fn main() {
    panic::set_hook(Box::new(|panic_info| {
        println!("Custom panic handler: {}", panic_info);
    }));
    
    panic!("This will be handled by our custom handler");
}
```

## Key Differences from Java Exception Handling

| Feature | Java | Rust |
|---------|------|------|
| Primary Error Mechanism | Exceptions | Result Type |
| Uncaught Exceptions | Propagate to thread uncaught exception handler | Cause thread panic |
| Compile-time Checking | Only checked exceptions | All Results must be handled |
| Performance Impact | High cost for throwing exceptions | Result is zero-cost abstraction |
| Philosophy | "Optimistic" path, exceptions for special cases | "Pessimistic" path, explicitly handle all possible errors |

## Best Practices

1. **Prioritize `Result`**: Make errors part of normal control flow
2. **Use `unwrap/expect` cautiously**: Only use when certain of no errors or in prototype code
3. **Avoid panic in library code**: Provide `Result` interfaces and let callers decide
4. **Use `?` operator**: Simplify error propagation
5. **Library code should avoid panic**: Provide `Result` interfaces for callers

Rust's design encourages developers to consider all possible error cases in advance, using the type system to ensure most runtime errors are caught at compile time. This is the most fundamental difference from Java exception handling.

---

# Chain Operations Using Tokio and Anyhow

Tokio and Anyhow are two important libraries for Rust asynchronous programming and error handling. Combined use can build clear and robust asynchronous operation chains. Here's how to chain operations with them:

## 1. Basic Combination Method

### Dependency Configuration
```toml
[dependencies]
tokio = { version = "1.0", features = ["full"] }
anyhow = "1.0"
```

### Basic Example
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

## 2. Chain Operation Patterns

### Using `and_then` Combination
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
    // Transformation logic
    Ok(data.to_uppercase())
}
```

## 3. Chain Processing Using `?` Operator

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

## 4. Complex Pipeline Combination

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
    // Processing logic
    Ok(vec![f1.to_owned(), f2.to_owned()])
}

fn validate_result(data: &[String]) -> Result<()> {
    if data.iter().any(|s| s.is_empty()) {
        anyhow::bail!("Empty string in result");
    }
    Ok(())
}
```

## 5. Using `try_join!` for Parallel Operations

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

## 6. Error Handling and Context Addition

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

## 7. Advanced Usage with Custom Error Types

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

## Best Practices

1. **Use `context()` reasonably**: Add meaningful context information to errors
2. **Keep error types consistent**: Use the same error type or `anyhow::Error` in pipelines
3. **Split functions appropriately**: Avoid overly long chain calls, maintain readability
4. **Utilize `?` operator**: Simplify error propagation
5. **Consider parallelization**: Use `try_join!` for independent operations to improve performance

This combination maintains Rust's powerful type safety while providing good error context information through Anyhow, and implements efficient asynchronous operations using Tokio.