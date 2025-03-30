# 使用 client-go 操作 Kubernetes 的完整指南

client-go 是 Kubernetes 官方提供的 Go 语言客户端库，用于与 Kubernetes API 交互。以下是详细的使用方法和实践示例。

## 1. 安装与初始化

### 安装 client-go
```bash
go get k8s.io/client-go@v0.24.0
```

### 基本客户端配置
```go
import (
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
)

func main() {
    // 使用kubeconfig文件创建配置
    kubeconfig := filepath.Join(os.Getenv("HOME"), ".kube", "config")
    config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        panic(err.Error())
    }

    // 创建clientset
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        panic(err.Error())
    }
}
```

## 2. 核心资源操作

### 2.1 Pod 操作示例

#### 列出所有Pod
```go
pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{})
for _, pod := range pods.Items {
    fmt.Printf("Pod: %s\n", pod.Name)
}
```

#### 创建Pod
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

#### 删除Pod
```go
err := clientset.CoreV1().Pods("default").Delete(context.TODO(), "demo-pod", metav1.DeleteOptions{})
```

### 2.2 Deployment 操作

#### 创建Deployment
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

### 2.3 Service 操作

#### 创建Service
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

## 3. 高级功能

### 3.1 Watch 机制（实时监听）

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

### 3.2 Informer 模式（推荐生产使用）

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

// 防止主程序退出
select {}
```

### 3.3 自定义资源(CRD)操作

```go
import (
    apiextensionsv1 "k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1"
    apiextensionsclient "k8s.io/apiextensions-apiserver/pkg/client/clientset/clientset"
)

// 创建CRD客户端
apiextensionsClient, err := apiextensionsclient.NewForConfig(config)

// 定义CRD
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

// 创建CRD
_, err = apiextensionsClient.ApiextensionsV1().CustomResourceDefinitions().Create(context.TODO(), crd, metav1.CreateOptions{})
```

## 4. 实用技巧

### 4.1 动态客户端（处理未知资源）

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

// 列出所有命名空间的Deployment
unstructuredList, err := dynamicClient.Resource(gvr).Namespace("").List(context.TODO(), metav1.ListOptions{})
```

### 4.2 客户端过滤和选择器

```go
// 使用字段选择器
pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{
    FieldSelector: "status.phase=Running",
})

// 使用标签选择器
pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{
    LabelSelector: "app=frontend",
})
```

### 4.3 错误处理

```go
if errors.IsNotFound(err) {
    fmt.Println("资源不存在")
} else if statusError, isStatus := err.(*errors.StatusError); isStatus {
    fmt.Printf("API错误: %v\n", statusError.ErrStatus.Message)
} else if err != nil {
    panic(err.Error())
} else {
    fmt.Println("操作成功")
}
```

## 5. 生产环境最佳实践

1. **使用Informer代替直接API调用**：减少API Server压力
2. **实现重试机制**：处理临时网络问题
3. **限制QPS**：避免API Server过载
   ```go
   config.QPS = 50
   config.Burst = 100
   ```
4. **使用Context控制超时**：
   ```go
   ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
   defer cancel()
   
   _, err := clientset.CoreV1().Pods("default").Get(ctx, "demo-pod", metav1.GetOptions{})
   ```

## 6. 测试工具

### 6.1 伪造客户端测试

```go
import (
    "k8s.io/client-go/kubernetes/fake"
)

func TestPodCreation(t *testing.T) {
    // 创建fake客户端
    clientset := fake.NewSimpleClientset()
    
    // 测试创建Pod
    pod := &v1.Pod{ObjectMeta: metav1.ObjectMeta{Name: "test-pod"}}
    _, err := clientset.CoreV1().Pods("default").Create(context.TODO(), pod, metav1.CreateOptions{})
    if err != nil {
        t.Fatalf("创建Pod失败: %v", err)
    }
    
    // 验证Pod存在
    _, err = clientset.CoreV1().Pods("default").Get(context.TODO(), "test-pod", metav1.GetOptions{})
    if err != nil {
        t.Fatalf("获取Pod失败: %v", err)
    }
}
```

### 6.2 集成测试环境

```go
import (
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/test-infra/kubetest/kind"
)

func TestIntegration(t *testing.T) {
    // 启动本地kind集群
    cluster := kind.NewCluster("test-cluster")
    if err := cluster.Create(); err != nil {
        t.Fatal(err)
    }
    defer cluster.Delete()
    
    // 获取kubeconfig
    kubeconfig, err := cluster.Kubeconfig()
    if err != nil {
        t.Fatal(err)
    }
    
    // 创建真实客户端
    config, err := clientcmd.RESTConfigFromKubeConfig([]byte(kubeconfig))
    clientset, err := kubernetes.NewForConfig(config)
    
    // 执行测试...
}
```

## 7. 性能优化

1. **批量操作**：
   ```go
   // 批量删除Pod
   err := clientset.CoreV1().Pods("default").DeleteCollection(
       context.TODO(),
       metav1.DeleteOptions{},
       metav1.ListOptions{LabelSelector: "app=old"},
   )
   ```

2. **并行处理**：
   ```go
   var wg sync.WaitGroup
   pods, _ := clientset.CoreV1().Pods("").List(context.TODO(), metav1.ListOptions{})
   
   for _, pod := range pods.Items {
       wg.Add(1)
       go func(p v1.Pod) {
           defer wg.Done()
           // 处理每个Pod
       }(pod)
   }
   wg.Wait()
   ```

3. **缓存响应**：
   ```go
   import "k8s.io/client-go/discovery/cached/memory"
   
   cachedDiscoveryClient := memory.NewMemCacheClient(clientset.Discovery())
   ```

client-go 是 Kubernetes 生态中最强大的客户端库之一，通过合理使用其各种功能，可以构建高效可靠的 Kubernetes 操作工具和控制器。