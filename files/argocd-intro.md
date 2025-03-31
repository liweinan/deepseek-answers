# Introduction to Argo CD

**Argo CD** is a **declarative, GitOps-based continuous delivery (CD) tool** for Kubernetes. It automates application deployments by syncing the live cluster state with the desired state defined in a Git repository.

Developed as part of the **Argo Project** (under the CNCF), Argo CD is widely used for **GitOps workflows**, ensuring that Kubernetes deployments are **auditable, reproducible, and secure**.

---

## **🔹 Key Features of Argo CD**
### **1. GitOps-Driven Deployments**
- **Source of Truth:** Uses Git repositories (e.g., GitHub, GitLab) to store Kubernetes manifests (YAML/Helm/Kustomize).
- **Automated Sync:** Continuously monitors Git and ensures the cluster matches the desired state.

### **2. Declarative Configuration**
- Defines applications using **Kubernetes Custom Resources (CRDs)**.
- Supports **Helm, Kustomize, Jsonnet, and plain YAML**.

### **3. Automated Synchronization & Self-Healing**
- Detects **drift** (differences between Git and cluster state) and auto-corrects it (if configured).
- Can be set to **manual approval** for production environments.

### **4. Multi-Cluster & Multi-Tenancy Support**
- Manages deployments across **multiple Kubernetes clusters**.
- Supports **RBAC (Role-Based Access Control)** for team permissions.

### **5. Web UI & CLI for Visibility**
- **Dashboard** for visualizing app status, sync state, and health.
- **`argocd` CLI** for managing deployments programmatically.

### **6. Integration with CI/CD Tools**
- Works with **Jenkins, GitHub Actions, Tekton, and other CI tools**.
- Can trigger deployments after CI pipelines complete.

---

## **🔹 How Argo CD Works**
1. **Define Application Manifests** (in Git):
    - Store Kubernetes YAML, Helm charts, or Kustomize files in a Git repo.
2. **Register App in Argo CD**:
    - Point Argo CD to the Git repo and target cluster.
3. **Sync & Deploy**:
    - Argo CD pulls the latest manifests and applies them to the cluster.
4. **Monitor & Self-Heal**:
    - If the cluster drifts from Git, Argo CD corrects it (if auto-sync is enabled).

---

## **🔹 Argo CD vs. Traditional CD Tools**
| **Feature**          | **Argo CD (GitOps)** | **Traditional CD (Jenkins, Spinnaker)** |  
|----------------------|----------------------|----------------------------------------|  
| **Source of Truth**  | Git Repository       | CI Pipeline Config                     |  
| **Deployment Model** | Pull-based (Git → Cluster) | Push-based (CI → Cluster) |  
| **Drift Detection**  | ✅ Automatic         | ❌ Manual Checks Needed                |  
| **Auditability**     | ✅ Full Git History  | ❌ Relies on CI Logs                   |  
| **Security**         | ✅ RBAC + Git Sign-off | ❌ Depends on CI Permissions          |  

---

## **🔹 Example: Deploying an App with Argo CD**
### **1. Install Argo CD**
```sh
kubectl create namespace argocd  
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml  
```  

### **2. Access the Argo CD UI**
```sh
kubectl port-forward svc/argocd-server -n argocd 8080:443  
```  
Visit → `http://localhost:8080` (Default login: `admin`, password retrieved via `kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d`).

### **3. Register an Application**
```sh
argocd app create myapp \  
  --repo https://github.com/your-repo/manifests.git \  
  --path ./k8s \  
  --dest-server https://kubernetes.default.svc \  
  --dest-namespace default  
```  

### **4. Sync & Deploy**
```sh
argocd app sync myapp  
```  

---

## **🔹 Use Cases for Argo CD**
✅ **GitOps for Kubernetes** – Enforces Git as the single source of truth.  
✅ **Multi-Cluster Management** – Deploys apps across dev/stage/prod clusters.  
✅ **CI/CD Integration** – Works with Jenkins, GitHub Actions, etc.  
✅ **Security & Compliance** – All changes are Git-audited.

---

## **🔹 Conclusion**
Argo CD is a **powerful GitOps tool** that brings **declarative, Git-driven automation** to Kubernetes deployments. It is ideal for teams adopting **DevOps best practices**, requiring **auditability, security, and scalability** in their CD workflows.

Would you like a deeper dive into **Argo CD vs. Flux CD** or **advanced Argo CD configurations**? 🚀

---

# **Argo CD Example: Deploying a Sample Application**

Here’s a **step-by-step guide** to deploying a simple NGINX web server using **Argo CD** in a Kubernetes cluster. This example covers:
- Setting up Argo CD
- Defining a Kubernetes Deployment in Git
- Syncing the app using Argo CD

---

## **🔹 Prerequisites**
- A running **Kubernetes cluster** (Minikube, Kind, or cloud-based like EKS/GKE)
- **`kubectl`** configured to access the cluster
- **Git** (for storing manifests)

---

## **🔹 Step 1: Install Argo CD**
Deploy Argo CD in your Kubernetes cluster:
```sh
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```
Wait for all pods to be ready:
```sh
kubectl get pods -n argocd --watch
```

---

## **🔹 Step 2: Access the Argo CD UI**
Expose the Argo CD server (default uses port `8080`):
```sh
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
Open **http://localhost:8080** in your browser.

### **Login Credentials**
Get the default admin password:
```sh
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```
(Username: `admin`)

---

## **🔹 Step 3: Prepare Git Repository**
Create a Git repo (e.g., GitHub) with the following structure:
```
my-argo-app/
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
```

### **Example: `deployment.yaml`**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```

### **Example: `service.yaml`**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

Push these files to your Git repo.

---

## **🔹 Step 4: Register the App in Argo CD**
### **Using the UI**
1. Click **"New App"**.
2. Fill in:
    - **Application Name**: `nginx-app`
    - **Project**: `default`
    - **Repository URL**: `https://github.com/your-username/my-argo-app.git`
    - **Path**: `k8s` (folder containing YAMLs)
    - **Cluster**: `https://kubernetes.default.svc` (in-cluster)
    - **Namespace**: `default`

### **Using CLI**
```sh
argocd app create nginx-app \
  --repo https://github.com/your-username/my-argo-app.git \
  --path k8s \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default
```

---

## **🔹 Step 5: Sync the Application**
### **Manual Sync (UI)**
1. Go to the **"Applications"** tab.
2. Click **"Sync"** on your `nginx-app`.
3. Confirm synchronization.

### **Manual Sync (CLI)**
```sh
argocd app sync nginx-app
```

### **Auto-Sync (Optional)**
Enable automatic synchronization (self-healing):
```sh
argocd app set nginx-app --sync-policy automated
```

---

## **🔹 Step 6: Verify Deployment**
Check the app status:
```sh
argocd app get nginx-app
```
Expected output:
```
Name:               nginx-app
Project:            default
Server:             https://kubernetes.default.svc
Namespace:          default
URL:                https://localhost:8080/applications/nginx-app
Repo:               https://github.com/your-username/my-argo-app.git
Target:             
Path:               k8s
SyncWindow:         Sync Allowed
Sync Policy:        <none>
Sync Status:        Synced to  (53e28f6)
Health Status:      Healthy
```

### **Access the NGINX Service**
Get the external IP (if using `LoadBalancer`):
```sh
kubectl get svc nginx-service
```
Open `http://<EXTERNAL-IP>` in a browser to see NGINX.

---

## **🔹 Step 7: Make a Git Change (Example of GitOps)**
1. Update `k8s/deployment.yaml` (e.g., change `replicas: 3`).
2. Commit and push to Git.
3. Argo CD **detects the drift** and syncs automatically (if auto-sync is enabled).

---

## **🔹 Key Takeaways**
✅ **Git as Source of Truth** – All changes are Git-driven.  
✅ **Declarative Sync** – Argo CD ensures the cluster matches Git.  
✅ **Self-Healing** – Auto-corrects manual cluster changes (if enabled).  
✅ **Auditability** – Every change is tracked in Git history.

---

## **🔹 Next Steps**
- **Try Helm/Kustomize** – Deploy apps using Helm charts.
- **Set Up Notifications** – Slack/email alerts for sync failures.
- **Multi-Cluster Deployments** – Sync apps across multiple clusters.

Would you like a **Flux CD vs. Argo CD** comparison next? 🚀