# OpenShift Build Strategies

In OpenShift, `Source Strategy` and `Docker Strategy` are two different build strategies used to build applications from source code or Docker images. Here are their differences:

### 1. Source Strategy
- **Definition**: Build applications from source code.
- **Applicable Scenarios**: Suitable for projects with source code that need to be compiled or packaged during the build process.
- **Build Process**:
    - Pull source code (like Git repository).
    - Compile code using specified builder image (like S2I, Source-to-Image).
    - Generate final application image and push to image registry.
- **Advantages**:
    - Automated compilation and packaging.
    - Support for multiple languages and frameworks.
- **Example**:
  ```yaml
  strategy:
    sourceStrategy:
      from:
        kind: "ImageStreamTag"
        name: "python:3.8"
  ```

### 2. Docker Strategy
- **Definition**: Build application image based on existing Dockerfile.
- **Applicable Scenarios**: Projects that already have Dockerfile or need complete control over the build process.
- **Build Process**:
    - Build image using provided Dockerfile.
    - Push generated image to image registry.
- **Advantages**:
    - Complete control over build process.
    - Suitable for complex build requirements.
- **Example**:
  ```yaml
  strategy:
    dockerStrategy:
      dockerfilePath: "Dockerfile"
  ```

### Main Differences
- **Input**: Source Strategy uses source code, Docker Strategy uses Dockerfile.
- **Build Process**: Source Strategy depends on builder image, Docker Strategy directly uses Dockerfile.
- **Flexibility**: Docker Strategy provides higher flexibility, Source Strategy is more automated.

### Selection Criteria
- Choose **Source Strategy**: Have source code and want automated builds.
- Choose **Docker Strategy**: Already have Dockerfile or need complete control over build process.

Choose the appropriate strategy based on project requirements.