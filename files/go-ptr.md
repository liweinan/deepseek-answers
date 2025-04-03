# When to Use Pointer Fields in Go Structs

Using pointers as fields in Go structs is an important design decision that affects memory usage, mutability, and performance. Here are the key scenarios when you should use pointer fields:

## 1. For Optional Fields (Nullable Semantics)

Pointers naturally represent optional fields since a nil pointer indicates absence:

```go
type User struct {
    ID       int
    Name     string
    Address  *Address // Optional field (may be nil)
}
```

Without pointers, you'd need zero-value sentinels or boolean flags to indicate absence.

## 2. For Large Structs (Memory Efficiency)

When a field contains a large struct, using a pointer avoids copying the entire struct:

```go
type Report struct {
    Metadata ReportMeta
    Data     *BigDataStruct // More efficient than embedding the entire big struct
}
```

## 3. For Mutable Shared State

When multiple instances need to reference and modify the same underlying data:

```go
type Player struct {
    ID     int
    Health *int // Shared health pool for party members
}
```

## 4. For Recursive or Self-Referential Types

Structs that need to reference themselves (like trees, linked lists):

```go
type Node struct {
    Value int
    Next  *Node // Can't use Node here - would be infinite size
}
```

## 5. When Implementing Interface Fields

If a field needs to hold different concrete types that implement an interface:

```go
type PaymentProcessor struct {
    Gateway PaymentGateway // Interface
    Logger  *log.Logger   // Concrete type via pointer
}
```

## 6. For Structs with Mutexes or Synchronization

Mutexes should never be copied (would break synchronization):

```go
type SafeCounter struct {
    mu    *sync.Mutex // Pointer ensures proper synchronization
    count int
}
```

## When NOT to Use Pointer Fields

1. **For Small, Frequently Used Value Types** (int, float64, time.Time)
   ```go
   type Point struct {
       X, Y float64 // Better as values
   }
   ```

2. **When Immutability is Desired**
   ```go
   type Config struct {
       Timeout time.Duration // Value prevents external modification
   }
   ```

3. **For Simple Data Transfer Objects**
   ```go
   type Coordinate struct {
       Lat, Long float64 // Values simplify usage
   }
   ```

## Performance Considerations

| Scenario | Pointer Field | Value Field |
|----------|--------------|-------------|
| Memory usage | Lower (for large structs) | Higher (full copy) |
| Allocation pressure | Higher (heap) | Lower (often stack) |
| Cache locality | Worse | Better |
| Mutation control | Shared changes | Isolated changes |
| Nil checks | Required | Not needed |

## Practical Example

```go
type Order struct {
    ID          int         // Value (small primitive)
    CreatedAt   time.Time   // Value (small struct)
    Customer    *Customer   // Pointer (may be nil/optional)
    Items       []*Item     // Slice of pointers (items may be large)
    Payment     PaymentInfo // Value (small-medium struct)
    CancelledBy *Employee   // Pointer (optional)
    mu          *sync.Mutex // Pointer (mutexes shouldn't be copied)
}
```

The decision ultimately depends on your specific requirements for memory usage, mutability, and performance characteristics.