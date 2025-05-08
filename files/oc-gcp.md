# 简明教程：在 GCP 上安装 OpenShift Container Platform 4.18

以下是基于 Red Hat OpenShift Container Platform 4.18 文档的简明教程，指导如何在 Google Cloud Platform (GCP) 上安装 OpenShift 集群（从 GCP 环境到 GCP 环境）。教程涵盖主要步骤，简化复杂细节，适合初次部署的用户。内容参考了官方文档，并确保清晰、简洁。


本教程指导您在 Google Cloud Platform (GCP) 上使用安装程序提供的架构（installer-provisioned infrastructure）部署 OpenShift Container Platform 4.18 集群。教程假设您有基本的 GCP 和 Linux 命令行知识。

## 前提条件
1. **GCP 账户和权限**：
    - 拥有 GCP 账户，并具备创建项目和分配 IAM 角色的权限。
    - 确保账户启用了计费。
2. **工具准备**：
    - 安装 `openshift-install`（从 [OpenShift Cluster Manager](https://console.redhat.com/openshift) 下载）。
    - 安装 `gcloud` CLI（用于管理 GCP 资源）。
    - 安装 `oc` CLI（用于与 OpenShift 交互）。
3. **网络要求**：
    - 确保您的防火墙允许 OpenShift 所需的站点访问（参考文档中的站点列表）。
    - GCP 项目需使用 **Premium Network Service Tier**，因为安装程序不支持 Standard Tier。

## 步骤 1：配置 GCP 项目
1. **创建 GCP 项目**：
    - 登录 GCP 控制台，创建一个新项目（参考 GCP 文档：*Creating and Managing Projects*）。
    - 记下项目 ID（例如 `my-openshift-project`）。
2. **启用所需 API**：
    - 在 GCP 控制台中，启用以下 API 服务：
        - Compute Engine API
        - Cloud Resource Manager API
        - DNS API
        - IAM API
        - Service Usage API
        - 其他相关 API（参考文档中的完整列表）。
    - 命令行示例：
      ```bash
      gcloud services enable compute.googleapis.com
      gcloud services enable dns.googleapis.com
      gcloud services enable iam.googleapis.com
      gcloud services enable cloudresourcemanager.googleapis.com
      gcloud services enable serviceusage.googleapis.com
      ```
3. **创建服务账户**：
    - 创建一个服务账户并分配 `Owner` 角色（为简化安装，授予所有必需权限）。
    - 命令行示例：
      ```bash
      gcloud iam service-accounts create openshift-installer
      gcloud projects add-iam-policy-binding my-openshift-project \
        --member="serviceAccount:openshift-installer@my-openshift-project.iam.gserviceaccount.com" \
        --role="roles/owner"
      ```
    - 下载服务账户密钥（JSON 格式）：
      ```bash
      gcloud iam service-accounts keys create ~/openshift-installer-key.json \
        --iam-account=openshift-installer@my-openshift-project.iam.gserviceaccount.com
      ```
4. **配置 DNS**：
    - 在 GCP 中为您的集群创建一个公共托管区域（public hosted zone）。
    - 示例：为域名 `clusters.mydomain.com` 创建托管区域。
    - 更新您的域名注册商的 NS 记录，指向 GCP 的名称服务器（参考 GCP 文档：*Creating public zones*）。

## 步骤 2：准备安装配置
1. **生成安装配置文件**：
    - 运行 `openshift-install` 创建默认的 `install-config.yaml`：
      ```bash
      openshift-install create install-config --dir=my-cluster
      ```
    - 按照提示输入：
        - 集群名称（例如 `my-cluster`）。
        - 基础域名（例如 `clusters.mydomain.com`）。
        - GCP 项目 ID。
        - 区域（例如 `us-central1`）。
        - 其他默认选项可保留。
2. **（可选）自定义配置**：
    - 编辑 `my-cluster/install-config.yaml`，根据需要调整参数，例如：
        - `compute` 和 `controlPlane` 的机器类型（默认：`n1-standard-4`）。
        - 网络配置（VPC、子网、MTU 等）。
        - 示例（部分配置）：
          ```yaml
          apiVersion: v1
          baseDomain: clusters.mydomain.com
          compute:
          - architecture: amd64
            hyperthreading: Enabled
            name: worker
            platform:
              gcp:
                type: n1-standard-4
            replicas: 3
          controlPlane:
            architecture: amd64
            hyperthreading: Enabled
            name: master
            platform:
              gcp:
                type: n1-standard-4
            replicas: 3
          platform:
            gcp:
              projectID: my-openshift-project
              region: us-central1
          ```
    - 注意：保存后，备份此文件，安装程序会销毁原始文件。

## 步骤 3：执行安装
1. **生成 Kubernetes 清单和 Ignition 文件**：
    - 运行以下命令生成必要的安装文件：
      ```bash
      openshift-install create manifests --dir=my-cluster
      openshift-install create ignition-configs --dir=my-cluster
      ```
2. **启动集群安装**：
    - 确保服务账户密钥文件可用（例如 `~/openshift-installer-key.json`）。
    - 设置环境变量：
      ```bash
      export GOOGLE_APPLICATION_CREDENTIALS=~/openshift-installer-key.json
      ```
    - 运行安装命令：
      ```bash
      openshift-install create cluster --dir=my-cluster
      ```
    - 安装过程可能需要 30-60 分钟，期间会创建 VPC、负载均衡器、虚拟机等资源。
3. **监控安装进度**：
    - 查看日志输出，检查是否有错误。
    - 如果失败，检查日志文件（位于 `my-cluster` 目录）或运行：
      ```bash
      openshift-install gather bootstrap --dir=my-cluster
      ```

## 步骤 4：访问集群
1. **获取登录凭据**：
    - 安装完成后，`openshift-install` 会输出集群的访问信息，包括：
        - 控制台 URL（例如 `https://console-openshift-console.apps.my-cluster.clusters.mydomain.com`）。
        - `kubeadmin` 用户的密码（存储在 `my-cluster/auth/kubeadmin-password`）。
2. **登录集群**：
    - 使用 `oc` CLI 登录：
      ```bash
      oc login -u kubeadmin -p <password> https://api.my-cluster.clusters.mydomain.com:6443
      ```
    - 或者通过浏览器访问控制台 URL。
3. **验证集群状态**：
    - 检查节点状态：
      ```bash
      oc get nodes
      ```
    - 确保所有节点显示 `Ready`。

## 步骤 5：后续操作
1. **优化权限**：
    - 安装完成后，可减少服务账户的权限，从 `Owner` 替换为 `Viewer` 角色：
      ```bash
      gcloud projects remove-iam-policy-binding my-openshift-project \
        --member="serviceAccount:openshift-installer@my-openshift-project.iam.gserviceaccount.com" \
        --role="roles/owner"
      gcloud projects add-iam-policy-binding my-openshift-project \
        --member="serviceAccount:openshift-installer@my-openshift-project.iam.gserviceaccount.com" \
        --role="roles/viewer"
      ```
2. **配置防火墙**：
    - 确保防火墙规则允许集群所需的流量（参考文档中的站点和端口列表）。
3. **管理集群**：
    - 使用 OpenShift Cluster Manager 或 `oc` CLI 管理订阅、更新和扩展集群。

## 注意事项
- **互联网访问**：安装过程需要访问互联网以获取安装镜像和 GCP API。如果在受限网络中，需配置镜像注册表（参考文档：*Installing a cluster in a restricted network*）。
- **IAM 手动配置**：如果不希望将管理员级别的凭据存储在集群中，可手动创建 IAM 凭据（参考文档：*Manually creating IAM for GCP*）。
- **故障排除**：如果安装失败，检查 `my-cluster` 目录中的日志，或参考文档中的故障排除指南。

## 参考资源
- [OpenShift Container Platform 4.18 文档：Installing on GCP](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/installing_on_gcp/index)
- [GCP 文档：Creating and Managing Projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
- [OpenShift Cluster Manager](https://console.redhat.com/openshift)

