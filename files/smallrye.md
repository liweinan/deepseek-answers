# SmallRye 是一个开源项目，专注于为云原生开发提供轻量级 Java 库和工具，主要实现 Eclipse MicroProfile 规范的各种 API，同时也提供一些独立的功能扩展。它旨在提升开发者的云环境开发体验，适用于容器化部署，并与 Quarkus、WildFly、Open Liberty 和 TomEE 等运行时或应用服务器集成，也可作为独立库在任何 Java 应用中使用。以下是 SmallRye 的核心特点和组件概述：

### 核心特点
1. **MicroProfile 规范实现**：SmallRye 提供 Eclipse MicroProfile 规范的实现，例如 Config、Metrics、Health、OpenAPI、Fault Tolerance 和 JWT 等，遵循微服务架构的标准。
2. **云原生优化**：专为容器环境设计，支持轻量级运行时，适合 Kubernetes 和其他云平台。
3. **灵活性**：既可与 Quarkus 等框架深度集成，也可独立使用，适配多种 Java 应用场景。
4. **开源社区驱动**：采用 Apache 2.0 许可证，托管在 GitHub，鼓励社区贡献，包括 bug 报告、功能请求和文档改进。[](https://smallrye.io/)[](https://github.com/smallrye)
5. **现代化技术**：支持 reactive 编程（通过 SmallRye Mutiny）、服务发现（SmallRye Stork）等现代开发需求。

### 主要组件
SmallRye 包含多个子项目，覆盖配置、监控、通信等开发需求，以下是部分关键组件：
- **SmallRye Config**：一个灵活的配置库，遵循 MicroProfile Config 规范，支持环境变量、属性文件等配置源，并扩展了更高级的配置功能。[](https://github.com/smallrye/smallrye-config)[](https://smallrye.io/smallrye-config/Main/)
- **SmallRye Metrics**：实现 MicroProfile Metrics 规范，用于监控应用性能指标。[](https://github.com/smallrye/smallrye-metrics)
- **SmallRye Health**：提供健康检查功能，支持 MicroProfile Health 规范，用于报告应用状态。[](https://mvnrepository.com/artifact/io.smallrye)
- **SmallRye Fault Tolerance**：实现 MicroProfile Fault Tolerance 规范，支持重试、超时、断路器等容错模式，早期基于 Hystrix，现已优化。[](https://quarkus.io/blog/tag/smallrye/)
- **SmallRye OpenAPI**：实现 MicroProfile OpenAPI 规范，自动生成 OpenAPI 文档。[](https://github.com/smallrye/smallrye-open-api)
- **SmallRye Mutiny**：一个直观的事件驱动 reactive 编程库，支持 Java Flow API，已从 Reactive Streams 升级到现代 API。[](https://github.com/smallrye/smallrye-mutiny)[](https://groups.google.com/g/smallrye)
- **SmallRye Stork**：服务发现和客户端负载均衡框架，简化微服务通信。[](https://github.com/smallrye)
- **SmallRye Reactive Messaging**：支持异步消息处理，集成 Kafka、AMQP、MQTT 等协议。[](https://groups.google.com/g/smallrye)
- **SmallRye JWT**：实现 JWT 认证和授权，支持 MicroProfile JWT 规范。[](https://groups.google.com/g/smallrye)
- **SmallRye Common**：提供通用工具和 BOM（Bill of Materials），简化依赖管理。[](https://github.com/smallrye/smallrye-common)
- **SmallRye LLM**：一个新兴项目，探索与大语言模型相关的功能（具体细节尚在发展）。[](https://groups.google.com/g/smallrye)

### 使用场景
- **微服务开发**：通过 MicroProfile 实现，SmallRye 提供标准化的微服务功能，如配置管理、监控和容错。
- **云原生应用**：与 Quarkus 等框架结合，SmallRye 优化了应用的启动时间和内存占用，适合容器化部署。
- **独立库**：开发者可选择单个 SmallRye 组件（如 SmallRye Config 或 Mutiny）用于非 MicroProfile 项目。

### 如何开始
1. **添加依赖**：通过 Maven 或 Gradle 添加所需 SmallRye 模块，例如：
   ```xml
   <dependency>
       <groupId>io.smallrye.config</groupId>
       <artifactId>smallrye-config</artifactId>
       <version>3.12.5-SNAPSHOT</version>
   </dependency>
   ```
   可使用 `smallrye-common-bom` 管理版本。[](https://github.com/smallrye/smallrye-common)[](https://smallrye.io/smallrye-config/Main/)
2. **访问文档**：SmallRye 官网 (smallrye.io) 提供详细的子项目文档和使用指南。[](https://smallrye.io/)
3. **加入社区**：通过 GitHub (github.com/smallrye) 或 Google Groups 参与贡献，提交 issue 或 PR。[](https://github.com/smallrye)[](https://groups.google.com/g/smallrye)

### 最新动态
- 部分组件已计划支持 Java 17 作为最低版本，反映了现代化趋势。[](https://groups.google.com/g/smallrye)
- SmallRye JWT 持续更新，最新版本（如 3.6.1）已支持 Jakarta IdentityStore 集成。[](https://groups.google.com/g/smallrye)
- SmallRye Health 和 Fault Tolerance 的最新发布分别在 2025 年 1 月和 4 月，保持活跃开发。[](https://mvnrepository.com/artifact/io.smallrye)

### 总结
SmallRye 是一个功能丰富、轻量灵活的 Java 生态项目，特别适合云原生和微服务开发。它通过实现 MicroProfile 规范并提供扩展功能，简化了开发者的工作，同时保持开源社区的活力。无论是构建 Quarkus 应用还是独立 Java 项目，SmallRye 都是值得考虑的工具集。

更多信息可访问 [SmallRye 官网](https://smallrye.io) 或 [GitHub 组织](https://github.com/smallrye)。[](https://smallrye.io/)[](https://github.com/smallrye

---

```mermaid
classDiagram
    class SmallRye {
        +Core Modules
        +Extensions
    }

%% Core Modules
    class SmallRye_Config {
        +Configuration Management
        +MicroProfile Config
    }
    class SmallRye_Metrics {
        +Performance Monitoring
        +MicroProfile Metrics
    }
    class SmallRye_Health {
        +Health Checks
        +MicroProfile Health
    }
    class SmallRye_FaultTolerance {
        +Retry, Timeout, Circuit Breaker
        +MicroProfile Fault Tolerance
    }
    class SmallRye_OpenAPI {
        +API Documentation
        +MicroProfile OpenAPI
    }
    class SmallRye_JWT {
        +Authentication & Authorization
        +MicroProfile JWT
    }

%% Extension Modules
    class SmallRye_Mutiny {
        +Reactive Programming
        +Java Flow API
    }
    class SmallRye_Stork {
        +Service Discovery
        +Client Load Balancing
    }
    class SmallRye_ReactiveMessaging {
        +Asynchronous Messaging
        +Kafka, AMQP, MQTT
    }
    class SmallRye_Common {
        +Utilities
        +BOM for Dependency Management
    }
    class SmallRye_LLM {
        +Large Language Model Exploration
        +Experimental
    }

%% Relationships
    SmallRye --> SmallRye_Config : Contains
    SmallRye --> SmallRye_Metrics : Contains
    SmallRye --> SmallRye_Health : Contains
    SmallRye --> SmallRye_FaultTolerance : Contains
    SmallRye --> SmallRye_OpenAPI : Contains
    SmallRye --> SmallRye_JWT : Contains
    SmallRye --> SmallRye_Mutiny : Contains
    SmallRye --> SmallRye_Stork : Contains
    SmallRye --> SmallRye_ReactiveMessaging : Contains
    SmallRye --> SmallRye_Common : Contains
    SmallRye --> SmallRye_LLM : Contains

%% Dependencies
    SmallRye_Config --> SmallRye_Common : Uses
    SmallRye_JWT --> SmallRye_Config : Uses
    SmallRye_FaultTolerance --> SmallRye_Config : Uses
    SmallRye_ReactiveMessaging --> SmallRye_Mutiny : Uses
    SmallRye_Stork --> SmallRye_Config : Uses
```