# OpenShift Disconnected Cluster

## AWS Directory Disconnected Cluster Related Scripts Summary

### 1. **VPC Configuration - `aws-provision-vpc-disconnected`**

**Location**: `step-registry/aws/provision/vpc/disconnected/`

**Purpose**: Create dedicated VPC network environment for disconnected cluster

**Key Features**:
- Create independent VPC supporting 1-3 availability zones
- Configure public and private subnets
- Set up Internet Gateway and NAT Gateway
- Configure route tables and network ACLs
- Optimize network configuration for disconnected environments

**Key Configuration**:
```yaml
ref:
  as: aws-provision-vpc-disconnected
  from_image:
    namespace: ocp
    name: "4.12"
    tag: upi-installer
  env:
  - name: ZONES_COUNT
    default: "3"
```

### 2. **IAM User Configuration - `aws-provision-cco-manual-users-static`**

**Location**: `step-registry/aws/provision/cco-manual-users/static/`

**Purpose**: Create static AWS IAM users and permissions for disconnected cluster

**Main Functions**:
- Extract CredentialsRequest from OpenShift release image
- Create corresponding IAM policies for each CredentialsRequest
- Create IAM users with minimum permissions
- Generate Kubernetes Secret manifest files
- Support filtering for TechPreview features

**Key Features**:
```yaml
ref:
  as: aws-provision-cco-manual-users-static
  documentation: |-
    Create static AWS IAM users for disconnected cluster.
```

### 3. **Core Script Function Analysis**

#### **VPC Creation Script** (`aws-provision-vpc-disconnected-commands.sh`):
- Create VPC using CloudFormation template
- Configure multi-availability zone support
- Set network labels and expiration time
- Output key information like VPC ID, subnet IDs

#### **IAM User Creation Script** (`aws-provision-cco-manual-users-static-commands.sh`):
- Use `oc adm release extract` to extract credential requests
- Dynamically generate IAM policy documents
- Create AWS IAM users and access keys
- Generate Kubernetes Secret YAML files
- Support mirror registry authentication configuration

### 4. **Special Considerations for Disconnected Cluster**

**Network Isolation**:
- VPC configuration optimized for disconnected environments
- Support private subnet configuration
- Configurable NAT Gateway for limited internet access

**Image Registry**:
- Support mirror registry configuration
- Handle pull secret and authentication
- Configure ImageContentSourcePolicy

**Permission Management**:
- Principle of least privilege
- Static IAM users instead of dynamic creation
- Support CCO (Cloud Credential Operator) manual mode

### 5. **Integration with Other Components**

These scripts typically work with other disconnected-related components:
- **Image Synchronization**: Use `oc-mirror` tool to sync images to local registry
- **Catalog Source**: Configure local operator catalog
- **Registry Configuration**: Set up mirror policies for image registry
- **Network Configuration**: Configure DNS and routing

### 6. **Use Cases**

These scripts are mainly used for:
- **CI/CD Environments**: Test OpenShift in isolated AWS environments
- **Offline Deployment**: Deploy OpenShift in environments without internet access
- **Security Compliance**: Meet enterprise security policy requirements
- **Performance Testing**: Conduct performance benchmarks in controlled environments

These configuration files and scripts provide a complete automated solution for deploying disconnected OpenShift clusters on AWS, covering key aspects like networking, permissions, and image synchronization.

---

CCO Meaning

**CCO** is the abbreviation for **Cloud Credential Operator**, which is a core component in OpenShift.

### 1. **Role of Cloud Credential Operator (CCO)**

CCO is the Operator in OpenShift responsible for managing cloud platform credentials. Its main functions include:

- **Credential Management**: Manage credentials required by various OpenShift cluster components to access cloud platforms
- **Permission Control**: Ensure each component only gets the minimum permissions it needs
- **Security Policy**: Implement security best practices for cloud platform access

### 2. **CCO Working Modes**

CCO supports multiple working modes:

#### **Mint Mode** (Default)
- CCO automatically creates and manages cloud platform credentials
- Dynamically creates IAM users/service accounts
- Suitable for environments with sufficient permissions

#### **Manual Mode**
- Administrator manually creates and manages credentials
- Uses pre-created IAM users/service accounts
- Suitable for permission-restricted or security-sensitive environments

#### **Passthrough Mode**
- Directly uses existing cloud platform credentials
- Does not perform any credential management

### 3. **Role of `cco-manual-users` Directory**

This directory is specifically for CCO configuration in **Manual Mode**:

#### **Main Functions**:
- **Extract CredentialsRequest**: Extract credential requests needed by various components from OpenShift release image
- **Create IAM Policies**: Automatically generate corresponding AWS IAM policies based on CredentialsRequest
- **Create IAM Users**: Create dedicated IAM users for each component
- **Generate Kubernetes Secret**: Create corresponding Kubernetes Secret manifest files

#### **Workflow**:
```bash
# 1. Extract CredentialsRequest from release image
oc adm release extract --credentials-requests --cloud=aws

# 2. Create IAM policies and users for each CredentialsRequest
# 3. Generate Kubernetes Secret YAML files
```

### 4. **Why Manual Mode is Needed?**

Manual mode is particularly important in the following scenarios:

- **Disconnected Environment**: Cannot dynamically create cloud resources during offline deployment
- **Security Compliance**: Enterprise security policies require manual credential management
- **Permission Limitations**: Cloud platform account permissions are insufficient to support Mint mode
- **Audit Requirements**: Need clear credential creation records

### 5. **Integration with Other Components**

CCO closely integrates with the following components:
- **ccoctl Tool**: CLI tool for generating cloud platform credentials
- **CredentialsRequest**: CRD that defines required permissions for components
- **Various Operators**: Such as image-registry, ingress, machine-api, etc.

### Summary

The scripts in the `cco-manual-users` directory are key components for OpenShift to automatically create and manage cloud platform credentials when deploying in Manual mode on AWS platform. It ensures that in disconnected or security-sensitive environments, OpenShift clusters can correctly obtain the permissions needed to access AWS services while following the principle of least privilege.

---

## Private Cluster vs Disconnected Cluster Installation Process Comparison

### 1. **Concept Definition**

#### **Private Cluster**
- **Network Level**: Cluster's API server and Ingress controller use private IP addresses
- **Access Method**: Access through VPN, jump host, or internal network
- **Internet Connection**: Usually has internet connection, but API server is not exposed externally

#### **Disconnected Cluster**
- **Network Level**: Completely isolated network environment, cannot access internet
- **Image Registry**: Requires local image registry to provide all container images
- **Software Packages**: All software packages and updates need to be pre-downloaded locally

### 2. **Main Differences in Installation Process**

#### **A. Network Configuration Differences**

**Private Cluster**:
```yaml
# install-config.yaml
publish: Internal  # Key configuration
platform:
  aws:
    privateLink: true  # Use private link
```

**Disconnected Cluster**:
```yaml
# install-config.yaml
publish: Internal  # Also uses internal publishing
# But needs additional mirror registry configuration
additionalTrustBundle: |
  -----BEGIN CERTIFICATE-----
  # Mirror registry CA certificate
  -----END CERTIFICATE-----
```

#### **B. Image Processing Methods**

**Private Cluster**:
- Pull images directly from internet
- Use standard pull secret
- No need to pre-prepare images

**Disconnected Cluster**:
- Need to pre-sync all images to local registry
- Use `oc-mirror` tool to sync images
- Configure ImageContentSourcePolicy to point to local registry

```bash
# Disconnected environment image synchronization
oc-mirror --config=imageset.yaml docker://local-registry:5000
```

#### **C. Installation Steps Comparison**

**Private Cluster Installation Flow**:
```yaml
steps:
  - ref: ipi-conf
  - ref: ipi-conf-private-dns  # Configure private DNS
  - ref: ipi-install-install
  - ref: ipi-install-registry  # Configure internal image registry
```

**Disconnected Cluster Installation Flow**:
```yaml
steps:
  - chain: vsphere-provision-bastionhost  # Need bastion host
  - ref: mirror-images-by-oc-adm-in-bastion  # Image synchronization
  - ref: ipi-conf-mirror  # Configure mirror registry
  - ref: ipi-install-install
  - ref: ipi-install-vsphere-registry
  - ref: enable-qe-catalogsource-disconnected  # Enable offline catalog
  - ref: mirror-images-tag-images  # Image tag processing
```

### 3. **Key Component Differences**

#### **A. Image Registry Configuration**

**Private Cluster**:
```yaml
# Use standard registry.redhat.io
imageContentSources:
- mirrors:
  - registry.redhat.io/openshift4/ose-kube-rbac-proxy
  source: registry.redhat.io/openshift4/ose-kube-rbac-proxy
```

**Disconnected Cluster**:
```yaml
# Use local mirror registry
imageContentSources:
- mirrors:
  - mirror-registry.example.com:5000/openshift4/ose-kube-rbac-proxy
  source: registry.redhat.io/openshift4/ose-kube-rbac-proxy
```

#### **B. CCO (Cloud Credential Operator) Configuration**

**Private Cluster**:
- Can use standard Mint mode
- Dynamically create cloud platform credentials

**Disconnected Cluster**:
- Must use Manual mode
- Pre-create static IAM users
- Use `cco-manual-users` script

#### **C. Catalog Source Configuration**

**Private Cluster**:
```yaml
# Use standard Red Hat catalog
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: redhat-operators
spec:
  image: registry.redhat.io/redhat/redhat-operator-index
```

**Disconnected Cluster**:
```yaml
# Use local catalog
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: redhat-operators
spec:
  image: mirror-registry.example.com:5000/redhat/redhat-operator-index
```

### 4. **Infrastructure Requirements**

#### **Private Cluster**:
- Private subnet configuration
- NAT Gateway (optional)
- Private DNS zone
- VPN or jump host access

#### **Disconnected Cluster**:
- Completely isolated network
- Local image registry (Registry)
- Bastion Host (Bastion Host)
- All pre-downloaded software packages
- Local certificate authority

### 5. **Maintenance and Updates**

#### **Private Cluster**:
- Can directly pull updates from internet
- Standard upgrade process
- Automatic image pulling

#### **Disconnected Cluster**:
- Need to pre-download all updates
- Manual image synchronization
- Offline upgrade process
- Need to maintain local software package repository

### 6. **Security Considerations**

#### **Private Cluster**:
- Network-level isolation
- API server not exposed externally
- Still requires internet connection

#### **Disconnected Cluster**:
- Complete network isolation
- No internet connection
- Higher security level
- Requires strict content validation

### Summary

**Private Cluster** mainly focuses on **network access control**, ensuring cluster API is not exposed externally, but still maintains internet connection to obtain images and updates.

**Disconnected Cluster** focuses on **complete network isolation**, requiring pre-preparation of all necessary images, software packages, and configurations, suitable for deployment in highly secure or completely isolated environments.

The main difference between the two is: Private Cluster is "network privatization", while Disconnected Cluster is "complete offline operation".

---

# OpenShift Cluster Installation Sequence Diagrams

This document contains UML sequence diagrams for OpenShift Private Cluster and Disconnected Cluster installation processes.

## 1. Private Cluster Installation Sequence

```mermaid
sequenceDiagram
    participant Admin as Administrator
    participant Installer as OpenShift Installer
    participant Cloud as Cloud Platform
    participant DNS as DNS Service
    participant Registry as Red Hat Registry
    participant Cluster as OpenShift Cluster

    Note over Admin,Cluster: Private Cluster Installation Process

    Admin->>Installer: 1. Create install-config.yaml<br/>(publish: Internal)
    Admin->>Installer: 2. Configure private networking
    Admin->>Installer: 3. Set pull secret

    Installer->>Cloud: 4. Create VPC with private subnets
    Cloud-->>Installer: VPC created

    Installer->>Cloud: 5. Create private DNS zone
    Cloud-->>Installer: Private DNS zone created

    Installer->>Cloud: 6. Create load balancers (internal)
    Cloud-->>Installer: Internal load balancers created

    Installer->>Cloud: 7. Create compute instances
    Cloud-->>Installer: Instances created

    Installer->>Registry: 8. Pull OpenShift images
    Registry-->>Installer: Images downloaded

    Installer->>Cluster: 9. Deploy control plane
    Cluster-->>Installer: Control plane ready

    Installer->>Cluster: 10. Deploy worker nodes
    Cluster-->>Installer: Worker nodes ready

    Installer->>DNS: 11. Configure private DNS records
    DNS-->>Installer: DNS records created

    Installer->>Cluster: 12. Configure internal registry
    Cluster-->>Installer: Internal registry ready

    Installer-->>Admin: 13. Installation complete<br/>(Private endpoints only)

    Note over Admin,Cluster: Cluster is accessible via VPN/Jump host
```

## 2. Disconnected Cluster Installation Sequence

```mermaid
sequenceDiagram
    participant Admin as Administrator
    participant Bastion as Bastion Host
    participant Mirror as Mirror Registry
    participant Installer as OpenShift Installer
    participant Cloud as Cloud Platform
    participant DNS as DNS Service
    participant Cluster as OpenShift Cluster
    participant CCO as Cloud Credential Operator

    Note over Admin,Cluster: Disconnected Cluster Installation Process

    Admin->>Bastion: 1. Provision bastion host<br/>(with internet access)
    Bastion-->>Admin: Bastion host ready

    Admin->>Bastion: 2. Install oc-mirror tool
    Bastion-->>Admin: oc-mirror installed

    Admin->>Bastion: 3. Create ImageSetConfiguration
    Bastion-->>Admin: Configuration created

    Admin->>Bastion: 4. Mirror OpenShift images<br/>to local registry
    Bastion->>Mirror: 4.1. Download images from Red Hat
    Mirror-->>Bastion: 4.2. Images stored locally
    Bastion-->>Admin: 4.3. Mirroring complete

    Admin->>Bastion: 5. Mirror operator catalogs
    Bastion->>Mirror: 5.1. Download operator catalogs
    Mirror-->>Bastion: 5.2. Catalogs stored locally
    Bastion-->>Admin: 5.3. Catalog mirroring complete

    Admin->>Installer: 6. Create install-config.yaml<br/>(with mirror registry config)
    Admin->>Installer: 7. Configure disconnected settings

    Installer->>Cloud: 8. Create VPC with private subnets
    Cloud-->>Installer: VPC created

    Installer->>Cloud: 9. Create private DNS zone
    Cloud-->>Installer: Private DNS zone created

    Installer->>Cloud: 10. Create load balancers (internal)
    Cloud-->>Installer: Internal load balancers created

    Installer->>Cloud: 11. Create compute instances
    Cloud-->>Installer: Instances created

    Installer->>Mirror: 12. Pull OpenShift images<br/>(from local mirror)
    Mirror-->>Installer: Images downloaded

    Installer->>Cluster: 13. Deploy control plane
    Cluster-->>Installer: Control plane ready

    Installer->>Cluster: 14. Deploy worker nodes
    Cluster-->>Installer: Worker nodes ready

    Installer->>DNS: 15. Configure private DNS records
    DNS-->>Installer: DNS records created

    Installer->>Cluster: 16. Configure internal registry
    Cluster-->>Installer: Internal registry ready

    Installer->>CCO: 17. Configure manual credentials<br/>(static IAM users)
    CCO-->>Installer: Credentials configured

    Installer->>Cluster: 18. Apply ImageContentSourcePolicy<br/>(point to mirror registry)
    Cluster-->>Installer: Image policy applied

    Installer->>Cluster: 19. Deploy local catalog sources
    Cluster-->>Installer: Local catalogs ready

    Installer-->>Admin: 20. Installation complete<br/>(Fully disconnected)

    Note over Admin,Cluster: Cluster operates completely offline
```

## 3. Key Differences Summary

| Aspect | Private Cluster | Disconnected Cluster |
|--------|----------------|---------------------|
| **Network Access** | Limited internet access | No internet access |
| **Image Source** | Red Hat registries | Local mirror registry |
| **Bastion Host** | Optional | Required |
| **Image Preparation** | None required | Pre-mirroring required |
| **CCO Mode** | Mint/Manual | Manual only |
| **Catalog Sources** | Standard Red Hat | Local mirrored |
| **Update Process** | Direct from internet | Manual mirroring |
| **Security Level** | Network isolation | Complete isolation |

## 4. Installation Prerequisites

### Private Cluster Prerequisites
- Cloud platform credentials
- Private network configuration
- DNS zone (private)
- Pull secret for Red Hat registries

### Disconnected Cluster Prerequisites
- Bastion host with internet access
- Local mirror registry
- Pre-mirrored OpenShift images
- Pre-mirrored operator catalogs
- Static cloud credentials (IAM users)
- Local certificate authority
- Complete software package repository

## 5. Post-Installation Considerations

### Private Cluster
- Configure VPN or jump host access
- Set up monitoring and logging
- Configure backup strategies
- Plan for updates and upgrades

### Disconnected Cluster
- Establish image update procedures
- Set up local package management
- Configure offline monitoring
- Plan for offline upgrades
- Maintain local security patches 

---

You're right! The sequence diagram indeed doesn't fully demonstrate the specific usage process of CCO in Disconnected Cluster. Let me explain in detail the key role of CCO in Disconnected Cluster installation:

## CCO Usage Process in Disconnected Cluster

### 1. **CCO Mode Configuration**
In Disconnected Cluster, CCO must use **Manual mode** because:
- Cluster cannot access internet to dynamically create cloud platform credentials
- Requires pre-created static IAM users/service accounts

### 2. **Specific Usage Steps**

#### **Step 1: Extract CredentialsRequest**
```bash
# Extract credential requests from OpenShift release image
oc adm release extract --credentials-requests --cloud=aws ${RELEASE_IMAGE}
```

#### **Step 2: Create Static IAM Users**
```bash
# Create corresponding IAM policies and users for each CredentialsRequest
# For example: openshift-image-registry-installer-cloud-credentials
# For example: openshift-ingress-operator-cloud-credentials
```

#### **Step 3: Generate Kubernetes Secret**
```yaml
# Generate corresponding Secret for each component
apiVersion: v1
kind: Secret
metadata:
  name: installer-cloud-credentials
  namespace: openshift-image-registry
data:
  aws_access_key_id: <base64-encoded-key>
  aws_secret_access_key: <base64-encoded-secret>
```

#### **Step 4: Apply Credential Configuration**
```bash
# Apply these Secrets during cluster installation
oc apply -f manifests/
```

### 3. **Missing Parts of CCO in Sequence Diagram**

In the Disconnected Cluster sequence diagram, the following should be shown in more detail:

```mermaid
sequenceDiagram
    participant Admin as Administrator
    participant CCO as Cloud Credential Operator
    participant AWS as AWS IAM
    participant Cluster as OpenShift Cluster

    Admin->>CCO: 1. Extract CredentialsRequest from release image
    CCO-->>Admin: CredentialsRequest manifests
    
    Admin->>AWS: 2. Create IAM policies for each component
    AWS-->>Admin: IAM policies created
    
    Admin->>AWS: 3. Create IAM users with minimal permissions
    AWS-->>Admin: IAM users created
    
    Admin->>CCO: 4. Generate Kubernetes Secret manifests
    CCO-->>Admin: Secret manifests ready
    
    Admin->>Cluster: 5. Apply Secret manifests during installation
    Cluster-->>Admin: Secrets applied
    
    Note over Admin,Cluster: CCO operates in Manual mode
```

### 4. **Key Differences of CCO**

| Aspect | Private Cluster | Disconnected Cluster |
|------|----------------|---------------------|
| **CCO Mode** | Mint/Manual | Manual only |
| **Credential Creation** | Dynamic creation | Static pre-creation |
| **Permission Management** | Automatic management | Manual management |
| **Internet Dependency** | Requires IAM API access | No internet access required |

### 5. **Why Disconnected Cluster Needs Manual Mode**

1. **Network Isolation**: Cluster cannot access AWS IAM API
2. **Security Requirements**: Enterprise security policies require manual credential management
3. **Audit Requirements**: Need clear credential creation records
4. **Permission Control**: Ensure principle of least privilege

### 6. **CCO Configuration Example**

```yaml
# install-config.yaml
credentialsMode: Manual  # Force Manual mode

# Example IAM policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeRegions"
      ],
      "Resource": "*"
    }
  ]
}
```

You're right, the sequence diagram indeed doesn't fully demonstrate the specific workflow of CCO. In actual Disconnected Cluster installation, CCO's Manual mode configuration is a critical step that requires pre-preparation of all necessary cloud platform credentials, rather than relying on dynamic creation.

---

Let me output the mermaid content containing the detailed CCO steps for the Disconnected Cluster installation sequence diagram:

```mermaid
sequenceDiagram
    participant Admin as Administrator
    participant Bastion as Bastion Host
    participant Mirror as Mirror Registry
    participant Installer as OpenShift Installer
    participant Cloud as Cloud Platform
    participant DNS as DNS Service
    participant Cluster as OpenShift Cluster
    participant CCO as Cloud Credential Operator
    participant IAM as AWS IAM

    Note over Admin,Cluster: Disconnected Cluster Installation Process

    Admin->>Bastion: 1. Provision bastion host<br/>(with internet access)
    Bastion-->>Admin: Bastion host ready

    Admin->>Bastion: 2. Install oc-mirror tool
    Bastion-->>Admin: oc-mirror installed

    Admin->>Bastion: 3. Create ImageSetConfiguration
    Bastion-->>Admin: Configuration created

    Admin->>Bastion: 4. Mirror OpenShift images<br/>to local registry
    Bastion->>Mirror: 4.1. Download images from Red Hat
    Mirror-->>Bastion: 4.2. Images stored locally
    Bastion-->>Admin: 4.3. Mirroring complete

    Admin->>Bastion: 5. Mirror operator catalogs
    Bastion->>Mirror: 5.1. Download operator catalogs
    Mirror-->>Bastion: 5.2. Catalogs stored locally
    Bastion-->>Admin: 5.3. Catalog mirroring complete

    Admin->>CCO: 6. Extract CredentialsRequest<br/>from release image
    CCO-->>Admin: CredentialsRequest manifests

    Admin->>IAM: 7. Create IAM policies<br/>for each component
    IAM-->>Admin: IAM policies created

    Admin->>IAM: 8. Create IAM users<br/>with minimal permissions
    IAM-->>Admin: IAM users created

    Admin->>CCO: 9. Generate Kubernetes<br/>Secret manifests
    CCO-->>Admin: Secret manifests ready

    Admin->>Installer: 10. Create install-config.yaml<br/>(with mirror registry config)
    Admin->>Installer: 11. Configure disconnected settings<br/>(credentialsMode: Manual)

    Installer->>Cloud: 12. Create VPC with private subnets
    Cloud-->>Installer: VPC created

    Installer->>Cloud: 13. Create private DNS zone
    Cloud-->>Installer: Private DNS zone created

    Installer->>Cloud: 14. Create load balancers (internal)
    Cloud-->>Installer: Internal load balancers created

    Installer->>Cloud: 15. Create compute instances
    Cloud-->>Installer: Instances created

    Installer->>Mirror: 16. Pull OpenShift images<br/>(from local mirror)
    Mirror-->>Installer: Images downloaded

    Installer->>Cluster: 17. Deploy control plane
    Cluster-->>Installer: Control plane ready

    Installer->>Cluster: 18. Deploy worker nodes
    Cluster-->>Installer: Worker nodes ready

    Installer->>DNS: 19. Configure private DNS records
    DNS-->>Installer: DNS records created

    Installer->>Cluster: 20. Configure internal registry
    Cluster-->>Installer: Internal registry ready

    Installer->>Cluster: 21. Apply Secret manifests<br/>(static IAM credentials)
    Cluster-->>Installer: Secrets applied

    Installer->>Cluster: 22. Apply ImageContentSourcePolicy<br/>(point to mirror registry)
    Cluster-->>Installer: Image policy applied

    Installer->>Cluster: 23. Deploy local catalog sources
    Cluster-->>Installer: Local catalogs ready

    Installer->>Cluster: 24. Configure CCO in Manual mode
    Cluster-->>Installer: CCO configured

    Installer-->>Admin: 25. Installation complete<br/>(Fully disconnected)

    Note over Admin,Cluster: Cluster operates completely offline<br/>with static cloud credentials
```

This updated sequence diagram includes the complete workflow of CCO in Disconnected Cluster installation:

1. **Steps 6-9**: Shows the CCO credential preparation process
    - Extract CredentialsRequest
    - Create IAM policies and users
    - Generate Kubernetes Secret manifests

2. **Step 11**: Explicitly configure credentialsMode as Manual

3. **Step 21**: Apply static credential Secrets

4. **Step 24**: Configure CCO in Manual mode

This more completely demonstrates the key role and usage of CCO in the Disconnected Cluster installation process.

---

This is a great question! Although Disconnected Cluster is completely offline, creating IAM users is still very important for the following reasons:

## Why Disconnected Cluster Still Needs IAM Users

### 1. **Cloud Platform Resource Management**
Even if the cluster is offline, it still needs to manage cloud platform resources:
- **Storage Volumes**: EBS volume creation, deletion, snapshots
- **Load Balancers**: Internal load balancer management
- **Network Resources**: Security groups, routing tables, etc.
- **Image Registry**: If using cloud platform container registry

### 2. **OpenShift Components Require Cloud Platform Access**

#### **Image Registry Operator**
```yaml
# Need to access S3 buckets to store images
apiVersion: v1
kind: Secret
metadata:
  name: installer-cloud-credentials
  namespace: openshift-image-registry
data:
  aws_access_key_id: <base64-encoded>
  aws_secret_access_key: <base64-encoded>
```

#### **Ingress Operator**
```yaml
# Need to manage AWS load balancers
apiVersion: v1
kind: Secret
metadata:
  name: cloud-credentials
  namespace: openshift-ingress-operator
```

#### **Machine API Operator**
```yaml
# Need to manage EC2 instances (when scaling)
apiVersion: v1
kind: Secret
metadata:
  name: aws-cloud-credentials
  namespace: openshift-machine-api
```

### 3. **The Real Meaning of "Disconnected"**

Disconnected Cluster's "disconnected" refers to:
- **No internet access** (pulling images, software packages)
- **No external services access** (Red Hat services, update servers)

But **does not** refer to:
- No access to cloud platform API
- No management of cloud platform resources

### 4. **Actual Usage Scenarios**

```bash
# During cluster operation, these operations still require cloud platform access:

# 1. Create new persistent volumes
oc create -f pvc.yaml  # Need to create EBS volumes

# 2. Scale nodes
oc scale machineset/worker-0 --replicas=3  # Need to create EC2 instances

# 3. Configure load balancers
oc create route edge myapp  # Need to create ALB/NLB

# 4. Store images to cloud registry
podman push image to AWS ECR  # Need to access ECR
```

### 5. **Principle of Least Privilege**

IAM users only get **minimum necessary permissions**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeRegions",
        "ec2:CreateVolume",
        "ec2:DeleteVolume",
        "elasticloadbalancing:DescribeLoadBalancers"
      ],
      "Resource": "*"
    }
  ]
}
```

### 6. **Differences from Private Cluster**

| Aspect | Private Cluster | Disconnected Cluster |
|------|----------------|---------------------|
| **Internet Access** | Yes (pull images) | No |
| **Cloud Platform Access** | Yes (dynamic creation) | Yes (static users) |
| **CCO Mode** | Mint/Manual | Manual only |
| **Credential Management** | Automatic/Manual | Completely manual |

### 7. **Summary**

Disconnected Cluster's "disconnected" is **network-level isolation**, not **cloud platform-level isolation**. The cluster still needs to:
- Manage cloud platform resources
- Access cloud platform API
- Use cloud platform services

Therefore, IAM users are required, only the creation method changes from dynamic to static, from automatic to manual. This ensures that in a completely network-isolated environment, the cluster can still properly manage its cloud platform resources.