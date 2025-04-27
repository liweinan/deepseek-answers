
# Rust 语言速查表（中文版）

Rust 是一门注重安全、性能和并发性的系统编程语言。本速查表涵盖了 Rust 的核心概念、语法和常用模式，适合初学者和有经验的开发者快速参考。

---

## 变量与数据类型

### 变量声明
- **不可变变量**（默认）：使用 `let` 声明，值不可更改。
- **可变变量**：使用 `let mut` 声明，允许修改值。
- **常量**：使用 `const` 声明，值在编译时确定，且不可更改。
- **静态变量**：使用 `static` 声明，具有固定内存地址和全局生命周期。

```rust
// 不可变变量
let x = 42; // 类型推导为 i32
let y: f64 = 3.14; // 显式指定类型

// 可变变量
let mut counter = 0;
counter += 1; // 合法

// 常量
const MAX_VALUE: u32 = 100_000; // 使用下划线分隔数字以提高可读性

// 静态变量
static GREETING: &str = "Hello, Rust!";
```

### 基本数据类型
Rust 的数据类型分为标量类型（单一值）和复合类型（多值组合）。

#### 标量类型
- **整数**：有符号（`i8`, `i16`, `i32`, `i64`, `i128`, `isize`）和无符号（`u8`, `u16`, `u32`, `u64`, `u128`, `usize`）。
    - `isize` 和 `usize` 大小取决于系统架构（32 位或 64 位）。
- **浮点数**：`f32`（单精度）和 `f64`（双精度）。
- **布尔值**：`bool`，值为 `true` 或 `false`。
- **字符**：`char`，表示单个 Unicode 标量值（4 字节）。

```rust
let signed_int: i32 = -42;
let unsigned_int: u32 = 42;
let float_num: f64 = 3.14159;
let is_active: bool = true;
let emoji: char = '😊';
```

#### 复合类型
- **元组**（Tuple）：固定长度，元素可以是不同类型。
- **数组**（Array）：固定长度，元素必须是同一类型。
- **字符串**：
    - `&str`：字符串切片，通常用于字符串字面量，存储在静态内存中。
    - `String`：动态分配的字符串，可增长，存储在堆上。

```rust
// 元组
let tup: (i32, f64, char) = (500, 6.4, 'x');
let (x, y, z) = tup; // 解构
let first = tup.0; // 访问第一个元素

// 数组
let arr: [i32; 3] = [1, 2, 3];
let first = arr[0]; // 访问第一个元素

// 字符串
let str_slice: &str = "Hello";
let owned_string: String = String::from("World");
```

---

## 控制流

### 条件语句
使用 `if`、`else if` 和 `else` 实现条件分支。条件表达式必须返回 `bool` 类型。

```rust
let number = 7;
if number > 0 {
    println!("正数");
} else if number < 0 {
    println!("负数");
} else {
    println!("零");
}
```

- **if 作为表达式**：`if` 可以返回一个值，分支必须返回相同类型。

```rust
let result = if number > 0 { "正数" } else { "负数" };
```

### 循环
Rust 提供三种循环结构：`loop`、`while` 和 `for`。

- **loop**：无限循环，直到显式 `break`。
- **while**：基于条件循环。
- **for**：迭代器循环，常用于遍历范围或集合。

```rust
// loop
let mut count = 0;
loop {
    if count >= 3 {
        break; // 退出循环
    }
    println!("循环次数: {}", count);
    count += 1;
}

// while
while count < 5 {
    println!("while 循环: {}", count);
    count += 1;
}

// for
for i in 0..5 { // 范围 0 到 4
    println!("for 循环: {}", i);
}
```

### 模式匹配
`match` 表达式用于模式匹配，处理多种可能性。必须覆盖所有可能情况（穷尽匹配）。

```rust
let value = 2;
match value {
    1 => println!("值为 1"),
    2 | 3 => println!("值为 2 或 3"),
    4..=10 => println!("值在 4 到 10 之间"),
    _ => println!("其他值"), // 通配符
}
```

---

## 函数

### 函数定义
使用 `fn` 关键字定义函数。返回值类型用 `->` 指定，最后一行表达式隐式返回（无需 `return`）。

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b // 隐式返回
}

fn greet(name: &str) -> String {
    return format!("你好, {}!", name); // 显式返回
}
```

### 闭包
闭包是匿名函数，可以捕获环境中的变量。

```rust
let multiply = |x: i32, y: i32| x * y;
let result = multiply(5, 3); // 15
```

---

## 所有权与借用

Rust 的核心特性是所有权系统，确保内存安全。

### 所有权规则
1. 每个值有且仅有一个所有者。
2. 当所有者超出作用域时，值被销毁。
3. 值在任意时刻只能有一个可变引用或任意数量的不可变引用。

```rust
let s1 = String::from("hello");
let s2 = s1; // s1 被移动，s1 不可再用
// println!("{}", s1); // 错误：s1 已失效
```

### 借用
- **不可变借用**（`&`）：允许多个不可变引用。
- **可变借用**（`&mut`）：仅允许一个可变引用，且不能同时存在不可变引用。

```rust
fn print_string(s: &String) {
    println!("{}", s);
}

fn append_string(s: &mut String) {
    s.push_str(" world");
}

let mut text = String::from("hello");
print_string(&text); // 不可变借用
append_string(&mut text); // 可变借用
```

---

## 结构体与枚举

### 结构体
Rust 支持三种结构体：经典结构体、元组结构体和单元结构体。

```rust
// 经典结构体
struct User {
    username: String,
    email: String,
    active: bool,
}

// 元组结构体
struct Color(u8, u8, u8);

// 单元结构体
struct Empty;

// 实现方法
impl User {
    fn new(username: String, email: String) -> User {
        User {
            username,
            email,
            active: true,
        }
    }
}
```

### 枚举
枚举用于定义一组相关但互斥的选项。

```rust
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

enum Option<T> {
    Some(T),
    None,
}
```

---

## 错误处理

Rust 使用 `Option` 和 `Result` 进行错误处理，避免空指针等问题。

### Option
表示值可能存在或不存在。

```rust
let maybe_value: Option<i32> = Some(42);
match maybe_value {
    Some(x) => println!("值是 {}", x),
    None => println!("无值"),
}

// 使用 unwrap（谨慎）
let value = maybe_value.unwrap_or(0); // 如果 None，返回 0
```

### Result
表示操作可能成功（`Ok`）或失败（`Err`）。

```rust
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err(String::from("除零错误"))
    } else {
        Ok(a / b)
    }
}

match divide(10.0, 2.0) {
    Ok(result) => println!("结果: {}", result),
    Err(e) => println!("错误: {}", e),
}
```

---

## 集合类型

### 向量（Vec）
动态数组，支持增长。

```rust
let mut v: Vec<i32> = Vec::new();
v.push(1);
v.push(2);
let v2 = vec![3, 4, 5]; // 宏创建
```

### 哈希表（HashMap）
键值对存储。

```rust
use std::collections::HashMap;
let mut scores = HashMap::new();
scores.insert("Blue".to_string(), 10);
scores.insert("Red".to_string(), 20);
```

### 字符串
`String` 是可变的堆分配字符串，`&str` 是不可变的字符串切片。

```rust
let mut s = String::from("Hello");
s.push_str(", Rust!");
let slice: &str = &s[0..5]; // "Hello"
```

---

## 特性（Traits）

特性定义共享行为，类似于接口。

```rust
trait Describable {
    fn describe(&self) -> String;
}

struct Person {
    name: String,
}

impl Describable for Person {
    fn describe(&self) -> String {
        format!("Person: {}", self.name)
    }
}
```

---

## 模块系统

模块用于组织代码，控制可见性。

```rust
mod utils {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }
}

use utils::add;
println!("加法结果: {}", add(2, 3));
```

---

## 并发

Rust 提供线程和同步原语，确保安全并发。

```rust
use std::thread;
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..5 {
    let counter = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    });
    handles.push(handle);
}
```

---

## 常用宏

- `println!`：格式化输出。
- `vec!`：快速创建向量。
- `assert_eq!`：断言相等。
- `todo!`：标记未实现代码。

```rust
println!("值: {}", 42);
let v = vec![1, 2, 3];
assert_eq!(2 + 2, 4);
```

---

## Cargo 命令

```bash
# 创建新项目
cargo new my_project

# 构建
cargo build

# 运行
cargo run

# 测试
cargo test

# 格式化代码
cargo fmt

# 检查代码
cargo clippy
```

---

## 常用第三方库

在 `Cargo.toml` 中添加依赖：

```toml
[dependencies]
serde = { version = "1.0", features = ["derive"] } # 序列化/反序列化
tokio = { version = "1.0", features = ["full"] } # 异步运行时
rand = "0.8" # 随机数生成
```

---

## 调试与属性

### 常用属性
- `#[derive(Debug)]`：自动实现调试输出。
- `#[cfg(test)]`：条件编译测试代码。
- `#[allow(unused)]`：忽略未使用警告。

```rust
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

println!("{:?}", Point { x: 1, y: 2 });
```

### 调试技巧
- 使用 `dbg!` 宏快速打印调试信息。
- 使用 `log` 库记录日志。

```rust
let x = 42;
dbg!(x); // 打印文件名、行号和值
```

---

本速查表涵盖了 Rust 的核心功能和语法，适合快速查阅。如需深入学习，请参考 [Rust 官方文档](https://doc.rust-lang.org/book/)。

