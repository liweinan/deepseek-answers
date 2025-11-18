# Complete Step-by-Step Tutorial for Deploying Jenkins in Kubernetes Cluster

Below is a **complete step-by-step tutorial** for deploying Jenkins in a Kubernetes cluster, covering persistent storage, Service exposure, Ingress configuration, and initial password retrieval:

---

### **Prerequisites**
1. Kubernetes cluster installed (such as Minikube, k3s, EKS, etc.).
2. `kubectl` installed and configured with cluster access permissions.
3. Optional: Helm installed (for simplified deployment).

---

## **Method 1: Direct Deployment Using kubectl (Recommended for Beginners)**

### **Step 1: Create Namespace**
```bash
kubectl create namespace jenkins
```

### **Step 2: Create Persistent Storage (PVC)**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jenkins-pvc
  namespace: jenkins
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF
```
> 📌 If using cloud services (like AWS EBS, Azure Disk), StorageClass may be automatically configured; local clusters need to deploy PV provisioner (like NFS) in advance.

---

### **Step 3: Deploy Jenkins Deployment**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts-jdk17
        ports:
        - containerPort: 8080
        - containerPort: 50000
        volumeMounts:
        - name: jenkins-storage
          mountPath: /var/jenkins_home
      volumes:
      - name: jenkins-storage
        persistentVolumeClaim:
          claimName: jenkins-pvc
      securityContext:
        runAsUser: 1000
        fsGroup: 1000
EOF
```
> 🔍 Notes:
> - Uses official LTS image (`jenkins/jenkins:lts-jdk17`).
> - Mounts PVC to `/var/jenkins_home` to ensure data persistence.
> - `securityContext` avoids permission issues.

---

### **Step 4: Expose Jenkins Service**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: jenkins
  namespace: jenkins
spec:
  type: NodePort
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30080
  - port: 50000
    targetPort: 50000
  selector:
    app: jenkins
EOF
```
> 🌐 Access methods:
> - **NodePort**: Access via `http://<node-ip>:30080`.
> - For domain access, continue to Step 5 (Ingress).

---

### **Step 5 (Optional): Configure Ingress**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jenkins-ingress
  namespace: jenkins
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: jenkins.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: jenkins
            port:
              number: 8080
EOF
```
> 📌 Prerequisites:
> - Ingress Controller installed (like Nginx Ingress).
> - Domain `jenkins.example.com` resolved to cluster Ingress IP.

---

### **Step 6: Get Initial Admin Password**
1. View Jenkins Pod name:
   ```bash
   kubectl get pods -n jenkins
   ```
2. Extract password from Pod logs:
   ```bash
   kubectl logs <jenkins-pod-name> -n jenkins | grep "InitialAdminPassword"
   ```
   > Or directly enter container to get:
   ```bash
   kubectl exec -it <jenkins-pod-name> -n jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword
   ```

---

## **Method 2: Quick Deployment Using Helm (Suitable for Production)**
### **Step 1: Add Jenkins Helm Repository**
```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update
```

### **Step 2: Custom Configuration**
Create `values.yaml`:
```yaml
controller:
  image: "jenkins/jenkins"
  tag: "lts-jdk17"
  adminUser: "admin"
  adminPassword: "your-strong-password"  # Recommend changing to complex password
  serviceType: NodePort
  servicePort: 8080
  serviceNodePort: 30080
  installPlugins:
    - kubernetes
    - workflow-aggregator
  persistence:
    enabled: true
    size: 10Gi
```

### **Step 3: Install Jenkins**
```bash
helm install jenkins jenkins/jenkins -n jenkins -f values.yaml
```

---

## **Verify Deployment**
1. Check Pod status:
   ```bash
   kubectl get pods -n jenkins -w
   ```
2. Access Jenkins:
   - NodePort: `http://<node-ip>:30080`
   - Ingress: `http://jenkins.example.com`

---

## **Common Issues Resolution**
1. **PVC not bound**:
   - Check if StorageClass is available: `kubectl get storageclass`.
   - Local clusters can switch to `hostPath` (for testing only):
     ```yaml
     volumes:
     - name: jenkins-storage
       hostPath:
         path: /data/jenkins
         type: DirectoryOrCreate
     ```

2. **Plugin installation failed**:
   - Change to domestic mirror source in Jenkins interface:
     - Go to **Manage Jenkins → Plugin Manager → Advanced**.
     - Change `Update Site` to `https://mirrors.tuna.tsinghua.edu.cn/jenkins/updates/update-center.json`.

---

## **Summary**
- **kubectl direct deployment**: Suitable for learning or quick verification.
- **Helm deployment**: Suitable for production, supports flexible configuration.
- **Key configurations**: Persistent storage, Service exposure, security context.

Following this tutorial, you'll get a complete and usable Jenkins service, and can dynamically manage build agents through Kubernetes (requires installing `kubernetes` plugin).