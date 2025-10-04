# 当一个 pod 包含多个容器时，需要指定容器名称来登录特定的容器。以下是详细的方法：

## 1. 查看 pod 中的容器

```bash
# 查看 pod 的详细信息，包括所有容器
kubectl describe pod <pod-name>

# 或者使用更简洁的方式查看容器列表
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'
```

## 2. 登录到特定容器

### 基本语法
```bash
# 指定容器名称登录
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash

# 如果容器没有 bash，使用 sh
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh
```

### 实际示例
```bash
# 假设你的 pod 有多个容器：nginx, redis, mysql
kubectl exec -it my-pod -c nginx -- /bin/bash
kubectl exec -it my-pod -c redis -- /bin/bash
kubectl exec -it my-pod -c mysql -- /bin/bash
```

## 3. 多容器 pod 的常见场景

### 示例：Web 应用 + 数据库 + 缓存
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app
spec:
  containers:
  - name: web-server
    image: nginx:latest
    ports:
    - containerPort: 80
  - name: database
    image: mysql:8.0
    ports:
    - containerPort: 3306
  - name: cache
    image: redis:latest
    ports:
    - containerPort: 6379
```

### 登录到各个容器
```bash
# 登录到 web 服务器容器
kubectl exec -it web-app -c web-server -- /bin/bash

# 登录到数据库容器
kubectl exec -it web-app -c database -- /bin/bash

# 登录到缓存容器
kubectl exec -it web-app -c cache -- /bin/bash
```

## 4. 实用技巧

### 查看所有容器状态
```bash
# 查看 pod 中所有容器的状态
kubectl get pod <pod-name> -o jsonpath='{range .status.containerStatuses[*]}{.name}: {.state}{"\n"}{end}'
```

### 获取容器日志
```bash
# 获取特定容器的日志
kubectl logs <pod-name> -c <container-name>

# 获取所有容器的日志
kubectl logs <pod-name> --all-containers=true
```

### 在容器中执行命令
```bash
# 在特定容器中执行命令
kubectl exec <pod-name> -c <container-name> -- ls -la

# 在容器中运行交互式命令
kubectl exec -it <pod-name> -c <container-name> -- mysql -u root -p
```

## 5. 调试多容器 pod 的完整流程

```bash
# 1. 查看 pod 状态
kubectl get pods

# 2. 查看 pod 详细信息
kubectl describe pod <pod-name>

# 3. 查看所有容器状态
kubectl get pod <pod-name> -o jsonpath='{range .status.containerStatuses[*]}{.name}: {.ready} - {.state}{"\n"}{end}'

# 4. 查看特定容器日志
kubectl logs <pod-name> -c <container-name>

# 5. 登录到特定容器
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash
```

## 6. 常见问题和解决方案

### 问题1：容器名称不明确
```bash
# 列出 pod 中所有容器名称
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}' | tr ' ' '\n'
```

### 问题2：容器没有 bash
```bash
# 尝试不同的 shell
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh
kubectl exec -it <pod-name> -c <container-name> -- /bin/zsh
kubectl exec -it <pod-name> -c <container-name> -- /bin/ash
```

### 问题3：容器崩溃重启
```bash
# 查看容器重启历史
kubectl describe pod <pod-name> | grep -A 10 "Containers:"

# 查看前一个容器的日志
kubectl logs <pod-name> -c <container-name> --previous
```

## 7. 实际应用示例

假设你有一个包含 nginx 和 php-fpm 的 pod：

```bash
# 查看容器列表
kubectl get pod my-app -o jsonpath='{.spec.containers[*].name}'
# 输出：nginx php-fpm

# 登录到 nginx 容器
kubectl exec -it my-app -c nginx -- /bin/bash

# 登录到 php-fpm 容器
kubectl exec -it my-app -c php-fpm -- /bin/bash

# 在 nginx 容器中检查配置
kubectl exec my-app -c nginx -- nginx -t

# 在 php-fpm 容器中检查 PHP 版本
kubectl exec my-app -c php-fpm -- php -v
```

## 8. 批量操作多容器

```bash
# 在所有容器中执行相同命令
for container in $(kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'); do
  echo "=== Container: $container ==="
  kubectl exec <pod-name> -c $container -- ps aux
done
```

这样你就可以灵活地登录和调试 pod 中的任何容器了！