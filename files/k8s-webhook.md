# Using `kubebuilder` to Create Projects with Webhook Functionality for Custom Resource Validation (ValidatingWebhook) or Mutation (MutatingWebhook)

Projects created with `kubebuilder` can enable webhook functionality to implement validation (ValidatingWebhook) or mutation (MutatingWebhook) of custom resources. Webhook data content is typically `AdmissionReview` requests sent by Kubernetes API Server to webhook servers, and `AdmissionReview` responses returned by webhook servers. Below is a typical webhook data content example, including request and response structures.

![image](https://github.com/user-attachments/assets/dd00a804-3c7e-45ea-9420-4b4e8e309b18)

### 1. **AdmissionReview Request Example**
Kubernetes API Server sends `AdmissionReview` requests to webhook servers containing resource information to be validated or mutated. Below is a JSON format request example:

```json
{
  "apiVersion": "admission.k8s.io/v1",
  "kind": "AdmissionReview",
  "request": {
    "uid": "705ab4f5-6393-11e8-b7cc-42010a800002",
    "kind": {
      "group": "example.com",
      "version": "v1",
      "kind": "Foo"
    },
    "resource": {
      "group": "example.com",
      "version": "v1",
      "resource": "foos"
    },
    "requestKind": {
      "group": "example.com",
      "version": "v1",
      "kind": "Foo"
    },
    "requestResource": {
      "group": "example.com",
      "version": "v1",
      "resource": "foos"
    },
    "name": "my-foo",
    "namespace": "default",
    "operation": "CREATE",
    "userInfo": {
      "username": "system:serviceaccount:kube-system:generic-garbage-collector",
      "uid": "7903a66e-6392-11e8-b7cc-42010a800002",
      "groups": [
        "system:serviceaccounts",
        "system:serviceaccounts:kube-system",
        "system:authenticated"
      ]
    },
    "object": {
      "apiVersion": "example.com/v1",
      "kind": "Foo",
      "metadata": {
        "name": "my-foo",
        "namespace": "default"
      },
      "spec": {
        "field": "value"
      }
    },
    "oldObject": null,
    "dryRun": false,
    "options": {}
  }
}
```

#### Key Field Descriptions:
- `uid`: Unique identifier for the request, used for matching in responses
- `kind` / `resource`: Describes the resource type being operated on (e.g., custom resource `Foo`)
- `operation`: Operation type (`CREATE`, `UPDATE`, `DELETE`, `CONNECT`)
- `object`: Current requested resource object (for `CREATE` and `UPDATE`)
- `oldObject`: For `UPDATE` or `DELETE`, contains the previous state of the resource (null for `CREATE`)
- `userInfo`: User information performing the operation
- `namespace`: Namespace where the resource is located (if applicable)

### 2. **AdmissionReview Response Example**
After processing the request, webhook servers return `AdmissionReview` responses indicating whether the operation is allowed (validation webhook) or modifications to the resource (mutation webhook). Below is a JSON response example:

#### Validation Webhook (ValidatingWebhook) Response
Validation webhooks check if resources comply with rules and decide whether to allow operations.

```json
{
  "apiVersion": "admission.k8s.io/v1",
  "kind": "AdmissionReview",
  "response": {
    "uid": "705ab4f5-6393-11e8-b7cc-42010a800002",
    "allowed": true
  }
}
```

If validation fails, rejection information can be returned:

```json
{
  "apiVersion": "admission.k8s.io/v1",
  "kind": "AdmissionReview",
  "response": {
    "uid": "705ab4f5-6393-11e8-b7cc-42010a800002",
    "allowed": false,
    "status": {
      "code": 403,
      "message": "Spec.field must not be empty"
    }
  }
}
```

#### Mutation Webhook (MutatingWebhook) Response
Mutation webhooks can modify resource content through the `patch` field returning JSON Patch.

```json
{
  "apiVersion": "admission.k8s.io/v1",
  "kind": "AdmissionReview",
  "response": {
    "uid": "705ab4f5-6393-11e8-b7cc-42010a800002",
    "allowed": true,
    "patchType": "JSONPatch",
    "patch": "W3sib3AiOiAiYWRkIiwgInBhdGgiOiAiL3NwZWMvbmV3RmllbGQiLCAidmFsdWUiOiAibXlWYWx1ZSJ9XQ=="
  }
}
```

#### Key Field Descriptions:
- `uid`: Must match the `uid` in the request
- `allowed`: Whether the operation is allowed (`true` means allow, `false` means reject)
- `status`: If `allowed` is `false`, can provide reason for rejection and HTTP status code
- `patchType`: If it's a mutation webhook, the type of patch returned (usually `JSONPatch`)
- `patch`: Patch content based on JSON Patch (RFC 6902), Base64 encoded. For example, the Base64 decoded content above is:
  ```json
  [{"op": "add", "path": "/spec/newField", "value": "myValue"}]
  ```
  Indicates adding a field `newField` to the resource's `spec`

### 3. **Implementation in Kubebuilder Projects**
In Kubebuilder projects, webhook implementations are typically in `api/v1/<kind>_webhook.go` files (e.g., `foo_webhook.go`). Below is a simple validation webhook implementation example:

```go
package v1

import (
	"context"
	"fmt"

	apierrors "k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/webhook"
	"sigs.k8s.io/controller-runtime/pkg/webhook/admission"
)

// +kubebuilder:webhook:path=/validate-example-com-v1-foo,mutating=false,failurePolicy=fail,sideEffects=None,groups=example.com,resources=foos,verbs=create;update,versions=v1,name=vfoo.kb.io,admissionReviewVersions=v1

func (r *Foo) SetupWebhookWithManager(mgr ctrl.Manager) error {
	return ctrl.NewWebhookManagedBy(mgr).
		For(r).
		Complete()
}

// +kubebuilder:webhook:verbs=create;update,path=/validate-example-com-v1-foo,mutating=false,failurePolicy=fail,groups=example.com,resources=foos,versions=v1,name=vfoo.kb.io,sideEffects=None,admissionReviewVersions=v1

func (r *Foo) ValidateCreate() (admission.Warnings, error) {
	if r.Spec.Field == "" {
		return nil, apierrors.NewInvalid(
			r.GroupVersionKind().GroupKind(),
			r.Name,
			field.ErrorList{
				field.Invalid(field.NewPath("spec").Child("field"), r.Spec.Field, "field must not be empty"),
			})
	}
	return nil, nil
}

func (r *Foo) ValidateUpdate(old runtime.Object) (admission.Warnings, error) {
	return r.ValidateCreate()
}

func (r *Foo) ValidateDelete() (admission.Warnings, error) {
	return nil, nil
}
```

#### Notes:
- `+kubebuilder:webhook` annotations define webhook configuration (path, operations, resources, etc.)
- `ValidateCreate` and `ValidateUpdate` methods implement validation logic, returning errors to reject requests that don't comply with rules
- Kubebuilder automatically generates webhook server-side code and registers it with Kubernetes

### 4. **How to Test Webhooks**
You can use `kubectl` to simulate sending `AdmissionReview` requests, or directly create/update resources in the cluster and observe webhook behavior. For example:

```bash
kubectl apply -f - <<EOF
apiVersion: example.com/v1
kind: Foo
metadata:
  name: my-foo
  namespace: default
spec:
  field: ""
EOF
```

If `field` is empty, the above validation webhook will reject the request and return an error similar to `"field must not be empty"`.

### 5. **Notes**
- **Security**: Ensure webhook servers use TLS (Kubebuilder automatically generates self-signed certificates by default)
- **Performance**: Webhooks need to respond quickly to avoid blocking API Server
- **Error Handling**: Provide clear error information in responses for easy debugging
- **FailurePolicy**: Configure `failurePolicy` in webhook annotations (`Fail` or `Ignore`) to determine behavior when webhooks are unavailable

If you need more specific webhook implementations (e.g., JSON Patch generation for mutation webhooks) or examples for specific custom resources, please provide more details and I can further customize the code or data content!

---

Controllers implemented using webhooks (usually referring to Kubernetes custom controllers combined with webhook functionality) and controllers not using webhooks have significant differences in functionality, implementation methods, and usage scenarios. Below is a detailed comparison from multiple dimensions:

### 1. **Definitions and Functions**
- **Webhook Controller**:
    - Webhook is an extension mechanism provided by Kubernetes, calling external HTTP services during resource operations (CREATE, UPDATE, DELETE, etc.) through `MutatingWebhookConfiguration` or `ValidatingWebhookConfiguration`
    - Mainly used for **real-time intervention** in Kubernetes API requests, such as validating resource compliance (ValidatingWebhook) or modifying resource content (MutatingWebhook)
    - Webhook is an "interceptor" for API Server, executing before resources are persisted to etcd
    - Commonly used for validation or default value setting of custom resources (CRD)

- **Non-Webhook Controller**:
    - Usually refers to Kubernetes controllers implemented through `controller-runtime` or other frameworks, based on event-driven **reconciliation loops (Reconcile Loop)**
    - Processes logic by listening to API object changes (using Informer/Watch mechanism) and triggering `Reconcile` functions after events occur, reconciling actual state to desired state
    - More suitable for handling resources that need continuous monitoring and management, such as deploying Pods, updating status fields, etc.

### 2. **Execution Timing**
- **Webhook Controller**:
    - **Synchronous Execution**: Called during Kubernetes API request lifecycle (resource creation, updates, etc.), part of request processing
    - Directly affects API request results (e.g., rejects creation, modifies resource content)
    - Executes before resources are persisted to etcd, requires fast response

- **Non-Webhook Controller**:
    - **Asynchronous Execution**: Listens to resource changes through event queues (Informer) and triggers `Reconcile` function for processing
    - Usually runs after resources are persisted to etcd, doesn't directly intervene in API requests
    - Suitable for handling operations that require longer time, such as creating sub-resources, calling external services, etc.

### 3. **Functional Differences**
- **Webhook Controller**:
    - **Validation (ValidatingWebhook)**: Checks if resources comply with rules, e.g., ensuring certain fields are not empty. Returns `allowed: false` to block operations
    - **Mutation (MutatingWebhook)**: Modifies resource content, e.g., setting default values, adding labels, returns JSON Patch
    - **Centralized Intervention**: Suitable for scenarios requiring enforcement of rules during resource creation or updates
    - **Stateless Logic**: Webhooks usually only process snapshots of current request resources, don't maintain state

- **Non-Webhook Controller**:
    - **State Reconciliation**: Compares resource desired state (Spec) and actual state (Status), executes operations to eliminate differences, e.g., Deployment controller creates or deletes Pods based on replica count
    - **Complex Logic**: Can handle multi-resource coordination, external system interaction, status updates, etc.
    - **Stateful Logic**: Controllers usually track resource state through caches (Informer) or other mechanisms, suitable for scenarios requiring historical information or context
    - **Event-Driven**: Responds to resource changes, suitable for long-running business logic

### 4. **Implementation Methods**
- **Webhook Controller** (Kubebuilder example):
    - Define webhook paths, operations, etc. through `+kubebuilder:webhook` annotations
    - Implement validation or mutation logic in `ValidateCreate`, `ValidateUpdate`, `Default` methods
    - Need to deploy webhook server (usually HTTPS server) and configure TLS certificates
    - Example code (validation webhook):
      ```go
      func (r *Foo) ValidateCreate() (admission.Warnings, error) {
          if r.Spec.Field == "" {
              return nil, apierrors.NewInvalid(
                  r.GroupVersionKind().GroupKind(),
                  r.Name,
                  field.ErrorList{
                      field.Invalid(field.NewPath("spec").Child("field"), r.Spec.Field, "field must not be empty"),
                  })
          }
          return nil, nil
      }
      ```

- **Non-Webhook Controller** (Kubebuilder example):
    - Implement `Reconcile` function to handle resource reconciliation logic
    - Use Informer to listen to resource changes and trigger `Reconcile` calls
    - No need for additional HTTPS server, just run controller process
    - Example code (Reconcile logic):
      ```go
      func (r *FooReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
          foo := &examplev1.Foo{}
          if err := r.Get(ctx, req.NamespacedName, foo); err != nil {
              return ctrl.Result{}, client.IgnoreNotFound(err)
          }
          if foo.Spec.Field == "" {
              foo.Status.Error = "Field is empty"
              return ctrl.Result{}, r.Status().Update(ctx, foo)
          }
          foo.Status.Error = ""
          return ctrl.Result{}, r.Status().Update(ctx, foo)
      }
      ```

### 5. **Usage Scenarios**
- **Webhook Controller**:
    - **Mandatory Validation**: Ensure resources meet specific rules, e.g., CRD field constraints (required fields, value ranges, etc.)
    - **Default Value Setting**: Automatically set default values for resources, e.g., add specific labels to Pods
    - **Cross-Resource Constraints**: Validate dependencies between resources (e.g., ensure referenced ConfigMap exists)
    - **Quick Intervention**: Need to immediately block operations that don't comply with rules
    - Examples: Istio's webhook validates Sidecar configuration, Kubebuilder-generated CRD default webhooks

- **Non-Webhook Controller**:
    - **Resource Management**: Manage resource lifecycle, e.g., create sub-resources (Pods, Services), clean up unused resources
    - **State Synchronization**: Synchronize external system state to Kubernetes (e.g., update CR's Status field)
    - **Complex Workflows**: Need to coordinate multiple resources or execute multi-step operations
    - Examples: Deployment controller manages ReplicaSet and Pod, Operator manages database instances

### 6. **Pros and Cons**
- **Webhook Controller**:
    - **Pros**:
        - Real-time, directly intervenes in API requests
        - Suitable for simple validation or mutation logic, lightweight code implementation
        - Tightly integrated with Kubernetes API, suitable for extending CRD functionality
    - **Cons**:
        - High performance requirements, latency affects API requests
        - Need to deploy HTTPS server, TLS configuration adds complexity
        - Not suitable for complex logic or long-running tasks
        - If webhook is unavailable (depending on `failurePolicy`), may cause API request failures or bypass validation

- **Non-Webhook Controller**:
    - **Pros**:
        - Suitable for complex logic and asynchronous processing, doesn't block API requests
        - No HTTPS server or additional webhook configuration needed, simpler deployment
        - Through event retry mechanism, stronger fault tolerance
        - Suitable for scenarios requiring state tracking or multi-resource coordination
    - **Cons**:
        - Asynchronous processing, cannot prevent non-compliant resources from being persisted (can only correct afterwards)
        - Implementing complex logic may require more code and state management
        - Dependent on Informer cache and event queues, debugging may be more complex

### 7. **Deployment and Operations**
- **Webhook Controller**:
    - Need to deploy webhook server, usually running as Pod in Kubernetes cluster
    - Must configure TLS certificates (Kubebuilder can automatically generate self-signed certificates)
    - Need to register `MutatingWebhookConfiguration` or `ValidatingWebhookConfiguration` with API Server
    - If service is unavailable, may cause API request failures (depending on `failurePolicy=Fail` or `Ignore`)

- **Non-Webhook Controller**:
    - Only need to deploy controller process, usually running as Deployment
    - No TLS or additional webhook configuration needed, relies on Kubernetes Client library to communicate with API Server
    - If controller is unavailable, events will queue and continue processing after recovery, minimal impact

### 8. **Typical Implementation in Kubebuilder**
- **Webhook Controller**:
    - Kubebuilder generates webhook framework code through `kubebuilder create webhook` command
    - Automatically generates webhook server-side code and Kubernetes configuration files
    - Implement validation or mutation logic in `api/v1/<kind>_webhook.go`

- **Non-Webhook Controller**:
    - Kubebuilder generates controller framework code through `kubebuilder create api` command
    - Implement `Reconcile` logic in `controllers/<kind>_controller.go`
    - Automatically configures Informer and event handling

### 9. **Practical Case Comparison**
- **Scenario**: Manage a custom resource `Foo`, requiring `spec.field` to be non-empty
    - **Webhook Implementation** (ValidatingWebhook):
        - During resource creation/updates, check `spec.field`, if empty, directly reject request (return `allowed: false`)
        - Users receive errors like `spec.field must not be empty`, resources won't be persisted
    - **Non-Webhook Implementation** (Controller):
        - Listen to `Foo` resource changes, check `spec.field` in `Reconcile`
        - If empty, update `status.error` field to record error or attempt repair (e.g., trigger other operations)
        - Resources will be persisted, but controller handles problems asynchronously

### 10. **Summary**
| Feature                | Webhook Controller                          | Non-Webhook Controller                     |
|---------------------|---------------------------------------|-------------------------------------|
| **Execution Timing**        | Synchronous, during API request processing                | Asynchronous, after resource changes                    |
| **Main Function**        | Validate resources, modify resources                    | Reconcile state, manage resource lifecycle          |
| **Real-time**          | High, directly intervenes in API requests                 | Low, asynchronous processing                        |
| **Complex Logic**        | Not suitable, requires fast response                    | Suitable, can handle complex workflows              |
| **Deployment Requirements**        | HTTPS server, TLS certificates                | Only controller process needed                      |
| **Fault Tolerance**          | Depends on `failurePolicy`, may affect API     | Event retry, strong fault tolerance                  |
| **Typical Scenarios**        | CRD validation, default value setting                  | Operator, resource management, state synchronization        |

### 11. **Selection Recommendations**
- If you need **real-time validation or modification of resources** (e.g., mandatory field constraints, setting default values), choose webhook controllers
- If you need **asynchronous management of resource states** or **complex business logic** (e.g., creating sub-resources, external system synchronization), choose non-webhook controllers
- In actual projects, **both can be combined**:
    - Use webhooks to ensure basic validation and default values during resource creation
    - Use controllers to handle subsequent management, status updates, or complex coordination of resources

If you need analysis of specific custom resources or scenarios, or want to design implementation plans for both approaches, please provide more details and I can help you design implementation plans or code examples!

---

Non-webhook Kubernetes controllers (usually based on `controller-runtime` or Kubebuilder implementation) **do not use HTTPS servers** and **have no callback interfaces**, which is fundamentally different from webhook controllers. Below is a detailed explanation and comparison of both, explaining the operation mechanism of non-webhook controllers and their relationship with HTTPS servers and callback interfaces.

### 1. **Operation Mechanism of Non-Webhook Controllers**
- **Event-Driven Reconciliation Loop**:
    - Non-webhook controllers use Kubernetes' Informer (usually provided by `controller-runtime`) to listen to changes in specific resources (e.g., Pods, Deployments, or custom resources)
    - Informer establishes long connections with API Server through **Watch mechanism**, subscribing to resource events (`ADDED`, `MODIFIED`, `DELETED`)
    - When API Server detects resource changes, it pushes events to the controller's Informer through Watch channels
    - Informer caches events locally and puts resource keys (e.g., `namespace/name`) that need processing into work queues, triggering the controller's `Reconcile` function

- **Communication Direction**:
    - **Controller → API Server**: Controller actively initiates communication with API Server, including:
        - **List Operations**: During initial synchronization, gets complete list of resources
        - **Watch Operations**: Establishes long connections to subscribe to resource changes
        - **Get/Update Operations**: In `Reconcile`, queries or updates resources
    - API Server pushes events to controller, but this is implemented through Watch channels, not HTTP callbacks

### 2. **When Does Communication Occur?**
Communication between non-webhook controllers and API Server mainly happens in the following stages:

#### (1) **Controller Startup: Initial Synchronization**
- **Timing**:
    - When controller process starts (e.g., Kubebuilder's `main.go` runs), Informer initializes and communicates with API Server
- **Communication Content**:
    - **List Request**: Informer sends HTTP GET request to API Server to get complete list of monitored resources
    - **Watch Request**: After List completes, Informer initiates Watch request to establish long connection with API Server, subscribing to subsequent resource changes
- **Communication Direction**:
    - Controller → API Server: Sends List and Watch requests
    - API Server → Controller: Returns resource list and Watch event stream
- **Example**:
    - When controller starts, Informer gets all `example.com/v1` group `Foo` resources, caches locally, and starts Watch
    - HTTP request example (pseudo-code):
      ```
      GET /apis/example.com/v1/foos
      GET /apis/example.com/v1/foos?watch=true
      ```

#### (2) **Resource Changes: Watch Event Triggering**
- **Timing**:
    - When resources in the cluster change (e.g., create, update, delete `Foo` resources), API Server pushes events through Watch channels
    - Event types include:
        - `ADDED`: Resource created
        - `MODIFIED`: Resource updated (Spec, Metadata, or Status)
        - `DELETED`: Resource deleted
- **Communication Content**:
    - API Server pushes events to controller's Informer (through established Watch connection)
    - Informer updates local cache and puts resource keys (e.g., `default/my-foo`) into work queue
    - Work queue triggers `Reconcile` function to process events
- **Communication Direction**:
    - API Server → Controller: Pushes Watch events
    - Controller → API Server: In `Reconcile`, may initiate Get/Update requests to get latest resource state or update resources
- **Example**:
    - User runs `kubectl apply -f foo.yaml` to create `Foo` resource
    - API Server pushes `ADDED` event to controller's Informer
    - Controller processes in `Reconcile`:
      ```go
      func (r *FooReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
          foo := &examplev1.Foo{}
          if err := r.Get(ctx, req.NamespacedName, foo); err != nil {
              return ctrl.Result{}, client.IgnoreNotFound(err)
          }
          // Process logic, e.g., update Status
          foo.Status.State = "Processed"
          return ctrl.Result{}, r.Status().Update(ctx, foo)
      }
      ```

#### (3) **Reconcile Execution: Active Query or Update**
- **Timing**:
    - When `Reconcile` function is triggered by work queue, controller may need to communicate with API Server to:
        - **Query Resource Status**: Get latest Spec or Status through `Get`
        - **Update Resources**: Modify Spec, Status, or Metadata through `Update` or `Patch`
        - **Create/Delete Sub-resources**: E.g., create Pods or clean up unused resources
- **Communication Content**:
    - **Get Request**: Get specific resources (e.g., `GET /apis/example.com/v1/namespaces/default/foos/my-foo`)
    - **Update/Patch Request**: Update resources (e.g., `PUT /apis/example.com/v1/namespaces/default/foos/my-foo`)
    - **List Request**: Query related resources (e.g., list all related Pods)
- **Communication Direction**:
    - Controller → API Server: Sends Get/Update/Patch requests
    - API Server → Controller: Returns resource data or update confirmation
- **Example**:
    - In `Reconcile`, check `Foo`'s `spec.field`, if empty, update `status.error`:
      ```go
      if foo.Spec.Field == "" {
          foo.Status.Error = "Field is empty"
          return ctrl.Result{}, r.Status().Update(ctx, foo) // Send Update request
      }
      ```

#### (4) **Periodic Resynchronization (Resync)**
- **Timing**:
    - Informer usually configures periodic resynchronization cycles (e.g., Kubebuilder default 10 hours)
    - Even without resource changes, Informer will relist resources and trigger `Reconcile` to ensure no events are missed (e.g., network interruption causing event loss)
- **Communication Content**:
    - Similar to initial synchronization, sends List request to get resource list
    - Compares with local cache, updates cache and triggers necessary `Reconcile`
- **Communication Direction**:
    - Controller → API Server: Sends List request
    - API Server → Controller: Returns resource list
- **Example**:
    - Every 10 hours, Informer re-gets all `Foo` resources, triggers `Reconcile` to check status

### 3. **Summary of Communication Trigger Timing**
Communication between non-webhook controllers and API Server occurs at these specific times:
1. **Controller Startup**:
    - List Request: Gets initial resource list
    - Watch Request: Subscribes to resource changes
2. **Resource Changes**:
    - API Server pushes `ADDED`, `MODIFIED`, `DELETED` events
    - Triggers `Reconcile`, may cause Get/Update requests
3. **Reconcile Execution**:
    - Controller actively initiates Get/Update/Patch requests to query or modify resources
4. **Periodic Resynchronization**:
    - Every certain period (default 10 hours) relists resources, triggers `Reconcile`

### 4. **Communication Frequency and Optimization**
- **Frequency**:
    - **List**: Only occurs at startup or Resync, low frequency
    - **Watch**: Establishes one long connection, continuously receives events, more events when resources change frequently
    - **Get/Update**: Depends on `Reconcile` trigger frequency and logic, may be higher
- **Optimization**:
    - Informer uses local cache to reduce Get requests to API Server
    - `controller-runtime` provides Delta Informer, only processes changed parts, reducing overhead
    - Reasonably set Resync cycle to avoid unnecessary List requests
    - In `Reconcile`, avoid frequent resource updates (e.g., use conditional checks to reduce Update calls)

### 5. **Comparison with Webhook Controllers**
- **Non-Webhook Controller**:
    - **Communication Timing**: At startup (List/Watch), when resources change (Watch events), during Reconcile execution (Get/Update), periodic Resync
    - **Communication Direction**: Controller actively initiates (List/Get/Update) or receives events through Watch
    - **No Callback**: Doesn't provide HTTP endpoints, API Server doesn't actively call controller
    - Example: Controller watches `Foo` resources, processes `ADDED` events, updates `status.state`

- **Webhook Controller**:
    - **Communication Timing**: When API Server performs resource operations (CREATE/UPDATE/DELETE), calls webhook's HTTPS endpoints through HTTP POST
    - **Communication Direction**: API Server → Controller (HTTP request)
    - **Has Callback**: Controller exposes HTTPS endpoints, receives `AdmissionReview` requests
    - Example: When API Server creates `Foo`, calls `/validate`, webhook checks `spec.field`

### 6. **Code Example: Communication Triggering Reconcile**
Below is a Kubebuilder controller's `Reconcile` function showing communication timing:
```go
package controllers

import (
    "context"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    examplev1 "my.api.group/v1"
)

type FooReconciler struct {
    client.Client
}

func (r *FooReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. Communication: Get request to get Foo resource
    foo := &examplev1.Foo{}
    if err := r.Get(ctx, req.NamespacedName, foo); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 2. Logic processing
    if foo.Spec.Field == "" {
        foo.Status.Error = "Field is empty"
    } else {
        foo.Status.Error = ""
    }

    // 3. Communication: Update request to update Status
    if err := r.Status().Update(ctx, foo); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}

func (r *FooReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&examplev1.Foo{}). // Watch Foo resources
        Complete(r)
}
```

- **Communication Timing**:
    - **At Startup**: Informer watches `Foo` resources, triggers List/Watch requests
    - **When Resources Change**: Users create/update `Foo`, Informer receives `ADDED`/`MODIFIED` events, triggers `Reconcile`
    - **In Reconcile**: `r.Get` sends GET request, `r.Status().Update` sends PATCH request

### 7. **Notes**
- **Performance**: Frequent Get/Update requests may increase API Server load, recommend using Informer cache to reduce requests
- **Network Interruption**: When Watch connection is disconnected, Informer will automatically reconnect and relist/watch
- **RBAC**: Controllers need correct RBAC permissions (e.g., `get`, `list`, `watch`, `update`) to communicate with API Server
- **Event Loss**: Resync mechanism ensures that even if events are lost, controllers can recover state through periodic List

### 8. **Summary**
Communication between non-webhook controllers and API Server occurs at:
- **At Startup**: List/Watch initializes resource cache and event subscriptions
- **When Resources Change**: Watch receives `ADDED`/`MODIFIED`/`DELETED` events, triggers `Reconcile`
- **During Reconcile Execution**: Get/Update/Patch queries or modifies resources
- **During Periodic Resync**: Relists resources to ensure state consistency

Communication direction is **Controller → API Server** (actively List/Get/Update) or **API Server → Controller** (pushes events through Watch). Unlike webhooks, non-webhook controllers don't run HTTPS servers or accept callback requests, but process asynchronously through event queues.

If you need more specific communication flow analysis, debugging methods, or code optimization suggestions, please provide more details and I can provide further customized answers!