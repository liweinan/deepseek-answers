# **Kubernetes Service** Sample

Below is a YAML sample description file for a **Kubernetes Service**, demonstrating how to define a basic `ClusterIP` type Service to expose a set of Pods (matched through label selectors):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service       # Service name
  namespace: default     # Optional, defaults to default
  labels:
    app: my-app          # Custom labels (optional)
spec:
  type: ClusterIP        # Service type (ClusterIP/NodePort/LoadBalancer)
  selector:              # Select Pods to proxy (matched through labels)
    app: my-app          # Must match Pod labels
    tier: frontend       # Optional, more granular label selection
  ports:
    - name: http         # Port name (optional)
      protocol: TCP      # Protocol (TCP/UDP/SCTP)
      port: 80           # Service exposed port
      targetPort: 8080   # Pod port (container port)
    - name: https        # Multiple ports can be defined
      protocol: TCP
      port: 443
      targetPort: 8443
```

---

### **Key Field Descriptions**
1. **`type`**:
    - `ClusterIP` (default): Internal cluster access.
    - `NodePort`: Exposed through node IP + static port.
    - `LoadBalancer`: Load balancer provided by cloud provider.

2. **`selector`**:
    - Must match the target Pod's `labels`, Service will proxy traffic to these Pods.

3. **`ports`**:
    - `port`: Service's virtual port.
    - `targetPort`: Pod container's actual port (must be consistent with Pod definition).

---

### **Other Common Service Type Examples**
#### **1. NodePort Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080  # Manually specify node port (optional, default range 30000-32767)
```

#### **2. LoadBalancer Service (Cloud Provider Applicable)**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-lb-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
  externalTrafficPolicy: Local  # Optional, preserve client source IP
```

---

### **Verify Service**
```bash
kubectl apply -f service.yaml    # Deploy Service
kubectl get svc                 # View Service status
kubectl describe svc my-service # Check detailed information
```

This example covers the most common Service configuration scenarios. You can adjust fields (such as ports, label selectors) according to actual requirements.

---

In Kubernetes, the main role of **Service** is to provide a stable access entry point for a set of Pods, and it is divided into three core types based on different usage scenarios: **ClusterIP**, **NodePort**, and **LoadBalancer**. Their core differences lie in **access scope** and **applicable scenarios**. Here is a detailed comparison:

---

### **1. ClusterIP (Default Type)**
#### **Characteristics**
- **Access Scope**: Only accessible within the cluster (such as communication between Pods).
- **IP Assignment**: Automatically assigns an internal cluster virtual IP (VIP), cannot be directly accessed from outside the cluster.
- **Typical Use Cases**: Internal microservice communication, database access, etc.

#### **Example YAML**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-clusterip-service
spec:
  type: ClusterIP  # Can be omitted, default type
  selector:
    app: my-app
  ports:
    - port: 80      # Service port
      targetPort: 8080  # Pod port
```

#### **Applicable Scenarios**
- Frontend Pods need to access backend Pods (such as frontend calling backend API).
- Internal cluster service discovery (through DNS name `my-service.namespace.svc.cluster.local`).

---

### **2. NodePort**
#### **Characteristics**
- **Access Scope**: Access from outside the cluster through any node's IP + static port (NodePort).
- **Port Range**: Default `30000-32767` (can be manually specified).
- **Underlying Implementation**: Based on ClusterIP, additionally opens a port on each node.

#### **Example YAML**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
    - port: 80          # Service port (cluster internal access)
      targetPort: 8080  # Pod port
      nodePort: 31000   # Manually specify node port (optional)
```

#### **Access Method**
- External access through `http://<any-node-IP>:31000`.
- Cluster internal access still available through ClusterIP (`http://<cluster-ip>:80`).

#### **Applicable Scenarios**
- Development and testing environments for temporary service exposure.
- Local clusters that don't support LoadBalancer (such as Minikube, bare metal clusters).

---

### **3. LoadBalancer**
#### **Characteristics**
- **Access Scope**: Access from outside through load balancer provided by cloud provider (such as AWS ALB, GCP LB).
- **Dependency Requirements**: Requires cluster to run on platform that supports cloud load balancing (such as AWS, Azure, GCP).
- **Underlying Implementation**: Based on NodePort, automatically creates external load balancer.

#### **Example YAML**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-lb-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 80          # Load balancer listening port
      targetPort: 8080  # Pod port
```

#### **Access Method**
- External access through load balancer's IP/DNS (such as `http://<LB-IP>:80`).
- Cluster internal access still available through ClusterIP or NodePort.

#### **Applicable Scenarios**
- Production environment service exposure (high availability, automatic traffic distribution).
- Cloud-native applications (such as web services on public cloud).

---

### **Core Differences Comparison**
| Feature                | ClusterIP              | NodePort                     | LoadBalancer               |
|---------------------|------------------------|------------------------------|----------------------------|
| **Access Scope**         | Cluster internal only             | Node IP + static port (external accessible) | Through cloud load balancer (external accessible) |
| **IP/Port**         | Cluster internal virtual IP         | Node IP + 30000-32767 port      | Cloud provider assigned LB IP           |
| **Applicable Environment**        | All clusters               | All clusters (including local development)       | Public cloud/private cloud supporting LB        |
| **Typical Use Cases**        | Internal service communication           | Development testing, temporary service exposure         | Production environment external services            |
| **Performance Overhead**        | No additional overhead             | Node port forwarding                  | Cloud LB + node port forwarding          |

---

### **How to Choose?**
1. **Cluster internal access only** → **ClusterIP** (such as database services).
2. **Temporary external access (testing/local cluster)** → **NodePort**.
3. **Production environment external access (cloud platform)** → **LoadBalancer**.
4. **More advanced requirements (such as HTTPS, routing rules)** → Combine with **Ingress** usage.

---

### **Supplement: Role of Ingress**
- The above three Services mainly solve **L4 (TCP/UDP) traffic exposure**, while **Ingress** is used to manage **L7 (HTTP/HTTPS) routing rules** (such as domain names, path routing).
- Usually used in conjunction with `LoadBalancer` or `NodePort` type Services.

---