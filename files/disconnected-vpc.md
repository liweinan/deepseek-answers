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

### 2. **Main Functional Differences**
| Feature                            | Disconnected Cluster                          | Shared Network                              |
|--------------------------------|-----------------------------------------------|--------------------------------------------|
| **VPC Endpoint Support**                | Supports S3 (Gateway type) and EC2, EFS, ELB, STS (Interface type) VPC endpoints for enhanced private access. | Only supports S3 VPC endpoint (Gateway type).           |
| **NAT Gateway**                    | Does not support NAT gateway, private subnets have no direct internet access.      | Supports NAT gateway, private subnets can access internet via NAT.   |
| **Subnet Sharing**                   | Does not support subnet sharing, all resources within single account.         | Supports sharing subnets to other accounts via AWS RAM.         |
| **Public-Only Subnet Option**             | Not supported, must create both public and private subnets.               | Supports creating only public subnets (`OnlyPublicSubnets`).  |
| **Additional Subnets**                   | Does not support creating additional subnets within same AZ.                 | Supports creating additional public/private subnets within same AZ (`AdditionalSubnetsCount`). |
| **AZ Selection Flexibility**               | Automatically selects AZ or based on default configuration.                    | Supports specifying AZ list (`AllowedAvailabilityZoneList`). |
| **Account Management**                   | Single account operation.                                | Supports dual-account mode (creator and sharing account).        |

---

### 3. **Network Architecture Differences**
#### **Disconnected Cluster**
- **Subnet Structure**:
    - Creates a pair of public and private subnets in each AZ (up to 3 AZs).
    - Public subnets access external networks through Internet Gateway, private subnets have no NAT gateway and cannot directly access internet.
    - Subnet CIDRs are allocated based on `!Cidr` function, fixed division into 6 blocks (3 public + 3 private).
- **Routing**:
    - Public subnets are associated with public route table, containing default route (0.0.0.0/0) pointing to Internet Gateway.
    - Private subnets are associated with independent route tables, no default route, access AWS services only through S3 VPC endpoint.
- **VPC Endpoints**:
    - S3 endpoint (Gateway type) connects to both public and private route tables.
    - EC2, EFS, ELB, STS endpoints (Interface type) are deployed in private subnets, access controlled by security groups.
- **Isolation**:
    - Highly isolated, private subnets access AWS services through VPC endpoints, no public internet needed.
    - Suitable for completely disconnected clusters, emphasizing internal communication and controlled AWS service access.

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

### 1. **Template Parameter Differences**
| 参数                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **VpcCidr**                  | Default 10.0.0.0/16, supports /16-/24.               | Same.                                     |
| **AvailabilityZoneCount**     | 1-3 AZs, default 1.                             | Same.                                     |
| **SubnetBits**               | Subnet size /19-/27, default /27.                   | Same.                                     |
| **DhcpOptionSet**            | Supports custom DNS (yes/no), default no.             | Same.                                     |
| **OnlyPublicSubnets**        | Not supported.                                     | Supports (yes/no), default no, allows creating only public subnets. |
| **AllowedAvailabilityZoneList** | Not supported.                                     | Supports specifying AZ list (comma-separated), default empty.        |
| **ResourceSharePrincipals**  | Not supported.                                     | Supports specifying sharing account ARN, default empty, for RAM sharing.  |
| **AdditionalSubnetsCount**   | Not supported.                                     | Supports creating additional subnets in same AZ (0/1), default 0.    |

**Analysis**:
- **Shared Network** provides more parameters (`OnlyPublicSubnets`, `AllowedAvailabilityZoneList`, `ResourceSharePrincipals`, `AdditionalSubnetsCount`), supporting more flexible configurations such as public-only subnets, specified AZs, and subnet sharing.
- **Disconnected Cluster** has simpler parameters, focused on standard VPC configuration.

---

### 2. **Subnet Configuration Differences**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **Subnet Count**                 | Fixed 1 public + 1 private subnet per AZ, max 3 AZs (6 subnets). | 1 public + 1 private (optional) per AZ, supports additional subnets, max 8 subnets. |
| **CIDR Allocation**                 | VPC CIDR divided into 6 blocks (3 public + 3 private).              | VPC CIDR divided into 8 blocks, allows more subnet allocation.         |
| **Public Subnets**                 | Fixed creation, associated with Internet Gateway.                    | Optional (`OnlyPublicSubnets`), supports `MapPublicIpOnLaunch`. |
| **Private Subnets**                 | Fixed creation, no NAT gateway.                         | Optional (`DoAz1PrivateSubnet` etc.), supports NAT gateway. |
| **Additional Subnets**                 | Not supported.                                     | Supports creating additional public/private subnets in AZ1 (`PublicSubnet1a`/`PrivateSubnet1a`). |
| **AZ Selection**                   | Automatic selection (`Fn::GetAZs`).                    | Supports specifying AZs (`AllowedAvailabilityZoneList`). |

**Analysis**:
- **Disconnected Cluster** has fixed subnet structure (6 CIDR blocks, 3 public + 3 private), no additional subnets or AZ specification, suitable for standardized deployments.
- **Shared Network** has more flexible subnet allocation (8 CIDR blocks), supports public-only subnets, additional subnets, and custom AZs, suitable for complex scenarios.

---

### 3. **Routing Configuration Differences**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **Public Route Table**               | 1, contains 0.0.0.0/0 pointing to Internet Gateway.            | Same.                                     |
| **Private Route Tables**               | 1 per AZ, no default route (0.0.0.0/0).           | 1 per AZ, contains 0.0.0.0/0 pointing to NAT gateway (if private subnet exists). |
| **NAT Gateway**                  | Not supported, private subnets have no internet access.                | 1 NAT gateway per AZ's private subnet (`NAT`/`NAT1a`/`NAT2`/`NAT3`). |
| **EIP**                      | Not supported.                                     | 1 EIP allocated per NAT gateway (`EIP`/`EIP1a`/`EIP2`/`EIP3`). |

**Analysis**:
- **Disconnected Cluster** private subnets have no NAT gateway, rely on VPC endpoints to access AWS services, emphasizing isolation.
- **Shared Network** provides controlled internet access for private subnets through NAT gateways, suitable for scenarios requiring external connectivity.

---

### 4. **VPC Endpoint Configuration Differences**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **S3 Endpoint**                   | Gateway type, associated with public and private route tables.            | Same.                                     |
| **Other Endpoints**                 | Interface types: EC2, EFS, ELB, STS, deployed in private subnets, controlled by security groups. | Not supported.                                   |
| **Security Groups**                   | Creates `EndpointSecurityGroup` for Interface endpoints, allows access within VPC CIDR. | Not supported (no Interface endpoints).                |

**Analysis**:
- **Disconnected Cluster** supports multiple VPC endpoints (S3, EC2, EFS, ELB, STS), suitable for disconnected environments to access AWS services through private connections.
- **Shared Network** only supports S3 endpoint, relies on NAT gateway to access other services, lower isolation.

---

### 5. **Conditional Logic Differences**
| 条件                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **DoAz2/DoAz3**              | 控制第2/3 AZ子网创建。                        | 相同。                                     |
| **DoDhcp**                   | 控制DHCP选项集创建。                          | 相同。                                     |
| **DoOnlyPublicSubnets**      | Not supported.                                     | Controls whether to create only public subnets.                   |
| **DoAz1PrivateSubnet**        | Not supported (private subnets fixed).                      | Controls AZ1 private subnet creation.                      |
| **DoAz2/3PrivateSubnet**      | Not supported (private subnets fixed).                      | Controls AZ2/3 private subnet creation.                    |
| **AzRestriction**            | Not supported.                                     | Controls whether to use specified AZ list.                   |
| **ShareSubnets**             | Not supported.                                     | Controls whether to create RAM resource sharing.                  |
| **DoAdditionalAz**           | Not supported.                                     | Controls AZ1 additional subnet creation.                      |

**Analysis**:
- **Shared Network** has more complex conditional logic, supports optional private subnets, specified AZs, and resource sharing, adapting to diverse requirements.
- **Disconnected Cluster** has simple conditional logic, focused on fixed subnets and VPC endpoint configuration.

---

### 6. **Resource Sharing Configuration**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **AWS RAM Sharing**              | Not supported.                                     | Supports (`ResourceShareSubnets`), shares public/private subnets to specified accounts. |
| **Sharing Parameters**                 | None.                                         | `ResourceSharePrincipals` specifies target account ARN. |

**Analysis**:
- **Shared Network** supports cross-account subnet sharing through AWS RAM, suitable for multi-account architectures.
- **Disconnected Cluster** has no sharing mechanism, resources limited to single account.

---

### 7. **Script Logic Differences**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **Account Management**                 | Single account (`AWS_SHARED_CREDENTIALS_FILE`).    | Supports dual accounts (`ENABLE_SHARED_VPC`, switches to `.awscred_shared_account`). |
| **Parameter Passing**                 | Hardcoded (e.g. `AvailabilityZoneCount`).          | Dynamically generates `vpc_params.json`, supports multiple parameters (e.g. `OnlyPublicSubnets`, `AllowedAvailabilityZoneList`). |
| **Error Checking**                 | Simple (e.g. `ZONES_COUNT` max 3).                 | Stricter (e.g. AZ list matches `ZONES_COUNT`).     |
| **Output**                     | Basic output (VPC ID, subnet IDs, route table IDs, AZs).     | Additional outputs `SubnetsByAz1/2/3` and `vpc_info.json`, structured subnet information. |
| **AZ Query**                   | Fixed query subnet AZ.                              | Dynamically queries available AZs, limits `MAX_ZONES_COUNT`.     |

**Analysis**:
- **Shared Network** scripts are more complex, support dual accounts, dynamic parameters, and detailed outputs, suitable for multi-tenant management.
- **Disconnected Cluster** scripts are simple, directly execute fixed configurations, suitable for single scenarios.

---

### 8. **Output Differences**
| 输出                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **VpcId**                    | 相同。                                       | 相同。                                     |
| **PublicSubnetIds**          | 公共子网ID列表。                             | 相同，支持额外子网。                       |
| **PrivateSubnetIds**         | 私有子网ID列表。                             | 相同，可为空（仅公共子网）。               |
| **PublicRouteTableId**       | 公共路由表ID。                               | 相同。                                     |
| **PrivateRouteTableIds**     | 私有路由表ID（按AZ）。                       | 相同，可为空（无私有子网）。               |
| **AvailabilityZones**        | AZ列表。                                     | 相同，支持指定AZ。                         |
| **SubnetsByAz1/2/3**         | Not supported.                                     | Subnet information organized by AZ (public + private).          |
| **vpc_info.json**            | Not supported.                                     | Structured JSON containing VPC ID and subnet information by AZ.     |

**Analysis**:
- **Shared Network** outputs are richer, include subnet information organized by AZ and JSON format, suitable for complex management.
- **Disconnected Cluster** outputs are simple, focused on basic resource information.

---

### Summary
- **Disconnected Cluster**:
    - Simple configuration, fixed subnet structure (3 public + 3 private), no NAT gateway, emphasizes isolation.
    - Supports multiple VPC endpoints (S3, EC2, EFS, ELB, STS), suitable for disconnected environments.
    - Single account, no sharing mechanism, straightforward script logic.
- **Shared Network**:
    - Flexible configuration, supports public-only subnets, additional subnets, specified AZs and cross-account sharing.
    - Provides NAT gateway, private subnets can access internet, only supports S3 endpoint.
    - Dual account support, complex scripts, detailed outputs, suitable for multi-tenant or hybrid scenarios.

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