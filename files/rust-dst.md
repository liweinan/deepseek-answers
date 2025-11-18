# Rust Type Classification: Copy/Non-Copy and DST/Non-DST

In Rust, data types can be classified along two dimensions: **Copy/Non-Copy** and **DST (Dynamic Sized Type)/Non-DST**. Here's the classification list and their relationships:

---

### **1. Copy Types vs Non-Copy Types**

#### **Copy Types**
- Implement the `Copy` trait, assignment or parameter passing performs automatic bitwise copy (implicit copy).
- Usually simple, fixed-size types.
- **Examples**:
    - All integer types: `i32`, `u8`, `usize`, etc.
    - All floating-point types: `f32`, `f64`.
    - Boolean type: `bool`.
    - Character type: `char`.
    - Immutable references: `&T` (but `&mut T` is not `Copy`).
    - Tuples or arrays composed of `Copy` types: `(i32, f64)`, `[u8; 4]`.

#### **Non-Copy Types**
- Do not implement the `Copy` trait, assignment or parameter passing uses move semantics by default.
- Usually involve heap memory, resource ownership, or mutability.
- **Examples**:
    - `String`, `Vec<T>` and other heap-allocated types.
    - Mutable references: `&mut T`.
    - Compound types containing `Non-Copy` types: `(String, Vec<u8>)`.

---

### **2. DST (Dynamic Sized Type) vs Non-DST**

#### **DST (Dynamic Sized Types)**
- Size is unknown at compile time, must be accessed indirectly through pointers (like `&`, `Box`).
- **Categories**:
    - **Slice types**: `[T]` (like `&[u8]`, `&str`).
    - **Trait objects**: `dyn Trait` (like `&dyn Debug`, `Box<dyn Error>`).
- **Characteristics**:
    - Cannot be used directly as function parameters or local variables (must be used through pointers).
    - May contain runtime length information (like slice length).

#### **Non-DST (Fixed Size Types)**
- Size is known at compile time, can be stored directly on the stack.
- **Examples**:
    - All basic types: `i32`, `f64`, `bool`.
    - Pointers or references: `&T`, `Box<T>` (the pointer itself is fixed-size, even when pointing to DST).
    - Fixed-length arrays: `[u8; 4]`.
    - Structs or tuples composed of `Non-DST` types: `struct S { x: i32 }`.

---

### **Relationships and Combinations**

| **Category**          | **Copy Types**               | **Non-Copy Types**           |
|-----------------------|-----------------------------|-----------------------------|
| **Non-DST**           | `i32`, `&T`, `(u8, bool)`   | `String`, `Vec<T>`, `&mut T` |
| **DST**               | None (DSTs usually don't implement `Copy`) | `[T]`, `dyn Trait`, `str`   |

#### **Key Points**
1. **Copy and DST are mutually exclusive**:
    - DSTs usually don't implement `Copy` (because copying requires knowing the size).
    - Exception: `&T` is `Copy`, but it's a fixed-size pointer to DST.
2. **Common combinations**:
    - `Non-DST + Copy`: Simple value types (like `i32`).
    - `Non-DST + Non-Copy`: Heap-allocated types (like `String`).
    - `DST + Non-Copy`: Dynamic types (like `[u8]`, `dyn Trait`).

---

### **Summary Table**

| Type Characteristics  | Examples                      | Can be stored on stack? | Supports implicit copy? |
|----------------------|------------------------------|------------------------|------------------------|
| `Non-DST + Copy`     | `i32`, `&T`, `(u8, bool)`    | Yes                    | Yes                    |
| `Non-DST + Non-Copy` | `String`, `Vec<T>`           | Yes                    | No                     |
| `DST + Non-Copy`     | `[T]`, `dyn Trait`, `str`    | No (needs pointer)     | No                     |

This classification helps better understand memory behavior and ownership rules in Rust.