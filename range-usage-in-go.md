# Range Usage Examples in Go

The `range` keyword in Go is used to iterate over elements in various data structures. Here are several practical examples:

## 1. Iterating Over Slices (Most Common Usage)

```go
package main

import "fmt"

func main() {
    fruits := []string{"apple", "banana", "orange", "kiwi"}
    
    // Basic iteration (index and value)
    for index, fruit := range fruits {
        fmt.Printf("Index: %d, Fruit: %s\n", index, fruit)
    }
    
    // Iterate with index only
    for index := range fruits {
        fmt.Printf("Index: %d\n", index)
    }
    
    // Iterate with value only (using blank identifier)
    for _, fruit := range fruits {
        fmt.Printf("Fruit: %s\n", fruit)
    }
}
```

## 2. Iterating Over Maps

```go
package main

import "fmt"

func main() {
    capitals := map[string]string{
        "USA":    "Washington D.C.",
        "France": "Paris",
        "Japan":  "Tokyo",
    }
    
    // Iterate over key-value pairs
    for country, capital := range capitals {
        fmt.Printf("%s's capital is %s\n", country, capital)
    }
    
    // Iterate over keys only
    for country := range capitals {
        fmt.Printf("Country: %s\n", country)
    }
}
```

## 3. Iterating Over Strings (Runes)

```go
package main

import "fmt"

func main() {
    message := "Hello, 世界"
    
    // Range over string gives Unicode code points (runes)
    for i, r := range message {
        fmt.Printf("Byte position: %d, Rune: %c, Unicode: %U\n", i, r, r)
    }
}
```

## 4. Iterating Over Channels

```go
package main

import "fmt"

func main() {
    ch := make(chan string, 3)
    ch <- "first"
    ch <- "second"
    ch <- "third"
    close(ch) // Must close channel for range to work
    
    // Range over channel receives values until channel is closed
    for value := range ch {
        fmt.Println("Received:", value)
    }
}
```

## 5. Practical Example: Summing Numbers

```go
package main

import "fmt"

func main() {
    numbers := []int{10, 20, 30, 40, 50}
    sum := 0
    
    for _, num := range numbers {
        sum += num
    }
    
    fmt.Println("Sum:", sum) // Output: Sum: 150
}
```

## 6. Modifying Slice Elements During Iteration

```go
package main

import "fmt"

func main() {
    prices := []float64{10.5, 20.3, 15.7, 8.2}
    
    // Apply 10% discount to each price
    for i := range prices {
        prices[i] *= 0.9
    }
    
    fmt.Println("Discounted prices:", prices)
}
```

## Key Points About `range`:

1. For slices/arrays, provides `(index, value)` pairs
2. For maps, provides `(key, value)` pairs
3. For strings, iterates over Unicode code points (runes), not bytes
4. For channels, receives values until channel is closed
5. The iteration order is:
    - Predictable for slices/arrays (0 to len-1)
    - Unpredictable for maps (intentionally random)
6. You can use the blank identifier `_` to ignore either the key or value

Would you like me to elaborate on any specific aspect of `range` usage in Go?