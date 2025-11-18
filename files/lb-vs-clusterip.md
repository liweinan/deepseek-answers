# Essential Differences Between LoadBalancer and ClusterIP Service Types

## Main Problem Analysis

### 1. **Troubleshooting ClusterIP + externalIPs**

**Error Description**:
> "If Node-A goes down, the service is completely paralyzed, and all users will see connection timeouts"

**Actual Situation**:
This description is **incorrect**. Let me explain why:

#### **Correct Understanding**:

```yaml
# ClusterIP Service with externalIPs
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP
  externalIPs:
  - 192.168.1.100  # This IP can be any routable IP
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
```

**Key Points**:
- The IP in `externalIPs` **doesn't have to be a node IP**
- It can be **any routable IP address**
- This IP can point to **load balancers, routers, or any network device**

#### **Actual Workflow**:

1. **Network Layer**: External traffic arrives at `192.168.1.100`
2. **Routing Layer**: Network devices route traffic to **any healthy node** in the cluster
3. **Kubernetes Layer**: `kube-proxy` forwards traffic to healthy Pods

### 2. **Relationship Between LoadBalancer and External Cloud LB**

**Error Description**:
> "They are like the relationship between design blueprints and actual buildings"

**Actual Situation**:
This analogy **overly simplifies** and can be misleading.

#### **Correct Understanding**:

**Two Implementation Methods of LoadBalancer Service**:

1. **Cloud Environment**:
   ```yaml
   # In AWS/GCP/Azure
   spec:
     type: LoadBalancer
   ```
   - Indeed creates cloud LB
   - Managed by Cloud Controller Manager

2. **Bare Metal Environment**:
   ```yaml
   # In bare metal clusters
   spec:
     type: LoadBalancer
   ```
   - Uses MetalLB and other implementations
   - **Doesn't create external cloud LB**
   - Just assigns IP addresses

### 3. **Fault Transfer Description Issues**

**Partially Incorrect**:
The original conversation's description of fault handling for ClusterIP + externalIPs was overly absolute.

#### **Actual Situation**:

**Reliability of ClusterIP + externalIPs Depends on Network Configuration**:

```bash
# If externalIPs points to a highly available load balancer
externalIPs:
- 192.168.1.100  # This is an HA load balancer's IP
```

In this case:
- The load balancer can detect backend node health status
- Automatically performs fault transfer
- Provides high availability similar to cloud LB

## Correct Comparison Summary

| Feature | LoadBalancer | ClusterIP + externalIPs |
|------|-------------|------------------------|
| **IP Assignment** | Automatic (Cloud/MetalLB) | Manual specification |
| **External Resources** | May create (cloud environment) | Doesn't create |
| **High Availability** | Depends on implementation | Depends on network configuration |
| **Management Complexity** | Low (declarative) | High (requires network configuration) |
| **Cost** | May have fees (cloud LB) | No additional cost |

## Practical Recommendations

### **Scenarios for Using LoadBalancer**:
- Cloud environments (AWS/GCP/Azure)
- Bare metal environments with MetalLB
- Want simplified management

### **Scenarios for Using ClusterIP + externalIPs**:
- Already have highly available network infrastructure
- Need precise control over IP addresses
- Cost-sensitive environments

## Conclusion

The main issues in the original conversation were:
1. **Over-simplification** of how ClusterIP + externalIPs works
2. **Incorrect assumption** that externalIPs must be node IPs
3. **Ignored** the possibility of high-availability network layer configurations

In fact, both methods can provide high availability under **proper configuration**, with differences mainly in **management complexity and automation level**.

---

Great question! There are indeed many practical cases of using LoadBalancer outside of Ingress Controller. Let me analyze these scenarios in detail.

## LoadBalancer Use Cases Beyond Ingress Controller

### 1. **Database Service Exposure**

#### **Scenario**: Exposing database services to external applications
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-external
spec:
  type: LoadBalancer
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
    protocol: TCP
```

**Use Cases**:
- External applications need direct database connection
- Data analysis tools need database access
- Cross-cluster database access

### 2. **Message Queue Services**

#### **Scenario**: RabbitMQ, Kafka and other message queues
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq-management
spec:
  type: LoadBalancer
  selector:
    app: rabbitmq
  ports:
  - name: management
    port: 15672
    targetPort: 15672
  - name: amqp
    port: 5672
    targetPort: 5672
```

**Use Cases**:
- External systems need to send messages to queues
- Management interface needs external access
- Cross-cluster message passing

### 3. **Monitoring and Logging Services**

#### **Scenario**: Prometheus, Grafana, ELK Stack
```yaml
# Prometheus
apiVersion: v1
kind: Service
metadata:
  name: prometheus-server
spec:
  type: LoadBalancer
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090

---
# Grafana
apiVersion: v1
kind: Service
metadata:
  name: grafana
spec:
  type: LoadBalancer
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
```

**Use Cases**:
- Operations team needs access to monitoring dashboards
- External systems need to push monitoring data
- Cross-environment monitoring data collection

### 4. **API Gateway Services**

#### **Scenario**: Kong, Zuul, API Gateway
```yaml
apiVersion: v1
kind: Service
metadata:
  name: kong-gateway
spec:
  type: LoadBalancer
  selector:
    app: kong
  ports:
  - name: proxy
    port: 8000
    targetPort: 8000
  - name: admin
    port: 8001
    targetPort: 8001
```

**Use Cases**:
- Microservices architecture API gateway
- External systems calling internal APIs
- API management and rate limiting

### 5. **File Storage Services**

#### **Scenario**: MinIO, NFS, Object Storage
```yaml
apiVersion: v1
kind: Service
metadata:
  name: minio
spec:
  type: LoadBalancer
  selector:
    app: minio
  ports:
  - name: api
    port: 9000
    targetPort: 9000
  - name: console
    port: 9001
    targetPort: 9001
```

**Use Cases**:
- External applications need file storage
- Cross-cluster file sharing
- Backup and recovery services

### 6. **Game Servers**

#### **Scenario**: Game backend services
```yaml
apiVersion: v1
kind: Service
metadata:
  name: game-server
spec:
  type: LoadBalancer
  selector:
    app: game-server
  ports:
  - name: tcp
    port: 7777
    targetPort: 7777
    protocol: TCP
  - name: udp
    port: 7777
    targetPort: 7777
    protocol: UDP
```

**Use Cases**:
- Game clients connect directly
- Real-time game communication
- Low latency requirements

### 7. **Blockchain Nodes**

#### **Scenario**: Ethereum, Bitcoin nodes
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ethereum-node
spec:
  type: LoadBalancer
  selector:
    app: ethereum
  ports:
  - name: rpc
    port: 8545
    targetPort: 8545
  - name: p2p
    port: 30303
    targetPort: 30303
```

**Use Cases**:
- External wallet connections
- Blockchain browsers
- Cross-node communication

## Actual Configuration Examples

Let me create a complete example to demonstrate these scenarios:

## More Practical Use Cases

### 8. **CI/CD Services**

#### **Scenario**: Jenkins, GitLab Runner
```yaml
apiVersion: v1
kind: Service
metadata:
  name: jenkins
spec:
  type: LoadBalancer
  selector:
    app: jenkins
  ports:
  - port: 8080
    targetPort: 8080
```

**Use Cases**:
- Development team accesses CI/CD interface
- External systems trigger builds
- Webhook reception

### 9. **Cache Services**

#### **Scenario**: Redis, Memcached
```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-external
spec:
  type: LoadBalancer
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

**Use Cases**:
- External applications use cache
- Cross-cluster cache sharing
- Data analysis tool access

### 10. **Blockchain Services**

#### **Scenario**: Ethereum nodes, IPFS
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ethereum-node
spec:
  type: LoadBalancer
  selector:
    app: ethereum
  ports:
  - name: rpc
    port: 8545
    targetPort: 8545
  - name: p2p
    port: 30303
    targetPort: 30303
```

## Reasons to Choose LoadBalancer Over Ingress

### **1. Protocol Support**
- **LoadBalancer**: Supports TCP, UDP, WebSocket
- **Ingress**: Mainly supports HTTP/HTTPS

### **2. Port Flexibility**
- **LoadBalancer**: Can expose any port
- **Ingress**: Usually only uses 80/443 ports

### **3. Direct Access**
- **LoadBalancer**: External systems access directly
- **Ingress**: Needs to go through domain name and path routing

### **4. Performance Considerations**
- **LoadBalancer**: Fewer network hops
- **Ingress**: Additional routing processing

## Best Practice Recommendations

### **Scenarios for Using LoadBalancer**:
1. **Non-HTTP Protocols**: Databases, message queues, caches
2. **Management Tools**: Monitoring, logging, CI/CD
3. **API Gateways**: Microservices architecture
4. **Game Servers**: Low latency requirements
5. **Blockchain Nodes**: P2P communication

### **Scenarios for Using Ingress**:
1. **Web Applications**: HTTP/HTTPS services
2. **Multi-Service Routing**: Based on domain names and paths
3. **SSL Termination**: Centralized certificate management
4. **Cost Optimization**: One IP serving multiple applications

## Summary

Beyond Ingress Controller, LoadBalancer has very rich use cases, mainly applicable to:

1. **Non-Web Services**: Databases, message queues, caches, etc.
2. **Management Tools**: Monitoring, logging, CI/CD, etc.
3. **Special Protocols**: TCP, UDP, WebSocket, etc.
4. **Direct Access**: External systems connect directly
5. **Performance Sensitive**: Low latency requirement services

In these scenarios, LoadBalancer provides more direct and flexible access than Ingress.

---

You raised a very precise question! Indeed, from the perspective of **client accessing database**, the effects of LoadBalancer and ClusterIP + externalIPs are almost identical. Let me analyze the **real advantages** of LoadBalancer in database scenarios.

## Actual Differences in Database Scenarios

### 1. **Automatic Fault Detection and Transfer**

#### **LoadBalancer Advantages**:
```yaml
# Cloud environment LoadBalancer
apiVersion: v1
kind: Service
metadata:
  name: mysql-lb
spec:
  type: LoadBalancer
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
```

**When database nodes fail**:
- **Cloud LB automatic detection**: Health checks discover failed nodes through health checks
- **Automatic removal of failed nodes**: Remove from backend pool
- **Automatic traffic rerouting**: Send traffic to healthy nodes
- **No manual intervention required**: Entire process is automated

#### **ClusterIP + externalIPs Limitations**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-cip
spec:
  type: ClusterIP
  externalIPs:
  - 192.168.1.100  # Points to specific node
```

**When that node fails**:
- **Requires manual configuration**: Network routing needs manual adjustment
- **Single point of failure**: If externalIPs points to failed node, service is interrupted
- **Complex recovery**: Manual network configuration updates are needed

### 2. **Intelligent Load Balancing**

#### **LoadBalancer Intelligent Load Balancing**:
```yaml
spec:
  type: LoadBalancer
  sessionAffinity: ClientIP  # Session affinity
  ports:
  - port: 3306
    targetPort: 3306
```

**Advantages**:
- **Session persistence**: Same client always connects to same database instance
- **Connection pool optimization**: Reduces database connection overhead
- **Read-write separation support**: Can configure different backend pools

#### **ClusterIP Simple Round Robin**:
- **Basic round robin**: Simple round-robin distribution
- **No session awareness**: May cause frequent connection switching
- **Database connection overhead**: Frequent establishment/disconnection of connections

### 3. **Monitoring and Observability**

#### **LoadBalancer Monitoring Advantages**:
```yaml
# Cloud LB provides monitoring metrics
- Connection count
- Response time
- Error rate
- Health check status
- Traffic distribution
```

**Actual Value**:
- **Real-time monitoring**: Real-time visibility of database connection status
- **Alert mechanism**: Automatic alerts for abnormal situations
- **Performance analysis**: Connection patterns and performance trends
- **Capacity planning**: Scaling based on actual usage

### 4. **Security and Access Control**

#### **LoadBalancer Security Features**:
```yaml
# Cloud LB security features
- IP whitelisting
- SSL/TLS termination
- DDoS protection
- Access logs
- Geographic restrictions
```

**Value in Database Scenarios**:
- **IP restrictions**: Only allow specific IPs to access database
- **Access auditing**: Record all database access
- **Encrypted transmission**: SSL encryption for database connections
- **Attack protection**: Automatic protection against malicious connections

### 5. **Cost-Benefit Analysis**

#### **LoadBalancer Costs**:
- **Cloud LB fees**: Usually charged by connection count or traffic
- **Automation benefits**: Reduced operational costs
- **High availability value**: Avoid losses from service interruptions

#### **ClusterIP + externalIPs Costs**:
- **No additional fees**: Kubernetes itself doesn't charge
- **Operational costs**: Manual network management required
- **Failure costs**: Potential losses from service interruptions

## Real-World Scenario Comparison

### **Scenario 1: Single Node Failure**

#### **LoadBalancer Performance**:
```
1. Node A fails
2. Cloud LB health check fails (within 5 seconds)
3. Automatically removes Node A from backend pool
4. Traffic automatically routes to Nodes B and C
5. Client connections are almost unaffected
```

#### **ClusterIP + externalIPs Performance**:
```
1. Node A fails (assuming externalIPs points to Node A)
2. All external connections fail
3. Manual network configuration update required
4. Service interruption until manual fix
```

### **Scenario 2: Database Scaling**

#### **LoadBalancer Performance**:
```
1. Add new database node
2. Cloud LB automatically discovers new node
3. Automatically adds to load balancing pool
4. No additional configuration needed
```

#### **ClusterIP + externalIPs Performance**:
```
1. Add new database node
2. Manual network configuration update required
3. May need to reconfigure externalIPs
4. Testing and validation required
```

## Summary

Although from the **client database access** perspective, LoadBalancer and ClusterIP + externalIPs have similar effects, LoadBalancer's **real value** in database scenarios lies in:

1. **Automated Operations**: Fault detection, transfer, and recovery are fully automated
2. **Intelligent Load Balancing**: Session persistence, connection optimization
3. **Enterprise Monitoring**: Real-time monitoring, alerts, and analysis
4. **Security Protection**: Access control, encryption, and auditing
5. **Operational Efficiency**: Reduced manual intervention, improved reliability

**Recommendations**:
- **Production Environment**: Use LoadBalancer for enterprise-grade reliability
- **Development/Test Environment**: Can use ClusterIP + externalIPs to reduce costs
- **Hybrid Solution**: Use LoadBalancer for primary database, ClusterIP for secondary databases

This is why LoadBalancer is the preferred solution for production database deployments.

---

You asked very well! Indeed, **without using LoadBalancer type Service, cloud provider's monitoring and LB components can still achieve high availability**. Let me analyze this important concept in detail.

## Independence of Cloud Provider Load Balancers

### 1. **Cloud Load Balancers Can Exist Independently of Kubernetes**

#### **Traditional Architecture Example**:
```
Internet → Cloud Load Balancer (AWS ALB/NLB) → Multiple Backend Servers → Database
```

**Key Points**:
- Cloud load balancers are **independent infrastructure resources**
- They don't depend on Kubernetes Service types
- Can directly point to physical servers, virtual machines, or containers

#### **Actual Configuration Example**:
```yaml
# Solution without using LoadBalancer Service for high availability
apiVersion: v1
kind: Service
metadata:
  name: mysql-clusterip
spec:
  type: ClusterIP  # Only uses ClusterIP
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
```

**External Configuration**:
```bash
# Configure load balancer through cloud console or API
# Backend targets: all nodes in the cluster or direct IPs
aws elbv2 create-target-group \
  --name mysql-targets \
  --protocol TCP \
  --port 3306 \
  --vpc-id vpc-12345

# Add backend targets
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=10.0.1.100,Port=33066 Id=10.0.1.101,Port=33066 Id=10.0.1.102,Port=33066
```

### 2. **Multiple High Availability Implementation Methods**

#### **Method 1: NodePort + Cloud Load Balancer**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-nodeport
spec:
  type: NodePort
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
    nodePort: 33066  # Fixed NodePort
```

**Cloud Load Balancer Configuration**:
- Backend targets: all nodes' `IP:33066`
- Health checks: TCP 33066 port
- Automatic fault transfer: automatically removes when nodes fail

#### **Method 2: ClusterIP + Cloud Load Balancer + Network Configuration**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-clusterip
spec:
  type: ClusterIP
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
```

**Network Layer Configuration**:
```bash
# Use cloud network features (like AWS VPC, GCP VPC)
# Configure routing tables to route traffic to multiple nodes
# Use health check features of cloud load balancers
```

#### **Method 3: Direct Pod IP + Cloud Load Balancer**:
```yaml
# Use Headless Service to get Pod IPs
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
```

**Dynamic Configuration**:
```bash
# Script regularly gets Pod IPs and updates cloud load balancer backends
kubectl get pods -l app=mysql -o jsonpath='{.items[*].status.podIP}'
# Output: 10.244.1.5 10.244.2.3 10.244.3.7

# Update cloud load balancer backend targets
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=10.244.1.5,Port=3306 Id=10.244.2.3,Port=3306 Id=10.244.3.7,Port=3306
```

### 3. **High Availability Features of Cloud Load Balancers (Independent of Kubernetes)**

#### **AWS Application Load Balancer (ALB) Features**:
```json
{
  "HealthCheck": {
    "Target": "TCP:3306",
    "Interval": 30,
    "Timeout": 5,
    "HealthyThreshold": 2,
    "UnhealthyThreshold": 3
  },
  "TargetGroupAttributes": [
    {
      "Key": "deregistration_delay.timeout_seconds",
      "Value": "30"
    }
  ]
}
```

**High Availability Features**:
- **Automatic health checks**: Regularly check backend health status
- **Automatic fault transfer**: Remove unhealthy backends
- **Cross-availability zone deployment**: Automatically distributed across multiple AZs
- **Connection draining**: Gracefully handle connection closure

#### **GCP Load Balancer Features**:
```yaml
# GCP backend service configuration
backendService:
  name: mysql-backend
  protocol: TCP
  healthChecks:
  - tcp:3306
  backends:
  - group: "zones/us-central1-a/instanceGroups/mysql-nodes"
    balancingMode: CONNECTION
  connectionDraining:
    drainingTimeoutSec: 30
```

### 4. **Actual Comparative Analysis**

#### **LoadBalancer Service Advantages**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-lb
spec:
  type: LoadBalancer  # Automatic integration
```

**Advantages**:
- **Declarative configuration**: Defined in YAML, automatically creates cloud load balancer
- **Automatic synchronization**: Pod changes automatically update backends
- **Unified management**: Managed through kubectl
- **Simplified operations**: Reduces manual configuration work

#### **Manual Cloud Load Balancer Configuration Advantages**:
```bash
# Manual cloud load balancer configuration
aws elbv2 create-load-balancer \
  --name mysql-lb \
  --subnets subnet-12345 subnet-67890 \
  --scheme internet-facing \
  --type network
```

**Advantages**:
- **Precise control**: Full control over load balancer configuration
- **Cost optimization**: Can choose cheaper load balancer types
- **Multi-cluster sharing**: One load balancer serving multiple clusters
- **Custom configuration**: Advanced features and optimization

### 5. **Hybrid Architecture Example**

#### **Production Environment Common Architecture**:
```
Internet → Cloud Load Balancer (AWS ALB) → Multiple Kubernetes Clusters
                                    ↓
                            ClusterIP Service → Pod
```

**Configuration Example**:
```yaml
# Cluster A
apiVersion: v1
kind: Service
metadata:
  name: mysql-cluster-a
spec:
  type: ClusterIP
  selector:
    app: mysql
    cluster: a
  ports:
  - port: 3306
    targetPort: 3306

---
# Cluster B  
apiVersion: v1
kind: Service
metadata:
  name: mysql-cluster-b
spec:
  type: ClusterIP
  selector:
    app: mysql
    cluster: b
  ports:
  - port: 3306
    targetPort: 3306
```

**Cloud Load Balancer Configuration**:
```bash
# Backend targets include nodes from both clusters
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets \
    Id=10.0.1.100,Port=33066 \
    Id=10.0.1.101,Port=33066 \
    Id=10.0.2.100,Port=33066 \
    Id=10.0.2.101,Port=33066
```

## Summary

Your understanding is **completely correct**:

### **Cloud Load Balancer's High Availability Capability is Independent**:
1. **Doesn't depend on Kubernetes Service type**
2. **Can be independently configured and managed**
3. **Provides the same high availability features**

### **The Real Value of LoadBalancer Service**:
1. **Automated integration**: Automatically creates and configures cloud load balancers
2. **Declarative management**: Managed through YAML
3. **Dynamic synchronization**: Pod changes automatically update
4. **Simplified operations**: Reduces manual configuration work

### **Selection Recommendations**:
- **Simple scenarios**: Use LoadBalancer Service
- **Complex requirements**: Manually configure cloud load balancer + ClusterIP
- **Multi-cluster**: Manually configure cloud load balancer to serve multiple clusters
- **Cost-sensitive**: Manually configure cheaper load balancer types

**Key insight**: LoadBalancer Service is not the **only way** to achieve high availability, but the **convenient way** to achieve high availability. Cloud load balancer's high availability capability is at the infrastructure level, unrelated to Kubernetes Service type.

---

You asked very well! Let me explain the value of LoadBalancer Service with specific examples.

## 1. Automated Integration: Automatically Create and Configure Cloud Load Balancers

### **Manual vs Automated Comparison**

#### **Manual Method (Complex and Error-Prone)**:
```bash
# Step 1: Manually create cloud load balancer
aws elbv2 create-load-balancer \
  --name mysql-lb \
  --subnets subnet-12345 subnet-67890 \
  --scheme internet-facing \
  --type network

# Step 2: Create target group
aws elbv2 create-target-group \
  --name mysql-targets \
  --protocol TCP \
  --port 3306 \
  --vpc-id vpc-12345

# Step 3: Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol TCP \
  --port 3306 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...

# Step 4: Get all node IPs
kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="ExternalIP")].address}'

# Step 5: Manually register backend targets
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=10.0.1.100,Port=33066 Id=10.0.1.101,Port=33066

# Step 6: Configure health checks
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --health-check-protocol TCP \
  --health-check-port 3306 \
  --health-check-interval-seconds 30
```

#### **LoadBalancer Service Method (One Command)**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-lb
spec:
  type: LoadBalancer
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
```

```bash
# One command completes all configuration
kubectl apply -f mysql-lb.yaml
```

**Cloud Controller Manager Automatically Executes**:
1. Detects `type: LoadBalancer`
2. Calls AWS API to create NLB
3. Automatically configures target groups and listeners
4. Automatically registers all nodes as backends
5. Automatically configures health checks
6. Writes external IP back to Service status
```