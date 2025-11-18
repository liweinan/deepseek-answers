# When a pod contains multiple containers, you need to specify the container name to log into a specific container. Here are the detailed methods:

## 1. View Containers in Pod

```bash
# View pod details including all containers
kubectl describe pod <pod-name>

# Or use a more concise way to view container list
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'
```

## 2. Log into Specific Container

### Basic Syntax
```bash
# Specify container name to log in
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash

# If container doesn't have bash, use sh
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh
```

### Practical Example
```bash
# Assume your pod has multiple containers: nginx, redis, mysql
kubectl exec -it my-pod -c nginx -- /bin/bash
kubectl exec -it my-pod -c redis -- /bin/bash
kubectl exec -it my-pod -c mysql -- /bin/bash
```

## 3. Common Scenarios for Multi-Container Pods

### Example: Web Application + Database + Cache
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

### Log into Each Container
```bash
# Log into web server container
kubectl exec -it web-app -c web-server -- /bin/bash

# Log into database container
kubectl exec -it web-app -c database -- /bin/bash

# Log into cache container
kubectl exec -it web-app -c cache -- /bin/bash
```

## 4. Practical Tips

### View Status of All Containers
```bash
# View status of all containers in pod
kubectl get pod <pod-name> -o jsonpath='{range .status.containerStatuses[*]}{.name}: {.state}{"\n"}{end}'
```

### Get Container Logs
```bash
# Get logs for specific container
kubectl logs <pod-name> -c <container-name>

# Get logs for all containers
kubectl logs <pod-name> --all-containers=true
```

### Execute Commands in Container
```bash
# Execute command in specific container
kubectl exec <pod-name> -c <container-name> -- ls -la

# Run interactive command in container
kubectl exec -it <pod-name> -c <container-name> -- mysql -u root -p
```

## 5. Complete Debugging Process for Multi-Container Pods

```bash
# 1. View pod status
kubectl get pods

# 2. View pod details
kubectl describe pod <pod-name>

# 3. View status of all containers
kubectl get pod <pod-name> -o jsonpath='{range .status.containerStatuses[*]}{.name}: {.ready} - {.state}{"\n"}{end}'

# 4. View logs for specific container
kubectl logs <pod-name> -c <container-name>

# 5. Log into specific container
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash
```

## 6. Common Issues and Solutions

### Issue 1: Container Name Not Clear
```bash
# List all container names in pod
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}' | tr ' ' '\n'
```

### Issue 2: Container Has No Bash
```bash
# Try different shells
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh
kubectl exec -it <pod-name> -c <container-name> -- /bin/zsh
kubectl exec -it <pod-name> -c <container-name> -- /bin/ash
```

### Issue 3: Container Crashes and Restarts
```bash
# View container restart history
kubectl describe pod <pod-name> | grep -A 10 "Containers:"

# View previous container's logs
kubectl logs <pod-name> -c <container-name> --previous
```

## 7. Practical Application Example

Assume you have a pod with nginx and php-fpm:

```bash
# View container list
kubectl get pod my-app -o jsonpath='{.spec.containers[*].name}'
# Output: nginx php-fpm

# Log into nginx container
kubectl exec -it my-app -c nginx -- /bin/bash

# Log into php-fpm container
kubectl exec -it my-app -c php-fpm -- /bin/bash

# Check nginx configuration in nginx container
kubectl exec my-app -c nginx -- nginx -t

# Check PHP version in php-fpm container
kubectl exec my-app -c php-fpm -- php -v
```

## 8. Batch Operations on Multiple Containers

```bash
# Execute same command in all containers
for container in $(kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'); do
  echo "=== Container: $container ==="
  kubectl exec <pod-name> -c $container -- ps aux
done
```

This way you can flexibly log into and debug any container in the pod!