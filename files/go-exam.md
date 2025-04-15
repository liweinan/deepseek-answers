# Go 语言面试题卷（含答案）

## 第一部分：基础语法（20分）

### 1. 下面代码输出什么？为什么？（5分）
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

**答案**：
```
2.5
```
**解析**：整数相除会截断小数部分，转换为 float64 后除法会保留小数。

### 2. 以下代码有什么问题？如何修复？（5分）
```go
func main() {
    var x int
    var y *int
    y = &x
    *y = 10
    fmt.Println(*y)
}
```

**答案**：
代码没有问题，输出 `10`。展示了指针的基本用法。

### 3. 下面代码的输出是什么？（5分）
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

**答案**：
```
[100 2 3]
```
**解析**：切片是引用类型，函数内修改会影响原切片。

### 4. 写出defer的执行顺序（5分）
```go
func main() {
    defer fmt.Println(1)
    defer fmt.Println(2)
    fmt.Println(3)
}
```

**答案**：
```
3
2
1
```
**解析**：defer 是后进先出（LIFO）的执行顺序。

## 第二部分：并发编程（30分）

### 1. 以下代码有什么问题？（10分）
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

**答案**：
问题1：`wg.Add(1)` 应该在 goroutine 外调用
问题2：闭包捕获的是循环变量的最终值（会输出多个5）
修复方案：
```go
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(i int) {
        defer wg.Done()
        fmt.Println(i)
    }(i)
}
```

### 2. 实现并发安全的计数器（10分）
```go
type Counter struct {
    // 补充代码
}

func (c *Counter) Inc() {
    // 补充代码
}

func (c *Counter) Value() int {
    // 补充代码
}
```

**答案**：
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

### 3. 使用channel实现工作池（10分）
实现一个工作池，处理100个任务，并发度为10。

**答案**：
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
    
    // 启动10个worker
    for w := 1; w <= 10; w++ {
        go worker(w, jobs, results)
    }
    
    // 发送100个任务
    for j := 1; j <= 100; j++ {
        jobs <- j
    }
    close(jobs)
    
    // 收集结果
    for a := 1; a <= 100; a++ {
        <-results
    }
}
```

## 第三部分：高级特性（30分）

### 1. 解释interface的底层实现（10分）

**答案**：
Go的interface由两部分组成：
1. `_type`：存储动态类型信息
2. `data`：指向实际值的指针

对于空接口`interface{}`：
```go
type eface struct {
    _type *_type
    data  unsafe.Pointer
}
```

对于非空接口（如`io.Reader`）：
```go
type iface struct {
    tab  *itab
    data unsafe.Pointer
}
```

### 2. 以下代码输出什么？（10分）
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

**答案**：
```
string: hello
```

### 3. 实现一个简单的HTTP服务器（10分）
要求：监听8080端口，/hello返回"Hello World"

**答案**：
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

## 第四部分：实战编程（20分）

### 1. 实现快速排序（10分）

**答案**：
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

### 2. 解析JSON文件并计算平均值（10分）
给定data.json:
```json
[{"name":"A","score":80},{"name":"B","score":90}]
```

**答案**：
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

## 评分标准

- 90-100分：资深Go开发工程师
- 70-89分：高级Go开发工程师
- 50-69分：中级Go开发工程师
- 30-49分：初级Go开发工程师
- 0-29分：需要加强Go语言学习

这份试卷涵盖了Go语言的核心知识点，包括基础语法、并发编程、高级特性和实战编程，适合评估候选人的综合Go语言能力。

