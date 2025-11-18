# **Hypershift Introduction**

**Hypershift** is an open-source **hosted OpenShift architecture** from Red Hat that allows users to run **lightweight OpenShift control planes** on **external infrastructure (such as AWS, Azure, GCP, or bare metal servers)**, while **worker nodes** are managed by the users themselves.  
It is essentially an OpenShift deployment model with **"separation of control plane and data plane"**, suitable for large-scale, multi-tenant OpenShift cluster management scenarios.

---

## **1. Hypershift Core Concepts**
### **(1) Control Plane and Data Plane Separation**
| Component          | Traditional OpenShift Cluster | Hypershift Cluster |
|--------------|--------------------|----------------|
| **Control Plane**  | Runs inside the cluster (3 Master nodes) | **Runs externally (hosted)**, managed by Red Hat or cloud provider |
| **Data Plane**  | Worker nodes managed by the cluster | **Worker nodes managed by users** (can be cloud VMs, bare metal, or edge nodes) |

### **(2) Hosted Control Plane**
- Hypershift's **control plane (API Server, Controller Manager, Scheduler, etc.)** runs in a **lightweight Kubernetes cluster** (called **"Management Cluster"**), rather than inside the cluster like traditional OpenShift.
- Users only need to manage **Worker Nodes**, the control plane is automatically managed by Hypershift, similar to the hosted models of **EKS (AWS), AKS (Azure), GKE (Google Cloud)**.

### **(3) Multi-tenancy Support**
- Since the control plane is lightweight, **multiple OpenShift clusters** can be hosted on a single **Management Cluster**, with each cluster running independently, suitable for **SaaS service providers, enterprise multi-team shared clusters** and similar scenarios.

---

## **2. Hypershift Architecture**
### **(1) Management Cluster**
- Runs the Hypershift Operator, responsible for managing control planes of all hosted OpenShift clusters.
- Can be any Kubernetes cluster (such as OpenShift, EKS, AKS, etc.).

### **(2) Hosted Cluster**
- OpenShift clusters created by users, **control plane runs on Management Cluster**, **Worker Nodes run on user-specified infrastructure** (such as AWS EC2, Azure VM, bare metal, etc.).
- Each Hosted Cluster has its own **etcd, API Server, Controller Manager**, but they are lightweight and don't consume Worker resources.

### **(3) Node Pool**
- Users can define **Node Pool**, specifying Worker Node specifications (such as AWS instance types, storage size, etc.).
- Hypershift automatically manages the lifecycle of these nodes (creation, scaling, deletion).

---

## **3. Hypershift Advantages**
### **(1) Cost Reduction**
- **Control plane doesn't consume Worker resources**, saving compute costs (traditional OpenShift requires 3 Master nodes).
- Suitable for **large-scale deployments**, multiple OpenShift clusters share the same Management Cluster.

### **(2) Simplified Operations**
- **Control plane is automatically managed by Hypershift**, users only need to focus on Worker Nodes.
- Operations like upgrades, backups, and recovery are handled by Hypershift, reducing operational burden.

### **(3) Multi-cluster Management**
- Can run **hundreds of OpenShift clusters on a single Management Cluster**, suitable for **SaaS providers, enterprise multi-team shared clusters** and similar scenarios.

### **(4) Cross-cloud and Hybrid Cloud Support**
- Worker Nodes can run in different environments like **AWS, Azure, GCP, VMware, bare metal, edge nodes**, achieving true **hybrid cloud deployment**.

---

## **4. Hypershift Use Cases**
### **(1) SaaS Service Providers**
- Provide **multi-tenant OpenShift services**, where each customer has their own independent OpenShift cluster, but the control plane is uniformly managed by the SaaS provider.

### **(2) Enterprise Multi-team Shared Clusters**
- Different teams can have their own OpenShift clusters, but **control planes are uniformly managed by the IT department**, avoiding resource waste.

### **(3) Edge Computing**
- Control plane runs in the cloud, Worker Nodes run on edge devices (such as factories, retail stores, vehicle-mounted devices, etc.).

### **(4) Quick Creation of Temporary Clusters**
- Used for CI/CD testing, development environments, can be deleted after use, reducing costs.

---

## **5. Hypershift vs. Traditional OpenShift**
| Feature                | Traditional OpenShift          | Hypershift               |
|---------------------|------------------------|--------------------------|
| **Control Plane Location**     | Runs inside cluster (3 Masters) | Runs externally (hosted)      |
| **Worker Management**      | Managed by cluster              | Managed by users (AWS/Azure/bare metal, etc.) |
| **Resource Usage**         | Requires 3+ Master nodes     | Lightweight control plane, resource-saving   |
| **Multi-cluster Support**       | Each cluster independent            | Single Management Cluster hosts multiple clusters |
| **Use Cases**         | Single cluster deployment              | Multi-tenant, SaaS, edge computing    |

---

## **6. How to Deploy Hypershift?**
Hypershift can be deployed through **OpenShift HyperShift Operator**, supporting:
- **AWS, Azure, GCP, VMware, bare metal** and other infrastructures.
- Cluster management through CLI (`hypershift`) or GitOps (such as ArgoCD).

**Example (AWS environment):**
```bash
hypershift create cluster aws \
  --name my-cluster \
  --region us-east-1 \
  --node-pool-replicas 3 \
  --instance-type m5.large
```

---

## **7. Summary**
- **Hypershift is a hosted OpenShift architecture** with separated control plane and data plane, suitable for **multi-tenant, hybrid cloud, edge computing** scenarios.
- **Advantages**: Cost reduction, simplified operations, support for large-scale multi-cluster management.
- **Target Users**: SaaS providers, enterprise IT departments, users needing flexible OpenShift deployment.

🚀 **Example Use Cases**:
- Cloud providers offering OpenShift hosting services (similar to ROSA, ARO).
- Enterprises providing independent OpenShift clusters for different departments while uniformly managing control planes.
- Edge computing scenarios where control plane is in the cloud and Workers are on edge devices.