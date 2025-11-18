# Kubernetes and OpenShift Interview Exam

## Basic Knowledge Section (30 points)

### Multiple Choice Questions (2 points each, 10 points total)

1. The smallest scheduling unit in Kubernetes is:
    - A) Pod
    - B) Container
    - C) Node
    - D) Deployment

2. OpenShift is built based on which Kubernetes distribution?
    - A) Rancher
    - B) Red Hat OpenShift Kubernetes Engine
    - C) Vanilla Kubernetes
    - D) EKS

3. In Kubernetes, the resource object used to store sensitive information is:
    - A) ConfigMap
    - B) Secret
    - C) Volume
    - D) PersistentVolume

4. What authentication method does OpenShift Web Console use by default?
    - A) Basic Auth
    - B) OAuth
    - C) LDAP
    - D) Kerberos

5. Which of the following is NOT a core component of Kubernetes?
    - A) kubelet
    - B) etcd
    - C) kube-proxy
    - D) Docker

### Fill-in-the-blank Questions (2 points each, 10 points total)

1. The REST path prefix for Kubernetes API is `/________`.

2. The component used to build container images in OpenShift is ________.

3. The resource type used to define Pod deployment and updates in Kubernetes is ________.

4. The object used to manage project quotas in OpenShift is ________.

5. The resource type used to expose external services to the cluster internally in Kubernetes is ________.

### Short Answer Questions (5 points each, 10 points total)

1. Briefly explain the main differences between Kubernetes and OpenShift.

2. Explain the relationship between Deployment, ReplicaSet, and Pod in Kubernetes.

## Intermediate Knowledge Section (40 points)

### Scenario Analysis Questions (10 points each, 20 points total)

1. You are managing an OpenShift cluster and suddenly find that Pods in a project cannot be created, with an error message "Failed to allocate resources". Please describe your troubleshooting steps and possible solutions.

2. Describe the steps to implement blue-green deployment in Kubernetes and explain how OpenShift simplifies this process.

### Command Operation Questions (10 points each, 20 points total)

1. Write a set of kubectl/oc commands to complete the following tasks:
    - Create a namespace/project named "test"
    - Deploy an nginx container in that namespace using Deployment resource
    - Expose the Deployment as a Service with NodePort type
    - Check Pod status and logs

2. You need to set up a build configuration in OpenShift to build a Node.js application from a GitHub repository and deploy it to the cluster. Please write the complete oc command flow.

## Advanced Knowledge Section (30 points)

### Architecture Design Question (15 points)

Design a highly available production-grade OpenShift cluster architecture, requiring:
- Include at least 3 master nodes and 5 worker nodes
- Consider etcd cluster deployment
- Include logging and monitoring solutions
- Consider network and storage high availability

### Troubleshooting Question (15 points)

In a production Kubernetes cluster, users report their applications are intermittently unavailable. You find:
- Pod status shows Running
- Service and Endpoints configuration is correct
- Network policies allow necessary traffic
- Node resource usage is normal

Please describe your systematic troubleshooting approach and possible root causes.

## Reference Answers

### Basic Knowledge Section

**Multiple Choice**:
1. A 2. B 3. B 4. B 5. D

**Fill-in-the-blank**:
1. /api
2. BuildConfig / Source-to-Image (S2I)
3. Deployment
4. ResourceQuota
5. Service (or Ingress)

**Short Answer**:
1. Kubernetes is an open-source container orchestration platform, OpenShift is an enterprise-grade distribution based on Kubernetes, providing additional features such as: built-in image registry, build tools, Web console, enhanced security features (like SCC), multi-tenant support, developer tool integration, etc.

2. Deployment manages ReplicaSet, ReplicaSet ensures a specified number of Pod replicas are running. Deployment provides declarative updates, rollback functions, ReplicaSet is responsible for Pod scaling, Pod is the unit that actually runs containers.

### Intermediate Knowledge Section

**Scenario Analysis Questions**:
1. Troubleshooting steps:
    - Check project quota: `oc describe quota -n <project>`
    - Check resource requests/limits: `oc describe pod <podname>`
    - Check node resources: `oc adm top nodes`
    - Check resource usage: `oc adm top pods -n <project>`
      Solutions may include: adjust quota, optimize resource requests, clean up unused resources, add more nodes, etc.

2. Blue-green deployment steps:
    - Deploy new version application (green) in parallel with old version (blue)
    - Use same labels but different version labels to distinguish
    - Switch traffic through Service
      OpenShift simplified approach:
    - Use Route and weight allocation
    - Utilize DeploymentConfig rolling strategy
    - Use OpenShift Pipelines automation process

**Command Operation Questions**:
1. ```bash
   kubectl create ns test
   kubectl create deployment nginx --image=nginx -n test
   kubectl expose deployment nginx --port=80 --type=NodePort -n test
   kubectl get pods -n test
   kubectl logs <pod-name> -n test
   ```

2. ```bash
   oc new-project nodejs-app
   oc new-app nodejs~https://github.com/your/nodejs-repo.git
   # Or more detailed build configuration
   oc new-build nodejs~https://github.com/your/nodejs-repo.git --name=nodejs-app
   oc new-app --image-stream=nodejs-app:latest
   oc expose svc/nodejs-app
   ```

### Advanced Knowledge Section

**Architecture Design Question**:
Key points:
- 3 master nodes form highly available control plane, use load balancer
- etcd cluster deployed independently or co-located with master nodes, odd number of nodes, across failure domains
- 5 worker nodes deployed across availability zones
- Logging solution: EFK or Loki stack
- Monitoring solution: Prometheus + Grafana or OpenShift monitoring stack
- Network: multiple network interfaces, SDN plugin (like OVN-Kubernetes)
- Storage: persistent volumes use storage backend supporting ReadWriteMany (like Ceph)

**Troubleshooting Question**:
Troubleshooting approach:
1. Check kube-proxy and CNI plugin status
2. Check if network policies conflict
3. Check if DNS resolution is normal
4. Check application health check configuration
5. Check node kernel logs for packet loss or connection issues
6. Use network diagnostic tools (like ping, curl, tcpdump)

Possible causes:
- kube-proxy rules not properly synchronized
- CNI network plugin issues
- Application health checks too sensitive
- Inter-node network issues
- DNS resolution intermittent failures
- Concurrent connection limit reached

---

In Kubernetes (k8s), **Pod generation involves multiple components working together**, but is mainly handled by the following two core components:

---

### **1. Control Plane**
#### **(1) kube-scheduler (Scheduler)**
- **Responsibilities**:
    - Monitor unscheduled Pods (`Pod.spec.nodeName` is empty).
    - Select the optimal Node to run Pod based on resource requirements, affinity rules, etc.
    - Write scheduling decisions to API Server (update `Pod.spec.nodeName`).
- **Key Points**:
    - **Does not directly create Pod**, only decides which Node Pod should run on.

#### **(2) kube-controller-manager (Controller Manager)**
- Including **Deployment Controller** / **ReplicaSet Controller** / **StatefulSet Controller**, etc.:
    - Monitor resource changes (like Deployment, ReplicaSet) in API Server.
    - Ensure the actual number of running Pods matches the declared replica count.
    - **Generate Pod templates** (PodSpec) and create Pod objects through API Server.
- **Key Points**:
    - **Responsible for generating Pod metadata** (like name, labels, resource requests, etc.), but Pod has not yet been scheduled or run.

---

### **2. Worker Node**
#### **(3) kubelet (Node Agent)**
- **Responsibilities**:
    - Monitor Pods assigned to this node in API Server.
    - Call container runtime (like containerd, CRI-O) to **actually create containers**.
    - Manage Pod lifecycle (start, stop, restart).
- **Key Points**:
    - **The process that actually generates Pods on the node**, transforms Pod from declarative state to actually running containers.

---

### **Complete Process Example (Using Deployment)**
1. **User Submits Deployment**:
   ```bash
   kubectl create deployment nginx --image=nginx
   ```
2. **Deployment Controller Generates ReplicaSet**:
    - Create ReplicaSet object based on Deployment template.
3. **ReplicaSet Controller Generates Pod Object**:
    - Create Pod through API Server (at this time `Pod.spec.nodeName` is empty).
4. **kube-scheduler Assigns Node**:
    - Select appropriate Node and update `Pod.spec.nodeName`.
5. **Target Node's kubelet Creates Container**:
    - Call container runtime to start containers in Pod.

---

### **Key Summary**
| Component                | Responsibility                               | Directly Generate Pod? |
|---------------------|-----------------------------------|------------------|
| **Deployment/ReplicaSet Controller** | Generate Pod metadata (through API Server) | ❌ (Only generates declaration)   |
| **kube-scheduler**  | Decide which Node Pod runs on           | ❌                |
| **kubelet**         | Actually create containers on node               | ✅                |

**Short Answer**:
- **Pod declarations are generated by controllers (like Deployment Controller)**, but **actual creation is executed by kubelet**.
- The entire process is coordinated through API Server's monitoring mechanism.