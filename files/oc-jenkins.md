# **Jenkins Pipeline手把手教程 - 为OpenShift测试设计**

## **1. Jenkins Pipeline基础概念**

### **1.1 什么是Pipeline?**
- **Pipeline**是Jenkins中实现持续集成/交付(CI/CD)的核心功能
- 使用代码(Groovy语法)定义整个构建、测试、部署流程
- 两种主要语法：
    - **Declarative**(声明式)：更结构化，适合新手
    - **Scripted**(脚本式)：更灵活，适合复杂场景

### **1.2 核心概念**
| 概念 | 说明 |
|------|------|
| **Node** | 执行Pipeline的工作节点 |
| **Stage** | 流程中的逻辑分组(如构建、测试) |
| **Step** | 单个具体操作(如执行shell命令) |
| **Agent** | 指定在哪里运行Pipeline |

## **2. 环境准备**

### **2.1 安装要求**
1. 已安装Jenkins(推荐2.346+版本)
2. 安装必要插件：
    - Pipeline
    - Kubernetes Plugin(如果连接OpenShift)
    - Git Plugin
    - Blue Ocean(可选，可视化界面)

```bash
# 检查Jenkins是否运行
systemctl status jenkins

# 安装常用插件(通过Jenkins UI)
Manage Jenkins > Manage Plugins > 搜索安装
```

### **2.2 OpenShift连接配置**
1. 在Jenkins中配置OpenShift凭证：
    - `Credentials` > `System` > `Global credentials` > `Add Credentials`
    - 选择"Secret text"，填入OpenShift的`oc login` token

2. 测试连接：
```groovy
// 测试脚本
node {
    withCredentials([string(credentialsId: 'openshift-token', variable: 'OC_TOKEN')]) {
        sh '''
        oc login https://your.openshift.server --token=$OC_TOKEN
        oc get pods
        '''
    }
}
```

## **3. 完整Pipeline示例**

### **3.1 Declarative Pipeline示例**
```groovy
pipeline {
    agent any
    
    environment {
        OC_CLI = credentials('openshift-token')  // 引用凭证
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
            junit '**/target/surefire-reports/*.xml'  // 收集测试报告
            archiveArtifacts artifacts: '**/target/*.jar'
        }
        failure {
            emailext body: '构建失败: ${BUILD_URL}', 
                     subject: 'Jenkins构建失败', 
                     to: 'team@example.com'
        }
    }
}
```

### **3.2 关键部分详解**

#### **1. Agent配置**
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

#### **2. OpenShift操作最佳实践**
```groovy
stage('Safe Deployment') {
    steps {
        script {
            try {
                // 蓝绿部署策略
                sh 'oc rollout latest dc/myapp'
                timeout(time: 5, unit: 'MINUTES') {
                    sh 'oc rollout status dc/myapp --watch'
                }
            } catch (err) {
                sh 'oc rollout undo dc/myapp'
                error "部署失败，已回滚"
            }
        }
    }
}
```

#### **3. 参数化构建**
```groovy
parameters {
    choice(name: 'DEPLOY_ENV', choices: ['dev', 'staging', 'prod'], description: '选择部署环境')
    string(name: 'IMAGE_TAG', defaultValue: 'latest', description: '镜像标签')
}
```

## **4. 高级技巧**

### **4.1 共享库(Shared Libraries)**
1. 创建共享库仓库：
   ```
   /vars
     └── openshift.groovy
   /src
     └── org
         └── utils
             └── OpenShiftUtils.groovy
   ```

2. 示例内容(`vars/openshift.groovy`)：
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

3. 在Pipeline中使用：
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

### **4.2 性能优化技巧**
1. **并行执行**：
```groovy
stage('Parallel Tests') {
    parallel {
        stage('Unit Test') { steps { sh './run-unit-tests' } }
        stage('Integration Test') { steps { sh './run-integration-tests' } }
    }
}
```

2. **缓存依赖**：
```groovy
stage('Build') {
    steps {
        sh '''
        // 缓存Maven依赖
        if [ -d ~/.m2/repository ]; then
            mv ~/.m2/repository /tmp/m2_cache
        fi
        mvn clean package
        '''
    }
}
```

## **5. 调试与维护**

### **5.1 常见问题排查**
1. **权限问题**：
    - 错误：`Error from server (Forbidden)`
    - 解决：检查OpenShift ServiceAccount权限
   ```bash
   oc policy add-role-to-user edit system:serviceaccount:jenkins:default -n target-namespace
   ```

2. **连接超时**：
    - 在Jenkins全局配置中增加超时时间：
   ```groovy
   timeout(time: 30, unit: 'MINUTES') {
       sh 'oc get pods'
   }
   ```

### **5.2 监控与日志**
1. 添加日志收集：
```groovy
post {
    always {
        sh 'oc logs dc/myapp > app.log'
        archiveArtifacts artifacts: 'app.log'
    }
}
```

2. 集成Prometheus监控：
```groovy
stage('Metrics') {
    steps {
        sh '''
        curl -X POST http://prometheus:9090/-/reload
        '''
    }
}
```

## **6. 可视化与报告**

### **6.1 Blue Ocean界面**
1. 安装Blue Ocean插件后：
    - 直观查看Pipeline执行情况
    - 轻松诊断失败阶段
    - 分支和PR的自动检测

![Blue Ocean界面示例](https://www.jenkins.io/doc/book/resources/images/blueocean-pipeline.png)

### **6.2 测试报告集成**
```groovy
post {
    always {
        junit '**/target/surefire-reports/*.xml'
        cucumber '**/target/cucumber-reports/*.json'
    }
}
```

## **7. 完整CI/CD流程示例**

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
                         message: "构建失败: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            }
            success {
                slackSend channel: '#notifications', 
                         message: "部署成功: ${env.BUILD_URL}"
            }
        }
    }
}
```

## **最佳实践总结**
1. **模块化设计**：将复杂流程拆分为多个阶段
2. **凭证安全**：永远不要硬编码敏感信息
3. **错误处理**：实现自动回滚机制
4. **资源清理**：Pipeline结束后清理测试资源
5. **文档化**：为每个Pipeline添加注释说明

通过这个教程，您应该能够：
✅ 创建基本的Jenkins Pipeline  
✅ 集成OpenShift操作  
✅ 实现自动化测试和部署  
✅ 处理常见错误和优化性能

需要进一步帮助可以查阅：
- [Jenkins官方文档](https://www.jenkins.io/doc/)
- [OpenShift Jenkins插件文档](https://docs.openshift.com/container-platform/4.10/cicd/jenkins/)