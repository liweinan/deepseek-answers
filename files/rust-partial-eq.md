# PartialEq

好的！下面我将通过一个简单的例子展示如何为一个自定义 `struct` 实现 `PartialEq` trait，并用它来进行比较。这个例子会创建一个表示二维点的 `Point` 结构体，并实现 `PartialEq` 以比较两个点是否相等。然后，我们会用 `assert_eq!` 和手动比较来演示 `PartialEq` 的使用。

### 示例代码

```rust
// 定义一个表示二维点的结构体
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

// 为 Point 实现 PartialEq trait
impl PartialEq for Point {
    fn eq(&self, other: &Self) -> bool {
        self.x == other.x && self.y == other.y
    }
}

fn main() {
    // 创建几个 Point 实例
    let p1 = Point { x: 1, y: 2 };
    let p2 = Point { x: 1, y: 2 };
    let p3 = Point { x: 3, y: 4 };

    // 使用 == 运算符比较（依赖 PartialEq）
    println!("p1 == p2: {}", p1 == p2); // true
    println!("p1 == p3: {}", p1 == p3); // false

    // 使用 assert_eq! 宏进行比较
    assert_eq!(p1, p2); // 通过
    assert_eq!(p1, p3); // 会 panic，因为 p1 != p3
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_point_equality() {
        let p1 = Point { x: 5, y: -3 };
        let p2 = Point { x: 5, y: -3 };
        let p3 = Point { x: 5, y: 0 };

        // 测试相等
        assert_eq!(p1, p2); // 通过
        assert_ne!(p1, p3); // 通过

        // 测试 Vec<Point> 与数组的比较
        let points_vec = vec![p1, p2];
        let points_array = [Point { x: 5, y: -3 }, Point { x: 5, y: -3 }];
        assert_eq!(points_vec, points_array); // 通过
    }
}
```

### 代码解析

#### 1. 定义 `Point` 结构体
- `Point` 是一个简单的结构体，包含两个字段：`x` 和 `y`，都是 `i32` 类型。
- 使用 `#[derive(Debug)]` 以便可以通过 `println!` 打印 `Point` 的内容（用于调试）。

#### 2. 实现 `PartialEq`
- 通过 `impl PartialEq for Point`，我们为 `Point` 实现了 `PartialEq` trait。
- `PartialEq` 要求实现 `eq` 方法，签名是 `fn eq(&self, other: &Self) -> bool`。
    - `self` 是第一个 `Point` 实例，`other` 是要比较的另一个 `Point` 实例。
    - 方法返回 `bool`，表示两个实例是否相等。
- 在 `eq` 方法中，我们检查 `self.x == other.x && self.y == other.y`，即两个点的坐标都相等时认为它们相等。

#### 3. 在 `main` 函数中演示
- 创建三个 `Point` 实例：`p1` 和 `p2` 坐标相同，`p3` 坐标不同。
- 使用 `==` 运算符比较：
    - `p1 == p2` 返回 `true`，因为它们的 `x` 和 `y` 相同。
    - `p1 == p3` 返回 `false`，因为它们的坐标不同。
- 使用 `assert_eq!(p1, p2)` 测试相等性，验证 `PartialEq` 实现正确。
- 尝试 `assert_eq!(p1, p3)` 会导致 panic，因为它们不相等（注释掉以避免程序终止）。

#### 4. 测试模块
- 在 `tests` 模块中，创建了更多的 `Point` 实例进行测试。
- 使用 `assert_eq!(p1, p2)` 验证相等性。
- 使用 `assert_ne!(p1, p3)` 验证不相等性（`assert_ne!` 检查两个值是否不相等）。
- **关键演示**：比较 `Vec<Point>` 和 `[Point; N]` 数组：
    - 创建一个 `Vec<Point>`（`points_vec`）和一个 `[Point; 2]` 数组（`points_array`）。
    - 使用 `assert_eq!(points_vec, points_array)` 验证它们相等。
    - 这展示了 `Vec<T>` 可以与 `[T; N]` 或 `&[T]` 进行比较，只要 `T` 实现了 `PartialEq`，就像在你之前的问题中 `Vec<String>` 与 `[&str; 4]` 的比较。

#### 5. 为什么 `Vec<Point>` 可以与 `[Point; N]` 比较
- Rust 的标准库为 `Vec<T>` 实现了 `PartialEq<&[U]>` 和 `PartialEq<[U; N]>`，其中 `T: PartialEq<U>`。
- 在这个例子中，`T` 是 `Point`，`U` 也是 `Point`（因为数组中的元素也是 `Point`）。
- 由于我们为 `Point` 实现了 `PartialEq`，Rust 可以逐元素比较 `Vec<Point>` 和 `[Point; N]`，就像 `Vec<String>` 可以与 `[&str; N]` 比较一样。

### 输出结果
运行代码（假设 `assert_eq!(p1, p3)` 被注释掉以避免 panic），输出为：

```
p1 == p2: true
p1 == p3: false
```

运行 `cargo test`，所有测试都会通过：

```
running 1 test
test tests::test_point_equality ... ok
```

### 扩展：如果不实现 `PartialEq`
如果不实现 `PartialEq`，尝试比较 `p1 == p2` 或使用 `assert_eq!(p1, p2)` 会导致编译错误：

```
error[E0369]: binary operation `==` cannot be applied to type `Point`
```

这是因为 `==` 运算符依赖于 `PartialEq` trait，而 Rust 不会自动为自定义类型实现它。

### 扩展：自动派生 `PartialEq`
Rust 允许通过 `#[derive(PartialEq)]` 自动实现 `PartialEq`，例如：

```rust
#[derive(Debug, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}
```

这会自动生成与我们手动实现的相同的 `eq` 方法（逐字段比较）。在这个例子中，手动实现是为了展示 `PartialEq` 的工作原理，但在实际开发中，如果比较逻辑是逐字段相等，通常会使用 `#[derive(PartialEq)]`。

### 总结
- 我们创建了一个 `Point` 结构体并手动实现了 `PartialEq`，以便比较两个点的坐标是否相等。
- 演示了使用 `==` 和 `assert_eq!` 进行比较。
- 在测试中展示了 `Vec<Point>` 与 `[Point; N]` 的比较，类似于你之前问题中 `Vec<String>` 与 `[&str; N]` 的情况。
- 这种比较依赖于 `PartialEq` 的实现，以及 Rust 标准库对 `Vec` 和数组/切片的 `PartialEq` 支持。

希望这个例子清楚地展示了 `PartialEq` 的实现和使用！如果有其他问题或需要更复杂的例子，请告诉我！

---

要了解 `Vec<T>` 如何实现 `PartialEq`，我们需要查看 Rust 标准库中 `Vec<T>` 的 `PartialEq` 实现，并分析其工作原理。以下我会详细解释 Rust 标准库中 `Vec<T>` 的 `PartialEq` 实现，结合你的需求（了解 `Vec` 如何实现 `PartialEq`），并提供一个简化的示例来演示其机制。

### 1. Rust 标准库中 `Vec<T>` 的 `PartialEq` 实现

`Vec<T>` 是 Rust 标准库中定义的一个动态数组类型，位于 `std::vec` 模块。它的 `PartialEq` 实现定义在标准库的 `vec.rs` 文件中。以下是关键部分的概述（基于 Rust 1.81.0 标准库源码，简化后）：

#### `PartialEq` 实现
在标准库中，`Vec<T>` 实现了 `PartialEq` trait，允许比较两个 `Vec` 或者 `Vec` 与其他类型（如切片 `&[U]` 或数组 `[U; N]`）。以下是主要的实现：

```rust
impl<T: PartialEq, A: Allocator> PartialEq for Vec<T, A> {
    #[inline]
    fn eq(&self, other: &Self) -> bool {
        self.as_slice() == other.as_slice()
    }
}

impl<T: PartialEq<U>, U, A: Allocator> PartialEq<&[U]> for Vec<T, A> {
    #[inline]
    fn eq(&self, other: &&[U]) -> bool {
        self.as_slice() == *other
    }
}

impl<T: PartialEq<U>, U, A: Allocator> PartialEq<&mut [U]> for Vec<T, A> {
    #[inline]
    fn eq(&self, other: &&mut [U]) -> bool {
        self.as_slice() == *other
    }
}

impl<T: PartialEq<U>, U, A: Allocator, const N: usize> PartialEq<[U; N]> for Vec<T, A> {
    #[inline]
    fn eq(&self, other: &[U; N]) -> bool {
        self.as_slice() == other.as_slice()
    }
}
```

#### 关键点解析
1. **`Vec<T, A>` 比较 `Vec<T, A>`**:
    - 实现 `PartialEq` for `Vec<T, A>`，其中 `T: PartialEq`（`T` 必须实现 `PartialEq`），`A: Allocator`（支持自定义分配器）。
    - 比较两个 `Vec` 时，调用 `self.as_slice() == other.as_slice()`。
    - `as_slice()` 将 `Vec<T>` 转换为 `&[T]`（切片），然后依赖切片的 `PartialEq` 实现。

2. **`Vec<T, A>` 比较 `&[U]`**:
    - 实现 `PartialEq<&[U]>`，其中 `T: PartialEq<U>`（`T` 和 `U` 可以比较）。
    - 比较 `Vec` 和切片时，将 `Vec` 转换为 `self.as_slice()`，并与 `other`（`&[U]`）直接比较。
    - 这允许 `Vec<String>` 与 `&[&str]` 比较，因为 `String: PartialEq<&str>`。

3. **`Vec<T, A>` 比较 `[U; N]`**:
    - 实现 `PartialEq<[U; N]>`，其中 `T: PartialEq<U>`，`N` 是数组长度。
    - 比较 `Vec` 和固定大小数组时，将 `Vec` 转换为 `self.as_slice()`，将数组转换为切片（`other.as_slice()`），然后比较两个切片。
    - 这就是为什么在你的原始问题中 `Vec<String>` 可以与 `[&str; 4]` 比较。

4. **切片的 `PartialEq` 实现**:
    - 切片 `&[T]` 的 `PartialEq` 实现（在 `std::slice` 模块）是 `Vec` 比较的核心：
      ```rust
      impl<T: PartialEq> PartialEq for [T] {
          fn eq(&self, other: &Self) -> bool {
              if self.len() != other.len() {
                  return false;
              }
              for i in 0..self.len() {
                  if self[i] != other[i] {
                      return false;
                  }
              }
              true
          }
      }
      ```
    - 它首先检查两个切片的长度是否相等。
    - 然后逐元素比较每个 `self[i]` 和 `other[i]`，依赖 `T` 的 `PartialEq` 实现。
    - 对于 `T: PartialEq<U>`（如 `String` 和 `&str`），它允许跨类型比较。

5. **为什么支持 `Vec<String>` 与 `[&str; N]`**:
    - 在你的例子中，`Vec<String>` 与 `[&str; 4]` 比较时：
        - `Vec<String>` 转换为 `&[String]`（通过 `as_slice()`）。
        - `[&str; 4]` 被视为 `&[&str]`（数组隐式转换为切片）。
        - 比较 `&[String]` 和 `&[&str]` 时，Rust 使用 `String: PartialEq<&str>` 的实现逐元素比较。
    - 因此，`assert_eq!(vec_string, [&str; N])` 能工作。

### 2. 简化的演示示例
为了进一步说明 `Vec<T>` 的 `PartialEq` 工作原理，我将创建一个简单的例子，定义一个自定义类型并实现 `PartialEq`，然后展示 `Vec` 如何与数组和切片比较。

```rust
// 自定义类型，表示一个简单的数字包装器
#[derive(Debug, Clone)]
struct Number(i32);

// 为 Number 实现 PartialEq，允许与 i32 比较
impl PartialEq<i32> for Number {
    fn eq(&self, other: &i32) -> bool {
        self.0 == *other
    }
}

// 为 Number 实现 PartialEq，允许 Number 与 Number 比较
impl PartialEq for Number {
    fn eq(&self, other: &Self) -> bool {
        self.0 == other.0
    }
}

fn main() {
    // 创建 Vec<Number>
    let vec_num = vec![Number(1), Number(2), Number(3)];
    
    // 创建数组 [i32; 3]
    let arr_i32 = [1, 2, 3];
    
    // 创建切片 &[i32]
    let slice_i32 = &[1, 2, 3];
    
    // 创建 Vec<i32>
    let vec_i32 = vec![1, 2, 3];
    
    // 比较 Vec<Number> 与 [i32; 3]
    assert_eq!(vec_num, arr_i32); // 有效，因为 Number: PartialEq<i32>
    
    // 比较 Vec<Number> 与 &[i32]
    assert_eq!(vec_num, slice_i32); // 有效，因为 Number: PartialEq<i32>
    
    // 比较 Vec<Number> 与 Vec<i32>
    assert_eq!(vec_num, vec_i32); // 有效，因为 Number: PartialEq<i32>
    
    // 比较两个 Vec<Number>
    let vec_num2 = vec![Number(1), Number(2), Number(3)];
    assert_eq!(vec_num, vec_num2); // 有效，因为 Number: PartialEq<Number>
    
    println!("All comparisons passed!");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_vec_comparisons() {
        let vec_num = vec![Number(10), Number(20)];
        let arr_i32 = [10, 20];
        let slice_i32 = &[10, 20];
        
        assert_eq!(vec_num, arr_i32);
        assert_eq!(vec_num, slice_i32);
        
        let vec_num2 = vec![Number(10), Number(20)];
        assert_eq!(vec_num, vec_num2);
    }
}
```

#### 示例解析
1. **自定义类型 `Number`**:
    - `Number` 是一个包装 `i32` 的结构体。
    - 实现了 `PartialEq<i32>`，允许 `Number` 与 `i32` 比较。
    - 实现了 `PartialEq<Number>`，允许 `Number` 与 `Number` 比较。

2. **比较演示**:
    - `Vec<Number>` 与 `[i32; N]` 比较：依赖 `Number: PartialEq<i32>` 和 `Vec<T>: PartialEq<[U; N]>`。
    - `Vec<Number>` 与 `&[i32]` 比较：依赖 `Number: PartialEq<i32>` 和 `Vec<T>: PartialEq<&[U]>`。
    - `Vec<Number>` 与 `Vec<i32>` 比较：依赖 `Number: PartialEq<i32>` 和 `Vec<T>: PartialEq<Vec<U>>`。
    - `Vec<Number>` 与 `Vec<Number>` 比较：依赖 `Number: PartialEq<Number>`。

3. **机制**:
    - 每次比较时，`Vec<Number>` 被转换为 `&[Number]`（通过 `as_slice()`）。
    - 目标类型（`[i32; N]`、`&[i32]` 或 `Vec<i32>`）被转换为切片或直接比较。
    - 切片比较逐元素调用 `Number::eq`（与 `i32` 或 `Number` 的实现）。

4. **输出**:
    - 运行 `main`，输出：`All comparisons passed!`
    - 运行 `cargo test`，所有测试通过。

### 3. 回到你的原始问题
在你的原始问题中，`assert_eq!(output, ["HELLO", ...])` 之所以有效，是因为：
- `output` 是 `Vec<String>`，被转换为 `&[String]`。
- `["HELLO", ...]` 是 `[&str; 4]`，被视为 `&[&str]`。
- `String: PartialEq<&str>`（标准库实现），允许逐元素比较。
- `Vec<String>: PartialEq<[&str; N]>`（通过 `Vec<T>: PartialEq<[U; N]>`，其中 `T = String`，`U = &str`）。

### 4. 源码深入分析
如果想深入了解，可以查看 Rust 标准库源码（`library/alloc/src/vec/mod.rs` 和 `library/core/src/slice/mod.rs`）：
- `Vec<T>` 的 `PartialEq` 实现依赖 `as_slice()`，将比较委托给切片。
- 切片的 `PartialEq` 实现（`[T]`) 逐元素比较，依赖 `T: PartialEq`。
- 标准库为 `String` 实现 `PartialEq<&str>`：
  ```rust
  impl PartialEq<str> for String {
      fn eq(&self, other: &str) -> bool {
          self.as_str() == other
      }
  }
  ```
  这允许 `String` 与 `&str` 比较，支撑了 `Vec<String>` 与 `[&str; N]` 的比较。

### 5. 总结
- `Vec<T>` 的 `PartialEq` 实现通过 `as_slice()` 将 `Vec` 转换为切片，然后依赖切片的 `PartialEq`。
- 支持与 `Vec<U>`、`&[U]`、`[U; N]` 比较，只要 `T: PartialEq<U>`。
- 切片比较检查长度并逐元素比较，依赖 `T` 的 `PartialEq`。
- 示例中的 `Number` 展示了自定义类型如何通过 `PartialEq` 支持 `Vec` 与数组/切片的比较，类似 `String` 与 `&str`。
- 你的原始问题中 `[&str; 4]` 有效，是因为 `String: PartialEq<&str>` 和 `Vec<String>: PartialEq<[&str; N]>`。

如果需要更深入的源码分析（比如切片比较的优化）或更复杂的示例，请告诉我！