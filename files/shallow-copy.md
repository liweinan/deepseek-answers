# Deep Copy vs Shallow Copy

## Overview

Deep copy and shallow copy are two ways of handling object copying in programming, with differences in how they handle nested data.

- **Shallow Copy**:
  - Only copies the first level of data. For nested objects or reference types (such as pointers, objects, slices), only the reference is copied, pointing to the same memory.
  - Modifying nested data in the copied object will affect the source object, and vice versa.
  - Advantages: Low memory usage, fast speed.
  - Disadvantages: Data coupling, may lead to accidental modifications.

- **Deep Copy**:
  - Recursively copies all levels of data, including nested objects, creating completely independent copies.
  - Modifying the source object or copied object does not affect each other.
  - Advantages: Data isolation, suitable for scenarios requiring independent copies.
  - Disadvantages: High memory usage, performance overhead.

Examples in Rust, Go, Java, and JavaScript are provided below, demonstrating shallow and deep copy implementations using the same `Person` and `Address` structures, clearly showing the behavioral differences between the two.

## Rust Example

Rust implements deep copy through the `Clone` trait, while shallow copy is typically achieved through references (`&`). The following example demonstrates deep and shallow copying of `Person` objects.

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

    // Deep Copy
    let p2 = p1.clone();
    println!("Before modification (deep copy):");
    println!("p1: {:?}", p1);
    println!("p2: {:?}", p2);
    let mut p2 = p2;
    p2.address.city = String::from("Boston");
    println!("After modifying p2.address.city:");
    println!("p1: {:?}", p1); // Not affected
    println!("p2: {:?}", p2);

    // Shallow Copy: Reference
    let p3 = &p1;
    println!("\nBefore modification (shallow copy):");
    println!("p1: {:?}", p1);
    println!("p3: {:?}", p3);
}
```

**Explanation**:
- **Deep Copy**: `p1.clone()` recursively copies all fields, `p2` is an independent copy, modifying `p2.address.city` does not affect `p1`.
- **Shallow Copy**: `p3` is a reference to `p1`, only borrowing data, cannot directly modify.
- **Output**:
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

## Go Example

In Go, struct assignment defaults to deep copy, but if the struct contains pointer or reference types (such as slices), assignment only copies the reference, exhibiting shallow copy behavior. The following example demonstrates shallow copy through pointers.

```go
package main

import (
    "encoding/json"
    "fmt"
)

type Address struct {
    City *string // Pointer type
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

    // Shallow Copy: Direct assignment (copies pointer)
    p2 := p1
    fmt.Println("Before modification (shallow copy):");
    fmt.Printf("p1: {Name: %s, Address: {City: %s}}\n", p1.Name, *p1.Address.City)
    fmt.Printf("p2: {Name: %s, Address: {City: %s}}\n", p2.Name, *p2.Address.City)
    *p2.Address.City = "Boston"
    fmt.Println("After modifying *p2.Address.City:")
    fmt.Printf("p1: {Name: %s, Address: {City: %s}}\n", p1.Name, *p1.Address.City) // Affected
    fmt.Printf("p2: {Name: %s, Address: {City: %s}}\n", p2.Name, *p2.Address.City)

    // Deep Copy
    p3 := p1.DeepCopy()
    fmt.Println("\nBefore modification (deep copy):")
    fmt.Printf("p1: {Name: %s, Address: {City: %s}}\n", p1.Name, *p1.Address.City)
    fmt.Printf("p3: {Name: %s, Address: {City: %s}}\n", p3.Name, *p3.Address.City)
    *p3.Address.City = "Chicago"
    fmt.Println("After modifying *p3.Address.City:")
    fmt.Printf("p1: {Name: %s, Address: {City: %s}}\n", p1.Name, *p1.Address.City) // Not affected
    fmt.Printf("p3: {Name: %s, Address: {City: %s}}\n", p3.Name, *p3.Address.City)
}
```

**Explanation**:
- **Shallow Copy**: `p2 := p1` copies the `City` pointer, `p1.Address.City` and `p2.Address.City` point to the same string, modifying `*p2.Address.City` affects `p1`.
- **Deep Copy**: JSON serialization creates an independent copy, `p3.Address.City` points to a new string, modifying `*p3.Address.City` does not affect `p1`.
- **Output**:
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

## Java Example

Java defaults to shallow copy through reference assignment, deep copy requires manual recursive cloning. The following example demonstrates shallow and deep copy using the `clone()` method.

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

    // Shallow Copy
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }

    // Deep Copy
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

        // Shallow Copy
        Person p2 = (Person) p1.clone();
        System.out.println("Before modification (shallow copy):");
        System.out.println("p1: " + p1);
        System.out.println("p2: " + p2);
        p2.address.city = "Boston";
        System.out.println("After modifying p2.address.city:");
        System.out.println("p1: " + p1); // Affected
        System.out.println("p2: " + p2);

        // Deep Copy
        Person p3 = p1.deepCopy();
        System.out.println("\nBefore modification (deep copy):");
        System.out.println("p1: " + p1);
        System.out.println("p3: " + p3);
        p3.address.city = "Chicago";
        System.out.println("After modifying p3.address.city:");
        System.out.println("p1: " + p1); // Not affected
        System.out.println("p3: " + p3);
    }
}
```

**Explanation**:
- **Shallow Copy**: `clone()` only copies the reference, `p2.address` and `p1.address` point to the same object, modifying `p2.address.city` affects `p1`.
- **Deep Copy**: `deepCopy` recursively clones `address`, `p3.address` is an independent object, modifying `p3.address.city` does not affect `p1`.
- **Output**:
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

## JavaScript Example

JavaScript object assignment defaults to shallow copy, deep copy requires specific methods such as JSON serialization.

```javascript
const p1 = {
    name: "Alice",
    address: { city: "New York" }
};

// Shallow Copy
const p2 = { ...p1 };
console.log("Before modification (shallow copy):");
console.log("p1:", p1);
console.log("p2:", p2);
p2.address.city = "Boston";
console.log("After modifying p2.address.city:");
console.log("p1:", p1); // Affected
console.log("p2:", p2);

// Deep Copy
const p3 = JSON.parse(JSON.stringify(p1));
console.log("\nBefore modification (deep copy):");
console.log("p1:", p1);
console.log("p3:", p3);
p3.address.city = "Chicago";
console.log("After modifying p3.address.city:");
console.log("p1:", p1); // Not affected
console.log("p3:", p3);
```

**Explanation**:
- **Shallow Copy**: The spread operator (`...`) only copies the first level, `p2.address` and `p1.address` point to the same object, modifying `p2.address.city` affects `p1`.
- **Deep Copy**: `JSON.parse(JSON.stringify(p1))` creates an independent copy, modifying `p3.address.city` does not affect `p1`.
- **Output**:
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

## Summary

| Language       | Deep Copy Implementation                     | Shallow Copy Implementation                     | Features and Considerations                        |
|------------|--------------------------------|--------------------------------|--------------------------------------|
| Rust       | `Clone` trait                 | Reference (`&`)                   | Defaults to deep copy, references implement shallow copy, memory safe  |
| Go         | JSON serialization or manual               | Assignment (with pointers/slices)           | Structs default to deep copy, pointers cause shallow copy      |
| Java       | Recursive cloning (`deepCopy`)        | `clone()`                     | Shallow copy only copies references, deep copy requires manual recursion    |
| JavaScript | `JSON.parse/stringify`        | `...` or `Object.assign()`    | JSON method is simple but not suitable for complex objects        |

These examples use consistent `Person` and `Address` structures to clearly demonstrate the shared reference problem of shallow copy and the isolation characteristics of deep copy. When choosing a copy method, you need to weigh performance and data isolation requirements.