# Go's Interfaces vs Structs: Comparison and Differences

Go takes a unique approach to object-oriented programming concepts through its **structs** and **interfaces**. Here's a comprehensive comparison:

## Structs in Go

**Definition**:
Structs are typed collections of fields that group related data together.

**Characteristics**:
```go
type Person struct {
    Name string
    Age  int
}
```

1. **Value types** - Created with actual memory allocation
2. **Concrete implementations** - Define both state (fields) and behavior (methods)
3. **Explicit composition** - Support embedding other structs
4. **Memory layout control** - Fields are stored in declared order

**Usage**:
```go
p := Person{Name: "Alice", Age: 30}
p.Age = 31  // Direct field access
```

## Interfaces in Go

**Definition**:
Interfaces are abstract types that define sets of method signatures.

**Characteristics**:
```go
type Speaker interface {
    Speak() string
}
```

1. **Reference types** - Hold (value, type) pairs
2. **Behavior contracts** - Only method definitions, no implementation
3. **Implicit implementation** - No explicit "implements" declaration
4. **Duck typing** - "If it quacks like a duck, it's a duck"

**Usage**:
```go
func MakeSound(s Speaker) {
    fmt.Println(s.Speak())
}
```

## Key Differences

| Feature              | Struct                          | Interface                      |
|----------------------|---------------------------------|--------------------------------|
| **Type**            | Concrete type                   | Abstract type                  |
| **Data Storage**    | Contains actual data fields     | Contains (value, type) pair    |
| **Methods**         | Implements methods              | Declares method signatures     |
| **Initialization**  | `s := MyStruct{}`               | `var i MyInterface = MyStruct{}` |
| **Zero Value**      | All fields zero-valued          | `nil`                          |
| **Implementation**  | Explicit field/method definition | Implicit satisfaction          |
| **Memory**         | Direct memory allocation        | Reference to concrete value    |
| **Use Case**       | Data organization               | Polymorphism                   |

## Practical Examples

### Struct Example
```go
type Car struct {
    Model string
    Speed int
}

func (c Car) Drive() string {
    return fmt.Sprintf("%s driving at %d mph", c.Model, c.Speed)
}
```

### Interface Example
```go
type Vehicle interface {
    Drive() string
}

func Describe(v Vehicle) {
    fmt.Println(v.Drive())
}

// Car automatically satisfies Vehicle by implementing Drive()
```

## When to Use Each

**Use Structs When**:
- You need to store actual data
- You want to define concrete behavior
- You need memory-efficient value types
- You want to control memory layout

**Use Interfaces When**:
- You need polymorphism
- You want to write generic functions
- You need to abstract implementation details
- You're defining contracts between components

## Unique Go Features

1. **Empty Interface** (`interface{}`):
    - Can hold any value
    - Used for generic programming (before Go 1.18 generics)

2. **Type Assertions**:
   ```go
   if car, ok := v.(Car); ok {
       fmt.Println(car.Model)
   }
   ```

3. **Interface Composition**:
   ```go
   type ReadWriter interface {
       Reader
       Writer
   }
   ```

4. **Struct Embedding**:
   ```go
   type Employee struct {
       Person  // Embedding
       Salary float64
   }
   ```

Go's approach emphasizes composition over classical inheritance, making the relationships between types more explicit and avoiding many of the pitfalls of traditional OOP inheritance hierarchies.