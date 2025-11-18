# Kubernetes Cheatsheet

## Basic Commands

```bash
kubectl version          # View client and server versions
kubectl cluster-info     # Display cluster information
kubectl get nodes        # View all nodes
kubectl config view      # View current configuration
kubectl api-resources    # View all API resource types
```

## Namespace Operations

```bash
kubectl get ns                     # View all namespaces
kubectl create ns <namespace>      # Create namespace
kubectl delete ns <namespace>      # Delete namespace
kubectl config set-context --current --namespace=<namespace> # Set default namespace
```

## Pod Operations

```bash
kubectl get pods [-n <namespace>]          # View Pod list
kubectl get pods -o wide                   # View Pod details (including node information)
kubectl describe pod <pod-name>            # View Pod detailed information
kubectl logs <pod-name> [-c <container>]   # View Pod logs
kubectl exec -it <pod-name> -- /bin/bash   # Enter Pod container
kubectl delete pod <pod-name>              # Delete Pod
kubectl top pod <pod-name>                 # View Pod resource usage
```

## Deployment Operations

```bash
kubectl get deployments                    # View all Deployments
kubectl describe deployment <deploy-name>  # View Deployment details
kubectl create deployment <name> --image=<image>  # Create Deployment
kubectl scale deployment <deploy-name> --replicas=3  # Scale up/down
kubectl edit deployment <deploy-name>      # Edit Deployment configuration
kubectl rollout status deployment/<deploy-name>  # View rolling update status
kubectl rollout history deployment/<deploy-name> # View update history
kubectl rollout undo deployment/<deploy-name>    # Rollback to previous version
kubectl rollout undo deployment/<deploy-name> --to-revision=2 # Rollback to specific version
kubectl delete deployment <deploy-name>    # Delete Deployment
```

## Service Operations

```bash
kubectl get services               # View all Services
kubectl expose deployment <deploy-name> --port=80 --target-port=8080 --type=NodePort # Create Service
kubectl describe service <svc-name> # View Service details
kubectl delete service <svc-name>  # Delete Service
```

## ConfigMap and Secret Operations

```bash
# ConfigMap
kubectl create configmap <name> --from-literal=key=value  # Create from literal
kubectl create configmap <name> --from-file=path/to/file  # Create from file
kubectl get configmaps             # View all ConfigMaps
kubectl describe configmap <name>  # View ConfigMap details

# Secret
kubectl create secret generic <name> --from-literal=key=value  # Create generic secret
kubectl create secret docker-registry <name> --docker-server=<server> --docker-username=<user> --docker-password=<pwd> # Create docker registry secret
kubectl get secrets               # View all Secrets
kubectl describe secret <name>    # View Secret details
```

## StatefulSet Operations

```bash
kubectl get statefulsets          # View all StatefulSets
kubectl describe statefulset <name> # View StatefulSet details
kubectl delete statefulset <name> # Delete StatefulSet
```

## Persistent Storage (PV/PVC)

```bash
kubectl get pv                    # View PersistentVolumes
kubectl get pvc                   # View PersistentVolumeClaims
kubectl describe pvc <pvc-name>   # View PVC details
```

## Workload Management

```bash
# Job
kubectl get jobs                  # View all Jobs
kubectl describe job <job-name>   # View Job details

# CronJob
kubectl get cronjobs              # View all CronJobs
kubectl describe cronjob <name>   # View CronJob details
```

## Network Policy (NetworkPolicy)

```bash
kubectl get networkpolicies       # View all network policies
kubectl describe networkpolicy <name> # View network policy details
```

## Resource Quotas and Limits

```bash
kubectl get quota                 # View resource quotas
kubectl describe quota <name>     # View quota details
kubectl get limitranges           # View limit ranges
```

## Debugging and Troubleshooting

```bash
kubectl get events --sort-by=.metadata.creationTimestamp  # View events (sorted by time)
kubectl get pods --field-selector=status.phase=Running    # Filter Pod status
kubectl port-forward <pod-name> 8080:80  # Port forwarding
kubectl cp <pod-name>:/path/to/file ./local-file  # Copy file from Pod
kubectl apply -f <file.yaml>      # Apply YAML configuration
kubectl delete -f <file.yaml>     # Delete resources defined in YAML
kubectl explain <resource>        # View resource definition documentation
```

## Common YAML Templates

### Pod Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.19
    ports:
    - containerPort: 80
```

### Deployment Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
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
        image: nginx:1.19
        ports:
        - containerPort: 80
```

### Service Example (NodePort)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30007
```

### ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.properties: |
    key1=value1
    key2=value2
```

### Secret Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: MWYyZDFlMmU2N2Rm
```

### PersistentVolumeClaim Example

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

## Common Tips

1. **Quickly create Pod and test**
   ```bash
   kubectl run -it --rm --image=busybox test-pod -- sh
   ```

2. **View Pod environment variables**
   ```bash
   kubectl exec <pod-name> -- env
   ```

3. **Force delete resources stuck in Terminating state**
   ```bash
   kubectl delete pod <pod-name> --grace-period=0 --force
   ```

4. **View Pod resource requests and limits**
   ```bash
   kubectl get pod <pod-name> -o json | jq '.spec.containers[].resources'
   ```

5. **View Pod scheduling events**
   ```bash
   kubectl get events --field-selector involvedObject.name=<pod-name>
   ```

6. **Use aliases to improve efficiency**
   ```bash
   alias k='kubectl'
   alias kgp='kubectl get pods'
   alias kgs='kubectl get services'
   ```

7. **Output in YAML or JSON format**
   ```bash
   kubectl get pod <pod-name> -o yaml
   kubectl get pod <pod-name> -o json
   ```

8. **Label selector queries**
   ```bash
   kubectl get pods -l app=nginx
   kubectl get pods -l 'environment in (production, staging)'
   ```

9. **View Pod IP addresses**
   ```bash
   kubectl get pod -o jsonpath='{.items[*].status.podIP}'
   ```

10. **Batch delete resources**
    ```bash
    kubectl delete pods,services -l name=myLabel
    ```

This Kubernetes cheatsheet covers the most commonly used commands and configurations in daily use, and can be used as a quick reference. Depending on your specific use cases, you may need to gain deeper understanding of certain specific areas.