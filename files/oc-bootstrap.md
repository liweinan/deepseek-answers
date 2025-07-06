# OpenShift Bootstrap Scripts 分析总结

基于对bootstrap-scripts目录的分析，这些是OpenShift bootstrap过程中的核心脚本，我来总结一下它们的工作流程和关键组件：

### 1. 核心启动流程

**主要启动顺序：**
```
bootkube.sh (主脚本) → crio-configure.sh → kubelet.sh → 各种operator启动
```

**bootkube.sh 的主要阶段：**
1. **API Bootstrap** - 渲染API服务器清单
2. **Auth API Bootstrap** - 渲染认证API清单
3. **Config Bootstrap** - 渲染集群配置
4. **CVO Bootstrap** - 渲染集群版本操作符
5. **Operator Bootstrap** - 启动各种operator

### 2. 关键脚本功能分析

#### **镜像处理相关：**
- **`release-image.sh`** - 定义镜像路径，已修复为使用本地registry
- **`node-image-pull.sh`** - 拉取CoreOS节点镜像
- **`release-image-download.sh`** - 下载release镜像

#### **容器运行时配置：**
- **`crio-configure.sh`** - 配置CRI-O使用本地pause镜像
- **`kubelet.sh`** - 启动kubelet，配置使用CRI-O socket

#### **系统服务：**
- **`node-image-pull.service`** - 拉取节点镜像的systemd服务
- **`node-image-overlay.service`** - 处理镜像覆盖层
- **`node-image-finish.service`** - 完成镜像处理

### 3. 配置文件分析

#### **Registry配置 (`registries.conf`)：**
- ✅ **已修复**：所有mirror都设置为 `insecure = true`
- ✅ **已配置**：所有外部registry都mirror到 `localhost:5000`
- ✅ **支持**：registry.ci.openshift.org、quay.io等

#### **Hosts配置 (`hosts`)：**
- ✅ **已配置**：将外部registry域名指向bastion (10.0.10.10)
- 包括：registry.ci.openshift.org、quay.io、registry.access.redhat.com

#### **Docker配置 (`docker-config.json`)：**
- ✅ **已配置**：包含localhost:5000的认证信息

### 4. 关键发现和状态

#### **✅ 已修复的问题：**
1. **Registry配置** - 所有mirror都正确设置为insecure=true
2. **Release镜像路径** - release-image.sh已修改为使用localhost:5000
3. **Hosts配置** - 外部registry域名正确指向bastion
4. **认证配置** - docker-config.json包含本地registry认证

#### **🔧 当前工作状态：**
1. **Bootstrap脚本已优化** - 支持disconnected环境
2. **镜像路径已修复** - 使用本地registry而不是外部
3. **配置已完善** - registry、hosts、认证都已正确配置

#### **📋 下一步需要解决的问题：**
1. **CRI-O运行时** - bootstrap节点需要CRI-O或Podman作为容器运行时
2. **crictl工具** - 需要crictl进行容器运行时测试
3. **镜像同步** - 确保所有必要镜像都在本地registry中

### 5. 脚本执行流程

**Bootstrap启动流程：**
```
1. 系统启动 → 2. 加载bootstrap.ign → 3. 执行bootkube.sh
4. 配置CRI-O → 5. 启动kubelet → 6. 渲染manifests
7. 启动etcd → 8. 启动API server → 9. 启动operators
10. 等待集群就绪 → 11. 完成bootstrap
```

---

OpenShift Disconnected Cluster Installation Timeline

## 完整安装时序图

```mermaid
sequenceDiagram
    participant Local as 本地机器
    participant AWS as AWS云平台
    participant Bastion as Bastion主机
    participant Registry as 本地镜像仓库
    participant Bootstrap as Bootstrap节点
    participant Master as Master节点
    participant Worker as Worker节点

    Note over Local,Worker: 阶段1: 基础设施准备
    Local->>AWS: 01-create-infrastructure.sh<br/>创建VPC、子网、安全组
    AWS-->>Local: 返回基础设施信息
    Local->>AWS: 02-create-bastion.sh<br/>部署Bastion主机
    AWS-->>Local: 返回Bastion连接信息
    
    Note over Local,Worker: 阶段2: 环境配置
    Local->>Bastion: 03-copy-credentials.sh<br/>复制AWS凭证、SSH密钥
    Local->>Bastion: 04-copy-infra-and-tools.sh<br/>复制工具和配置
    Bastion->>Bastion: 安装oc、podman、jq等工具
    
    Note over Local,Worker: 阶段3: 镜像仓库搭建
    Bastion->>Bastion: 05-setup-mirror-registry.sh<br/>部署私有镜像仓库
    Bastion->>Registry: 启动registry容器
    Registry-->>Bastion: registry就绪
    
    Note over Local,Worker: 阶段4: 镜像同步
    Bastion->>Registry: 06-sync-images-robust.sh<br/>同步OpenShift镜像
    loop 21个核心镜像
        Bastion->>Registry: sync-single-image.sh<br/>pull + push单个镜像
        Registry-->>Bastion: 镜像同步完成
    end
    
    Note over Local,Worker: 阶段5: 安装配置
    Bastion->>Bastion: 07-prepare-install-config.sh<br/>生成install-config.yaml
    Bastion->>Bastion: 创建manifests
    Bastion->>Bastion: 验证配置正确性
    
    Note over Local,Worker: 阶段6: 集群安装
    Bastion->>Bootstrap: 08-install-cluster.sh<br/>启动bootstrap节点
    Bootstrap->>Bootstrap: 加载bootstrap.ign
    Bootstrap->>Bootstrap: 执行bootkube.sh
    
    Note over Bootstrap: Bootstrap过程
    Bootstrap->>Registry: 拉取容器镜像
    Registry-->>Bootstrap: 返回镜像
    Bootstrap->>Bootstrap: 启动CRI-O容器运行时
    Bootstrap->>Bootstrap: 启动kubelet
    Bootstrap->>Bootstrap: 渲染Kubernetes manifests
    Bootstrap->>Bootstrap: 启动etcd集群
    Bootstrap->>Bootstrap: 启动API server
    Bootstrap->>Bootstrap: 启动各种operators
    
    Note over Bootstrap: 等待集群就绪
    loop 等待集群就绪
        Bootstrap->>Bootstrap: 检查API server健康状态
        Bootstrap->>Bootstrap: 等待operators就绪
    end
    
    Bootstrap->>Master: 启动master节点
    Master->>Registry: 拉取容器镜像
    Registry-->>Master: 返回镜像
    Master->>Master: 加入集群
    Master->>Master: 启动控制平面组件
    
    Bootstrap->>Worker: 启动worker节点
    Worker->>Registry: 拉取容器镜像
    Registry-->>Worker: 返回镜像
    Worker->>Worker: 加入集群
    Worker->>Worker: 启动工作负载组件
    
    Note over Local,Worker: 阶段7: 验证和清理
    Bastion->>Bootstrap: 09-verify-cluster.sh<br/>验证集群功能
    Bootstrap-->>Bastion: 验证结果
    Bastion->>Bootstrap: 清理bootstrap节点
    Local->>AWS: 10-cleanup.sh<br/>清理临时资源
```

## Bootstrap节点详细时序图

```mermaid
sequenceDiagram
    participant System as 系统启动
    participant Ignition as Ignition配置
    participant CRIO as CRI-O运行时
    participant Kubelet as Kubelet
    participant Bootkube as Bootkube脚本
    participant Registry as 本地Registry
    participant Etcd as Etcd集群
    participant API as API Server
    participant Operators as Operators

    System->>Ignition: 加载bootstrap.ign
    Ignition->>Ignition: 应用系统配置
    Note over Ignition: 配置hosts、registries.conf等
    
    Ignition->>CRIO: 启动CRI-O服务
    CRIO->>CRIO: 加载crio-configure.sh
    CRIO->>CRIO: 配置pause镜像
    CRIO-->>Ignition: CRI-O就绪
    
    Ignition->>Kubelet: 启动kubelet服务
    Kubelet->>Kubelet: 加载kubelet.sh
    Kubelet->>CRIO: 连接CRI-O socket
    Kubelet-->>Ignition: Kubelet就绪
    
    Ignition->>Bootkube: 执行bootkube.sh
    Bootkube->>Registry: 拉取release镜像
    Registry-->>Bootkube: 返回镜像
    
    Note over Bootkube: API Bootstrap阶段
    Bootkube->>Bootkube: 渲染API manifests
    Bootkube->>Bootkube: 创建API server配置
    
    Note over Bootkube: Auth API Bootstrap阶段
    Bootkube->>Bootkube: 渲染认证API manifests
    Bootkube->>Bootkube: 配置认证组件
    
    Note over Bootkube: Config Bootstrap阶段
    Bootkube->>Bootkube: 渲染集群配置
    Bootkube->>Bootkube: 生成kubeconfig
    
    Note over Bootkube: CVO Bootstrap阶段
    Bootkube->>Bootkube: 渲染CVO manifests
    Bootkube->>Bootkube: 配置集群版本管理
    
    Bootkube->>Etcd: 启动etcd集群
    Etcd->>Etcd: 初始化数据目录
    Etcd->>Etcd: 启动etcd服务
    Etcd-->>Bootkube: Etcd就绪
    
    Bootkube->>API: 启动API server
    API->>Etcd: 连接etcd集群
    API->>API: 启动API服务
    API-->>Bootkube: API server就绪
    
    Note over Bootkube: Operator Bootstrap阶段
    Bootkube->>Operators: 启动各种operators
    loop 等待operators就绪
        Operators->>API: 注册CRDs
        Operators->>Operators: 启动operator逻辑
        Operators-->>Bootkube: 报告状态
    end
    
    Bootkube->>Bootkube: 等待集群就绪
    Bootkube->>API: 检查API健康状态
    API-->>Bootkube: 健康状态报告
    
    Note over Bootkube: Bootstrap完成
    Bootkube->>Bootkube: 记录完成状态
    Bootkube-->>Ignition: Bootstrap成功
```

## 镜像同步详细时序图

```mermaid
sequenceDiagram
    participant Bastion as Bastion主机
    participant CI as CI Registry
    participant Local as 本地Registry
    participant Script as 同步脚本

    Bastion->>Script: 执行06-sync-images-robust.sh
    
    Note over Script: 登录阶段
    Script->>CI: oc login CI集群
    CI-->>Script: 认证成功
    Script->>Local: podman login本地registry
    Local-->>Script: 认证成功
    
    loop 21个核心镜像
        Script->>Script: 选择下一个镜像
        
        Note over Script: Pull阶段
        Script->>CI: podman pull镜像
        CI-->>Script: 下载镜像完成
        
        Note over Script: Push阶段
        Script->>Local: podman push镜像
        Local-->>Script: 上传镜像完成
        
        Note over Script: 清理阶段
        Script->>Script: 清理本地镜像
        Script->>Script: 释放磁盘空间
    end
    
    Script->>Script: 生成同步报告
    Script->>Script: 生成ImageContentSources配置
    Script-->>Bastion: 同步完成
```

---

关键配置点

### 1. Registry配置
- 所有外部registry都mirror到localhost:5000
- 所有mirror都设置为insecure=true
- 支持registry.ci.openshift.org、quay.io等

### 2. 网络配置
- VPC私有子网，通过NAT网关访问外网
- Bastion在公有子网，作为跳板机
- Bootstrap/Master/Worker在私有子网

### 3. 认证配置
- AWS凭证通过bastion传递
- Registry认证包含在docker-config.json中
- SSH密钥用于节点访问

### 4. 镜像处理
- 使用image_for()函数获取本地镜像路径
- 支持镜像digest和tag两种方式
- 自动重试机制处理网络问题

## 故障排除点

### 1. 镜像同步失败
- 检查网络连接
- 验证CI集群认证
- 检查本地registry存储空间

### 2. Bootstrap启动失败
- 检查CRI-O配置
- 验证镜像可访问性
- 查看bootstrap日志

### 3. 集群安装失败
- 检查manifests配置
- 验证网络策略
- 查看operator日志

### 4. 节点无法加入集群
- 检查kubelet配置
- 验证证书配置
- 查看节点日志

### 6. 关键配置点

#### **镜像处理：**
- 使用 `image_for()` 函数获取本地镜像路径
- 所有镜像都从 `localhost:5000` 拉取
- 支持镜像digest和tag两种方式

#### **容器运行时：**
- kubelet配置使用 `/var/run/crio/crio.sock`
- CRI-O配置使用本地pause镜像
- 支持systemd cgroup驱动

#### **网络配置：**
- 使用host网络模式避免IP冲突
- 配置本地registry访问
- 支持insecure registry

### 7. 总结

这些bootstrap脚本已经很好地适配了disconnected环境：

1. **✅ Registry配置正确** - 所有外部registry都mirror到本地
2. **✅ 镜像路径已修复** - 使用本地registry路径
3. **✅ Hosts配置完善** - 外部域名正确解析
4. **✅ 认证配置正确** - 包含本地registry认证

**当前主要挑战：**
- bootstrap节点需要容器运行时（CRI-O或Podman）
- 需要crictl工具进行测试
- 确保所有必要镜像都在本地registry中

这些脚本为disconnected OpenShift集群的bootstrap过程提供了完整的支持。

---

OpenShift Disconnected Cluster Installation Timeline

## 完整安装时序图

```mermaid
sequenceDiagram
    participant Local as 本地机器
    participant AWS as AWS云平台
    participant Bastion as Bastion主机
    participant Registry as 本地镜像仓库
    participant Bootstrap as Bootstrap节点
    participant Master as Master节点
    participant Worker as Worker节点

    Note over Local,Worker: 阶段1: 基础设施准备
    Local->>AWS: 01-create-infrastructure.sh<br/>创建VPC、子网、安全组
    AWS-->>Local: 返回基础设施信息
    Local->>AWS: 02-create-bastion.sh<br/>部署Bastion主机
    AWS-->>Local: 返回Bastion连接信息
    
    Note over Local,Worker: 阶段2: 环境配置
    Local->>Bastion: 03-copy-credentials.sh<br/>复制AWS凭证、SSH密钥
    Local->>Bastion: 04-copy-infra-and-tools.sh<br/>复制工具和配置
    Bastion->>Bastion: 安装oc、podman、jq等工具
    
    Note over Local,Worker: 阶段3: 镜像仓库搭建
    Bastion->>Bastion: 05-setup-mirror-registry.sh<br/>部署私有镜像仓库
    Bastion->>Registry: 启动registry容器
    Registry-->>Bastion: registry就绪
    
    Note over Local,Worker: 阶段4: 镜像同步
    Bastion->>Registry: 06-sync-images-robust.sh<br/>同步OpenShift镜像
    loop 21个核心镜像
        Bastion->>Registry: sync-single-image.sh<br/>pull + push单个镜像
        Registry-->>Bastion: 镜像同步完成
    end
    
    Note over Local,Worker: 阶段5: 安装配置
    Bastion->>Bastion: 07-prepare-install-config.sh<br/>生成install-config.yaml
    Bastion->>Bastion: 创建manifests
    Bastion->>Bastion: 验证配置正确性
    
    Note over Local,Worker: 阶段6: 集群安装
    Bastion->>Bootstrap: 08-install-cluster.sh<br/>启动bootstrap节点
    Bootstrap->>Bootstrap: 加载bootstrap.ign
    Bootstrap->>Bootstrap: 执行bootkube.sh
    
    Note over Bootstrap: Bootstrap过程
    Bootstrap->>Registry: 拉取容器镜像
    Registry-->>Bootstrap: 返回镜像
    Bootstrap->>Bootstrap: 启动CRI-O容器运行时
    Bootstrap->>Bootstrap: 启动kubelet
    Bootstrap->>Bootstrap: 渲染Kubernetes manifests
    Bootstrap->>Bootstrap: 启动etcd集群
    Bootstrap->>Bootstrap: 启动API server
    Bootstrap->>Bootstrap: 启动各种operators
    
    Note over Bootstrap: 等待集群就绪
    loop 等待集群就绪
        Bootstrap->>Bootstrap: 检查API server健康状态
        Bootstrap->>Bootstrap: 等待operators就绪
    end
    
    Bootstrap->>Master: 启动master节点
    Master->>Registry: 拉取容器镜像
    Registry-->>Master: 返回镜像
    Master->>Master: 加入集群
    Master->>Master: 启动控制平面组件
    
    Bootstrap->>Worker: 启动worker节点
    Worker->>Registry: 拉取容器镜像
    Registry-->>Worker: 返回镜像
    Worker->>Worker: 加入集群
    Worker->>Worker: 启动工作负载组件
    
    Note over Local,Worker: 阶段7: 验证和清理
    Bastion->>Bootstrap: 09-verify-cluster.sh<br/>验证集群功能
    Bootstrap-->>Bastion: 验证结果
    Bastion->>Bootstrap: 清理bootstrap节点
    Local->>AWS: 10-cleanup.sh<br/>清理临时资源
```

## Bootstrap节点详细时序图

```mermaid
sequenceDiagram
    participant System as 系统启动
    participant Ignition as Ignition配置
    participant CRIO as CRI-O运行时
    participant Kubelet as Kubelet
    participant Bootkube as Bootkube脚本
    participant Registry as 本地Registry
    participant Etcd as Etcd集群
    participant API as API Server
    participant Operators as Operators

    System->>Ignition: 加载bootstrap.ign
    Ignition->>Ignition: 应用系统配置
    Note over Ignition: 配置hosts、registries.conf等
    
    Ignition->>CRIO: 启动CRI-O服务
    CRIO->>CRIO: 加载crio-configure.sh
    CRIO->>CRIO: 配置pause镜像
    CRIO-->>Ignition: CRI-O就绪
    
    Ignition->>Kubelet: 启动kubelet服务
    Kubelet->>Kubelet: 加载kubelet.sh
    Kubelet->>CRIO: 连接CRI-O socket
    Kubelet-->>Ignition: Kubelet就绪
    
    Ignition->>Bootkube: 执行bootkube.sh
    Bootkube->>Registry: 拉取release镜像
    Registry-->>Bootkube: 返回镜像
    
    Note over Bootkube: API Bootstrap阶段
    Bootkube->>Bootkube: 渲染API manifests
    Bootkube->>Bootkube: 创建API server配置
    
    Note over Bootkube: Auth API Bootstrap阶段
    Bootkube->>Bootkube: 渲染认证API manifests
    Bootkube->>Bootkube: 配置认证组件
    
    Note over Bootkube: Config Bootstrap阶段
    Bootkube->>Bootkube: 渲染集群配置
    Bootkube->>Bootkube: 生成kubeconfig
    
    Note over Bootkube: CVO Bootstrap阶段
    Bootkube->>Bootkube: 渲染CVO manifests
    Bootkube->>Bootkube: 配置集群版本管理
    
    Bootkube->>Etcd: 启动etcd集群
    Etcd->>Etcd: 初始化数据目录
    Etcd->>Etcd: 启动etcd服务
    Etcd-->>Bootkube: Etcd就绪
    
    Bootkube->>API: 启动API server
    API->>Etcd: 连接etcd集群
    API->>API: 启动API服务
    API-->>Bootkube: API server就绪
    
    Note over Bootkube: Operator Bootstrap阶段
    Bootkube->>Operators: 启动各种operators
    loop 等待operators就绪
        Operators->>API: 注册CRDs
        Operators->>Operators: 启动operator逻辑
        Operators-->>Bootkube: 报告状态
    end
    
    Bootkube->>Bootkube: 等待集群就绪
    Bootkube->>API: 检查API健康状态
    API-->>Bootkube: 健康状态报告
    
    Note over Bootkube: Bootstrap完成
    Bootkube->>Bootkube: 记录完成状态
    Bootkube-->>Ignition: Bootstrap成功
```

---

镜像同步详细时序图

```mermaid
sequenceDiagram
    participant Bastion as Bastion主机
    participant CI as CI Registry
    participant Local as 本地Registry
    participant Script as 同步脚本

    Bastion->>Script: 执行06-sync-images-robust.sh
    
    Note over Script: 登录阶段
    Script->>CI: oc login CI集群
    CI-->>Script: 认证成功
    Script->>Local: podman login本地registry
    Local-->>Script: 认证成功
    
    loop 21个核心镜像
        Script->>Script: 选择下一个镜像
        
        Note over Script: Pull阶段
        Script->>CI: podman pull镜像
        CI-->>Script: 下载镜像完成
        
        Note over Script: Push阶段
        Script->>Local: podman push镜像
        Local-->>Script: 上传镜像完成
        
        Note over Script: 清理阶段
        Script->>Script: 清理本地镜像
        Script->>Script: 释放磁盘空间
    end
    
    Script->>Script: 生成同步报告
    Script->>Script: 生成ImageContentSources配置
    Script-->>Bastion: 同步完成
```

## 关键配置点

### 1. Registry配置
- 所有外部registry都mirror到localhost:5000
- 所有mirror都设置为insecure=true
- 支持registry.ci.openshift.org、quay.io等

### 2. 网络配置
- VPC私有子网，通过NAT网关访问外网
- Bastion在公有子网，作为跳板机
- Bootstrap/Master/Worker在私有子网

### 3. 认证配置
- AWS凭证通过bastion传递
- Registry认证包含在docker-config.json中
- SSH密钥用于节点访问

### 4. 镜像处理
- 使用image_for()函数获取本地镜像路径
- 支持镜像digest和tag两种方式
- 自动重试机制处理网络问题

## 故障排除点

### 1. 镜像同步失败
- 检查网络连接
- 验证CI集群认证
- 检查本地registry存储空间

### 2. Bootstrap启动失败
- 检查CRI-O配置
- 验证镜像可访问性
- 查看bootstrap日志

### 3. 集群安装失败
- 检查manifests配置
- 验证网络策略
- 查看operator日志

### 4. 节点无法加入集群
- 检查kubelet配置
- 验证证书配置
- 查看节点日志 


