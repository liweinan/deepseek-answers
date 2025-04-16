# 在 Kubernetes 中删除 Service、Deployment 和对应的 Pods

在 Kubernetes 中删除一个完整的应用资源（包括 Service、Deployment 和对应的 Pods），有以下几种方法：

## 方法1：逐个删除资源

```bash
# 删除 Service
kubectl delete service <service-name>

# 删除 Deployment（会自动删除对应的 ReplicaSet 和 Pods）
kubectl delete deployment <deployment-name>
```

## 方法2：使用标签选择器删除

如果您的资源有共同的标签（推荐做法），可以使用标签选择器一次性删除：

```bash
# 查看资源及其标签
kubectl get svc,deploy,pods --show-labels

# 使用标签选择器删除（例如 app=my-app）
kubectl delete svc,deploy,pods -l app=<your-app-label>
```

## 方法3：删除整个命名空间（谨慎使用）

如果您的所有资源都在同一个命名空间中，可以删除整个命名空间：

```bash
# 删除命名空间及其所有资源
kubectl delete namespace <namespace-name>
```

## 方法4：使用 kubectl 通配符删除

```bash
# 删除所有匹配名称模式的资源
kubectl delete all --all -n <namespace>  # 删除命名空间中的所有资源
kubectl delete all -l app=<your-app-label>  # 删除特定标签的所有资源
```

## 方法5：通过清单文件删除

如果您最初是通过 YAML 文件创建的资源，可以使用相同的文件删除：

```bash
kubectl delete -f your-deployment-and-service.yaml
```

## 注意事项

1. **删除顺序**：通常不需要特别关注删除顺序，因为 Kubernetes 会自动处理依赖关系

2. **Pod 删除**：当您删除 Deployment 时，它管理的 ReplicaSet 和 Pods 会自动被删除

3. **验证删除**：删除后可以运行以下命令验证：
   ```bash
   kubectl get svc,deploy,pods
   ```

4. **持久化存储**：如果使用了 PersistentVolumeClaims，需要单独删除：
   ```bash
   kubectl delete pvc <pvc-name>
   ```

5. **ConfigMaps 和 Secrets**：如果有相关的 ConfigMaps 或 Secrets，也需要单独删除

## 推荐做法

1. **使用标签**：为相关资源打上相同的标签，便于统一管理
2. **使用命名空间**：为不同应用使用不同命名空间
3. **使用清单文件**：通过 YAML 文件管理资源，便于版本控制和重复部署

通过以上方法，您可以彻底清理 Kubernetes 集群中的相关资源。