# 在本地主机 Kubernetes 集群上部署 Prow（使用 NodePort）

本教程指导你在本地主机 Kubernetes 集群上部署 Prow，使用 `NodePort` 暴露服务，GitHub 可访问本地主机端口，无需 Google Cloud Storage 配置。

## 前提条件
- 本地主机运行的 Kubernetes 集群（如 Minikube）。
- 已安装 `kubectl` 和 `git`。
- GitHub 账户和组织，用于创建 GitHub App。
- 本地主机 IP 可被 GitHub 访问（例如通过端口转发）。

## 步骤 1：创建 GitHub App
1. 登录 GitHub，访问 [GitHub App 创建页面](https://github.com/settings/apps/new)。
2. 填写 App 名称（例如 `my-prow-bot`），Webhook URL 暂时设为 `http://example.com`（稍后更新）。
3. 配置权限：
    - Administration: Read-Only
    - Checks: Read-Only
    - Contents: Read & Write
    - Issues: Read & Write
    - Pull Requests: Read & Write
    - Metadata: Read-Only
4. 保存后，记录 **App ID** 和 **Webhook Secret**。
5. 生成并下载私钥（`.pem` 文件）。

## 步骤 2：准备 Kubernetes 集群
1. 创建 Prow 命名空间：
   ```bash
   kubectl create namespace prow
   ```

## 步骤 3：配置 Prow 的 Secrets
1. 生成 HMAC 令牌：
   ```bash
   openssl rand -hex 20 > /path/to/hook/secret
   ```
2. 创建 Secrets：
   ```bash
   kubectl create secret -n prow generic hmac-token --from-file=hmac=/path/to/hook/secret
   kubectl create secret -n prow generic github-token --from-file=app_private_key=/path/to/private-key.pem --from-literal=app_id=<your-app-id>
   ```

## 步骤 4：部署 Prow 组件（使用 NodePort）
1. 下载 `100_starter.yaml`：
   ```bash
   curl -O https://raw.githubusercontent.com/kubernetes-sigs/prow/main/test/integration/config/prow/cluster/100_starter.yaml
   ```
2. 修改 `100_starter.yaml` 中的服务配置为 `NodePort`：
    - 编辑 Hook 服务（确保服务名为 `hook`）：
      ```yaml
      apiVersion: v1
      kind: Service
      metadata:
        name: hook
        namespace: prow
      spec:
        selector:
          app: hook
        ports:
        - port: 8888
          targetPort: 8888
          nodePort: 30001
        type: NodePort
      ```
    - 编辑 Deck 服务（确保服务名为 `deck`）：
      ```yaml
      apiVersion: v1
      kind: Service
      metadata:
        name: deck
        namespace: prow
      spec:
        selector:
          app: deck
        ports:
        - port: 80
          targetPort: 80
          nodePort: 30002
        type: NodePort
      ```
3. 应用配置文件：
   ```bash
   kubectl apply -f 100_starter.yaml
   ```
4. 验证 Prow 组件运行：
   ```bash
   kubectl get pods -n prow
   ```
   确保所有 Pod 状态为 `Running`。

## 步骤 5：配置 GitHub Webhook
1. 获取本地主机 IP（例如 `192.168.1.100`）。
2. 返回 GitHub App 设置页面，更新 Webhook URL 为 `http://<your-local-ip>:30001/hook`（例如 `http://192.168.1.100:30001/hook`）。
3. 将 Webhook Secret 设置为 `/path/to/hook/secret` 中的值。
4. 选择事件：Push、Pull Request、Issue Comment。

## 步骤 6：配置 Prow 作业
1. 在你的 GitHub 仓库中创建 `prow-jobs.yaml`，定义作业。例如：
   ```yaml
   presubmits:
     your-org/your-repo:
     - name: unit-test
       always_run: true
       decorate: true
       spec:
         containers:
         - image: golang:1.18
           command:
           - go
           args:
           - test
   ```
2. 提交到仓库根目录。

## 步骤 7：测试和验证
1. 触发一个 Pull Request，检查 Prow 是否运行作业。
2. 访问 Deck 仪表板：`http://<your-local-ip>:30002`（例如 `http://192.168.1.100:30002`），查看作业状态。
3. 检查 Hook 是否收到 Webhook：
   ```bash
   kubectl logs -n prow -l app=hook
   ```

## 故障排除
- **Webhook 失败**：确保 `30001` 端口可被 GitHub 访问，检查防火墙设置。
- **Deck 无法访问**：确认 `30002` 端口未被占用，Pod 状态正常。
- **作业未运行**：检查 `prow-jobs.yaml` 语法，确保存储库权限正确。



### 说明
- **NodePort 配置**：Hook 使用 `30001` 端口（映射到 `8888`），Deck 使用 `30002` 端口（映射到 `80`），适合本地主机部署。
- **移除 Google 相关配置**：教程中已移除 Google Cloud Storage 和相关服务账户配置。
- **简洁性**：教程聚焦核心步骤，适合快速部署。

如需进一步调整或帮助，请告诉我！

---

以下是基于上述教程（在本地主机 Kubernetes 集群上部署 Prow，使用 `NodePort` 配置方式）的 Mermaid 部署架构图。图中包含了教程中的核心组件和交互关系，去除了 Google Cloud Storage 相关部分，并明确了 `NodePort` 的端口暴露。

### Mermaid 部署架构图

```mermaid
graph TD
    subgraph GitHub
        A[GitHub App] -->|Webhook| B[GitHub Webhook]
    end

    subgraph Localhost Kubernetes Cluster
        subgraph Prow Namespace
            C[Hook<br>NodePort: 30001] -->|Receives Webhook| D[Plank]
            D -->|Manages Jobs| E[Deck<br>NodePort: 30002]
            D -->|Cleans Resources| F[Sinker]
            G[Secrets<br>hmac-token<br>github-token] --> C
            G --> D
        end
        I[Prow Job Config<br>prow-jobs.yaml] --> D
    end

    B -->|Sends Events<br>http://<local-ip>:30001/hook| C
    subgraph User
        J[Browser] -->|Access Dashboard<br>http://<local-ip>:30002| E
    end
```

### 图表说明
1. **GitHub 部分**：
    - `GitHub App` 通过 `GitHub Webhook` 发送事件到 Prow 的 Hook 组件。
    - Webhook URL 配置为 `http://<local-ip>:30001/hook`，对应 Hook 的 `NodePort` 端口 `30001`。

2. **Kubernetes 集群（本地主机）**：
    - 所有 Prow 组件运行在 `prow` 命名空间内。
    - `Hook` 接收 Webhook 事件，暴露在 `NodePort: 30001`（映射到服务端口 `8888`）。
    - `Plank` 管理作业，基于 `prow-jobs.yaml` 配置。
    - `Deck` 提供仪表板，暴露在 `NodePort: 30002`（映射到服务端口 `80`），供用户通过浏览器访问。
    - `Sinker` 清理资源，无需外部访问。
    - `Secrets`（`hmac-token` 和 `github-token`）用于身份验证。

3. **用户访问**：
    - 用户通过浏览器访问 Deck 仪表板，URL 为 `http://<local-ip>:30002`。

### 渲染方式
- 你可以将上述 Mermaid 代码粘贴到支持 Mermaid 的工具中（如 GitHub Markdown 或 Mermaid Live Editor：https://mermaid.live/）来渲染图表。

如果需要调整图表样式或添加更多细节，请告诉我！

---

# 好的！由于你的主机有公网 IP 和独立域名，并且可以部署 Nginx 配合 HTTPS，这确实为 Prow 的部署带来了优势。以下我会分析这些优势，调整教程以使用 Nginx Ingress 和 HTTPS，并将更新后的 Mermaid 图整合到教程中。

### 部署优势分析
1. **公网 IP 和独立域名的优势**：
    - **可访问性**：公网 IP 使 GitHub Webhook 和用户浏览器可以直接访问你的 Prow 服务，无需额外的端口转发或工具（如 UltraHook）。
    - **域名管理**：独立域名（例如 `prow.yourdomain.com`）可以为 Prow 的不同组件（如 Hook 和 Deck）分配子域名（如 `hook.prow.yourdomain.com` 和 `deck.prow.yourdomain.com`），更易于管理和访问。

2. **Nginx Ingress 的优势**：
    - **统一入口**：Nginx Ingress 控制器提供一个统一的入口点，通过域名路由到不同的 Prow 服务（Hook、Deck 等），无需为每个服务单独暴露 `NodePort`。
    - **负载均衡**：Nginx Ingress 提供简单的负载均衡功能，适合生产环境。
    - **可扩展性**：可以轻松为其他服务添加路由规则。

3. **HTTPS 的优势**：
    - **安全性**：HTTPS 确保 GitHub Webhook 和用户浏览器与 Prow 服务的通信是加密的，保护数据安全。
    - **合规性**：GitHub Webhook 更推荐使用 HTTPS 端点，许多生产环境要求 HTTPS。

### 调整后的教程
以下是调整后的教程，使用 Nginx Ingress 和 HTTPS 部署 Prow，移除 `NodePort` 配置，改为通过域名访问服务。



# 在本地主机 Kubernetes 集群上部署 Prow（使用 Nginx 和 HTTPS）

本教程指导你在本地主机 Kubernetes 集群上部署 Prow，使用公网 IP 和独立域名，通过 Nginx Ingress 控制器暴露服务，并启用 HTTPS。

## 前提条件
- 本地主机运行的 Kubernetes 集群（如 Minikube）。
- 已安装 `kubectl` 和 `git`。
- GitHub 账户和组织，用于创建 GitHub App。
- 本地主机有公网 IP（例如 `203.0.113.10`）。
- 独立域名（例如 `prow.yourdomain.com`），DNS 已配置指向公网 IP。
- 已安装 `cert-manager` 用于自动获取 HTTPS 证书（或手动准备 TLS 证书）。

## 步骤 1：创建 GitHub App
1. 登录 GitHub，访问 [GitHub App 创建页面](https://github.com/settings/apps/new)。
2. 填写 App 名称（例如 `my-prow-bot`），Webhook URL 暂时设为 `https://hook.prow.yourdomain.com/hook`（稍后验证）。
3. 配置权限：
    - Administration: Read-Only
    - Checks: Read-Only
    - Contents: Read & Write
    - Issues: Read & Write
    - Pull Requests: Read & Write
    - Metadata: Read-Only
4. 保存后，记录 **App ID** 和 **Webhook Secret**。
5. 生成并下载私钥（`.pem` 文件）。

## 步骤 2：准备 Kubernetes 集群
1. 创建 Prow 命名空间：
   ```bash
   kubectl create namespace prow
   ```

## 步骤 3：配置 Prow 的 Secrets
1. 生成 HMAC 令牌：
   ```bash
   openssl rand -hex 20 > /path/to/hook/secret
   ```
2. 创建 Secrets：
   ```bash
   kubectl create secret -n prow generic hmac-token --from-file=hmac=/path/to/hook/secret
   kubectl create secret -n prow generic github-token --from-file=app_private_key=/path/to/private-key.pem --from-literal=app_id=<your-app-id>
   ```

## 步骤 4：安装 Nginx Ingress 控制器
1. 安装 Nginx Ingress 控制器：
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/baremetal/deploy.yaml
   ```
2. 验证控制器运行：
   ```bash
   kubectl get pods -n ingress-nginx
   ```
3. 获取 Nginx Ingress 的外部 IP（通常是主机的公网 IP `203.0.113.10`）：
   ```bash
   kubectl get svc -n ingress-nginx
   ```

## 步骤 5：配置 HTTPS（使用 cert-manager）
1. 安装 cert-manager（用于自动获取 Let's Encrypt 证书）：
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.3/cert-manager.yaml
   ```
2. 创建 ClusterIssuer 用于 Let's Encrypt：
   ```yaml
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-prod
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: your-email@example.com
       privateKeySecretRef:
         name: letsencrypt-prod
       solvers:
       - http01:
           ingress:
             class: nginx
   ```
   应用：
   ```bash
   kubectl apply -f clusterissuer.yaml
   ```

## 步骤 6：部署 Prow 组件
1. 下载 `100_starter.yaml`：
   ```bash
   curl -O https://raw.githubusercontent.com/kubernetes-sigs/prow/main/test/integration/config/prow/cluster/100_starter.yaml
   ```
2. 确保服务类型为 `ClusterIP`（默认即可，Nginx Ingress 会处理外部访问）。
3. 应用配置文件：
   ```bash
   kubectl apply -f 100_starter.yaml
   ```
4. 验证 Prow 组件运行：
   ```bash
   kubectl get pods -n prow
   ```

## 步骤 7：配置 Ingress 资源
1. 创建 Ingress 资源，使用子域名路由到 Hook 和 Deck：
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: prow-ingress
     namespace: prow
     annotations:
       nginx.ingress.kubernetes.io/rewrite-target: /
       cert-manager.io/cluster-issuer: letsencrypt-prod
   spec:
     ingressClassName: nginx
     tls:
     - hosts:
       - hook.prow.yourdomain.com
       - deck.prow.yourdomain.com
       secretName: prow-tls
     rules:
     - host: hook.prow.yourdomain.com
       http:
         paths:
         - path: /hook
           pathType: Prefix
           backend:
             service:
               name: hook
               port:
                 number: 8888
     - host: deck.prow.yourdomain.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: deck
               port:
                 number: 80
   ```
2. 应用 Ingress 配置：
   ```bash
   kubectl apply -f prow-ingress.yaml
   ```

## 步骤 8：配置 DNS
1. 在你的域名提供商处，添加以下 DNS 记录：
   ```
   hook.prow.yourdomain.com  A  203.0.113.10
   deck.prow.yourdomain.com  A  203.0.113.10
   ```

## 步骤 9：配置 GitHub Webhook
1. 返回 GitHub App 设置页面，更新 Webhook URL 为 `https://hook.prow.yourdomain.com/hook`。
2. 将 Webhook Secret 设置为 `/path/to/hook/secret` 中的值。
3. 选择事件：Push、Pull Request、Issue Comment。

## 步骤 10：配置 Prow 作业
1. 在你的 GitHub 仓库中创建 `prow-jobs.yaml`：
   ```yaml
   presubmits:
     your-org/your-repo:
     - name: unit-test
       always_run: true
       decorate: true
       spec:
         containers:
         - image: golang:1.18
           command:
           - go
           args:
           - test
   ```
2. 提交到仓库根目录。

## 步骤 11：测试和验证
1. 触发一个 Pull Request，检查 Prow 是否运行作业。
2. 访问 Deck 仪表板：`https://deck.prow.yourdomain.com`，查看作业状态。
3. 检查 Hook 日志：
   ```bash
   kubectl logs -n prow -l app=hook
   ```

## 部署架构图
以下是部署架构图，使用 Mermaid 绘制：

```mermaid
graph TD
    subgraph GitHub
        A[GitHub App] -->|Webhook| B[GitHub Webhook]
    end

    subgraph Localhost Kubernetes Cluster
        subgraph Ingress Controller
            K[Nginx Ingress<br>Public IP: 203.0.113.10] -->|HTTPS| L[hook.prow.yourdomain.com]
            K -->|HTTPS| M[deck.prow.yourdomain.com]
        end

        subgraph Prow Namespace
            L --> C[Hook]
            M --> E[Deck]
            C -->|Receives Webhook| D[Plank]
            D -->|Manages Jobs| E
            D -->|Cleans Resources| F[Sinker]
            G[Secrets<br>hmac-token<br>github-token] --> C
            G --> D
        end
        I[Prow Job Config<br>prow-jobs.yaml] --> D
    end

    B -->|Sends Events<br>https://hook.prow.yourdomain.com/hook| L
    subgraph User
        J[Browser] -->|Access Dashboard<br>https://deck.prow.yourdomain.com| M
    end
```

## 故障排除
- **Webhook 失败**：确保 DNS 解析正确，HTTPS 证书有效，端口 443 可访问。
- **Deck 无法访问**：检查 Ingress 配置，确保存储库权限正确。
- **证书问题**：查看 cert-manager 日志：
  ```bash
  kubectl logs -n cert-manager -l app=cert-manager
  ```



### 调整说明
1. **Nginx 和 HTTPS**：
    - 使用 Nginx Ingress 控制器统一管理外部访问，通过子域名（`hook.prow.yourdomain.com` 和 `deck.prow.yourdomain.com`）路由到 Hook 和 Deck。
    - 使用 `cert-manager` 自动获取 Let's Encrypt 证书，实现 HTTPS。

2. **移除 NodePort**：
    - 不再需要 `NodePort` 配置，服务保持默认的 `ClusterIP` 类型，Nginx Ingress 负责外部访问。

3. **Mermaid 图更新**：
    - 添加了 Nginx Ingress 控制器，显示通过公网 IP 和子域名访问。
    - 明确了 HTTPS 通信路径，移除 `NodePort` 相关标注。

如果需要进一步调整或更详细的配置（例如手动 TLS 证书），请告诉我！