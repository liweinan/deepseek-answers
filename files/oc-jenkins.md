# **Jenkins Pipeline Step-by-Step Tutorial - Designed for OpenShift Testing**

## **1. Jenkins Pipeline Basic Concepts**

### **1.1 What is a Pipeline?**
- **Pipeline** is the core functionality in Jenkins for implementing continuous integration/delivery (CI/CD)
- Uses code (Groovy syntax) to define the entire build, test, and deployment process
- Two main syntaxes:
    - **Declarative**: More structured, suitable for beginners
    - **Scripted**: More flexible, suitable for complex scenarios

### **1.2 Core Concepts**
| Concept | Description |
|------|------|
| **Node** | Work node that executes the Pipeline |
| **Stage** | Logical grouping in the process (e.g., build, test) |
| **Step** | Single specific operation (e.g., execute shell command) |
| **Agent** | Specifies where to run the Pipeline |

## **2. Environment Setup**

### **2.1 Installation Requirements**
1. Jenkins installed (recommended version 2.346+)
2. Install necessary plugins:
    - Pipeline
    - Kubernetes Plugin (if connecting to OpenShift)
    - Git Plugin
    - Blue Ocean (optional, visual interface)

```bash
# Check if Jenkins is running
systemctl status jenkins

# Install common plugins (via Jenkins UI)
Manage Jenkins > Manage Plugins > Search and install
```

### **2.2 OpenShift Connection Configuration**
1. Configure OpenShift credentials in Jenkins:
    - `Credentials` > `System` > `Global credentials` > `Add Credentials`
    - Select "Secret text", enter OpenShift's `oc login` token

2. Test connection:
```groovy
// Test script
node {
    withCredentials([string(credentialsId: 'openshift-token', variable: 'OC_TOKEN')]) {
        sh '''
        oc login https://your.openshift.server --token=$OC_TOKEN
        oc get pods
        '''
    }
}
```

## **3. Complete Pipeline Example**

### **3.1 Declarative Pipeline Example**
```groovy
pipeline {
    agent any
    
    environment {
        OC_CLI = credentials('openshift-token')  // Reference credentials
        NAMESPACE = 'test-env'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', 
                     url: 'https://github.com/yourrepo/openshift-tests.git'
            }
        }
        
        stage('Build App') {
            steps {
                sh 'mvn clean package'
                archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
            }
        }
        
        stage('Deploy to OpenShift') {
            steps {
                sh '''
                oc login https://api.openshift.example.com --token=${OC_CLI}
                oc project ${NAMESPACE}
                oc apply -f k8s/deployment.yaml
                '''
            }
        }
        
        stage('Run Tests') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'mvn test'
                    }
                }
                stage('E2E Tests') {
                    steps {
                        sh 'npm run e2e'
                    }
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                sh '''
                oc get pods -n ${NAMESPACE}
                oc rollout status deployment/myapp -n ${NAMESPACE} --timeout=2m
                '''
            }
        }
    }
    
    post {
        always {
            junit '**/target/surefire-reports/*.xml'  // Collect test reports
            archiveArtifacts artifacts: '**/target/*.jar'
        }
        failure {
            emailext body: 'Build failed: ${BUILD_URL}', 
                     subject: 'Jenkins Build Failed', 
                     to: 'team@example.com'
        }
    }
}
```

### **3.2 Key Sections Explained**

#### **1. Agent Configuration**
```groovy
agent {
    kubernetes {
        label 'openshift-agent'
        yaml """
        apiVersion: v1
        kind: Pod
        metadata:
          labels:
            jenkins: agent
        spec:
          containers:
          - name: jnlp
            image: jenkins/jnlp-agent:latest
          - name: oc
            image: openshift/origin-cli:latest
            command: ['cat']
            tty: true
        """
    }
}
```

#### **2. OpenShift Operations Best Practices**
```groovy
stage('Safe Deployment') {
    steps {
        script {
            try {
                // Blue-green deployment strategy
                sh 'oc rollout latest dc/myapp'
                timeout(time: 5, unit: 'MINUTES') {
                    sh 'oc rollout status dc/myapp --watch'
                }
            } catch (err) {
                sh 'oc rollout undo dc/myapp'
                error "Deployment failed, rolled back"
            }
        }
    }
}
```

#### **3. Parameterized Build**
```groovy
parameters {
    choice(name: 'DEPLOY_ENV', choices: ['dev', 'staging', 'prod'], description: 'Select deployment environment')
    string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Image tag')
}
```

## **4. Advanced Techniques**

### **4.1 Shared Libraries**
1. Create shared library repository:
   ```
   /vars
     └── openshift.groovy
   /src
     └── org
         └── utils
             └── OpenShiftUtils.groovy
   ```

2. Example content (`vars/openshift.groovy`):
```groovy
def deploy(Map args) {
    withCredentials([string(credentialsId: args.credential, variable: 'OC_TOKEN']) {
        sh """
        oc login ${args.server} --token=$OC_TOKEN
        oc project ${args.namespace}
        oc apply -f ${args.file}
        """
    }
}
```

3. Use in Pipeline:
```groovy
@Library('my-shared-lib') _

pipeline {
    stages {
        stage('Deploy') {
            steps {
                openshift.deploy(
                    server: 'https://api.openshift.example.com',
                    namespace: 'prod',
                    file: 'k8s/deployment.yaml',
                    credential: 'openshift-prod-token'
                )
            }
        }
    }
}
```

### **4.2 Performance Optimization Tips**
1. **Parallel Execution**:
```groovy
stage('Parallel Tests') {
    parallel {
        stage('Unit Test') { steps { sh './run-unit-tests' } }
        stage('Integration Test') { steps { sh './run-integration-tests' } }
    }
}
```

2. **Cache Dependencies**:
```groovy
stage('Build') {
    steps {
        sh '''
        // Cache Maven dependencies
        if [ -d ~/.m2/repository ]; then
            mv ~/.m2/repository /tmp/m2_cache
        fi
        mvn clean package
        '''
    }
}
```

## **5. Debugging and Maintenance**

### **5.1 Common Issue Troubleshooting**
1. **Permission Issues**:
    - Error: `Error from server (Forbidden)`
    - Solution: Check OpenShift ServiceAccount permissions
   ```bash
   oc policy add-role-to-user edit system:serviceaccount:jenkins:default -n target-namespace
   ```

2. **Connection Timeout**:
    - Increase timeout in Jenkins global configuration:
   ```groovy
   timeout(time: 30, unit: 'MINUTES') {
       sh 'oc get pods'
   }
   ```

### **5.2 Monitoring and Logging**
1. Add log collection:
```groovy
post {
    always {
        sh 'oc logs dc/myapp > app.log'
        archiveArtifacts artifacts: 'app.log'
    }
}
```

2. Integrate Prometheus monitoring:
```groovy
stage('Metrics') {
    steps {
        sh '''
        curl -X POST http://prometheus:9090/-/reload
        '''
    }
}
```

## **6. Visualization and Reporting**

### **6.1 Blue Ocean Interface**
1. After installing Blue Ocean plugin:
    - Intuitively view Pipeline execution status
    - Easily diagnose failed stages
    - Automatic detection of branches and PRs

![Blue Ocean Interface Example](https://www.jenkins.io/doc/book/resources/images/blueocean-pipeline.png)

### **6.2 Test Report Integration**
```groovy
post {
    always {
        junit '**/target/surefire-reports/*.xml'
        cucumber '**/target/cucumber-reports/*.json'
    }
}
```

## **7. Complete CI/CD Flow Example**

```groovy
// Jenkinsfile
@pipeline
def call() {
    pipeline {
        agent any
        
        stages {
            stage('Checkout & Build') {
                steps {
                    checkout scm
                    sh 'mvn clean package'
                }
            }
            
            stage('Unit Test') {
                steps {
                    sh 'mvn test'
                }
                post {
                    always {
                        junit '**/target/surefire-reports/*.xml'
                    }
                }
            }
            
            stage('Build Image') {
                steps {
                    script {
                        docker.build("myapp:${env.BUILD_ID}")
                    }
                }
            }
            
            stage('Deploy to OpenShift') {
                steps {
                    openshift.withCluster() {
                        openshift.withProject('dev') {
                            def dc = openshift.selector('dc', 'myapp')
                            if (dc.exists()) {
                                dc.rollout().latest()
                            } else {
                                openshift.create('-f', 'k8s/deployment.yaml')
                            }
                        }
                    }
                }
            }
            
            stage('E2E Test') {
                steps {
                    sh 'npm run e2e'
                }
            }
        }
        
        post {
            failure {
                slackSend channel: '#alerts', 
                         message: "Build failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            }
            success {
                slackSend channel: '#notifications', 
                         message: "Deployment successful: ${env.BUILD_URL}"
            }
        }
    }
}
```

## **Best Practices Summary**
1. **Modular Design**: Break complex processes into multiple stages
2. **Credential Security**: Never hardcode sensitive information
3. **Error Handling**: Implement automatic rollback mechanisms
4. **Resource Cleanup**: Clean up test resources after Pipeline completion
5. **Documentation**: Add comments for each Pipeline

Through this tutorial, you should be able to:
✅ Create basic Jenkins Pipelines  
✅ Integrate OpenShift operations  
✅ Implement automated testing and deployment  
✅ Handle common errors and optimize performance

For further help, refer to:
- [Jenkins Official Documentation](https://www.jenkins.io/doc/)
- [OpenShift Jenkins Plugin Documentation](https://docs.openshift.com/container-platform/4.10/cicd/jenkins/)
