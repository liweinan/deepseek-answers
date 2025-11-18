# Deleting Services, Deployments and Corresponding Pods in Kubernetes

In Kubernetes, there are several methods to delete a complete application resource (including Service, Deployment and corresponding Pods):

## Method 1: Delete Resources Individually

```bash
# Delete Service
kubectl delete service <service-name>

# Delete Deployment (will automatically delete corresponding ReplicaSet and Pods)
kubectl delete deployment <deployment-name>
```

## Method 2: Delete Using Label Selectors

If your resources have common labels (recommended practice), you can use label selectors to delete them all at once:

```bash
# View resources and their labels
kubectl get svc,deploy,pods --show-labels

# Delete using label selector (e.g. app=my-app)
kubectl delete svc,deploy,pods -l app=<your-app-label>
```

## Method 3: Delete Entire Namespace (Use with Caution)

If all your resources are in the same namespace, you can delete the entire namespace:

```bash
# Delete namespace and all its resources
kubectl delete namespace <namespace-name>
```

## Method 4: Delete Using kubectl Wildcards

```bash
# Delete all resources matching name patterns
kubectl delete all --all -n <namespace>  # Delete all resources in namespace
kubectl delete all -l app=<your-app-label>  # Delete all resources with specific label
```

## Method 5: Delete via Manifest Files

If you originally created resources through YAML files, you can use the same files to delete them:

```bash
kubectl delete -f your-deployment-and-service.yaml
```

## Notes

1. **Deletion Order**: Usually no need to pay special attention to deletion order, as Kubernetes will automatically handle dependencies

2. **Pod Deletion**: When you delete a Deployment, its managed ReplicaSet and Pods will be automatically deleted

3. **Verify Deletion**: After deletion, you can run the following commands to verify:
   ```bash
   kubectl get svc,deploy,pods
   ```

4. **Persistent Storage**: If PersistentVolumeClaims are used, they need to be deleted separately:
   ```bash
   kubectl delete pvc <pvc-name>
   ```

5. **ConfigMaps and Secrets**: If there are related ConfigMaps or Secrets, they also need to be deleted separately

## Recommended Practices

1. **Use Labels**: Apply the same labels to related resources for easier unified management
2. **Use Namespaces**: Use different namespaces for different applications
3. **Use Manifest Files**: Manage resources through YAML files for easier version control and repeated deployment

Through these methods, you can thoroughly clean up related resources in the Kubernetes cluster.