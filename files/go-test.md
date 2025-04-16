# 如何编写基于Go的单元测试

Go语言内置了强大的测试框架，使得编写单元测试非常简单。下面我将详细介绍如何编写Go单元测试。

## 基本单元测试

1. **测试文件命名**：测试文件必须以`_test.go`结尾
2. **测试函数签名**：测试函数必须以`Test`开头，接收`*testing.T`参数

### 示例

假设我们有一个`math.go`文件：

```go
// math.go
package math

func Add(a, b int) int {
    return a + b
}
```

对应的测试文件`math_test.go`：

```go
// math_test.go
package math

import "testing"

func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -1, -1, -2},
        {"mixed numbers", -1, 1, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := Add(tt.a, tt.b); got != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, got, tt.expected)
            }
        })
    }
}
```

## 表格驱动测试

上面的例子展示了表格驱动测试(table-driven tests)，这是Go中推荐的测试方式：

1. 定义测试用例结构体切片
2. 每个测试用例包含输入和期望输出
3. 遍历所有测试用例运行测试

## 常用testing.T方法

- `t.Error` / `t.Errorf`：标记测试失败但继续执行
- `t.Fatal` / `t.Fatalf`：标记测试失败并立即终止
- `t.Log` / `t.Logf`：输出日志信息
- `t.Run`：创建子测试

## 运行测试

```bash
# 运行当前包的所有测试
go test

# 显示详细测试信息
go test -v

# 运行特定测试函数
go test -run TestAdd

# 运行基准测试
go test -bench .

# 显示测试覆盖率
go test -cover
```

## 基准测试

Go还支持基准测试：

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
```

## 示例测试

示例测试可以同时作为测试和文档：

```go
func ExampleAdd() {
    fmt.Println(Add(1, 2))
    // Output: 3
}
```

## 测试辅助函数

可以使用`t.Helper()`标记辅助函数：

```go
func assertEqual(t *testing.T, got, want int) {
    t.Helper()
    if got != want {
        t.Errorf("got %d, want %d", got, want)
    }
}
```

## 测试初始化与清理

可以使用`TestMain`进行测试初始化和清理：

```go
func TestMain(m *testing.M) {
    // 初始化代码
    setup()
    
    // 运行测试
    code := m.Run()
    
    // 清理代码
    teardown()
    
    os.Exit(code)
}
```

## 第三方测试库

除了标准库，还可以使用这些流行的测试库：

- `testify/assert`：提供更丰富的断言方法
- `httptest`：HTTP测试工具
- `gomock`：生成mock对象

Go的测试框架简单而强大，遵循这些模式可以编写出清晰、可维护的单元测试。