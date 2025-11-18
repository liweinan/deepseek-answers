# Go Language Cheatsheet

## Basic Syntax

```go
package main      // Package declaration

import "fmt"      // Import package

func main() {     // Main function
    fmt.Println("Hello, World!")
}
```

## Variables and Constants

```go
// Variable declaration
var name string = "Go"
var age = 30      // Type inference
count := 10       // Short declaration (only inside functions)

// Multiple variable declaration
var a, b, c = 1, 2, 3
x, y := "x", "y"

// Constants
const Pi = 3.14
const (
    StatusOK = 200
    StatusNotFound = 404
)

// iota enumeration
const (
    Zero = iota   // 0
    One           // 1
    Two           // 2
)
```

## Basic Data Types

```go
// Boolean
var isActive bool = true

// Numeric types
var num int = 42
var floatNum float64 = 3.14

// String
str := "Hello"
ch := str[0]       // Get character (byte type)
length := len(str) // String length

// Type conversion
i := 42
f := float64(i)
s := string(i)     // Note: not number to string conversion
s2 := fmt.Sprintf("%d", i) // Correct way to convert number to string
```

## Composite Data Types

```go
// Array
var arr [3]int = [3]int{1, 2, 3}
arr2 := [...]int{4, 5, 6} // Compiler calculates length

// Slice (dynamic array)
slice := []int{1, 2, 3}
slice = append(slice, 4)  // Append element
sub := slice[1:3]        // Slice operation [start:end]

// Map
m := map[string]int{"a": 1, "b": 2}
value, exists := m["a"]  // Check if key exists

// Struct
type Person struct {
    Name string
    Age  int
}
p := Person{Name: "Alice", Age: 25}
```

## Control Structures

```go
// if-else
if x > 10 {
    // ...
} else if x > 5 {
    // ...
} else {
    // ...
}

// switch
switch day {
case "Mon":
    fmt.Println("Monday")
case "Tue":
    fmt.Println("Tuesday")
default:
    fmt.Println("Other day")
}

// for loop
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// while equivalent
i := 0
for i < 10 {
    fmt.Println(i)
    i++
}

// infinite loop
for {
    // ...
    break // exit loop
}

// range iteration
for index, value := range slice {
    fmt.Println(index, value)
}
```

## Functions

```go
// Basic function
func add(a int, b int) int {
    return a + b
}

// Multiple return values
func swap(a, b int) (int, int) {
    return b, a
}

// Named return values
func divide(a, b float64) (result float64, err error) {
    if b == 0.0 {
        err = errors.New("division by zero")
        return
    }
    result = a / b
    return
}

// Variadic parameters
func sum(nums ...int) int {
    total := 0
    for _, num := range nums {
        total += num
    }
    return total
}

// Anonymous functions and closures
func adder() func(int) int {
    sum := 0
    return func(x int) int {
        sum += x
        return sum
    }
}
```

## Pointers

```go
var p *int          // Pointer declaration
i := 42
p = &i              // Get address
fmt.Println(*p)     // Dereference
*p = 21             // Modify value through pointer
```

## Interfaces

```go
type Shape interface {
    Area() float64
}

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func printArea(s Shape) {
    fmt.Println(s.Area())
}
```

## Error Handling

```go
// Basic error handling
result, err := someFunction()
if err != nil {
    log.Fatal(err)
}

// Custom errors
type MyError struct {
    Msg string
}

func (e *MyError) Error() string {
    return e.Msg
}

func test() error {
    return &MyError{"Something went wrong"}
}
```

## Concurrency

```go
// goroutine
go func() {
    fmt.Println("Running in goroutine")
}()

// channel
ch := make(chan int)
go func() {
    ch <- 42 // Send
}()
value := <-ch // Receive

// Buffered channel
bufCh := make(chan int, 2)
bufCh <- 1
bufCh <- 2

// select
select {
case msg1 := <-ch1:
    fmt.Println(msg1)
case msg2 := <-ch2:
    fmt.Println(msg2)
case <-time.After(time.Second):
    fmt.Println("timeout")
}

// sync.WaitGroup
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(i int) {
        defer wg.Done()
        fmt.Println(i)
    }(i)
}
wg.Wait()
```

## Common Standard Libraries

```go
// fmt
fmt.Print("No newline")
fmt.Println("With newline")
fmt.Printf("Formatted: %s %d\n", "text", 42)

// strings
strings.Contains("hello", "ell")  // true
strings.Split("a,b,c", ",")      // ["a", "b", "c"]
strings.Join([]string{"a", "b"}, "-") // "a-b"

// strconv
strconv.Itoa(123)    // "123"
strconv.Atoi("123")  // 123, <error>

// os
os.Args              // Command line arguments
os.Getenv("PATH")    // Get environment variable
os.Setenv("KEY", "value")

// io/ioutil (Go 1.16+ replaced with os and io packages)
data, _ := os.ReadFile("file.txt")
os.WriteFile("file.txt", data, 0644)

// json
jsonData, _ := json.Marshal(data)
var decodedData SomeType
json.Unmarshal(jsonData, &decodedData)

// time
now := time.Now()
duration := time.Second * 5
time.Sleep(duration)
```

## Testing

```go
// Test file (xxx_test.go)
func TestAdd(t *testing.T) {
    result := add(2, 3)
    if result != 5 {
        t.Errorf("Expected 5, got %d", result)
    }
}

// Benchmark test
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        add(1, 2)
    }
}
```

## Common Commands

```bash
go run main.go       # Compile and run
go build             # Compile to executable
go test              # Run tests
go test -v           # Verbose test output
go test -bench=.     # Run benchmark tests
go mod init example.com/mymodule  # Initialize module
go get package       # Download dependencies
go fmt               # Format code
go doc fmt.Println   # View documentation
```

## Example Program

```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

func main() {
    http.HandleFunc("/users", usersHandler)
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func usersHandler(w http.ResponseWriter, r *http.Request) {
    users := []User{
        {1, "Alice", "alice@example.com"},
        {2, "Bob", "bob@example.com"},
    }
    
    w.Header().Set("Content-Type", "application/json")
    if err := json.NewEncoder(w).Encode(users); err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
    }
}
```

This cheatsheet covers the main features of the Go language and can be used as a quick reference for daily development. You can dive deeper into specific areas based on your needs.