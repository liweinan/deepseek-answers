# 在 Rust 中，问号操作符 `?` 是非常重要的语法糖，主要用于**错误处理**的简洁写法。它可以让错误处理代码从“层层嵌套的 match”或“层层 unwrap”变成几乎像写正常逻辑一样流畅。

### 1. 基本作用：快速传播错误

`?` 的核心作用是：  
**如果值是 Ok(T) 或 Some(T)，就把里面的 T 取出来继续使用；  
如果值是 Err(e) 或 None，就直接 return 这个错误，不继续执行当前函数剩下的代码。**

```rust
use std::fs::File;
use std::io::Read;

fn read_file_content(path: &str) -> Result<String, std::io::Error> {
    let mut file = File::open(path)?;    // 如果打开失败，直接返回 Err
    let mut contents = String::new();
    file.read_to_string(&mut contents)?; // 如果读取失败，也直接返回 Err
    Ok(contents)                         // 只有都成功了才返回 Ok(String)
}
```

等价于下面这种又臭又臭又长的写法：

```rust
let mut file = match File::open(path) {
    Ok(f) => f,
    Err(e) => return Err(e),
};
let mut contents = String::new();
match file.read_to_string(&mut contents) {
    Ok(_) => {},
    Err(e) => return Err(e),
};
Ok(contents)
```

所以 `?` 能让你把错误处理压缩成一行，极大提升代码可读性。

### 2. 能在哪些类型上使用 `?`

`?` 只能用在实现了 `std::ops::Try` trait 的类型上，常见的有：

| 类型          | 能用 ? 吗 | 成功时取出 | 失败时返回        |
|---------------|-----------|------------|-------------------|
| `Result<T, E>`| 是        | `Ok(t)` → t| `Err(e)` → return Err(e) |
| `Option<T>`   | 是（Rust 1.13+） | `Some(t)` → t | `None` → return None |
| 自定义类型    | 可以      | 只要实现 Try trait 即可 |

### 3. Option 上的 ? 用法（和 Result 类似）

```rust
fn find_user_age(name: &str) -> Option<u32> {
    let user = get_user(name)?;        // 如果找不到用户，直接返回 None
    let profile = user.profile()?;     // 如果没有 profile，也返回 None
    Some(profile.age)
}
```

### 4. 不同错误类型之间的转换（常用）

很多时候函数返回 `Result<T, Box<dyn std::error::Error>>` 或自己的错误类型，但库函数返回的是具体错误，这时需要转换：

```rust
// 方法1：用 .map_err() 转换错误类型
fn do_something() -> Result<String, Box<dyn std::error::Error>> {
    let mut file = File::open("config.toml").map_err(|e| Box::new(e))?;
    // 或者更简洁（Rust 2018+ 支持直接 ?）
    Ok(contents)
}

// 方法2：直接用 ?（推荐写法，Rust 1.0 起支持 From trait 自动转换）
use std::fs::File;
use std::io;

#[derive(Debug)]
struct MyError {
    details: String,
}

// 实现 From 把 io::Error 自动转成 MyError
impl From<io::Error> for MyError {
    fn from(err: io::Error) -> Self {
        MyError { details: err.to_string() }
    }
}

fn read_config() -> Result<String, MyError> {
    let mut file = File::open("config.toml")?;  // 自动调用 From<io::Error>
    let mut s = String::new();
    file.read_to_string(&mut s)?;
    Ok(s)
}
```

只要目标错误类型实现了 `From<源错误类型>`，就可以直接用 `?` 自动转换。

### 5. 常见的库提供的快捷工具

- `anyhow`（应用开发最常用）：返回 `anyhow::Result<T>`，几乎所有错误都能直接 `?`
  ```rust
  use anyhow::Context;
  
  let content = std::fs::read_to_string("config.toml")
      .with_context(|| "无法读取配置文件")?;
  ```

- `thiserror`：方便定义自己的错误类型并自动实现 From

### 总结：问号 `?` 在 Rust 中的核心价值

| 场景               | 不用 ? 的写法         | 用 ? 的写法               | 效果                  |
|--------------------|-----------------------|---------------------------|-----------------------|
| 正常流程           | 层层 match / unwrap   | 直接写正常逻辑            | 代码极简洁            |
| 出错时             | 手动 return Err(e)    | 自动 return               | 不用关心错误传播路径  |
| 不同错误类型       | 手动 map_err          | 实现 From 后直接 ?        | 类型安全又方便        |
| Option 处理        | match Some/None       | 直接 ?                    | 和 Result 统一风格    |

掌握了 `?` 操作符，你写 Rust 的错误处理代码就会从“痛苦”变成“优雅”，这也是 Rust 错误处理被很多人称赞的核心原因之一。

Rust 里 **没有** `a?.some_ops()` 这种“空值安全调用”语法！  
这是很多从 JavaScript / TypeScript / Kotlin / Swift / C# 过来的人最大的误解点。

Rust 的 `?` 和 JS 的 `?.` 是完全不同的东西：

| 语言       | 语法            | 含义                              | 是否有“可选链” |
|------------|-----------------|-----------------------------------|----------------|
| JavaScript | `?.`            | 可选链（Optional Chaining）       | 有             |
| Rust       | `?`（单独一个） | 错误/None 传播操作符（Try）       | 没有           |

Rust 完全没有实现类似 `obj?.method()?.another()` 的可选链语法（截至 2025 年 11 月也没有）。

### 那 Rust 中怎么解决“None 后续调用”的问题？

Rust 社区提供了好几种非常地道且比可选链还好用的写法，常见有 6 种：

#### 1. 用 `if let` / while let`（最直观）
```rust
if let Some(user) = get_user() {
    println!("Hello {}", user.name.to_uppercase());
}
```

#### 2. 用 `and_then`（函数式链式，类似可选链的感觉）
```rust
let age = get_user()
    .and_then(|u| u.profile)
    .and_then(|p| p.age)
    .unwrap_or(0);

println!("年龄: {}", age);
```

#### 3. 用 `map` + `unwrap_or` / `unwrap_or_else`
```rust
let name_upper = get_user()
    .map(|u| u.name.to_uppercase())
    .unwrap_or_else(|| "匿名".to_string());
```

#### 4. 最接近“可选链”写法的宏：`option_expect!` 或第三方库（推荐）
最流行的就是社区写的几个宏，写出来几乎和 JS 一模一样：

```rust
// 使用 tryopt! 宏（https://crates.io/crates/tryopt）
use tryopt::tryopt;

let age = tryopt![get_user()?.profile?.age];
```

或者更强大的 `maybe` 宏：

```rust
use maybe::maybe;

let name = maybe! {
    user   = get_user() => user,
    profile = user.profile => profile,
    name   = profile.name => name,
    => "默认值".to_string()
};
```

#### 5. 用 `?` 在自定义函数里提前返回 None（最 Rust 风格）
```rust
fn get_user_age(id: i32) -> Option<u32> {
    let user = get_user(id)?;           // None 就直接返回 None
    let profile = user.profile()?;      // 同样
    Some(profile.age)                   // 只有全都有才到这里
}
```

这其实这才是 Rust 推荐的做法：把“可能失败”的操作封装成返回 `Option` 的函数，用 `?` 传播 None。

#### 6. 自己写一个小宏（很多人项目里都这么干）
```rust
macro_rules! opt_chain {
    ($e:expr) => { $($rest:tt)* } => {
        if let Some(x) = $e {
            opt_chain!(x $($rest)*)
        } else {
            return None;
        }
    };
    ($e:expr) => { $e };
}

fn get_age() -> Option<u32> {
    let age = opt_chain!(get_user()?.profile?.age);
    Some(age)
}
```

### 总结对比表

| 需求                         | JavaScript 写法               | Rust 最地道写法                                |
|------------------------------|-------------------------------|------------------------------------------------|
| 取值或默认                   | `user?.name ?? "匿名"`         | `get_user().map(|u| &u.name).unwrap_or("匿名")` |
| 连续取嵌套字段               | `user?.profile?.age`          | `get_user().and_then(|u| u.profile).and_then(|p| p.age)` |
| 连续取字段并处理           | `user?.profile?.age?.toString()` | `get_user()?.profile?.age.map(|a| a.to_string())` |
| 最像可选链的写法             | 原生支持                      | 使用 `tryopt!`、`maybe!` 等第三方宏             |

所以：Rust 没有 `?.` 可选链，但用 `Option` + `?` + `and_then`/`map` 的组合，实际上比很多语言的可选链还强大、还安全、还零成本。

你现在看到的很多 Rust 老手的代码里，基本看不到 `unwrap()` 乱飞，就是因为他们全用 `?` + `and_then` 把“None 传播”写得又短又安全。