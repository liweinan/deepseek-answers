# Kubernetes OSI 七层网络拓扑结构图

本文档基于 `kube-proxy-cni.md` 的内容，生成一个完整的 Kubernetes 网络拓扑结构图，展示各个组件在 OSI 七层网络模型中的位置，并标注每层对应的协议和物理设备。

## OSI 七层网络模型与 Kubernetes 组件映射

### 各层协议和设备标注

| OSI 层级 | 协议/标准 | 物理设备 | Kubernetes 组件 |
|---------|-----------|----------|----------------|
| **L7 应用层** | HTTP/HTTPS, DNS, gRPC, REST API | 应用服务器, 负载均衡器 | Ingress 控制器, Service Mesh, CoreDNS, Pod 应用 |
| **L6 表示层** | SSL/TLS, JSON, XML, 数据加密 | 加密设备, 数据转换器 | Service Mesh (加密), Ingress (SSL 终止) |
| **L5 会话层** | NetBIOS, RPC, 会话管理 | 会话管理设备 | Service Mesh (会话保持) |
| **L4 传输层** | TCP, UDP, 端口管理 | 防火墙, 负载均衡器 | kube-proxy, CNI 网络策略, Service Mesh |
| **L3 网络层** | IP, ICMP, 路由协议 (BGP, OSPF) | 路由器, 三层交换机 | kube-proxy, CNI 插件, 网络策略 |
| **L2 数据链路层** | Ethernet, VLAN, MAC 地址 | 交换机, 网桥, 网卡 | CNI 插件, 虚拟网卡 (veth) |
| **L1 物理层** | 电信号, 光信号, 物理介质 | 网线, 光纤, 网卡, 集线器 | 物理网卡, 虚拟网卡 |

## Mermaid 网络拓扑结构图

```mermaid
graph TB
    %% OSI 七层网络模型
    subgraph OSI["OSI 七层网络模型"]
        L7["L7 应用层<br/>HTTP/HTTPS, DNS, gRPC<br/>应用服务器, 负载均衡器"]
        L6["L6 表示层<br/>SSL/TLS, JSON, XML<br/>加密设备, 数据转换器"]
        L5["L5 会话层<br/>NetBIOS, RPC<br/>会话管理设备"]
        L4["L4 传输层<br/>TCP, UDP<br/>防火墙, 负载均衡器"]
        L3["L3 网络层<br/>IP, ICMP, BGP, OSPF<br/>路由器, 三层交换机"]
        L2["L2 数据链路层<br/>Ethernet, VLAN, MAC<br/>交换机, 网桥, 网卡"]
        L1["L1 物理层<br/>电信号, 光信号<br/>网线, 光纤, 网卡"]
    end

    %% Kubernetes 网络组件
    subgraph K8S["Kubernetes 网络组件"]
        %% L7 应用层组件
        subgraph L7_Components["L7 应用层组件"]
            Ingress["Ingress 控制器<br/>Nginx, Traefik, Contour<br/>HTTP/HTTPS 路由"]
            ServiceMesh["Service Mesh<br/>Istio, Linkerd<br/>gRPC, HTTP 流量管理"]
            CoreDNS["CoreDNS<br/>DNS 解析服务<br/>域名解析"]
            PodApp["Pod 应用<br/>Web 服务器, API<br/>HTTP, gRPC 服务"]
        end

        %% L4 传输层组件
        subgraph L4_Components["L4 传输层组件"]
            KubeProxy["kube-proxy<br/>iptables, IPVS<br/>TCP/UDP 负载均衡"]
            CNIPolicy["CNI 网络策略<br/>端口过滤<br/>传输层安全"]
            ServiceMeshL4["Service Mesh L4<br/>TCP 流量控制<br/>连接管理"]
        end

        %% L3 网络层组件
        subgraph L3_Components["L3 网络层组件"]
            CNI["CNI 插件<br/>Flannel, Calico, Cilium<br/>IP 分配, 路由配置"]
            NetworkPolicy["网络策略<br/>IP 过滤, 路由规则<br/>三层安全"]
            KubeProxyL3["kube-proxy L3<br/>ClusterIP 转发<br/>IP 负载均衡"]
        end

        %% L2 数据链路层组件
        subgraph L2_Components["L2 数据链路层组件"]
            Veth["虚拟网卡 (veth)<br/>容器网络接口<br/>MAC 地址管理"]
            Bridge["网桥 (cni0)<br/>虚拟交换机<br/>VLAN 配置"]
            VXLAN["VXLAN 隧道<br/>Overlay 网络<br/>二层封装"]
        end

        %% L1 物理层组件
        subgraph L1_Components["L1 物理层组件"]
            PhysicalNIC["物理网卡<br/>eth0, ens33<br/>硬件网络接口"]
            VirtualNIC["虚拟网卡<br/>veth, tap<br/>虚拟网络接口"]
        end
    end

    %% 物理基础设施
    subgraph Physical["物理基础设施"]
        subgraph Master["Master 节点"]
            APIServer["API Server<br/>etcd<br/>Controller Manager"]
        end
        
        subgraph Worker1["Worker 节点 1"]
            Kubelet1["kubelet"]
            KubeProxy1["kube-proxy"]
            CNI1["CNI Plugin"]
            Pod1["Pod 1"]
            Pod2["Pod 2"]
        end
        
        subgraph Worker2["Worker 节点 2"]
            Kubelet2["kubelet"]
            KubeProxy2["kube-proxy"]
            CNI2["CNI Plugin"]
            Pod3["Pod 3"]
            Pod4["Pod 4"]
        end
        
        subgraph External["外部网络"]
            Internet["Internet"]
            LoadBalancer["外部负载均衡器"]
        end
    end

    %% 连接关系
    %% L7 连接
    Ingress --> L7
    ServiceMesh --> L7
    CoreDNS --> L7
    PodApp --> L7

    %% L4 连接
    KubeProxy --> L4
    CNIPolicy --> L4
    ServiceMeshL4 --> L4

    %% L3 连接
    CNI --> L3
    NetworkPolicy --> L3
    KubeProxyL3 --> L3

    %% L2 连接
    Veth --> L2
    Bridge --> L2
    VXLAN --> L2

    %% L1 连接
    PhysicalNIC --> L1
    VirtualNIC --> L1

    %% 组件间连接
    Ingress --> KubeProxy
    ServiceMesh --> KubeProxy
    KubeProxy --> CNI
    CNI --> Veth
    Veth --> PhysicalNIC

    %% 节点间连接
    Worker1 -.->|网络通信| Worker2
    Master -.->|控制平面| Worker1
    Master -.->|控制平面| Worker2
    External -.->|外部访问| Ingress

    %% 样式定义
    classDef osiLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef k8sComponent fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef physical fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef l7 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef l4 fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef l3 fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    classDef l2 fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef l1 fill:#fafafa,stroke:#212121,stroke-width:2px

    %% 应用样式
    class L7,L6,L5,L4,L3,L2,L1 osiLayer
    class Ingress,ServiceMesh,CoreDNS,PodApp l7
    class KubeProxy,CNIPolicy,ServiceMeshL4 l4
    class CNI,NetworkPolicy,KubeProxyL3 l3
    class Veth,Bridge,VXLAN l2
    class PhysicalNIC,VirtualNIC l1
    class Master,Worker1,Worker2,External physical
```

## 网络流量流向图

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant LB as 外部负载均衡器
    participant Ingress as Ingress 控制器
    participant KubeProxy as kube-proxy
    participant CNI as CNI 插件
    participant Pod as 目标 Pod
    participant Physical as 物理网络

    Note over Client,Physical: 外部客户端访问 Kubernetes 服务

    %% L7 应用层
    Client->>LB: HTTP/HTTPS 请求 (L7)
    LB->>Ingress: 转发请求 (L7)
    Ingress->>Ingress: SSL 终止 (L6)
    Ingress->>Ingress: 会话管理 (L5)
    
    %% L4 传输层
    Ingress->>KubeProxy: TCP/UDP 转发 (L4)
    KubeProxy->>KubeProxy: 负载均衡决策 (L4)
    
    %% L3 网络层
    KubeProxy->>CNI: IP 路由 (L3)
    CNI->>CNI: 路由表查询 (L3)
    
    %% L2 数据链路层
    CNI->>Physical: MAC 地址解析 (L2)
    Physical->>Physical: 以太网帧转发 (L2)
    
    %% L1 物理层
    Physical->>Pod: 电信号传输 (L1)
    
    %% 响应路径
    Pod-->>Physical: 响应数据 (L1)
    Physical-->>CNI: 以太网帧 (L2)
    CNI-->>KubeProxy: IP 数据包 (L3)
    KubeProxy-->>Ingress: TCP/UDP 响应 (L4)
    Ingress-->>LB: HTTP 响应 (L7)
    LB-->>Client: 最终响应 (L7)
```

## 详细协议和设备说明

### L7 应用层
- **协议**: HTTP/1.1, HTTP/2, HTTPS, DNS, gRPC, REST API
- **设备**: 应用服务器, 负载均衡器, DNS 服务器
- **Kubernetes 组件**: 
  - Ingress 控制器 (Nginx, Traefik, Contour)
  - Service Mesh (Istio, Linkerd)
  - CoreDNS
  - Pod 内应用 (Web 服务器, API 服务)

### L6 表示层
- **协议**: SSL/TLS, JSON, XML, 数据压缩, 加密
- **设备**: 加密设备, 数据转换器, SSL 加速器
- **Kubernetes 组件**:
  - Ingress 控制器的 SSL 终止功能
  - Service Mesh 的 mTLS 加密
  - 数据序列化/反序列化

### L5 会话层
- **协议**: NetBIOS, RPC, 会话管理协议
- **设备**: 会话管理设备, 连接保持设备
- **Kubernetes 组件**:
  - Service Mesh 的会话保持
  - 连接池管理

### L4 传输层
- **协议**: TCP, UDP, SCTP
- **设备**: 防火墙, 四层负载均衡器, NAT 设备
- **Kubernetes 组件**:
  - kube-proxy (iptables, IPVS 模式)
  - CNI 网络策略 (端口过滤)
  - Service Mesh 的 TCP 流量控制

### L3 网络层
- **协议**: IPv4, IPv6, ICMP, BGP, OSPF, VXLAN, IPIP
- **设备**: 路由器, 三层交换机, 网关
- **Kubernetes 组件**:
  - CNI 插件 (Flannel, Calico, Cilium)
  - 网络策略 (IP 过滤, 路由规则)
  - kube-proxy 的 ClusterIP 转发

### L2 数据链路层
- **协议**: Ethernet, VLAN, MAC 地址, ARP
- **设备**: 交换机, 网桥, 网卡
- **Kubernetes 组件**:
  - 虚拟网卡 (veth pairs)
  - 网桥 (cni0, docker0)
  - VXLAN 隧道

### L1 物理层
- **协议**: 电信号, 光信号, 物理介质规范
- **设备**: 网线, 光纤, 网卡, 集线器, 中继器
- **Kubernetes 组件**:
  - 物理网卡 (eth0, ens33)
  - 虚拟网卡 (veth, tap)

## 网络拓扑特点

1. **分层架构**: 严格按照 OSI 七层模型组织，每层职责明确
2. **协议标注**: 每层都标注了对应的网络协议和标准
3. **设备映射**: 明确标识了每层对应的物理和虚拟设备
4. **组件分布**: 展示了 Kubernetes 网络组件在各层的分布
5. **流量流向**: 通过时序图展示数据包在各层的处理流程

## 使用说明

1. **渲染工具**: 将 Mermaid 代码复制到支持 Mermaid 的工具中渲染
2. **交互式查看**: 建议使用 Mermaid Live Editor 进行交互式查看
3. **自定义修改**: 可根据实际环境调整组件和连接关系
4. **扩展性**: 可以添加更多 CNI 插件或网络组件

这个拓扑结构图完整展示了 Kubernetes 网络在 OSI 七层模型中的实现，为理解 Kubernetes 网络架构提供了清晰的视觉参考。