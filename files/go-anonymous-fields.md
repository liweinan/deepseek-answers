# Anonymous Fields in Go Structs (Embedding)

In Go, you can define struct fields that consist of just a type without an explicit field name. These are called **anonymous fields** or **embedded fields**, and they enable a powerful feature called **type embedding**.

## Basic Syntax

```go
type Person struct {
    Name string
    Age  int
}

type Employee struct {
    Person  // Anonymous field (embedding)
    Salary float64
}
```

## Key Characteristics

1. **Promotion of Methods**:
    - All methods of the embedded type get promoted to the containing struct
    - You can call them directly on the outer struct

   ```go
   func (p Person) Greet() {
       fmt.Println("Hello, my name is", p.Name)
   }

   emp := Employee{Person: Person{Name: "Alice"}}
   emp.Greet()  // Works even though Greet() is Person's method
   ```

2. **Field Access**:
    - Fields of the embedded type are accessible without qualification
    - But you can still qualify them if needed

   ```go
   fmt.Println(emp.Name)      // Direct access
   fmt.Println(emp.Person.Name)  // Qualified access
   ```

3. **Collision Handling**:
    - If there are naming conflicts, you must qualify the field/method
    - Outer struct's fields/methods shadow embedded ones

## Common Use Cases

1. **Composition Over Inheritance**:
   ```go
   type Engine struct {
       Power int
   }

   type Car struct {
       Engine  // Car "has an" Engine
       Model string
   }
   ```

2. **Interface Implementation**:
   ```go
   type Reader interface {
       Read(p []byte) (n int, err error)
   }

   type MyReader struct {
       io.Reader  // Implements Reader by embedding
   }
   ```

3. **Extending Behavior**:
   ```go
   type Admin struct {
       User       // Gets all User fields/methods
       Privileges []string
   }
   ```

## Important Details

1. **Embedding Pointers**:
   You can embed pointer types too:
   ```go
   type Wrapper struct {
       *SomeType
   }
   ```

2. **Multiple Embedding**:
   ```go
   type Hybrid struct {
       TypeA
       TypeB
   }
   ```

3. **Interface Embedding**:
   ```go
   type ReadCloser interface {
       io.Reader
       io.Closer
   }
   ```

4. **Zero Values**:
   Embedded fields are initialized to their zero values like regular fields

## Comparison With Regular Fields

| Feature            | Anonymous Field            | Regular Named Field         |
|--------------------|----------------------------|----------------------------|
| Access             | Direct or qualified        | Only via name              |
| Method promotion   | Yes                        | No                         |
| Shadowing          | Outer type can override    | No special relationship    |
| Memory layout      | Same as named field        | Normal field layout        |

## Example With Multiple Embedding

```go
type Address struct {
    City string
}

type Contact struct {
    Phone string
}

type Customer struct {
    Address
    Contact
    LoyaltyPoints int
}

func main() {
    c := Customer{
        Address: Address{City: "Boston"},
        Contact: Contact{Phone: "555-1234"},
    }
    
    fmt.Println(c.City)   // From Address
    fmt.Println(c.Phone)  // From Contact
}
```

Anonymous fields are a powerful Go feature that enables clean composition patterns while avoiding the complexity of classical inheritance. They're widely used in Go code to build flexible and maintainable type hierarchies.