# Go's I/O Approach vs Java NIO

Go doesn't have an exact equivalent to Java NIO (New I/O), but it provides similar non-blocking I/O capabilities through different mechanisms that are more idiomatic to Go's design. Here's how they compare:

## Key Similarities to Java NIO

1. **Non-blocking I/O**: Go's goroutines and channels provide a model for handling concurrent I/O operations without blocking threads.

2. **Multiplexing**: The `select` statement allows waiting on multiple channel operations similar to Java's `Selector`.

3. **Buffered operations**: Go has buffered channels and I/O buffers in packages like `bufio`.

## Key Differences

1. **No explicit selectors**: Go handles this through channels and the `select` statement rather than explicit selector objects.

2. **Goroutines instead of callbacks**: Go uses lightweight goroutines instead of Java's callback-based approach.

## Go Features Comparable to Java NIO Components

### 1. Channels (similar to Java NIO Channels)
```go
file, err := os.Open("file.txt") // Similar to FileChannel
conn, err := net.Dial("tcp", "example.com:80") // Similar to SocketChannel
```

### 2. Multiplexing with `select` (similar to Selector)
```go
select {
case data := <-ch1:
    // Handle data from ch1
case data := <-ch2:
    // Handle data from ch2
case <-time.After(time.Second):
    // Timeout handling
}
```

### 3. Non-blocking I/O
```go
// Non-blocking channel operation
select {
case msg := <-ch:
    fmt.Println(msg)
default:
    // No message available
}

// Non-blocking HTTP request with context
ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
req, _ := http.NewRequestWithContext(ctx, "GET", "http://example.com", nil)
```

### 4. Buffered I/O
```go
// Similar to Java's BufferedXXX channels
reader := bufio.NewReader(file)
writer := bufio.NewWriter(file)
```

### 5. Epoll/kqueue equivalent
Go's runtime uses efficient I/O multiplexing (epoll/kqueue/IOCP) automatically:
```go
// The net package uses non-blocking I/O internally
ln, _ := net.Listen("tcp", ":8080")
conn, _ := ln.Accept() // Underlying non-blocking I/O handled by runtime
```

## Example: Non-blocking TCP Server

Here's a Go equivalent to a Java NIO server:

```go
package main

import (
    "log"
    "net"
)

func handleConn(conn net.Conn) {
    defer conn.Close()
    buf := make([]byte, 1024)
    for {
        n, err := conn.Read(buf)
        if err != nil {
            return
        }
        conn.Write(buf[:n])
    }
}

func main() {
    ln, err := net.Listen("tcp", ":8080")
    if err != nil {
        log.Fatal(err)
    }
    
    for {
        conn, err := ln.Accept()
        if err != nil {
            log.Println(err)
            continue
        }
        go handleConn(conn) // Each connection handled in its own goroutine
    }
}
```

While the implementation approach differs, Go provides similar non-blocking I/O capabilities through its goroutine scheduler and channel-based concurrency model, which many find simpler to work with than Java's NIO.