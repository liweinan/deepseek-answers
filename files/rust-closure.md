# Rust闭包练习卷

## **一、选择题（每题4分，共20分）**

1. 以下哪个选项正确描述了Rust闭包的特点？  
   A. 闭包无法捕获环境变量  
   B. 闭包总是以`move`方式捕获变量  
   C. 闭包可以根据使用方式实现`Fn`、`FnMut`或`FnOnce` trait  
   D. 闭包无法作为函数参数传递

2. 当闭包使用`move`关键字时，会发生什么？  
   A. 闭包只能以不可变借用捕获变量  
   B. 闭包会强制捕获变量的所有权  
   C. 闭包无法捕获任何变量  
   D. 闭包会自动实现`FnMut` trait

3. 以下闭包的trait实现是什么？
   ```rust
   let x = 10;
   let closure = || println!("x is {}", x);
   ```  
   A. `FnOnce`  
   B. `FnMut`  
   C. `Fn`  
   D. 以上都不是

4. 在多线程场景中，为什么通常需要使用`move`关键字？  
   A. 为了避免闭包捕获变量  
   B. 为了确保线程拥有数据的独立副本  
   C. 为了让闭包实现`FnMut` trait  
   D. 为了减少闭包的内存占用

5. 以下哪个闭包可以多次调用？  
   A. 实现`FnOnce`但不实现`Fn`的闭包  
   B. 实现`Fn`的闭包  
   C. 使用`move`并消耗变量的闭包  
   D. 不捕获任何变量的闭包，但实现`FnOnce`

---

## **二、填空题（每题5分，共20分）**

1. Rust闭包可以捕获环境变量，捕获方式包括________、________和________三种。
2. 在闭包定义前添加`move`关键字，会使闭包________环境变量的所有权。
3. 如果一个闭包需要修改捕获的变量，它至少需要实现________ trait。
4. 在以下代码中，闭包捕获变量`x`的方式是________：
   ```rust
   let x = 10;
   let closure = || println!("x is {}", x);
   ```

---

## **三、代码分析题（每题10分，共30分）**

1. 分析以下代码，说明为什么会报错，并提供修复方法：
   ```rust
   fn main() {
       let s = String::from("hello");
       let closure = || println!("s is {}", s);
       std::thread::spawn(closure);
       println!("s is still here: {}", s);
   }
   ```

2. 以下代码的输出是什么？为什么？
   ```rust
   fn main() {
       let mut x = 10;
       let mut closure = move || {
           x += 1;
           println!("x is {}", x);
       };
       closure();
       println!("x outside is {}", x);
   }
   ```

3. 以下代码中，闭包实现了哪个trait？为什么？
   ```rust
   fn main() {
       let s = String::from("hello");
       let closure = move || drop(s);
   }
   ```

---

## **四、编程题（每题15分，共30分）**

1. 编写一个程序，使用闭包和`move`关键字，将一个`Vec<i32>`传递给新线程，并在新线程中打印向量内容。确保主线程无法再次访问该向量。

2. 编写一个函数`apply_twice`，接受一个闭包和一个整数参数`x`，并将闭包应用于`x`两次，返回最终结果。闭包需要实现`Fn` trait。提供示例调用代码。

---

## **参考答案**

### **一、选择题**
1. C （闭包可以捕获环境变量，并根据使用方式实现`Fn`、`FnMut`或`FnOnce`）
2. B （`move`强制闭包捕获变量的所有权）
3. C （只读取`x`，实现`Fn`）
4. B （`move`确保线程拥有独立数据副本）
5. B （实现`Fn`的闭包可以多次调用）

### **二、填空题**
1. 不可变借用、可变借用、所有权转移
2. 捕获
3. `FnMut`
4. 不可变借用

### **三、代码分析题**
1. **问题**：`std::thread::spawn`需要闭包拥有捕获变量的所有权，但`closure`默认以借用方式捕获`s`，而`s`的生命周期可能在主线程结束时销毁，导致线程访问无效数据。  
   **修复**：在`closure`前添加`move`关键字：
   ```rust
   let closure = move || println!("s is {}", s);
   std::thread::spawn(closure);
   ```
   修复后，`s`的所有权转移到闭包，主线程无法再次访问`s`。

2. **输出**：
   ```
   x is 11
   x outside is 10
   ```
   **原因**：`move`关键字使闭包捕获`x`的副本（`i32`是`Copy`类型），闭包修改的是副本，不会影响原始`x`。

3. **答案**：闭包实现`FnOnce`。  
   **原因**：闭包通过`move`捕获`s`的所有权，并调用`drop(s)`消耗了`s`，因此只能调用一次，符合`FnOnce`的定义。

### **四、编程题**

1. **代码**：
   ```rust
   use std::thread;
   
   fn main() {
       let data = vec![1, 2, 3];
       let handle = thread::spawn(move || {
           println!("Data in thread: {:?}", data);
       });
       handle.join().unwrap();
       // println!("{:?}", data); // 错误：data已移动
   }
   ```

2. **代码**：
   ```rust
   fn apply_twice<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 {
       f(f(x))
   }
   
   fn main() {
       let add_one = |x| x + 1;
       let result = apply_twice(add_one, 5);
       println!("Result: {}", result); // 输出：Result: 7
   }
   ```

---

你提到的问题涉及Rust中`move`关键字的行为以及变量捕获的机制。让我们仔细分析代码，解释为什么`x`在`move`闭包执行后仍然可以在`outside`使用，以及为什么会产生这样的结果。

### **代码回顾**
```rust
fn main() {
    let mut x = 10;
    let mut closure = move || {
        x += 1;
        println!("x is {}", x);
    };
    closure();
    println!("x outside is {}", x);
}
```

**输出**：
```
x is 11
x outside is 10
```

### **问题分析：为什么`x`在`outside`仍然可用？**

1. **`move`关键字的作用**：
    - 在Rust中，`move`关键字强制闭包捕获环境变量的所有权，而不是以借用（`&T`或`&mut T`）的方式捕获。
    - 当闭包捕获变量时，`move`会将变量的所有权转移到闭包中。通常，这意味着原始变量在原始作用域中变得不可用（因为所有权被转移）。

2. **关键点：`i32`是`Copy`类型**：
    - 在Rust中，`i32`是一个实现了`Copy` trait的类型。`Copy`类型在转移所有权时不会真正“移动”数据，而是会自动创建一个副本。
    - 当闭包使用`move`捕获`x`时，实际上是将`x`的**副本**（一个新的`i32`值）移动到闭包中，而不是移动原始的`x`。
    - 因此，原始的`x`仍然存在于主作用域中，并且可以继续使用。

3. **闭包中的修改**：
    - 在闭包内部，`x += 1`修改的是闭包捕获的`x`副本（因为`move`创建了一个独立的`i32`值）。
    - 由于`x`是`Copy`类型，原始的`x`（在主作用域中）不会受到闭包中修改的影响。
    - 这就是为什么闭包打印`x is 11`，而主作用域打印`x outside is 10`。

4. **对比非`Copy`类型**：
   如果`x`是一个非`Copy`类型（例如`String`），情况会不同。`move`会将`x`的所有权完全转移到闭包中，主作用域无法再次访问`x`，否则会导致编译错误。例如：

   ```rust
   fn main() {
       let x = String::from("hello");
       let closure = move || {
           println!("x is {}", x);
       };
       closure();
       println!("x outside is {}", x); // 错误：x已被移动
   }
   ```

   在这个例子中，`x`是`String`（非`Copy`类型），`move`会导致`x`的所有权转移到闭包，主作用域无法再使用`x`。

### **回答问题：是`move`自己clone了一份吗？**
- 严格来说，`move`本身并没有调用`clone`方法，而是利用了`i32`的`Copy` trait。
- 当`move`捕获一个`Copy`类型的变量时，Rust会自动复制该变量的值（本质上是一个字节级别的拷贝），而不是移动原始数据。这是因为`Copy`类型的语义保证了复制是廉价且安全的。
- 因此，可以说`move`在捕获`i32`时，隐式地创建了一个副本（通过`Copy`），但这并不是通过显式的`clone`方法完成的。

### **进一步验证**
为了更清楚地理解`Copy`和`move`的行为，可以尝试以下代码：

```rust
fn main() {
    let mut x = 10;
    let mut closure = move || {
        x += 1;
        println!("x is {}", x);
    };
    closure();
    closure(); // 再次调用
    println!("x outside is {}", x);
}
```

**输出**：
```
x is 11
x is 12
x outside is 10
```

- 闭包内部的`x`是独立的副本，多次调用闭包会继续修改这个副本（因为闭包是`mut`的）。
- 主作用域的`x`始终保持为`10`，因为它从未被修改。

### **如何避免副本行为？**
如果希望闭包完全“拥有”`x`并确保主作用域无法访问，可以使用非`Copy`类型，或者通过其他方式（如将`x`包装在`Box`或`Rc`中）改变其所有权语义。例如：

```rust
fn main() {
    let x = Box::new(10); // Box<i32> 不是Copy类型
    let mut closure = move || {
        println!("x is {}", x);
    };
    closure();
    // println!("x outside is {}", x); // 错误：x已被移动
}
```

### **总结**
- `x`在`outside`仍然可用的原因是`i32`实现了`Copy` trait，`move`捕获时创建了`x`的副本，原始`x`未被移动。
- `move`本身没有显式调用`clone`，但`Copy`类型的语义导致值被复制到闭包中。
- 闭包修改的是捕获的副本，因此主作用域的`x`保持不变。
- 如果需要真正的所有权转移（避免副本），可以使用非`Copy`类型（如`String`或`Box<T>`）。

如果你有更多关于闭包或所有权的疑问，欢迎进一步讨论！
