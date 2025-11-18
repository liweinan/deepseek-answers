# Complete Guide to Operating Kubernetes with client-go

client-go is the official Go language client library provided by Kubernetes for interacting with the Kubernetes API. Below are detailed usage methods and practical examples.

## 1. Installation and Initialization

### Install client-go
```bash
go get k8s.io/client-go@v0.24.0
```

### Basic Client Configuration
```go
import (
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
)

func main() {
    // Create configuration using kubeconfig file
    kubeconfig := filepath.Join(os.Getenv("HOME"), ".kube", "config")
    config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        panic(err.Error())
    }

    // Create clientset
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        panic(err.Error())
    }
}
```

## 2. Core Resource Operations

### 2.1 Pod Operations Examples

#### List All Pods
```go
pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{})
for _, pod := range pods.Items {
    fmt.Printf("Pod: %s\n", pod.Name)
}
```

#### Create Pod
```go
pod := &v1.Pod{
    ObjectMeta: metav1.ObjectMeta{
        Name: "demo-pod",
    },
    Spec: v1.PodSpec{
        Containers: []v1.Container{
            {
                Name:  "nginx",
                Image: "nginx:latest",
                Ports: []v1.ContainerPort{
                    {
                        ContainerPort: 80,
                    },
                },
            },
        },
    },
}

result, err := clientset.CoreV1().Pods("default").Create(context.TODO(), pod, metav1.CreateOptions{})
```

#### Delete Pod
```go
err := clientset.CoreV1().Pods("default").Delete(context.TODO(), "demo-pod", metav1.DeleteOptions{})
```

### 2.2 Deployment Operations

#### Create Deployment
```go
deployment := &appsv1.Deployment{
    ObjectMeta: metav1.ObjectMeta{
        Name: "demo-deployment",
    },
    Spec: appsv1.DeploymentSpec{
        Replicas: int32Ptr(3),
        Selector: &metav1.LabelSelector{
            MatchLabels: map[string]string{
                "app": "demo",
            },
        },
        Template: v1.PodTemplateSpec{
            ObjectMeta: metav1.ObjectMeta{
                Labels: map[string]string{
                    "app": "demo",
                },
            },
            Spec: v1.PodSpec{
                Containers: []v1.Container{
                    {
                        Name:  "web",
                        Image: "nginx:1.19",
                        Ports: []v1.ContainerPort{
                            {
                                ContainerPort: 80,
                            },
                        },
                    },
                },
            },
        },
    },
}

result, err := clientset.AppsV1().Deployments("default").Create(context.TODO(), deployment, metav1.CreateOptions{})
```

### 2.3 Service Operations

#### Create Service
```go
service := &v1.Service{
    ObjectMeta: metav1.ObjectMeta{
        Name: "demo-service",
    },
    Spec: v1.ServiceSpec{
        Selector: map[string]string{
            "app": "demo",
        },
        Ports: []v1.ServicePort{
            {
                Protocol:   "TCP",
                Port:       80,
                TargetPort: intstr.FromInt(80),
            },
        },
    },
}

result, err := clientset.CoreV1().Services("default").Create(context.TODO(), service, metav1.CreateOptions{})
```

## 3. Advanced Features

### 3.1 Watch Mechanism (Real-time Monitoring)

```go
watchInterface, err := clientset.CoreV1().Pods("default").Watch(context.TODO(), metav1.ListOptions{})
if err != nil {
    panic(err.Error())
}

for event := range watchInterface.ResultChan() {
    pod := event.Object.(*v1.Pod)
    fmt.Printf("Event: %s Pod: %s\n", event.Type, pod.Name)
}
```

### 3.2 Informer Pattern (Recommended for Production)

```go
import (
    "k8s.io/client-go/informers"
    "k8s.io/client-go/tools/cache"
)

factory := informers.NewSharedInformerFactory(clientset, 0)
podInformer := factory.Core().V1().Pods().Informer()

podInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
    AddFunc: func(obj interface{}) {
        pod := obj.(*v1.Pod)
        fmt.Printf("Pod added: %s\n", pod.Name)
    },
    UpdateFunc: func(oldObj, newObj interface{}) {
        oldPod := oldObj.(*v1.Pod)
        newPod := newObj.(*v1.Pod)
        fmt.Printf("Pod updated: %s -> %s\n", oldPod.ResourceVersion, newPod.ResourceVersion)
    },
    DeleteFunc: func(obj interface{}) {
        pod := obj.(*v1.Pod)
        fmt.Printf("Pod deleted: %s\n", pod.Name)
    },
})

stopCh := make(chan struct{})
defer close(stopCh)
go podInformer.Run(stopCh)

if !cache.WaitForCacheSync(stopCh, podInformer.HasSynced) {
    panic("Timed out waiting for caches to sync")
}

// Prevent main program from exiting
select {}
```

### 3.3 Custom Resource (CRD) Operations

```go
import (
    apiextensionsv1 "k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1"
    apiextensionsclient "k8s.io/apiextensions-apiserver/pkg/client/clientset/clientset"
)

// Create CRD client
apiextensionsClient, err := apiextensionsclient.NewForConfig(config)

// Define CRD
crd := &apiextensionsv1.CustomResourceDefinition{
    ObjectMeta: metav1.ObjectMeta{
        Name: "foos.example.com",
    },
    Spec: apiextensionsv1.CustomResourceDefinitionSpec{
        Group: "example.com",
        Versions: []apiextensionsv1.CustomResourceDefinitionVersion{
            {
                Name:    "v1",
                Served:  true,
                Storage: true,
                Schema: &apiextensionsv1.CustomResourceValidation{
                    OpenAPIV3Schema: &apiextensionsv1.JSONSchemaProps{
                        Type: "object",
                        Properties: map[string]apiextensionsv1.JSONSchemaProps{
                            "spec": {
                                Type: "object",
                                Properties: map[string]apiextensionsv1.JSONSchemaProps{
                                    "foo": {
                                        Type: "string",
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        Scope: apiextensionsv1.NamespaceScoped,
        Names: apiextensionsv1.CustomResourceDefinitionNames{
            Plural:   "foos",
            Singular: "foo",
            Kind:     "Foo",
        },
    },
}

// Create CRD
_, err = apiextensionsClient.ApiextensionsV1().CustomResourceDefinitions().Create(context.TODO(), crd, metav1.CreateOptions{})
```

## 4. Practical Tips

### 4.1 Dynamic Client (Handling Unknown Resources)

```go
import (
    "k8s.io/client-go/dynamic"
    "k8s.io/apimachinery/pkg/runtime/schema"
)

dynamicClient, err := dynamic.NewForConfig(config)

gvr := schema.GroupVersionResource{
    Group:    "apps",
    Version:  "v1",
    Resource: "deployments",
}

// List Deployments in all namespaces
unstructuredList, err := dynamicClient.Resource(gvr).Namespace("").List(context.TODO(), metav1.ListOptions{})
```

### 4.2 Client Filtering and Selectors

```go
// Use field selector
pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{
    FieldSelector: "status.phase=Running",
})

// Use label selector
pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{
    LabelSelector: "app=frontend",
})
```

### 4.3 Error Handling

```go
if errors.IsNotFound(err) {
    fmt.Println("Resource does not exist")
} else if statusError, isStatus := err.(*errors.StatusError); isStatus {
    fmt.Printf("API error: %v\n", statusError.ErrStatus.Message)
} else if err != nil {
    panic(err.Error())
} else {
    fmt.Println("Operation successful")
}
```

## 5. Production Best Practices

1. **Use Informer instead of direct API calls**: Reduces API Server pressure
2. **Implement retry mechanisms**: Handles temporary network issues
3. **Limit QPS**: Prevents API Server overload
   ```go
   config.QPS = 50
   config.Burst = 100
   ```
4. **Use Context to control timeout**:
   ```go
   ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
   defer cancel()
   
   _, err := clientset.CoreV1().Pods("default").Get(ctx, "demo-pod", metav1.GetOptions{})
   ```

## 6. Testing Tools

### 6.1 Fake Client Testing

```go
import (
    "k8s.io/client-go/kubernetes/fake"
)

func TestPodCreation(t *testing.T) {
    // Create fake client
    clientset := fake.NewSimpleClientset()
    
    // Test Pod creation
    pod := &v1.Pod{ObjectMeta: metav1.ObjectMeta{Name: "test-pod"}}
    _, err := clientset.CoreV1().Pods("default").Create(context.TODO(), pod, metav1.CreateOptions{})
    if err != nil {
        t.Fatalf("Pod creation failed: %v", err)
    }
    
    // Verify Pod exists
    _, err = clientset.CoreV1().Pods("default").Get(context.TODO(), "test-pod", metav1.GetOptions{})
    if err != nil {
        t.Fatalf("Failed to get Pod: %v", err)
    }
}
```

### 6.2 Integration Test Environment

```go
import (
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/test-infra/kubetest/kind"
)

func TestIntegration(t *testing.T) {
    // Start local kind cluster
    cluster := kind.NewCluster("test-cluster")
    if err := cluster.Create(); err != nil {
        t.Fatal(err)
    }
    defer cluster.Delete()
    
    // Get kubeconfig
    kubeconfig, err := cluster.Kubeconfig()
    if err != nil {
        t.Fatal(err)
    }
    
    // Create real client
    config, err := clientcmd.RESTConfigFromKubeConfig([]byte(kubeconfig))
    clientset, err := kubernetes.NewForConfig(config)
    
    // Execute tests...
}
```

## 7. Performance Optimization

1. **Batch Operations**:
   ```go
   // Batch delete Pods
   err := clientset.CoreV1().Pods("default").DeleteCollection(
       context.TODO(),
       metav1.DeleteOptions{},
       metav1.ListOptions{LabelSelector: "app=old"},
   )
   ```

2. **Parallel Processing**:
   ```go
   var wg sync.WaitGroup
   pods, _ := clientset.CoreV1().Pods("").List(context.TODO(), metav1.ListOptions{})
   
   for _, pod := range pods.Items {
       wg.Add(1)
       go func(p v1.Pod) {
           defer wg.Done()
           // Process each Pod
       }(pod)
   }
   wg.Wait()
   ```

3. **Cache Responses**:
   ```go
   import "k8s.io/client-go/discovery/cached/memory"
   
   cachedDiscoveryClient := memory.NewMemCacheClient(clientset.Discovery())
   ```

client-go is one of the most powerful client libraries in the Kubernetes ecosystem. By properly utilizing its various features, you can build efficient and reliable Kubernetes operation tools and controllers.