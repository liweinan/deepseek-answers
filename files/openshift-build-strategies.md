# OpenShift的构建策略

在OpenShift中，`Source Strategy` 和 `Docker Strategy` 是两种不同的构建策略，用于从源代码或 Docker 镜像构建应用。以下是它们的区别：

### 1. Source Strategy
- **定义**：从源代码构建应用。
- **适用场景**：适用于有源代码且需在构建过程中编译或打包的项目。
- **构建过程**：
    - 拉取源代码（如 Git 仓库）。
    - 使用指定的构建器镜像（如 S2I，Source-to-Image）编译代码。
    - 生成最终的应用镜像并推送到镜像仓库。
- **优点**：
    - 自动化编译和打包。
    - 支持多种语言和框架。
- **示例**：
  ```yaml
  strategy:
    sourceStrategy:
      from:
        kind: "ImageStreamTag"
        name: "python:3.8"
  ```

### 2. Docker Strategy
- **定义**：基于现有 Dockerfile 构建应用镜像。
- **适用场景**：已有 Dockerfile 或需完全控制构建过程的项目。
- **构建过程**：
    - 使用提供的 Dockerfile 构建镜像。
    - 生成的镜像推送到镜像仓库。
- **优点**：
    - 完全控制构建过程。
    - 适合复杂构建需求。
- **示例**：
  ```yaml
  strategy:
    dockerStrategy:
      dockerfilePath: "Dockerfile"
  ```

### 主要区别
- **输入**：Source Strategy 使用源代码，Docker Strategy 使用 Dockerfile。
- **构建过程**：Source Strategy 依赖构建器镜像，Docker Strategy 直接使用 Dockerfile。
- **灵活性**：Docker Strategy 提供更高灵活性，Source Strategy 更自动化。

### 选择依据
- 选择 **Source Strategy**：有源代码且希望自动化构建。
- 选择 **Docker Strategy**：已有 Dockerfile 或需要完全控制构建过程。

根据项目需求选择合适的策略。