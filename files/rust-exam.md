# Rust Programming Interview Questions with Answers

## Basic Level Questions

### 1. What is Rust's ownership system and why is it important?
**Answer:**  
Rust's ownership system is a set of rules that governs how memory is managed:
- Each value has a variable called its owner
- There can only be one owner at a time
- When the owner goes out of scope, the value is dropped

Importance:
- Prevents memory leaks
- Eliminates data races at compile time
- No need for garbage collection
- Enables thread safety without runtime overhead

### 2. Explain the difference between `String` and `&str` in Rust.
**Answer:**
- `String`: A growable, heap-allocated UTF-8 string (owned type)
- `&str`: A string slice (borrowed reference to string data)

Key differences:
- `String` is mutable while `&str` is immutable
- `String` owns its data, `&str` borrows it
- `String` can be modified (push, pop, etc.), `&str` cannot

### 3. What are Rust's traits and how do they compare to interfaces in other languages?
**Answer:**  
Traits define shared behavior across types (similar to interfaces):
- Define method signatures that implementing types must provide
- Can include default method implementations
- Support trait bounds for generic programming

Differences from traditional interfaces:
- Traits can be implemented for any type (even foreign types)
- Support associated types and constants
- Enable zero-cost abstractions

## Intermediate Level Questions

### 4. Explain the concept of lifetimes in Rust with an example.
**Answer:**  
Lifetimes ensure references are valid for as long as they're needed:

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

Key points:
- `'a` is a lifetime parameter
- Indicates returned reference lives at least as long as inputs
- Prevents dangling references

### 5. How does Rust handle concurrency safely?
**Answer:**  
Rust guarantees thread safety through:
1. Ownership system:
    - A value can only have one mutable reference at a time
    - Prevents data races at compile time
2. Type system:
    - `Send` trait marks types safe to transfer between threads
    - `Sync` trait marks types safe to share between threads
3. Standard library primitives:
    - `Mutex<T>`, `RwLock<T>` for shared mutable state
    - Channels (`std::sync::mpsc`) for message passing

### 6. What is the difference between `unwrap()`, `expect()`, and proper error handling in Rust?
**Answer:**
- `unwrap()`: Panics if Result/Option is Err/None (quick and dirty)
- `expect()`: Similar but allows custom panic message
- Proper error handling:
    - Pattern matching (`match` or `if let`)
    - `?` operator for error propagation
    - Combinators (`map`, `and_then`, etc.)

Example of proper handling:
```rust
fn read_file() -> Result<String, io::Error> {
    let mut file = File::open("file.txt")?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}
```

## Advanced Level Questions

### 7. Explain how Rust achieves zero-cost abstractions.
**Answer:**  
Zero-cost abstractions mean:
- Higher-level constructs compile to code as efficient as hand-written low-level code
- You pay only for what you use
- No runtime overhead for unused features

Implementation mechanisms:
- Monomorphization (compile-time generics)
- Inlining
- Ownership system enables optimizations impossible in GC languages
- Traits enable dynamic dispatch only when explicitly requested (`dyn Trait`)

### 8. How would you implement a custom smart pointer in Rust?
**Answer:**  
Example of a simple smart pointer:

```rust
use std::ops::Deref;

struct MyBox<T>(T);

impl<T> MyBox<T> {
    fn new(x: T) -> MyBox<T> {
        MyBox(x)
    }
}

impl<T> Deref for MyBox<T> {
    type Target = T;
    
    fn deref(&self) -> &T {
        &self.0
    }
}
```

Key traits to implement:
- `Deref` and `DerefMut` for dereferencing
- `Drop` for custom cleanup
- May implement `Borrow`, `AsRef` depending on use case

### 9. What are Rust's unsafe superpowers and when should they be used?
**Answer:**  
Unsafe Rust allows:
1. Dereferencing raw pointers
2. Calling unsafe functions
3. Accessing or modifying mutable static variables
4. Implementing unsafe traits

When to use:
- When you need to bypass compiler guarantees
- For FFI with other languages
- When you can prove safety but compiler can't verify
- Performance-critical code where invariants are manually verified

Always:
- Keep unsafe blocks as small as possible
- Document safety invariants
- Provide safe abstractions if exposing to other code

## Practical Coding Questions

### 10. Implement a thread-safe cache using Rust
**Answer:**  
Example implementation:

```rust
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

struct Cache<K, V> {
    store: Arc<RwLock<HashMap<K, V>>>,
}

impl<K, V> Cache<K, V>
where
    K: Eq + std::hash::Hash + Clone,
    V: Clone,
{
    pub fn new() -> Self {
        Cache {
            store: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn get(&self, key: &K) -> Option<V> {
        let store = self.store.read().unwrap();
        store.get(key).cloned()
    }

    pub fn set(&self, key: K, value: V) {
        let mut store = self.store.write().unwrap();
        store.insert(key, value);
    }
}
```

Key points:
- Uses `RwLock` for concurrent access
- `Arc` for shared ownership across threads
- Cloning values to avoid lifetime issues
- Proper error handling with `unwrap()` (production code would handle errors better)

### 11. Write a Rust macro that generates enum variants with associated values
**Answer:**  
Example macro:

```rust
macro_rules! enum_with_values {
    ($name:ident { $($variant:ident($type:ty)),* }) => {
        enum $name {
            $($variant($type)),*
        }
        
        impl $name {
            fn new(variant: &str, value: impl Into<String>) -> Option<Self> {
                match variant {
                    $(stringify!($variant) => Some(Self::$variant(value.into().parse::<$type>().ok()?)),)*
                    _ => None
                }
            }
        }
    };
}

// Usage:
enum_with_values! {
    MyEnum {
        IntValue(i32),
        FloatValue(f64),
        TextValue(String)
    }
}
```

### 12. Optimize this Rust code for performance
**Original:**
```rust
fn sum_of_squares(numbers: &[i32]) -> i32 {
    let mut sum = 0;
    for &n in numbers {
        sum += n * n;
    }
    sum
}
```

**Optimized:**
```rust
fn sum_of_squares(numbers: &[i32]) -> i32 {
    numbers.iter().map(|&n| n * n).sum()
}
```

Optimizations:
- Uses iterator combinators (can enable auto-vectorization)
- More concise and idiomatic
- Same performance in release mode due to LLVM optimizations
- Consider `fold` if additional operations needed during summation

## System Programming Questions

### 13. How would you implement a memory allocator in Rust?
**Answer:**  
Basic implementation steps:

1. Implement the `GlobalAlloc` trait:
```rust
use std::alloc::{GlobalAlloc, Layout};

struct MyAllocator;

unsafe impl GlobalAlloc for MyAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        // Allocation logic
    }
    
    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        // Deallocation logic
    }
}
```

2. Key considerations:
- Memory alignment (from `Layout`)
- Thread safety
- Fragmentation management
- Performance characteristics

3. Advanced techniques:
- Arena allocation
- Bump allocators
- Pool allocators
- Custom allocation strategies for specific patterns

### 14. Explain how Rust's async/await works under the hood
**Answer:**  
Async/await transformation:
1. `async fn` is rewritten as a state machine (generator)
2. `.await` points become state transition points
3. The Future trait defines the interface:
```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

Runtime components:
- Executor: Drives futures to completion
- Waker: Notifies executor when future can make progress
- Reactor: Handles I/O events and wakes tasks

Key advantages:
- Zero-cost abstraction (no implicit allocations)
- Cooperative multitasking
- Integrates with any executor (tokio, async-std, etc.)

## Evaluation Criteria

When assessing candidates:
1. **Ownership understanding** (30% weight)
    - Proper use of borrowing
    - Lifetime annotations
    - Move vs copy semantics

2. **Error handling** (20% weight)
    - Proper use of Result/Option
    - Error propagation
    - Match ergonomics

3. **Concurrency** (20% weight)
    - Thread safety awareness
    - Appropriate primitive selection
    - Sync/Send understanding

4. **Idiomatic code** (15% weight)
    - Trait usage
    - Iterator patterns
    - Macro usage

5. **Performance awareness** (15% weight)
    - Allocation patterns
    - Zero-cost abstractions
    - Optimization potential

This question set covers fundamental Rust concepts while allowing assessment of both theoretical knowledge and practical coding skills.