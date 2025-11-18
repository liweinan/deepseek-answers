# OpenShift's Three Core Resources

In OpenShift (based on Kubernetes), **Service Account**, **ConfigMap**, and **Secret** are three core resources used for managing authentication, configuration data, and sensitive information respectively. Here's a detailed explanation and comparison:

---

## **1. Service Account (Service Account)**
### **Purpose**
- **Authentication**: Provides identity for Pods or system components to interact with the OpenShift/Kubernetes API.
- **Access Control**: Associates permissions through `RoleBinding` or `ClusterRoleBinding` (RBAC).

### **Characteristics**
- Each namespace automatically generates a default Service Account (`default`).
- If not explicitly specified, Pods will automatically use the `default` Service Account at runtime.
- Used for secure access to cluster resources (such as creating Pods, reading Secrets).

### **Example**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: my-namespace
```

### **Use Cases**
- Pods need to call the Kubernetes API (such as CI/CD pipelines).
- Restrict Pod permissions (avoid using high-privilege `default` accounts).

---

## **2. ConfigMap (Configuration Map)**
### **Purpose**
- **Store non-sensitive configuration data** (such as environment variables, configuration files).
- Decouple configuration from container images for flexible management.

### **Characteristics**
- Data stored in key-value pairs format.
- Can be injected into Pods through environment variables or mounted as files.
- **Not encrypted**, not suitable for storing passwords, keys, and other sensitive information.

### **Example**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
  namespace: my-namespace
data:
  # Key-value pair configuration
  APP_COLOR: "blue"
  APP_MODE: "production"
  # Configuration file content
  config-file.properties: |
    server.port=8080
    logging.level=INFO
```

### **Use Cases**
- Application configuration (such as database connection strings, log levels).
- Dynamically adjust parameters without rebuilding images.

---

## **3. Secret (Secret)**
### **Purpose**
- **Store sensitive information** (such as passwords, TLS certificates, tokens).
- Data is Base64 encoded by default (not encrypted, needs RBAC and network policies for protection).

### **Characteristics**
- Types include:
    - `Opaque`: General secrets (such as username/password).
    - `kubernetes.io/tls`: TLS certificates.
    - `docker-registry`: Image repository authentication information.
- More secure than ConfigMap (but requires additional measures for true security).

### **Example**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
  namespace: my-namespace
type: Opaque
data:
  username: YWRtaW4=  # Base64 encoded "admin"
  password: MWYyZDFlMmU2N2Rm  # Base64 encoded "1f2d1e2e67df"
```

### **Use Cases**
- Database passwords, API keys.
- TLS certificates or image repository authentication.

---

## **Core Differences Between the Three**
| Feature                | Service Account         | ConfigMap               | Secret                  |
|------------------------|------------------------|-------------------------|-------------------------|
| **Purpose**            | Authentication and permission management | Store non-sensitive configuration | Store sensitive information |
| **Data Security**      | Protected by RBAC permissions | Plain text storage      | Base64 encoded (not encrypted) |
| **Typical Data**       | API access tokens        | Environment variables, config files | Passwords, certificates, tokens |
| **Encryption**         | No (but protected by RBAC) | No                      | No (requires additional encryption measures) |
| **Mounting Method**    | Automatically mounted to Pod | Environment variables or volume mounts | Environment variables or volume mounts |

---

## **Common Usage Methods**

### **1. Referencing ConfigMap/Secret in Pods**
#### **As Environment Variables**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: my-container
      image: nginx
      env:
        - name: APP_COLOR  # Injected from ConfigMap
          valueFrom:
            configMapKeyRef:
              name: my-config
              key: APP_COLOR
        - name: DB_PASSWORD  # Injected from Secret
          valueFrom:
            secretKeyRef:
              name: my-secret
              key: password
```

#### **As Volume Mounts**
```yaml
spec:
  containers:
    - name: my-container
      image: nginx
      volumeMounts:
        - name: config-volume
          mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        name: my-config
    - name: secret-volume
      secret:
        secretName: my-secret
```

### **2. Specifying Service Account for Pods**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-service-account  # Specify custom Service Account
  containers:
    - name: my-container
      image: nginx
```

---

## **Best Practices**
1. **Service Account**:
    - Avoid Pods using high-privilege `default` accounts, create minimum privilege accounts as needed.
2. **ConfigMap**:
    - Only store non-sensitive configurations, restart Pods after changes or use applications that support hot reloading.
3. **Secret**:
    - Combine with **SealedSecret** or **Vault** for encryption.
    - Limit access to Secrets (RBAC).

---

## **Summary**
- **Service Account**: Manages Pod identity and permissions.
- **ConfigMap**: Stores application configurations (non-sensitive).
- **Secret**: Stores sensitive data (requires additional protection).
- **Three Working Together**:  
  `Service Account` controls access permissions → `ConfigMap` provides configuration → `Secret` protects keys.