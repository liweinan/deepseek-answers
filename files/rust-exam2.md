# Rust 编程语言测试卷

## 第一部分：选择题 (每题5分，共25分)

1. Rust 中的所有权系统主要解决了什么问题？
   A. 内存泄漏
   B. 数据竞争
   C. 空指针异常
   D. 内存安全和并发安全

   **答案与解析**：D。Rust的所有权系统通过编译时的严格检查，确保了内存安全和并发安全，避免了数据竞争和悬垂指针等问题。

2. 下面哪个是 Rust 中的有效变量声明？
   A. let x = 5;
   B. let mut x: i32 = 5;
   C. const x = 5;
   D. A 和 B 都正确

   **答案与解析**：D。A是不可变变量声明，B是可变的带类型注解的变量声明，都是有效的。C错误是因为const需要显式类型注解。

3. 关于 trait 的说法，哪个是正确的？
   A. 类似于其他语言中的接口
   B. 可以为外部类型实现外部 trait
   C. 不能有默认实现
   D. 一个类型只能实现一个 trait

   **答案与解析**：A。trait类似于接口，可以有默认实现(B错)，可以为自己的类型实现外部trait(
   但不能为外部类型实现外部trait，这是孤儿规则，所以B错)，一个类型可以实现多个trait(D错)。

4. 下面代码的输出是什么？
   ```rust
   fn main() {
       let s = String::from("hello");
       let s1 = s;
       println!("{}", s);
   }
   ```
   A. hello
   B. 编译错误
   C. 运行时错误
   D. 空字符串

   **答案与解析**：B。由于String没有实现Copy trait，赋值操作会导致所有权转移，s不再有效，所以println!会报编译错误。

5. 关于Rust的错误处理，正确的是：
   A. 只有panic!一种方式
   B. 使用Option和Result枚举
   C. 不支持异常处理
   D. B和C都正确

   **答案与解析**：D。Rust主要使用Option和Result进行错误处理，没有传统的异常机制，但可以通过panic!紧急处理不可恢复错误。

## 第二部分：填空题 (每题5分，共25分)

1. Rust 中用于确保线程安全的主要机制是______。

   **答案与解析**：所有权系统和借用检查器。Rust在编译时通过所有权规则和借用检查确保线程安全。

2. 实现一个结构体的Display trait时，需要实现的方法是______。

   **答案与解析**：fmt。Display trait要求实现fmt方法，签名是`fn fmt(&self, f: &mut Formatter) -> Result`。

3. Rust 中的智能指针类型有______、______和______(写出三个)。

   **答案与解析**：Box、Rc、Arc、RefCell、Mutex等中的任意三个。Box用于堆分配，Rc是引用计数，Arc是线程安全的引用计数，RefCell提供内部可变性。

4. 将`&str`转换为`String`的方法是______。

   **答案与解析**：to_string()或String::from()。例如：`let s = "hello".to_string();`或`let s = String::from("hello");`

5. 在Rust中，模式匹配常用的关键字是______。

   **答案与解析**：match。Rust中使用match表达式进行模式匹配，也可以使用if let简化某些情况。

## 第三部分：代码分析题 (每题10分，共20分)

1. 分析下面代码的问题并修正：
   ```rust
   fn longest(x: &str, y: &str) -> &str {
       if x.len() > y.len() {
           x
       } else {
           y
       }
   }
   ```

   **答案与解析**：
   问题：函数返回引用但没有指定生命周期参数，编译器无法确定返回引用的有效期。
   修正：
   ```rust
   fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
       if x.len() > y.len() {
           x
       } else {
           y
       }
   }
   ```
   需要明确指定输入和输出参数的生命周期关系。

2. 解释下面代码的输出原因：
   ```rust
   fn main() {
       let v = vec![1, 2, 3];
       let iter = v.iter().map(|x| x * 2);
       println!("{:?}", v);
       println!("{:?}", iter.collect::<Vec<_>>());
   }
   ```

   **答案与解析**：
   输出：
   ```
   [1, 2, 3]
   [2, 4, 6]
   ```
   原因：iter()获取的是不可变引用，map操作是惰性的，只有调用collect()时才会实际执行。原始向量v在整个过程中未被修改。

## 第四部分：编程题 (每题15分，共30分)

1. 实现一个简单的计算器结构体Calculator，支持加、减、乘、除四种运算，并处理除零错误。

   **参考答案**：
   ```rust
   #[derive(Debug)]
   enum CalcError {
       DivisionByZero,
   }
   
   struct Calculator;
   
   impl Calculator {
       fn add(a: f64, b: f64) -> f64 {
           a + b
       }
       
       fn sub(a: f64, b: f64) -> f64 {
           a - b
       }
       
       fn mul(a: f64, b: f64) -> f64 {
           a * b
       }
       
       fn div(a: f64, b: f64) -> Result<f64, CalcError> {
           if b == 0.0 {
               Err(CalcError::DivisionByZero)
           } else {
               Ok(a / b)
           }
       }
   }
   
   // 使用示例
   fn main() {
       println!("Add: {}", Calculator::add(5.0, 3.0));
       match Calculator::div(10.0, 0.0) {
           Ok(result) => println!("Div: {}", result),
           Err(e) => println!("Error: {:?}", e),
       }
   }
   ```

2. 实现一个线程安全的计数器，使用Arc和Mutex来允许多线程安全地递增计数。

   **参考答案**：
   ```rust
   use std::sync::{Arc, Mutex};
   use std::thread;
   
   fn main() {
       let counter = Arc::new(Mutex::new(0));
       let mut handles = vec![];
   
       for _ in 0..10 {
           let counter = Arc::clone(&counter);
           let handle = thread::spawn(move || {
               let mut num = counter.lock().unwrap();
               *num += 1;
           });
           handles.push(handle);
       }
   
       for handle in handles {
           handle.join().unwrap();
       }
   
       println!("Result: {}", *counter.lock().unwrap());
   }
   ```
   解析：使用Arc实现多所有权，Mutex提供内部可变性，确保线程安全。每个线程获取锁后递增计数器，最终结果为10。

---

这份试卷涵盖了Rust的核心概念，包括所有权系统、trait、错误处理、并发编程等。难度适中，适合检验对Rust基础知识的掌握程度。

---

# Rust 综合应用试卷：生命周期、Move语义、泛型和类型

## 第一部分：生命周期与泛型

### 题目 1

```rust
struct SharedData<'a, T> {
    data: &'a T,
    metadata: String,
}

impl<'a, T> SharedData<'a, T> {
    fn new(data: &'a T, metadata: String) -> Self {
        SharedData { data, metadata }
    }

    // 请实现一个方法，返回data的引用和metadata的元组
    fn get_parts(&self) -> (&T, &str) {
        todo!()
    }
}

fn main() {
    let value = 42;
    let shared = SharedData::new(&value, "Answer".to_string());
    let (data_ref, meta) = shared.get_parts();
    println!("Data: {}, Metadata: {}", data_ref, meta);
}
```

**问题**：补全 `get_parts` 方法的实现，使其能正确返回 `data` 的引用和 `metadata` 的切片。

## 第二部分：Move语义与泛型

### 题目 2

```rust
fn process_and_drop<T: std::fmt::Display>(item: T) {
    println!("Processing: {}", item);
    // 这里item被drop
}

fn main() {
    let s = String::from("Hello");
    process_and_drop(s);
    // 下面这行代码会编译通过吗？为什么？
    println!("Original string: {}", s);
}
```

**问题**：1. 解释 `process_and_drop` 函数的行为；2. 最后的 `println!` 能编译通过吗？为什么？

## 第三部分：类型别名与泛型

### 题目 3

```rust
type Result<T> = std::result::Result<T, String>;

fn parse_number(s: &str) -> Result<i32> {
    s.parse().map_err(|e| format!("Parse error: {}", e))
}

fn double_number(s: &str) -> Result<i32> {
    let num = parse_number(s)?;
    Ok(num * 2)
}

fn main() {
    match double_number("42") {
        Ok(n) => println!("Result: {}", n),
        Err(e) => println!("Error: {}", e),
    }
}
```

**问题**：1. 解释 `Result<T>` 类型别名的含义；2. `double_number` 函数中的 `?` 操作符在这里如何工作？

## 第四部分：综合应用

### 题目 4

```rust
trait Processor<T> {
    type Output;

    fn process(&self, data: T) -> Self::Output;
}

struct StringLengthProcessor;

impl Processor<&str> for StringLengthProcessor {
    type Output = usize;

    fn process(&self, data: &str) -> usize {
        data.len()
    }
}

struct MoveStringProcessor;

impl Processor<String> for MoveStringProcessor {
    type Output = String;

    fn process(&self, data: String) -> String {
        data.to_uppercase()
    }
}

fn main() {
    let s = "hello".to_string();

    // 使用StringLengthProcessor
    let len = StringLengthProcessor.process(&s);
    println!("Length: {}", len);

    // 使用MoveStringProcessor
    let upper = MoveStringProcessor.process(s);
    println!("Uppercase: {}", upper);

    // 下面这行代码会编译通过吗？为什么？
    println!("Original string: {}", s);
}
```

**问题**：1. 解释两个不同的 `Processor` 实现的区别；2. 最后的 `println!` 能编译通过吗？为什么？

## 第五部分：高级综合

### 题目 5

```rust
struct Wrapper<T>(T);

impl<T: Clone> Wrapper<T> {
    fn clone_inner(&self) -> T {
        self.0.clone()
    }
}

fn process_wrapped_string(w: Wrapper<String>) -> String {
    let s = w.clone_inner();
    s + " processed"
}

fn main() {
    let original = String::from("data");
    let wrapped = Wrapper(original);

    let processed = process_wrapped_string(wrapped);
    println!("Processed: {}", processed);

    // 下面这行代码会编译通过吗？为什么？
    println!("Original: {}", wrapped.0);
}
```

**问题**：1. 解释 `Wrapper` 结构体及其实现；2. 为什么 `process_wrapped_string` 能接受 `wrapped` 作为参数？3. 最后的
`println!` 能编译通过吗？为什么？

---

## 解答部分

### 题目 1 解答

```rust
fn get_parts(&self) -> (&T, &str) {
    (self.data, &self.metadata)
}
```

**解释**：

1. 方法返回一个元组，包含 `data` 的引用和 `metadata` 的字符串切片
2. 生命周期由编译器自动推导，`&T` 使用结构体本身的生命周期 `'a`，`&str` 使用 `self` 的生命周期

### 题目 2 解答

1. `process_and_drop` 接受一个泛型参数 `T`，打印它然后丢弃（所有权转移）
2. 最后的 `println!` 不能编译通过，因为 `s` 的所有权已经转移到 `process_and_drop` 函数中，之后不能再使用

### 题目 3 解答

1. `Result<T>` 是标准库 `Result` 的类型别名，错误类型固定为 `String`
2. `?` 操作符会自动解包 `Result`，如果是 `Ok` 则取出值，如果是 `Err` 则提前返回错误

### 题目 4 解答

1. 两个 `Processor` 实现的区别：
    - `StringLengthProcessor` 处理 `&str` 借用，返回 `usize`
    - `MoveStringProcessor` 处理 `String` 所有权，返回新的 `String`
2. 最后的 `println!` 不能编译通过，因为 `s` 的所有权已经通过 `MoveStringProcessor.process(s)` 转移

### 题目 5 解答

1. `Wrapper` 是一个泛型元组结构体，`clone_inner` 方法要求 `T` 实现 `Clone`
2. `process_wrapped_string` 能接受 `wrapped` 因为函数参数要求 `Wrapper<String>` 类型
3. 最后的 `println!` 不能编译通过，因为 `wrapped` 的所有权已经转移到 `process_wrapped_string` 函数中

---

# # Rust 生命周期和 Move 语义练习题

## 生命周期练习题

### 题目 1

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

fn main() {
    let string1 = String::from("long string is long");
    let result;
    {
        let string2 = String::from("xyz");
        result = longest(string1.as_str(), string2.as_str());
    }
    println!("The longest string is {}", result);
}
```

**问题**：这段代码能编译通过吗？如果不能，为什么？

### 题目 2

```rust
struct ImportantExcerpt<'a> {
    part: &'a str,
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find a '.'");
    let i;
    {
        i = ImportantExcerpt {
            part: first_sentence,
        };
    }
    println!("Excerpt: {}", i.part);
}
```

**问题**：这段代码能编译通过吗？为什么？

### 题目 3

```rust
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    &s[..]
}

fn main() {
    let my_string = String::from("hello world");
    let word = first_word(&my_string);
    my_string.clear();
    println!("the first word is: {}", word);
}
```

**问题**：这段代码能编译通过吗？为什么？

## Move 语义练习题

### 题目 4

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;
    println!("{}, world!", s1);
}
```

**问题**：这段代码能编译通过吗？为什么？

### 题目 5

```rust
fn take_ownership(s: String) {
    println!("{}", s);
}

fn main() {
    let s = String::from("hello");
    take_ownership(s);
    println!("{}", s);
}
```

**问题**：这段代码能编译通过吗？为什么？

### 题目 6

```rust
fn main() {
    let x = 5;
    let y = x;
    println!("x = {}, y = {}", x, y);
}
```

**问题**：这段代码能编译通过吗？为什么？

## 解答

### 题目 1 解答

**答案**：不能编译通过。

**解释**：`longest` 函数返回的引用的生命周期与两个参数中较短的那个相同。在这个例子中，`string2` 的生命周期比 `string1` 短，所以
`result` 的生命周期不能超过 `string2` 的生命周期。但是在 `println!` 时，`string2` 已经离开了作用域，导致 `result`
成为悬垂引用，违反了 Rust 的借用规则。

### 题目 2 解答

**答案**：能编译通过。

**解释**：`ImportantExcerpt` 结构体有一个生命周期参数 `'a`，它的 `part` 字段是一个引用。`first_sentence` 的生命周期与
`novel` 相同，而 `i` 的生命周期虽然在一个内部作用域中初始化，但 `first_sentence` 的生命周期足够长，因此 `i.part` 在
`println!` 时仍然是有效的。

### 题目 3 解答

**答案**：不能编译通过。

**解释**：`first_word` 返回了一个 `my_string` 的切片引用，然后 `my_string.clear()` 尝试可变地借用 `my_string` 来清空它。这违反了
Rust 的借用规则：不能同时存在可变借用和不可变借用。`word` 是不可变借用，而 `clear()` 需要可变借用。

### 题目 4 解答

**答案**：不能编译通过。

**解释**：`String` 类型没有实现 `Copy` trait，所以在 `let s2 = s1;` 时发生了移动（move）而不是拷贝。移动后 `s1` 不再有效，因此不能在
`println!` 中使用它。

### 题目 5 解答

**答案**：不能编译通过。

**解释**：`take_ownership` 函数获取了 `s` 的所有权，在函数调用后 `s` 被移动到了函数内部，因此在 `main` 函数中再次使用 `s`
会导致编译错误，因为 `s` 已经不再有效。

### 题目 6 解答

**答案**：能编译通过。

**解释**：`i32` 是实现了 `Copy` trait 的类型，所以 `let y = x;` 执行的是拷贝而不是移动。`x`
仍然有效，可以在之后使用。基本标量类型（如整数、浮点数、布尔值、字符）和只包含这些类型的元组通常都实现了 `Copy` trait。

---

