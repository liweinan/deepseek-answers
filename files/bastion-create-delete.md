# Bastion Host Creation in OpenShift CI Operator

The OpenShift CI Operator project provisions the AWS bastion host using a combination of a shell script and a CloudFormation template. The main logic is found in:

- `step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh`
- The CloudFormation template is generated dynamically within this script.

## Process Overview

1. **Gather VPC and Subnet Information**
    - The script determines the VPC ID and a public subnet to use for the bastion host, either from shared files or by querying AWS.

2. **Prepare Bastion Host AMI and Ignition**
    - If a custom AMI is not provided, the script fetches the latest RHCOS AMI for the region.
    - An ignition config for the bastion is uploaded to S3.

3. **Generate CloudFormation Template**
    - The script writes a CloudFormation YAML template to disk, defining:
        - An IAM role and instance profile for the bastion
        - A security group with SSH and proxy ports open
        - The EC2 instance for the bastion host, with user data (ignition) and block device mappings
    - **File:** `step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh`  
      **Lines:** 62–211 (template generation)

4. **Create the Bastion Host Stack**
    - The script runs:
      ```bash
      *# step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh (lines 312–324)*
      aws --region $REGION cloudformation create-stack --stack-name ${stack_name} \
          --template-body file://${bastion_cf_tpl_file} \
          --capabilities CAPABILITY_NAMED_IAM \
          --parameters \
              ParameterKey=VpcId,ParameterValue="${VpcId}"  \
              ParameterKey=BastionHostInstanceType,ParameterValue="${BastionHostInstanceType}"  \
              ParameterKey=Machinename,ParameterValue="${stack_name}"  \
              ParameterKey=PublicSubnet,ParameterValue="${PublicSubnet}" \
              ParameterKey=ControlPlaneSecurityGroup,ParameterValue="${ControlPlaneSecurityGroup}" \
              ParameterKey=AmiId,ParameterValue="${ami_id}" \
              ParameterKey=BastionIgnitionLocation,ParameterValue="${ign_location}"  &
      ```
    - It waits for stack creation to complete and extracts outputs (instance ID, DNS, IP).

5. **Expose Bastion Host Info**
    - The script writes the public/private DNS and IP to shared files for use by other steps.
    - **File:** `step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh`  
      **Lines:** 340–350 (extracting outputs)

## Key Code Snippets

**CloudFormation Stack Creation:**
```bash
*# step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh (lines 312–324)*
aws --region $REGION cloudformation create-stack --stack-name ${stack_name} \
    --template-body file://${bastion_cf_tpl_file} \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameters \
        ParameterKey=VpcId,ParameterValue="${VpcId}"  \
        ParameterKey=BastionHostInstanceType,ParameterValue="${BastionHostInstanceType}"  \
        ParameterKey=Machinename,ParameterValue="${stack_name}"  \
        ParameterKey=PublicSubnet,ParameterValue="${PublicSubnet}" \
        ParameterKey=ControlPlaneSecurityGroup,ParameterValue="${ControlPlaneSecurityGroup}" \
        ParameterKey=AmiId,ParameterValue="${ami_id}" \
        ParameterKey=BastionIgnitionLocation,ParameterValue="${ign_location}"  &
```

**CloudFormation Template (Excerpt):**
```yaml
*# step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh (lines 62–211)*
Resources:
  BastionInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref AmiId
      IamInstanceProfile: !Ref BastionInstanceProfile
      InstanceType: !Ref BastionHostInstanceType
      NetworkInterfaces:
      - AssociatePublicIpAddress: "True"
        DeviceIndex: "0"
        GroupSet:
          - !GetAtt BastionSecurityGroup.GroupId
          - !If [ "HasControlPlaneSecurityGroupSet", !Ref "ControlPlaneSecurityGroup", !Ref "AWS::NoValue"]
        SubnetId: !Ref "PublicSubnet"
      Tags:
      - Key: Name
        Value: !Join ["", [!Ref Machinename]]
      BlockDeviceMappings:
        !If
          - "UseIgnition"
          - - DeviceName: /dev/xvda
              Ebs:
                VolumeSize: "500"
                VolumeType: gp2
          - - DeviceName: /dev/sda1
              Ebs:
                VolumeSize: "500"
                VolumeType: gp2
      UserData:
        !If
          - "UseIgnition"
          - Fn::Base64:
              !Sub
                - '{"ignition":{"config":{"replace":{"source":"${IgnitionLocation}"}},"version":"3.0.0"}}'
                - IgnitionLocation: !Ref BastionIgnitionLocation
          - !Ref "AWS::NoValue"
```

**Extracting Outputs:**
```bash
*# step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh (lines 340–350)*
INSTANCE_ID="$(aws --region "${REGION}" cloudformation describe-stacks --stack-name "${stack_name}" \
--query 'Stacks[].Outputs[?OutputKey == `BastionInstanceId`].OutputValue' --output text)"
BASTION_HOST_PUBLIC_DNS="$(aws --region "${REGION}" cloudformation describe-stacks --stack-name "${stack_name}" \
  --query 'Stacks[].Outputs[?OutputKey == `PublicDnsName`].OutputValue' --output text)"
```

## Summary Table

| Filename                                                        | Line Range   | Purpose                                 |
|------------------------------------------------------------------|--------------|-----------------------------------------|
| `step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh` | 62–211       | CloudFormation template generation      |
| `step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh` | 312–324      | CloudFormation stack creation command   |
| `step-registry/aws/provision/bastionhost/aws-provision-bastionhost-commands.sh` | 340–350      | Extracting outputs (instance ID, DNS)   |

## Summary

- **The bastion host is created using a dynamically generated CloudFormation template.**
- **The script handles all AWS resource creation, including IAM, security groups, and the EC2 instance.**
- **Outputs (instance ID, DNS, IP) are extracted for use by other CI steps.**

---


VPC Deletion Logic in the AWS Directory

**Yes, the AWS directory does contain VPC delete logic**, but it's implemented through **CloudFormation stack deletion** rather than direct VPC deletion scripts.

### Key Findings:

1. **VPC Creation**: VPCs are created using CloudFormation stacks:
    - `ci-operator/step-registry/aws/provision/vpc/shared/aws-provision-vpc-shared-commands.sh` - Creates shared VPCs
    - `ci-operator/step-registry/aws/provision/vpc/disconnected/aws-provision-vpc-disconnected-commands.sh` - Creates disconnected VPCs

2. **VPC Deletion**: VPCs are deleted through the **stacks deprovision script**:
    - `ci-operator/step-registry/aws/deprovision/stacks/aws-deprovision-stacks-commands.sh` - This script deletes CloudFormation stacks, including VPC stacks

### How VPC Deletion Works:

1. **Stack Tracking**: During VPC creation, the stack names are added to cleanup lists:
   ```bash
   # For regular VPCs
   echo ${STACK_NAME} >> "${SHARED_DIR}/to_be_removed_cf_stack_list"
   
   # For shared VPCs  
   echo ${STACK_NAME} >> "${SHARED_DIR}/to_be_removed_cf_stack_list_shared_account"
   ```

2. **Stack Deletion**: The deprovision script reads these lists and deletes the stacks:
   ```bash
   # From aws-deprovision-stacks-commands.sh
   stack_list="${SHARED_DIR}/to_be_removed_cf_stack_list"
   if [ -e "${stack_list}" ]; then
       echo "Deleting stacks:"
       cat ${stack_list}
       export AWS_SHARED_CREDENTIALS_FILE="${CLUSTER_PROFILE_DIR}/.awscred"
       delete_stacks ${stack_list}
   fi
   ```

3. **Deletion Function**: The actual deletion uses AWS CloudFormation:
   ```bash
   function delete_stacks() {
       local stack_list=$1
       for stack_name in `tac ${stack_list}`; do 
           echo "Deleting stack ${stack_name} ..."
           aws --region $REGION cloudformation delete-stack --stack-name "${stack_name}"
           aws --region $REGION cloudformation wait stack-delete-complete --stack-name "${stack_name}"
       done
   }
   ```

### Documentation Reference:
The deprovision stacks reference file explicitly mentions VPC deletion:
```yaml
# From aws-deprovision-stacks-ref.yaml
documentation: |-
  Delete AWS CloudFormation stacks, e.g, apps dns stack, bastion host stack, vpc stack.
```

**Summary**: The AWS directory contains VPC deletion logic, but it's implemented through CloudFormation stack deletion rather than direct VPC API calls. This approach ensures that all VPC-related resources (subnets, route tables, internet gateways, etc.) are properly cleaned up when the stack is deleted.