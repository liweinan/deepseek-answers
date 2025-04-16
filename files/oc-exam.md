# Kubernetes 和 OpenShift 面试考卷

## 基础知识部分 (30分)

### 选择题 (每题2分，共10分)

1. Kubernetes 中的最小调度单位是：
    - A) Pod
    - B) Container
    - C) Node
    - D) Deployment

2. OpenShift 是基于哪个 Kubernetes 发行版构建的？
    - A) Rancher
    - B) Red Hat OpenShift Kubernetes Engine
    - C) Vanilla Kubernetes
    - D) EKS

3. 在 Kubernetes 中，用于存储敏感信息的资源对象是：
    - A) ConfigMap
    - B) Secret
    - C) Volume
    - D) PersistentVolume

4. OpenShift 的 Web 控制台默认使用哪种身份验证方式？
    - A) Basic Auth
    - B) OAuth
    - C) LDAP
    - D) Kerberos

5. 以下哪个不是 Kubernetes 的核心组件？
    - A) kubelet
    - B) etcd
    - C) kube-proxy
    - D) Docker

### 填空题 (每题2分，共10分)

1. Kubernetes API 的 REST 路径前缀是 `/________`。

2. OpenShift 中用于构建容器镜像的组件是 ________。

3. Kubernetes 中用于定义 Pod 部署和更新的资源类型是 ________。

4. OpenShift 中用于管理项目配额的对象是 ________。

5. Kubernetes 中用于将外部服务暴露给集群内部的资源类型是 ________。

### 简答题 (每题5分，共10分)

1. 简要说明 Kubernetes 和 OpenShift 的主要区别。

2. 解释 Kubernetes 中 Deployment、ReplicaSet 和 Pod 之间的关系。

## 中级知识部分 (40分)

### 场景分析题 (每题10分，共20分)

1. 你正在管理一个 OpenShift 集群，突然发现某个项目的 Pod 无法创建，报错提示 "Failed to allocate resources"。请描述你的排查步骤和可能的解决方案。

2. 描述在 Kubernetes 中实现蓝绿部署的步骤，并说明 OpenShift 如何简化这个过程。

### 命令操作题 (每题10分，共20分)

1. 编写一组 kubectl/oc 命令完成以下任务：
    - 创建一个名为 "test" 的命名空间/项目
    - 在该命名空间中部署一个 nginx 容器，使用 Deployment 资源
    - 暴露该 Deployment 为 Service，类型为 NodePort
    - 检查 Pod 的状态和日志

2. 你需要在 OpenShift 中设置一个构建配置，从 GitHub 仓库构建一个 Node.js 应用，并将其部署到集群中。请写出完整的 oc 命令流程。

## 高级知识部分 (30分)

### 架构设计题 (15分)

设计一个高可用的生产级 OpenShift 集群架构，要求：
- 包含至少 3 个 master 节点和 5 个 worker 节点
- 考虑 etcd 集群的部署
- 包含日志和监控方案
- 考虑网络和存储的高可用性

### 故障排除题 (15分)

一个生产 Kubernetes 集群中，用户报告他们的应用间歇性不可用。你发现：
- Pod 状态显示为 Running
- Service 和 Endpoints 配置正确
- 网络策略允许必要的流量
- 节点资源使用率正常

请描述你的系统化排查方法和可能的根本原因。

## 参考答案

### 基础知识部分

**选择题**：
1. A 2. B 3. B 4. B 5. D

**填空题**：
1. /api
2. BuildConfig / Source-to-Image (S2I)
3. Deployment
4. ResourceQuota
5. Service (或 Ingress)

**简答题**：
1. Kubernetes 是开源容器编排平台，OpenShift 是基于 Kubernetes 的企业级发行版，提供额外的功能如：内置镜像仓库、构建工具、Web 控制台、增强的安全特性(如SCC)、多租户支持、开发者工具集成等。

2. Deployment 管理 ReplicaSet，ReplicaSet 确保指定数量的 Pod 副本运行。Deployment 提供声明式更新、回滚等功能，ReplicaSet 负责 Pod 的扩缩容，Pod 是实际运行容器的单元。

### 中级知识部分

**场景分析题**：
1. 排查步骤：
    - 检查项目配额：`oc describe quota -n <project>`
    - 检查资源请求/限制：`oc describe pod <podname>`
    - 检查节点资源：`oc adm top nodes`
    - 检查资源使用情况：`oc adm top pods -n <project>`
      解决方案可能包括：调整配额、优化资源请求、清理未使用的资源、添加更多节点等。

2. 蓝绿部署步骤：
    - 部署新版本应用(绿色)与旧版本(蓝色)并行
    - 使用相同标签但不同版本标签区分
    - 通过 Service 切换流量
      OpenShift 简化方式：
    - 使用 Route 和权重分配
    - 利用 DeploymentConfig 的滚动策略
    - 使用 OpenShift Pipelines 自动化流程

**命令操作题**：
1. ```bash
   kubectl create ns test
   kubectl create deployment nginx --image=nginx -n test
   kubectl expose deployment nginx --port=80 --type=NodePort -n test
   kubectl get pods -n test
   kubectl logs <pod-name> -n test
   ```

2. ```bash
   oc new-project nodejs-app
   oc new-app nodejs~https://github.com/your/nodejs-repo.git
   # 或更详细的构建配置
   oc new-build nodejs~https://github.com/your/nodejs-repo.git --name=nodejs-app
   oc new-app --image-stream=nodejs-app:latest
   oc expose svc/nodejs-app
   ```

### 高级知识部分

**架构设计题**：
关键点：
- 3个master节点组成高可用控制平面，使用负载均衡器
- etcd 集群独立部署或与master节点共存，奇数节点，跨故障域
- 5个worker节点跨可用区部署
- 日志方案：EFK 或 Loki 堆栈
- 监控方案：Prometheus + Grafana 或 OpenShift 监控堆栈
- 网络：多网络接口，SDN 插件(如OVN-Kubernetes)
- 存储：持久卷使用支持 ReadWriteMany 的存储后端(如Ceph)

**故障排除题**：
排查方法：
1. 检查 kube-proxy 和 CNI 插件状态
2. 检查网络策略是否冲突
3. 检查 DNS 解析是否正常
4. 检查应用健康检查配置
5. 检查节点内核日志是否有丢包或连接问题
6. 使用网络诊断工具(如ping, curl, tcpdump)

可能原因：
- kube-proxy 规则未正确同步
- CNI 网络插件问题
- 应用健康检查过于敏感
- 节点间网络问题
- DNS 解析间歇性失败
- 并发连接数达到限制

---

在 Kubernetes（k8s）中，**Pod 的生成涉及多个组件协同工作**，但主要由以下两个核心组件负责：

---

### **1. 控制平面（Control Plane）**
#### **（1）kube-scheduler（调度器）**
- **职责**：
    - 监听未被调度的 Pod（`Pod.spec.nodeName` 为空）。
    - 根据资源需求、亲和性规则等，选择最优的 Node 运行 Pod。
    - 将调度决策写入 API Server（更新 `Pod.spec.nodeName`）。
- **关键点**：
    - **不直接创建 Pod**，仅决定 Pod 应该运行在哪个 Node 上。

#### **（2）kube-controller-manager（控制器管理器）**
- 其中的 **Deployment Controller** / **ReplicaSet Controller** / **StatefulSet Controller** 等：
    - 监听 API Server 中资源（如 Deployment、ReplicaSet）的变化。
    - 确保实际运行的 Pod 数量与声明的副本数一致。
    - **生成 Pod 模板**（PodSpec）并通过 API Server 创建 Pod 对象。
- **关键点**：
    - **负责生成 Pod 的元数据**（如名称、标签、资源请求等），但 Pod 尚未被调度或运行。

---

### **2. 工作节点（Worker Node）**
#### **（3）kubelet（节点代理）**
- **职责**：
    - 监听 API Server 中分配到本节点的 Pod。
    - 调用容器运行时（如 containerd、CRI-O）**实际创建容器**。
    - 管理 Pod 生命周期（启动、停止、重启）。
- **关键点**：
    - **真正在节点上生成 Pod 的进程**，将 Pod 从声明式状态变为实际运行的容器。

---

### **完整流程示例（以 Deployment 为例）**
1. **用户提交 Deployment**：
   ```bash
   kubectl create deployment nginx --image=nginx
   ```
2. **Deployment Controller 生成 ReplicaSet**：
    - 根据 Deployment 模板创建 ReplicaSet 对象。
3. **ReplicaSet Controller 生成 Pod 对象**：
    - 通过 API Server 创建 Pod（此时 `Pod.spec.nodeName` 为空）。
4. **kube-scheduler 分配 Node**：
    - 选择合适 Node 并更新 `Pod.spec.nodeName`。
5. **目标 Node 的 kubelet 创建容器**：
    - 调用容器运行时启动 Pod 内的容器。

---

### **关键总结**
| 组件                | 职责                               | 是否直接生成 Pod？ |
|---------------------|-----------------------------------|------------------|
| **Deployment/ReplicaSet Controller** | 生成 Pod 元数据（通过 API Server） | ❌（仅生成声明）   |
| **kube-scheduler**  | 决定 Pod 运行在哪个 Node           | ❌                |
| **kubelet**         | 在节点上实际创建容器               | ✅                |

**简答**：
- **Pod 的声明由控制器（如 Deployment Controller）生成**，但**实际创建由 kubelet 执行**。
- 整个过程通过 API Server 的监听机制协调完成。