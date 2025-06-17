# AWS Private Cluster Installation Guide

This guide provides a detailed walkthrough of installing a private OpenShift cluster on AWS, including code snippets and configuration examples.

## Overview

A private cluster on AWS restricts network access to internal networks and creates private endpoints for cluster services. This setup provides enhanced security by limiting exposure to the public internet.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI configured
3. OpenShift installer
4. DNS domain registered in Route53

## Network Configuration

### VPC and Subnet Setup

The private cluster requires a VPC with both private and public subnets. Here's the Terraform configuration from `upi/aws/cloudformation/01_vpc_99_subnet.yaml`:

```yaml
# File: upi/aws/cloudformation/01_vpc_99_subnet.yaml
Resources:
   # Define a private subnet for the cluster nodes
   PrivateSubnet:
      Type: "AWS::EC2::Subnet"
      Properties:
         # Reference to the VPC where this subnet will be created
         VpcId: !Ref VpcId
         # CIDR block for the private subnet
         CidrBlock: !Ref PrivateSubnetCidr
         # Specify the availability zone for high availability
         AvailabilityZone: !Ref ZoneName
         Tags:
            - Key: Name
               # Create a descriptive name for the subnet
              Value: !Join ['-', [!Ref ClusterName, "private", !Ref ZoneName]]

   # Associate the private subnet with a route table
   PrivateSubnetRouteTableAssociation:
      Type: "AWS::EC2::SubnetRouteTableAssociation"
      Properties:
         # Link the subnet to the route table
         SubnetId: !Ref PrivateSubnet
         # Reference to the route table that controls traffic
         RouteTableId: !Ref PrivateRouteTableId
```

### Route Tables and NAT Gateway

```hcl
# NAT Gateway for private subnets
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.cluster_id}-nat"
  }
}

# Route table for private subnets
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.cluster_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "${var.cluster_id}-private"
  }
}
```

## DNS Configuration

### Private Hosted Zone

From `pkg/infrastructure/aws/clusterapi/aws.go`:

```go
// File: pkg/infrastructure/aws/clusterapi/aws.go (lines 146-228)
// Get the hosted zone ID from the install config or create a new one
phzID := in.InstallConfig.Config.AWS.HostedZone
if len(phzID) == 0 {
    logrus.Debugln("Creating private Hosted Zone")

    // Create a new private hosted zone for the cluster
    res, err := client.CreateHostedZone(ctx, &awsconfig.HostedZoneInput{
        // Unique identifier for the infrastructure
        InfraID:  in.InfraID,
        // VPC where the hosted zone will be associated
        VpcID:    vpcID,
        // AWS region for the hosted zone
        Region:   awsCluster.Spec.Region,
        // Domain name for the cluster
        Name:     in.InstallConfig.Config.ClusterDomain(),
        // IAM role for the hosted zone (if using cross-account)
        Role:     in.InstallConfig.Config.AWS.HostedZoneRole,
        // Additional tags for resource management
        UserTags: awsCluster.Spec.AdditionalTags,
    })
    if err != nil {
        return fmt.Errorf("failed to create private hosted zone: %w", err)
    }
    phzID = aws.StringValue(res.Id)
    logrus.Infoln("Created private Hosted Zone")
}

// Create DNS records for the API server in the private zone
if err := client.CreateOrUpdateRecord(ctx, &awsconfig.CreateRecordInput{
    // API server DNS name
    Name:           apiName,
    // AWS region for the record
    Region:         awsCluster.Spec.Region,
    // Target for the DNS record (load balancer)
    DNSTarget:      awsCluster.Spec.ControlPlaneEndpoint.Host,
    // ID of the private hosted zone
    ZoneID:         phzID,
    // ID of the load balancer's hosted zone
    AliasZoneID:    aliasZoneID,
    // IAM role for cross-account access
    HostedZoneRole: in.InstallConfig.Config.AWS.HostedZoneRole,
}); err != nil {
    return fmt.Errorf("failed to create records for api in private zone: %w", err)
}
```

## Load Balancer Configuration

### Internal Load Balancer

From `upi/aws/cloudformation/05_cluster_master_nodes.yaml`:

```yaml
# File: upi/aws/cloudformation/05_cluster_master_nodes.yaml
Resources:
  # Define the first master node
  Master0:
    Type: AWS::EC2::Instance
    Properties:
      # Use the RHCOS AMI for the instance
      ImageId: !Ref RhcosAmi
      # Configure the root volume
      BlockDeviceMappings:
      - DeviceName: /dev/xvda
        Ebs:
          # 120GB root volume
          VolumeSize: "120"
          # Use gp2 volume type for better performance
          VolumeType: "gp2"
      # IAM role for the master node
      IamInstanceProfile: !Ref MasterInstanceProfileName
      # Instance type for the master node
      InstanceType: !Ref MasterInstanceType
      # Network configuration
      NetworkInterfaces:
      - # Disable public IP assignment for private cluster
        AssociatePublicIpAddress: "false"
        DeviceIndex: "0"
        # Security group for the master node
        GroupSet:
        - !Ref "MasterSecurityGroupId"
        # Place in the first private subnet
        SubnetId: !Ref "Master0Subnet"
```

## Security Groups

```hcl
# Security group for control plane nodes
resource "aws_security_group" "master" {
  name        = "${var.cluster_id}-master-sg"
  description = "Security group for master nodes"
  vpc_id      = aws_vpc.cluster_vpc.id

  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

## Installation Process

1. **Create install-config.yaml**

```yaml
# File: install-config.yaml
apiVersion: v1
# Base domain for the cluster
baseDomain: example.com
metadata:
  # Name of the cluster
  name: private-cluster
platform:
  aws:
    # AWS region for the cluster
    region: us-west-2
    # List of private subnets for the cluster
    subnets:
      - subnet-12345678
      - subnet-87654321
# Specify internal publishing strategy for private cluster
publish: Internal
```

2. **Generate Ignition Configs**

```bash
# Command to generate ignition configs for the cluster
openshift-install create ignition-configs
```

3. **Create Bootstrap Node**

From `upi/aws/cloudformation/05_cluster_master_nodes.yaml`:

```yaml
# File: upi/aws/cloudformation/05_cluster_master_nodes.yaml
Resources:
  # Define the bootstrap node for cluster installation
  BootstrapNode:
    Type: AWS::EC2::Instance
    Properties:
      # Use the RHCOS AMI for the bootstrap node
      ImageId: !Ref RhcosAmi
      # Instance type for the bootstrap node
      InstanceType: !Ref BootstrapInstanceType
      # Place in the first private subnet
      SubnetId: !Ref PrivateSubnet1
      # Security group for the bootstrap node
      SecurityGroupIds:
        - !Ref BootstrapSecurityGroup
      # Ignition configuration for the node
      UserData:
        Fn::Base64: !Ref BootstrapIgnition
```

4. **Create Control Plane Nodes**

```yaml
# CloudFormation template for master nodes
Resources:
  Master0:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref RhcosAmi
      InstanceType: !Ref MasterInstanceType
      NetworkInterfaces:
      - AssociatePublicIpAddress: "false"
        DeviceIndex: "0"
        GroupSet:
        - !Ref "MasterSecurityGroupId"
        SubnetId: !Ref "Master0Subnet"
```

## Post-Installation Configuration

1. **Verify Private Connectivity**

```bash
# Test API server access using the private endpoint
curl -k https://api.private-cluster.example.com:6443/version

# Verify internal DNS resolution for the API server
dig api.private-cluster.example.com
```

2. **Configure Private Registry Access**

```yaml
# File: registry-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
   name: registry-config
data:
   registry.conf: |
      # Configure private registry access
      [[registry]]
        # Registry prefix for private images
        prefix = "private-registry.example.com"
        # Location of the private registry
        location = "private-registry.example.com"
        # Only use digest-based pulls for security
        mirror-by-digest-only = true
        # Allow insecure registry access
        insecure = true
```

## Troubleshooting

### Common Issues

1. **DNS Resolution**
   - Verify private hosted zone configuration
   - Check VPC DNS settings
   - Validate security group rules

2. **Network Connectivity**
   - Check NAT Gateway status
   - Verify route table configurations
   - Test internal load balancer health

3. **API Access**
   - Verify security group rules
   - Check internal load balancer configuration
   - Validate DNS records

## Best Practices

1. **Network Security**
   - Use separate security groups for different components
   - Implement strict security group rules
   - Enable VPC flow logs

2. **High Availability**
   - Deploy across multiple availability zones
   - Use internal load balancers for redundancy
   - Implement proper health checks

3. **Monitoring**
   - Set up CloudWatch alarms
   - Enable VPC flow logs
   - Monitor NAT Gateway metrics

## References

- [AWS Private Link Documentation](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html)
- [OpenShift AWS Installation Guide](https://docs.openshift.com/container-platform/latest/installing/installing_aws/installing-aws-private.html)
- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html) 