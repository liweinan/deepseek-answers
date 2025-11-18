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

### 3. **Mirror Registry的URL配置**

```bash
# 在bastion host脚本中设置
MIRROR_REGISTRY_URL="${BASTION_HOST_PUBLIC_DNS}:5000"
echo "${MIRROR_REGISTRY_URL}" > "${SHARED_DIR}/mirror_registry_url"
```

### 4. **实际部署方式**

#### **A. 通过Ignition配置部署**
```bash
# bastion host使用Ignition配置
bastion_ignition_file="${SHARED_DIR}/${CLUSTER_NAME}-bastion.ign"

# Ignition配置包含mirror registry的安装和配置
```

#### **B. 容器化部署**
```yaml
# 通常在bastion host上运行容器化的registry
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

### 5. **为什么选择Bastion Host**

#### **A. 网络优势**
- **双重网络访问**: 可以访问互联网（同步镜像）和内部网络（服务集群）
- **网络隔离**: 作为网络边界，控制流量流向
- **安全控制**: 集中管理网络访问策略

#### **B. 资源管理**
- **存储集中**: 镜像存储在bastion host上，集群节点共享访问
- **带宽优化**: 避免每个节点都从外部拉取镜像
- **缓存效果**: 一次同步，多次使用

#### **C. 运维便利**
- **统一管理**: 镜像同步、更新、维护都在一个地方
- **监控集中**: 可以统一监控镜像仓库状态
- **备份简单**: 只需要备份bastion host上的数据

### 6. **实际工作流程**

```bash
# 1. Bastion Host创建
aws-provision-bastionhost-commands.sh
# 创建EC2实例，配置安全组，安装mirror registry

# 2. 镜像同步
mirror-images-by-oc-mirror-commands.sh
# 在bastion host上执行oc-mirror，同步镜像到本地registry

# 3. 集群安装
# 集群安装时从bastion host的mirror registry拉取镜像
```

### 7. **配置示例**

#### **A. Bastion Host上的Registry配置**
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

#### **B. 集群中的镜像配置**
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

### 8. **其他可能的部署方式**

虽然主要部署在bastion host，但也有其他选择：

#### **A. 独立服务器**
```bash
# 专门的镜像仓库服务器
MIRROR_REGISTRY_HOST="mirror-registry.example.com:5000"
```

#### **B. 集群内部**
```bash
# 在集群内部部署registry
# 但需要先有基础镜像才能启动
```

### 9. **总结**

**Mirror Registry确实安装在bastion host里面**，这种设计有以下优势：

1. **网络架构合理**: 作为网络边界，控制内外流量
2. **资源利用高效**: 集中存储，共享访问
3. **运维管理简单**: 统一管理镜像同步和维护
4. **安全控制好**: 集中管理访问策略和认证

这种架构是disconnected cluster部署的标准模式，确保了镜像同步的效率和安全性。

---

Ignition是Red Hat CoreOS (RHCOS) 和 Fedora CoreOS (FCOS) 使用的**系统初始化工具**，用于在系统首次启动时配置操作系统。让我详细解释一下：

## Ignition配置概述

### 1. **什么是Ignition**

Ignition是CoreOS家族的**第一启动配置工具**，类似于：
- **cloud-init** (Ubuntu/Debian)
- **user-data** (AWS)
- **custom-data** (Azure)

### 2. **核心功能**

```yaml
# Ignition配置示例
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

### 3. **在Bastion Host中的应用**

#### **A. 创建Ignition配置**
```bash
# 在aws-provision-bastionhost-commands.sh中
bastion_ignition_file="${SHARED_DIR}/${CLUSTER_NAME}-bastion.ign"

# 这个文件包含了bastion host的完整配置
```

#### **B. 配置内容示例**
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

### 4. **Ignition配置的组成部分**

#### **A. 文件系统配置 (storage)**
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

#### **B. 系统服务配置 (systemd)**
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

#### **C. 用户配置 (passwd)**
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

### 5. **在AWS中的使用**

#### **A. 通过UserData传递**
```bash
# 在CloudFormation模板中
UserData:
  Fn::Base64:
    !Sub
      - '{"ignition":{"config":{"replace":{"source":"${IgnitionLocation}"}},"version":"3.0.0"}}'
      - IgnitionLocation: !Ref BastionIgnitionLocation
```

#### **B. S3存储配置**
```bash
# 将Ignition配置上传到S3
ign_location="s3://${s3_bucket_name}/bastion.ign"
aws --region $REGION s3 cp ${bastion_ignition_file} "${ign_location}"
```

### 6. **Ignition vs 其他配置工具**

| 特性 | Ignition | cloud-init | user-data |
|------|----------|------------|-----------|
| **目标系统** | CoreOS | Ubuntu/Debian | AWS EC2 |
| **配置格式** | JSON | YAML/Shell | Shell/Cloud-init |
| **执行时机** | 首次启动 | 首次启动 | 首次启动 |
| **配置方式** | 声明式 | 脚本式 | 脚本式 |

### 7. **实际工作流程**

```mermaid
sequenceDiagram
    participant Admin as Administrator
    participant S3 as S3 Bucket
    participant EC2 as EC2 Instance
    participant Ignition as Ignition Service

    Admin->>S3: 1. 上传Ignition配置
    S3-->>Admin: 配置已存储

    Admin->>EC2: 2. 启动EC2实例
    Note over EC2: UserData包含Ignition配置URL

    EC2->>Ignition: 3. 首次启动时读取配置
    Ignition->>S3: 4. 下载完整配置
    S3-->>Ignition: 返回配置内容

    Ignition->>EC2: 5. 应用配置
    Note over EC2: 创建文件、目录、服务等

    EC2-->>Admin: 6. 系统配置完成
```

### 8. **优势**

#### **A. 声明式配置**
```json
// 声明要创建什么，而不是如何创建
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

#### **B. 幂等性**
- 多次执行结果相同
- 不会产生副作用

#### **C. 安全性**
- 配置在传输和存储时加密
- 支持TLS验证

#### **D. 灵活性**
- 支持多种数据源
- 可以引用外部配置

### 9. **在Disconnected Cluster中的作用**

在disconnected cluster部署中，Ignition配置用于：

1. **配置Bastion Host**: 安装mirror registry、HTTP代理等服务
2. **设置网络**: 配置网络接口、路由等
3. **安装软件**: 安装必要的工具和容器
4. **配置服务**: 启动和配置各种服务
5. **设置认证**: 配置SSH密钥、用户账户等

### 总结

Ignition是CoreOS系统的**核心配置工具**，它提供了一种**声明式、安全、可靠**的方式来配置系统。在disconnected cluster部署中，它确保了bastion host能够正确安装和配置所有必要的服务，为后续的镜像同步和集群安装提供基础设施支持。