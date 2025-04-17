### OpenShift Installer 详解

OpenShift Installer 是 Red Hat 提供的用于部署 **OpenShift Container Platform (OCP)** 的核心工具，它简化了在多种基础设施（如 AWS、Azure、裸机等）上安装 OpenShift 集群的过程。以下是其关键特性和工作流程的详细介绍：

---

#### **1. 核心功能**
- **自动化部署**：一键式创建 OpenShift 集群，包括控制平面（Master）和工作节点（Worker）。
- **多平台支持**：
    - 公有云（AWS、Azure、GCP、IBM Cloud）
    - 私有云（VMware vSphere、OpenStack）
    - 裸机（Bare Metal）
    - 边缘计算（Compact/Single Node OpenShift）
- **声明式配置**：通过配置文件（如 `install-config.yaml`）定义集群参数。
- **可扩展性**：支持自定义网络插件（如 Calico、OVN-Kubernetes）、存储后端等。

---

#### **2. 安装流程**
1. **准备环境**：
    - 满足[硬件要求](https://docs.openshift.com/container-platform/latest/installing/installing_bare_metal/installing-bare-metal.html#minimum-resource-requirements_installing-bare-metal)（如 CPU、内存、存储）。
    - 配置基础设施权限（如 AWS IAM 策略、vSphere 账户）。

2. **下载 Installer**：
   ```bash
   # 从 Red Hat 镜像站下载（需订阅）
   wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-linux.tar.gz
   tar -xvf openshift-install-linux.tar.gz
   ```

3. **生成配置文件**：
   ```bash
   # 交互式生成 install-config.yaml
   ./openshift-install create install-config --dir=<installation_dir>
   ```
    - 编辑 `install-config.yaml` 示例：
      ```yaml
      apiVersion: v1
      baseDomain: example.com
      compute:
      - name: worker
        replicas: 3
      controlPlane:
        name: master
        replicas: 3
      metadata:
        name: my-cluster
      platform:
        aws:
          region: us-east-1
      pullSecret: '{"auths": ...}'  # 从 Red Hat 控制台获取
      sshKey: 'ssh-rsa ...'         # 用于节点访问
      ```

4. **部署集群**：
   ```bash
   ./openshift-install create cluster --dir=<installation_dir>
   ```
    - 自动完成以下步骤：
        - 基础设施资源创建（如 VPC、虚拟机）。
        - 引导节点启动。
        - 控制平面和工作节点配置。
        - Operator 部署（如 Ingress、监控）。

5. **访问集群**：
    - 安装完成后，输出 `kubeconfig` 文件路径：
      ```bash
      export KUBECONFIG=<installation_dir>/auth/kubeconfig
      oc get nodes  # 验证集群状态
      ```

---

#### **3. 高级功能**
- **定制化安装**：
    - 通过 `manifest` 和 `openshift` 目录修改集群配置（如网络 CIDR）。
    - 使用 `MachineConfig` 调整节点内核参数。
- **离线安装**：
    - 配置镜像仓库（如 `mirror.openshift.com`）和本地镜像缓存。
- **集群扩展**：
    - 通过 `openshift-install` 添加新节点或升级版本。

---

#### **4. 关键文件结构**
```
<installation_dir>/
├── auth/                    # 认证文件
│   ├── kubeconfig           # 集群访问配置
│   └── kubeadmin-password   # 默认管理员密码
├── install-config.yaml      # 安装配置（安装后自动删除）
└── .openshift_install.log   # 安装日志
```

---

#### **5. 常见问题排查**
- **网络问题**：
    - 确保防火墙允许 OpenShift 端口（如 6443、22623）。
- **资源不足**：
    - 检查节点资源是否符合[最低要求](https://docs.openshift.com/container-platform/latest/installing/installing_bare_metal/installing-bare-metal.html#minimum-resource-requirements_installing-bare-metal)。
- **证书错误**：
    - 使用 `openshift-install wait-for install-complete` 监控进度。

---

#### **6. 与相关工具对比**
| 工具                | OpenShift Installer | kubeadm | Terraform + RKE |
|---------------------|---------------------|---------|-----------------|
| **目标平台**        | 多云/企业级         | 通用    | 多云/定制化     |
| **复杂度**          | 中等（集成化）      | 低      | 高              |
| **适用场景**        | 生产环境            | 测试/PoC| 混合云          |

---

#### **7. 参考资源**
- [官方文档](https://docs.openshift.com/container-platform/latest/installing/installing_bare_metal/installing-bare-metal.html)
- [GitHub 仓库](https://github.com/openshift/installer)
- [Red Hat 学习路径](https://www.redhat.com/en/services/training/do280-openshift-administration-i)

通过 OpenShift Installer，用户可以快速获得一个符合企业安全标准的 Kubernetes 环境，并直接使用 OpenShift 的增强功能（如 Operator Framework、内置监控等）。


---

OpenShift Installer 支持多种平台（也称为 **安装目标平台**），覆盖公有云、私有云、裸金属和边缘环境。以下是详细的平台支持列表及其关键特性：

---

### **1. 公有云平台**
| 平台       | 支持版本 | 关键特性                                                                 |
|------------|----------|--------------------------------------------------------------------------|
| **AWS**    | 全区域   | 自动配置 VPC、负载均衡器、EBS 存储；支持 ROSA（Red Hat OpenShift on AWS） |
| **Azure**  | 全区域   | 集成 Azure Active Directory、Managed Disks；支持 ARO（Azure Red Hat OpenShift） |
| **GCP**    | 全区域   | 使用 Google Cloud Storage 存储镜像；支持 GKE 集成                        |
| **IBM Cloud** | 全区域 | 支持 PowerVS 和 Classic Infrastructure                                  |

---

### **2. 私有云/虚拟化平台**
| 平台               | 支持版本                | 关键特性                                                                 |
|--------------------|-------------------------|--------------------------------------------------------------------------|
| **VMware vSphere** | 6.7 及以上              | 自动部署 VM、配置 vCenter 存储；支持网络自定义（NSX-T 或标准交换机）     |
| **OpenStack**      | Queens 及以上           | 集成 Neutron 网络、Cinder 存储；需配置 Octavia 负载均衡                  |
| **RHV (Red Hat Virtualization)** | 4.4 及以上 | 需手动导入镜像，支持 oVirt 管理接口                                      |

---

### **3. 裸金属（Bare Metal）**
| 场景               | 要求                                                                 |
|--------------------|----------------------------------------------------------------------|
| **标准裸金属**     | 需 PXE 或 ISO 引导；手动配置 DHCP、DNS 和负载均衡器（如 HAProxy）    |
| **UPI (User-Provisioned Infrastructure)** | 用户自行准备网络、存储和节点，Installer 生成配置后手动部署           |
| **单节点 OpenShift (SNO)** | 单个节点运行控制平面和工作负载，适用于边缘场景                      |

---

### **4. 边缘/特殊环境**
| 平台                     | 用途                                                                 |
|--------------------------|----------------------------------------------------------------------|
| **OpenShift on ARM**     | 支持 AWS Graviton 和裸金属 ARM 架构（如 Raspberry Pi 集群需定制）    |
| **Compact OpenShift**    | 最小化集群（3 个节点，控制平面与工作节点合并）                       |
| **Disconnected 安装**    | 离线环境，需预先镜像仓库（如 `mirror.openshift.com`）                |

---

### **5. 其他平台/技术预览**
| 平台               | 状态           | 说明                                                                 |
|--------------------|----------------|----------------------------------------------------------------------|
| **Alibaba Cloud**  | 技术预览       | 需手动配置 Terraform 脚本                                           |
| **Nutanix**        | 技术预览       | 通过 CSI 驱动集成存储                                               |
| **OpenShift Local (CRC)** | 开发用途 | 单机版 OpenShift（需 Red Hat 订阅）                                 |

---

### **关键选择因素**
1. **网络要求**：
    - 公有云：自动配置 VPC 和子网。
    - 裸金属：需用户提供负载均衡器（如 HAProxy + Keepalived）。
2. **存储集成**：
    - AWS/GCP/Azure：默认使用云存储（EBS、Persistent Disk等）。
    - vSphere/Bare Metal：需配置 StorageClass（如 Ceph、NFS）。
3. **认证与权限**：
    - 公有云需 IAM 角色（如 AWS `AdministratorAccess`）。
    - vSphere 需 `Datacenter Administrator` 权限。

---

### **安装命令示例**
#### AWS 部署
```bash
# 生成安装配置
openshift-install create install-config --dir=aws-cluster
# 开始部署
openshift-install create cluster --dir=aws-cluster --log-level=info
```

#### 裸金属 UPI 部署
```bash
# 生成 Ignition 配置文件
openshift-install create ignition-configs --dir=baremetal-cluster
# 手动将 ignition 文件部署到节点
```

---

### **不支持或已弃用的平台**
- **Microsoft Azure Stack Hub**：需使用 Azure Red Hat OpenShift (ARO)。
- **Oracle Cloud Infrastructure (OCI)**：需通过 Terraform 自定义部署。
- **OpenShift 3.x 的 Docker 安装**：已完全弃用。

---

### **参考文档**
- [官方支持平台列表](https://docs.openshift.com/container-platform/latest/installing/installing-preparing.html)
- [裸金属安装指南](https://docs.openshift.com/container-platform/latest/installing/installing_bare_metal/installing-bare-metal.html)

根据您的基础设施选择合适的平台，OpenShift Installer 会处理底层复杂性（如证书、网络策略等），确保集群符合企业级 SLA 要求。

---

### OpenShift Installer 在本地 Linux 环境的安装支持

**OpenShift Installer** 支持在本地 Linux 环境安装 OpenShift Container Platform (OCP)，但需满足特定条件和依赖。以下是详细说明：

---

### **1. 支持的本地安装类型**
#### **(1) 裸金属 (Bare Metal)**
- **标准 UPI (User-Provisioned Infrastructure)**  
  需手动配置网络、负载均衡、DNS 和节点（通过 PXE 或 ISO 引导）。
- **单节点 OpenShift (SNO)**  
  单个节点运行控制平面和工作负载，适用于边缘或测试环境。

#### **(2) 本地虚拟化环境**
- **OpenShift on KVM/libvirt**  
  通过 `libvirt` 驱动在本地 KVM 虚拟机上部署（需手动配置存储和网络）。
- **CRC (CodeReady Containers)**  
  开发者本地单节点 OpenShift（仅限开发/测试，非生产环境）。

---

### **2. 支持的 Linux 发行版**
OpenShift Installer **本身** 可以在以下 Linux 发行版上运行（用于执行安装命令）：
| 发行版          | 支持版本               | 备注                                                                 |
|-----------------|------------------------|----------------------------------------------------------------------|
| **Red Hat Enterprise Linux (RHEL)** | 7.9+, 8.x, 9.x | 官方推荐，兼容性最佳                                                |
| **CentOS**      | 7.9+, 8.x (Stream)     | 需自行解决依赖（部分功能可能受限）                                   |
| **Fedora**      | 34+                    | 适合开发测试，但需注意版本兼容性                                    |
| **Ubuntu**      | 20.04 LTS, 22.04 LTS   | 需手动安装依赖（如 `libvirt`、`qemu`）                              |

---

### **3. 节点操作系统要求**
OpenShift **集群节点**（Master/Worker）必须使用以下操作系统：
- **RHCOS (Red Hat CoreOS)**  
  官方默认，由 OpenShift Installer 自动部署（通过 Ignition 文件配置）。
- **RHEL 8/9**  
  需满足：
    - 最小化安装（无 GUI）。
    - 禁用 SELinux 或配置为 `permissive` 模式。
    - 安装特定依赖包（如 `openshift-sdn`、`kubelet`）。

> 📌 **注意**：
> - 不支持其他发行版（如 Ubuntu、Debian、SUSE）作为集群节点。
> - 若需在非 RHCOS/RHEL 节点运行，需手动解决兼容性问题（非官方支持）。

---

### **4. 本地安装前提条件**
#### **(1) 硬件要求**
- **控制平面节点**：4 CPU / 16GB RAM / 100GB 存储
- **工作节点**：2 CPU / 8GB RAM / 50GB 存储
- **网络**：静态 IP、DNS 解析、负载均衡器（如 HAProxy）。

#### **(2) 软件依赖**
- **OpenShift Installer**：从 [Red Hat 镜像站](https://mirror.openshift.com/) 下载。
- **Podman/Docker**：用于运行本地镜像仓库（离线安装时）。
- **libvirt/qemu**（可选）：本地虚拟化部署时需安装。

---

### **5. 安装流程示例（裸金属 UPI）**
#### **步骤 1：准备安装配置**
```bash
# 生成 install-config.yaml
openshift-install create install-config --dir=ocp-cluster
```
编辑 `install-config.yaml`：
```yaml
apiVersion: v1
baseDomain: example.com
compute:
- name: worker
  replicas: 2
controlPlane:
  name: master
  replicas: 3
metadata:
  name: ocp-cluster
platform:
  baremetal: {}
pullSecret: '{"auths": ...}'
sshKey: 'ssh-rsa ...'
```

#### **步骤 2：生成 Ignition 文件**
```bash
openshift-install create ignition-configs --dir=ocp-cluster
```
输出文件：
- `bootstrap.ign`、`master.ign`、`worker.ign`

#### **步骤 3：手动部署节点**
- 通过 PXE 或 ISO 引导节点，加载 Ignition 文件。
- 配置负载均衡器指向控制平面节点。

---

### **6. 常见问题**
#### **Q：能否在 Ubuntu/Debian 上运行集群节点？**
- **否**。OpenShift 仅官方支持 RHCOS 或 RHEL 作为节点 OS。

#### **Q：本地安装需要 Red Hat 订阅吗？**
- **是**。需有效的 Red Hat 订阅下载 Installer 和镜像。

#### **Q：如何简化本地开发测试？**
- 使用 **CRC (CodeReady Containers)**：
  ```bash
  crc setup
  crc start --pull-secret-file=pull-secret.json
  ```

---

### **7. 参考文档**
- [官方裸金属安装指南](https://docs.openshift.com/container-platform/latest/installing/installing_bare_metal/installing-bare-metal.html)
- [CRC 快速入门](https://developers.redhat.com/products/codeready-containers)

如需在生产环境部署，建议使用 RHEL 作为安装主机，并遵循 Red Hat 官方最佳实践。


---

以下是一个在 **本地机器** 上安装 **Red Hat CoreOS (RHCOS)** 和 **OpenShift Container Platform (OCP)** 的详细手把手教程。我们将使用 **裸金属 (Bare Metal) UPI (User-Provisioned Infrastructure)** 方式，适用于物理机或本地虚拟机（如 KVM/libvirt）。

---

## **前提条件**
1. **硬件要求**：
    - 至少 **3 台机器**（1 Bootstrap + 3 Master/Control Plane，可选 2 Worker）。
    - 每台机器配置：
        - **4 CPU** / **16GB RAM** / **100GB 存储**（Master）。
        - **2 CPU** / **8GB RAM** / **50GB 存储**（Worker）。
    - 本地网络（静态 IP、DNS、负载均衡器）。

2. **软件要求**：
    - 一台 **Linux 管理机**（RHEL 8/9 或 Ubuntu 20.04+）。
    - 有效的 **Red Hat 订阅**（下载 OpenShift Installer 和 Pull Secret）。
    - `openshift-install` 和 `oc` 客户端工具。

---

## **步骤 1：准备环境**
### 1.1 下载 OpenShift Installer
```bash
# 在管理机上下载 openshift-install 和 oc
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-linux.tar.gz
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz

# 解压
tar -xvf openshift-install-linux.tar.gz
tar -xvf openshift-client-linux.tar.gz

# 移动到 PATH
sudo mv openshift-install oc kubectl /usr/local/bin/
```

### 1.2 获取 Pull Secret
1. 登录 [Red Hat OpenShift Cluster Manager](https://cloud.redhat.com/openshift/install)。
2. 下载 **Pull Secret**（保存为 `pull-secret.json`）。

---

## **步骤 2：生成安装配置**
### 2.1 创建 `install-config.yaml`
```bash
mkdir ocp-install && cd ocp-install
openshift-install create install-config --dir=.
```
编辑生成的 `install-config.yaml`：
```yaml
apiVersion: v1
baseDomain: example.com          # 替换为你的域名
compute:
- name: worker
  replicas: 2                   # Worker 节点数量
controlPlane:
  name: master
  replicas: 3                   # Master 节点数量
metadata:
  name: ocp-cluster             # 集群名称
platform:
  baremetal: {}                 # 裸金属安装
pullSecret: '{"auths": ...}'    # 粘贴你的 pull-secret
sshKey: 'ssh-rsa AAA...'        # 你的 SSH 公钥
```

### 2.2 生成 Ignition 配置文件
```bash
openshift-install create ignition-configs --dir=.
```
生成的文件：
- `bootstrap.ign`（引导节点）
- `master.ign`（Master 节点）
- `worker.ign`（Worker 节点）

---

## **步骤 3：部署 RHCOS 节点**
### 3.1 下载 RHCOS ISO 和 RAW 镜像
```bash
# 获取最新 RHCOS 镜像
openshift-install coreos print-stream-json | grep location
# 下载 ISO（用于 PXE 引导）
wget https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/latest/latest/rhcos-live.x86_64.iso
```

### 3.2 启动 Bootstrap 节点
1. 使用 `rhcos-live.x86_64.iso` 启动机器。
2. 在启动参数中添加：
   ```
   coreos.inst.install_dev=/dev/sda coreos.inst.ignition_url=http://<管理机IP>/bootstrap.ign
   ```
3. 等待 Bootstrap 启动完成（约 10 分钟）。

### 3.3 启动 Master 节点
1. 使用相同的 ISO 启动 3 台 Master 机器。
2. 在启动参数中替换为 `master.ign`：
   ```
   coreos.inst.install_dev=/dev/sda coreos.inst.ignition_url=http://<管理机IP>/master.ign
   ```

### 3.4 启动 Worker 节点（可选）
1. 使用相同的 ISO 启动 Worker 机器。
2. 在启动参数中替换为 `worker.ign`：
   ```
   coreos.inst.install_dev=/dev/sda coreos.inst.ignition_url=http://<管理机IP>/worker.ign
   ```

---

## **步骤 4：配置负载均衡和 DNS**
### 4.1 配置 HAProxy（在管理机上）
```bash
sudo dnf install haproxy -y
```
编辑 `/etc/haproxy/haproxy.cfg`：
```ini
frontend openshift-api
    bind *:6443
    default_backend openshift-api
backend openshift-api
    server bootstrap <bootstrapIP>:6443 check
    server master1 <master1IP>:6443 check
    server master2 <master2IP>:6443 check
    server master3 <master3IP>:6443 check

frontend openshift-ingress
    bind *:80
    bind *:443
    default_backend openshift-ingress
backend openshift-ingress
    server worker1 <worker1IP>:80 check
    server worker2 <worker2IP>:80 check
```
重启 HAProxy：
```bash
sudo systemctl restart haproxy
```

### 4.2 配置 DNS（示例：`/etc/hosts`）
```
<bootstrapIP> bootstrap.ocp-cluster.example.com
<master1IP> master1.ocp-cluster.example.com
<master2IP> master2.ocp-cluster.example.com
<master3IP> master3.ocp-cluster.example.com
<worker1IP> worker1.ocp-cluster.example.com
```

---

## **步骤 5：完成安装**
### 5.1 监控 Bootstrap 进度
```bash
openshift-install wait-for bootstrap-complete --dir=. --log-level=info
```
输出 `"Bootstrap complete!"` 后，关闭 Bootstrap 节点。

### 5.2 等待集群就绪
```bash
export KUBECONFIG=auth/kubeconfig
oc get nodes                 # 查看节点状态
openshift-install wait-for install-complete --dir=.
```
完成后会输出管理员凭据（`kubeadmin` 密码）。

---

## **步骤 6：访问 OpenShift 控制台**
1. 获取控制台 URL：
   ```bash
   oc whoami --show-console
   ```
2. 使用 `kubeadmin` 和输出的密码登录。

---

## **验证集群**
```bash
oc get clusterversion         # 查看 OpenShift 版本
oc get pods -A               # 检查所有 Pod 状态
oc get csr                   # 批准未处理的 CSR
```

---

## **常见问题**
1. **Bootstrap 超时**：
    - 检查 HAProxy 和 DNS 配置。
    - 确保 Ignition 文件可通过 HTTP 访问。
2. **Master 节点未就绪**：
    - 检查 `journalctl -u bootkube` 日志。
3. **证书问题**：
    - 确保时间同步（NTP）。

---

## **总结**
通过此教程，你已在本地机器上成功部署了 **Red Hat CoreOS** 和 **OpenShift**。如需进一步优化：
- 配置持久化存储（如 NFS、Ceph）。
- 部署应用（通过 `oc new-app` 或 Operator Hub）。

> 📌 **注意**：生产环境建议使用 Red Hat 官方支持的硬件和网络架构。

---

# 以下是 **两台机器** 部署 OpenShift 的简化方案（适用于测试/开发环境），使用 **单节点 OpenShift (SNO)** 或 **紧凑型集群 (Compact Cluster)** 架构：

---

### **方案选择**
| **架构**               | **机器数量** | **适用场景**                     | **资源要求**                     |
|------------------------|-------------|----------------------------------|----------------------------------|
| **单节点 OpenShift (SNO)** | 1 台        | 开发/测试，边缘计算              | 8 CPU / 32GB RAM / 120GB 存储    |
| **紧凑型集群 (Compact)**  | 2 台        | 高可用性测试环境                 | 每台 4 CPU / 16GB RAM / 100GB 存储 |

---

## **方案 1：单节点 OpenShift (SNO)**
**仅需 1 台机器**，合并控制平面和工作负载。

### **步骤 1：准备环境**
1. **机器配置**：
    - 8 CPU / 32GB RAM / 120GB 存储
    - 静态 IP、主机名（如 `sno.example.com`）

2. **下载工具**：
   ```bash
   wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-linux.tar.gz
   tar -xvf openshift-install-linux.tar.gz
   sudo mv openshift-install /usr/local/bin/
   ```

### **步骤 2：生成 SNO 配置**
```bash
mkdir sno-install && cd sno-install
cat <<EOF > install-config.yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: sno-cluster
compute:
- name: worker
  replicas: 0                  # 禁用独立 Worker 节点
controlPlane:
  name: master
  replicas: 1                  # 单节点模式
platform:
  baremetal:
    apiVIP: 192.168.1.100      # 虚拟 IP（与机器 IP 不同）
    ingressVIP: 192.168.1.101
pullSecret: '{"auths": ...}'   # 替换为你的 pull-secret
sshKey: 'ssh-rsa AAA...'       # 替换为你的 SSH 公钥
EOF
```

### **步骤 3：部署单节点**
```bash
openshift-install create single-node-ignition-config --dir=.
# 将生成的 bootstrap-in-place-for-live-iso.ign 写入 USB 或 PXE 引导
```

### **步骤 4：启动机器**
1. 使用 RHCOS Live ISO 启动。
2. 在启动参数中添加：
   ```
   coreos.inst.install_dev=/dev/sda coreos.inst.ignition_url=http://<管理机IP>/bootstrap-in-place-for-live-iso.ign
   ```
3. 等待约 30 分钟，检查状态：
   ```bash
   export KUBECONFIG=auth/kubeconfig
   oc get nodes  # 应显示 1 个 Ready 节点
   ```

---

## **方案 2：两节点紧凑型集群**
**2 台机器**：1 台 Combined Control Plane + Worker，1 台 Worker。

### **步骤 1：准备环境**
- **机器 1** (Master + Worker): 4 CPU / 16GB RAM / 100GB 存储
- **机器 2** (Worker): 4 CPU / 8GB RAM / 50GB 存储
- 共享存储（如 NFS）用于镜像仓库

### **步骤 2：生成安装配置**
```bash
mkdir compact-install && cd compact-install
cat <<EOF > install-config.yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: compact-cluster
compute:
- name: worker
  replicas: 1                  # 1 个独立 Worker
controlPlane:
  name: master
  replicas: 1                  # 1 个 Combined 节点
platform:
  baremetal: {}
pullSecret: '{"auths": ...}'
sshKey: 'ssh-rsa AAA...'
EOF
```

### **步骤 3：部署集群**
```bash
openshift-install create ignition-configs --dir=.
# 为机器 1（Master）使用 master.ign
# 为机器 2（Worker）使用 worker.ign
```

### **步骤 4：手动批准 CSR**
由于节点少，需手动批准证书：
```bash
oc get csr -o name | xargs oc adm certificate approve
```

---

## **关键注意事项**
1. **网络要求**：
    - 确保两台机器在同一子网。
    - 如果无负载均衡器，需在 `/etc/hosts` 中手动解析主机名。

2. **存储**：
    - SNO 默认使用本地存储（需额外配置持久化卷）。
    - 紧凑集群建议配置 NFS 或 Ceph。

3. **资源限制**：
    - SNO 最低要求 8 CPU / 32GB RAM（低于此规格可能失败）。
    - 紧凑集群中 Combined 节点负载较高。

---

## **验证安装**
```bash
oc get nodes                 # 检查节点状态
oc get clusterversion        # 查看集群版本
oc logs -n openshift-ingress-operator deployments/ingress-operator  # 检查 Ingress
```

---

## **扩展建议**
- **持久化存储**：
  ```bash
  oc create -f https://raw.githubusercontent.com/openshift/openshift-docs/main/modules/nfs-provisioner.adoc
  ```
- **监控**：
    - 访问 Prometheus 控制台（`oc get route prometheus-k8s -n openshift-monitoring`）。

---

## **总结**
| **场景**       | **推荐方案**       | **优点**                     | **缺点**               |
|----------------|--------------------|------------------------------|------------------------|
| 开发/边缘      | 单节点 OpenShift   | 资源占用低，部署简单         | 无高可用               |
| 测试高可用     | 两节点紧凑集群     | 模拟生产环境                 | 需手动负载均衡         |

选择方案后，根据实际需求调整资源配置和存储方案。


---

以下是基于 **Vagrant** 虚拟机在本地部署 **单节点 OpenShift (SNO)** 或 **两节点紧凑集群** 的完整手把手教程，适用于开发/测试环境。

---

## **方案选择**
| **架构**               | **虚拟机数量** | **资源分配**               | **适用场景**         |
|------------------------|---------------|----------------------------|----------------------|
| **单节点 OpenShift (SNO)** | 1 台          | 8 CPU / 32GB RAM / 120GB   | 本地开发、功能测试   |
| **两节点紧凑集群**       | 2 台          | 控制平面: 4C/16GB, Worker: 4C/8GB | 学习多节点管理      |

---

# **手把手教程：基于 Vagrant 的 OpenShift 部署**

## **1. 环境准备**
### **1.1 安装依赖工具**
```bash
# 安装 Vagrant 和 Libvirt (Linux)
sudo apt-get install -y vagrant libvirt-daemon libvirt-dev qemu-kvm
vagrant plugin install vagrant-libvirt

# 安装 VirtualBox (Mac/Windows 备用)
# 下载地址: https://www.virtualbox.org/wiki/Downloads

# 安装 OpenShift 客户端 (oc 和 openshift-install)
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-linux.tar.gz
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz
tar -xvf openshift-install-linux.tar.gz
tar -xvf openshift-client-linux.tar.gz
sudo mv openshift-install oc kubectl /usr/local/bin/
```

### **1.2 获取 Pull Secret**
登录 [Red Hat OpenShift Cluster Manager](https://cloud.redhat.com/openshift/install)，下载 `pull-secret.json`。

---

## **2. 单节点 OpenShift (SNO) 部署**
### **2.1 创建 Vagrantfile**
```bash
mkdir openshift-sno && cd openshift-sno
cat <<EOF > Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.define "sno" do |node|
    node.vm.box = "generic/rhel9"  # 使用 RHEL 9 基础镜像
    node.vm.hostname = "sno"
    node.vm.network "private_network", ip: "192.168.56.10"  # 静态 IP
    node.vm.provider "libvirt" do |v|
      v.memory = 32768  # 32GB RAM
      v.cpus = 8        # 8 CPU
      v.storage :file, size: "120G"  # 120GB 磁盘
    end
  end
end
EOF
```

### **2.2 启动虚拟机**
```bash
vagrant up
vagrant ssh sno  # 登录虚拟机
```

### **2.3 在虚拟机内安装 OpenShift**
```bash
# 在虚拟机内执行
sudo dnf install -y git jq
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-linux.tar.gz
tar -xvf openshift-install-linux.tar.gz
sudo mv openshift-install /usr/local/bin/

# 生成 SNO 配置
mkdir sno-install && cd sno-install
cat <<EOF > install-config.yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: sno-cluster
compute:
- name: worker
  replicas: 0
controlPlane:
  name: master
  replicas: 1
platform:
  baremetal:
    apiVIP: 192.168.56.10  # 使用虚拟机 IP
    ingressVIP: 192.168.56.10
pullSecret: '$(cat /path/to/pull-secret.json | jq -c)'  # 替换路径
sshKey: '$(cat ~/.ssh/id_rsa.pub)'  # 替换为你的 SSH 公钥
EOF

# 生成 Ignition 配置
openshift-install create single-node-ignition-config --dir=.

# 安装 RHCOS
sudo coreos-installer install /dev/sda --ignition-file bootstrap-in-place-for-live-iso.ign
sudo reboot
```

### **2.4 验证安装**
```bash
# 从宿主机访问
export KUBECONFIG=sno-install/auth/kubeconfig
oc get nodes  # 应显示 1 个节点
oc get clusterversion
```

---

## **3. 两节点紧凑集群部署**
### **3.1 创建 Vagrantfile**
```bash
mkdir openshift-compact && cd openshift-compact
cat <<EOF > Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.define "master" do |node|
    node.vm.box = "generic/rhel9"
    node.vm.hostname = "master"
    node.vm.network "private_network", ip: "192.168.56.10"
    node.vm.provider "libvirt" do |v|
      v.memory = 16384  # 16GB RAM
      v.cpus = 4        # 4 CPU
      v.storage :file, size: "100G"
    end
  end

  config.vm.define "worker" do |node|
    node.vm.box = "generic/rhel9"
    node.vm.hostname = "worker"
    node.vm.network "private_network", ip: "192.168.56.11"
    node.vm.provider "libvirt" do |v|
      v.memory = 8192   # 8GB RAM
      v.cpus = 4        # 4 CPU
      v.storage :file, size: "50G"
    end
  end
end
EOF
```

### **3.2 启动虚拟机**
```bash
vagrant up
```

### **3.3 配置负载均衡 (HAProxy)**
在宿主机或虚拟机内安装 HAProxy：
```bash
# 在宿主机执行
sudo dnf install -y haproxy
cat <<EOF | sudo tee /etc/haproxy/haproxy.cfg
frontend openshift-api
    bind *:6443
    default_backend openshift-api
backend openshift-api
    server master 192.168.56.10:6443 check

frontend openshift-ingress
    bind *:80
    bind *:443
    default_backend openshift-ingress
backend openshift-ingress
    server worker 192.168.56.11:80 check
EOF
sudo systemctl restart haproxy
```

### **3.4 生成安装配置**
```bash
# 在宿主机执行
mkdir compact-install && cd compact-install
cat <<EOF > install-config.yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: compact-cluster
compute:
- name: worker
  replicas: 1
controlPlane:
  name: master
  replicas: 1
platform:
  baremetal:
    apiVIP: 192.168.56.10
    ingressVIP: 192.168.56.10
pullSecret: '$(cat /path/to/pull-secret.json | jq -c)'
sshKey: '$(cat ~/.ssh/id_rsa.pub)'
EOF

# 生成 Ignition 文件
openshift-install create ignition-configs --dir=.
```

### **3.5 部署节点**
```bash
# 将 ignition 文件复制到虚拟机
vagrant upload master.ign master:/tmp/
vagrant upload worker.ign worker:/tmp/

# 在每个虚拟机内执行
sudo coreos-installer install /dev/sda --ignition-file /tmp/master.ign  # master
sudo coreos-installer install /dev/sda --ignition-file /tmp/worker.ign  # worker
sudo reboot
```

### **3.6 验证集群**
```bash
export KUBECONFIG=compact-install/auth/kubeconfig
oc get nodes                 # 应显示 2 个节点
oc get pods -A               # 检查所有 Pod 状态
```

---

## **4. 访问 OpenShift 控制台**
```bash
oc get routes -n openshift-console
# 访问 https://console-openshift-console.apps.<cluster-name>.<base-domain>
# 用户名: kubeadmin, 密码: compact-install/auth/kubeadmin-password
```

---

## **关键问题解决**
1. **证书未批准**：
   ```bash
   oc get csr -o name | xargs oc adm certificate approve
   ```
2. **资源不足**：
    - 调整 Vagrantfile 中的 CPU/RAM 或减少集群组件（如禁用监控）。
3. **网络问题**：
    - 确保虚拟机 IP 和 HAProxy 配置一致。

---

## **总结**
| **场景**       | **Vagrant 方案**      | **命令摘要**                     |
|----------------|-----------------------|----------------------------------|
| 单节点开发     | SNO                   | `openshift-install create single-node-ignition-config` |
| 多节点学习     | 两节点紧凑集群        | 手动配置 HAProxy + Ignition 文件 |

通过 Vagrant 可快速搭建 OpenShift 测试环境，适合验证功能或学习 Kubernetes 高级特性。生产环境请使用官方支持的硬件和网络架构。


---

以下是专为 **macOS 平台** 调整的 **Vagrant 部署 OpenShift 手把手教程**，支持单节点 (SNO) 或两节点紧凑集群，使用 VirtualBox 作为虚拟机驱动。

---

## **方案选择**
| **架构**               | **虚拟机数量** | **资源分配**               | **适用场景**         |
|------------------------|---------------|----------------------------|----------------------|
| **单节点 OpenShift (SNO)** | 1 台          | 8 CPU / 32GB RAM / 120GB   | 本地开发、功能测试   |
| **两节点紧凑集群**       | 2 台          | 控制平面: 4C/16GB, Worker: 4C/8GB | 学习多节点管理      |

---

# **macOS 上的 OpenShift 部署教程**
### **1. 环境准备**
#### **1.1 安装依赖工具**
```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Vagrant 和 VirtualBox
brew install vagrant virtualbox

# 安装 OpenShift 客户端 (oc 和 openshift-install)
brew install openshift-cli
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-mac.tar.gz
tar -xvf openshift-install-mac.tar.gz
sudo mv openshift-install /usr/local/bin/
```

#### **1.2 获取 Pull Secret**
登录 [Red Hat OpenShift Cluster Manager](https://cloud.redhat.com/openshift/install)，下载 `pull-secret.json` 并保存到 `~/Downloads/pull-secret.json`。

---

## **2. 单节点 OpenShift (SNO) 部署**
### **2.1 创建 Vagrantfile**
```bash
mkdir openshift-sno && cd openshift-sno
cat <<EOF > Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.define "sno" do |node|
    node.vm.box = "fedora/38-cloud-base"  # 轻量级基础镜像
    node.vm.hostname = "sno"
    node.vm.network "private_network", ip: "192.168.56.10"
    node.vm.provider "virtualbox" do |v|
      v.memory = 32768  # 32GB RAM
      v.cpus = 8        # 8 CPU
      v.customize ["modifyvm", :id, "--ioapic", "on"]  # 必须启用 IOAPIC
      v.customize ["createhd", "--filename", "sno-disk.vdi", "--size", 120 * 1024]  # 120GB 磁盘
      v.customize ["storageattach", :id, "--storagectl", "SATA Controller", "--port", 1, "--device", 0, "--type", "hdd", "--medium", "sno-disk.vdi"]
    end
  end
end
EOF
```

### **2.2 启动虚拟机**
```bash
vagrant up
vagrant ssh sno  # 登录虚拟机
```

### **2.3 在虚拟机内安装 OpenShift**
```bash
# 在虚拟机内执行
sudo dnf install -y git jq
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-linux.tar.gz
tar -xvf openshift-install-linux.tar.gz
sudo mv openshift-install /usr/local/bin/

# 生成 SNO 配置
mkdir sno-install && cd sno-install
cat <<EOF > install-config.yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: sno-cluster
compute:
- name: worker
  replicas: 0
controlPlane:
  name: master
  replicas: 1
platform:
  baremetal:
    apiVIP: 192.168.56.10  # 使用虚拟机 IP
    ingressVIP: 192.168.56.10
pullSecret: '$(cat /vagrant/pull-secret.json | jq -c)'  # 从宿主机共享文件
sshKey: '$(cat /vagrant/.ssh/id_rsa.pub)'  # 假设已提前放置公钥
EOF

# 生成 Ignition 配置
openshift-install create single-node-ignition-config --dir=.

# 安装 RHCOS（模拟）
sudo coreos-installer install /dev/sda --ignition-file bootstrap-in-place-for-live-iso.ign
sudo reboot
```

### **2.4 验证安装**
```bash
# 从宿主机访问
export KUBECONFIG=sno-install/auth/kubeconfig
oc get nodes  # 应显示 1 个节点
```

---

## **3. 两节点紧凑集群部署**
### **3.1 创建 Vagrantfile**
```bash
mkdir openshift-compact && cd openshift-compact
cat <<EOF > Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.define "master" do |node|
    node.vm.box = "fedora/38-cloud-base"
    node.vm.hostname = "master"
    node.vm.network "private_network", ip: "192.168.56.10"
    node.vm.provider "virtualbox" do |v|
      v.memory = 16384  # 16GB RAM
      v.cpus = 4        # 4 CPU
      v.customize ["createhd", "--filename", "master-disk.vdi", "--size", 100 * 1024]  # 100GB 磁盘
      v.customize ["storageattach", :id, "--storagectl", "SATA Controller", "--port", 1, "--device", 0, "--type", "hdd", "--medium", "master-disk.vdi"]
    end
  end

  config.vm.define "worker" do |node|
    node.vm.box = "fedora/38-cloud-base"
    node.vm.hostname = "worker"
    node.vm.network "private_network", ip: "192.168.56.11"
    node.vm.provider "virtualbox" do |v|
      v.memory = 8192   # 8GB RAM
      v.cpus = 4        # 4 CPU
      v.customize ["createhd", "--filename", "worker-disk.vdi", "--size", 50 * 1024]  # 50GB 磁盘
      v.customize ["storageattach", :id, "--storagectl", "SATA Controller", "--port", 1, "--device", 0, "--type", "hdd", "--medium", "worker-disk.vdi"]
    end
  end
end
EOF
```

### **3.2 启动虚拟机**
```bash
vagrant up
```

### **3.3 配置负载均衡 (HAProxy)**
在宿主机（Mac）上运行 HAProxy：
```bash
# 安装 HAProxy
brew install haproxy

# 配置 HAProxy
cat <<EOF | sudo tee /usr/local/etc/haproxy.cfg
frontend openshift-api
    bind *:6443
    default_backend openshift-api
backend openshift-api
    server master 192.168.56.10:6443 check

frontend openshift-ingress
    bind *:80
    bind *:443
    default_backend openshift-ingress
backend openshift-ingress
    server worker 192.168.56.11:80 check
EOF

# 启动 HAProxy
sudo haproxy -f /usr/local/etc/haproxy.cfg
```

### **3.4 生成安装配置**
```bash
# 在宿主机执行
mkdir compact-install && cd compact-install
cat <<EOF > install-config.yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: compact-cluster
compute:
- name: worker
  replicas: 1
controlPlane:
  name: master
  replicas: 1
platform:
  baremetal:
    apiVIP: 192.168.56.10
    ingressVIP: 192.168.56.10
pullSecret: '$(cat ~/Downloads/pull-secret.json | jq -c)'
sshKey: '$(cat ~/.ssh/id_rsa.pub)'
EOF

# 生成 Ignition 文件
openshift-install create ignition-configs --dir=.
```

### **3.5 部署节点**
```bash
# 将 ignition 文件复制到虚拟机
vagrant upload master.ign master:/tmp/
vagrant upload worker.ign worker:/tmp/

# 在每个虚拟机内执行
sudo coreos-installer install /dev/sda --ignition-file /tmp/master.ign  # master
sudo coreos-installer install /dev/sda --ignition-file /tmp/worker.ign  # worker
sudo reboot
```

### **3.6 验证集群**
```bash
export KUBECONFIG=compact-install/auth/kubeconfig
oc get nodes                 # 应显示 2 个节点
oc get pods -A               # 检查所有 Pod 状态
```

---

## **4. 访问 OpenShift 控制台**
```bash
oc get routes -n openshift-console
# 在浏览器访问: https://console-openshift-console.apps.<cluster-name>.example.com
# 用户名: kubeadmin, 密码: compact-install/auth/kubeadmin-password
```

---

## **macOS 专属优化**
1. **VirtualBox 网络配置**：
    - 确保 `192.168.56.0/24` 网段在 VirtualBox 全局设置中未被占用。
    - 在 **VirtualBox 管理界面** -> **偏好设置** -> **网络** 中添加 `Host-only Network`。

2. **性能调优**：
    - 关闭 macOS 的 Spotlight 索引（避免磁盘 IO 竞争）：
      ```bash
      sudo mdutil -a -i off
      ```
    - 为 VirtualBox 分配更多 CPU 资源（通过 GUI 设置）。

3. **SSH 密钥转发**：
   ```bash
   vagrant ssh-config > ssh-config
   ssh -F ssh-config master  # 直接登录
   ```

---

## **常见问题解决**
1. **虚拟机启动失败**：
    - 确保 VirtualBox 和 Vagrant 版本最新：
      ```bash
      brew upgrade virtualbox vagrant
      ```
2. **Ignition 文件无法访问**：
    - 使用 `vagrant upload` 或共享文件夹：
      ```ruby
      config.vm.synced_folder ".", "/vagrant", disabled: false
      ```
3. **资源不足错误**：
    - 减少 OpenShift 组件资源请求：
      ```bash
      oc edit clusterversion version  # 调整资源限制
      ```

---

## **总结**
| **场景**       | **推荐方案**      | **关键命令**                          |
|----------------|-------------------|---------------------------------------|
| 快速开发测试   | 单节点 (SNO)      | `openshift-install create single-node-ignition-config` |
| 学习多节点管理 | 两节点紧凑集群    | 手动配置 HAProxy + Ignition 文件       |

通过 Vagrant 在 macOS 上部署 OpenShift，可以高效模拟生产环境，适合开发和学习。生产环境请使用官方支持的硬件平台。


---

以下是针对 **192.168.0.0/24** 网段调整后的 **macOS + Vagrant + VirtualBox 部署 OpenShift** 教程（单节点 SNO 或两节点集群），确保所有 IP 配置与您的本地网络兼容。

---

## **调整要点**
1. **虚拟机 IP 范围**：改为 `192.168.0.100-192.168.0.200`（避免与现有设备冲突）。
2. **VIP (Virtual IP)**：使用 `192.168.0.150`（API）和 `192.168.0.151`（Ingress）。
3. **负载均衡器配置**：绑定到宿主机（Mac）的 `192.168.0.x` 地址。

---

# **教程开始**
## **1. 环境准备**
### **1.1 安装工具（Mac）**
```bash
# 安装 Homebrew、Vagrant、VirtualBox
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install vagrant virtualbox

# 安装 OpenShift 客户端
brew install openshift-cli
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-mac.tar.gz
tar -xvf openshift-install-mac.tar.gz
sudo mv openshift-install /usr/local/bin/
```

### **1.2 配置 VirtualBox 网络**
1. 打开 **VirtualBox** -> **偏好设置** -> **网络** -> **Host-only Networks**。
2. 创建一个新网卡（如 `vboxnet0`），配置如下：
    - **IPv4 地址**: `192.168.0.1`
    - **子网掩码**: `255.255.255.0`
    - 取消勾选 **DHCP 服务器**（手动分配 IP）。

---

## **2. 单节点 OpenShift (SNO) 部署**
### **2.1 创建 Vagrantfile**
```bash
mkdir openshift-sno && cd openshift-sno
cat <<EOF > Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.define "sno" do |node|
    node.vm.box = "fedora/38-cloud-base"
    node.vm.hostname = "sno"
    node.vm.network "private_network", ip: "192.168.0.100"  # 静态 IP
    node.vm.provider "virtualbox" do |v|
      v.memory = 32768  # 32GB RAM
      v.cpus = 8        # 8 CPU
      v.customize ["modifyvm", :id, "--ioapic", "on"]
      v.customize ["createhd", "--filename", "sno-disk.vdi", "--size", 120 * 1024]  # 120GB 磁盘
      v.customize ["storageattach", :id, "--storagectl", "SATA Controller", "--port", 1, "--device", 0, "--type", "hdd", "--medium", "sno-disk.vdi"]
    end
  end
end
EOF
```

### **2.2 生成安装配置**
```bash
# 生成 install-config.yaml
cat <<EOF > install-config.yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: sno-cluster
compute:
- name: worker
  replicas: 0
controlPlane:
  name: master
  replicas: 1
platform:
  baremetal:
    apiVIP: "192.168.0.150"  # 虚拟 IP（与虚拟机 IP 不同）
    ingressVIP: "192.168.0.151"
pullSecret: '$(cat ~/Downloads/pull-secret.json | jq -c)'
sshKey: '$(cat ~/.ssh/id_rsa.pub)'
EOF

# 生成 Ignition 配置
openshift-install create single-node-ignition-config --dir=.
```

### **2.3 启动虚拟机并安装**
```bash
vagrant up
vagrant ssh sno -- sudo coreos-installer install /dev/sda --ignition-file /vagrant/bootstrap-in-place-for-live-iso.ign
vagrant reload sno  # 重启虚拟机
```

### **2.4 验证安装**
```bash
export KUBECONFIG=auth/kubeconfig
oc get nodes  # 应显示 1 个节点
```

---

## **3. 两节点紧凑集群部署**
### **3.1 创建 Vagrantfile**
```bash
mkdir openshift-compact && cd openshift-compact
cat <<EOF > Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.define "master" do |node|
    node.vm.box = "fedora/38-cloud-base"
    node.vm.hostname = "master"
    node.vm.network "private_network", ip: "192.168.0.100"
    node.vm.provider "virtualbox" do |v|
      v.memory = 16384  # 16GB RAM
      v.cpus = 4        # 4 CPU
      v.customize ["createhd", "--filename", "master-disk.vdi", "--size", 100 * 1024]  # 100GB 磁盘
      v.customize ["storageattach", :id, "--storagectl", "SATA Controller", "--port", 1, "--device", 0, "--type", "hdd", "--medium", "master-disk.vdi"]
    end
  end

  config.vm.define "worker" do |node|
    node.vm.box = "fedora/38-cloud-base"
    node.vm.hostname = "worker"
    node.vm.network "private_network", ip: "192.168.0.101"
    node.vm.provider "virtualbox" do |v|
      v.memory = 8192   # 8GB RAM
      v.cpus = 4        # 4 CPU
      v.customize ["createhd", "--filename", "worker-disk.vdi", "--size", 50 * 1024]  # 50GB 磁盘
      v.customize ["storageattach", :id, "--storagectl", "SATA Controller", "--port", 1, "--device", 0, "--type", "hdd", "--medium", "worker-disk.vdi"]
    end
  end
end
EOF
```

### **3.2 配置负载均衡（Mac 宿主机）**
```bash
# 安装并配置 HAProxy
brew install haproxy
cat <<EOF | sudo tee /usr/local/etc/haproxy.cfg
frontend openshift-api
    bind 192.168.0.1:6443  # 宿主机 IP
    default_backend openshift-api
backend openshift-api
    server master 192.168.0.100:6443 check

frontend openshift-ingress
    bind 192.168.0.1:80
    bind 192.168.0.1:443
    default_backend openshift-ingress
backend openshift-ingress
    server worker 192.168.0.101:80 check
EOF

# 启动 HAProxy
sudo haproxy -f /usr/local/etc/haproxy.cfg
```

### **3.3 生成安装配置**
```bash
cat <<EOF > install-config.yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: compact-cluster
compute:
- name: worker
  replicas: 1
controlPlane:
  name: master
  replicas: 1
platform:
  baremetal:
    apiVIP: "192.168.0.150"  # 虚拟 IP
    ingressVIP: "192.168.0.151"
pullSecret: '$(cat ~/Downloads/pull-secret.json | jq -c)'
sshKey: '$(cat ~/.ssh/id_rsa.pub)'
EOF

openshift-install create ignition-configs --dir=.
```

### **3.4 部署节点**
```bash
vagrant up
vagrant ssh master -- sudo coreos-installer install /dev/sda --ignition-file /vagrant/master.ign
vagrant ssh worker -- sudo coreos-installer install /dev/sda --ignition-file /vagrant/worker.ign
vagrant reload master worker
```

### **3.5 验证集群**
```bash
export KUBECONFIG=auth/kubeconfig
oc get nodes                 # 应显示 2 个节点
oc get clusteroperators      # 检查所有 Operator 状态
```

---

## **4. 访问 OpenShift 控制台**
1. 在 Mac 的 `/etc/hosts` 中添加解析：
   ```bash
   # 编辑 hosts 文件
   sudo sh -c 'echo "192.168.0.150 console-openshift-console.apps.example.com" >> /etc/hosts'
   sudo sh -c 'echo "192.168.0.151 oauth-openshift.apps.example.com" >> /etc/hosts'
   ```
2. 浏览器访问：
    - **控制台**: https://console-openshift-console.apps.example.com
    - **用户名**: `kubeadmin`
    - **密码**: `cat auth/kubeadmin-password`

---

## **关键调整总结**
| **配置项**       | **原值**         | **调整为**       | **原因**                     |
|------------------|------------------|------------------|------------------------------|
| 虚拟机 IP        | 192.168.56.x    | 192.168.0.100+   | 匹配您的本地网络             |
| VIP (API/Ingress)| 192.168.56.10   | 192.168.0.150/151 | 避免冲突且易记忆            |
| HAProxy 绑定 IP  | 任意            | 192.168.0.1      | 宿主机在 192.168.0.x 网段   |

---

## **故障排查**
1. **虚拟机无法通信**：
    - 检查 VirtualBox 的 `vboxnet0` 配置是否与宿主机同网段。
    - 禁用 Mac 防火墙：`sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off`。
2. **Ignition 文件失效**：
    - 确保文件通过 `vagrant upload` 或共享文件夹 (`/vagrant`) 传递。
3. **证书错误**：
    - 手动批准 CSR：
      ```bash
      oc get csr -o name | xargs oc adm certificate approve
      ```

---

通过以上调整，您可以在 **192.168.0.0/24** 网段中顺利部署 OpenShift。如果需要进一步简化，可以使用 [CodeReady Containers (CRC)](https://developers.redhat.com/products/codeready-containers) 快速启动单节点集群。


---

以下是针对 **ARM 架构 Mac（如 M1/M2 芯片）** 的 OpenShift 部署方案调整说明：

---

### **关键结论**
1. **原生支持有限**：  
   OpenShift 官方仅正式支持 x86_64 架构，**不原生支持 ARM 架构的 Mac**（如 M1/M2）。
2. **替代方案**：
    - **使用 x86 模拟器**（如 Rosetta 2 + VirtualBox）运行 x86 虚拟机（性能较低）。
    - **等待官方支持**：Red Hat 已开始测试 OpenShift 对 ARM 的支持，但尚未正式发布。

---

## **可行方案（基于 ARM Mac）**
### **方案 1：使用 CodeReady Containers (CRC)**
**适用场景**：快速本地开发测试（单节点 OpenShift）  
**优势**：唯一官方支持的轻量级方案（需 Rosetta 2 转译）。

#### **步骤**
1. **安装依赖**：
   ```bash
   # 安装 Rosetta 2（如果未安装）
   softwareupdate --install-rosetta

   # 安装 CRC 和 Podman
   brew install crc podman
   ```

2. **下载 CRC（x86 版本）**：
   ```bash
   # 下载 x86 版 CRC（通过 Rosetta 运行）
   wget https://developers.redhat.com/content-gateway/file/pub/openshift-v4/clients/crc/latest/crc-macos-amd64.tar.xz
   tar -xvf crc-macos-amd64.tar.xz
   sudo mv crc-macos-amd64/crc /usr/local/bin/
   ```

3. **启动 CRC**：
   ```bash
   crc setup
   crc start --pull-secret-file=pull-secret.json  # 使用从 Red Hat 下载的 pull-secret
   ```

4. **访问集群**：
   ```bash
   eval $(crc oc-env)
   oc get nodes  # 应显示 1 个节点
   ```

---

### **方案 2：使用 x86 虚拟机（UTM/QEMU）**
**适用场景**：需要多节点测试（性能较差）  
**工具**：UTM（Mac 上的 QEMU 前端）模拟 x86 环境。

#### **步骤**
1. **安装 UTM**：
   ```bash
   brew install --cask utm
   ```

2. **创建 x86 虚拟机**：
    - 在 UTM 中新建虚拟机，选择 **x86_64** 架构。
    - 安装 RHEL 8/9 x86 镜像（需 Red Hat 订阅）。

3. **在虚拟机内部署 OpenShift**：
    - 参考 [x86 部署教程](#)，但需注意：
        - 虚拟机性能较低（建议分配 8 CPU / 32GB RAM）。
        - 仅适合功能验证，不适用于生产。

---

### **方案 3：等待官方 ARM 支持**
- **当前进展**：  
  Red Hat 已开始测试 OpenShift 对 ARM64（如 AWS Graviton）的支持，但尚未覆盖 Mac M1/M2。
- **跟踪动态**：  
  关注 [OpenShift 官方博客](https://www.openshift.com/blog) 或 [GitHub 问题](https://github.com/openshift/installer/issues/5163)。

---

## **不支持的场景**
1. **直接运行 OpenShift Installer**：  
   `openshift-install` 无 ARM 原生版本，无法直接在 M1/M2 上运行。
2. **Vagrant + VirtualBox**：  
   VirtualBox 不支持 ARM Mac，需改用 UTM 或 Parallels（仅商业版支持）。

---

## **性能对比**
| **方案**          | **兼容性** | **性能** | **复杂度** | **适用场景**       |
|--------------------|------------|----------|------------|--------------------|
| **CRC (Rosetta 2)** | ✅         | ⭐⭐      | 低         | 开发测试           |
| **UTM x86 虚拟机** | ✅         | ⭐        | 高         | 功能验证           |
| **原生 ARM 支持**  | ❌         | ⭐⭐⭐⭐    | -          | 未来生产环境       |

---

## **总结建议**
- **短期方案**：  
  使用 **CRC**（通过 Rosetta 2）快速测试 OpenShift 功能。
- **长期方案**：  
  等待 Red Hat 官方发布 ARM 版 OpenShift，或使用 AWS Graviton 实例（如已订阅 ROSA）。