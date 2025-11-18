# Let me analyze the collaborative working principle of ingress controller and loadbalancer type service. First, let me check the relevant configuration files in the ingress-example directory.


[4 tools called]

Now let me check the subdomain routing configuration files:


[1 tool called]

Based on the analysis of the ingress-example directory, let me explain in detail the collaborative working principle of Ingress Controller and LoadBalancer type Service:

## Ingress Controller and LoadBalancer Service Collaborative Working Principle

### 1. Overall Architecture Hierarchy

```
External Request → MetalLB LoadBalancer → Ingress Controller → Application Service
```

### 2. Core Component Collaboration Mechanism

#### **MetalLB's Role**
- **IP Allocation**: MetalLB assigns external IP to Ingress Controller's LoadBalancer service (like `192.168.1.200`)
- **L2 Mode**: Uses ARP/NDP protocol to advertise IP addresses in local network
- **Address Pool Management**: Allocates addresses from configured IP range (`192.168.1.200-192.168.1.250`)

#### **Ingress Controller's Role**
- **Entry Point**: Acts as the single entry point for the cluster, receiving all external traffic
- **Routing Decision**: Performs request routing based on Ingress rules
- **Load Balancing**: Distributes requests among multiple backend Pods

### 3. Detailed Workflow

#### **Step 1: Service Discovery and IP Assignment**
```yaml
# MetalLB Configuration
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.200-192.168.1.250
```

#### **Step 2: Ingress Controller Service Configuration**
```bash
# Actual deployed service status
NAME                                 TYPE           CLUSTER-IP       EXTERNAL-IP     PORT(S)
ingress-nginx-controller             LoadBalancer   10.152.183.101   192.168.1.200   80:30236/TCP,443:32580/TCP
```

#### **Step 3: Application Service Configuration**
```yaml
# Application service uses ClusterIP, not directly exposed
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
  type: ClusterIP  # Key: Use ClusterIP, not LoadBalancer
```

### 4. Request Processing Flow

#### **External Request Processing**
1. **DNS Resolution**: Client resolves domain name to `192.168.1.200`
2. **Network Routing**: Request reaches IP address assigned by MetalLB
3. **LoadBalancer Forwarding**: MetalLB forwards request to Ingress Controller Pod
4. **Ingress Routing**: Ingress Controller routes to backend service according to rules

#### **Path Routing Example**
```yaml
# Multi-service path routing
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-service-ingress
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

### 5. Kubernetes Internal Working Principles

#### **Service Type Hierarchy**
```
LoadBalancer Service (Ingress Controller)
    ↓
ClusterIP Service (Application Service)
    ↓
Pod (Application Instance)
```

#### **Network Traffic Path**
1. **External Network** → **MetalLB** → **Ingress Controller Pod**
2. **Ingress Controller** → **Application Service** → **Application Pod**

#### **Key Design Principles**
- **Single Entry Point**: All external traffic enters through Ingress Controller
- **Service Isolation**: Application services use ClusterIP, not directly exposed
- **Centralized Routing**: All routing rules managed uniformly in Ingress

### 6. Actual Access Examples

#### **Path Routing Access**
```bash
# Access Nginx service
curl -H "Host: example.com" http://192.168.1.200/nginx

# Access other services
curl -H "Host: example.com" http://192.168.1.200/other
```

#### **Subdomain Routing Access**
```bash
# Access via subdomain
curl -H "Host: nginx.example.com" http://192.168.1.200
curl -H "Host: other.example.com" http://192.168.1.200
```

### 7. Advantages Analysis

#### **Architecture Advantages**
- **Cost Effective**: No need for cloud provider load balancers
- **Simplified Management**: Unified entry point and routing rules
- **Flexible Configuration**: Supports path and domain routing
- **Standard Compatible**: Uses Kubernetes standard interfaces

#### **Network Advantages**
- **L2 Mode**: Suitable for local network environments
- **IP Persistence**: Assigned IP addresses remain stable
- **Failover**: Supports high availability deployment

This architecture is particularly suitable for bare metal Kubernetes clusters, providing LoadBalancer functionality through MetalLB, combined with Ingress Controller to achieve complete service exposure and routing management.

---

Based on the `multi-service-ingress-by-path.yaml` file, let me explain in detail how Ingress rules are configured to specific Ingress Controllers.

## Ingress Rule Configuration to Ingress Controller Mechanism

### 1. Ingress Rule Recognition Mechanism

In `multi-service-ingress-by-path.yaml`, the key configuration is:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-service-ingress
  annotations:
    kubernetes.io/ingress.class: nginx  # Key: specify Ingress Controller type
    nginx.ingress.kubernetes.io/rewrite-target: /
```

### 2. Ingress Controller Selection Mechanism

#### **Method 1: Specify via Annotation (Traditional Method)**
```yaml
annotations:
  kubernetes.io/ingress.class: nginx
```

#### **Method 2: Via IngressClass Resource (Modern Method)**
```yaml
spec:
  ingressClassName: nginx
```

### 3. Configuration Propagation Process

#### **Step 1: Ingress Resource Creation**
```bash
kubectl apply -f multi-service-ingress-by-path.yaml
```

#### **Step 2: Ingress Controller Monitoring**
- Ingress Controller listens to Ingress resource changes through Kubernetes API
- Uses `kubernetes.io/ingress.class: nginx` annotation to identify rules that need processing

#### **Step 3: Configuration Update**
- Ingress Controller reads Ingress rules
- Updates internal configuration (like Nginx config file)
- Reloads configuration

### 4. Specific Configuration Mapping Process

#### **Ingress Rule Parsing**
```yaml
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

#### **Convert to Nginx Configuration**
Ingress Controller will convert the above rules to Nginx configuration similar to:

```nginx
server {
    listen 80;
    server_name example.com;
    
    location /nginx {
        rewrite /nginx/(.*) /$1 break;
        proxy_pass http://nginx-service.default.svc.cluster.local:80;
    }
    
    location /other {
        rewrite /other/(.*) /$1 break;
        proxy_pass http://other-service.default.svc.cluster.local:9090;
    }
}
```

### 5. Verify Configuration Effectiveness

#### **Check Ingress Status**
```bash
kubectl get ingress multi-service-ingress
kubectl describe ingress multi-service-ingress
```

#### **Check Ingress Controller Configuration**
```bash
# View Ingress Controller Pod logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Check configuration updates
kubectl exec -n ingress-nginx deployment/ingress-nginx-controller -- cat /etc/nginx/nginx.conf
```

### 6. Configuration Update Mechanism

#### **Real-time Updates**
- Ingress Controller uses Kubernetes Watch API to listen to Ingress resource changes
- When Ingress rules are updated, configuration is automatically reloaded

#### **Configuration Validation**
```bash
# Test if configuration is correct
curl -H "Host: example.com" http://192.168.1.200/nginx
curl -H "Host: example.com" http://192.168.1.200/other
```

### 7. Multiple Ingress Controller Scenarios

#### **Different Ingress Controllers Coexistence**
```yaml
# Nginx Ingress Controller
annotations:
  kubernetes.io/ingress.class: nginx

# Traefik Ingress Controller  
annotations:
  kubernetes.io/ingress.class: traefik

# Istio Ingress Controller
annotations:
  kubernetes.io/ingress.class: istio
```

#### **IngressClass Resource (Recommended Method)**
```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: nginx
spec:
  controller: k8s.io/ingress-nginx
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-service-ingress
spec:
  ingressClassName: nginx  # Use IngressClass instead of annotation
```

### 8. Troubleshooting

#### **Common Issues**
1. **Ingress Controller Not Recognizing Rules**
   ```bash
   # Check if annotation is correct
   kubectl get ingress multi-service-ingress -o yaml
   ```

2. **Configuration Not Taking Effect**
   ```bash
   # Check Ingress Controller logs
   kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
   ```

3. **Service Cannot Be Accessed**
   ```bash
   # Check backend service status
   kubectl get svc nginx-service other-service
   kubectl get pods -l app=nginx
   kubectl get pods -l app=other-app
   ```

### 9. Configuration Best Practices

#### **Annotation Usage**
```yaml
annotations:
  kubernetes.io/ingress.class: nginx
  nginx.ingress.kubernetes.io/rewrite-target: /
  nginx.ingress.kubernetes.io/ssl-redirect: "false"
  nginx.ingress.kubernetes.io/force-ssl-redirect: "false"
```

#### **Path Configuration**
```yaml
paths:
  - path: /nginx
    pathType: Prefix  # Exact match, prefix match, or regex match
    backend:
      service:
        name: nginx-service
        port:
          number: 80
```

Summary: Yes, Ingress rules will eventually be configured to the specific Nginx service. Ingress Controller acts as a middle layer, responsible for converting Kubernetes Ingress resources to standard Nginx configuration files, and making configuration effective through hot reload mechanism.

---

Yes, absolutely correct! When Ingress Controller uses Nginx, an Ingress rule will eventually be configured to the specific Nginx service. Let me explain this process in detail:

## Ingress Rule to Nginx Configuration Conversion Process

### 1. Configuration Conversion Process

```
Ingress Resource → Ingress Controller → Nginx Config File → Nginx Service
```

### 2. Specific Conversion Example

Based on the rules in `multi-service-ingress-by-path.yaml`:

```yaml
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

### 3. Convert to Nginx Configuration

Ingress Controller will convert the above rules to Nginx configuration similar to:

```nginx
# In /etc/nginx/nginx.conf
upstream upstream_balancer {
    # nginx-service Pod IP list
    server 10.244.1.5:80;
    server 10.244.2.3:80;
}

upstream upstream_balancer_other {
    # other-service Pod IP list  
    server 10.244.1.8:9090;
    server 10.244.2.6:9090;
}

server {
    listen 80;
    server_name example.com;
    
    location /nginx {
        # Rewrite path, remove /nginx prefix
        rewrite /nginx/(.*) /$1 break;
        proxy_pass http://upstream_balancer;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /other {
        # Rewrite path, remove /other prefix
        rewrite /other/(.*) /$1 break;
        proxy_pass http://upstream_balancer_other;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4. Configuration Update Mechanism

#### **Real-time Configuration Updates**
```bash
# Ingress Controller monitors Ingress resource changes
kubectl get ingress multi-service-ingress -w

# When Ingress rules are updated, Nginx configuration automatically updates
# 1. Read new Ingress rules
# 2. Generate new Nginx configuration
# 3. Reload Nginx service
```

#### **Configuration Validation**
```bash
# View actual Nginx configuration
kubectl exec -n ingress-nginx deployment/ingress-nginx-controller -- cat /etc/nginx/nginx.conf

# View generated configuration files
kubectl exec -n ingress-nginx deployment/ingress-nginx-controller -- ls -la /etc/nginx/conf.d/
```

### 5. Annotation to Nginx Directive Mapping

#### **Rewrite Rule Mapping**
```yaml
# Ingress annotation
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /
```

Converted to Nginx directives:
```nginx
# Nginx configuration
rewrite /nginx/(.*) /$1 break;
rewrite /other/(.*) /$1 break;
```

#### **Other Common Annotation Mappings**
```yaml
# Ingress annotation
annotations:
  nginx.ingress.kubernetes.io/ssl-redirect: "true"
  nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
  nginx.ingress.kubernetes.io/proxy-body-size: "1m"
```

Converted to Nginx configuration:
```nginx
# Nginx configuration
return 301 https://$server_name$request_uri;
client_max_body_size 1m;
```

### 6. Service Discovery and Load Balancing

#### **Backend Service Discovery**
```bash
# Ingress Controller automatically discovers backend Pods
kubectl get endpoints nginx-service
kubectl get endpoints other-service
```

#### **Dynamic Updates**
```nginx
# Upstream in Nginx configuration will be dynamically updated
upstream upstream_balancer {
    # When Pods restart or scale, these IPs will be automatically updated
    server 10.244.1.5:80;
    server 10.244.2.3:80;
    server 10.244.3.7:80;  # Newly added Pod
}
```

### 7. Configuration Hot Reload

#### **Nginx Configuration Reload**
```bash
# Executed internally by Ingress Controller
nginx -s reload

# Or through signal
kill -HUP <nginx_pid>
```

#### **Zero Downtime Updates**
- Configuration updates won't interrupt existing connections
- New connections use new configuration
- Existing connections continue using old configuration until complete

### 8. Actual Verification

#### **View Generated Configuration**
```bash
# Enter Ingress Controller Pod
kubectl exec -n ingress-nginx -it deployment/ingress-nginx-controller -- /bin/bash

# View generated configuration file
cat /etc/nginx/conf.d/default-multi-service-ingress.conf
```

#### **Test Configuration Effectiveness**
```bash
# Test path routing
curl -H "Host: example.com" http://192.168.1.200/nginx
curl -H "Host: example.com" http://192.168.1.200/other

# View Nginx access logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### 9. Configuration Management Best Practices

#### **Configuration Templates**
Ingress Controller uses templates to generate Nginx configuration:
```go
// Pseudo-code example
func generateNginxConfig(ingress *Ingress) string {
    template := `
    server {
        listen 80;
        server_name {{.Host}};
        {{range .Paths}}
        location {{.Path}} {
            rewrite {{.Path}}/(.*) /$1 break;
            proxy_pass http://{{.Service}};
        }
        {{end}}
    }`
    return render(template, ingress)
}
```

#### **Configuration Validation**
```bash
# Test Nginx configuration syntax
kubectl exec -n ingress-nginx deployment/ingress-nginx-controller -- nginx -t
```

Summary: Yes, Ingress rules will eventually be configured to the specific Nginx service. Ingress Controller acts as a middle layer, responsible for converting Kubernetes Ingress resources to standard Nginx configuration files, and making configuration effective through hot reload mechanism.