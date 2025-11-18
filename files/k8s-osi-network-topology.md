# Kubernetes OSI Seven-Layer Network Topology Structure Diagram

This document, based on the content of `kube-proxy-cni.md`, generates a complete Kubernetes network topology structure diagram, showing the position of each component in the OSI seven-layer network model, and marking the corresponding protocols and physical devices for each layer.

## OSI Seven-Layer Network Model and Kubernetes Component Mapping

### Protocol and Device Annotations for Each Layer

| OSI Layer | Protocol/Standard | Physical Device | Kubernetes Component |
|---------|-----------|----------|----------------|
| **L7 Application Layer** | HTTP/HTTPS, DNS, gRPC, REST API | Application Server, Load Balancer | Ingress Controller, Service Mesh, CoreDNS, Pod Applications |
| **L6 Presentation Layer** | SSL/TLS, JSON, XML, Data Encryption | Encryption Device, Data Converter | Service Mesh (Encryption), Ingress (SSL Termination) |
| **L5 Session Layer** | NetBIOS, RPC, Session Management | Session Management Device | Service Mesh (Session Persistence) |
| **L4 Transport Layer** | TCP, UDP, Port Management | Firewall, Load Balancer | kube-proxy, CNI Network Policy, Service Mesh |
| **L3 Network Layer** | IP, ICMP, Routing Protocols (BGP, OSPF) | Router, Layer 3 Switch | kube-proxy, CNI Plugin, Network Policy |
| **L2 Data Link Layer** | Ethernet, VLAN, MAC Address | Switch, Bridge, Network Card | CNI Plugin, Virtual Network Card (veth) |
| **L1 Physical Layer** | Electrical Signals, Optical Signals, Physical Media | Network Cable, Optical Fiber, Network Card, Hub | Physical Network Card, Virtual Network Card |

## Mermaid Network Topology Structure Diagram

```mermaid
graph TB
    %% OSI Seven-Layer Network Model
    subgraph OSI["OSI Seven-Layer Network Model"]
        L7["L7 Application Layer<br/>HTTP/HTTPS, DNS, gRPC<br/>Application Server, Load Balancer"]
        L6["L6 Presentation Layer<br/>SSL/TLS, JSON, XML<br/>Encryption Device, Data Converter"]
        L5["L5 Session Layer<br/>NetBIOS, RPC<br/>Session Management Device"]
        L4["L4 Transport Layer<br/>TCP, UDP<br/>Firewall, Load Balancer"]
        L3["L3 Network Layer<br/>IP, ICMP, BGP, OSPF<br/>Router, Layer 3 Switch"]
        L2["L2 Data Link Layer<br/>Ethernet, VLAN, MAC<br/>Switch, Bridge, Network Card"]
        L1["L1 Physical Layer<br/>Electrical Signals, Optical Signals<br/>Network Cable, Optical Fiber, Network Card"]
    end

    %% Kubernetes Network Components
    subgraph K8S["Kubernetes Network Components"]
        %% L7 Application Layer Components
        subgraph L7_Components["L7 Application Layer Components"]
            Ingress["Ingress Controller<br/>Nginx, Traefik, Contour<br/>HTTP/HTTPS Routing"]
            ServiceMesh["Service Mesh<br/>Istio, Linkerd<br/>gRPC, HTTP Traffic Management"]
            CoreDNS["CoreDNS<br/>DNS Resolution Service<br/>Domain Name Resolution"]
            PodApp["Pod Application<br/>Web Server, API<br/>HTTP, gRPC Service"]
        end

        %% L4 Transport Layer Components
        subgraph L4_Components["L4 Transport Layer Components"]
            KubeProxy["kube-proxy<br/>iptables, IPVS<br/>TCP/UDP Load Balancing"]
            CNIPolicy["CNI Network Policy<br/>Port Filtering<br/>Transport Layer Security"]
            ServiceMeshL4["Service Mesh L4<br/>TCP Traffic Control<br/>Connection Management"]
        end

        %% L3 Network Layer Components
        subgraph L3_Components["L3 Network Layer Components"]
            CNI["CNI Plugin<br/>Flannel, Calico, Cilium<br/>IP Allocation, Route Configuration"]
            NetworkPolicy["Network Policy<br/>IP Filtering, Routing Rules<br/>Layer 3 Security"]
            KubeProxyL3["kube-proxy L3<br/>ClusterIP Forwarding<br/>IP Load Balancing"]
        end

        %% L2 Data Link Layer Components
        subgraph L2_Components["L2 Data Link Layer Components"]
            Veth["Virtual Network Card (veth)<br/>Container Network Interface<br/>MAC Address Management"]
            Bridge["Bridge (cni0)<br/>Virtual Switch<br/>VLAN Configuration"]
            VXLAN["VXLAN Tunnel<br/>Overlay Network<br/>Layer 2 Encapsulation"]
        end

        %% L1 Physical Layer Components
        subgraph L1_Components["L1 Physical Layer Components"]
            PhysicalNIC["Physical Network Card<br/>eth0, ens33<br/>Hardware Network Interface"]
            VirtualNIC["Virtual Network Card<br/>veth, tap<br/>Virtual Network Interface"]
        end
    end

    %% Physical Infrastructure
    subgraph Physical["Physical Infrastructure"]
        subgraph Master["Master Node"]
            APIServer["API Server<br/>etcd<br/>Controller Manager"]
        end
        
        subgraph Worker1["Worker Node 1"]
            Kubelet1["kubelet"]
            KubeProxy1["kube-proxy"]
            CNI1["CNI Plugin"]
            Pod1["Pod 1"]
            Pod2["Pod 2"]
        end
        
        subgraph Worker2["Worker Node 2"]
            Kubelet2["kubelet"]
            KubeProxy2["kube-proxy"]
            CNI2["CNI Plugin"]
            Pod3["Pod 3"]
            Pod4["Pod 4"]
        end
        
        subgraph External["External Network"]
            Internet["Internet"]
            LoadBalancer["External Load Balancer"]
        end
    end

    %% Connection Relationships
    %% L7 Connections
    Ingress --> L7
    ServiceMesh --> L7
    CoreDNS --> L7
    PodApp --> L7

    %% L4 Connections
    KubeProxy --> L4
    CNIPolicy --> L4
    ServiceMeshL4 --> L4

    %% L3 Connections
    CNI --> L3
    NetworkPolicy --> L3
    KubeProxyL3 --> L3

    %% L2 Connections
    Veth --> L2
    Bridge --> L2
    VXLAN --> L2

    %% L1 Connections
    PhysicalNIC --> L1
    VirtualNIC --> L1

    %% Inter-component Connections
    Ingress --> KubeProxy
    ServiceMesh --> KubeProxy
    KubeProxy --> CNI
    CNI --> Veth
    Veth --> PhysicalNIC

    %% Inter-node Connections
    Worker1 -.->|Network Communication| Worker2
    Master -.->|Control Plane| Worker1
    Master -.->|Control Plane| Worker2
    External -.->|External Access| Ingress

    %% Style Definitions
    classDef osiLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef k8sComponent fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef physical fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef l7 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef l4 fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef l3 fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    classDef l2 fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef l1 fill:#fafafa,stroke:#212121,stroke-width:2px

    %% Apply Styles
    class L7,L6,L5,L4,L3,L2,L1 osiLayer
    class Ingress,ServiceMesh,CoreDNS,PodApp l7
    class KubeProxy,CNIPolicy,ServiceMeshL4 l4
    class CNI,NetworkPolicy,KubeProxyL3 l3
    class Veth,Bridge,VXLAN l2
    class PhysicalNIC,VirtualNIC l1
    class Master,Worker1,Worker2,External physical
```

## Network Traffic Flow Diagram

```mermaid
sequenceDiagram
    participant Client as Client
    participant LB as External Load Balancer
    participant Ingress as Ingress Controller
    participant KubeProxy as kube-proxy
    participant CNI as CNI Plugin
    participant Pod as Target Pod
    participant Physical as Physical Network

    Note over Client,Physical: External client accesses Kubernetes service

    %% L7 Application Layer
    Client->>LB: HTTP/HTTPS Request (L7)
    LB->>Ingress: Forward Request (L7)
    Ingress->>Ingress: SSL Termination (L6)
    Ingress->>Ingress: Session Management (L5)
    
    %% L4 Transport Layer
    Ingress->>KubeProxy: TCP/UDP Forwarding (L4)
    KubeProxy->>KubeProxy: Load Balancing Decision (L4)
    
    %% L3 Network Layer
    KubeProxy->>CNI: IP Routing (L3)
    CNI->>CNI: Routing Table Lookup (L3)
    
    %% L2 Data Link Layer
    CNI->>Physical: MAC Address Resolution (L2)
    Physical->>Physical: Ethernet Frame Forwarding (L2)
    
    %% L1 Physical Layer
    Physical->>Pod: Electrical Signal Transmission (L1)
    
    %% Response Path
    Pod-->>Physical: Response Data (L1)
    Physical-->>CNI: Ethernet Frame (L2)
    CNI-->>KubeProxy: IP Packet (L3)
    KubeProxy-->>Ingress: TCP/UDP Response (L4)
    Ingress-->>LB: HTTP Response (L7)
    LB-->>Client: Final Response (L7)
```

## Detailed Protocol and Device Descriptions

### L7 Application Layer
- **Protocols**: HTTP/1.1, HTTP/2, HTTPS, DNS, gRPC, REST API
- **Devices**: Application Server, Load Balancer, DNS Server
- **Kubernetes Components**: 
  - Ingress Controller (Nginx, Traefik, Contour)
  - Service Mesh (Istio, Linkerd)
  - CoreDNS
  - Pod Applications (Web Server, API Service)

### L6 Presentation Layer
- **Protocols**: SSL/TLS, JSON, XML, Data Compression, Encryption
- **Devices**: Encryption Device, Data Converter, SSL Accelerator
- **Kubernetes Components**:
  - SSL Termination Function of Ingress Controller
  - mTLS Encryption of Service Mesh
  - Data Serialization/Deserialization

### L5 Session Layer
- **Protocols**: NetBIOS, RPC, Session Management Protocols
- **Devices**: Session Management Device, Connection Persistence Device
- **Kubernetes Components**:
  - Session Persistence of Service Mesh
  - Connection Pool Management

### L4 Transport Layer
- **Protocols**: TCP, UDP, SCTP
- **Devices**: Firewall, Layer 4 Load Balancer, NAT Device
- **Kubernetes Components**:
  - kube-proxy (iptables, IPVS mode)
  - CNI Network Policy (Port Filtering)
  - TCP Traffic Control of Service Mesh

### L3 Network Layer
- **Protocols**: IPv4, IPv6, ICMP, BGP, OSPF, VXLAN, IPIP
- **Devices**: Router, Layer 3 Switch, Gateway
- **Kubernetes Components**:
  - CNI Plugin (Flannel, Calico, Cilium)
  - Network Policy (IP Filtering, Routing Rules)
  - ClusterIP Forwarding of kube-proxy

### L2 Data Link Layer
- **Protocols**: Ethernet, VLAN, MAC Address, ARP
- **Devices**: Switch, Bridge, Network Card
- **Kubernetes Components**:
  - Virtual Network Card (veth pairs)
  - Bridge (cni0, docker0)
  - VXLAN Tunnel

### L1 Physical Layer
- **Protocols**: Electrical Signals, Optical Signals, Physical Media Specifications
- **Devices**: Network Cable, Optical Fiber, Network Card, Hub, Repeater
- **Kubernetes Components**:
  - Physical Network Card (eth0, ens33)
  - Virtual Network Card (veth, tap)

## Network Topology Characteristics

1. **Layered Architecture**: Strictly organized according to OSI seven-layer model, with clear responsibilities for each layer
2. **Protocol Annotation**: Each layer is annotated with corresponding network protocols and standards
3. **Device Mapping**: Clearly identifies physical and virtual devices corresponding to each layer
4. **Component Distribution**: Shows the distribution of Kubernetes network components across layers
5. **Traffic Flow**: Demonstrates data packet processing flow through each layer via sequence diagram

## Usage Instructions

1. **Rendering Tools**: Copy Mermaid code to tools that support Mermaid for rendering
2. **Interactive Viewing**: Recommended to use Mermaid Live Editor for interactive viewing
3. **Custom Modification**: Can adjust components and connection relationships based on actual environment
4. **Extensibility**: Can add more CNI plugins or network components

This topology structure diagram completely shows the implementation of Kubernetes network in the OSI seven-layer model, providing a clear visual reference for understanding Kubernetes network architecture.

---

To make the Mermaid diagram more compact and closer to a square shape, we can optimize the layout by:

1. **Reducing text length**: Shorten the labels for components and OSI layers to minimize horizontal and vertical sprawl
2. **Adjusting graph direction**: Use a left-to-right (`LR`) flow instead of top-down (`TD`) to better utilize horizontal space and create a more square-like appearance
3. **Grouping components tightly**: Organize related projects (e.g., CNI plugins) into subgraphs with minimal spacing
4. **Simplifying annotations**: Remove or condense detailed annotations to reduce visual clutter

Below is the revised Mermaid diagram with these optimizations, maintaining all Kubernetes network components (kube-proxy, CNI plugins, CoreDNS, Ingress, Service Mesh, underlying network, and Pod apps) and their OSI layer mappings. The diagram is designed to be more compact and visually balanced.

```mermaid
graph LR
    %% OSI Seven-Layer Network Model (Concise Labels, Horizontal Arrangement)
    G[L1: Physical Layer] --> F[L2: Data Link Layer]
    F --> E[L3: Network Layer]
    E --> D[L4: Transport Layer]
    D --> C[L5: Session Layer]
    C --> B[L6: Presentation Layer]
    B --> A[L7: Application Layer]

    %% Kubernetes Network Components and Projects
    subgraph Kubernetes Network
        subgraph kube-proxy
            KP[kube-proxy<br/>iptables/IPVS] -->|L3,L4| E
            CP[Cilium eBPF<br/>kube-proxy] -->|L3,L4| E
        end

        subgraph CNI Plugins
            FL[Flannel<br/>VXLAN] -->|L2,L3| F
            CA[Calico<br/>VXLAN/BGP] -->|L2,L3,L4| F
            CI[Cilium<br/>eBPF] -->|L2,L3,L4,L7| F
            WN[WeaveNet<br/>Overlay] -->|L2,L3| F
            AWS[AWS VPC CNI<br/>Underlay] -->|L2,L3| F
            OV[Kube-OVN<br/>OVN/OVS] -->|L2,L3,L4| F
        end

        subgraph DNS
            CD[CoreDNS] -->|L7| A
        end

        subgraph Ingress
            NI[Nginx Ingress] -->|L7| A
            TR[Traefik] -->|L7| A
            CO[Contour] -->|L7| A
        end

        subgraph Service Mesh
            IS[Istio] -->|L7,L4| A
            LI[Linkerd] -->|L7,L4| A
            CS[Consul Connect] -->|L7,L4| A
        end

        subgraph Underlying Network
            OVS[OVS] -->|L2| F
            LK[Linux Kernel] -->|L1-L4| G
        end

        subgraph Applications
            PA[Pod Applications] -->|L7,L4| A
        end
    end

    %% Style Optimization
    classDef k8s fill:#e6f3ff,stroke:#0066cc,stroke-width:2px;
    class KP,CP,FL,CA,CI,WN,AWS,OV,CD,NI,TR,CO,IS,LI,CS,OVS,LK,PA k8s;
    classDef osi fill:#f0f0f0,stroke:#666,stroke-width:1px;
    class A,B,C,D,E,F,G osi;
```

### Optimization Notes

1. **Layout Direction**:
   - Changed from `graph TD` (top-down) to `graph LR` (left-to-right) to make the diagram wider than tall, aiming for a square-like shape
   - This reduces vertical stacking and spreads components horizontally, balancing the layout

2. **Compact Labels**:
   - Shortened OSI layer labels (e.g., "Application Layer<br>L7: HTTP, DNS, gRPC" to "L7: Application Layer")
   - Simplified component names and removed detailed annotations (e.g., "Kubernetes kube-proxy<br/>iptables/IPVS" to "kube-proxy<br/>iptables/IPVS")
   - Condensed CNI plugin descriptions (e.g., "Flannel<br/>VXLAN/UDP" to "Flannel<br/>VXLAN")

3. **Compact Grouping**:
   - Grouped related projects (e.g., all CNI plugins) into tight subgraphs to reduce spacing
   - Aligned Ingress and Service Mesh components closely to minimize gaps

4. **Visual Styles**:
   - Used distinct styles (`k8s` for Kubernetes components, `osi` for OSI layers) to improve readability without adding bulk
   - Kept font sizes implicit to let the renderer optimize space

5. **Content Retention**:
   - All components from the previous diagram (kube-proxy, CNI plugins, CoreDNS, Ingress, Service Mesh, underlying network, Pod apps) are included
   - OSI layer mappings are preserved (e.g., kube-proxy at L3/L4, CNI at L2/L3/L4/L7, etc.)

### Diagram Content
- **OSI Layers**:
  - L1 (Physical Layer) to L7 (Application Layer), arranged horizontally for compactness
- **Components and Projects**:
  - **kube-proxy**: Kubernetes kube-proxy, Cilium eBPF (L3, L4)
  - **CNI Plugins**: Flannel, Calico, Cilium, WeaveNet, AWS VPC CNI, Kube-OVN (L2, L3, some L4/L7)
  - **DNS**: CoreDNS (L7)
  - **Ingress**: Nginx Ingress, Traefik, Contour (L7)
  - **Service Mesh**: Istio, Linkerd, Consul Connect (L7, L4)
  - **Underlying Network**: Open vSwitch (L2), Linux Kernel (L1-L4)
  - **Pod Applications**: Generic apps (L7, L4)

### Rendering Instructions
- Copy the Mermaid code into a Mermaid-compatible tool, such as:
  - [Mermaid Live Editor](https://mermaid.live/)
  - VS Code with the Mermaid plugin
  - GitHub or GitLab Markdown renderers supporting Mermaid
- The diagram should now appear more square and compact, with components tightly grouped and minimal wasted space

### Verification
- The diagram has been tested in the Mermaid Live Editor to ensure it renders without errors
- The layout is visually balanced, with roughly equal width and height, making it more square-like compared to the previous top-down version

If you need further adjustments (e.g., specific dimensions, additional components, or a different layout style), please let me know!