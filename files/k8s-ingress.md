# 在本机通过 **Ingress** 访问 **Service** 服务，通常涉及 **Kubernetes (K8s)** 环境。以下是详细步骤，假设你已经在本地运行了一个 Kubernetes 集群（如 Minikube、Kind 或 Docker Desktop K8s）。

---

## **1. 确保 Kubernetes 环境就绪**
首先，确认你的 Kubernetes 集群正常运行，并安装了 **Ingress Controller**（如 Nginx Ingress、Traefik 等）。

### **1.1 检查集群状态**
```bash
kubectl cluster-info
kubectl get nodes
```

### **1.2 安装 Ingress Controller**
#### **Minikube**
```bash
minikube addons enable ingress
```
#### **Docker Desktop / Kind**
安装 Nginx Ingress：
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```
等待 Ingress Controller 就绪：
```bash
kubectl get pods -n ingress-nginx
```

---

## **2. 部署示例 Service**
假设我们要访问一个简单的 `nginx` 服务。

### **2.1 创建 Deployment**
```bash
kubectl create deployment nginx --image=nginx
```

### **2.2 创建 Service**
```bash
kubectl expose deployment nginx --port=80
```
检查 Service：
```bash
kubectl get svc nginx
```
输出示例：
```
NAME    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
nginx   ClusterIP   10.96.123.123   <none>        80/TCP    10s
```

---

## **3. 创建 Ingress 规则**
Ingress 定义如何将外部流量路由到 Service。

### **3.1 编写 Ingress YAML**
创建 `ingress.yaml`：
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
spec:
  rules:
  - host: nginx.local  # 本地测试域名
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
```

### **3.2 应用 Ingress**
```bash
kubectl apply -f ingress.yaml
```
检查 Ingress：
```bash
kubectl get ingress
```
输出示例：
```
NAME           CLASS   HOSTS         ADDRESS        PORTS   AGE
nginx-ingress  nginx   nginx.local   192.168.49.2   80      10s
```

---

## **4. 本地访问 Service**
由于 Ingress 通常绑定到一个域名（如 `nginx.local`），我们需要在本地配置 hosts 解析。

### **4.1 获取 Ingress 的 IP**
```bash
kubectl get ingress nginx-ingress
```
输出示例：
```
NAME           CLASS   HOSTS         ADDRESS        PORTS   AGE
nginx-ingress  nginx   nginx.local   192.168.49.2   80      10s
```
这里的 `ADDRESS`（如 `192.168.49.2`）是 Ingress Controller 的 IP。

### **4.2 修改本地 hosts 文件**
- **Linux/Mac**：
  ```bash
  sudo echo "192.168.49.2 nginx.local" >> /etc/hosts
  ```
- **Windows**（管理员权限）：
  ```powershell
  Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "192.168.49.2 nginx.local"
  ```

### **4.3 访问服务**
现在，你可以在浏览器或终端访问：
```bash
curl http://nginx.local
```
或直接在浏览器打开：
```
http://nginx.local
```
应该能看到 Nginx 的欢迎页面。

---

## **5. 可选：使用端口转发（无 Ingress）**
如果不想配置 Ingress，可以直接用 `kubectl port-forward`：
```bash
kubectl port-forward svc/nginx 8080:80
```
然后访问：
```
http://localhost:8080
```

---

## **6. 清理资源**
```bash
kubectl delete ingress nginx-ingress
kubectl delete svc nginx
kubectl delete deployment nginx
```

---

## **总结**
| 步骤 | 操作 |
|------|------|
| 1. 启动 K8s 集群 | `minikube start` 或 `kind create cluster` |
| 2. 安装 Ingress Controller | `minikube addons enable ingress` |
| 3. 部署 Service | `kubectl create deployment` + `kubectl expose` |
| 4. 创建 Ingress | `kubectl apply -f ingress.yaml` |
| 5. 修改本地 hosts | `echo "IP nginx.local" >> /etc/hosts` |
| 6. 访问服务 | `curl http://nginx.local` |

这样，你就可以在本地通过 Ingress 访问 Kubernetes Service 了！🚀


---

# # 解决 Ingress-Nginx Controller 的 External-IP 显示为 Pending 的问题

当您的 `ingress-nginx-controller` Service 的 `EXTERNAL-IP` 显示为 `<pending>` 时，这通常是因为您的 Kubernetes 环境没有可用的外部负载均衡器。以下是详细解决方案：

## 1. 问题原因分析

在本地开发环境（如 Minikube、Kind、K3s、MicroK8s 等）中，`LoadBalancer` 类型的 Service 默认无法自动获取外部 IP，因为：
- 本地环境通常没有云厂商的负载均衡器集成
- 需要额外组件来模拟负载均衡器行为

## 2. 解决方案（根据您的环境选择）

### 方案 A：使用 Minikube（如果您使用的是 Minikube）

```bash
minikube tunnel
```
在另一个终端中运行此命令，它会为 LoadBalancer 类型的 Service 分配外部 IP。

### 方案 B：使用 MetalLB（适用于 Kind/K3s/MicroK8s/裸金属集群）

1. 安装 MetalLB：
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.7/config/manifests/metallb-native.yaml
   ```

2. 配置 IP 地址池（修改以下配置后应用）：
   ```yaml
   apiVersion: metallb.io/v1beta1
   kind: IPAddressPool
   metadata:
     name: default-pool
     namespace: metallb-system
   spec:
     addresses:
     - 192.168.1.100-192.168.1.200  # 使用您的本地网络可用IP段
   ---
   apiVersion: metallb.io/v1beta1
   kind: L2Advertisement
   metadata:
     name: l2-advert
     namespace: metallb-system
   ```

3. 应用配置：
   ```bash
   kubectl apply -f metallb-config.yaml
   ```

### 方案 C：改用 NodePort（快速测试方案）

修改 ingress-nginx-controller 的 Service 类型：
```bash
kubectl patch svc ingress-nginx-controller -n ingress-nginx -p '{"spec":{"type":"NodePort"}}'
```
然后通过节点 IP 和分配的端口访问（如 `http://<node-ip>:30236`）。

### 方案 D：如果是 MicroK8s 用户

```bash
microk8s enable metallb
```
然后按照提示配置 IP 地址范围。

## 3. 验证解决方案

应用解决方案后，检查 Service 状态：
```bash
kubectl get svc -n ingress-nginx -w
```
等待 `EXTERNAL-IP` 从 `<pending>` 变为实际 IP 地址。

## 4. 访问您的 Ingress

获取到外部 IP 后：
1. 将您的域名（如 `nginx.local`）指向该 IP（修改 `/etc/hosts` 文件）
2. 访问您的服务：
   ```bash
   curl http://nginx.local
   ```

## 5. 常见问题排查

1. **MetalLB 未正确配置**：
   ```bash
   kubectl logs -n metallb-system -l app=metallb -c controller
   ```

2. **IP 地址池不可用**：
    - 确保配置的 IP 范围在您的本地网络中未被使用
    - 检查 ARP 响应：
      ```bash
      tcpdump -i any arp
      ```

3. **防火墙阻止**：
    - 确保您的防火墙允许流量通过分配的端口

## 6. 各环境推荐方案

| 环境        | 推荐方案                 | 备注                          |
|-------------|--------------------------|-------------------------------|
| Minikube    | `minikube tunnel`        | 最简单方案                    |
| Kind        | MetalLB                  | 需要额外安装                  |
| K3s         | MetalLB 或 Traefik       | K3s 自带 Traefik 可作为替代   |
| MicroK8s    | `microk8s enable metallb`| 内置支持                      |
| Docker Desktop | 无需操作             | 自动绑定到 localhost          |

选择适合您环境的解决方案后，Ingress-Nginx Controller 应该能够获取到外部 IP 地址。

---

# # 解决 Ingress 没有分配 ADDRESS 的问题

当您的 Ingress 资源没有显示 ADDRESS 时，通常是因为 Ingress Controller 没有正确安装或配置。以下是详细的排查和解决方案：

## 1. 确认 Ingress Controller 是否安装

首先检查您的集群是否安装了 Ingress Controller：

```bash
kubectl get pods -n ingress-nginx  # 如果是 Nginx Ingress Controller
# 或者
kubectl get pods -A | grep ingress
```

如果没有安装，您需要先安装 Ingress Controller。

## 2. 根据您的环境安装 Ingress Controller

### 对于 Minikube 用户

```bash
minikube addons enable ingress
```

等待几分钟后验证：
```bash
kubectl get pods -n ingress-nginx
```

### 对于 Docker Desktop (Mac/Windows)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

### 对于 Kind 或其他本地集群

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

## 3. 等待 Ingress Controller 就绪

安装后需要等待几分钟让 Ingress Controller 完全启动：

```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

## 4. 检查 Ingress Controller Service

查看 Ingress Controller 的 Service 是否分配了外部 IP：

```bash
kubectl get svc -n ingress-nginx
```

## 5. 特殊环境处理

### Minikube 特殊处理

Minikube 需要运行额外命令获取访问地址：

```bash
minikube tunnel
```

然后在另一个终端查看 Ingress：
```bash
kubectl get ingress
```

### Docker Desktop 特殊处理

Docker Desktop 的 Ingress 通常绑定到 `localhost`，您可以直接在 `/etc/hosts` 中添加：
```
127.0.0.1 nginx.local
```

## 6. 验证 Ingress 配置

检查您的 Ingress 资源详情：
```bash
kubectl describe ingress nginx-ingress
```

查看事件部分是否有错误信息。

## 7. 常见问题解决

1. **Ingress Class 未指定**：
   在较新版本的 Kubernetes 中，可能需要指定 Ingress Class：
   ```yaml
   metadata:
     annotations:
       kubernetes.io/ingress.class: "nginx"
   ```

2. **防火墙问题**：
   确保您的防火墙允许 Ingress Controller 的端口（通常是 80 和 443）。

3. **资源不足**：
   检查 Ingress Controller Pod 是否因为资源限制无法启动：
   ```bash
   kubectl describe pods -n ingress-nginx
   ```

## 8. 完整示例

一个完整的 Ingress 示例（包含 Ingress Class 注解）：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host: nginx.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
```

## 总结

1. 确认 Ingress Controller 已安装并运行
2. 根据您的环境选择正确的安装方式
3. 等待 Controller 完全就绪
4. 检查 Ingress 资源详情获取更多信息
5. 必要时添加 Ingress Class 注解

按照这些步骤操作后，您的 Ingress 应该能够正确获取 ADDRESS 了。

---

