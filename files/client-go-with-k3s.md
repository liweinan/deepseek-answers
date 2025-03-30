# Why client-go Works with k3s

Yes, **client-go** (the official Kubernetes Go client library) can operate **k3s**, as **k3s is a fully compliant Kubernetes distribution**.

### **Why client-go Works with k3s**
1. **k3s is Kubernetes** – It passes the **Kubernetes Conformance Tests**, meaning it supports the standard Kubernetes API.
2. **client-go interacts with the Kubernetes API** – Since k3s exposes the same API as standard Kubernetes, client-go can manage resources (Pods, Deployments, Services, etc.) just like with any other K8s cluster.

---

### **How to Use client-go with k3s**
#### 1. **Get k3s kubeconfig**
By default, k3s stores its kubeconfig at:
```sh
/etc/rancher/k3s/k3s.yaml
```
You may need to:
- Copy it to `~/.kube/config` (default location for `kubectl` and `client-go`).
- Or explicitly load it in your Go code.

#### 2. **Example: Using client-go with k3s**
Here’s a simple Go snippet that lists Pods in the `default` namespace:

```go
package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

func main() {
	// Load kubeconfig (usually from ~/.kube/config or /etc/rancher/k3s/k3s.yaml)
	kubeconfig := filepath.Join(homedir.HomeDir(), ".kube", "config")
	if _, err := os.Stat(kubeconfig); os.IsNotExist(err) {
		kubeconfig = "/etc/rancher/k3s/k3s.yaml" // Fallback to k3s default
	}

	config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
	if err != nil {
		panic(err.Error())
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err.Error())
	}

	// List Pods in the default namespace
	pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		panic(err.Error())
	}

	fmt.Println("Pods in default namespace:")
	for _, pod := range pods.Items {
		fmt.Printf("- %s\n", pod.Name)
	}
}
```

#### 3. **Run the Code**
```sh
go run main.go
```
If connected correctly, it will list Pods in your k3s cluster.

---

### **Possible Issues & Fixes**
1. **Permission Issues**
    - Ensure your kubeconfig (`k3s.yaml`) has the right permissions.
    - If running k3s as root, you might need:
      ```sh
      sudo chmod 644 /etc/rancher/k3s/k3s.yaml
      ```  

2. **Firewall/Network Issues**
    - By default, k3s API runs on port `6443`. Make sure it’s accessible.

3. **TLS Errors**
    - If using a self-signed cert (common in k3s), you might need to disable TLS verification in `client-go`:
      ```go
      config.TLSClientConfig.Insecure = true // Not recommended for production!
      ```  

---

### **Conclusion**
✅ **Yes, client-go works perfectly with k3s** since k3s is a lightweight but fully compatible Kubernetes distribution.  
✅ Use standard `client-go` methods to interact with k3s just like any other K8s cluster.  
✅ Ensure proper `kubeconfig` setup and permissions.

Would you like help with a specific use case (e.g., CRDs, custom controllers)? 🚀