# Disconnected Cluster Creation

## Usage in Private Cluster

### 1. **Scenarios Where It Can Be Used**

#### **Private Cluster Requiring Image Synchronization**
```bash
# When private cluster needs to pre-sync images
# For example: network bandwidth limitations, security requirements, performance optimization
```

#### **Hybrid Network Environment**
```bash
# Cluster is private but needs temporary access to external resources
# For example: sync images during installation, disconnect after installation
```

### 2. **Script Universal Design**

The script itself is designed to be universal, containing multiple configuration options:

```bash
# Support custom AMI
if [[ "${BASTION_HOST_AMI}" == "" ]]; then
  # Dynamic creation
else
  # Use BYO (Bring Your Own) bastion host
  ami_id=${BASTION_HOST_AMI}
fi
```

### 3. **Specific Uses in Private Cluster**

#### **A. Image Pre-synchronization**
```bash
# Pre-sync images before private cluster installation
# Avoid network issues during installation process
MIRROR_REGISTRY_URL="${BASTION_HOST_PUBLIC_DNS}:5000"
```

#### **B. Proxy Service**
```bash
# Provide proxy access for private cluster
PROXY_PUBLIC_URL="http://${PROXY_CREDENTIAL}@${BASTION_HOST_PUBLIC_DNS}:3128"
PROXY_PRIVATE_URL="http://${PROXY_CREDENTIAL}@${BASTION_HOST_PRIVATE_DNS}:3128"
```

#### **C. Temporary External Access**
```bash
# Provide temporary external access capability during installation
# Can be removed after installation is complete
```

## Usage Differences

### **Private Cluster vs Disconnected Cluster**

| Aspect | Private Cluster | Disconnected Cluster |
|------|----------------|---------------------|
| **Necessity** | Optional | Required |
| **Usage Duration** | Temporary | Permanent |
| **Network Configuration** | May be removed after installation | Continuously used |
| **Image Synchronization** | Optional optimization | Required step |

### **Configuration Example for Private Cluster**

```yaml
# install-config.yaml for Private Cluster
publish: Internal
platform:
  aws:
    privateLink: true
# Can optionally configure mirror registry
imageContentSources:
- mirrors:
  - bastion-host:5000/openshift4/ose-kube-rbac-proxy
  source: registry.redhat.io/openshift4/ose-kube-rbac-proxy
```

## Actual Usage Scenarios

### **Scenario 1: Network-limited Private Cluster**
```bash
# Enterprise network has bandwidth limitations
# Use bastion host to pre-sync images
# Pull from local registry during installation
```

### **Scenario 2: High Security Requirements Private Cluster**
```bash
# Need to pre-validate all images
# Use bastion host as image validation point
# Ensure all images pass security scanning
```

### **Scenario 3: Performance-optimized Private Cluster**
```bash
# Avoid network latency during installation
# Pre-sync images locally
# Improve installation speed and stability
```

## Configuration Options

### **Optional Usage**
```bash
# Can control whether to use via environment variables
BASTION_HOST_AMI=""  # Don't use custom AMI
CUSTOM_PROXY_CREDENTIAL="false"  # Use default proxy configuration
```

### **Partial Function Usage**
```bash
# Only use mirror registry functionality
# Don't use proxy functionality
# Or only use proxy functionality, don't use mirror registry
```

## Summary

This script **can definitely be used for private cluster installation**, but is usually **optional** rather than required. In private clusters, it is mainly used for:

1. **Performance Optimization**: Pre-sync images
2. **Network Optimization**: Reduce network dependencies during installation
3. **Security Enhancement**: Image validation and scanning
4. **Temporary Access**: External resource access during installation process

Unlike disconnected clusters, after private cluster installation is complete, these bastion hosts and mirror registry services can usually be removed, because the cluster itself can still access the internet to pull images.

---

Let me introduce in detail the content related to disconnected cluster and mirror registry in this project.

## Project Structure and Disconnected Cluster Related Components

### 1. **AWS Infrastructure Layer (step-registry/aws/provision/)**

#### **A. VPC Configuration**
```bash
step-registry/aws/provision/vpc/disconnected/
├── aws-provision-vpc-disconnected-ref.yaml
├── aws-provision-vpc-disconnected-commands.sh
└── aws-provision-vpc-disconnected-ref.metadata.json
```
**Purpose**: Create dedicated VPC network environment for disconnected cluster

#### **B. Bastion Host Configuration**
```bash
step-registry/aws/provision/bastionhost/
├── aws-provision-bastionhost-ref.yaml
├── aws-provision-bastionhost-commands.sh
└── aws-provision-bastionhost-chain.yaml
```
**Purpose**: Create bastion host, provide mirror registry and proxy services

#### **C. CCO Static User Configuration**
```bash
step-registry/aws/provision/cco-manual-users/static/
├── aws-provision-cco-manual-users-static-ref.yaml
├── aws-provision-cco-manual-users-static-commands.sh
└── aws-provision-cco-manual-users-static-ref.metadata.json
```
**Purpose**: Create static IAM users and permissions for disconnected cluster

### 2. **Image Synchronization Layer (step-registry/mirror-images/)**

#### **A. Main Image Synchronization Tool**
```bash
step-registry/mirror-images/by-oc-mirror/
├── mirror-images-by-oc-mirror-ref.yaml
├── mirror-images-by-oc-mirror-commands.sh
└── conf-mirror/
    ├── mirror-images-by-oc-mirror-conf-mirror-ref.yaml
    └── mirror-images-by-oc-mirror-conf-mirror-commands.sh
```

**Core Functions**:
```bash
# Use oc-mirror tool to synchronize images
oc-mirror --config=imageset.yaml docker://${MIRROR_REGISTRY_HOST}

# Generate ImageContentSourcePolicy and CatalogSource
# Output to oc-mirror-workspace/results-*/
```

#### **B. Image Tag Processing**
```bash
step-registry/mirror-images/tag-images/
├── mirror-images-tag-images-ref.yaml
└── mirror-images-tag-images-commands.sh
```
**Purpose**: Process image tags to ensure correct image references in disconnected environment

### 3. **Cluster Installation Configuration Layer (step-registry/ipi/)**

#### **A. Image Configuration**
```bash
step-registry/ipi/conf/mirror/
├── ipi-conf-mirror-ref.yaml
└── ipi-conf-mirror-commands.sh
```
**Purpose**: Configure mirror registry settings in install-config.yaml

#### **B. Installation Process**
```bash
step-registry/ipi/install/install/
├── ipi-install-install-ref.yaml
└── ipi-install-install-commands.sh
```
**Purpose**: Execute OpenShift cluster installation

### 4. **Post-Installation Configuration Layer**

#### **A. Catalog Source Configuration**
```bash
step-registry/enable-qe-catalogsource/disconnected/
├── enable-qe-catalogsource-disconnected-ref.yaml
└── enable-qe-catalogsource-disconnected-commands.sh
```
**Purpose**: Configure local operator catalog for disconnected environment

#### **B. Image Registry Configuration**
```bash
step-registry/ipi/install/registry/
├── ipi-install-vsphere-registry-ref.yaml
└── ipi-install-vsphere-registry-commands.sh
```
**Purpose**: Configure internal image registry of the cluster

### 5. **Complete Installation Chain (step-registry/cucushift/)**

#### **A. Disconnected Cluster Installation Chain**
```bash
step-registry/cucushift/installer/rehearse/vsphere/ipi/disconnected/provision/
├── cucushift-installer-rehearse-vsphere-ipi-disconnected-provision-chain.yaml
└── cucushift-installer-rehearse-vsphere-ipi-disconnected-provision-workflow.yaml
```

**Installation Steps**:
```yaml
steps:
  - chain: ipi-conf-vsphere
  - ref: ipi-install-rbac
  - chain: vsphere-provision-bastionhost
  - ref: mirror-images-by-oc-adm-in-bastion
  - ref: ipi-conf-mirror
  - ref: ipi-install-install
  - ref: ipi-install-vsphere-registry
  - ref: enable-qe-catalogsource-disconnected
  - ref: mirror-images-tag-images
  - ref: set-sample-operator-disconnected
```

### 6. **Tools and Scripts**

#### **A. oc-mirror Tool Usage**
```bash
# Download and install
curl -L -o oc-mirror.tar.gz https://mirror.openshift.com/pub/openshift-v4/amd64/clients/ocp/latest/oc-mirror.tar.gz
tar -xvzf oc-mirror.tar.gz

# Image synchronization
./oc-mirror --config=imageset.yaml docker://${MIRROR_REGISTRY_HOST} --continue-on-error --skip-missing
```

#### **B. ImageSetConfiguration Configuration**
```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
mirror:
  operators:
  - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.16
    packages:
    - name: openshift-cert-manager-operator
  additionalImages:
  - name: quay.io/openshifttest/helm:3.17.0
```

### 7. **Configuration File Examples**

#### **A. install-config.yaml (disconnected)**
```yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: disconnected-cluster
publish: Internal
platform:
  aws:
    region: us-east-1
    privateLink: true
imageContentSources:
- mirrors:
  - mirror-registry.example.com:5000/openshift4/ose-kube-rbac-proxy
  source: registry.redhat.io/openshift4/ose-kube-rbac-proxy
additionalTrustBundle: |
  -----BEGIN CERTIFICATE-----
  # Mirror registry CA certificate
  -----END CERTIFICATE-----
```

#### **B. ImageContentSourcePolicy**
```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ImageContentSourcePolicy
metadata:
  name: disconnected-mirror
spec:
  repositoryDigestMirrors:
  - mirrors:
    - mirror-registry.example.com:5000/openshift4
    source: registry.redhat.io/openshift4
```

### 8. **Key Environment Variables**

```bash
# Mirror registry configuration
MIRROR_REGISTRY_HOST="bastion-host.example.com:5000"
MIRROR_REGISTRY_URL="${MIRROR_REGISTRY_HOST}"

# Proxy configuration
PROXY_PUBLIC_URL="http://user:pass@bastion-host.example.com:3128"
PROXY_PRIVATE_URL="http://user:pass@bastion-host.example.com:3128"

# CCO configuration
CREDENTIALS_MODE="Manual"
```

### 9. **Workflow Summary**

```mermaid
graph TD
    A[AWS Provision] --> B[Bastion Host]
    B --> C[Mirror Registry Setup]
    C --> D[Image Synchronization]
    D --> E[Cluster Installation]
    E --> F[Post-installation Config]
    
    A1[VPC Creation] --> A
    A2[CCO Users] --> A
    A3[Security Groups] --> A
    
    D1[oc-mirror] --> D
    D2[ImageSetConfig] --> D
    
    F1[Catalog Sources] --> F
    F2[Image Policies] --> F
```

### 10. **Project Features**

1. **Modular Design**: Each component has clear responsibilities and can be used independently
2. **Multi-platform Support**: Supports AWS, vSphere, Nutanix and other platforms
3. **Tool Integration**: Deep integration with OpenShift official tools like oc-mirror
4. **Flexible Configuration**: Supports multiple disconnected scenario configurations
5. **High Automation**: Full automation from infrastructure to application deployment

This project provides a complete solution for deploying disconnected OpenShift clusters, covering all aspects from infrastructure preparation to application deployment.

---

Yes, mirror registry is usually installed inside the bastion host. Let me explain this architecture in detail:

## Mirror Registry Deployment in Bastion Host

### 1. **Architecture Design**

```mermaid
graph TD
    A[Internet] --> B[Bastion Host]
    B --> C[Mirror Registry :5000]
    B --> D[HTTP Proxy :3128]
    B --> E[Additional Services]
    
    F[Disconnected Cluster] --> B
    G[Installation Process] --> B
    
    B --> H[S3 Storage]
    B --> I[Local Storage]
```

### 2. **Service Configuration in Bastion Host**

From `aws-provision-bastionhost-commands.sh`, we can see the bastion host is configured with multiple ports:

```yaml
# Security group configuration
- IpProtocol: tcp
  FromPort: 5000
  ToPort: 5000
  CidrIp: 0.0.0.0/0  # Mirror Registry port

- IpProtocol: tcp
  FromPort: 6001
  ToPort: 6002
  CidrIp: 0.0.0.0/0  # Additional mirror registry ports

- IpProtocol: tcp
  FromPort: 3128
  ToPort: 3128
  CidrIp: 0.0.0.0/0  # HTTP proxy port
```

### 3. **Mirror Registry URL Configuration**

```bash
# Set in bastion host script
MIRROR_REGISTRY_URL="${BASTION_HOST_PUBLIC_DNS}:5000"
echo "${MIRROR_REGISTRY_URL}" > "${SHARED_DIR}/mirror_registry_url"
```

### 4. **Actual Deployment Methods**

#### **A. Deploy via Ignition Configuration**
```bash
# Bastion host uses Ignition configuration
bastion_ignition_file="${SHARED_DIR}/${CLUSTER_NAME}-bastion.ign"

# Ignition configuration includes mirror registry installation and configuration
```

#### **B. Containerized Deployment**
```yaml
# Usually run containerized registry on bastion host
apiVersion: v1
kind: Pod
metadata:
  name: mirror-registry
spec:
  containers:
  - name: registry
    image: registry:2
    ports:
    - containerPort: 5000
    volumeMounts:
    - name: registry-storage
      mountPath: /var/lib/registry
```

### 5. **Why Choose Bastion Host**

#### **A. Network Advantages**
- **Dual Network Access**: Can access both internet (sync images) and internal network (service cluster)
- **Network Isolation**: Acts as network boundary, controlling traffic flow
- **Security Control**: Centralized management of network access policies

#### **B. Resource Management**
- **Centralized Storage**: Image storage on bastion host, shared access by cluster nodes
- **Bandwidth Optimization**: Avoid each node pulling images from external sources
- **Caching Effect**: Sync once, use multiple times

#### **C. Operational Convenience**
- **Unified Management**: Image sync, update, and maintenance all in one place
- **Centralized Monitoring**: Can monitor mirror registry status uniformly
- **Simple Backup**: Only need to backup data on bastion host

### 6. **Actual Workflow**

```bash
# 1. Bastion Host Creation
aws-provision-bastionhost-commands.sh
# Create EC2 instance, configure security groups, install mirror registry

# 2. Image Synchronization
mirror-images-by-oc-mirror-commands.sh
# Execute oc-mirror on bastion host, sync images to local registry

# 3. Cluster Installation
# Cluster pulls images from bastion host's mirror registry during installation
```

### 7. **Configuration Examples**

#### **A. Registry Configuration on Bastion Host**
```yaml
# /etc/registry/config.yml
version: 0.1
log:
  level: debug
storage:
  filesystem:
    rootdirectory: /var/lib/registry
  delete:
    enabled: true
http:
  addr: :5000
  headers:
    X-Content-Type-Options: [nosniff]
auth:
  htpasswd:
    realm: basic-realm
    path: /etc/registry/auth/htpasswd
```

#### **B. Image Configuration in Cluster**
```yaml
# ImageContentSourcePolicy
apiVersion: operator.openshift.io/v1alpha1
kind: ImageContentSourcePolicy
metadata:
  name: disconnected-mirror
spec:
  repositoryDigestMirrors:
  - mirrors:
    - bastion-host.example.com:5000/openshift4
    source: registry.redhat.io/openshift4
```

### 8. **Other Possible Deployment Methods**

Although mainly deployed on bastion host, there are other options:

#### **A. Standalone Server**
```bash
# Dedicated mirror registry server
MIRROR_REGISTRY_HOST="mirror-registry.example.com:5000"
```

#### **B. Inside Cluster**
```bash
# Deploy registry inside cluster
# But requires base images to start first
```

### 9. **Summary**

**Mirror Registry is indeed installed inside the bastion host**, this design has the following advantages:

1. **Reasonable Network Architecture**: Acts as network boundary, controlling internal and external traffic
2. **Efficient Resource Utilization**: Centralized storage, shared access
3. **Simple Operations Management**: Unified management of image sync and maintenance
4. **Good Security Control**: Centralized management of access policies and authentication

This architecture is the standard pattern for disconnected cluster deployment, ensuring efficiency and security of image synchronization.

---

Ignition is the **system initialization tool** used by Red Hat CoreOS (RHCOS) and Fedora CoreOS (FCOS) to configure the operating system during first boot. Let me explain in detail:

## Ignition Configuration Overview

### 1. **What is Ignition**

Ignition is the **first boot configuration tool** for the CoreOS family, similar to:
- **cloud-init** (Ubuntu/Debian)
- **user-data** (AWS)
- **custom-data** (Azure)

### 2. **Core Functions**

```yaml
# Ignition configuration example
{
  "ignition": {
    "version": "3.4.0",
    "config": {
      "replace": {
        "source": "http://example.com/config.ign"
      }
    }
  },
  "storage": {
    "files": [
      {
        "path": "/etc/hostname",
        "mode": 420,
        "contents": {
          "source": "data:,bastion-host"
        }
      }
    ],
    "directories": [
      {
        "path": "/opt/mirror-registry",
        "mode": 493
      }
    ]
  },
  "systemd": {
    "units": [
      {
        "name": "mirror-registry.service",
        "enabled": true,
        "contents": "[Unit]\nDescription=Mirror Registry\n[Service]\nExecStart=/usr/bin/podman run --name mirror-registry -p 5000:5000 -v /opt/mirror-registry:/var/lib/registry registry:2\n[Install]\nWantedBy=multi-user.target"
      }
    ]
  }
}
```

### 3. **Application in Bastion Host**

#### **A. Create Ignition Configuration**
```bash
# In aws-provision-bastionhost-commands.sh
bastion_ignition_file="${SHARED_DIR}/${CLUSTER_NAME}-bastion.ign"

# This file contains the complete configuration for bastion host
```

#### **B. Configuration Content Example**
```json
{
  "ignition": {
    "version": "3.0.0",
    "config": {
      "replace": {
        "source": "s3://${s3_bucket_name}/bastion.ign"
      }
    }
  },
  "storage": {
    "files": [
      {
        "path": "/etc/hostname",
        "mode": 420,
        "contents": {
          "source": "data:,${CLUSTER_NAME}-bastion"
        }
      },
      {
        "path": "/etc/mirror-registry/config.yml",
        "mode": 420,
        "contents": {
          "source": "data:,",
          "inline": "version: 0.1\nstorage:\n  filesystem:\n    rootdirectory: /var/lib/registry\nhttp:\n  addr: :5000"
        }
      }
    ],
    "directories": [
      {
        "path": "/var/lib/registry",
        "mode": 493
      }
    ]
  },
  "systemd": {
    "units": [
      {
        "name": "mirror-registry.service",
        "enabled": true,
        "contents": "[Unit]\nDescription=Mirror Registry\nAfter=network.target\n[Service]\nType=simple\nExecStart=/usr/bin/podman run --name mirror-registry -p 5000:5000 -v /var/lib/registry:/var/lib/registry registry:2\nRestart=always\n[Install]\nWantedBy=multi-user.target"
      },
      {
        "name": "http-proxy.service",
        "enabled": true,
        "contents": "[Unit]\nDescription=HTTP Proxy\nAfter=network.target\n[Service]\nType=simple\nExecStart=/usr/bin/squid -f /etc/squid/squid.conf\nRestart=always\n[Install]\nWantedBy=multi-user.target"
      }
    ]
  }
}
```

### 4. **Components of Ignition Configuration**

#### **A. File System Configuration (storage)**
```json
"storage": {
  "files": [
    {
      "path": "/etc/hostname",
      "mode": 420,
      "contents": {
        "source": "data:,my-hostname"
      }
    }
  ],
  "directories": [
    {
      "path": "/opt/app",
      "mode": 493
    }
  ],
  "links": [
    {
      "path": "/etc/localtime",
      "target": "/usr/share/zoneinfo/UTC"
    }
  ]
}
```

#### **B. System Service Configuration (systemd)**
```json
"systemd": {
  "units": [
    {
      "name": "my-service.service",
      "enabled": true,
      "contents": "[Unit]\nDescription=My Service\n[Service]\nExecStart=/usr/bin/my-app\n[Install]\nWantedBy=multi-user.target"
    }
  ]
}
```

#### **C. User Configuration (passwd)**
```json
"passwd": {
  "users": [
    {
      "name": "core",
      "sshAuthorizedKeys": [
        "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
      ]
    }
  ]
}
```

### 5. **Usage in AWS**

#### **A. Pass via UserData**
```bash
# In CloudFormation template
UserData:
  Fn::Base64:
    !Sub
      - '{"ignition":{"config":{"replace":{"source":"${IgnitionLocation}"}},"version":"3.0.0"}}'
      - IgnitionLocation: !Ref BastionIgnitionLocation
```

#### **B. S3 Storage Configuration**
```bash
# Upload Ignition configuration to S3
ign_location="s3://${s3_bucket_name}/bastion.ign"
aws --region $REGION s3 cp ${bastion_ignition_file} "${ign_location}"
```

### 6. **Ignition vs Other Configuration Tools**

| Feature | Ignition | cloud-init | user-data |
|------|----------|------------|-----------|
| **Target System** | CoreOS | Ubuntu/Debian | AWS EC2 |
| **Configuration Format** | JSON | YAML/Shell | Shell/Cloud-init |
| **Execution Timing** | First boot | First boot | First boot |
| **Configuration Method** | Declarative | Scripted | Scripted |

### 7. **Actual Workflow**

```mermaid
sequenceDiagram
    participant Admin as Administrator
    participant S3 as S3 Bucket
    participant EC2 as EC2 Instance
    participant Ignition as Ignition Service

    Admin->>S3: 1. Upload Ignition configuration
    S3-->>Admin: Configuration stored

    Admin->>EC2: 2. Launch EC2 instance
    Note over EC2: UserData contains Ignition configuration URL

    EC2->>Ignition: 3. Read configuration during first boot
    Ignition->>S3: 4. Download complete configuration
    S3-->>Ignition: Return configuration content

    Ignition->>EC2: 5. Apply configuration
    Note over EC2: Create files, directories, services, etc.

    EC2-->>Admin: 6. System configuration complete
```

### 8. **Advantages**

#### **A. Declarative Configuration**
```json
// Declare what to create, not how to create
{
  "storage": {
    "files": [
      {
        "path": "/etc/hostname",
        "contents": {"source": "data:,my-host"}
      }
    ]
  }
}
```

#### **B. Idempotency**
- Same result from multiple executions
- No side effects

#### **C. Security**
- Configuration encrypted during transmission and storage
- Supports TLS verification

#### **D. Flexibility**
- Supports multiple data sources
- Can reference external configurations

### 9. **Role in Disconnected Cluster**

In disconnected cluster deployment, Ignition configuration is used for:

1. **Configure Bastion Host**: Install mirror registry, HTTP proxy and other services
2. **Set up Network**: Configure network interfaces, routing, etc.
3. **Install Software**: Install necessary tools and containers
4. **Configure Services**: Start and configure various services
5. **Set up Authentication**: Configure SSH keys, user accounts, etc.

### Summary

Ignition is the **core configuration tool** for CoreOS systems, providing a **declarative, secure, and reliable** way to configure systems. In disconnected cluster deployment, it ensures that the bastion host can correctly install and configure all necessary services, providing infrastructure support for subsequent image synchronization and cluster installation.