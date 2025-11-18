# StatefulSet Introduction

**StatefulSet** is a workload API object in Kubernetes used for managing stateful applications. Unlike **Deployment** and **ReplicaSet**, which are mainly used for managing stateless applications, StatefulSet is specifically designed for applications that require persistent storage, stable network identifiers, and ordered deployment/scaling/deletion.

---

## **Core Features of StatefulSet**

1. **Stable Network Identity**:
    - Each Pod has a unique and stable network identifier (such as `pod-name-0`, `pod-name-1`), and even if the Pod is rescheduled, its name and network identifier will not change.
    - For example, a StatefulSet named `web` will create Pods named sequentially as `web-0`, `web-1`, `web-2`.

2. **Stable Storage**:
    - Each Pod can bind to one or more persistent storage volumes (Persistent Volume, PV), and even if the Pod is deleted or rescheduled, the storage volume will be retained and rebound to the new Pod.
    - The lifecycle of the storage volume is decoupled from the Pod, ensuring data persistence.

3. **Ordered Deployment and Scaling**:
    - Pods in a StatefulSet are created in order (from 0 to N-1), and the next Pod will only be created after the previous Pod is in a running state.
    - When scaling down, Pods are deleted in reverse order (from N-1 to 0).

4. **Ordered Rolling Updates**:
    - When updating a StatefulSet, Pods are updated in order (from N-1 to 0) to ensure application stability.

5. **Uniqueness**:
    - Each Pod in a StatefulSet is unique and cannot be randomly replaced or recreated.

---

## **Typical Use Cases for StatefulSet**

1. **Database Clusters**:
    - Databases such as MySQL, PostgreSQL, MongoDB that require persistent storage and stable network identifiers.
    - Each Pod corresponds to a database instance, and storage volumes are used to save data.

2. **Distributed Systems**:
    - Distributed systems such as ZooKeeper, Etcd, Kafka that require clear member identity and stable network identifiers.

3. **Stateful Applications**:
    - Any application that requires persistent storage or depends on specific network identifiers.

---

## **How StatefulSet Works**

1. **Pod Naming Rules**:
    - Pods created by StatefulSet follow the format `<statefulset-name>-<ordinal-index>`, such as `web-0`, `web-1`.

2. **Persistent Storage**:
    - Dynamically creates persistent storage volumes (Persistent Volume Claim, PVC) for each Pod through `volumeClaimTemplates`.
    - Example:
      ```yaml
      volumeClaimTemplates:
      - metadata:
          name: data
        spec:
          accessModes: [ "ReadWriteOnce" ]
          resources:
            requests:
              storage: 10Gi
      ```

3. **Service Discovery**:
    - Provides unique DNS records for each Pod through Headless Service (headless service).
    - For example, a StatefulSet named `web` and a Headless Service named `web` will generate the following DNS records:
        - `web-0.web.default.svc.cluster.local`
        - `web-1.web.default.svc.cluster.local`

4. **Ordered Operations**:
    - When deploying, scaling, scaling down, and updating, StatefulSet strictly performs operations in order.

---

## **Example of StatefulSet**

The following is a simple StatefulSet example for deploying a MySQL cluster with 3 replicas:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: "mysql"
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:5.7
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

---

## **Differences Between StatefulSet and Deployment**

| Feature                | StatefulSet                     | Deployment                     |
|------------------------|---------------------------------|--------------------------------|
| **Network Identity**    | Stable and unique               | Randomly generated             |
| **Storage**            | Each Pod has independent persistent storage | Usually no persistent storage |
| **Pod Naming**         | Ordered and stable (e.g., `web-0`, `web-1`) | Random naming                 |
| **Deployment Order**   | Ordered (from 0 to N-1)         | Parallel                       |
| **Use Cases**          | Stateful applications (e.g., databases, distributed systems) | Stateless applications (e.g., web services) |

---

## **Summary**

- StatefulSet is a core tool in Kubernetes for managing stateful applications, suitable for scenarios that require stable network identifiers, persistent storage, and ordered operations.

- Through StatefulSet, you can easily deploy and manage stateful applications such as databases and distributed systems while ensuring high availability and consistency of data.

- If you need to deploy stateless applications, using Deployment or ReplicaSet is more appropriate.