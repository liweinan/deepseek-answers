# ### 深拷贝与浅拷贝的区别

- **浅拷贝 (Shallow Copy)**：
    - 只复制对象的第一层数据。对于嵌套的对象或引用类型，复制的只是引用（指针），而不是实际的数据。
    - 源对象和拷贝对象的嵌套引用指向同一块内存，修改其中一个会影响另一个。
    - 优点：节省内存，速度快。
    - 缺点：可能导致意外的副作用。

- **深拷贝 (Deep Copy)**：
    - 递归复制对象的所有层级数据，包括嵌套对象或引用类型，生成完全独立的新对象。
    - 源对象和拷贝对象互不影响，修改任一方不会影响另一方。
    - 优点：数据隔离，适合需要独立副本的场景。
    - 缺点：内存占用大，性能开销高。

---

### Rust 示例

Rust 强调内存安全，默认行为倾向于深拷贝（通过 `Clone` 实现），但可以手动实现浅拷贝。

```rust
// 深拷贝
#[derive(Clone, Debug)]
struct Person {
    name: String,
    address: Address,
}

#[derive(Clone, Debug)]
struct Address {
    city: String,
}

fn main() {
    let addr = Address { city: String::from("New York") };
    let p1 = Person { name: String::from("Alice"), address: addr };
    
    // 深拷贝：p2 和 p1 完全独立
    let p2 = p1.clone();
    
    println!("p1: {:?}", p1);
    println!("p2: {:?}", p2);
}

// 浅拷贝（通过引用实现）
fn shallow_copy() {
    let addr = Address { city: String::from("New York") };
    let p1 = Person { name: String::from("Alice"), address: addr };
    
    // 浅拷贝：仅复制引用
    let p2 = &p1;
    
    println!("p1: {:?}", p1);
    println!("p2: {:?}", p2);
}
```

- **深拷贝**：通过 `Clone` trait 实现，递归复制所有字段。
- **浅拷贝**：通过引用（`&`）实现，p2 只是 p1 的借用。

---

### Go 示例

Go 没有内置的深拷贝机制，深拷贝通常需要手动实现。结构体赋值默认是深拷贝，但包含指针或切片时可能导致部分浅拷贝。

```go
package main

import (
    "encoding/json"
    "fmt"
)

// 深拷贝
type Address struct {
    City string
}

type Person struct {
    Name    string
    Address Address
}

func main() {
    p1 := Person{Name: "Alice", Address: Address{City: "New York"}}
    
    // 深拷贝：通过序列化和反序列化实现
    var p2 Person
    bytes, _ := json.Marshal(p1)
    json.Unmarshal(bytes, &p2)
    
    p2.Address.City = "Boston"
    fmt.Printf("p1: %+v\n", p1) // p1 不受影响
    fmt.Printf("p2: %+v\n", p2)
    
    // 浅拷贝：直接赋值（注意：Go 结构体默认深拷贝，但指针或切片需要注意）
    p3 := p1
    p3.Address.City = "Chicago"
    fmt.Printf("p1: %+v\n", p1) // p1 受影响，因为 Address 是值类型
    fmt.Printf("p3: %+v\n", p3)
}
```

- **深拷贝**：通过 `json.Marshal/Unmarshal` 实现，生成独立副本。
- **浅拷贝**：Go 结构体赋值默认深拷贝，但如果结构体包含指针或切片，可能导致浅拷贝行为。

---

### Java 示例

Java 的对象默认通过引用赋值（浅拷贝），深拷贝需要手动实现。

```java
import java.io.*;

// 深拷贝
class Address implements Cloneable, Serializable {
    String city;

    public Address(String city) {
        this.city = city;
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}

class Person implements Cloneable, Serializable {
    String name;
    Address address;

    public Person(String name, Address address) {
        this.name = name;
        this.address = address;
    }

    // 深拷贝：通过序列化实现
    public Person deepCopy() throws IOException, ClassNotFoundException {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bos);
        oos.writeObject(this);

        ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
        ObjectInputStream ois = new ObjectInputStream(bis);
        return (Person) ois.readObject();
    }

    // 浅拷贝
    @Override
    protected Object clone() throws CloneNotSupportedException {
        Person cloned = (Person) super.clone();
        cloned.address = (Address) address.clone(); // 需要手动克隆嵌套对象
        return cloned;
    }
}

public class Main {
    public static void main(String[] args) throws Exception {
        Address addr = new Address("New York");
        Person p1 = new Person("Alice", addr);

        // 浅拷贝
        Person p2 = (Person) p1.clone();
        p2.address.city = "Boston";
        System.out.println("p1: " + p1.address.city); // 受影响
        System.out.println("p2: " + p2.address.city);

        // 深拷贝
        Person p3 = p1.deepCopy();
        p3.address.city = "Chicago";
        System.out.println("p1: " + p1.address.city); // 不受影响
        System.out.println("p3: " + p3.address.city);
    }
}
```

- **深拷贝**：通过序列化实现，生成完全独立的对象。
- **浅拷贝**：通过 `clone()` 方法实现，但需要手动克隆嵌套对象。

---

### JavaScript 示例

JavaScript 的对象赋值默认是浅拷贝，深拷贝需要使用特定方法。

```javascript
// 浅拷贝
const p1 = {
    name: "Alice",
    address: { city: "New York" }
};

const p2 = { ...p1 }; // 浅拷贝
p2.address.city = "Boston";

console.log(p1.address.city); // Boston（受影响）
console.log(p2.address.city); // Boston

// 深拷贝
const p3 = JSON.parse(JSON.stringify(p1)); // 深拷贝
p3.address.city = "Chicago";

console.log(p1.address.city); // Boston（不受影响）
console.log(p3.address.city); // Chicago
```

- **深拷贝**：通过 `JSON.parse(JSON.stringify())` 实现，但不适用于函数或特殊对象。
- **浅拷贝**：通过展开运算符（`...`）或 `Object.assign()` 实现，仅复制第一层。

---

### 总结

| 语言   | 深拷贝实现                     | 浅拷贝实现                     | 注意事项                              |
|--------|--------------------------------|--------------------------------|--------------------------------------|
| Rust   | `Clone` trait                 | 引用（`&`）                   | 强调内存安全，默认倾向深拷贝          |
| Go     | 手动（如 `json.Marshal`）      | 结构体赋值（注意指针/切片）    | 结构体默认深拷贝，指针需手动处理      |
| Java   | 序列化或递归克隆              | `clone()` 方法                | 默认引用赋值，深拷贝需手动实现        |
| JavaScript | `JSON.parse/stringify`      | `...` 或 `Object.assign()`    | JSON 方法不适用于复杂对象            |

各语言的深拷贝和浅拷贝实现方式不同，选择时需根据场景权衡性能和数据隔离需求。