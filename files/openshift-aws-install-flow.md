# OpenShift AWS Installation Flow

This document outlines the core code structure, main processes, key call chains, and resource cleanup mechanisms related to AWS installation in the `installer` project. It includes references to key implementation code to help developers and operators understand the overall implementation.

---

## 1. Provider Structure and Main Methods

### Code Snippet
```go
// pkg/infrastructure/aws/clusterapi/aws.go
// Provider implements AWS CAPI installation.
type Provider struct {
    bestEffortDeleteIgnition bool
}
```
The Provider implements all core process interfaces for AWS installation.

---

## 2. Key Installation Process Methods and Code Explanation

### PreProvision
Responsible for creating IAM roles and handling AMI images.

```go
// pkg/infrastructure/aws/clusterapi/aws.go
// Lines: 57-93
func (*Provider) PreProvision(ctx context.Context, in clusterapi.PreProvisionInput) error {
    if err := createIAMRoles(ctx, in.InfraID, in.InstallConfig); err != nil {
        return fmt.Errorf("failed to create IAM roles: %w", err)
    }
    // ... omitted ...
    amiID, err := copyAMIToRegion(ctx, in.InstallConfig, in.InfraID, in.RhcosImage)
    if err != nil {
        return fmt.Errorf("failed to copy AMI: %w", err)
    }
    // Update Machine manifests
    for i := range in.MachineManifests {
        if awsMachine, ok := in.MachineManifests[i].(*capa.AWSMachine); ok {
            awsMachine.Spec.AMI.ID = ptr.To(amiID)
        }
    }
    return nil
}
```
- First creates IAM roles (`createIAMRoles`).
- Checks/copies RHCOS AMI image to target region (`copyAMIToRegion`).
- Updates AMI ID in Machine manifests.

---

### Ignition
Edits ignition files and injects load balancer information.

```go
// pkg/infrastructure/aws/clusterapi/aws.go
// Lines: 93-108
func (p Provider) Ignition(ctx context.Context, in clusterapi.IgnitionInput) ([]*corev1.Secret, error) {
    ignOutput, err := editIgnition(ctx, in)
    if err != nil {
        return nil, fmt.Errorf("failed to edit bootstrap master or worker ignition: %w", err)
    }
    ignSecrets := []*corev1.Secret{
        clusterapi.IgnitionSecret(ignOutput.UpdatedBootstrapIgn, in.InfraID, "bootstrap"),
        clusterapi.IgnitionSecret(ignOutput.UpdatedMasterIgn, in.InfraID, "master"),
        clusterapi.IgnitionSecret(ignOutput.UpdatedWorkerIgn, in.InfraID, "worker"),
    }
    return ignSecrets, nil
}
```
- Calls `editIgnition` to inject load balancer information.
- Generates Kubernetes Secret.

---

### InfraReady
Creates private DNS zones, Route53 records, etc.

```go
// pkg/infrastructure/aws/clusterapi/aws.go
// Lines: 108-230
func (*Provider) InfraReady(ctx context.Context, in clusterapi.InfraReadyInput) error {
    awsCluster := &capa.AWSCluster{}
    key := k8sClient.ObjectKey{
        Name:      in.InfraID,
        Namespace: capiutils.Namespace,
    }
    if err := in.Client.Get(ctx, key, awsCluster); err != nil {
        return fmt.Errorf("failed to get AWSCluster: %w", err)
    }
    awsSession, err := in.InstallConfig.AWS.Session(ctx)
    if err != nil {
        return fmt.Errorf("failed to get aws session: %w", err)
    }
    // ... omitted ...
    if in.InstallConfig.Config.AWS.UserProvisionedDNS == dns.UserProvisionedDNSEnabled {
        logrus.Debugf("User Provisioned DNS enabled, skipping dns record creation")
        return nil
    }
    // Create Route53 records
    if err := client.CreateOrUpdateRecord(ctx, &awsconfig.CreateRecordInput{
        Name:           apiName,
        Region:         awsCluster.Spec.Region,
        DNSTarget:      pubLB.DNSName,
        ZoneID:         aws.StringValue(zone.Id),
        AliasZoneID:    aliasZoneID,
        HostedZoneRole: "",
    }); err != nil {
        return fmt.Errorf("failed to create records for api in public zone: %w", err)
    }
    // ... omitted ...
}
```
- Supports user-defined DNS.
- Automatically creates Route53 records.

---

## 3. Destruction and Cleanup Process

### DestroyBootstrap
Removes SSH rules (security groups) for bootstrap nodes.

```go
// pkg/infrastructure/aws/clusterapi/aws.go
// Lines: 298-364
func (p *Provider) DestroyBootstrap(ctx context.Context, in clusterapi.BootstrapDestroyInput) error {
    // ... omitted ...
    if err := wait.PollUntilContextTimeout(ctx, 15*time.Second, timeout, true,
        func(ctx context.Context) (bool, error) {
            if err := removeSSHRule(ctx, in.Client, in.Metadata.InfraID); err != nil {
                // ... omitted ...
            }
            return isSSHRuleGone(ctx, session, region, sgID)
        },
    ); err != nil {
        // ... omitted ...
    }
    // ... omitted ...
}
```
- Polls until security group rules are removed.

### PostDestroy
Deletes the ignition S3 bucket.

```go
// pkg/infrastructure/aws/clusterapi/aws.go
// Lines: 428-451
func (p *Provider) PostDestroy(ctx context.Context, in clusterapi.PostDestroyerInput) error {
    region := in.Metadata.AWS.Region
    session, err := awsconfig.GetSessionWithOptions(
        awsconfig.WithRegion(region),
        awsconfig.WithServiceEndpoints(region, in.Metadata.AWS.ServiceEndpoints),
    )
    if err != nil {
        return fmt.Errorf("failed to create aws session: %w", err)
    }
    bucketName := awsmanifest.GetIgnitionBucketName(in.Metadata.InfraID)
    if err := removeS3Bucket(ctx, session, bucketName); err != nil {
        if p.bestEffortDeleteIgnition {
            logrus.Warnf("failed to delete ignition bucket %s: %v", bucketName, err)
            return nil
        }
        return fmt.Errorf("failed to delete ignition bucket %s: %w", bucketName, err)
    }
    return nil
}
```
- Calls `removeS3Bucket` to delete the S3 bucket.

---

## 4. Key Helper Functions

### Get VPC
```go
// pkg/infrastructure/aws/clusterapi/aws.go
// Lines: 230-273
func getVPCFromSubnets(ctx context.Context, awsSession *session.Session, region string, subnetIDs []string) (string, error) {
    // ... omitted ...
}
```
- Queries VPC ID using subnet IDs.

### Get NLB HostedZoneID
```go
// pkg/infrastructure/aws/clusterapi/aws.go
// Lines: 273-298
func getHostedZoneIDForNLB(ctx context.Context, awsSession *session.Session, region string, lbName string) (string, error) {
    // ... omitted ...
}
```
- Queries the HostedZoneID for NLB.

---

## 5. References and Location

- Main implementation file: `pkg/infrastructure/aws/clusterapi/aws.go`
- Related helper packages: `pkg/asset/installconfig/aws`, `pkg/asset/manifests/aws`, `pkg/types/aws`

---

For further analysis of specific functions, processes, or AWS resource interaction details, please refer to the files mentioned above or contact the maintainers. 