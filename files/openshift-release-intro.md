# OpenShift Release Project Structure Analysis

## Top-Level Structure
- `ci-operator/`: CI workflow configuration, including:
    - `config/`: CI operator configs for component repositories.
    - `jobs/`: Prow job configs (mostly generated).
    - `step-registry/`: Reusable test steps and workflows.
    - `templates/`: Legacy black-box test workflows.
- `core-services/`: Core service and configuration manifests for clusters.
- `clusters/`: Cluster configuration manifests (some legacy, some current).
- `services/`: Additional/legacy service configuration (not applied to main cluster).
- `projects/`: Manifests for experimental, legacy, or non-critical services and deprecated build manifests.
- `tools/`: Tooling build manifests for container images and utility tools.
- `hack/`: Scripts and utilities for validation, automation, and maintenance.
- `docs/`: Documentation (including SOPs and guides).
- `.specstory/`, `.git/`: Internal/project management and version control.
- Project management and meta files: `README.md`, `LICENSE`, `Makefile`, `OWNERS`, `CONTRIBUTING.md`, etc.

## Summary
- The project is a monorepo for OpenShift CI/CD, cluster, and service configuration.
- It contains both current and legacy configuration for clusters, services, and CI workflows.
- There are directories for reusable tools, scripts, and documentation.
- The structure supports both new and legacy workflows, with a focus on maintainability and migration to newer systems.

## ci-operator Directory Outline

- **Purpose:**  
  The `ci-operator` directory contains configuration, templates, and reusable steps for defining and running CI workflows for OpenShift and related projects. It is central to how jobs are defined, orchestrated, and executed in the OpenShift CI system.

- **Key Subdirectories and Files:**
    - `config/`  
      Contains per-repository configuration files for the `ci-operator`. Each subdirectory corresponds to a different organization or project, and contains YAML files that define how builds and tests should be run for each component.
    - `jobs/`  
      Contains Prow job configuration files, mostly generated from the `ci-operator` configs. These define how and when jobs are triggered in the CI system.
    - `step-registry/`  
      Contains reusable definitions of steps, chains, and workflows for multi-stage jobs. This registry allows for modular and maintainable CI job definitions.
        - Example: `step-registry/openshift/installer/` contains steps and workflows related to OpenShift installer jobs.
    - `templates/`  
      Contains legacy black-box test workflow templates, primarily for backward compatibility. New workflows should use the step registry instead.
        - Example: `templates/openshift/installer/` contains YAML templates for cluster installation and end-to-end tests.
    - `platform-balance/`  
      Contains scripts and documentation for balancing test workloads across different cloud platforms to optimize resource usage.
    - `populate-secrets-from-bitwarden.sh`  
      (Deprecated) Previously used to populate secrets from Bitwarden; replaced by tooling in `core-services`.
    - `README.md`  
      Points to onboarding and architecture documentation for the CI operator.
    - `REHEARSALS.md`  
      Points to external documentation for job rehearsals.
    - `SECRETS.md`  
      Documents the management and usage of secrets in the CI infrastructure.

### Representative Code Snippets from ci-operator

#### 1. Example: ci-operator Config File (YAML)
This snippet shows how a component's build and test configuration is defined:

```yaml
*# ci-operator/config/openshift/oc-compliance/openshift-oc-compliance-master.yaml*
binary_build_commands: make build
build_root:
  image_stream_tag:
    name: release
    namespace: openshift
    tag: golang-1.19
releases:
  latest:
    candidate:
      architecture: amd64
      product: ocp
      stream: nightly
      version: "4.12"
resources:
  '*':
    limits:
      memory: 4Gi
    requests:
      cpu: 100m
      memory: 200Mi
tests:
- as: go-build
  commands: make build
  container:
    from: src
- as: e2e
  steps:
    cluster_profile: aws-3
    test:
    - as: e2e
      cli: latest
      commands: make e2e
      from: src
      resources:
        requests:
          cpu: 100m
    workflow: ipi-aws
```

#### 2. Example: Prow Job Config (YAML)
This snippet shows how a Prow job is defined to run a test using the ci-operator:

```yaml
*# ci-operator/jobs/openshift/oc-compliance/openshift-oc-compliance-master-presubmits.yaml*
presubmits:
  openshift/oc-compliance:
  - agent: kubernetes
    always_run: true
    branches:
    - ^master$
    cluster: build10
    context: ci/prow/e2e
    decorate: true
    name: pull-ci-openshift-oc-compliance-master-e2e
    spec:
      containers:
      - args:
        - --target=e2e
        command:
        - ci-operator
        image: ci-operator:latest
        imagePullPolicy: Always
        resources:
          requests:
            cpu: 10m
      serviceAccountName: ci-operator
```

#### 3. Example: Step Registry Entry (README)
The step registry holds reusable steps, chains, and workflows for jobs:

```markdown
# ci-operator/step-registry/README.md

The step registry holds definitions of steps, chains and workflows for re-use in
`ci-operator` multi-stage jobs. Definitions of terms and expected format can be
found in the [production server](https://steps.ci.openshift.org/).
```

#### 4. Example: Legacy Template (YAML)
A legacy template for a cluster installation and e2e test job:

```yaml
*# ci-operator/templates/openshift/installer/cluster-launch-installer-e2e.yaml*
kind: Template
apiVersion: template.openshift.io/v1

parameters:
- name: JOB_NAME
  required: true
- name: NAMESPACE
  required: true
- name: IMAGE_FORMAT
objects:
- kind: Pod
  apiVersion: v1
  metadata:
    name: ${JOB_NAME_SAFE}
    namespace: ${NAMESPACE}
  spec:
    containers:
    - name: test
      image: ${IMAGE_TESTS}
      command:
      - /bin/bash
      - -c
      - |
        #!/bin/bash
        set -euo pipefail
        # test logic here
``` 
