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

The private cluster requires a VPC with both private and public subnets. Here's the Terraform configuration:

```hcl
# VPC Configuration
resource "aws_vpc" "cluster_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.cluster_id}-vpc"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.cluster_vpc.id
  cidr_block        = "10.0.${count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.cluster_id}-private-${count.index}"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = 3
  vpc_id            = aws_vpc.cluster_vpc.id
  cidr_block        = "10.0.${count.index + 3}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.cluster_id}-public-${count.index}"
  }
}
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

```go
// Create private hosted zone for the cluster
res, err := client.CreateHostedZone(ctx, &awsconfig.HostedZoneInput{
    InfraID:  in.InfraID,
    VpcID:    vpcID,
    Region:   awsCluster.Spec.Region,
    Name:     in.InstallConfig.Config.ClusterDomain(),
    Role:     in.InstallConfig.Config.AWS.HostedZoneRole,
    UserTags: awsCluster.Spec.AdditionalTags,
})
```

### DNS Records

```go
// Create API records in private zone
if err := client.CreateOrUpdateRecord(ctx, &awsconfig.CreateRecordInput{
    Name:           apiName,
    Region:         awsCluster.Spec.Region,
    DNSTarget:      awsCluster.Spec.ControlPlaneEndpoint.Host,
    ZoneID:         phzID,
    AliasZoneID:    aliasZoneID,
    HostedZoneRole: in.InstallConfig.Config.AWS.HostedZoneRole,
}); err != nil {
    return fmt.Errorf("failed to create records for api in private zone: %w", err)
}
```

## Load Balancer Configuration

### Internal Load Balancer

```yaml
# CloudFormation template for internal load balancer
Resources:
  InternalApiLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Scheme: internal
      Type: network
      Subnets: 
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
        - !Ref PrivateSubnet3
      Tags:
        - Key: Name
          Value: !Sub ${InfrastructureName}-int
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
apiVersion: v1
baseDomain: example.com
metadata:
  name: private-cluster
platform:
  aws:
    region: us-west-2
    subnets:
      - subnet-12345678
      - subnet-87654321
publish: Internal
```

2. **Generate Ignition Configs**

```bash
openshift-install create ignition-configs
```

3. **Create Bootstrap Node**

```yaml
# CloudFormation template for bootstrap node
Resources:
  BootstrapNode:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref RhcosAmi
      InstanceType: !Ref BootstrapInstanceType
      SubnetId: !Ref PrivateSubnet1
      SecurityGroupIds:
        - !Ref BootstrapSecurityGroup
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
# Test API server access
curl -k https://api.private-cluster.example.com:6443/version

# Verify internal DNS resolution
dig api.private-cluster.example.com
```

2. **Configure Private Registry Access**

```yaml
# ConfigMap for private registry
apiVersion: v1
kind: ConfigMap
metadata:
  name: registry-config
data:
  registry.conf: |
    [[registry]]
      prefix = "private-registry.example.com"
      location = "private-registry.example.com"
      mirror-by-digest-only = true
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