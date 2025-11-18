# Accessing **Service** through **Ingress** on Local Machine typically involves a **Kubernetes (K8s)** environment. Here are detailed steps, assuming you already have a Kubernetes cluster running locally (such as Minikube, Kind, or Docker Desktop K8s).

---

## **1. Ensure Kubernetes Environment is Ready**
First, confirm your Kubernetes cluster is running normally and has **Ingress Controller** installed (such as Nginx Ingress, Traefik, etc.).

### **1.1 Check Cluster Status**
```bash
kubectl cluster-info
kubectl get nodes
```

### **1.2 Install Ingress Controller**
#### **Minikube**
```bash
minikube addons enable ingress
```
#### **Docker Desktop / Kind**
Install Nginx Ingress:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```
Wait for Ingress Controller to be ready:
```bash
kubectl get pods -n ingress-nginx
```

---

## **2. Deploy Example Service**
Assume we want to access a simple `nginx` service.

### **2.1 Create Deployment**
```bash
kubectl create deployment nginx --image=nginx
```

### **2.2 Create Service**
```bash
kubectl expose deployment nginx --port=80
```
Check Service:
```bash
kubectl get svc nginx
```
Example output:
```
NAME    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
nginx   ClusterIP   10.96.123.123   <none>        80/TCP    10s
```

---

## **3. Create Ingress Rules**
Ingress defines how to route external traffic to Service.

### **3.1 Write Ingress YAML**
Create `ingress.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
spec:
  rules:
  - host: nginx.local  # Local test domain
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
```

### **3.2 Apply Ingress**
```bash
kubectl apply -f ingress.yaml
```
Check Ingress:
```bash
kubectl get ingress
```
Example output:
```
NAME           CLASS   HOSTS         ADDRESS        PORTS   AGE
nginx-ingress  nginx   nginx.local   192.168.49.2   80      10s
```

---

## **4. Access Service Locally**
Since Ingress is usually bound to a domain name (like `nginx.local`), we need to configure hosts resolution locally.

### **4.1 Get Ingress IP**
```bash
kubectl get ingress nginx-ingress
```
Example output:
```
NAME           CLASS   HOSTS         ADDRESS        PORTS   AGE
nginx-ingress  nginx   nginx.local   192.168.49.2   80      10s
```
The `ADDRESS` here (like `192.168.49.2`) is the Ingress Controller's IP.

### **4.2 Modify Local hosts File**
- **Linux/Mac**:
  ```bash
  sudo echo "192.168.49.2 nginx.local" >> /etc/hosts
  ```
- **Windows** (administrator privileges):
  ```powershell
  Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "192.168.49.2 nginx.local"
  ```

### **4.3 Access Service**
Now, you can access in browser or terminal:
```bash
curl http://nginx.local
```
Or directly open in browser:
```
http://nginx.local
```
You should see the Nginx welcome page.

---

## **5. Optional: Use Port Forwarding (No Ingress)**
If you don't want to configure Ingress, you can directly use `kubectl port-forward`:
```bash
kubectl port-forward svc/nginx 8080:80
```
Then access:
```
http://localhost:8080
```

---

## **6. Clean Up Resources**
```bash
kubectl delete ingress nginx-ingress
kubectl delete svc nginx
kubectl delete deployment nginx
```

---

## **Summary**
| Step | Operation |
|------|------|
| 1. Start K8s Cluster | `minikube start` or `kind create cluster` |
| 2. Install Ingress Controller | `minikube addons enable ingress` |
| 3. Deploy Service | `kubectl create deployment` + `kubectl expose` |
| 4. Create Ingress | `kubectl apply -f ingress.yaml` |
| 5. Modify Local hosts | `echo "IP nginx.local" >> /etc/hosts` |
| 6. Access Service | `curl http://nginx.local` |

This way, you can access Kubernetes Service through Ingress locally! 🚀


---

# Solving Ingress-Nginx Controller External-IP Pending Issue

When your `ingress-nginx-controller` Service's `EXTERNAL-IP` displays as `<pending>`, this usually means your Kubernetes environment doesn't have an available external load balancer. Here are detailed solutions:

## 1. Problem Cause Analysis

In local development environments (like Minikube, Kind, K3s, MicroK8s, etc.), `LoadBalancer` type Services cannot automatically obtain external IPs because:
- Local environments typically don't have cloud provider load balancer integration
- Additional components are needed to simulate load balancer behavior

## 2. Solutions (Choose Based on Your Environment)

### Option A: Use Minikube (If You're Using Minikube)

```bash
minikube tunnel
```
Run this command in another terminal, it will assign external IPs to LoadBalancer type Services.

### Option B: Use MetalLB (For Kind/K3s/MicroK8s/Bare Metal Clusters)

1. Install MetalLB:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.7/config/manifests/metallb-native.yaml
   ```

2. Configure IP address pool (modify following configuration then apply):
   ```yaml
   apiVersion: metallb.io/v1beta1
   kind: IPAddressPool
   metadata:
     name: default-pool
     namespace: metallb-system
   spec:
     addresses:
     - 192.168.1.100-192.168.1.200  # Use your local network's available IP range
   ---
   apiVersion: metallb.io/v1beta1
   kind: L2Advertisement
   metadata:
     name: l2-advert
     namespace: metallb-system
   ```

3. Apply configuration:
   ```bash
   kubectl apply -f metallb-config.yaml
   ```

### Option C: Switch to NodePort (Quick Testing Solution)

Modify ingress-nginx-controller Service type:
```bash
kubectl patch svc ingress-nginx-controller -n ingress-nginx -p '{"spec":{"type":"NodePort"}}'
```
Then access through node IP and assigned port (like `http://<node-ip>:30236`).

### Option D: If You're MicroK8s User

```bash
microk8s enable metallb
```
Then follow prompts to configure IP address range.

## 3. Verify Solution

After applying solution, check Service status:
```bash
kubectl get svc -n ingress-nginx -w
```
Wait for `EXTERNAL-IP` to change from `<pending>` to actual IP address.

## 4. Access Your Ingress

After getting external IP:
1. Point your domain (like `nginx.local`) to this IP (modify `/etc/hosts` file)
2. Access your service:
   ```bash
   curl http://nginx.local
   ```

## 5. Common Issues Troubleshooting

1. **MetalLB not properly configured**:
   ```bash
   kubectl logs -n metallb-system -l app=metallb -c controller
   ```

2. **IP address pool unavailable**:
   - Ensure configured IP range is unused in your local network
   - Check ARP response:
     ```bash
     tcpdump -i any arp
     ```

3. **Firewall blocking**:
   - Ensure your firewall allows traffic through assigned ports

## 6. Recommended Solutions by Environment

| Environment | Recommended Solution | Notes |
|-------------|---------------------|--------|
| Minikube | `minikube tunnel` | Simplest solution |
| Kind | MetalLB | Requires additional installation |
| K3s | MetalLB or Traefik | K3s comes with Traefik as alternative |
| MicroK8s | `microk8s enable metallb` | Built-in support |
| Docker Desktop | No action needed | Automatically binds to localhost |

After choosing the appropriate solution for your environment, Ingress-Nginx Controller should be able to obtain an external IP address.

---

# Solving Ingress Not Assigning ADDRESS Problem

When your Ingress resource doesn't show an ADDRESS, it's usually because the Ingress Controller isn't properly installed or configured. Here are detailed troubleshooting and solutions:

## 1. Confirm Ingress Controller Installation

First check if your cluster has Ingress Controller installed:

```bash
kubectl get pods -n ingress-nginx  # If using Nginx Ingress Controller
# or
kubectl get pods -A | grep ingress
```

If not installed, you need to install Ingress Controller first.

## 2. Install Ingress Controller Based on Your Environment

### For Minikube Users

```bash
minikube addons enable ingress
```

Wait a few minutes then verify:
```bash
kubectl get pods -n ingress-nginx
```

### For Docker Desktop (Mac/Windows)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

### For Kind or Other Local Clusters

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

## 3. Wait for Ingress Controller to be Ready

After installation, wait a few minutes for Ingress Controller to fully start:

```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

## 4. Check Ingress Controller Service

View if Ingress Controller's Service has been assigned external IP:

```bash
kubectl get svc -n ingress-nginx
```

## 5. Special Environment Handling

### Minikube Special Handling

Minikube needs to run additional command to get access address:

```bash
minikube tunnel
```

Then in another terminal check Ingress:
```bash
kubectl get ingress
```

### Docker Desktop Special Handling

Docker Desktop's Ingress usually binds to `localhost`, you can directly add to `/etc/hosts`:
```
127.0.0.1 nginx.local
```

## 6. Verify Ingress Configuration

Check your Ingress resource details:
```bash
kubectl describe ingress nginx-ingress
```

View the events section for any error messages.

## 7. Common Issues Resolution

1. **Ingress Class not specified**:
   In newer Kubernetes versions, you may need to specify Ingress Class:
   ```yaml
   metadata:
     annotations:
       kubernetes.io/ingress.class: "nginx"
   ```

2. **Firewall issues**:
   Ensure your firewall allows Ingress Controller ports (usually 80 and 443).

3. **Insufficient resources**:
   Check if Ingress Controller Pod can't start due to resource limits:
   ```bash
   kubectl describe pods -n ingress-nginx
   ```

## 8. Complete Example

A complete Ingress example (including Ingress Class annotation):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host: nginx.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
```

## Summary

1. Confirm Ingress Controller is installed and running
2. Choose correct installation method for your environment
3. Wait for Controller to be fully ready
4. Check Ingress resource details for more information
5. Add Ingress Class annotation when necessary

Following these steps, your Ingress should be able to correctly obtain ADDRESS.