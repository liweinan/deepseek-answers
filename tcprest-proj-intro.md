# **Comprehensive Technical Report: TcpRest Project**

## **1. Project Overview**
**Repository**: [liweinan/tcprest](https://github.com/liweinan/tcprest)  
**Language**: Java  
**Framework**: Netty (NIO-based)  
**Purpose**: A lightweight **HTTP-to-TCP proxy** that:
- Accepts HTTP requests
- Forwards payloads to a downstream TCP service
- Returns TCP responses as HTTP replies

---

## **2. Key Components**
### **2.1 Architecture Overview**
```mermaid
flowchart LR
    A[HTTP Client] -->|POST /send| B[Netty HTTP Server]
    B --> C[HttpServerHandler]
    C -->|Forward| D[Netty TCP Client]
    D -->|TCP Req| E[Downstream TCP Service]
    E -->|TCP Resp| D
    D --> C
    C --> B
    B -->|HTTP 200/Error| A
```

### **2.2 Module Breakdown**
| Component           | Purpose                          | Key Classes                     |
|---------------------|----------------------------------|---------------------------------|
| **HTTP Server**     | Listens on HTTP (8080 by default)| `NettyHttpServer`, `HttpServerHandler` |
| **TCP Client**      | Connects to downstream TCP       | `NettyTcpClient`                |
| **TCP Server**      | Optional test TCP server (7001)  | `NettyTcpServer`, `TcpServerHandler` |

---

## **3. Detailed UML Diagrams**
### **3.1 Class Diagram**
```mermaid
classDiagram
    class TcpRestApp {
        +main(String[] args)
    }

    class NettyHttpServer {
        -int port
        +start()
        -createServerBootstrap() ServerBootstrap
    }

    class HttpServerHandler {
        -NettyTcpClient tcpClient
        +channelRead(ctx, msg)
    }

    class NettyTcpClient {
        +send(String msg): String
    }

    class NettyTcpServer {
        -int port
        +start()
    }

    class TcpServerHandler {
        +channelRead(ctx, msg)
    }

    TcpRestApp --> NettyHttpServer
    TcpRestApp --> NettyTcpServer
    NettyHttpServer --> HttpServerHandler
    HttpServerHandler --> NettyTcpClient
    NettyTcpServer --> TcpServerHandler
```

### **3.2 Sequence Diagram (HTTP → TCP Flow)**
```mermaid
sequenceDiagram
    participant HTTP_Client
    participant Netty_HTTP_Server
    participant HttpServerHandler
    participant Netty_TCP_Client
    participant Downstream_TCP_Service

    HTTP_Client ->> Netty_HTTP_Server: POST /send {"data":"test"}
    Netty_HTTP_Server ->> HttpServerHandler: Forward ByteBuf
    HttpServerHandler ->> Netty_TCP_Client: send("test")
    Netty_TCP_Client ->> Downstream_TCP_Service: TCP "test"
    Downstream_TCP_Service -->> Netty_TCP_Client: TCP "OK"
    Netty_TCP_Client -->> HttpServerHandler: "OK"
    HttpServerHandler -->> Netty_HTTP_Server: HTTP 200 "OK"
    Netty_HTTP_Server -->> HTTP_Client: HTTP 200 {"response":"OK"}
```

---

## **4. NIO Implementation**
### **4.1 Netty NIO Components**
| Class               | NIO Usage                              |
|---------------------|----------------------------------------|
| `NettyHttpServer`   | `NioEventLoopGroup`, `NioServerSocketChannel` |
| `NettyTcpServer`    | `NioEventLoopGroup`, `NioSocketChannel` |
| `NettyTcpClient`    | Bootstrap with NIO transport           |

### **4.2 Non-Blocking I/O Flow**
1. **EventLoop Groups**:
   ```java
   // Both HTTP and TCP servers use NIO
   EventLoopGroup bossGroup = new NioEventLoopGroup();
   EventLoopGroup workerGroup = new NioEventLoopGroup();
   ```
2. **Zero-Copy Optimization**:
    - Uses Netty's `ByteBuf` for zero-copy memory access.

---

## **5. Code Highlights**
### **5.1 HTTP → TCP Bridging**
```java
// HttpServerHandler.java
public void channelRead(ChannelHandlerContext ctx, Object msg) {
    if (msg instanceof FullHttpRequest) {
        String content = ((FullHttpRequest) msg).content().toString(CharsetUtil.UTF_8);
        String tcpResponse = tcpClient.send(content); // Blocking call (could be improved)
        FullHttpResponse httpResponse = new DefaultFullHttpResponse(
            HTTP_1_1, OK, Unpooled.copiedBuffer(tcpResponse, CharsetUtil.UTF_8));
        ctx.writeAndFlush(httpResponse);
    }
}
```

### **5.2 TCP Server Handler**
```java
// TcpServerHandler.java
public void channelRead(ChannelHandlerContext ctx, Object msg) {
    String request = (String) msg;
    ctx.writeAndFlush("TCP Reply: " + request); // Echo server behavior
}
```

---

## **6. Performance Characteristics**
| Metric               | Detail                                |
|----------------------|---------------------------------------|
| **Concurrency Model**| Netty NIO (1 thread per core)         |
| **Throughput**       | Limited by TCP client's blocking call |
| **Scalability**      | Vertical scaling (more cores)         |

---

## **7. Limitations & Improvements**
### **7.1 Current Limitations**
1. **Blocking TCP Client**: `NettyTcpClient.send()` is synchronous.
2. **No Connection Pooling**: New TCP connection per request.
3. **Minimal Error Handling**: Basic channel exception logging.

### **7.2 Suggested Improvements**
1. **Reactive TCP Client**:
   ```java
   public Mono<String> sendReactive(String msg) {
       return Mono.fromCallable(() -> tcpClient.send(msg))
           .subscribeOn(Schedulers.boundedElastic());
   }
   ```
2. **Protocol Buffers Support**:
   ```java
   ch.pipeline().addLast(new ProtobufVarint32FrameDecoder());
   ch.pipeline().addLast(new ProtobufDecoder(MyProto.getDefaultInstance()));
   ```
3. **Load Testing**: Add JMeter/Gatling scenarios.

---

## **8. Conclusion**
This project demonstrates a **minimalist Netty-based gateway** for:  
✅ HTTP-to-TCP protocol conversion  
✅ NIO-powered non-blocking I/O  
✅ Extensible handler architecture

**Best For**: Legacy system integration where HTTP frontends need to communicate with TCP backends.

---
**Final Note**: The absence of Spring makes this project ideal for lightweight deployments where framework overhead is undesirable. Contributions to make the TCP client non-blocking would significantly improve throughput.