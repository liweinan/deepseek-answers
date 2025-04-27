# Configuring an **Ingress Controller
** to redirect traffic to multiple services running on different ports in a Kubernetes cluster.

To configure an **Ingress Controller** to redirect traffic to multiple services running on different ports in a
Kubernetes cluster, you can use a single **Ingress** resource with multiple **path-based** or **host-based
** routing rules. Each rule can point to a specific service and its corresponding port. This is a common pattern for
exposing multiple services (e.g., different applications or endpoints) under a single Ingress Controller, which
typically listens on standard ports (80 for HTTP, 443 for HTTPS).

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

If a single Service exposes multiple ports (e.g., one app serving HTTP on 8080 and another protocol on 9090), you can
define multiple ports in the Service and reference them in the Ingress.

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


---

The issue is that your Ingress configuration is not correctly routing requests to the backend services, resulting in 404
errors from the NGINX Ingress controller. Let's diagnose and fix the problem.

### Root Cause

1. **NGINX Configuration Conflict**: Your `ConfigMap` defines a custom `nginx.conf` that is mounted to the NGINX
   container in the `nginx-deployment`. This configuration is likely overriding the NGINX Ingress controller's
   configuration, causing it to serve requests directly from the NGINX pod instead of respecting the Ingress rules. The
   Ingress controller typically manages its own NGINX configuration, and your custom `nginx.conf` is interfering.
2. **Path Routing**: The `nginx.ingress.kubernetes.io/rewrite-target: /` annotation in the Ingress resource rewrites the
   request path to `/`, which might cause issues if the backend services expect the original path (`/nginx` or
   `/other`). This can lead to the backend services not finding the requested resource.
3. **Host Header**: The Ingress rule specifies `host: example.com`, but your `curl` commands (
   `curl http://192.168.1.200/nginx`) are not sending the `Host: example.com` header. If the Ingress controller is
   strictly enforcing the host, requests without the correct `Host` header may fail.

### Steps to Fix

#### 1. Remove Custom NGINX Configuration

The `ConfigMap` mounting a custom `nginx.conf` to `/etc/nginx/nginx.conf` in the `nginx-deployment` is likely causing
the NGINX pod to serve requests directly, bypassing the Ingress controller's routing logic. Since you're using an NGINX
Ingress controller, the Ingress controller should manage the NGINX configuration.

**Solution**: Remove the `ConfigMap` and the `volumeMount` for `nginx.conf` from the `nginx-deployment`. The NGINX
container should use its default configuration, and the Ingress controller will handle routing.

**Modified Deployment**:

```yaml
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
            - containerPort: 80  # Use default NGINX port (80) instead of 8080
```

**Remove**:

- The entire `ConfigMap` resource (`nginx-config`).
- The `volumeMounts` and `volumes` sections from the `nginx-deployment`.

**Update Service**:
Update the `nginx-service` to use port 80 (default NGINX port) instead of 8080:

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
  type: ClusterIP
```

**Update Ingress**:
Update the Ingress to reference the correct port for `nginx-service`:

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
                  number: 80  # Updated to 80
          - path: /other
            pathType: Prefix
            backend:
              service:
                name: other-service
                port:
                  number: 9090
```

#### 2. Adjust Path Rewrite Behavior

The `nginx.ingress.kubernetes.io/rewrite-target: /` annotation rewrites the incoming path (e.g., `/nginx/something`) to
`/` before forwarding to the backend. This means the `nginx-service` and `other-service` receive requests with the path
`/`, which may not match their expected routes.

**Solution**: If the backend services expect the original path (e.g., `/nginx` or `/other`), you can modify the rewrite
behavior or remove the annotation if unnecessary.

For example, to preserve the path prefix, use a more specific rewrite rule:

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /  # Optional: Remove if services can handle /nginx or /other directly
```

Alternatively, if the services expect the exact path, you can configure the rewrite to strip the prefix correctly:

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /nginx(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: nginx-service
                port:
                  number: 80
          - path: /other(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: other-service
                port:
                  number: 9090
```

This configuration captures the trailing path (e.g., `/nginx/something` becomes `/something`) and forwards it to the
backend.

#### 3. Test with Correct Host Header

Since the Ingress rule specifies `host: example.com`, you must include the `Host` header in your `curl` commands.
Without it, the Ingress controller may not match the rule and return a 404.

**Test Commands**:

```bash
curl -H "Host: example.com" http://192.168.1.200/nginx
curl -H "Host: example.com" http://192.168.1.200/other
```

Alternatively, add `example.com` to your `/etc/hosts` file to map it to `192.168.1.200`:

```bash
echo "192.168.1.200 example.com" | sudo tee -a /etc/hosts
```

Then test:

```bash
curl http://example.com/nginx
curl http://example.com/other
```

#### 4. Verify Backend Services

Ensure the backend services are responding correctly:

- For `nginx-service`, the NGINX container should serve the default welcome page at `/` (e.g.,
  `/usr/share/nginx/html/index.html`).
- For `other-service`, the Node.js server should respond with "Hello from Other Service!".

**Test Directly**:
Bypass the Ingress controller to verify the services:

```bash
kubectl port-forward svc/nginx-service 8080:80
curl http://localhost:8080  # Should return NGINX welcome page
```

```bash
kubectl port-forward svc/other-service 9090:9090
curl http://localhost:9090  # Should return "Hello from Other Service!"
```

If these fail, debug the pod logs:

```bash
kubectl logs -l app=nginx
kubectl logs -l app=other-app
```

#### 5. Verify Ingress Controller

Ensure the NGINX Ingress controller is properly installed and running:

```bash
kubectl get pods -n ingress-nginx
```

Check the Ingress controller logs for errors:

```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

If the Ingress controller is not installed, install it:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

### Updated Full Configuration

Here’s the corrected configuration:

```yaml
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
            - containerPort: 80
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
      port: 80
      targetPort: 80
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
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /
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
                  number: 80
          - path: /other
            pathType: Prefix
            backend:
              service:
                name: other-service
                port:
                  number: 9090
```

### Apply and Test

1. Apply the updated configuration:
   ```bash
   kubectl apply -f <your-config-file>.yaml
   ```
2. Test with the correct `Host` header:
   ```bash
   curl -H "Host: example.com" http://192.168.1.200/nginx
   curl -H "Host: example.com" http://192.168.1.200/other
   ```
3. Expected output:
    - `/nginx`: NGINX welcome page.
    - `/other`: "Hello from Other Service!".

### Additional Notes

- If you don’t need the `host: example.com` restriction, you can remove the `host` field from the Ingress rule to match
  all hosts:
  ```yaml
  spec:
    rules:
      - http:
          paths:
            - path: /nginx
              pathType: Prefix
              backend:
                service:
                  name: nginx-service
                  port:
                    number: 80
            - path: /other
              pathType: Prefix
              backend:
                service:
                  name: other-service
                  port:
                    number: 9090
  ```
- If you’re running this in a local environment (e.g., Minikube), ensure the Ingress controller is enabled:
  ```bash
  minikube addons enable ingress
  ```
- If the issue persists, provide the output of:
  ```bash
  kubectl describe pod -l app=nginx
  kubectl describe pod -l app=other-app
  kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
  ```

This should resolve the 404 errors and enable proper path-based routing. Let me know if you encounter further issues!

---

I'm glad the path-based routing is working! Now, let's create a Kubernetes configuration that uses **subdomains** instead of paths to serve different services. In this example, we'll configure an Ingress resource to route traffic to the same two services (`nginx-service` and `other-service`) using subdomains like `nginx.example.com` and `other.example.com` instead of paths like `/nginx` and `/other`.

### Overview
- We'll reuse the same `Deployment` and `Service` definitions for the NGINX and Node.js services from your original configuration (with the updated ports from the previous fix).
- We'll replace the path-based `Ingress` with a subdomain-based `Ingress` that routes traffic based on the `Host` header.
- The configuration assumes you're using an NGINX Ingress controller, and we'll ensure the setup is compatible with your environment.

### Subdomain-Based Ingress Configuration
In a subdomain-based setup, the Ingress resource defines rules for different `host` values. For example:
- `nginx.example.com` → Routes to `nginx-service` on port 80.
- `other.example.com` → Routes to `other-service` on port 9090.

Since you're testing locally (based on your use of `192.168.1.200`), we'll include instructions for testing subdomains using `/etc/hosts` or a similar approach.

### Full Configuration
Below is the complete Kubernetes configuration, including the `Deployment`, `Service`, and `Ingress` resources. The `Ingress` is updated to use subdomains instead of paths. The `ConfigMap` and custom NGINX configuration are omitted, as they were removed in the previous fix.

```yaml
```yaml
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
            - containerPort: 80
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
      port: 80
      targetPort: 80
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
          command: ["node", "-e", "require('http').createServer((req, res) => { res.writeHead(200); res.end('Hello from Other Service!'); }).listen(9090)"]
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
  name: subdomain-ingress
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
                  number: 80
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
```

### Explanation of Changes
1. **Ingress Resource**:
   - The `Ingress` is named `subdomain-ingress` to distinguish it from the previous `multi-service-ingress`.
   - Instead of a single `host: example.com` with multiple paths, we define two `host` rules:
     - `nginx.example.com`: Routes all requests (`/`) to `nginx-service` on port 80.
     - `other.example.com`: Routes all requests (`/`) to `other-service` on port 9090.
   - The `path: /` with `pathType: Prefix` ensures all requests to the subdomain are forwarded to the respective service.
   - The `nginx.ingress.kubernetes.io/rewrite-target` annotation is removed because we don’t need path rewriting for subdomain-based routing.

2. **Deployments and Services**:
   - The `nginx-deployment` and `nginx-service` remain unchanged, using the default NGINX port (80).
   - The `other-deployment` and `other-service` remain unchanged, using port 9090 for the Node.js service.
   - No `ConfigMap` or custom NGINX configuration is included, as the NGINX Ingress controller manages the routing.

### Applying the Configuration
1. Save the configuration to a file, e.g., `subdomain-ingress.yaml`.
2. Apply it to your cluster:
   ```bash
   kubectl apply -f subdomain-ingress.yaml
   ```

### Testing the Subdomain-Based Routing
Since you're testing locally with `192.168.1.200` (from your previous `curl` commands), you need to map the subdomains `nginx.example.com` and `other.example.com` to this IP address. You can do this by editing your `/etc/hosts` file or using `curl` with the `Host` header.

#### Option 1: Update `/etc/hosts`
1. Add the following lines to your `/etc/hosts` file:
   ```bash
   echo "192.168.1.200 nginx.example.com other.example.com" | sudo tee -a /etc/hosts
   ```
2. Test the subdomains:
   ```bash
   curl http://nginx.example.com
   curl http://other.example.com
   ```
3. Expected output:
   - `http://nginx.example.com`: NGINX welcome page (HTML content).
   - `http://other.example.com`: "Hello from Other Service!".

#### Option 2: Use `curl` with `Host` Header
If you don’t want to modify `/etc/hosts`, you can simulate the subdomain by setting the `Host` header:
```bash
curl -H "Host: nginx.example.com" http://192.168.1.200
curl -H "Host: other.example.com" http://192.168.1.200
```
Expected output is the same as above.

### Verifying the Ingress
Check the Ingress resource to ensure it’s configured correctly:
```bash
kubectl describe ingress subdomain-ingress
```
Expected output (abridged):
```
Name:             subdomain-ingress
Namespace:        default
Address:          192.168.1.200
Rules:
  Host                Path  Backends
  ----                ----  --------
  nginx.example.com   
                      /     nginx-service:80 (<pod-ip>:80)
  other.example.com   
                      /     other-service:9090 (<pod-ip>:9090)
Annotations:          kubernetes.io/ingress.class: nginx
```

### Troubleshooting
If the subdomains don’t work as expected:
1. **Verify Ingress Controller**:
   Ensure the NGINX Ingress controller is running:
   ```bash
   kubectl get pods -n ingress-nginx
   ```
   Check logs for errors:
   ```bash
   kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
   ```

2. **Check Service Availability**:
   Test the services directly to ensure they’re responding:
   ```bash
   kubectl port-forward svc/nginx-service 8080:80
   curl http://localhost:8080  # Should return NGINX welcome page
   ```
   ```bash
   kubectl port-forward svc/other-service 9090:9090
   curl http://localhost:9090  # Should return "Hello from Other Service!"
   ```

3. **Inspect Pods**:
   Check pod status and logs:
   ```bash
   kubectl describe pod -l app=nginx
   kubectl describe pod -l app=other-app
   kubectl logs -l app=nginx
   kubectl logs -l app=other-app
   ```

4. **DNS Resolution**:
   If you’re not seeing responses, ensure your `/etc/hosts` file or `Host` header is correctly set. Without proper DNS resolution, the Ingress controller won’t match the `host` rules.

### Notes
- **Real DNS**: In a production environment, you’d need to configure DNS records for `nginx.example.com` and `other.example.com` to point to your Ingress controller’s external IP or load balancer. For local testing, `/etc/hosts` or `Host` headers suffice.
- **TLS/HTTPS**: If you want to add TLS for secure connections, you can create a `Secret` with a TLS certificate and add a `tls` section to the Ingress. Let me know if you need an example!
- **Ingress Controller**: This configuration assumes you’re using the NGINX Ingress controller. If you’re using a different controller (e.g., Traefik, HAProxy), the annotations or `ingress.class` may need adjustment.

This configuration should give you a working subdomain-based routing setup. Let me know if you need further clarification or additional features, like TLS or scaling the deployments!