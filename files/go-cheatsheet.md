# Go 语言速查表 (Cheatsheet)

## 基础语法

```go
package main      // 包声明

import "fmt"      // 导入包

func main() {     // 主函数
    fmt.Println("Hello, World!")
}
```

## 变量与常量

```go
// 变量声明
var name string = "Go"
var age = 30      // 类型推断
count := 10       // 简短声明(只能在函数内)

// 多变量声明
var a, b, c = 1, 2, 3
x, y := "x", "y"

// 常量
const Pi = 3.14
const (
    StatusOK = 200
    StatusNotFound = 404
)

// iota 枚举
const (
    Zero = iota   // 0
    One           // 1
    Two           // 2
)
```

## 基本数据类型

```go
// 布尔
var isActive bool = true

// 数字类型
var num int = 42
var floatNum float64 = 3.14

// 字符串
str := "Hello"
ch := str[0]       // 获取字符(byte类型)
length := len(str) // 字符串长度

// 类型转换
i := 42
f := float64(i)
s := string(i)     // 注意: 不是数字转字符串
s2 := fmt.Sprintf("%d", i) // 正确数字转字符串方式
```

## 复合数据类型

```go
// 数组
var arr [3]int = [3]int{1, 2, 3}
arr2 := [...]int{4, 5, 6} // 编译器计算长度

// 切片(动态数组)
slice := []int{1, 2, 3}
slice = append(slice, 4)  // 追加元素
sub := slice[1:3]        // 切片操作 [start:end]

// 映射(map)
m := map[string]int{"a": 1, "b": 2}
value, exists := m["a"]  // 检查键是否存在

// 结构体
type Person struct {
    Name string
    Age  int
}
p := Person{Name: "Alice", Age: 25}
```

## 控制结构

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

// for 循环
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// while 等效
i := 0
for i < 10 {
    fmt.Println(i)
    i++
}

// 无限循环
for {
    // ...
    break // 退出循环
}

// range 遍历
for index, value := range slice {
    fmt.Println(index, value)
}
```

## 函数

```go
// 基本函数
func add(a int, b int) int {
    return a + b
}

// 多返回值
func swap(a, b int) (int, int) {
    return b, a
}

// 命名返回值
func divide(a, b float64) (result float64, err error) {
    if b == 0.0 {
        err = errors.New("division by zero")
        return
    }
    result = a / b
    return
}

// 可变参数
func sum(nums ...int) int {
    total := 0
    for _, num := range nums {
        total += num
    }
    return total
}

// 匿名函数和闭包
func adder() func(int) int {
    sum := 0
    return func(x int) int {
        sum += x
        return sum
    }
}
```

## 指针

```go
var p *int          // 指针声明
i := 42
p = &i              // 获取地址
fmt.Println(*p)     // 解引用
*p = 21             // 通过指针修改值
```

## 接口

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

## 错误处理

```go
// 基本错误处理
result, err := someFunction()
if err != nil {
    log.Fatal(err)
}

// 自定义错误
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

## 并发

```go
// goroutine
go func() {
    fmt.Println("Running in goroutine")
}()

// channel
ch := make(chan int)
go func() {
    ch <- 42 // 发送
}()
value := <-ch // 接收

// 带缓冲的channel
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

## 常用标准库

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
os.Args              // 命令行参数
os.Getenv("PATH")    // 获取环境变量
os.Setenv("KEY", "value")

// io/ioutil (Go 1.16+ 使用 os 和 io 包替代)
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

## 测试

```go
// 测试文件 (xxx_test.go)
func TestAdd(t *testing.T) {
    result := add(2, 3)
    if result != 5 {
        t.Errorf("Expected 5, got %d", result)
    }
}

// 基准测试
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        add(1, 2)
    }
}
```

## 常用命令

```bash
go run main.go       # 编译并运行
go build             # 编译生成可执行文件
go test              # 运行测试
go test -v           # 详细测试输出
go test -bench=.     # 运行基准测试
go mod init example.com/mymodule  # 初始化模块
go get package       # 下载依赖
go fmt               # 格式化代码
go doc fmt.Println   # 查看文档
```

## 示例程序

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

这个速查表涵盖了 Go 语言的主要特性，可以作为日常开发的快速参考。根据你的具体需求，可以进一步深入某个特定领域。