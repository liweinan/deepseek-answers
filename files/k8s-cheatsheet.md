# Kubernetes 速查表 (Cheatsheet)

## 基础命令

```bash
kubectl version          # 查看客户端和服务器版本
kubectl cluster-info     # 显示集群信息
kubectl get nodes        # 查看所有节点
kubectl config view      # 查看当前配置
kubectl api-resources    # 查看所有API资源类型
```

## 命名空间(Namespace)操作

```bash
kubectl get ns                     # 查看所有命名空间
kubectl create ns <namespace>      # 创建命名空间
kubectl delete ns <namespace>      # 删除命名空间
kubectl config set-context --current --namespace=<namespace> # 设置默认命名空间
```

## Pod操作

```bash
kubectl get pods [-n <namespace>]          # 查看Pod列表
kubectl get pods -o wide                   # 查看Pod详情(包括节点信息)
kubectl describe pod <pod-name>            # 查看Pod详细信息
kubectl logs <pod-name> [-c <container>]   # 查看Pod日志
kubectl exec -it <pod-name> -- /bin/bash   # 进入Pod容器
kubectl delete pod <pod-name>              # 删除Pod
kubectl top pod <pod-name>                 # 查看Pod资源使用情况
```

## Deployment操作

```bash
kubectl get deployments                    # 查看所有Deployment
kubectl describe deployment <deploy-name>  # 查看Deployment详情
kubectl create deployment <name> --image=<image>  # 创建Deployment
kubectl scale deployment <deploy-name> --replicas=3  # 扩缩容
kubectl edit deployment <deploy-name>      # 编辑Deployment配置
kubectl rollout status deployment/<deploy-name>  # 查看滚动更新状态
kubectl rollout history deployment/<deploy-name> # 查看更新历史
kubectl rollout undo deployment/<deploy-name>    # 回滚到上一版本
kubectl rollout undo deployment/<deploy-name> --to-revision=2 # 回滚到指定版本
kubectl delete deployment <deploy-name>    # 删除Deployment
```

## Service操作

```bash
kubectl get services               # 查看所有Service
kubectl expose deployment <deploy-name> --port=80 --target-port=8080 --type=NodePort # 创建Service
kubectl describe service <svc-name> # 查看Service详情
kubectl delete service <svc-name>  # 删除Service
```

## ConfigMap和Secret操作

```bash
# ConfigMap
kubectl create configmap <name> --from-literal=key=value  # 从字面值创建
kubectl create configmap <name> --from-file=path/to/file  # 从文件创建
kubectl get configmaps             # 查看所有ConfigMap
kubectl describe configmap <name>  # 查看ConfigMap详情

# Secret
kubectl create secret generic <name> --from-literal=key=value  # 创建generic secret
kubectl create secret docker-registry <name> --docker-server=<server> --docker-username=<user> --docker-password=<pwd> # 创建docker registry secret
kubectl get secrets               # 查看所有Secret
kubectl describe secret <name>    # 查看Secret详情
```

## 状态管理(StatefulSet)

```bash
kubectl get statefulsets          # 查看所有StatefulSet
kubectl describe statefulset <name> # 查看StatefulSet详情
kubectl delete statefulset <name> # 删除StatefulSet
```

## 持久化存储(PV/PVC)

```bash
kubectl get pv                    # 查看持久卷(PersistentVolume)
kubectl get pvc                   # 查看持久卷声明(PersistentVolumeClaim)
kubectl describe pvc <pvc-name>   # 查看PVC详情
```

## 工作负载管理

```bash
# Job
kubectl get jobs                  # 查看所有Job
kubectl describe job <job-name>   # 查看Job详情

# CronJob
kubectl get cronjobs              # 查看所有CronJob
kubectl describe cronjob <name>   # 查看CronJob详情
```

## 网络策略(NetworkPolicy)

```bash
kubectl get networkpolicies       # 查看所有网络策略
kubectl describe networkpolicy <name> # 查看网络策略详情
```

## 资源配额和限制

```bash
kubectl get quota                 # 查看资源配额
kubectl describe quota <name>     # 查看配额详情
kubectl get limitranges           # 查看限制范围
```

## 调试和故障排查

```bash
kubectl get events --sort-by=.metadata.creationTimestamp  # 查看事件(按时间排序)
kubectl get pods --field-selector=status.phase=Running    # 过滤Pod状态
kubectl port-forward <pod-name> 8080:80  # 端口转发
kubectl cp <pod-name>:/path/to/file ./local-file  # 从Pod复制文件
kubectl apply -f <file.yaml>      # 应用YAML配置
kubectl delete -f <file.yaml>     # 删除YAML定义的资源
kubectl explain <resource>        # 查看资源定义文档
```

## 常用YAML模板

### Pod示例

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.19
    ports:
    - containerPort: 80
```

### Deployment示例

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.19
        ports:
        - containerPort: 80
```

### Service示例(NodePort)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30007
```

### ConfigMap示例

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.properties: |
    key1=value1
    key2=value2
```

### Secret示例

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  username: YWRtaW4=  # base64编码
  password: MWYyZDFlMmU2N2Rm
```

### PersistentVolumeClaim示例

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

## 常用技巧

1. **快速创建Pod并测试**
   ```bash
   kubectl run -it --rm --image=busybox test-pod -- sh
   ```

2. **查看Pod的环境变量**
   ```bash
   kubectl exec <pod-name> -- env
   ```

3. **强制删除卡在Terminating状态的资源**
   ```bash
   kubectl delete pod <pod-name> --grace-period=0 --force
   ```

4. **查看Pod的资源请求和限制**
   ```bash
   kubectl get pod <pod-name> -o json | jq '.spec.containers[].resources'
   ```

5. **查看Pod调度事件**
   ```bash
   kubectl get events --field-selector involvedObject.name=<pod-name>
   ```

6. **使用别名提高效率**
   ```bash
   alias k='kubectl'
   alias kgp='kubectl get pods'
   alias kgs='kubectl get services'
   ```

7. **输出为YAML或JSON格式**
   ```bash
   kubectl get pod <pod-name> -o yaml
   kubectl get pod <pod-name> -o json
   ```

8. **标签选择器查询**
   ```bash
   kubectl get pods -l app=nginx
   kubectl get pods -l 'environment in (production, staging)'
   ```

9. **查看Pod的IP地址**
   ```bash
   kubectl get pod -o jsonpath='{.items[*].status.podIP}'
   ```

10. **批量删除资源**
    ```bash
    kubectl delete pods,services -l name=myLabel
    ```

这个Kubernetes速查表涵盖了日常使用中最常用的命令和配置，可以作为快速参考使用。根据你的具体使用场景，可能需要更深入地了解某些特定领域。

