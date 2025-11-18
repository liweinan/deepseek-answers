# Go Language Interview Questions (with Answers)

## Part 1: Basic Syntax (20 points)

### 1. What does the following code output? Why? (5 points)
```go
package main

import "fmt"

func main() {
    var a int = 5
    var b int = 2
    var c float64 = float64(a) / float64(b)
    fmt.Println(c)
}
```

**Answer**:
```
2.5
```
**Explanation**: Integer division truncates the decimal part, converting to float64 preserves decimals in division.

### 2. What's wrong with this code? How to fix it? (5 points)
```go
func main() {
    var x int
    var y *int
    y = &x
    *y = 10
    fmt.Println(*y)
}
```

**Answer**:
No problem with the code, outputs `10`. Demonstrates basic pointer usage.

### 3. What does this code output? (5 points)
```go
func main() {
    s := []int{1, 2, 3}
    modifySlice(s)
    fmt.Println(s)
}

func modifySlice(s []int) {
    s[0] = 100
}
```

**Answer**:
```
[100 2 3]
```
**Explanation**: Slices are reference types, modifications inside function affect the original slice.

### 4. Write the defer execution order (5 points)
```go
func main() {
    defer fmt.Println(1)
    defer fmt.Println(2)
    fmt.Println(3)
}
```

**Answer**:
```
3
2
1
```
**Explanation**: defer executes in LIFO (Last In, First Out) order.

## Part 2: Concurrent Programming (30 points)

### 1. What's wrong with this code? (10 points)
```go
func main() {
    var wg sync.WaitGroup
    for i := 0; i < 5; i++ {
        go func() {
            wg.Add(1)
            defer wg.Done()
            fmt.Println(i)
        }()
    }
    wg.Wait()
}
```

**Answer**:
Problem 1: `wg.Add(1)` should be called outside the goroutine
Problem 2: The closure captures the final value of the loop variable (will output multiple 5s)
Fix:
```go
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(i int) {
        defer wg.Done()
        fmt.Println(i)
    }(i)
}
```

### 2. Implement a concurrent-safe counter (10 points)
```go
type Counter struct {
    // Complete the code
}

func (c *Counter) Inc() {
    // Complete the code
}

func (c *Counter) Value() int {
    // Complete the code
}
```

**Answer**:
```go
type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}
```

### 3. Implement a worker pool using channels (10 points)
Implement a worker pool that processes 100 tasks with concurrency of 10.

**Answer**:
```go
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        fmt.Printf("worker %d processing job %d\n", id, j)
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)
    
    // Start 10 workers
    for w := 1; w <= 10; w++ {
        go worker(w, jobs, results)
    }
    
    // Send 100 tasks
    for j := 1; j <= 100; j++ {
        jobs <- j
    }
    close(jobs)
    
    // Collect results
    for a := 1; a <= 100; a++ {
        <-results
    }
}
```

## Part 3: Advanced Features (30 points)

### 1. Explain interface underlying implementation (10 points)

**Answer**:
Go's interface consists of two parts:
1. `_type`: stores dynamic type information
2. `data`: pointer to actual value

For empty interface `interface{}`:
```go
type eface struct {
    _type *_type
    data  unsafe.Pointer
}
```

For non-empty interface (like `io.Reader`):
```go
type iface struct {
    tab  *itab
    data unsafe.Pointer
}
```

### 2. What does this code output? (10 points)
```go
func main() {
    var i interface{} = "hello"
    
    switch v := i.(type) {
    case int:
        fmt.Printf("int: %d\n", v)
    case string:
        fmt.Printf("string: %s\n", v)
    default:
        fmt.Printf("unknown type\n")
    }
}
```

**Answer**:
```
string: hello
```

### 3. Implement a simple HTTP server (10 points)
Requirement: Listen on port 8080, return "Hello World" at /hello

**Answer**:
```go
package main

import (
    "fmt"
    "net/http"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello World")
}

func main() {
    http.HandleFunc("/hello", helloHandler)
    http.ListenAndServe(":8080", nil)
}
```

## Part 4: Practical Programming (20 points)

### 1. Implement quicksort (10 points)

**Answer**:
```go
func quickSort(arr []int) []int {
    if len(arr) <= 1 {
        return arr
    }
    
    pivot := arr[0]
    var left, right []int
    
    for i := 1; i < len(arr); i++ {
        if arr[i] < pivot {
            left = append(left, arr[i])
        } else {
            right = append(right, arr[i])
        }
    }
    
    left = quickSort(left)
    right = quickSort(right)
    
    return append(append(left, pivot), right...)
}
```

### 2. Parse JSON file and calculate average (10 points)
Given data.json:
```json
[{"name":"A","score":80},{"name":"B","score":90}]
```

**Answer**:
```go
type Student struct {
    Name  string `json:"name"`
    Score int    `json:"score"`
}

func averageScore(filename string) (float64, error) {
    data, err := os.ReadFile(filename)
    if err != nil {
        return 0, err
    }
    
    var students []Student
    if err := json.Unmarshal(data, &students); err != nil {
        return 0, err
    }
    
    if len(students) == 0 {
        return 0, nil
    }
    
    sum := 0
    for _, s := range students {
        sum += s.Score
    }
    
    return float64(sum) / float64(len(students)), nil
}
```

## Scoring Criteria

- 90-100 points: Senior Go Development Engineer
- 70-89 points: Advanced Go Development Engineer
- 50-69 points: Intermediate Go Development Engineer
- 30-49 points: Junior Go Development Engineer
- 0-29 points: Needs to strengthen Go language learning

This exam covers the core knowledge points of Go language, including basic syntax, concurrent programming, advanced features, and practical programming, suitable for assessing candidates' comprehensive Go language abilities.

