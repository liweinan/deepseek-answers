# 在 OpenShift Local (CRC) 上部署一个简单 Service 使用 Docker Hub 公开镜像的完整步骤

### 1. 准备工作
```bash
# 登录 CRC OpenShift
oc login -u developer -p developer https://api.crc.testing:6443

# 创建新项目（可选）
oc new-project my-demo
```

### 2. 部署简单应用（Nginx 示例）
```bash
# 方法1：使用 oc new-app 快速部署
oc new-app --name=my-web --docker-image=nginx:alpine

# 方法2：使用 YAML 文件（推荐）
cat <<EOF | oc apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-web
spec:
  selector:
    matchLabels:
      app: my-web
  template:
    metadata:
      labels:
        app: my-web
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
EOF
```

### 3. 创建 Service
```bash
# 暴露 Deployment
oc expose deployment/my-web --port=80
```

### 4. 创建 Route（外部访问）
```bash
oc expose svc/my-web
```

### 5. 验证部署
```bash
# 查看所有资源状态
oc get all -l app=my-web

# 获取访问URL
echo "访问地址：http://$(oc get route my-web -o jsonpath='{.spec.host}')"

# 测试访问（在主机执行）
curl http://$(oc get route my-web -o jsonpath='{.spec.host}')
```

### 6. 常见问题解决

#### 问题1：镜像拉取失败
```bash
# 检查节点是否能访问外网
oc debug node/crc -- chroot /host ping 8.8.8.8

# 临时解决方案（使用内置镜像）
oc new-app --name=my-web --docker-image=image-registry.openshift-image-registry.svc:5000/openshift/nginx:latest
```

#### 问题2：权限问题
```bash
# 授予安全权限（开发环境适用）
oc adm policy add-scc-to-user anyuid -z default
oc rollout restart deployment/my-web
```

### 7. 清理资源
```bash
oc delete all -l app=my-web
```

### 关键说明：
1. CRC 默认使用内部镜像仓库，如需访问 Docker Hub：
   ```bash
   # 在 CRC 虚拟机中添加 Docker Hub 镜像拉取秘钥
   oc create secret docker-registry dockerhub \
     --docker-server=docker.io \
     --docker-username=<your-username> \
     --docker-password=<your-token>
   ```

2. 推荐使用 `alpine` 版本镜像（体积更小，更适合测试环境）

3. 如果遇到网络问题，可以检查 CRC 网络配置：
   ```bash
   crc config view | grep network
   ```

4. 性能优化建议：
   ```bash
   # 限制资源使用（防止 CRC 过载）
   oc set resources deployment/my-web --limits=cpu=200m,memory=256Mi
   ```

这样就能在 CRC 上快速部署一个最简单的服务。如需其他镜像，只需替换 `nginx:alpine` 为其他 Docker Hub 公开镜像即可。