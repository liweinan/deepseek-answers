# Configuring an **Ingress Controller** to redirect traffic to multiple services running on different ports in a Kubernetes cluster.


To configure an **Ingress Controller** to redirect traffic to multiple services running on different ports in a Kubernetes cluster, you can use a single **Ingress** resource with multiple **path-based** or **host-based
** routing rules. Each rule can point to a specific service and its corresponding port. This is a common pattern for exposing multiple services (e.g., different applications or endpoints) under a single Ingress Controller, which typically listens on standard ports (80 for HTTP, 443 for HTTPS).

Below, I’ll explain how to set up an Ingress Controller to route traffic to multiple services on different ports, using
your existing `nginx-service` (port 8080) as an example, and adding another hypothetical service for context. I’ll also
provide a complete configuration and explain the concepts.

---

### Key Concepts

1. **Ingress Resource**:
    - An Ingress resource defines routing rules for external traffic to Kubernetes services.
    - Rules can be based on:
        - **Paths**: Different URL paths (e.g., `/app1`, `/app2`) route to different services.
        - **Hosts**: Different domains (e.g., `app1.example.com`, `app2.example.com`) route to different services.
    - Each path or host rule specifies a backend (a Service and its port).

2. **Service Ports**:
    - Each Kubernetes Service can expose one or more ports (e.g., `nginx-service` on port 8080).
    - The Ingress references the Service’s port (e.g., `number: 8080`) to route traffic to the correct backend.

3. **Ingress Controller**:
    - The Ingress Controller (e.g., `nginx-ingress`) listens on external ports (80/443) and proxies traffic to the
      specified Service ports based on the Ingress rules.
    - It doesn’t need to listen on the same ports as the backend Services (e.g., it can route HTTP port 80 to a Service
      on port 8080).

4. **Multiple Services**:
    - You can define multiple backend Services in one Ingress resource, each with its own port, by specifying different
      paths or hosts.
    - The Ingress Controller handles the routing logic transparently.

---

### Example Scenario

Let’s assume you have:

- **Service 1**: `nginx-service` (from your previous configuration), listening on port 8080, serving an Nginx
  application.
- **Service 2**: A hypothetical `other-service`, listening on port 9090, serving a different application (e.g., a
  Node.js app).

You want the Ingress Controller to:

- Route requests to `http://example.com/nginx` to `nginx-service` on port 8080.
- Route requests to `http://example.com/other` to `other-service` on port 9090.

Alternatively, you could use different domains:

- `http://nginx.example.com` → `nginx-service` (port 8080).
- `http://other.example.com` → `other-service` (port 9090).

---

### Step-by-Step Configuration

#### 1. Define the Services

Ensure both services are defined with their respective ports.

**nginx-service** (already exists from your YAML):

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
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

**other-service** (example):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: other-service
spec:
  selector:
    app: other-app
  ports:
    - protocol: TCP
      port: 9090
      targetPort: 9090
  type: ClusterIP
```

**Associated Deployment for other-service** (example):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: other-deployment
  labels:
    app: other-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: other-app
  template:
    metadata:
      labels:
        app: other-app
    spec:
      containers:
        - name: other-app
          image: node:18 # Example image
          ports:
            - containerPort: 9090
```

#### 2. Create the Ingress Resource

Define an Ingress resource to route traffic to both services based on **path-based routing** or **host-based routing**.

##### Option 1: Path-Based Routing

Route different paths to different services:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-service-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /nginx
            pathType: Prefix
            backend:
              service:
                name: nginx-service
                port:
                  number: 8080
          - path: /other
            pathType: Prefix
            backend:
              service:
                name: other-service
                port:
                  number: 9090
```

**Explanation**:

- Requests to `http://example.com/nginx/*` are routed to `nginx-service` on port 8080.
- Requests to `http://example.com/other/*` are routed to `other-service` on port 9090.
- The `rewrite-target: /` annotation ensures that the path (e.g., `/nginx`) is rewritten to `/` when forwarded to the
  backend, so the application doesn’t need to handle the `/nginx` prefix.
- Replace `example.com` with your actual domain or the Ingress Controller’s IP (e.g., `192.168.1.200`).

##### Option 2: Host-Based Routing

Route different domains to different services:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-service-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: nginx.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx-service
                port:
                  number: 8080
    - host: other.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: other-service
                port:
                  number: 9090
```

**Explanation**:

- Requests to `http://nginx.example.com/*` are routed to `nginx-service` on port 8080.
- Requests to `http://other.example.com/*` are routed to `other-service` on port 9090.
- No path rewriting is needed since the entire domain routes to the respective service.
- Configure DNS or your `/etc/hosts` file to map `nginx.example.com` and `other.example.com` to `192.168.1.200`.

#### 3. Apply the Configuration

Save the Ingress and Service configurations to a file (e.g., `multi-service-ingress.yaml`) and apply:

```bash
kubectl apply -f multi-service-ingress.yaml
```

If you’re adding `other-service` and its Deployment, include them in the YAML or apply separately.

#### 4. Verify the Ingress

Check the Ingress resource:

```bash
kubectl get ingress
```

Example output:

```
NAME                   CLASS    HOSTS                           ADDRESS         PORTS   AGE
multi-service-ingress  <none>   example.com                     192.168.1.200   80      5m
```

Or, for host-based:

```
NAME                   CLASS    HOSTS                           ADDRESS         PORTS   AGE
multi-service-ingress  <none>   nginx.example.com,other.example.com 192.168.1.200 80      5m
```

Describe the Ingress to confirm routing rules:

```bash
kubectl describe ingress multi-service-ingress
```

Look for the `Rules` section to verify paths or hosts point to the correct services and ports.

#### 5. Test the Setup

**For Path-Based Routing**:

```bash
curl http://192.168.1.200/nginx
curl http://192.168.1.200/other
```

- The first should return the Nginx welcome page (from `nginx-service`).
- The second should return the response from `other-service` (e.g., Node.js app output).

**For Host-Based Routing**:
Add entries to your `/etc/hosts` file (or equivalent):

```
192.168.1.200 nginx.example.com
192.168.1.200 other.example.com
```

Test:

```bash
curl http://nginx.example.com
curl http://other.example.com
```

**Using Port-Forward (for debugging)**:
If the Ingress isn’t working, test each Service directly:

```bash
kubectl port-forward svc/nginx-service 8080:8080
curl http://localhost:8080
```

```bash
kubectl port-forward svc/other-service 9090:9090
curl http://localhost:9090
```

#### 6. Ensure Ingress Controller is Configured

Your cluster already has an `nginx-ingress` controller running (at `192.168.1.200:80`, assigned by MetalLB). Verify it’s
healthy:

```bash
kubectl get pods -n ingress-nginx
```

Check logs if needed:

```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

If you need to support non-standard ports (e.g., redirecting to services on ports other than 80/443), the
`nginx-ingress` controller already supports this by specifying the Service port in the Ingress (e.g., `number: 8080`,
`number: 9090`).

---

### Complete Example YAML

Here’s a complete YAML combining `nginx-service`, `other-service`, and a path-based Ingress:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    events {}
    http {
        server {
            listen 8080;
            server_name localhost;
            location / {
                root /usr/share/nginx/html;
                index index.html index.htm;
            }
            error_page 500 502 503 504 /50x.html;
            location = /50x.html {
                root /usr/share/nginx/html;
            }
        }
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
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
            - containerPort: 8080
          volumeMounts:
            - name: nginx-config
              mountPath: /etc/nginx/nginx.conf
              subPath: nginx.conf
      volumes:
        - name: nginx-config
          configMap:
            name: nginx-config
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: other-deployment
  labels:
    app: other-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: other-app
  template:
    metadata:
      labels:
        app: other-app
    spec:
      containers:
        - name: other-app
          image: node:18
          ports:
            - containerPort: 9090
          command: [ "node", "-e", "require('http').createServer((req, res) => { res.writeHead(200); res.end('Hello from Other Service!'); }).listen(9090)" ]
---
apiVersion: v1
kind: Service
metadata:
  name: other-service
spec:
  selector:
    app: other-app
  ports:
    - protocol: TCP
      port: 9090
      targetPort: 9090
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-service-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /nginx
            pathType: Prefix
            backend:
              service:
                name: nginx-service
                port:
                  number: 8080
          - path: /other
            pathType: Prefix
            backend:
              service:
                name: other-service
                port:
                  number: 9090
```

**Deploy**:

```bash
kubectl apply -f multi-service-ingress.yaml
```

**Test**:

```bash
curl http://192.168.1.200/nginx
curl http://192.168.1.200/other
```

**Cleanup**:

```bash
kubectl delete -f multi-service-ingress.yaml
```

---

### Handling Multiple Ports in a Single Service

If a single Service exposes multiple ports (e.g., one app serving HTTP on 8080 and another protocol on 9090), you can define multiple ports in the Service and reference them in the Ingress.

**Example Service with Multiple Ports**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: multi-port-service
spec:
  selector:
    app: multi-app
  ports:
    - name: http
      protocol: TCP
      port: 8080
      targetPort: 8080
    - name: other
      protocol: TCP
      port: 9090
      targetPort: 9090
  type: ClusterIP
```

**Ingress for Multiple Ports**:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-port-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /http
            pathType: Prefix
            backend:
              service:
                name: multi-port-service
                port:
                  number: 8080
          - path: /other
            pathType: Prefix
            backend:
              service:
                name: multi-port-service
                port:
                  number: 9090
```

**Note**:

- The Service’s `ports` must have unique `name` fields (e.g., `http`, `other`) to distinguish them.
- The Ingress references the Service’s port numbers (e.g., `8080`, `9090`).

---

### Additional Considerations

1. **TLS/HTTPS**:
   To support HTTPS, add a `tls` section to the Ingress:
   ```yaml
   spec:
     tls:
     - hosts:
       - example.com
       secretName: example-tls
     rules:
     ...
   ```
   Create a TLS secret with your certificate:
   ```bash
   kubectl create secret tls example-tls --cert=path/to/cert --key=path/to/key
   ```

2. **Path Conflicts**:
   Ensure paths don’t overlap (e.g., `/nginx` and `/nginx/sub` may conflict). Use `pathType: Exact` for precise matching
   if needed.

3. **Multiple Ingress Controllers**:
   If you have multiple Ingress Controllers, specify the correct one with `kubernetes.io/ingress.class: nginx` or use
   `ingressClassName`:
   ```yaml
   spec:
     ingressClassName: nginx
   ```

4. **Performance**:
   For high-traffic services, consider scaling the Deployments (`replicas`) and tuning the Ingress Controller (e.g.,
   worker connections).

5. **Debugging**:
   If routing fails, check:
    - Ingress Controller logs: `kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx`
    - Service endpoints: `kubectl describe svc <service-name>`
    - Pod logs: `kubectl logs -l app=<app-name>`

---

### Your Specific Setup

Since you’re using the `nginx-ingress` controller with MetalLB at `192.168.1.200:80`, the above configurations will work
with your cluster. The Ingress Controller will handle external traffic on port 80 and route it to the specified Service
ports (8080, 9090, etc.) based on the rules.

If you want to test with your existing `nginx-service` and add another service, use the path-based Ingress example and
replace `other-service` with your second service’s details. Ensure the second service’s Deployment and Service are
deployed and running.

---

### Summary

- Use a single Ingress resource to route traffic to multiple services on different ports using **path-based** (`/nginx`,
  `/other`) or **host-based** (`nginx.example.com`, `other.example.com`) rules.
- Specify the Service and its port in the Ingress backend (e.g., `nginx-service:8080`, `other-service:9090`).
- The Ingress Controller listens on 80/443 and proxies to the Service ports transparently.
- Apply the provided YAML, test with `curl`, and verify with `kubectl describe ingress`.

If you have specific services or ports you want to configure, or if you encounter issues (e.g., with your
`nginx-service` still not responding on 8080), please provide details (e.g., the second service’s configuration, test
outputs), and I can tailor the solution further.