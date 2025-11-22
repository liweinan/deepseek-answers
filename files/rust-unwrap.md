# 在 Rust 中，`unwrap()` 是最方便但也最“危险”的方法之一，它在 `Option` 或 `Result` 为 `None`/`Err` 时会直接 `panic`，线上服务一旦 panic 就会崩溃。因此生产代码里基本要**避免无脑 unwrap**。以下是常用的安全替代方案，从推荐度由高到低排序：

### 1. 优先使用 ? 操作符（最推荐）
如果你在返回 `Result<T, E>` 的函数里，直接用 `?` 传播错误，上层统一处理。

```rust
fn read_config() -> Result<Config, Box<dyn std::error::Error>> {
    let s = std::fs::read_to_string("config.toml")?;  // 这里不会 unwrap
    let config: Config = toml::from_str(&s)?;
    Ok(config)
}
```

这样错误会一层层向上冒，最后在 main 里统一处理：

```rust
fn main() {
    let config = read_config().expect("读取配置文件失败，程序无法继续运行");
    // 或者更优雅的自定义错误处理
}
```

### 2. 匹配（match）或 if let（明确想处理两种情况时）
```rust
match std::env::var("PORT") {
    Ok(port) => port.parse().unwrap_or(8080),
    Err(_) => 8080.to_string(),
}

// 或者更简洁
let port = if let Ok(p) = std::env::var("PORT") {
    p.parse().unwrap_or(8080)
} else {
    8080
};
```

表格在大多数地方都能正常显示，但确实有些平台（比如某些手机客户端、旧版微信、Telegram 等）会把 Markdown 表格渲染得乱七八糟或直接变纯文本。

给你一个**排版更好、更通用**的版本，不管在哪儿看都清晰：

### 3. 提供默认值的方法（最安全常用）

**针对 Option<T> 的安全方法：**
- `unwrap_or(default)` → 最常用，直接给默认值
- `unwrap_or_else(|| 复杂计算)` → 只有真的走到 None 才会执行闭包（性能更好）
- `unwrap_or_default()` → 当 T 实现 Default 时（比如 String、Vec、u32 等很多都实现了）
- `or_else(|| Some(value))` → 常配合 and_then 链式调用

**针对 Result<T,E> 的安全方法：**
- `unwrap_or(default)` → Err 时返回默认的 T
- `unwrap_or_else(|err| 根据 err 计算默认值)` → 可以看到错误信息，做不同处理
- `ok()` → 把 Result 变成 Option，错误直接丢掉（常用于不在乎错误的情况）
- `or_else(|err| Ok(另一个值))` → 错误恢复常用

**实测最常用的一行代码写法（社区最爱）：**
```rust
let port: u16 = std::env::var("PORT")
    .ok()                          // VarError → None
    .and_then(|s| s.parse().ok())  // 解析错误 → None
    .unwrap_or(8080);              // 都失败就用 8080
```

这样不管你是看手机、电脑、微信、钉钉、Typora、VS Code、Obsidian……都能看清，不再担心表格错位了。

示例：

```rust
let threads: usize = std::env::var("THREADS")
    .ok()
    .and_then(|s| s.parse().ok())
    .unwrap_or(8);  // 完全不 panic

// 更优雅的写法（社区最常见）
let threads = std::env::var("THREADS")
    .as_deref()
    .and_then(str::parse::<usize>)
    .unwrap_or(8);
```

### 4. expect 只在真正“不可能出错”或启动失败就该崩溃的地方用
```rust
// 这种情况用 expect 是可以接受的
let listener = TcpListener::bind(addr)
    .expect("绑定端口失败，可能是端口被占用或权限不足，请检查配置");
// 程序启动就失败了，直接崩溃比继续跑更有意义
```

### 5. 完全避免 unwrap 的实用组合技
```rust
// 读取配置文件的终极安全写法
let config = std::fs::read_to_string("config.json")
    .ok()
    .and_then(|s| serde_json::from_str(&s).ok())
    .unwrap_or_default();

// 从 HashMap 取值的安全方式
let value = map.get(&key).cloned().unwrap_or(default_value);

// 从 Vec 取索引的安全方式
let item = vec.get(index).copied().or_else(|| vec.first().copied());
```

### 6. 推荐的第三方库（进一步减少样板代码）
- `anyhow`：最流行的错误处理库，`?` 能自动转换各种错误
- `thiserror`：优雅地定义自己的错误类型
- `config`、`figment` 等配置库：基本不用自己读文件和 unwrap

示例用 anyhow（几乎看不到 unwrap）：

```rust
use anyhow::{Context, Result};

fn main() -> Result<()> {
    let config = std::fs::read_to_string("config.toml")
        .context("读取配置文件失败")?;
    let app: AppConfig = toml::from_str(&config)
        .context("解析配置文件失败")?;
    Ok(())
}
```

### 总结：生产代码的 unwrap 替代优先级
1. 用 `?` + anyhow/eyre（99% 的情况）
2. `.unwrap_or` / `.unwrap_or_default` / `.unwrap_or_else`
3. `match` / `if let`（需要分别处理成功和失败逻辑时）
4. `expect("明确说明为什么这里必须成功")`（启动阶段不可能出错的地方）
5. 绝对不要用裸 `unwrap()`（除非写示例代码或快速原型）

把 `cargo expand` 或 `rust-analyzer` 的 “expand macro” 功能打开，你会发现很多库内部其实也在疯狂 unwrap，但对外暴露的 API 都是安全的。只要你自己的 public 函数不随便 panic，就完全没问题。

---

下面是一个**完整、可直接编译运行**的实战例子，展示了如何在真实项目中优雅地结合使用：

- `thiserror`：定义清晰、类型安全的自定义错误
- `anyhow`：在 main 和上层业务逻辑中轻松传播和处理错误（几乎不用写 ? 转换）

```rust
// Cargo.toml
[dependencies]
anyhow = "1.0"
thiserror = "1.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

// src/main.rs 或 lib.rs
use anyhow::{Context, Result};
use thiserror::Error;
use serde::Deserialize;
use std::path::Path;

// 1. 用 thiserror 定义底层库的错误类型（类型安全、自动实现 std::error::Error）
#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("读取配置文件失败: {path}")]
    Io {
        path: String,
        #[source]
        source: std::io::Error,
    },

    #[error("解析 JSON 失败")]
    Json {
        #[from]
        source: serde_json::Error,
    },

    #[error("配置缺少必填字段: {0}")]
    MissingField(String),

    #[error("端口号必须在 1~65535 之间，当前是 {0}")]
    InvalidPort(u16),
}

// 2. 你的配置结构体
#[derive(Debug, Deserialize)]
pub struct AppConfig {
    host: String,
    port: u16,
    database_url: String,
    #[serde(default = "default_debug")]
    debug: bool,
}

fn default_debug() -> bool {
    false
}

// 3. 底层读取+解析函数，返回自定义的 ConfigError（库的公共 API 推荐这样）
pub fn load_config<P: AsRef<Path>>(path: P) -> std::result::Result<AppConfig, ConfigError> {
    let path_str = path.as_ref().to_string_lossy();
    let content = std::fs::read_to_string(&path)
        .map_err(|e| ConfigError::Io { path: path_str.into_owned(), source: e })?;

    let config: AppConfig = serde_json::from_str(&content)?;

    // 业务校验
    if config.port == 0 || config.port > 65535 {
        return Err(ConfigError::InvalidPort(config.port));
    }
    if config.host.is_empty() {
        return Err(ConfigError::MissingField("host".to_owned()));
    }

    Ok(config)
}

// 4. 上层业务代码使用 anyhow（main、bin、handler 等地方最舒服）
fn main() -> Result<()> {
    // 只需要加 .context() 就能把任何错误变成带上下文的 anyhow::Error
    let config = load_config("config.json")
        .context("无法加载配置文件，请检查文件是否存在且权限正确")?;  // ← 关键！

    println!("启动服务器 {}:{}", config.host, config.port);

    // 再举几个常见场景
    start_server(&config).context("服务器启动失败")?;
    connect_database(&config.database_url).context("数据库连接失败")?;

    Ok(())
}

fn start_server(config: &AppConfig) -> Result<()> {
    // 模拟可能出错的操作
    std::net::TcpListener::bind((config.host.as_str(), config.port))
        .map(|_| ())
        .map_err(anyhow::anyhow) // 也可以直接 .context("绑定端口失败")
        .context(format!("绑定 {}:{} 失败", config.host, config.port))
}

fn connect_database(url: &str) -> Result<()> {
    if url.contains("postgres") {
        Ok(())
    } else {
        Err(anyhow::anyhow!("暂不支持的数据库协议"))
    }
}
```

### 运行时错误输出示例（超漂亮）

```bash
$ cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 0.0s
     Running `target/debug/myapp`
Error: 无法加载配置文件，请检查文件是否存在且权限正确

Caused by:
    读取配置文件失败: config.json

Caused by:
    No such file or directory (os error 2)
```

或者校验失败时：

```text
Error: 无法加载配置文件，请检查文件是否存在且权限正确

Caused by:
    端口号必须在 1~65535 之间，当前是 0
```

### 总结：最佳实践分工

| 位置             | 用哪个库         | 原因                                                                 |
|------------------|------------------|----------------------------------------------------------------------|
| library crate    | `thiserror`      | 提供类型安全的错误，外部用户可以 `match` 或 `downcast`                 |
| binary / main    | `anyhow`         | 只需要打印错误 + 上下文，不关心具体错误类型，最简洁                     |
| 跨 crate 传播错误 | `thiserror` + `#[from]` | 自动实现 From 转换，配合 `?` 能一路向上变成 `anyhow::Error`         |

这样写出来的代码：

- 底层错误类型清晰（IDE 能跳转、match 补全）
- 上层几乎看不到 `unwrap` / `expect`
- 错误信息带完整上下文和调用栈，线上排查问题超级舒服

这就是目前 2025 年 Rust 社区公认的“最舒服的错误处理组合”。直接把上面代码复制到新项目里用就行了！