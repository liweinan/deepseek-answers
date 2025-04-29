# 一个极简的 **Kubernetes Custom Resource Definition (CRD)** 教程

以下是一个极简的 **Kubernetes Custom Resource Definition (CRD)** 教程，指导你如何编写、部署和使用 CRD 到现有的 Kubernetes 集群中。教程使用中文，内容简洁，涵盖核心步骤，并包含必要的代码示例。

---

### 什么是 CRD？
CRD（Custom Resource Definition）允许你在 Kubernetes 中定义自定义资源，扩展 Kubernetes API，让你像使用内置资源（如 Pod、Deployment）一样管理自定义对象。CRD 常用于实现自定义控制器或扩展 Kubernetes 功能。

---

### 教程目标
我们将：
1. 创建一个简单的 CRD，定义一个名为 `SimpleApp` 的自定义资源。
2. 部署 CRD 到 Kubernetes 集群。
3. 创建一个 `SimpleApp` 自定义资源实例。
4. 验证部署结果。

---

### 环境准备
- 一个运行中的 Kubernetes 集群（可以用 Minikube、Kind 或云端集群）。
- `kubectl` 已配置好并能访问集群。
- 文本编辑器（如 VS Code）或直接在终端操作。

---

### 步骤

#### 1. 编写 CRD 定义
我们将定义一个简单的 CRD，名为 `SimpleApp`，它包含以下字段：
- `appName`：应用的名称。
- `replicas`：副本数。

创建文件 `simpleapp-crd.yaml`：

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: simpleapps.example.com
spec:
  group: example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                appName:
                  type: string
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 10
  scope: Namespaced
  names:
    plural: simpleapps
    singular: simpleapp
    kind: SimpleApp
    shortNames:
      - sapp
```


**说明**：
- `group`：自定义资源的 API 组（`example.com`）。
- `versions`：定义 CRD 的版本（这里是 `v1`）。
- `schema`：定义资源结构，`appName` 是字符串，`replicas` 是 1 到 10 的整数。
- `scope`：`Namespaced` 表示资源是命名空间级别的（而不是集群级别的）。
- `names`：定义资源的名称、复数形式和缩写。

---

#### 2. 部署 CRD 到集群

使用 `kubectl` 应用 CRD 定义：

```bash
kubectl apply -f simpleapp-crd.yaml
```

验证 CRD 是否创建成功：

```bash
kubectl get crd
```

输出应包含：

```
NAME                     CREATED AT
simpleapps.example.com   <创建时间>
```

---

#### 3. 创建自定义资源实例
现在我们创建一个 `SimpleApp` 资源实例。创建文件 `simpleapp-instance.yaml`：

```yaml
apiVersion: example.com/v1
kind: SimpleApp
metadata:
  name: my-simple-app
  namespace: default
spec:
  appName: my-app
  replicas: 3
```


**说明**：
- `apiVersion`：使用 CRD 定义的 `group` 和 `version`（`example.com/v1`）。
- `kind`：使用 CRD 定义的 `kind`（`SimpleApp`）。
- `spec`：包含 `appName` 和 `replicas`，符合 CRD 的 schema。

部署实例：
```bash
kubectl apply -f simpleapp-instance.yaml
```

---

#### 4. 验证自定义资源
检查 `SimpleApp` 资源是否创建成功：
```bash
kubectl get simpleapps
```
输出：
```
NAME             AGE
my-simple-app    <创建时间>
```

查看资源详情：
```bash
kubectl describe simpleapp my-simple-app
```
输出将显示资源的 `metadata` 和 `spec`，例如：
```
Name:         my-simple-app
Namespace:    default
API Version:  example.com/v1
Kind:         SimpleApp
Spec:
  App Name:   my-app
  Replicas:   3
```

你也可以使用缩写：
```bash
kubectl get sapp
```

---

#### 5. （可选）清理资源
如果需要删除创建的资源：
```bash
kubectl delete -f simpleapp-instance.yaml
kubectl delete -f simpleapp-crd.yaml
```

注意：删除 CRD 会同时删除所有相关的自定义资源实例。

---

### 后续步骤
- **添加控制器**：CRD 本身只定义了数据结构。要让 `SimpleApp` 资源实际触发行为（例如创建 Pod），需要编写一个自定义控制器（Operator）。你可以使用工具如 [Operator SDK](https://sdk.operatorframework.io/) 或 [Kubebuilder](https://book.kubebuilder.io/) 来实现。
- **扩展 CRD**：可以添加更多字段（如 `image`、`port`）或支持多版本 API。
- **权限控制**：为 CRD 配置 RBAC，确保只有授权用户可以操作。

---

### 常见问题
1. **CRD 未出现在 `kubectl get crd`**？
    - 检查 `simpleapp-crd.yaml` 是否正确应用：`kubectl apply -f simpleapp-crd.yaml`。
    - 查看事件：`kubectl describe crd simpleapps.example.com`。

2. **自定义资源创建失败**？
    - 确保 `apiVersion` 和 `kind` 与 CRD 定义一致。
    - 检查 schema 是否匹配：`kubectl describe simpleapp my-simple-app`。

3. **如何测试控制器**？
    - 本教程只创建 CRD，未实现控制器。如果需要控制器，推荐学习 Operator SDK 或 Kubebuilder。

---

### 总结
通过以上步骤，你已经：
- 定义并部署了一个简单的 CRD（`SimpleApp`）。
- 创建了一个自定义资源实例。
- 验证了资源在集群中的状态。

这个 CRD 是一个基础示例，适合学习和扩展。如果你需要更复杂的 CRD（如多版本支持、复杂 schema）或实现自定义控制器，请告诉我，我可以提供更详细的教程！

--- 

如果有其他问题或需要进一步扩展（例如添加控制器代码），请随时告知！

---

好的！我们将扩展之前的 `SimpleApp` CRD，添加一个简单的功能：当创建或更新 `SimpleApp` 资源时，在 Kubernetes 集群的日志中打印 `Hello, World!` 以及资源的 `appName` 和 `replicas` 信息。为此，我们需要编写一个简单的 **自定义控制器**（Custom Controller）来监听 `SimpleApp` 资源的变更，并实现日志打印逻辑。控制器将使用 **Go** 语言和 **controller-runtime** 库编写。

---

### 目标
1. 扩展现有的 `SimpleApp` CRD，保持其结构（`appName` 和 `replicas`）。
2. 编写一个简单的 Go 控制器，监听 `SimpleApp` 资源的创建和更新事件，并在日志中打印 `Hello, World!` 以及资源信息。
3. 提供部署控制器的步骤，确保它运行在 Kubernetes 集群中。
4. 包含所有必要的代码和配置文件，保持极简风格。

---

### 环境准备
- **Kubernetes 集群**：已运行并可通过 `kubectl` 访问。
- **Go 环境**：Go 1.20 或更高版本（推荐使用最新版）。
- **工具**：
    - `kubectl`：用于应用 CRD 和部署控制器。
    - `docker`：用于构建控制器镜像。
    - 一个容器注册表（如 Docker Hub）或本地镜像支持（如 Minikube）。
- **代码依赖**：
    - `controller-runtime`：Kubernetes 控制器框架。
    - `k8s.io/api` 和 `k8s.io/apimachinery`：Kubernetes API 库。

---

### 步骤

#### 1. 复用并部署 CRD
我们继续使用之前的 `SimpleApp` CRD，无需修改其定义。以下是 CRD 的配置文件（与之前一致）：

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: simpleapps.example.com
spec:
  group: example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                appName:
                  type: string
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 10
  scope: Namespaced
  names:
    plural: simpleapps
    singular: simpleapp
    kind: SimpleApp
    shortNames:
      - sapp
```

**部署 CRD**：
```bash
kubectl apply -f simpleapp-crd.yaml
```

验证：
```bash
kubectl get crd simpleapps.example.com
```

---

#### 2. 编写 Go 控制器代码
我们将创建一个简单的 Go 项目，包含：
- CRD 的 Go 类型定义（API）。
- 控制器逻辑，用于监听 `SimpleApp` 资源并打印日志。

##### 项目结构
```
simpleapp-controller/
├── go.mod
├── main.go
├── api/
│   └── v1/
│       └── simpleapp_types.go
├── controllers/
│   └── simpleapp_controller.go
└── Dockerfile
```

##### 步骤 1：初始化 Go 项目
创建一个目录并初始化 Go 模块：
```bash
mkdir simpleapp-controller
cd simpleapp-controller
go mod init simpleapp-controller
```

添加依赖：
```bash
go get sigs.k8s.io/controller-runtime@v0.17.0
go get k8s.io/api@v0.29.0
go get k8s.io/apimachinery@v0.29.0
```

##### 步骤 2：定义 CRD 类型
创建 `api/v1/simpleapp_types.go`，定义 `SimpleApp` 的 Go 结构体，与 CRD 的 schema 保持一致：

```go
package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// SimpleAppSpec defines the desired state of SimpleApp
type SimpleAppSpec struct {
	AppName  string `json:"appName"`
	Replicas int32  `json:"replicas"`
}

// SimpleAppStatus defines the observed state of SimpleApp
type SimpleAppStatus struct {
	// Add status fields if needed
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status

// SimpleApp is the Schema for the simpleapps API
type SimpleApp struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   SimpleAppSpec   `json:"spec,omitempty"`
	Status SimpleAppStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

// SimpleAppList contains a list of SimpleApp
type SimpleAppList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []SimpleApp `json:"items"`
}

func init() {
	SchemeBuilder.Register(&SimpleApp{}, &SimpleAppList{})
}
```

**说明**：
- `SimpleAppSpec`：定义 `appName` 和 `replicas`，与 CRD schema 匹配。
- `SimpleAppStatus`：目前为空，可用于存储资源状态（本例不使用）。
- `+kubebuilder` 注释：用于生成 Kubernetes 资源元数据（由 `controller-tools` 使用，但本例手动编写）。

##### 步骤 3：编写控制器逻辑
创建 `controllers/simpleapp_controller.go`，实现监听 `SimpleApp` 资源的逻辑：

```go
package controllers

import (
	"context"
	"fmt"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	examplecomv1 "simpleapp-controller/api/v1"
)

// SimpleAppReconciler reconciles a SimpleApp object
type SimpleAppReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=example.com,resources=simpleapps,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=example.com,resources=simpleapps/status,verbs=get;update;patch

func (r *SimpleAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx)

	// Fetch the SimpleApp instance
	simpleApp := &examplecomv1.SimpleApp{}
	err := r.Get(ctx, req.NamespacedName, simpleApp)
	if err != nil {
		logger.Error(err, "unable to fetch SimpleApp")
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	// Print "Hello, World!" and SimpleApp details
	logger.Info("Hello, World!", "AppName", simpleApp.Spec.AppName, "Replicas", simpleApp.Spec.Replicas)
	fmt.Printf("Hello, World! AppName: %s, Replicas: %d\n", simpleApp.Spec.AppName, simpleApp.Spec.Replicas)

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager
func (r *SimpleAppReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&examplecomv1.SimpleApp{}).
		Complete(r)
}
```

**说明**：
- `Reconcile`：每次 `SimpleApp` 资源创建或更新时触发，打印 `Hello, World!` 以及 `appName` 和 `replicas`。
- `logger.Info`：将日志写入 Kubernetes 控制器日志。
- `fmt.Printf`：同时打印到控制器的标准输出（便于调试）。
- RBAC 注释：定义控制器需要的权限（读取和更新 `SimpleApp` 资源）。

##### 步骤 4：编写主程序
创建 `main.go`，初始化控制器并运行：

```go
package main

import (
	"flag"
	"os"

	"k8s.io/apimachinery/pkg/runtime"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	_ "k8s.io/client-go/plugin/pkg/client/auth"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/healthz"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"

	examplecomv1 "simpleapp-controller/api/v1"
	"simpleapp-controller/controllers"
)

var (
	scheme = runtime.NewScheme()
)

func init() {
	utilruntime.Must(clientgoscheme.AddToScheme(scheme))
	utilruntime.Must(examplecomv1.AddToScheme(scheme))
}

func main() {
	var metricsAddr string
	var enableLeaderElection bool
	var probeAddr string
	flag.StringVar(&metricsAddr, "metrics-bind-address", ":8080", "The address the metric endpoint binds to.")
	flag.StringVar(&probeAddr, "health-probe-bind-address", ":8081", "The address the probe endpoint binds to.")
	flag.BoolVar(&enableLeaderElection, "leader-elect", false, "Enable leader election for controller manager.")
	flag.Parse()

	ctrl.SetLogger(zap.New(zap.UseDevMode(true)))

	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
		Scheme:                 scheme,
		MetricsBindAddress:     metricsAddr,
		Port:                   9443,
		HealthProbeBindAddress: probeAddr,
		LeaderElection:         enableLeaderElection,
		LeaderElectionID:       "simpleapp-controller.example.com",
	})
	if err != nil {
		ctrl.Log.Error(err, "unable to start manager")
		os.Exit(1)
	}

	if err = (&controllers.SimpleAppReconciler{
		Client: mgr.GetClient(),
		Scheme: mgr.GetScheme(),
	}).SetupWithManager(mgr); err != nil {
		ctrl.Log.Error(err, "unable to create controller", "controller", "SimpleApp")
		os.Exit(1)
	}

	if err := mgr.AddHealthzCheck("healthz", healthz.Ping); err != nil {
		ctrl.Log.Error(err, "unable to set up health check")
		os.Exit(1)
	}
	if err := mgr.AddReadyzCheck("readyz", healthz.Ping); err != nil {
		ctrl.Log.Error(err, "unable to set up ready check")
		os.Exit(1)
	}

	ctrl.Log.Info("starting manager")
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		ctrl.Log.Error(err, "problem running manager")
		os.Exit(1)
	}
}
```

**说明**：
- 初始化 Kubernetes 客户端和 `controller-runtime` 管理器。
- 注册 `SimpleApp` 的 schema。
- 设置 `SimpleAppReconciler` 控制器。

##### 步骤 5：创建 Dockerfile
创建 `Dockerfile` 用于构建控制器镜像：

```dockerfile
```dockerfile
FROM golang:1.20 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o simpleapp-controller .

FROM gcr.io/distroless/static:nonroot
WORKDIR /
COPY --from=builder /app/simpleapp-controller .
USER 65532:65532
ENTRYPOINT ["/simpleapp-controller"]
```
```

**说明**：
- 使用多阶段构建：先编译 Go 程序，然后使用轻量级 `distroless` 镜像运行。
- 非 root 用户运行，增强安全性。

---

#### 3. 构建并推送控制器镜像
1. 构建镜像（替换 `your-dockerhub-username` 为你的 Docker Hub 用户名，或使用其他容器注册表）：
   ```bash
   docker build -t your-dockerhub-username/simpleapp-controller:latest .
   ```

2. 推送镜像：
   ```bash
   docker push your-dockerhub-username/simpleapp-controller:latest
   ```

**本地测试（例如 Minikube）**：
如果使用 Minikube，可以直接加载镜像：
```bash
minikube image load your-dockerhub-username/simpleapp-controller:latest
```

---

#### 4. 部署控制器到 Kubernetes
创建 `controller-deployment.yaml` 来部署控制器：

```yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: simpleapp-controller
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: simpleapp-controller-role
rules:
- apiGroups: ["example.com"]
  resources: ["simpleapps"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["example.com"]
  resources: ["simpleapps/status"]
  verbs: ["get", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: simpleapp-controller-rolebinding
subjects:
- kind: ServiceAccount
  name: simpleapp-controller
  namespace: default
roleRef:
  kind: ClusterRole
  name: simpleapp-controller-role
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simpleapp-controller
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: simpleapp-controller
  template:
    metadata:
      labels:
        app: simpleapp-controller
    spec:
      serviceAccountName: simpleapp-controller
      containers:
      - name: controller
        image: your-dockerhub-username/simpleapp-controller:latest
        imagePullPolicy: Always
```

**说明**：
- `ServiceAccount`：为控制器提供身份。
- `ClusterRole` 和 `ClusterRoleBinding`：授予控制器操作 `SimpleApp` 资源的权限。
- `Deployment`：运行控制器镜像。

**部署**：
```bash
kubectl apply -f controller-deployment.yaml
```

验证控制器是否运行：
```bash
kubectl get pods -n default
```
输出应包含：
```
NAME                                  READY   STATUS    RESTARTS   AGE
simpleapp-controller-<hash>           1/1     Running   0          <time>
```

---

#### 5. 创建 SimpleApp 资源并验证日志
复用之前的 `SimpleApp` 实例：

```yaml
apiVersion: example.com/v1
kind: SimpleApp
metadata:
  name: my-simple-app
  namespace: default
spec:
  appName: my-app
  replicas: 3
```

**部署实例**：
```bash
kubectl apply -f simpleapp-instance.yaml
```

**检查控制器日志**：
```bash
kubectl logs -l app=simpleapp-controller -n default
```

**预期输出**（日志中应包含类似内容）：
```
2025-04-28T12:34:56Z    INFO    Hello, World!   {"AppName": "my-app", "Replicas": 3}
Hello, World! AppName: my-app, Replicas: 3
```

每次创建或更新 `SimpleApp` 资源（例如修改 `replicas`），控制器都会触发 `Reconcile` 并打印日志。

---

#### 6. 清理资源
清理测试资源：
```bash
kubectl delete -f simpleapp-instance.yaml
kubectl delete -f controller-deployment.yaml
kubectl delete -f simpleapp-crd.yaml
```

---

### 代码和部署总结
- **CRD**：定义了 `SimpleApp` 资源，包含禁止使用 `kubectl apply` 部署。
- **控制器**：使用 Go 和 `controller-runtime` 编写的简单控制器，监听 `SimpleApp` 资源并打印日志。
- **功能**：当 `SimpleApp` 资源创建或更新时，打印 `Hello, World!` 和资源信息。
- **部署**：通过 Docker 镜像和 Kubernetes Deployment 运行控制器。

---

### 常见问题
1. **控制器日志没有输出？**
    - 检查控制器 Pod 是否运行：`kubectl get pods -n default`。
    - 查看 Pod 日志：`kubectl logs -l app=simpleapp-controller -n default`。
    - 确保 CRD 和 `SimpleApp` 实例已正确应用。

2. **权限错误？**
    - 确保 `ClusterRole` 和 `ClusterRoleBinding` 已正确应用。
    - 检查控制器是否使用正确的 `ServiceAccount`。

3. **镜像拉取失败？**
    - 确保镜像已推送到注册表或加载到本地（如 Minikube）。
    - 检查 `imagePullPolicy` 和镜像名称。

---

### 扩展建议
- **添加状态**：在 `SimpleAppStatus` 中记录控制器处理状态（例如 `LastProcessedTime`）。
- **实际操作**：让控制器根据 `SimpleApp` 创建 Pod 或 Deployment（例如部署 NGINX）。
- **事件记录**：使用 `r.Recorder` 记录 Kubernetes 事件（`kubectl get events`）。
- **工具支持**：使用 Kubebuilder 或 Operator SDK 生成更完整的控制器框架。

如果你需要进一步扩展（例如让控制器创建 Pod 或添加更复杂逻辑），请告诉我，我可以提供更详细的代码和指导！

---

