# Complete Example of Multi-architecture (multiarch) Build with Docker Buildx on macOS

Here is a complete example of using Docker Buildx for multi-architecture builds on macOS, targeting the construction of an image that supports both `linux/amd64` and `linux/arm64` architectures, and pushing the results to Docker Hub. You can run this example on macOS (including Intel or Apple Silicon chips).

### Example: Building a Simple Multi-architecture Image

#### Prerequisites
1. **Install Docker Desktop**: Ensure you have the latest version of Docker Desktop installed (supports Buildx and QEMU).
2. **Docker Hub Account**: You need a Docker Hub account to push images (or use another container registry).
3. **Login to Docker Hub**:
   ```bash
   docker login
   ```
   Enter your Docker Hub username and password.

#### Steps

1. **Create Project Directory**:
   ```bash
   mkdir multiarch-example
   cd multiarch-example
   ```

2. **Create Dockerfile**:
   Create a simple `Dockerfile` using `alpine` as the base image (supports multi-architecture):
   ```Dockerfile
   # Dockerfile
   FROM --platform=$BUILDPLATFORM alpine:latest
   RUN echo "Running on $(uname -m)" > /hello.txt
   CMD ["cat", "/hello.txt"]
   ```
    - `FROM --platform=$BUILDPLATFORM alpine:latest` ensures using the build platform's architecture.
    - `uname -m` outputs architecture information (like `x86_64` or `aarch64`).

3. **Enable Buildx and Set Up QEMU**:
    - Create a new Buildx builder:
      ```bash
      docker buildx create --name mybuilder --use
      ```
    - Start the builder and check status:
      ```bash
      docker buildx inspect --bootstrap
      ```
    - Install QEMU emulator (usually Docker Desktop already includes this, but run the following command to ensure multi-architecture support):
      ```bash
      docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
      ```

4. **Execute Multi-architecture Build and Push**:
   Assuming your Docker Hub username is `yourusername`, run the following command to build and push the image:
   ```bash
   docker buildx build \
     --platform linux/amd64,linux/arm64 \
     -t yourusername/multiarch-example:latest \
     --push .
   ```
    - `--platform linux/amd64,linux/arm64`: Specify target architectures.
    - `-t yourusername/multiarch-example:latest`: Set image name and tag.
    - `--push`: Push the built image to Docker Hub.
    - `.`: Specify current directory (contains `Dockerfile`).

5. **Verify Image**:
   Check if the pushed image supports multi-architecture:
   ```bash
   docker buildx imagetools inspect yourusername/multiarch-example:latest
   ```
   Output will show supported architectures, for example:
   ```
   Name:      yourusername/multiarch-example:latest
   MediaType: application/vnd.oci.image.index.v1+json
   Digest:    sha256:...
   ...
   Platform:  linux/amd64
   Platform:  linux/arm64
   ```

6. **Test Image** (Optional):
    - Run the image locally (uses native architecture by default, e.g., `arm64` on Apple Silicon):
      ```bash
      docker run --rm yourusername/multiarch-example:latest
      ```
      Example output: `Running on aarch64` (or `x86_64` depending on your macOS architecture).
    - To test other architectures, you can pull and run the image on a machine that supports the target architecture, or use Docker's `--platform` parameter (requires QEMU support):
      ```bash
      docker run --rm --platform linux/amd64 yourusername/multiarch-example:latest
      ```

#### Output Example
Assuming you run on an Apple Silicon Mac, after successful build and push, running the image might give:
- Local run (`arm64`):
  ```
  Running on aarch64
  ```
- Run with `--platform linux/amd64`:
  ```
  Running on x86_64
  ```

#### Notes
- **Docker Hub Replacement**: Replace `yourusername` with your Docker Hub username. If using other registries (like GitHub Container Registry), adjust the image name (e.g., `ghcr.io/yourusername/multiarch-example`).
- **Local Save**: If you don't want to push the image to a registry, you can replace `--push` with `--output type=local,dest=./output`:
  ```bash
  docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t multiarch-example:latest \
    --output type=local,dest=./output .
  ```
  This will save the image to the `./output` directory.
- **Performance**: QEMU emulation may cause slower builds, especially for complex images. Ensure Docker Desktop allocates sufficient CPU and memory (adjust in Docker Desktop settings).
- **Apple Silicon**: On M1/M2 Macs, `arm64` builds are native, while `amd64` builds rely on QEMU emulation, but Docker Desktop usually handles this well.

#### Cleanup
After building, clean up the Buildx builder (optional):
```bash
docker buildx rm mybuilder
```

### Common Issues
- **Error: QEMU not registered**: Re-run `docker run --privileged multiarch/qemu-user-static --reset -p yes`.
- **Push failed**: Ensure you're logged into Docker Hub (`docker login`) and the image name is correct.
- **Slow build**: Check Docker Desktop resource allocation, or simplify the Dockerfile.

This example demonstrates the complete process of building multi-architecture images with Docker Buildx on macOS. If you need a more complex Dockerfile or specific architecture support, let me know and I can further customize the example!