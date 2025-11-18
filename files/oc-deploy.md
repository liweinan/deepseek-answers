# Concise Tutorial for Deploying Nginx Application on OpenShift Local (CRC)

This tutorial guides you through deploying an Nginx application on OpenShift Local (CRC) on macOS, based on OpenShift 4.18.2, running in the `my-demo` namespace, accessing the service through `127.0.0.1` and CRC's automatically modified `/etc/hosts`. The tutorial includes proxy configuration, permission configuration, correct configuration files, and methods to access the Service.

## Prerequisites

- **Environment**: macOS, with CRC and `oc` CLI installed.
- **Namespace**: `my-demo` (created via `oc new-project my-demo`).
- **Image**: `docker.io/library/nginx:latest` (no authentication required).
- **Network**: Uses `127.0.0.1`, CRC automatically updates `/etc/hosts` to resolve domain names, proxy is `squid.corp.redhat.com:3128`.

## Objectives

- Deploy Nginx Pod with `Running` status.
- Configure Service and Route, access service through `127.0.0.1`.
- Ensure proxy and permissions are correctly set.

---

## Tutorial Steps

### 1. Proxy Configuration

Configure CRC and cluster to use proxy, ensuring normal image pulling.

#### 1.1 Set Proxy

```bash
export HTTP_PROXY=http://squid.corp.redhat.com:3128
export HTTPS_PROXY=http://squid.corp.redhat.com:3128
export NO_PROXY=localhost,127.0.0.1,.crc.testing,.apps-crc.testing
crc config set http-proxy $HTTP_PROXY
crc config set https-proxy $HTTPS_PROXY
crc config set no-proxy "$NO_PROXY"
```

#### 1.2 Restart CRC

```bash
crc stop
crc start
```

---

### 2. Permission Configuration

Grant necessary permissions to `developer` user and `default` service account, ensuring ability to create resources and use `anyuid` SCC.

#### 2.1 Grant `developer` Permissions

Bind `edit` role to `developer` user in `my-demo` namespace:

```bash
oc create rolebinding developer-edit --clusterrole=edit --user=developer -n my-demo
```

Verify:

```bash
oc auth can-i create configmaps -n my-demo
oc auth can-i create pods -n my-demo
oc auth can-i create services -n my-demo
oc auth can-i create routes -n my-demo
```

- Expected: `yes`

#### 2.2 Grant `anyuid` SCC

As `kubeadmin` user, bind `anyuid` SCC to `default` service account:

```bash
oc login -u kubeadmin
oc adm policy add-scc-to-user anyuid -z default -n my-demo
oc login -u developer
```

Verify:

```bash
oc describe clusterrolebinding | grep anyuid
```

- Confirm inclusion of `system:serviceaccount:my-demo:default`.

---

### 3. Configuration Files

Here are verified runnable configuration files for deploying Nginx Pod, Service, and Route.

#### 3.1 ConfigMap (`nginx-config.yaml`)

Create Nginx configuration file, listening on port 8080:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: my-demo
data:
  nginx.conf: |
    worker_processes auto;
    events {
      worker_connections 1024;
    }
    http {
      include /etc/nginx/conf.d/*.conf;
    }
  default.conf: |
    server {
      listen 8080;
      server_name localhost;
      location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
      }
    }
```

Apply:

```bash
oc apply -f nginx-config.yaml
```

#### 3.2 Pod (`nginx-pod.yaml`)

Deploy Nginx Pod, using `anyuid` SCC and `emptyDir` volumes:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  namespace: my-demo
  labels:
    app: nginx
spec:
  securityContext:
    fsGroup: 101
  containers:
    - name: nginx
      image: docker.io/library/nginx:latest
      securityContext:
        runAsUser: 101
        runAsGroup: 101
      volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf
        - name: nginx-config
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: default.conf
        - name: nginx-cache
          mountPath: /var/cache/nginx
        - name: nginx-run
          mountPath: /run
      ports:
        - containerPort: 8080
  volumes:
    - name: nginx-config
      configMap:
        name: nginx-config
    - name: nginx-cache
      emptyDir: { }
    - name: nginx-run
      emptyDir: { }
```

Apply:

```bash
oc apply -f nginx-pod.yaml
```

#### 3.3 Service (`nginx-service.yaml`)

Expose Nginx Pod:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: my-demo
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

Apply:

```bash
oc apply -f nginx-service.yaml
```

#### 3.4 Route (`nginx-route.yaml`)

Create external route:

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: nginx-route
  namespace: my-demo
spec:
  to:
    kind: Service
    name: nginx-service
  port:
    targetPort: 8080
  wildcardPolicy: None
```

Apply:

```bash
oc apply -f nginx-route.yaml
```

---

### 4. Access Service

Service is accessed through `127.0.0.1`, CRC automatically adds route hostname to `/etc/hosts`.

#### 4.1 Confirm `/etc/hosts`

Check `/etc/hosts`:

```bash
cat /etc/hosts
```

- CRC will automatically add:
  ```
  127.0.0.1        nginx-route-my-demo.apps-crc.testing
  ```
- No manual modification needed, CRC updates when Route is created or cluster starts.

#### 4.2 Access Route

```bash
curl http://nginx-route-my-demo.apps-crc.testing
```

- Expected: Returns Nginx welcome page:
  ```
  <!DOCTYPE html>
  <html>
  <head>
  <title>Welcome to nginx!</title>
  ...
  <h1>Welcome to nginx!</h1>
  ...
  </html>
  ```

#### 4.3 Bypass Proxy

If access fails, ensure proxy doesn't interfere:

```bash
unset HTTP_PROXY HTTPS_PROXY
curl http://nginx-route-my-demo.apps-crc.testing
```

Or:

```bash
export NO_PROXY=localhost,127.0.0.1,.crc.testing,.apps-crc.testing
curl http://nginx-route-my-demo.apps-crc.testing
```

---

### Verification

```bash
oc get pods -n my-demo
oc get svc nginx-service -n my-demo
oc get route nginx-route -n my-demo
curl http://nginx-route-my-demo.apps-crc.testing
```

---

### Cleanup

```bash
oc login -u kubeadmin
oc adm policy remove-scc-from-user anyuid -z default -n my-demo
oc login -u developer
oc delete pod nginx-pod -n my-demo
oc delete svc nginx-service -n my-demo
oc delete route nginx-route -n my-demo
oc delete configmap nginx-config -n my-demo
oc delete rolebinding developer-edit -n my-demo
```

---

### Notes

- **Proxy**: Ensure `NO_PROXY` includes `localhost`, `127.0.0.1`, `.crc.testing`, `.apps-crc.testing` to avoid interfering with local access.
- **Permissions**: `developer` user needs `edit` role, `default` service account needs `anyuid` SCC.
- **Domain**: CRC automatically manages `/etc/hosts`, no manual modification needed.
- **Firewall**: If access fails, check macOS firewall:
  ```bash
  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
  ```

---

### Summary

This tutorial provides a complete process for deploying Nginx applications on macOS using CRC, accessing services through `127.0.0.1` and CRC's automatically updated `/etc/hosts`. Proxy configuration ensures image pulling, permission configuration supports Pod deployment, configuration files are verified, and access methods are simple and reliable.

For further assistance, please provide:

- Output of `oc get route -n my-demo`.
- Latest content of `/etc/hosts`.
- Result of `curl http://nginx-route-my-demo.apps-crc.testing` (if failed).

Wish you successful deployment!