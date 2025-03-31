# OpenShift的三种核心资源

在 OpenShift（基于 Kubernetes）中，**Service Account**、**ConfigMap** 和 **Secret** 是三种核心资源，分别用于管理身份认证、配置数据和敏感信息。以下是它们的详细说明和对比：

---

## **1. Service Account（服务账户）**
### **作用**
- **身份认证**：为 Pod 或系统组件提供身份，用于与 OpenShift/Kubernetes API 交互。
- **权限控制**：通过 `RoleBinding` 或 `ClusterRoleBinding` 关联权限（RBAC）。

### **特点**
- 每个 Namespace 自动生成一个默认 Service Account（`default`）。
- Pod 运行时如果没有显式指定，会自动使用 `default` Service Account。
- 用于安全访问集群资源（如创建 Pod、读取 Secrets）。

### **示例**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: my-namespace
```

### **使用场景**
- Pod 需要调用 Kubernetes API（如 CI/CD 流水线）。
- 限制 Pod 的权限（避免使用高权限的 `default` 账户）。

---

## **2. ConfigMap（配置映射）**
### **作用**
- **存储非敏感的配置数据**（如环境变量、配置文件）。
- 将配置与容器镜像解耦，便于灵活管理。

### **特点**
- 数据以键值对（Key-Value）形式存储。
- 可以通过环境变量或挂载为文件的方式注入到 Pod 中。
- **不加密**，不适合存储密码、密钥等敏感信息。

### **示例**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
  namespace: my-namespace
data:
  # 键值对形式的配置
  APP_COLOR: "blue"
  APP_MODE: "production"
  # 配置文件内容
  config-file.properties: |
    server.port=8080
    logging.level=INFO
```

### **使用场景**
- 应用配置（如数据库连接字符串、日志级别）。
- 动态调整参数无需重新构建镜像。

---

## **3. Secret（密钥）**
### **作用**
- **存储敏感信息**（如密码、TLS 证书、令牌）。
- 数据默认以 Base64 编码（非加密，需配合 RBAC 和网络策略保护）。

### **特点**
- 类型包括：
    - `Opaque`：通用密钥（如用户名/密码）。
    - `kubernetes.io/tls`：TLS 证书。
    - `docker-registry`：镜像仓库认证信息。
- 比 ConfigMap 更安全（但需额外措施确保真正安全）。

### **示例**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
  namespace: my-namespace
type: Opaque
data:
  username: YWRtaW4=  # Base64 编码的 "admin"
  password: MWYyZDFlMmU2N2Rm  # Base64 编码的 "1f2d1e2e67df"
```

### **使用场景**
- 数据库密码、API 密钥。
- TLS 证书或镜像仓库认证。

---

## **三者的核心区别**
| 特性                | Service Account         | ConfigMap               | Secret                  |
|---------------------|------------------------|-------------------------|-------------------------|
| **用途**            | 身份认证和权限管理      | 存储非敏感配置          | 存储敏感信息            |
| **数据安全**        | 关联 RBAC 权限          | 明文存储                | Base64 编码（非加密）    |
| **典型数据**        | API 访问令牌            | 环境变量、配置文件       | 密码、证书、令牌         |
| **是否加密**        | 否（但受 RBAC 保护）    | 否                      | 否（需额外加密措施）     |
| **挂载方式**        | 自动挂载到 Pod          | 环境变量或文件卷         | 环境变量或文件卷         |

---

## **常见使用方式**
### **1. 在 Pod 中引用 ConfigMap/Secret**
#### **作为环境变量**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: my-container
      image: nginx
      env:
        - name: APP_COLOR  # 从 ConfigMap 注入
          valueFrom:
            configMapKeyRef:
              name: my-config
              key: APP_COLOR
        - name: DB_PASSWORD  # 从 Secret 注入
          valueFrom:
            secretKeyRef:
              name: my-secret
              key: password
```

#### **作为文件卷挂载**
```yaml
spec:
  containers:
    - name: my-container
      image: nginx
      volumeMounts:
        - name: config-volume
          mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        name: my-config
    - name: secret-volume
      secret:
        secretName: my-secret
```

### **2. 为 Pod 指定 Service Account**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-service-account  # 指定自定义 Service Account
  containers:
    - name: my-container
      image: nginx
```

---

## **最佳实践**
1. **Service Account**：
    - 避免 Pod 使用高权限的 `default` 账户，按需创建最小权限账户。
2. **ConfigMap**：
    - 仅存储非敏感配置，变更后需重启 Pod 或使用支持热加载的应用。
3. **Secret**：
    - 结合 **SealedSecret** 或 **Vault** 实现加密。
    - 限制 Secret 的访问权限（RBAC）。

---

## **总结**
- **Service Account**：管理 Pod 身份和权限。
- **ConfigMap**：存储应用配置（非敏感）。
- **Secret**：存储敏感数据（需额外保护）。
- **三者协作**：  
  `Service Account` 控制访问权限 → `ConfigMap` 提供配置 → `Secret` 保护密钥。