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