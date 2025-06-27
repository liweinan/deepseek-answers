# 以下是对“disconnected cluster”和“shared network”两种网络配置的比较，基于提供的AWS CloudFormation模板和脚本，重点分析它们在功能、架构和使用场景上的区别：

---

### 1. **总体目标与使用场景**
- **Disconnected Cluster**:
    - 设计目标是为“断连”（disconnected）环境中的集群提供网络基础设施，通常用于安全性要求高的场景，例如需要限制外部网络访问的私有集群。
    - 强调通过VPC端点（VPCEndpoints）提供对AWS服务的访问（如S3、EC2、EFS、ELB、STS），避免直接通过公网访问。
    - 适用于需要高度隔离的私有化部署，常见于政府、金融机构或其他对数据主权和网络隔离有严格要求的环境。

- **Shared Network**:
    - 设计目标是支持跨AWS账户共享VPC资源，允许一个账户创建VPC并通过AWS Resource Access Manager（RAM）将其子网共享给其他账户。
    - 提供更灵活的网络配置，支持仅创建公共子网、额外的子网，以及通过NAT网关为私有子网提供受控的互联网访问。
    - 适用于多账户架构（如企业级AWS组织），或需要在多个团队/项目之间共享网络资源的场景。

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
- **子网结构**：
    - 每个AZ内创建公共子网，私有子网可选（由`OnlyPublicSubnets`控制）。
    - 支持在同一AZ内创建额外子网（`AdditionalSubnetsCount`），增加灵活性。
    - 子网CIDR划分为8个块，允许更细粒度的子网分配。
- **路由**：
    - 公共子网通过互联网网关访问外部。
    - 私有子网通过NAT网关（部署在对应公共子网）访问互联网，每个AZ的私有子网有独立的NAT网关和路由表。
- **VPC端点**：
    - 仅支持S3端点（Gateway类型），连接到公共和私有路由表。
    - 无其他服务（EC2、EFS等）的VPC端点支持。
- **共享性**：
    - 通过AWS RAM共享子网（`ResourceShareSubnets`），允许其他AWS账户使用VPC资源。
    - 支持跨账户的资源管理，适合多租户或分担成本的场景。

---

### 4. **脚本逻辑差异**
- **Disconnected Cluster**：
    - 脚本专注于单一账户内的VPC创建和配置。
    - 硬编码参数（如`AvailabilityZoneCount`），直接通过命令行传递。
    - 输出包括VPC ID、子网ID、路由表ID和AZ信息，存储在共享目录中。
    - 无账户切换或共享逻辑。

- **Shared Network**：
    - 支持双账户模式（`ENABLE_SHARED_VPC`），通过`.awscred_shared_account`切换到共享账户。
    - 动态生成参数JSON（`vpc_params.json`），支持灵活配置（如`OnlyPublicSubnets`、`AllowedAvailabilityZoneList`）。
    - 额外的输出（`SubnetsByAz1/2/3`）提供按AZ组织的子网信息，生成结构化的`vpc_info.json`。
    - 包含错误检查（如AZ列表与数量匹配）。

---

### 5. **输出差异**
- **Disconnected Cluster**：
    - 输出包括：
        - `VpcId`：VPC ID。
        - `PublicSubnetIds`：公共子网ID列表。
        - `PrivateSubnetIds`：私有子网ID列表。
        - `PublicRouteTableId`：公共路由表ID。
        - `PrivateRouteTableIds`：私有路由表ID（按AZ组织）。
        - `availability_zones`：AZ列表。
    - 输出格式简单，专注于基本网络资源。

- **Shared Network**：
    - 输出更丰富，增加：
        - `AvailabilityZones`：AZ列表。
        - `SubnetsByAz1/2/3`：按AZ组织的子网信息（公共+私有，包含额外子网）。
        - `vpc_info.json`：结构化JSON，包含VPC ID和按AZ组织的子网ID（公共/私有）。
    - 输出支持跨账户共享和更复杂的子网管理。

---

### 6. **适用场景对比**
- **Disconnected Cluster**：
    - **优点**：
        - 高隔离性，适合断连环境。
        - 多个VPC端点支持，减少对公网依赖。
        - 简单配置，适合单一账户的私有集群。
    - **缺点**：
        - 无NAT网关，私有子网无法访问外部资源（除非通过VPC端点）。
        - 不支持子网共享，扩展性有限。
    - **适用场景**：
        - 私有化部署（如OpenShift on AWS在断连环境中）。
        - 高安全性需求（如合规性要求限制公网访问）。

- **Shared Network**：
    - **优点**：
        - 支持跨账户共享，适合多团队/项目协作。
        - 灵活配置（仅公共子网、额外子网、指定AZ）。
        - NAT网关支持，私有子网可控访问互联网。
    - **缺点**：
        - 仅支持S3端点，AWS服务访问受限。
        - 配置复杂，需管理多账户凭证和RAM共享。
    - **适用场景**：
        - 多账户AWS架构（如企业级AWS组织）。
        - 需要共享网络资源的场景（如开发/测试环境）。
        - 需私有子网访问公网的混合部署。

---

### 7. **总结**
- **Disconnected Cluster** 专注于高隔离的断连环境，通过VPC端点提供AWS服务访问，适合安全性敏感的私有集群，但缺乏灵活性和扩展性。
- **Shared Network** 强调跨账户共享和灵活配置，支持NAT网关和额外子网，适合多租户或需要互联网访问的场景，但VPC端点支持有限。
- **选择建议**：
    - 如果需要完全隔离的私有集群，选择 **Disconnected Cluster**。
    - 如果需要跨账户共享或私有子网访问公网，选择 **Shared Network**。

如需进一步分析特定配置或优化建议，请提供更多上下文！

---

以下是对“disconnected cluster”和“shared network”两种网络配置在AWS CloudFormation模板和脚本中的具体配置区别的详细解释，重点分析模板参数、资源定义、条件逻辑、路由配置、VPC端点以及脚本逻辑的差异。内容将尽量简洁并直接对比关键点。

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

**分析**：
- **Shared Network** 提供更多参数（`OnlyPublicSubnets`、`AllowedAvailabilityZoneList`、`ResourceSharePrincipals`、`AdditionalSubnetsCount`），支持更灵活的配置，如仅公共子网、指定AZ和子网共享。
- **Disconnected Cluster** 参数较简单，专注于标准VPC配置。

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

**分析**：
- **Disconnected Cluster** 子网结构固定（6块CIDR，3公共+3私有），无额外子网或AZ指定，适合标准化部署。
- **Shared Network** 子网分配更灵活（8块CIDR），支持仅公共子网、额外子网和自定义AZ，适合复杂场景。

---

### 3. **路由配置差异**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **公共路由表**               | 1个，包含0.0.0.0/0指向互联网网关。            | 相同。                                     |
| **私有路由表**               | 每个AZ1个，无默认路由（0.0.0.0/0）。           | 每个AZ1个，包含0.0.0.0/0指向NAT网关（若私有子网存在）。 |
| **NAT网关**                  | 不支持，私有子网无互联网访问。                | 每个AZ的私有子网关联1个NAT网关（`NAT`/`NAT1a`/`NAT2`/`NAT3`）。 |
| **EIP**                      | 不支持。                                     | 每个NAT网关分配1个EIP（`EIP`/`EIP1a`/`EIP2`/`EIP3`）。 |

**分析**：
- **Disconnected Cluster** 私有子网无NAT网关，依赖VPC端点访问AWS服务，强调隔离性。
- **Shared Network** 通过NAT网关为私有子网提供受控互联网访问，适合需要外部连接的场景。

---

### 4. **VPC端点配置差异**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **S3端点**                   | Gateway类型，关联公共和私有路由表。            | 相同。                                     |
| **其他端点**                 | Interface类型：EC2、EFS、ELB、STS，部署在私有子网，使用安全组控制。 | 不支持。                                   |
| **安全组**                   | 为Interface端点创建`EndpointSecurityGroup`，允许VPC CIDR内访问。 | 不支持（无Interface端点）。                |

**分析**：
- **Disconnected Cluster** 支持多种VPC端点（S3、EC2、EFS、ELB、STS），适合断连环境通过私有连接访问AWS服务。
- **Shared Network** 仅支持S3端点，依赖NAT网关访问其他服务，隔离性较低。

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

**分析**：
- **Shared Network** 条件逻辑更复杂，支持可选私有子网、指定AZ和资源共享，适应多样化需求。
- **Disconnected Cluster** 条件逻辑简单，专注于固定子网和VPC端点配置。

---

### 6. **资源共享配置**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **AWS RAM共享**              | 不支持。                                     | 支持（`ResourceShareSubnets`），共享公共/私有子网给指定账户。 |
| **共享参数**                 | 无。                                         | `ResourceSharePrincipals`指定目标账户ARN。 |

**分析**：
- **Shared Network** 通过AWS RAM支持跨账户子网共享，适合多账户架构。
- **Disconnected Cluster** 无共享机制，资源限于单一账户。

---

### 7. **脚本逻辑差异**
| 配置                          | Disconnected Cluster                          | Shared Network                              |
|------------------------------|-----------------------------------------------|--------------------------------------------|
| **账户管理**                 | 单一账户（`AWS_SHARED_CREDENTIALS_FILE`）。    | 支持双账户（`ENABLE_SHARED_VPC`，切换到`.awscred_shared_account`）。 |
| **参数传递**                 | 硬编码（如`AvailabilityZoneCount`）。          | 动态生成`vpc_params.json`，支持多参数（如`OnlyPublicSubnets`、`AllowedAvailabilityZoneList`）。 |
| **错误检查**                 | 简单（如`ZONES_COUNT`上限3）。                 | 更严格（如AZ列表与`ZONES_COUNT`匹配）。     |
| **输出**                     | 基本输出（VPC ID、子网ID、路由表ID、AZ）。     | 额外输出`SubnetsByAz1/2/3`和`vpc_info.json`，结构化子网信息。 |
| **AZ查询**                   | 固定查询子网AZ。                              | 动态查询可用AZ，限制`MAX_ZONES_COUNT`。     |

**分析**：
- **Shared Network** 脚本更复杂，支持双账户、动态参数和详细输出，适合多租户管理。
- **Disconnected Cluster** 脚本简单，直接执行固定配置，适合单一场景。

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

**分析**：
- **Shared Network** 输出更丰富，包含按AZ组织的子网信息和JSON格式，适合复杂管理。
- **Disconnected Cluster** 输出简单，专注于基本资源信息。

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

**建议**：
- 如果需要高隔离的断连集群，选择 **Disconnected Cluster**。
- 如果需要跨账户共享或私有子网访问公网，选择 **Shared Network**。

如需深入分析某部分（如子网CIDR分配或VPC端点配置），请进一步说明！

---

在“disconnected cluster”配置中，通过特定的网络架构和配置实现无法访问互联网（Internet），从而确保高度隔离的“断连”环境。以下是详细的机制和实现方式，基于提供的AWS CloudFormation模板和脚本，解释如何阻止互联网访问：

---

### 1. **私有子网无NAT网关**
- **机制**：
    - 在“disconnected cluster”配置中，私有子网（`PrivateSubnet`、`PrivateSubnet2`、`PrivateSubnet3`）的路由表（`PrivateRouteTable`、`PrivateRouteTable2`、`PrivateRouteTable3`）**不包含默认路由**（`0.0.0.0/0`）。
    - 没有NAT网关（`AWS::EC2::NatGateway`）或弹性IP（`AWS::EC2::EIP`）资源，私有子网无法通过公共子网间接访问互联网。
- **实现**：
    - 模板中，私有路由表仅关联S3 VPC端点（Gateway类型），没有指向互联网网关或NAT网关的路由。
    - 例如：
      ```yaml
      PrivateRouteTable:
        Type: "AWS::EC2::RouteTable"
        Properties:
          VpcId: !Ref VPC
      ```
      无`AWS::EC2::Route`资源定义`DestinationCidrBlock: 0.0.0.0/0`。
- **效果**：
    - 私有子网中的实例无法发起或接收来自互联网的流量，只能通过VPC端点访问特定的AWS服务。

---

### 2. **公共子网受限访问**
- **机制**：
    - 公共子网（`PublicSubnet`、`PublicSubnet2`、`PublicSubnet3`）虽然通过互联网网关（`InternetGateway`）和默认路由（`0.0.0.0/0`）可以访问互联网，但“disconnected cluster”场景通常限制这些子网的使用。
    - 集群的工作负载（如OpenShift节点）主要部署在私有子网，公共子网仅用于必要的基础设施（如负载均衡器或堡垒主机），且通过安全组严格控制流量。
- **实现**：
    - 公共路由表配置默认路由指向互联网网关：
      ```yaml
      PublicRoute:
        Type: "AWS::EC2::Route"
        DependsOn: GatewayToInternet
        Properties:
          RouteTableId: !Ref PublicRouteTable
          DestinationCidrBlock: 0.0.0.0/0
          GatewayId: !Ref InternetGateway
      ```
    - 但私有子网不关联此路由表，且集群配置通常避免将关键组件部署在公共子网。
- **效果**：
    - 公共子网的互联网访问能力不影响私有子网的隔离，集群核心组件在私有子网中运行，无法访问互联网。

---

### 3. **VPC端点替代互联网访问**
- **机制**：
    - 通过VPC端点（`AWS::EC2::VPCEndpoint`）提供对AWS服务的私有访问，绕过互联网。
    - 支持的服务包括：
        - **S3**（Gateway类型）：通过`S3Endpoint`访问S3存储。
        - **EC2、EFS、ELB、STS**（Interface类型）：通过`ec2Endpoint`、`efsEndpoint`、`elbEndpoint`、`stsEndpoint`访问。
    - 这些端点在VPC内部解析DNS并直接路由到AWS服务，无需公网。
- **实现**：
    - S3端点关联到公共和私有路由表：
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
    - Interface端点部署在私有子网，使用安全组（`EndpointSecurityGroup`）限制访问：
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
- **效果**：
    - 集群通过VPC端点以私有方式访问AWS服务（如S3存储、EC2 API、EFS文件系统），无需互联网连接。

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