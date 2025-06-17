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

### Route53 Integration

The private cluster requires proper DNS configuration in Route53. Here's how to set it up:

1. **Create Private Hosted Zone**

```yaml
# File: upi/aws/cloudformation/02_route53.yaml
Resources:
  # Define the private hosted zone for the cluster
  PrivateHostedZone:
    Type: AWS::Route53::HostedZone
    Properties:
      # Domain name for the cluster
      Name: !Ref ClusterDomain
      # VPC association for private DNS
      VPCs:
        - VPCId: !Ref VpcId
          VPCRegion: !Ref AWS::Region
      # Tags for resource management
      HostedZoneTags:
        - Key: Name
          Value: !Sub "${ClusterName}-private-zone"
        - Key: kubernetes.io/cluster/${ClusterName}
          Value: owned

  # Create DNS records for the API server
  ApiServerRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      # Reference to the private hosted zone
      HostedZoneId: !Ref PrivateHostedZone
      # API server DNS name
      Name: !Sub "api.${ClusterDomain}"
      # Record type (A record for IPv4)
      Type: A
      # TTL for the record
      TTL: 300
      # Alias target (internal load balancer)
      AliasTarget:
        # DNS name of the internal load balancer
        DNSName: !GetAtt InternalLoadBalancer.DNSName
        # Hosted zone ID of the load balancer
        HostedZoneId: !GetAtt InternalLoadBalancer.CanonicalHostedZoneID
        # Evaluate target health
        EvaluateTargetHealth: true

  # Create DNS records for the internal API server
  InternalApiServerRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneId: !Ref PrivateHostedZone
      Name: !Sub "api-int.${ClusterDomain}"
      Type: A
      TTL: 300
      AliasTarget:
        DNSName: !GetAtt InternalLoadBalancer.DNSName
        HostedZoneId: !GetAtt InternalLoadBalancer.CanonicalHostedZoneID
        EvaluateTargetHealth: true
```

2. **Route53 Health Checks**

```yaml
# File: upi/aws/cloudformation/02_route53.yaml
  # Health check for the API server
  ApiServerHealthCheck:
    Type: AWS::Route53::HealthCheck
    Properties:
      # Health check configuration
      HealthCheckConfig:
        # Type of health check
        Type: HTTPS
        # Port to check
        Port: 6443
        # Resource path to check
        ResourcePath: /healthz
        # Fully qualified domain name to check
        FullyQualifiedDomainName: !Sub "api.${ClusterDomain}"
        # Request interval in seconds
        RequestInterval: 30
        # Failure threshold
        FailureThreshold: 3
        # Enable SSL verification
        EnableSNI: true
      # Tags for the health check
      HealthCheckTags:
        - Key: Name
          Value: !Sub "${ClusterName}-api-health-check"
```

3. **Route53 IAM Permissions**

```yaml
# File: upi/aws/cloudformation/03_iam.yaml
  # IAM policy for Route53 access
  Route53Policy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: !Sub "${ClusterName}-route53-policy"
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Action:
              - route53:GetHostedZone
              - route53:ListHostedZones
              - route53:CreateHostedZone
              - route53:DeleteHostedZone
              - route53:ChangeResourceRecordSets
              - route53:ListResourceRecordSets
              - route53:GetHealthCheck
              - route53:CreateHealthCheck
              - route53:DeleteHealthCheck
            Resource: "*"
      Roles:
        - !Ref MasterInstanceRole
        - !Ref WorkerInstanceRole
```

### Route53 Integration Best Practices

1. **DNS Record Management**
   - Use alias records for load balancers to avoid IP changes
   - Set appropriate TTL values for different record types
   - Use health checks for critical services
   - Implement DNS failover for high availability

2. **Security Considerations**
   - Use private hosted zones for internal DNS
   - Implement proper IAM permissions
   - Enable VPC DNS resolution
   - Use SSL/TLS for API server endpoints

3. **Monitoring and Maintenance**
   - Monitor DNS query metrics
   - Set up CloudWatch alarms for health checks
   - Regularly review and update DNS records
   - Implement DNS logging for troubleshooting

4. **Troubleshooting Route53 Issues**

```bash
# Check DNS resolution from within the VPC
dig +short api.private-cluster.example.com

# Verify health check status
aws route53 get-health-check-status --health-check-id <health-check-id>

# List all records in the hosted zone
aws route53 list-resource-record-sets --hosted-zone-id <hosted-zone-id>

# Test DNS resolution from different VPCs
aws route53 test-dns-answer --hosted-zone-id <hosted-zone-id> --record-name api.private-cluster.example.com --record-type A
```

5. **Common Route53 Issues and Solutions**

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| DNS resolution fails | VPC DNS settings | Enable VPC DNS resolution |
| Health check failures | Security group rules | Update security groups to allow health check traffic |
| Alias record issues | Load balancer configuration | Verify load balancer DNS name and hosted zone ID |
| Cross-account access | IAM permissions | Update IAM roles with proper Route53 permissions |

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