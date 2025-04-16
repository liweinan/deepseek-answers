# 在 Kubernetes 集群中部署 Jenkins 的 **手把手完整教程**

以下是在 Kubernetes 集群中部署 Jenkins 的 **手把手完整教程**，涵盖持久化存储、Service 暴露、Ingress 配置及初始密码获取：

---

### **前置条件**
1. 已安装 Kubernetes 集群（如 Minikube、k3s、EKS 等）。
2. 已安装 `kubectl` 并配置集群访问权限。
3. 可选：已安装 Helm（用于简化部署）。

---

## **方法一：使用 kubectl 直接部署（推荐初学者）**

### **步骤 1：创建 Namespace**
```bash
kubectl create namespace jenkins
```

### **步骤 2：创建持久化存储（PVC）**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jenkins-pvc
  namespace: jenkins
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF
```
> 📌 如果使用云服务（如 AWS EBS、Azure Disk），StorageClass 可能已自动配置；本地集群需提前部署 PV 供给器（如 NFS）。

---

### **步骤 3：部署 Jenkins Deployment**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts-jdk17
        ports:
        - containerPort: 8080
        - containerPort: 50000
        volumeMounts:
        - name: jenkins-storage
          mountPath: /var/jenkins_home
      volumes:
      - name: jenkins-storage
        persistentVolumeClaim:
          claimName: jenkins-pvc
      securityContext:
        runAsUser: 1000
        fsGroup: 1000
EOF
```
> 🔍 说明：
> - 使用官方 LTS 镜像（`jenkins/jenkins:lts-jdk17`）。
> - 挂载 PVC 到 `/var/jenkins_home` 确保数据持久化。
> - `securityContext` 避免权限问题。

---

### **步骤 4：暴露 Jenkins Service**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: jenkins
  namespace: jenkins
spec:
  type: NodePort
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30080
  - port: 50000
    targetPort: 50000
  selector:
    app: jenkins
EOF
```
> 🌐 访问方式：
> - **NodePort**：通过 `http://<节点IP>:30080` 访问。
> - 如需域名访问，继续步骤 5（Ingress）。

---

### **步骤 5（可选）：配置 Ingress**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jenkins-ingress
  namespace: jenkins
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: jenkins.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: jenkins
            port:
              number: 8080
EOF
```
> 📌 需提前：
> - 安装 Ingress Controller（如 Nginx Ingress）。
> - 将域名 `jenkins.example.com` 解析到集群 Ingress IP。

---

### **步骤 6：获取初始管理员密码**
1. 查看 Jenkins Pod 名称：
   ```bash
   kubectl get pods -n jenkins
   ```
2. 从 Pod 日志中提取密码：
   ```bash
   kubectl logs <jenkins-pod-name> -n jenkins | grep "InitialAdminPassword"
   ```
   > 或直接进入容器获取：
   ```bash
   kubectl exec -it <jenkins-pod-name> -n jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword
   ```

---

## **方法二：使用 Helm 快速部署（适合生产环境）**
### **步骤 1：添加 Jenkins Helm 仓库**
```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update
```

### **步骤 2：自定义配置**
创建 `values.yaml`：
```yaml
controller:
  image: "jenkins/jenkins"
  tag: "lts-jdk17"
  adminUser: "admin"
  adminPassword: "your-strong-password"  # 建议改为复杂密码
  serviceType: NodePort
  servicePort: 8080
  serviceNodePort: 30080
  installPlugins:
    - kubernetes
    - workflow-aggregator
  persistence:
    enabled: true
    size: 10Gi
```

### **步骤 3：安装 Jenkins**
```bash
helm install jenkins jenkins/jenkins -n jenkins -f values.yaml
```

---

## **验证部署**
1. 检查 Pod 状态：
   ```bash
   kubectl get pods -n jenkins -w
   ```
2. 访问 Jenkins：
    - NodePort：`http://<节点IP>:30080`
    - Ingress：`http://jenkins.example.com`

---

## **常见问题解决**
1. **PVC 未绑定**：
    - 检查 StorageClass 是否可用：`kubectl get storageclass`。
    - 本地集群可改用 `hostPath`（仅测试用途）：
      ```yaml
      volumes:
      - name: jenkins-storage
        hostPath:
          path: /data/jenkins
          type: DirectoryOrCreate
      ```

2. **插件安装失败**：
    - 在 Jenkins 界面中更换为国内镜像源：
        - 进入 **Manage Jenkins → Plugin Manager → Advanced**。
        - 将 `Update Site` 改为 `https://mirrors.tuna.tsinghua.edu.cn/jenkins/updates/update-center.json`。

---

## **总结**
- **kubectl 直接部署**：适合学习或快速验证。
- **Helm 部署**：适合生产环境，支持灵活配置。
- **关键配置**：持久化存储、Service 暴露、安全上下文。

按此教程操作后，你将获得一个完整可用的 Jenkins 服务，并可通过 Kubernetes 动态管理构建代理（需安装 `kubernetes` 插件）。