# A Minimal **Kubernetes Custom Resource Definition (CRD)** Tutorial

Below is a minimal **Kubernetes Custom Resource Definition (CRD)** tutorial that guides you through how to write, deploy, and use CRDs in an existing Kubernetes cluster. The tutorial is in English, concise, covers core steps, and includes necessary code examples.

---

### What is CRD?
CRD (Custom Resource Definition) allows you to define custom resources in Kubernetes, extending the Kubernetes API so you can manage custom objects just like built-in resources (such as Pods, Deployments). CRDs are commonly used to implement custom controllers or extend Kubernetes functionality.

---

### Tutorial Objectives
We will:
1. Create a simple CRD that defines a custom resource named `SimpleApp`.
2. Deploy the CRD to a Kubernetes cluster.
3. Create a `SimpleApp` custom resource instance.
4. Verify the deployment results.

---

### Environment Preparation
- A running Kubernetes cluster (can use Minikube, Kind, or cloud clusters).
- `kubectl` is configured and can access the cluster.
- Text editor (such as VS Code) or operate directly in terminal.

---

### Steps

#### 1. Write CRD Definition
We will define a simple CRD named `SimpleApp` that contains the following fields:
- `appName`: The name of the application.
- `replicas`: The number of replicas.

Create file `simpleapp-crd.yaml`:

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


**Explanation**:
- `group`: The API group for the custom resource (`example.com`).
- `versions`: Defines the version of the CRD (here it's `v1`).
- `schema`: Defines the resource structure, `appName` is a string, `replicas` is an integer from 1 to 10.
- `scope`: `Namespaced` indicates the resource is namespace-level (rather than cluster-level).
- `names`: Defines the resource name, plural form, and short names.

---

#### 2. Deploy CRD to Cluster

Use `kubectl` to apply the CRD definition:

```bash
kubectl apply -f simpleapp-crd.yaml
```

Verify the CRD was created successfully:

```bash
kubectl get crd
```

Output should include:

```
NAME                     CREATED AT
simpleapps.example.com   <creation time>
```

---

#### 3. Create Custom Resource Instance
Now we create a `SimpleApp` resource instance. Create file `simpleapp-instance.yaml`:

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


**Explanation**:
- `apiVersion`: Uses the `group` and `version` defined in CRD (`example.com/v1`).
- `kind`: Uses the `kind` defined in CRD (`SimpleApp`).
- `spec`: Contains `appName` and `replicas`, matching the CRD schema.

Deploy the instance:
```bash
kubectl apply -f simpleapp-instance.yaml
```

---

#### 4. Verify Custom Resource
Check if the `SimpleApp` resource was created successfully:
```bash
kubectl get simpleapps
```
Output:
```
NAME             AGE
my-simple-app    <creation time>
```

View resource details:
```bash
kubectl describe simpleapp my-simple-app
```
Output will show the resource's `metadata` and `spec`, for example:
```
Name:         my-simple-app
Namespace:    default
API Version:  example.com/v1
Kind:         SimpleApp
Spec:
  App Name:   my-app
  Replicas:   3
```

You can also use the short name:
```bash
kubectl get sapp
```

---

#### 5. (Optional) Clean Up Resources
If you need to delete the created resources:
```bash
kubectl delete -f simpleapp-instance.yaml
kubectl delete -f simpleapp-crd.yaml
```

Note: Deleting the CRD will also delete all related custom resource instances.

---

### Next Steps
- **Add Controller**: CRD itself only defines data structure. To make `SimpleApp` resources actually trigger behaviors (like creating Pods), you need to write a custom controller (Operator). You can use tools like [Operator SDK](https://sdk.operatorframework.io/) or [Kubebuilder](https://book.kubebuilder.io/) to implement it.
- **Extend CRD**: You can add more fields (like `image`, `port`) or support multi-version APIs.
- **Access Control**: Configure RBAC for CRD to ensure only authorized users can operate it.

---

### Common Issues
1. **CRD not appearing in `kubectl get crd`**?
    - Check if `simpleapp-crd.yaml` was applied correctly: `kubectl apply -f simpleapp-crd.yaml`.
    - View events: `kubectl describe crd simpleapps.example.com`.

2. **Custom resource creation failed**?
    - Ensure `apiVersion` and `kind` match the CRD definition.
    - Check if schema matches: `kubectl describe simpleapp my-simple-app`.

3. **How to test controller**?
    - This tutorial only creates CRD, doesn't implement controller. If you need a controller, recommend learning Operator SDK or Kubebuilder.

---

### Summary
Through the above steps, you have:
- Defined and deployed a simple CRD (`SimpleApp`).
- Created a custom resource instance.
- Verified the resource status in the cluster.

This CRD is a basic example, suitable for learning and extension. If you need more complex CRDs (like multi-version support, complex schema) or want to implement custom controllers, please let me know, I can provide more detailed tutorials!

--- 

Great! We will extend the previous `SimpleApp` CRD by adding a simple feature: when creating or updating `SimpleApp` resources, print `Hello, World!` along with the resource's `appName` and `replicas` information in the Kubernetes cluster logs. For this, we need to write a simple **custom controller** (Custom Controller) to listen for `SimpleApp` resource changes and implement the log printing logic. The controller will be written using **Go** language and the **controller-runtime** library.

---

### Objectives
1. Extend the existing `SimpleApp` CRD, keeping its structure (`appName` and `replicas`).
2. Write a simple Go controller that listens for `SimpleApp` resource creation and update events, and prints `Hello, World!` along with resource information in the logs.
3. Provide steps to deploy the controller, ensuring it runs in the Kubernetes cluster.
4. Include all necessary code and configuration files, keeping it minimal.

---

### Environment Preparation
- **Kubernetes Cluster**: Running and accessible via `kubectl`.
- **Go Environment**: Go 1.20 or higher (recommended to use latest version).
- **Tools**:
    - `kubectl`: For applying CRD and deploying controller.
    - `docker`: For building controller images.
    - A container registry (such as Docker Hub) or local image support (such as Minikube).
- **Code Dependencies**:
    - `controller-runtime`: Kubernetes controller framework.
    - `k8s.io/api` and `k8s.io/apimachinery`: Kubernetes API libraries.

---

### Steps

#### 1. Reuse and Deploy CRD
We continue using the previous `SimpleApp` CRD without modifying its definition. Here's the CRD configuration file (same as before):

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

**Deploy CRD**:
```bash
kubectl apply -f simpleapp-crd.yaml
```

Verify:
```bash
kubectl get crd simpleapps.example.com
```

---

#### 2. Write Go Controller Code
We will create a simple Go project containing:
- Go type definitions for CRD (API).
- Controller logic to listen for `SimpleApp` resources and print logs.

##### Project Structure
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

##### Step 1: Initialize Go Project
Create a directory and initialize Go module:
```bash
mkdir simpleapp-controller
cd simpleapp-controller
go mod init simpleapp-controller
```

Add dependencies:
```bash
go get sigs.k8s.io/controller-runtime@v0.17.0
go get k8s.io/api@v0.29.0
go get k8s.io/apimachinery@v0.29.0
```

##### Step 2: Define CRD Types
Create `api/v1/simpleapp_types.go`, defining `SimpleApp` Go structs consistent with CRD schema:

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

**Explanation**:
- `SimpleAppSpec`: Defines `appName` and `replicas`, matching CRD schema.
- `SimpleAppStatus`: Currently empty, can be used to store resource status (not used in this example).
- `+kubebuilder` annotations: Used to generate Kubernetes resource metadata (used by `controller-tools`, but manually written in this example).

##### Step 3: Write Controller Logic
Create `controllers/simpleapp_controller.go`, implementing logic to listen for `SimpleApp` resources:

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

**Explanation**:
- `Reconcile`: Triggered every time `SimpleApp` resource is created or updated, prints `Hello, World!` along with `appName` and `replicas`.
- `logger.Info`: Writes logs to Kubernetes controller logs.
- `fmt.Printf`: Also prints to controller's standard output (for debugging).
- RBAC annotations: Define permissions required by the controller (read and update `SimpleApp` resources).

##### Step 4: Write Main Program
Create `main.go`, initialize controller and run:

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

**Explanation**:
- Initializes Kubernetes client and `controller-runtime` manager.
- Registers `SimpleApp` schema.
- Sets up `SimpleAppReconciler` controller.

##### Step 5: Create Dockerfile
Create `Dockerfile` for building controller images:

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

**Explanation**:
- Uses multi-stage build: first compiles Go program, then uses lightweight `distroless` image to run.
- Runs as non-root user for enhanced security.

---

#### 3. Build and Push Controller Image
1. Build image (replace `your-dockerhub-username` with your Docker Hub username, or use other container registry):
   ```bash
   docker build -t your-dockerhub-username/simpleapp-controller:latest .
   ```

2. Push image:
   ```bash
   docker push your-dockerhub-username/simpleapp-controller:latest
   ```

**Local Testing (e.g., Minikube)**:
If using Minikube, you can directly load image:
```bash
minikube image load your-dockerhub-username/simpleapp-controller:latest
```

---

#### 4. Deploy Controller to Kubernetes
Create `controller-deployment.yaml` to deploy controller:

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

**Explanation**:
- `ServiceAccount`: Provides identity for the controller.
- `ClusterRole` and `ClusterRoleBinding`: Grant controller permissions to operate `SimpleApp` resources.
- `Deployment`: Runs controller image.

**Deploy**:
```bash
kubectl apply -f controller-deployment.yaml
```

Verify controller is running:
```bash
kubectl get pods -n default
```
Output should include:
```
NAME                                  READY   STATUS    RESTARTS   AGE
simpleapp-controller-<hash>           1/1     Running   0          <time>
```

---

#### 5. Create SimpleApp Resource and Verify Logs
Reuse the previous `SimpleApp` instance:

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

**Deploy Instance**:
```bash
kubectl apply -f simpleapp-instance.yaml
```

**Check Controller Logs**:
```bash
kubectl logs -l app=simpleapp-controller -n default
```

**Expected Output** (logs should contain similar content):
```
2025-04-28T12:34:56Z    INFO    Hello, World!   {"AppName": "my-app", "Replicas": 3}
Hello, World! AppName: my-app, Replicas: 3
```

Every time `SimpleApp` resource is created or updated (such as modifying `replicas`), the controller will trigger `Reconcile` and print logs.

---

#### 6. Clean Up Resources
Clean up test resources:
```bash
kubectl delete -f simpleapp-instance.yaml
kubectl delete -f controller-deployment.yaml
kubectl delete -f simpleapp-crd.yaml
```

---

### Code and Deployment Summary
- **CRD**: Defines `SimpleApp` resource, deployed using `kubectl apply`.
- **Controller**: Simple controller written using Go and `controller-runtime`, listens for `SimpleApp` resources and prints logs.
- **Functionality**: When `SimpleApp` resource is created or updated, prints `Hello, World!` and resource information.
- **Deployment**: Runs controller through Docker image and Kubernetes Deployment.

---

### Common Issues
1. **No controller log output?**
    - Check if controller Pod is running: `kubectl get pods -n default`.
    - View Pod logs: `kubectl logs -l app=simpleapp-controller -n default`.
    - Ensure CRD and `SimpleApp` instances are correctly applied.

2. **Permission errors?**
    - Ensure `ClusterRole` and `ClusterRoleBinding` are correctly applied.
    - Check if controller is using correct `ServiceAccount`.

3. **Image pull failed?**
    - Ensure image is pushed to registry or loaded locally (such as Minikube).
    - Check `imagePullPolicy` and image name.

---

### Extension Suggestions
- **Add Status**: Record controller processing status in `SimpleAppStatus` (such as `LastProcessedTime`).
- **Actual Operations**: Let controller create Pods or Deployments based on `SimpleApp` (such as deploying NGINX).
- **Event Recording**: Use `r.Recorder` to record Kubernetes events (`kubectl get events`).
- **Tool Support**: Use Kubebuilder or Operator SDK to generate more complete controller frameworks.

If you need further extensions (such as having the controller create Pods or add more complex logic), please let me know, I can provide more detailed code and guidance!