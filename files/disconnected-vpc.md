# Comparison of "Disconnected Cluster" and "Shared Network" Network Configurations

The following is a comparison of the "disconnected cluster" and "shared network" network configurations, based on the provided AWS CloudFormation templates and scripts, focusing on analyzing their differences in functionality, architecture, and usage scenarios:

---

### 1. **Overall Objectives and Use Cases**
- **Disconnected Cluster**:
    - Designed to provide network infrastructure for clusters in "disconnected" environments, typically used in high-security scenarios that require restricting external network access to private clusters.
    - Emphasizes providing access to AWS services (such as S3, EC2, EFS, ELB, STS) through VPC endpoints, avoiding direct public internet access.
    - Suitable for highly isolated private deployments, commonly found in government, financial institutions, or other environments with strict requirements for data sovereignty and network isolation.

- **Shared Network**:
    - Designed to support cross-AWS account sharing of VPC resources, allowing one account to create a VPC and share its subnets with other accounts through AWS Resource Access Manager (RAM).
    - Provides more flexible network configuration, supporting creation of only public subnets, additional subnets, and controlled internet access for private subnets through NAT gateways.
    - Suitable for multi-account architectures (such as enterprise-level AWS organizations), or scenarios requiring shared network resources across multiple teams/projects.

---

### 2. **主要功能差异**
| 特性                            | Disconnected Cluster                          | Shared Network                              |
|--------------------------------|-----------------------------------------------|--------------------------------------------|
| **VPC端点支持**                | 支持S3（Gateway类型）以及EC2、EFS、ELB、STS（Interface类型）的VPC端点，增强私有访问。 | 仅支持S3的VPC端点（Gateway类型）。           |
| **NAT网关**                    | 不支持NAT网关，私有子网无直接互联网访问。      | 支持NAT网关，私有子网可通过NAT访问互联网。   |
| **子网共享**                   | 不支持子网共享，所有资源在单一账户内。         | 支持通过AWS RAM共享子网给其他账户。         |
| **仅公共子网选项**             | 不支持，必须创建公共和私有子网。               | 支持仅创建公共子网（`OnlyPublicSubnets`）。  |
| **额外子网**                   | 不支持在同一AZ内创建额外子网。                 | 支持在同一AZ内创建额外公共/私有子网（`AdditionalSubnetsCount`）。 |
| **AZ选择灵活性**               | 自动选择AZ或基于默认配置。                    | 支持指定AZ列表（`AllowedAvailabilityZoneList`）。 |
| **账户管理**                   | 单一账户操作。                                | 支持双账户模式（创建者和共享账户）。        |

---

### 3. **网络架构差异**
#### **Disconnected Cluster**
- **子网结构**：
    - 每个AZ内创建一对公共子网和私有子网（最多3个AZ）。
    - 公共子网通过互联网网关（Internet Gateway）访问外部，私有子网无NAT网关，无法直接访问互联网。
    - 子网CIDR基于`!Cidr`函数分配，固定划分为6个块（3公共+3私有）。
- **路由**：
    - 公共子网关联到公共路由表，包含默认路由（0.0.0.0/0）指向互联网网关。
    - 私有子网关联到独立路由表，无默认路由，仅通过S3 VPC端点访问AWS服务。
- **VPC端点**：
    - S3端点（Gateway类型）连接到公共和私有路由表。
    - EC2、EFS、ELB、STS端点（Interface类型）部署在私有子网，使用安全组控制访问。
- **隔离性**：
    - 高度隔离，私有子网通过VPC端点访问AWS服务，无需公网。
    - 适合完全断连的集群，强调内部通信和受控的AWS服务访问。

#### **Shared Network**
- **Subnet Structure**:
    - Creates public subnets in each AZ, with private subnets optional (controlled by `OnlyPublicSubnets`).
    - Supports creating additional subnets within the same AZ (`AdditionalSubnetsCount`), increasing flexibility.
    - Subnet CIDR is divided into 8 blocks, allowing more granular subnet allocation.
- **Routing**:
    - Public subnets access external networks through internet gateway.
    - Private subnets access the internet through NAT gateways (deployed in corresponding public subnets), with each AZ's private subnet having independent NAT gateways and route tables.
- **VPC Endpoints**:
    - Only supports S3 endpoint (Gateway type), connected to public and private route tables.
    - No VPC endpoint support for other services (EC2, EFS, etc.).
- **Sharing**:
    - Shares subnets through AWS RAM (`ResourceShareSubnets`), allowing other AWS accounts to use VPC resources.
    - Supports cross-account resource management, suitable for multi-tenant or cost-sharing scenarios.

---

### 4. **Script Logic Differences**
- **Disconnected Cluster**:
    - Scripts focus on VPC creation and configuration within a single account.
    - Uses hardcoded parameters (such as `AvailabilityZoneCount`), passed directly through command line.
    - Outputs include VPC ID, subnet IDs, route table IDs, and AZ information, stored in shared directories.
    - No account switching or sharing logic.

- **Shared Network**:
    - Supports dual-account mode (`ENABLE_SHARED_VPC`), switching to shared account via `.awscred_shared_account`.
    - Dynamically generates parameter JSON (`vpc_params.json`), supporting flexible configuration (such as `OnlyPublicSubnets`, `AllowedAvailabilityZoneList`).
    - Additional outputs (`SubnetsByAz1/2/3`) provide subnet information organized by AZ, generating structured `vpc_info.json`.
    - Includes error checking (such as AZ list matching count).

---

### 5. **Output Differences**
- **Disconnected Cluster**:
    - Outputs include:
        - `VpcId`: VPC ID.
        - `PublicSubnetIds`: List of public subnet IDs.
        - `PrivateSubnetIds`: List of private subnet IDs.
        - `PublicRouteTableId`: Public route table ID.
        - `PrivateRouteTableIds`: Private route table IDs (organized by AZ).
        - `availability_zones`: AZ list.
    - Simple output format, focused on basic network resources.

- **Shared Network**:
    - Richer outputs, adding:
        - `AvailabilityZones`: AZ list.
        - `SubnetsByAz1/2/3`: Subnet information organized by AZ (public + private, including additional subnets).
        - `vpc_info.json`: Structured JSON containing VPC ID and subnet IDs organized by AZ (public/private).
    - Outputs support cross-account sharing and more complex subnet management.

---

### 6. **Applicable Scenario Comparison**
- **Disconnected Cluster**:
    - **Advantages**:
        - High isolation, suitable for disconnected environments.
        - Multiple VPC endpoint support, reducing dependency on public internet.
        - Simple configuration, suitable for single-account private clusters.
    - **Disadvantages**:
        - No NAT gateway, private subnets cannot access external resources (except through VPC endpoints).
        - No subnet sharing support, limited scalability.
    - **Applicable Scenarios**:
        - Private deployments (such as OpenShift on AWS in disconnected environments).
        - High security requirements (such as compliance requirements restricting public internet access).

- **Shared Network**:
    - **Advantages**:
        - Supports cross-account sharing, suitable for multi-team/project collaboration.
        - Flexible configuration (only public subnets, additional subnets, specified AZs).
        - NAT gateway support, private subnets can access internet in a controlled manner.
    - **Disadvantages**:
        - Only supports S3 endpoint, limited AWS service access.
        - Complex configuration, requires managing multi-account credentials and RAM sharing.
    - **Applicable Scenarios**:
        - Multi-account AWS architectures (such as enterprise-level AWS organizations).
        - Scenarios requiring shared network resources (such as development/testing environments).
        - Hybrid deployments requiring private subnet access to public internet.

---

### 7. **Summary**
- **Disconnected Cluster** focuses on highly isolated disconnected environments, providing AWS service access through VPC endpoints, suitable for security-sensitive private clusters, but lacks flexibility and scalability.
- **Shared Network** emphasizes cross-account sharing and flexible configuration, supporting NAT gateways and additional subnets, suitable for multi-tenant or internet-access scenarios, but with limited VPC endpoint support.
- **Selection Recommendations**:
    - If you need completely isolated private clusters, choose **Disconnected Cluster**.
    - If you need cross-account sharing or private subnet access to public internet, choose **Shared Network**.

For further analysis of specific configurations or optimization suggestions, please provide more context!

---

The following provides a detailed explanation of the specific configuration differences between the "disconnected cluster" and "shared network" network configurations in AWS CloudFormation templates and scripts, focusing on analyzing differences in template parameters, resource definitions, conditional logic, routing configuration, VPC endpoints, and script logic. The content will be as concise as possible and directly compare key points.

---

### 1. **模板参数差异**
| 参数                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **VpcCidr**                  | 默认10.0.0.0/16，支持/16-/24。               | 相同。                                     |
| **AvailabilityZoneCount**     | 1-3个AZ，默认1。                             | 相同。                                     |
| **SubnetBits**               | 子网大小/19-/27，默认/27。                   | 相同。                                     |
| **DhcpOptionSet**            | 支持自定义DNS（yes/no），默认no。             | 相同。                                     |
| **OnlyPublicSubnets**        | 不支持。                                     | 支持（yes/no），默认no，允许仅创建公共子网。 |
| **AllowedAvailabilityZoneList** | 不支持。                                     | 支持指定AZ列表（逗号分隔），默认空。        |
| **ResourceSharePrincipals**  | 不支持。                                     | 支持指定共享账户ARN，默认空，用于RAM共享。  |
| **AdditionalSubnetsCount**   | 不支持。                                     | 支持在同一AZ创建额外子网（0/1），默认0。    |

**Analysis**:
- **Shared Network** provides more parameters (`OnlyPublicSubnets`, `AllowedAvailabilityZoneList`, `ResourceSharePrincipals`, `AdditionalSubnetsCount`), supporting more flexible configurations such as public-only subnets, specified AZs, and subnet sharing.
- **Disconnected Cluster** has simpler parameters, focused on standard VPC configuration.

---

### 2. **子网配置差异**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **子网数量**                 | 每个AZ固定1公共+1私有子网，最多3AZ（6子网）。 | 每个AZ1公共+1私有（可选），支持额外子网，最多8子网。 |
| **CIDR分配**                 | VPC CIDR分为6块（3公共+3私有）。              | VPC CIDR分为8块，允许更多子网分配。         |
| **公共子网**                 | 固定创建，关联互联网网关。                    | 可选（`OnlyPublicSubnets`），支持`MapPublicIpOnLaunch`。 |
| **私有子网**                 | 固定创建，无NAT网关。                         | 可选（`DoAz1PrivateSubnet`等），支持NAT网关。 |
| **额外子网**                 | 不支持。                                     | 支持在AZ1创建额外公共/私有子网（`PublicSubnet1a`/`PrivateSubnet1a`）。 |
| **AZ选择**                   | 自动选择（`Fn::GetAZs`）。                    | 支持指定AZ（`AllowedAvailabilityZoneList`）。 |

**Analysis**:
- **Disconnected Cluster** has fixed subnet structure (6 CIDR blocks, 3 public + 3 private), no additional subnets or AZ specification, suitable for standardized deployments.
- **Shared Network** has more flexible subnet allocation (8 CIDR blocks), supports public-only subnets, additional subnets, and custom AZs, suitable for complex scenarios.

---

### 3. **路由配置差异**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **公共路由表**               | 1个，包含0.0.0.0/0指向互联网网关。            | 相同。                                     |
| **私有路由表**               | 每个AZ1个，无默认路由（0.0.0.0/0）。           | 每个AZ1个，包含0.0.0.0/0指向NAT网关（若私有子网存在）。 |
| **NAT网关**                  | 不支持，私有子网无互联网访问。                | 每个AZ的私有子网关联1个NAT网关（`NAT`/`NAT1a`/`NAT2`/`NAT3`）。 |
| **EIP**                      | 不支持。                                     | 每个NAT网关分配1个EIP（`EIP`/`EIP1a`/`EIP2`/`EIP3`）。 |

**Analysis**:
- **Disconnected Cluster** private subnets have no NAT gateway, rely on VPC endpoints to access AWS services, emphasizing isolation.
- **Shared Network** provides controlled internet access for private subnets through NAT gateways, suitable for scenarios requiring external connectivity.

---

### 4. **VPC端点配置差异**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **S3端点**                   | Gateway类型，关联公共和私有路由表。            | 相同。                                     |
| **其他端点**                 | Interface类型：EC2、EFS、ELB、STS，部署在私有子网，使用安全组控制。 | 不支持。                                   |
| **安全组**                   | 为Interface端点创建`EndpointSecurityGroup`，允许VPC CIDR内访问。 | 不支持（无Interface端点）。                |

**Analysis**:
- **Disconnected Cluster** supports multiple VPC endpoints (S3, EC2, EFS, ELB, STS), suitable for disconnected environments to access AWS services through private connections.
- **Shared Network** only supports S3 endpoint, relies on NAT gateway to access other services, lower isolation.

---

### 5. **条件逻辑差异**
| 条件                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **DoAz2/DoAz3**              | 控制第2/3 AZ子网创建。                        | 相同。                                     |
| **DoDhcp**                   | 控制DHCP选项集创建。                          | 相同。                                     |
| **DoOnlyPublicSubnets**      | 不支持。                                     | 控制是否仅创建公共子网。                   |
| **DoAz1PrivateSubnet**        | 不支持（私有子网固定）。                      | 控制AZ1私有子网创建。                      |
| **DoAz2/3PrivateSubnet**      | 不支持（私有子网固定）。                      | 控制AZ2/3私有子网创建。                    |
| **AzRestriction**            | 不支持。                                     | 控制是否使用指定AZ列表。                   |
| **ShareSubnets**             | 不支持。                                     | 控制是否创建RAM资源共享。                  |
| **DoAdditionalAz**           | 不支持。                                     | 控制AZ1额外子网创建。                      |

**Analysis**:
- **Shared Network** has more complex conditional logic, supports optional private subnets, specified AZs, and resource sharing, adapting to diverse requirements.
- **Disconnected Cluster** has simple conditional logic, focused on fixed subnets and VPC endpoint configuration.

---

### 6. **资源共享配置**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **AWS RAM共享**              | 不支持。                                     | 支持（`ResourceShareSubnets`），共享公共/私有子网给指定账户。 |
| **共享参数**                 | 无。                                         | `ResourceSharePrincipals`指定目标账户ARN。 |

**Analysis**:
- **Shared Network** supports cross-account subnet sharing through AWS RAM, suitable for multi-account architectures.
- **Disconnected Cluster** has no sharing mechanism, resources limited to single account.

---

### 7. **脚本逻辑差异**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **账户管理**                 | 单一账户（`AWS_SHARED_CREDENTIALS_FILE`）。    | 支持双账户（`ENABLE_SHARED_VPC`，切换到`.awscred_shared_account`）。 |
| **参数传递**                 | 硬编码（如`AvailabilityZoneCount`）。          | 动态生成`vpc_params.json`，支持多参数（如`OnlyPublicSubnets`、`AllowedAvailabilityZoneList`）。 |
| **错误检查**                 | 简单（如`ZONES_COUNT`上限3）。                 | 更严格（如AZ列表与`ZONES_COUNT`匹配）。     |
| **输出**                     | 基本输出（VPC ID、子网ID、路由表ID、AZ）。     | 额外输出`SubnetsByAz1/2/3`和`vpc_info.json`，结构化子网信息。 |
| **AZ查询**                   | 固定查询子网AZ。                              | 动态查询可用AZ，限制`MAX_ZONES_COUNT`。     |

**Analysis**:
- **Shared Network** scripts are more complex, support dual accounts, dynamic parameters, and detailed outputs, suitable for multi-tenant management.
- **Disconnected Cluster** scripts are simple, directly execute fixed configurations, suitable for single scenarios.

---

### 8. **输出差异**
| 输出                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **VpcId**                    | 相同。                                       | 相同。                                     |
| **PublicSubnetIds**          | 公共子网ID列表。                             | 相同，支持额外子网。                       |
| **PrivateSubnetIds**         | 私有子网ID列表。                             | 相同，可为空（仅公共子网）。               |
| **PublicRouteTableId**       | 公共路由表ID。                               | 相同。                                     |
| **PrivateRouteTableIds**     | 私有路由表ID（按AZ）。                       | 相同，可为空（无私有子网）。               |
| **AvailabilityZones**        | AZ列表。                                     | 相同，支持指定AZ。                         |
| **SubnetsByAz1/2/3**         | 不支持。                                     | 按AZ组织的子网信息（公共+私有）。          |
| **vpc_info.json**            | 不支持。                                     | 结构化JSON，包含VPC ID和按AZ子网信息。     |

**Analysis**:
- **Shared Network** outputs are richer, include subnet information organized by AZ and JSON format, suitable for complex management.
- **Disconnected Cluster** outputs are simple, focused on basic resource information.

---

### 总结
- **Disconnected Cluster**：
    - 配置简单，固定子网结构（3公共+3私有），无NAT网关，强调隔离性。
    - 支持多种VPC端点（S3、EC2、EFS、ELB、STS），适合断连环境。
    - 单一账户，无共享机制，脚本逻辑直接。
- **Shared Network**：
    - 配置灵活，支持仅公共子网、额外子网、指定AZ和跨账户共享。
    - 提供NAT网关，私有子网可访问互联网，仅支持S3端点。
    - 双账户支持，脚本复杂，输出详细，适合多租户或混合场景。

**Recommendations**:
- If you need highly isolated disconnected clusters, choose **Disconnected Cluster**.
- If you need cross-account sharing or private subnet access to public internet, choose **Shared Network**.

For in-depth analysis of specific parts (such as subnet CIDR allocation or VPC endpoint configuration), please provide further details!

---

In the "disconnected cluster" configuration, internet access is prevented through specific network architecture and configuration, ensuring a highly isolated "disconnected" environment. The following details the mechanisms and implementation methods, based on the provided AWS CloudFormation templates and scripts, explaining how internet access is blocked:

---

### 1. **Private Subnets Without NAT Gateway**
- **Mechanism**:
    - In the "disconnected cluster" configuration, the route tables for private subnets (`PrivateSubnet`, `PrivateSubnet2`, `PrivateSubnet3`) (`PrivateRouteTable`, `PrivateRouteTable2`, `PrivateRouteTable3`) **do not contain default routes** (`0.0.0.0/0`).
    - No NAT gateway (`AWS::EC2::NatGateway`) or Elastic IP (`AWS::EC2::EIP`) resources, private subnets cannot access the internet indirectly through public subnets.
- **Implementation**:
    - In the template, private route tables only associate with S3 VPC endpoint (Gateway type), with no routes pointing to internet gateway or NAT gateway.
    - For example:
      ```yaml
      PrivateRouteTable:
        Type: "AWS::EC2::RouteTable"
        Properties:
          VpcId: !Ref VPC
      ```
      No `AWS::EC2::Route` resource defines `DestinationCidrBlock: 0.0.0.0/0`.
- **Effect**:
    - Instances in private subnets cannot initiate or receive traffic from the internet, can only access specific AWS services through VPC endpoints.

---

### 2. **Restricted Public Subnet Access**
- **Mechanism**:
    - Although public subnets (`PublicSubnet`, `PublicSubnet2`, `PublicSubnet3`) can access the internet through internet gateway (`InternetGateway`) and default route (`0.0.0.0/0`), the "disconnected cluster" scenario typically restricts the use of these subnets.
    - Cluster workloads (such as OpenShift nodes) are mainly deployed in private subnets, public subnets are only used for necessary infrastructure (such as load balancers or bastion hosts), with traffic strictly controlled through security groups.
- **Implementation**:
    - Public route table configures default route pointing to internet gateway:
      ```yaml
      PublicRoute:
        Type: "AWS::EC2::Route"
        DependsOn: GatewayToInternet
        Properties:
          RouteTableId: !Ref PublicRouteTable
          DestinationCidrBlock: 0.0.0.0/0
          GatewayId: !Ref InternetGateway
      ```
    - But private subnets do not associate with this route table, and cluster configuration typically avoids deploying critical components in public subnets.
- **Effect**:
    - Public subnet internet access capability does not affect private subnet isolation, cluster core components run in private subnets and cannot access the internet.

---

### 3. **VPC Endpoints Replace Internet Access**
- **Mechanism**:
    - Provides private access to AWS services through VPC endpoints (`AWS::EC2::VPCEndpoint`), bypassing the internet.
    - Supported services include:
        - **S3** (Gateway type): Access S3 storage through `S3Endpoint`.
        - **EC2, EFS, ELB, STS** (Interface type): Access through `ec2Endpoint`, `efsEndpoint`, `elbEndpoint`, `stsEndpoint`.
    - These endpoints resolve DNS internally within the VPC and route directly to AWS services, no public internet needed.
- **Implementation**:
    - S3 endpoint associates with public and private route tables:
      ```yaml
      S3Endpoint:
        Type: AWS::EC2::VPCEndpoint
        Properties:
          RouteTableIds:
            - !Ref PublicRouteTable
            - !Ref PrivateRouteTable
            - !If [DoAz2, !Ref PrivateRouteTable2, !Ref "AWS::NoValue"]
            - !If [DoAz3, !Ref PrivateRouteTable3, !Ref "AWS::NoValue"]
          ServiceName: !Join [ '', [ 'com.amazonaws.', !Ref 'AWS::Region', '.s3' ] ]
          VpcId: !Ref VPC
      ```
    - Interface endpoints deploy in private subnets, using security groups (`EndpointSecurityGroup`) to restrict access:
      ```yaml
      ec2Endpoint:
        Type: AWS::EC2::VPCEndpoint
        Properties:
          PrivateDnsEnabled: true
          VpcEndpointType: Interface
          SecurityGroupIds:
            - !Ref EndpointSecurityGroup
          SubnetIds:
            - !Ref PrivateSubnet
            - !If [DoAz2, !Ref PrivateSubnet2, !Ref "AWS::NoValue"]
          ServiceName: !Join [ '', [ 'com.amazonaws.', !Ref 'AWS::Region', '.ec2' ] ]
          VpcId: !Ref VPC
      ```
- **Effect**:
    - Cluster accesses AWS services privately through VPC endpoints (such as S3 storage, EC2 API, EFS file systems), no internet connection required.

---

### 4. **安全组限制**
- **机制**：
    - Interface类型VPC端点（EC2、EFS、ELB、STS）关联一个安全组（`EndpointSecurityGroup`），仅允许VPC内部的流量（`CidrIp: !Ref VpcCidr`）。
- **实现**：
    - 安全组配置：
      ```yaml
      EndpointSecurityGroup:
        Type: AWS::EC2::SecurityGroup
        Properties:
          GroupDescription: VPC Endpoint Security Group
          SecurityGroupIngress:
            - IpProtocol: -1
              CidrIp: !Ref VpcCidr
          VpcId: !Ref VPC
      ```
    - 仅允许VPC CIDR（如`10.0.0.0/16`）内的入站流量，阻止外部访问。
- **效果**：
    - 即使VPC端点解析到公共DNS，外部流量无法访问，强化了隔离。

---

### 5. **DNS配置**
- **机制**：
    - VPC启用DNS支持（`EnableDnsSupport: true`）和主机名（`EnableDnsHostnames: true`），确保VPC端点的DNS名称在VPC内解析到私有IP。
    - 可选的DHCP选项集（`DhcpOptions`）使用`AmazonProvidedDNS`，确保AWS服务的DNS请求路由到VPC端点。
- **实现**：
    - VPC配置：
      ```yaml
      VPC:
        Type: "AWS::EC2::VPC"
        Properties:
          EnableDnsSupport: "true"
          EnableDnsHostnames: "true"
          CidrBlock: !Ref VpcCidr
      ```
    - DHCP选项（若启用）：
      ```yaml
      DhcpOptions:
        Type: AWS::EC2::DHCPOptions
        Condition: DoDhcp
        Properties:
          DomainName: example.com
          DomainNameServers:
            - AmazonProvidedDNS
      ```
- **效果**：
    - AWS服务（如`s3.us-east-1.amazonaws.com`）的DNS请求通过VPC端点解析到VPC内部IP，避免公网DNS解析。

---

### 6. **脚本逻辑支持隔离**
- **机制**：
    - 脚本不配置任何允许互联网访问的资源（如NAT网关或公共IP分配）。
    - 输出（如`private_subnet_ids`）仅包含私有子网ID，确保集群部署在隔离环境中。
- **实现**：
    - 脚本仅保存VPC ID、子网ID、路由表ID和AZ信息到共享目录（如`${SHARED_DIR}/vpc_id`、`${SHARED_DIR}/private_subnet_ids`），无NAT相关配置。
    - 例如：
      ```bash
      PrivateSubnetIds="$(jq -c '[.Stacks[].Outputs[] | select(.OutputKey=="PrivateSubnetIds") | .OutputValue | split(",")[]]' "${SHARED_DIR}/vpc_stack_output" | sed "s/\"/'/g")"
      echo "$PrivateSubnetIds" > "${SHARED_DIR}/private_subnet_ids"
      ```
- **效果**：
    - 集群部署脚本（如OpenShift安装）使用私有子网，确保工作负载无法访问互联网。

---

### 7. **断连环境的整体设计**
- **架构总结**：
    - 私有子网无默认路由或NAT网关，阻止互联网流量。
    - VPC端点提供对S3、EC2、EFS、ELB、STS的私有访问，替代公网需求。
    - 安全组和DNS配置确保流量限于VPC内部。
    - 公共子网仅用于必要组件（如负载均衡器），不影响私有子网隔离。
- **典型场景**：
    - OpenShift集群部署在私有子网，镜像存储在通过S3端点访问的私有存储桶，API调用通过EC2/STS端点完成，文件存储使用EFS端点。
    - 所有操作在VPC内完成，无需互联网连接。

---

### 总结
“Disconnected cluster”通过以下方式实现无法访问互联网：
1. 私有子网无NAT网关和默认路由（`0.0.0.0/0`），阻止外部流量。
2. VPC端点（S3、EC2、EFS、ELB、STS）提供AWS服务的私有访问，绕过公网。
3. 安全组限制VPC端点流量仅限VPC内部。
4. DNS配置确保服务请求解析到VPC端点。
5. 脚本和模板避免配置任何互联网访问资源。

这种设计确保集群在“断连”环境中运行，适合高安全性场景（如政府、金融机构）。如需进一步澄清或分析特定组件（如VPC端点策略），请提供更多细节！