# 深拷贝与浅拷贝

## 概述

深拷贝和浅拷贝是编程中处理对象复制的两种方式，区别在于如何处理嵌套数据。

- **浅拷贝 (Shallow Copy)**：
  - 只复制对象的第一层数据。对于嵌套的对象或引用类型（如指针、对象、切片），仅复制引用，指向相同的内存。
  - 修改拷贝对象的嵌套数据会影响源对象，反之亦然。
  - 优点：内存占用低，速度快。
  - 缺点：数据耦合，可能导致意外修改。

- **深拷贝 (Deep Copy)**：
  - 递归复制对象的所有层级数据，包括嵌套对象，生成完全独立的副本。
  - 修改源对象或拷贝对象互不影响。
  - 优点：数据隔离，适合需要独立副本的场景。
  - 缺点：内存占用高，性能开销大。

以下为 Rust、Go、Java 和 JavaScript 的示例，展示浅拷贝和深拷贝的实现。每个示例使用相同的 `Person` 和 `Address` 结构，清晰对比两者的行为差异。

## Rust 示例

Rust 通过 `Clone` trait 实现深拷贝，浅拷贝通常通过引用（`&`）实现。以下示例展示 `Person` 对象的深拷贝和浅拷贝。

```rust
#[derive(Clone, Debug)]
struct Address {
    city: String,
}

#[derive(Clone, Debug)]
struct Person {
    name: String,
    address: Address,
}

fn main() {
    let addr = Address { city: String::from("New York") };
    let p1 = Person { name: String::from("Alice"), address: addr };

    // 深拷贝
    let p2 = p1.clone();
    println!("Before modification (deep copy):");
    println!("p1: {:?}", p1);
    println!("p2: {:?}", p2);
    let mut p2 = p2;
    p2.address.city = String::from("Boston");
    println!("After modifying p2.address.city:");
    println!("p1: {:?}", p1); // 不受影响
    println!("p2: {:?}", p2);

    // 浅拷贝：引用
    let p3 = &p1;
    println!("\nBefore modification (shallow copy):");
    println!("p1: {:?}", p1);
    println!("p3: {:?}", p3);
}
```

**说明**：
- **深拷贝**：`p1.clone()` 递归复制所有字段，`p2` 是独立副本，修改 `p2.address.city` 不影响 `p1`。
- **浅拷贝**：`p3` 是 `p1` 的引用，只借用数据，无法直接修改。
- **输出**：
  ```
  Before modification (deep copy):
  p1: Person { name: "Alice", address: Address { city: "New York" } }
  p2: Person { name: "Alice", address: Address { city: "New York" } }
  After modifying p2.address.city:
  p1: Person { name: "Alice", address: Address { city: "New York" } }
  p2: Person { name: "Alice", address: Address { city: "Boston" } }

  Before modification (shallow copy):
  p1: Person { name: "Alice", address: Address { city: "New York" } }
  p3: Person { name: "Alice", address: Address { city: "New York" } }
  ```

## Go 示例

Go 中结构体赋值默认是深拷贝，但如果结构体包含指针或引用类型（如切片），赋值只复制引用，表现出浅拷贝行为。以下示例通过指针展示浅拷贝。

```go
package main

import (
    "encoding/json"
    "fmt"
)

type Address struct {
    City *string // 指针类型
}

type Person struct {
    Name    string
    Address Address
}

func (p Person) DeepCopy() Person {
    var result Person
    bytes, _ := json.Marshal(p)
    json.Unmarshal(bytes, &result)
    return result
}

func main() {
    city := "New York"
    p1 := Person{
        Name: "Alice",
        Address: Address{City: &city},
    }

    // 浅拷贝：直接赋值（复制指针）
    p2 := p1
    fmt.Println("Before modification (shallow copy):")
    fmt.Printf("p1: {Name: %s, Address: {City: %s}}\n", p1.Name, *p1.Address.City)
    fmt.Printf("p2: {Name: %s, Address: {City: %s}}\n", p2.Name, *p2.Address.City)
    *p2.Address.City = "Boston"
    fmt.Println("After modifying *p2.Address.City:")
    fmt.Printf("p1: {Name: %s, Address: {City: %s}}\n", p1.Name, *p1.Address.City) // 受影响
    fmt.Printf("p2: {Name: %s, Address: {City: %s}}\n", p2.Name, *p2.Address.City)

    // 深拷贝
    p3 := p1.DeepCopy()
    fmt.Println("\nBefore modification (deep copy):")
    fmt.Printf("p1: {Name: %s, Address: {City: %s}}\n", p1.Name, *p1.Address.City)
    fmt.Printf("p3: {Name: %s, Address: {City: %s}}\n", p3.Name, *p3.Address.City)
    *p3.Address.City = "Chicago"
    fmt.Println("After modifying *p3.Address.City:")
    fmt.Printf("p1: {Name: %s, Address: {City: %s}}\n", p1.Name, *p1.Address.City) // 不受影响
    fmt.Printf("p3: {Name: %s, Address: {City: %s}}\n", p3.Name, *p3.Address.City)
}
```

**说明**：
- **浅拷贝**：`p2 := p1` 复制 `City` 指针，`p1.Address.City` 和 `p2.Address.City` 指向同一字符串，修改 `*p2.Address.City` 影响 `p1`。
- **深拷贝**：JSON 序列化生成独立副本，`p3.Address.City` 指向新字符串，修改 `*p3.Address.City` 不影响 `p1`。
- **输出**：
  ```
  Before modification (shallow copy):
  p1: {Name: Alice, Address: {City: New York}}
  p2: {Name: Alice, Address: {City: New York}}
  After modifying *p2.Address.City:
  p1: {Name: Alice, Address: {City: Boston}}
  p2: {Name: Alice, Address: {City: Boston}}

  Before modification (deep copy):
  p1: {Name: Alice, Address: {City: Boston}}
  p3: {Name: Alice, Address: {City: Boston}}
  After modifying *p3.Address.City:
  p1: {Name: Alice, Address: {City: Boston}}
  p3: {Name: Alice, Address: {City: Chicago}}
  ```

## Java 示例

Java 默认通过引用赋值实现浅拷贝，深拷贝需手动递归克隆。以下示例使用 `clone()` 展示浅拷贝和深拷贝。

```java
class Address implements Cloneable {
    String city;

    public Address(String city) {
        this.city = city;
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }

    @Override
    public String toString() {
        return "Address{city='" + city + "'}";
    }
}

class Person implements Cloneable {
    String name;
    Address address;

    public Person(String name, Address address) {
        this.name = name;
        this.address = address;
    }

    // 浅拷贝
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }

    // 深拷贝
    public Person deepCopy() throws CloneNotSupportedException {
        Person cloned = (Person) super.clone();
        cloned.address = (Address) address.clone();
        return cloned;
    }

    @Override
    public String toString() {
        return "Person{name='" + name + "', address=" + address + "}";
    }
}

public class CopyExample {
    public static void main(String[] args) throws CloneNotSupportedException {
        Address address = new Address("New York");
        Person p1 = new Person("Alice", address);

        // 浅拷贝
        Person p2 = (Person) p1.clone();
        System.out.println("Before modification (shallow copy):");
        System.out.println("p1: " + p1);
        System.out.println("p2: " + p2);
        p2.address.city = "Boston";
        System.out.println("After modifying p2.address.city:");
        System.out.println("p1: " + p1); // 受影响
        System.out.println("p2: " + p2);

        // 深拷贝
        Person p3 = p1.deepCopy();
        System.out.println("\nBefore modification (deep copy):");
        System.out.println("p1: " + p1);
        System.out.println("p3: " + p3);
        p3.address.city = "Chicago";
        System.out.println("After modifying p3.address.city:");
        System.out.println("p1: " + p1); // 不受影响
        System.out.println("p3: " + p3);
    }
}
```

**说明**：
- **浅拷贝**：`clone()` 只复制引用，`p2.address` 和 `p1.address` 指向同一对象，修改 `p2.address.city` 影响 `p1`。
- **深拷贝**：`deepCopy` 递归克隆 `address`，`p3.address` 是独立对象，修改 `p3.address.city` 不影响 `p1`。
- **输出**：
  ```
  Before modification (shallow copy):
  p1: Person{name='Alice', address=Address{city='New York'}}
  p2: Person{name='Alice', address=Address{city='New York'}}
  After modifying p2.address.city:
  p1: Person{name='Alice', address=Address{city='Boston'}}
  p2: Person{name='Alice', address=Address{city='Boston'}}

  Before modification (deep copy):
  p1: Person{name='Alice', address=Address{city='Boston'}}
  p3: Person{name='Alice', address=Address{city='Boston'}}
  After modifying p3.address.city:
  p1: Person{name='Alice', address=Address{city='Boston'}}
  p3: Person{name='Alice', address=Address{city='Chicago'}}
  ```

## JavaScript 示例

JavaScript 对象赋值默认是浅拷贝，深拷贝需使用特定方法，如 JSON 序列化。

```javascript
const p1 = {
    name: "Alice",
    address: { city: "New York" }
};

// 浅拷贝
const p2 = { ...p1 };
console.log("Before modification (shallow copy):");
console.log("p1:", p1);
console.log("p2:", p2);
p2.address.city = "Boston";
console.log("After modifying p2.address.city:");
console.log("p1:", p1); // 受影响
console.log("p2:", p2);

// 深拷贝
const p3 = JSON.parse(JSON.stringify(p1));
console.log("\nBefore modification (deep copy):");
console.log("p1:", p1);
console.log("p3:", p3);
p3.address.city = "Chicago";
console.log("After modifying p3.address.city:");
console.log("p1:", p1); // 不受影响
console.log("p3:", p3);
```

**说明**：
- **浅拷贝**：展开运算符（`...`）只复制第一层，`p2.address` 和 `p1.address` 指向同一对象，修改 `p2.address.city` 影响 `p1`。
- **深拷贝**：`JSON.parse(JSON.stringify(p1))` 创建独立副本，修改 `p3.address.city` 不影响 `p1`。
- **输出**：
  ```
  Before modification (shallow copy):
  p1: { name: 'Alice', address: { city: 'New York' } }
  p2: { name: 'Alice', address: { city: 'New York' } }
  After modifying p2.address.city:
  p1: { name: 'Alice', address: { city: 'Boston' } }
  p2: { name: 'Alice', address: { city: 'Boston' } }

  Before modification (deep copy):
  p1: { name: 'Alice', address: { city: 'Boston' } }
  p3: { name: 'Alice', address: { city: 'Boston' } }
  After modifying p3.address.city:
  p1: { name: 'Alice', address: { city: 'Boston' } }
  p3: { name: 'Alice', address: { city: 'Chicago' } }
  ```

## 总结

| 语言       | 深拷贝实现                     | 浅拷贝实现                     | 特点与注意事项                        |
|------------|--------------------------------|--------------------------------|--------------------------------------|
| Rust       | `Clone` trait                 | 引用（`&`）                   | 默认深拷贝，引用实现浅拷贝，内存安全  |
| Go         | JSON 序列化或手动             | 赋值（含指针/切片）           | 结构体默认深拷贝，指针导致浅拷贝      |
| Java       | 递归克隆（`deepCopy`）        | `clone()`                     | 浅拷贝只复制引用，深拷贝需手动递归    |
| JavaScript | `JSON.parse/stringify`        | `...` 或 `Object.assign()`    | JSON 方法简单但不适用复杂对象        |

这些示例通过一致的 `Person` 和 `Address` 结构，清晰展示了浅拷贝的共享引用问题和深拷贝的隔离特性。选择拷贝方式时，需根据性能和数据隔离需求权衡。

