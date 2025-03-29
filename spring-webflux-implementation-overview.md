# Spring WebFlux Implementation Overview

Spring WebFlux is the reactive-stack web framework introduced in Spring 5, designed as an alternative to Spring MVC for non-blocking, asynchronous request handling. Here's how it's implemented:

## Core Architecture

1. **Reactive Foundation**
    - Built on Project Reactor (Reactor Core 3.x)
    - Uses reactive types (`Mono` and `Flux`) instead of traditional `CompletableFuture` or direct values

2. **Event Loop Model**
    - Non-blocking I/O model (not necessarily tied to Netty but commonly used with it)
    - Can run on Servlet 3.1+ containers with async support or on non-Servlet runtimes like Netty

## Key Implementation Components

### 1. HTTP Layer Abstraction
- **Reactive HTTP API**: `ServerHttpRequest` and `ServerHttpResponse` interfaces
- **Server Adaptations**:
    - Netty (default)
    - Undertow
    - Servlet 3.1+ containers (Tomcat, Jetty)
    - Reactor-Native (experimental)

### 2. Handler Chain
```java
HttpHandler -> WebHandler -> DispatcherHandler -> HandlerAdapter -> Controller
```
- `HttpHandler`: Top-level contract for HTTP request handling
- `WebHandler`: Core web handler API with filter chain support
- `DispatcherHandler`: Central dispatcher (similar to MVC's DispatcherServlet)

### 3. Router Function Implementation
Functional endpoint alternative to annotation-based controllers:
```java
RouterFunctions.route()
  .GET("/path", handlerFunction)
  .POST("/other", otherHandler)
  .build();
```

### 4. Reactive Return Types
Controller methods return:
- `Mono<T>` (0..1 result)
- `Flux<T>` (0..N results)
- Other reactive types (RxJava, etc.) via adapters

### 5. Reactive Adapters
- Conversion between different reactive libraries:
    - Reactor ↔ RxJava
    - Reactor ↔ Java 9 Flow
    - Reactor ↔ Kotlin Coroutines

## Under the Hood

1. **Request Processing Flow**:
    - Request arrives on event loop thread
    - Non-blocking parsing of headers/body
    - Dispatch to handler
    - Async processing chain
    - Non-blocking response writing

2. **Backpressure Support**:
    - Built into Reactor types
    - Controls data flow from producer to consumer

3. **Error Handling**:
    - Special `onError*` operators in Reactor
    - Global error handlers via `@ControllerAdvice`

## Configuration

Configured through:
- `WebFluxConfigurer` interface
- `@EnableWebFlux` annotation
- Functional registration via `RouterFunction`

## Performance Characteristics

- Low thread count (not 1:1 per request)
- High concurrency with limited resources
- Better for I/O-bound operations

## Example Internal Flow

```txt
// Simplified sequence:
1. NettyWorker receives request
2. Creates ServerHttpRequest/Response wrappers
3. Passes to HttpHandler (usually WebHttpHandlerBuilder)
4. Filters execute (e.g., WebFilter chain)
5. DispatcherHandler finds matching @Controller
6. HandlerAdapter invokes controller method
7. Returned Publisher (Mono/Flux) is subscribed to
8. Response is written asynchronously
```

The implementation maximizes non-blocking operations throughout the entire stack, from HTTP parsing to business logic execution to response writing.