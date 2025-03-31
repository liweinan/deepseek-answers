# **Kubernetes Service** 的样例  

以下是一个 **Kubernetes Service** 的 YAML 样例描述文件，演示了如何定义一个基本的 `ClusterIP` 类型的 Service，用于暴露一组 Pod（通过标签选择器匹配）：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service       # Service 名称
  namespace: default     # 可选，默认是 default
  labels:
    app: my-app          # 自定义标签（可选）
spec:
  type: ClusterIP        # Service 类型（ClusterIP/NodePort/LoadBalancer）
  selector:              # 选择要代理的 Pod（通过标签匹配）
    app: my-app          # 必须与 Pod 的 labels 匹配
    tier: frontend       # 可选，更精细的标签选择
  ports:
    - name: http         # 端口名称（可选）
      protocol: TCP      # 协议（TCP/UDP/SCTP）
      port: 80           # Service 暴露的端口
      targetPort: 8080   # Pod 上的端口（容器端口）
    - name: https        # 可以定义多个端口
      protocol: TCP
      port: 443
      targetPort: 8443
```

---

### **关键字段说明**
1. **`type`**:
    - `ClusterIP`（默认）：集群内部访问。
    - `NodePort`：通过节点 IP + 静态端口暴露。
    - `LoadBalancer`：云厂商提供的负载均衡器。

2. **`selector`**:
    - 必须与目标 Pod 的 `labels` 匹配，Service 会代理这些 Pod 的流量。

3. **`ports`**:
    - `port`: Service 的虚拟端口。
    - `targetPort`: Pod 容器的实际端口（需与 Pod 定义一致）。

---

### **其他常见 Service 类型示例**
#### **1. NodePort Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080  # 手动指定节点端口（可选，范围默认 30000-32767）
```

#### **2. LoadBalancer Service（云厂商适用）**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-lb-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
  externalTrafficPolicy: Local  # 可选，保留客户端源 IP
```

---

### **验证 Service**
```bash
kubectl apply -f service.yaml    # 部署 Service
kubectl get svc                 # 查看 Service 状态
kubectl describe svc my-service # 检查详细信息
```

这个示例覆盖了最常见的 Service 配置场景，您可以根据实际需求调整字段（如端口、标签选择器等）。

---

在 Kubernetes 中，**Service** 的主要作用是为一组 Pod 提供稳定的访问入口，并根据不同的使用场景分为三种核心类型：**ClusterIP**、**NodePort** 和 **LoadBalancer**。它们的核心区别在于 **访问范围** 和 **适用场景**。以下是详细对比：

---

### **1. ClusterIP（默认类型）**
#### **特点**
- **访问范围**：仅在集群内部可访问（如 Pod 之间的通信）。
- **IP 分配**：自动分配一个集群内部的虚拟 IP（VIP），无法从集群外部直接访问。
- **典型用途**：内部微服务通信、数据库访问等。

#### **示例 YAML**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-clusterip-service
spec:
  type: ClusterIP  # 可省略，默认类型
  selector:
    app: my-app
  ports:
    - port: 80      # Service 端口
      targetPort: 8080  # Pod 端口
```

#### **适用场景**
- 前端 Pod 需要访问后端 Pod（如前端调用后端 API）。
- 集群内部的服务发现（通过 DNS 名称 `my-service.namespace.svc.cluster.local`）。

---

### **2. NodePort**
#### **特点**
- **访问范围**：通过任意节点的 IP + 静态端口（NodePort）从集群外部访问。
- **端口范围**：默认 `30000-32767`（可手动指定）。
- **底层实现**：在 ClusterIP 基础上，额外在每个节点上开放一个端口。

#### **示例 YAML**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
    - port: 80          # Service 端口（集群内访问）
      targetPort: 8080  # Pod 端口
      nodePort: 31000   # 手动指定节点端口（可选）
```

#### **访问方式**
- 外部通过 `http://<任意节点IP>:31000` 访问服务。
- 集群内部仍可通过 ClusterIP (`http://<cluster-ip>:80`) 访问。

#### **适用场景**
- 开发测试环境临时暴露服务。
- 不支持 LoadBalancer 的本地集群（如 Minikube、裸金属集群）。

---

### **3. LoadBalancer**
#### **特点**
- **访问范围**：通过云厂商提供的负载均衡器（如 AWS ALB、GCP LB）从外部访问。
- **依赖条件**：需要集群运行在支持云负载均衡的平台上（如 AWS、Azure、GCP）。
- **底层实现**：在 NodePort 基础上，自动创建外部负载均衡器。

#### **示例 YAML**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-lb-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 80          # 负载均衡器监听的端口
      targetPort: 8080  # Pod 端口
```

#### **访问方式**
- 外部通过负载均衡器的 IP/DNS（如 `http://<LB-IP>:80`）访问。
- 集群内部仍可通过 ClusterIP 或 NodePort 访问。

#### **适用场景**
- 生产环境暴露服务（高可用、自动流量分发）。
- 云原生应用（如公有云上的 Web 服务）。

---

### **三者的核心区别对比**
| 特性                | ClusterIP              | NodePort                     | LoadBalancer               |
|---------------------|------------------------|------------------------------|----------------------------|
| **访问范围**         | 仅集群内部             | 节点IP + 静态端口（外部可访问）| 通过云负载均衡器（外部可访问） |
| **IP/端口**         | 集群内部虚拟IP         | 节点IP + 30000-32767端口      | 云厂商分配的LB IP           |
| **适用环境**        | 所有集群               | 所有集群（包括本地开发）       | 公有云/支持LB的私有云        |
| **典型用途**        | 内部服务通信           | 开发测试、临时暴露服务         | 生产环境对外服务            |
| **性能开销**        | 无额外开销             | 节点端口转发                  | 云LB + 节点端口转发          |

---

### **如何选择？**
1. **仅集群内部访问** → **ClusterIP**（如数据库服务）。
2. **临时外部访问（测试/本地集群）** → **NodePort**。
3. **生产环境外部访问（云平台）** → **LoadBalancer**。
4. **更高级需求（如 HTTPS、路由规则）** → 结合 **Ingress** 使用。

---

### **补充：Ingress 的作用**
- 上述三种 Service 主要解决 **L4（TCP/UDP）流量暴露**，而 **Ingress** 用于管理 **L7（HTTP/HTTPS）路由规则**（如域名、路径路由）。
- 通常与 `LoadBalancer` 或 `NodePort` 类型的 Service 配合使用。

---

