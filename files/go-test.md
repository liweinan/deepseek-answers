# How to Write Unit Tests in Go

Go has a powerful built-in testing framework that makes writing unit tests very simple. Below I'll provide a detailed introduction to writing Go unit tests.

## 基本单元测试

1. **Test file naming**: Test files must end with `_test.go`
2. **Test function signature**: Test functions must start with `Test` and accept a `*testing.T` parameter

### Example

Suppose we have a `math.go` file:

```go
// math.go
package math

func Add(a, b int) int {
    return a + b
}
```

The corresponding test file `math_test.go`:

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

## Table-Driven Tests

The above example demonstrates table-driven tests, which is the recommended testing approach in Go:

1. Define a slice of test case structs
2. Each test case contains input and expected output
3. Iterate through all test cases to run tests

## Common testing.T Methods

- `t.Error` / `t.Errorf`: Marks test as failed but continues execution
- `t.Fatal` / `t.Fatalf`: Marks test as failed and terminates immediately
- `t.Log` / `t.Logf`: Outputs log information
- `t.Run`: Creates subtests

## Running Tests

```bash
# Run all tests in current package
go test

# Show detailed test information
go test -v

# Run specific test function
go test -run TestAdd

# Run benchmark tests
go test -bench .

# Show test coverage
go test -cover
```

## Benchmark Tests

Go also supports benchmark tests:

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
```

## Example Tests

Example tests can serve as both tests and documentation:

```go
func ExampleAdd() {
    fmt.Println(Add(1, 2))
    // Output: 3
}
```

## Test Helper Functions

You can use `t.Helper()` to mark helper functions:

```go
func assertEqual(t *testing.T, got, want int) {
    t.Helper()
    if got != want {
        t.Errorf("got %d, want %d", got, want)
    }
}
```

## Test Initialization and Cleanup

You can use `TestMain` for test initialization and cleanup:

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

## Third-Party Testing Libraries

Besides the standard library, you can also use these popular testing libraries:

- `testify/assert`: Provides richer assertion methods
- `httptest`: HTTP testing tools
- `gomock`: Generates mock objects

Go's testing framework is simple yet powerful. Following these patterns allows you to write clear, maintainable unit tests.