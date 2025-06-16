# oc and kubectl Cheatsheet

## oc (OpenShift CLI) Cheatsheet
The `oc` command is used to interact with OpenShift clusters, extending `kubectl` with OpenShift-specific features.

### Cluster Information
- **Login to cluster**: `oc login <api-url> -u <username> -p <password>`
- **Get current user**: `oc whoami`
- **View cluster info**: `oc cluster-info`
- **Get project list**: `oc projects`
- **Switch project**: `oc project <project-name>`

### Resource Management
- **List resources**: `oc get <resource> [-n <namespace>]` (e.g., `oc get pods`)
- **Describe resource**: `oc describe <resource> <name> [-n <namespace>]`
- **Delete resource**: `oc delete <resource> <name> [-n <namespace>]`
- **Create resource from file**: `oc create -f <file.yaml>`
- **Apply resource changes**: `oc apply -f <file.yaml>`

### Application Management
- **Create new app**: `oc new-app <image|template> [--name <app-name>]`
- **Deploy an image**: `oc import-image <image-name> --from=<registry> --confirm`
- **Expose service**: `oc expose svc/<service-name> [--hostname=<hostname>]`
- **Scale deployment**: `oc scale dc/<dc-name> --replicas=<number>`
- **Rollout new version**: `oc rollout latest dc/<dc-name>`
- **View rollout status**: `oc rollout status dc/<dc-name>`

### Logs and Debugging
- **View pod logs**: `oc logs <pod-name> [-c <container>]`
- **Exec into pod**: `oc exec <pod-name> -c <container> -- <command>`
- **Port forward**: `oc port-forward <pod-name> <local-port>:<pod-port>`
- **Debug pod**: `oc debug <pod-name>`

### OpenShift-Specific
- **Create build config**: `oc new-build <source> --name=<build-name>`
- **Start build**: `oc start-build <build-config-name>`
- **Manage routes**: `oc get routes`, `oc delete route <route-name>`
- **View templates**: `oc get templates [-n <namespace>]`
- **Process template**: `oc process -f <template.yaml> | oc create -f -`

## kubectl (Kubernetes CLI) Cheatsheet
The `kubectl` command is the standard CLI for interacting with Kubernetes clusters.

### Cluster Information
- **View cluster info**: `kubectl cluster-info`
- **Get contexts**: `kubectl config get-contexts`
- **Switch context**: `kubectl config use-context <context-name>`
- **View current context**: `kubectl config current-context`

### Resource Management
- **List resources**: `kubectl get <resource> [-n <namespace>] [--watch]` (e.g., `kubectl get pods`)
- **Describe resource**: `kubectl describe <resource> <name> [-n <namespace>]`
- **Delete resource**: `kubectl delete <resource> <name> [-n <namespace>]`
- **Create resource from file**: `kubectl create -f <file.yaml>`
- **Apply resource changes**: `kubectl apply -f <file.yaml>`
- **Edit resource**: `kubectl edit <resource> <name> [-n <namespace>]`

### Application Management
- **Create deployment**: `kubectl create deployment <name> --image=<image>`
- **Scale deployment**: `kubectl scale deployment/<name> --replicas=<number>`
- **Rollout update**: `kubectl set image deployment/<name> <container>=<image>`
- **View rollout status**: `kubectl rollout status deployment/<name>`
- **Rollback rollout**: `kubectl rollout undo deployment/<name>`

### Logs and Debugging
- **View pod logs**: `kubectl logs <pod-name> [-c <container>] [--follow]`
- **Exec into pod**: `kubectl exec <pod-name> -c <container> -- <command>`
- **Port forward**: `kubectl port-forward <pod-name> <local-port>:<pod-port>`
- **Debug pod**: `kubectl debug <pod-name>`

### Namespaces and RBAC
- **List namespaces**: `kubectl get namespaces`
- **Create namespace**: `kubectl create namespace <namespace>`
- **View roles**: `kubectl get roles [-n <namespace>]`
- **View role bindings**: `kubectl get rolebindings [-n <namespace>]`

## Comparison Table: oc vs kubectl

| **Feature/Aspect**              | **oc**                                                                 | **kubectl**                                                           |
|---------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------------|
| **Purpose**                     | CLI for OpenShift, extends `kubectl` with OpenShift-specific features | Standard CLI for Kubernetes clusters                                 |
| **Cluster Management**          | `oc login`, `oc cluster-info`, `oc projects`                         | `kubectl cluster-info`, `kubectl config use-context`                 |
| **Resource Management**         | Similar to `kubectl` (`oc get`, `oc apply`, `oc delete`)              | Core commands (`kubectl get`, `kubectl apply`, `kubectl delete`)     |
| **Application Deployment**      | `oc new-app`, `oc import-image`, `oc rollout`                         | `kubectl create deployment`, `kubectl set image`, `kubectl rollout`  |
| **Networking**                  | `oc expose`, `oc get routes` (OpenShift routes)                      | `kubectl expose`, services, and ingress (no routes)                  |
| **Builds and Pipelines**        | `oc new-build`, `oc start-build` (OpenShift build configs)           | Not available (Kubernetes does not manage builds)                    |
| **Templates**                   | `oc process`, `oc get templates` (OpenShift templates)               | Not available (use Helm or raw YAML for Kubernetes)                  |
| **Debugging**                   | `oc logs`, `oc exec`, `oc debug`, `oc port-forward`                  | `kubectl logs`, `kubectl exec`, `kubectl debug`, `kubectl port-forward` |
| **RBAC and Security**           | OpenShift-specific roles (`oc adm policy`)                           | Standard Kubernetes RBAC (`kubectl get roles`, `kubectl get rolebindings`) |
| **Use Case**                    | OpenShift clusters with enterprise features (routes, builds, templates) | Any Kubernetes cluster (vanilla, managed, or custom)                |
| **Compatibility**               | Works with OpenShift and Kubernetes APIs                             | Works with any Kubernetes cluster, but no OpenShift-specific features |
| **Extensibility**               | Includes `kubectl` commands; `oc` is a superset                      | Core Kubernetes CLI, extended by tools like Helm or Kustomize        |

### Notes
- **oc** is essentially a wrapper around `kubectl` with additional OpenShift-specific commands for managing builds, routes, and templates.
- **kubectl** is more generic and works with any Kubernetes cluster, while `oc` is tailored for OpenShift’s additional abstractions.
- Use `oc` for OpenShift-specific workflows (e.g., build pipelines, routes) and `kubectl` for standard Kubernetes operations or non-OpenShift clusters.
- Both tools support similar syntax for core Kubernetes resources (pods, services, deployments), but `oc` simplifies OpenShift-specific tasks.

