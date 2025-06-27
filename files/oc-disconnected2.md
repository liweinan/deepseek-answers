# Disconnected Cluster Creation

## 在Private Cluster中的使用

### 1. **可以使用的场景**

#### **需要镜像同步的Private Cluster**
```bash
# 当private cluster需要预先同步镜像时
# 例如：网络带宽限制、安全要求、性能优化
```

#### **混合网络环境**
```bash
# 集群私有，但需要临时访问外部资源
# 例如：安装时同步镜像，运行后断开
```

### 2. **脚本的通用性设计**

脚本本身设计得比较通用，包含了多种配置选项：

```bash
# 支持自定义AMI
if [[ "${BASTION_HOST_AMI}" == "" ]]; then
  # 动态创建
else
  # 使用BYO (Bring Your Own) bastion host
  ami_id=${BASTION_HOST_AMI}
fi
```

### 3. **在Private Cluster中的具体用途**

#### **A. 镜像预同步**
```bash
# 在private cluster安装前同步镜像
# 避免安装过程中的网络问题
MIRROR_REGISTRY_URL="${BASTION_HOST_PUBLIC_DNS}:5000"
```

#### **B. 代理服务**
```bash
# 为private cluster提供代理访问
PROXY_PUBLIC_URL="http://${PROXY_CREDENTIAL}@${BASTION_HOST_PUBLIC_DNS}:3128"
PROXY_PRIVATE_URL="http://${PROXY_CREDENTIAL}@${BASTION_HOST_PRIVATE_DNS}:3128"
```

#### **C. 临时外部访问**
```bash
# 在安装过程中提供临时的外部访问能力
# 安装完成后可以移除
```

## 使用差异

### **Private Cluster vs Disconnected Cluster**

| 方面 | Private Cluster | Disconnected Cluster |
|------|----------------|---------------------|
| **必要性** | 可选 | 必需 |
| **使用时长** | 临时 | 永久 |
| **网络配置** | 安装后可能移除 | 持续使用 |
| **镜像同步** | 可选优化 | 必需步骤 |

### **Private Cluster中的配置示例**

```yaml
# install-config.yaml for Private Cluster
publish: Internal
platform:
  aws:
    privateLink: true
# 可以选择性地配置镜像仓库
imageContentSources:
- mirrors:
  - bastion-host:5000/openshift4/ose-kube-rbac-proxy
  source: registry.redhat.io/openshift4/ose-kube-rbac-proxy
```

## 实际使用场景

### **场景1: 网络受限的Private Cluster**
```bash
# 企业网络有带宽限制
# 使用bastion host预先同步镜像
# 安装时从本地仓库拉取
```

### **场景2: 安全要求高的Private Cluster**
```bash
# 需要预先验证所有镜像
# 使用bastion host作为镜像验证点
# 确保所有镜像都经过安全扫描
```

### **场景3: 性能优化的Private Cluster**
```bash
# 避免安装时的网络延迟
# 预先同步镜像到本地
# 提高安装速度和稳定性
```

## 配置选项

### **可选使用**
```bash
# 可以通过环境变量控制是否使用
BASTION_HOST_AMI=""  # 不使用自定义AMI
CUSTOM_PROXY_CREDENTIAL="false"  # 使用默认代理配置
```

### **部分功能使用**
```bash
# 只使用镜像仓库功能
# 不使用代理功能
# 或者只使用代理功能，不使用镜像仓库
```

## 总结

这个脚本**完全可以用于private cluster的安装**，但通常是**可选的**，而不是必需的。在private cluster中，它主要用于：

1. **性能优化**: 预先同步镜像
2. **网络优化**: 减少安装时的网络依赖
3. **安全增强**: 镜像验证和扫描
4. **临时访问**: 安装过程中的外部资源访问

与disconnected cluster不同，private cluster安装完成后，这些bastion host和镜像仓库服务通常可以移除，因为集群本身仍然可以访问互联网来拉取镜像。

---

我来为你详细介绍这个项目中与disconnected cluster和mirror registry相关的内容。

## 项目结构与Disconnected Cluster相关组件

### 1. **AWS基础设施层 (step-registry/aws/provision/)**

#### **A. VPC配置**
```bash
step-registry/aws/provision/vpc/disconnected/
├── aws-provision-vpc-disconnected-ref.yaml
├── aws-provision-vpc-disconnected-commands.sh
└── aws-provision-vpc-disconnected-ref.metadata.json
```
**作用**: 为disconnected cluster创建专用的VPC网络环境

#### **B. Bastion Host配置**
```bash
step-registry/aws/provision/bastionhost/
├── aws-provision-bastionhost-ref.yaml
├── aws-provision-bastionhost-commands.sh
└── aws-provision-bastionhost-chain.yaml
```
**作用**: 创建跳板机，提供镜像仓库和代理服务

#### **C. CCO静态用户配置**
```bash
step-registry/aws/provision/cco-manual-users/static/
├── aws-provision-cco-manual-users-static-ref.yaml
├── aws-provision-cco-manual-users-static-commands.sh
└── aws-provision-cco-manual-users-static-ref.metadata.json
```
**作用**: 为disconnected cluster创建静态IAM用户和权限

### 2. **镜像同步层 (step-registry/mirror-images/)**

#### **A. 主要镜像同步工具**
```bash
step-registry/mirror-images/by-oc-mirror/
├── mirror-images-by-oc-mirror-ref.yaml
├── mirror-images-by-oc-mirror-commands.sh
└── conf-mirror/
    ├── mirror-images-by-oc-mirror-conf-mirror-ref.yaml
    └── mirror-images-by-oc-mirror-conf-mirror-commands.sh
```

**核心功能**:
```bash
# 使用oc-mirror工具同步镜像
oc-mirror --config=imageset.yaml docker://${MIRROR_REGISTRY_HOST}

# 生成ImageContentSourcePolicy和CatalogSource
# 输出到oc-mirror-workspace/results-*/
```

#### **B. 镜像标签处理**
```bash
step-registry/mirror-images/tag-images/
├── mirror-images-tag-images-ref.yaml
└── mirror-images-tag-images-commands.sh
```
**作用**: 处理镜像标签，确保disconnected环境中的镜像引用正确

### 3. **集群安装配置层 (step-registry/ipi/)**

#### **A. 镜像配置**
```bash
step-registry/ipi/conf/mirror/
├── ipi-conf-mirror-ref.yaml
└── ipi-conf-mirror-commands.sh
```
**作用**: 配置install-config.yaml中的镜像仓库设置

#### **B. 安装流程**
```bash
step-registry/ipi/install/install/
├── ipi-install-install-ref.yaml
└── ipi-install-install-commands.sh
```
**作用**: 执行OpenShift集群安装

### 4. **安装后配置层**

#### **A. Catalog Source配置**
```bash
step-registry/enable-qe-catalogsource/disconnected/
├── enable-qe-catalogsource-disconnected-ref.yaml
└── enable-qe-catalogsource-disconnected-commands.sh
```
**作用**: 为disconnected环境配置本地operator catalog

#### **B. 镜像仓库配置**
```bash
step-registry/ipi/install/registry/
├── ipi-install-vsphere-registry-ref.yaml
└── ipi-install-vsphere-registry-commands.sh
```
**作用**: 配置集群内部的镜像仓库

### 5. **完整安装链 (step-registry/cucushift/)**

#### **A. Disconnected Cluster安装链**
```bash
step-registry/cucushift/installer/rehearse/vsphere/ipi/disconnected/provision/
├── cucushift-installer-rehearse-vsphere-ipi-disconnected-provision-chain.yaml
└── cucushift-installer-rehearse-vsphere-ipi-disconnected-provision-workflow.yaml
```

**安装步骤**:
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

### 6. **工具和脚本**

#### **A. oc-mirror工具使用**
```bash
# 下载和安装
curl -L -o oc-mirror.tar.gz https://mirror.openshift.com/pub/openshift-v4/amd64/clients/ocp/latest/oc-mirror.tar.gz
tar -xvzf oc-mirror.tar.gz

# 镜像同步
./oc-mirror --config=imageset.yaml docker://${MIRROR_REGISTRY_HOST} --continue-on-error --skip-missing
```

#### **B. ImageSetConfiguration配置**
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

### 7. **配置文件示例**

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
  # 镜像仓库的CA证书
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

### 8. **关键环境变量**

```bash
# 镜像仓库配置
MIRROR_REGISTRY_HOST="bastion-host.example.com:5000"
MIRROR_REGISTRY_URL="${MIRROR_REGISTRY_HOST}"

# 代理配置
PROXY_PUBLIC_URL="http://user:pass@bastion-host.example.com:3128"
PROXY_PRIVATE_URL="http://user:pass@bastion-host.example.com:3128"

# CCO配置
CREDENTIALS_MODE="Manual"
```

### 9. **工作流程总结**

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

### 10. **项目特色**

1. **模块化设计**: 每个组件职责明确，可独立使用
2. **多平台支持**: 支持AWS、vSphere、Nutanix等平台
3. **工具集成**: 深度集成oc-mirror等OpenShift官方工具
4. **配置灵活**: 支持多种disconnected场景配置
5. **自动化程度高**: 从基础设施到应用部署全流程自动化

这个项目为disconnected OpenShift集群的部署提供了完整的解决方案，涵盖了从基础设施准备到应用部署的各个环节。

---

是的，mirror registry通常是安装在bastion host里面的。让我详细解释一下这个架构：

## Mirror Registry在Bastion Host中的部署

### 1. **架构设计**

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

### 2. **Bastion Host中的服务配置**

从`aws-provision-bastionhost-commands.sh`可以看到，bastion host配置了多个端口：

```yaml
# 安全组配置
- IpProtocol: tcp
  FromPort: 5000
  ToPort: 5000
  CidrIp: 0.0.0.0/0  # Mirror Registry端口

- IpProtocol: tcp
  FromPort: 6001
  ToPort: 6002
  CidrIp: 0.0.0.0/0  # 额外的镜像仓库端口

- IpProtocol: tcp
  FromPort: 3128
  ToPort: 3128
  CidrIp: 0.0.0.0/0  # HTTP代理端口
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