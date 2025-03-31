# **Kubeflow MLOps Example on OKD/OpenShift**

Kubeflow is a popular **MLOps platform** for deploying machine learning workflows on Kubernetes. Below is a step-by-step example of setting up a **Kubeflow pipeline** on **OKD/OpenShift** to train and deploy an ML model.

---

## **1. Prerequisites**
- **OKD/OpenShift Cluster** (v4.x recommended)
- **oc CLI** (OpenShift client)
- **kustomize** (for Kubeflow installation)
- **Persistent Storage** (for pipelines and artifacts)

---

## **2. Install Kubeflow on OKD/OpenShift**

### **Option 1: Using the Kubeflow Operator (Recommended)**
1. **Deploy the Kubeflow Operator**
   ```bash
   oc apply -k "github.com/kubeflow/manifests/apps/pipeline/upstream/operator/cluster-scoped-resources?ref=master"
   oc apply -k "github.com/kubeflow/manifests/apps/pipeline/upstream/operator/namespace-scoped-resources?ref=master"
   ```

2. **Create a Kubeflow Instance**
   ```bash
   cat <<EOF | oc apply -f -
   apiVersion: kubeflow.org/v1
   kind: Kubeflow
   metadata:
     name: kubeflow
     namespace: kubeflow
   spec:
     pipelines:
       enabled: true
   EOF
   ```

3. **Access the Kubeflow Dashboard**
   ```bash
   oc get route -n kubeflow kubeflow -o jsonpath='{.spec.host}'
   ```
    - Open the URL in a browser and log in.

---

### **Option 2: Manual Installation with kustomize**
If the operator doesn’t work, try:
```bash
git clone https://github.com/kubeflow/manifests.git
cd manifests
while ! kustomize build example | oc apply -f -; do echo "Retrying..."; sleep 10; done
```

---

## **3. Example: ML Pipeline for Training & Deploying a Model**

### **Step 1: Define a Kubeflow Pipeline**
Create a Python script (`pipeline.py`) using the Kubeflow Pipelines SDK:

```python
from kfp import dsl
from kfp import components

def preprocess_data(input_path: str, output_path: str):
    import pandas as pd
    from sklearn.model_selection import train_test_split
    
    df = pd.read_csv(input_path)
    train, test = train_test_split(df, test_size=0.2)
    train.to_csv(f"{output_path}/train.csv", index=False)
    test.to_csv(f"{output_path}/test.csv", index=False)

def train_model(data_path: str, model_path: str):
    from sklearn.ensemble import RandomForestClassifier
    import pandas as pd
    import joblib
    
    df = pd.read_csv(f"{data_path}/train.csv")
    X, y = df.drop("target", axis=1), df["target"]
    model = RandomForestClassifier().fit(X, y)
    joblib.dump(model, f"{model_path}/model.joblib")

@dsl.pipeline(name="ML Training Pipeline")
def ml_pipeline(data_path: str="/data", model_path: str="/model"):
    preprocess_task = components.create_component_from_func(
        preprocess_data,
        base_image="python:3.9"
    )(input_path=f"{data_path}/raw_data.csv", output_path=data_path)
    
    train_task = components.create_component_from_func(
        train_model,
        base_image="python:3.9-sklearn"
    )(data_path=data_path, model_path=model_path).after(preprocess_task)
```

### **Step 2: Upload & Run the Pipeline**
1. **Compile the pipeline**
   ```bash
   dsl-compile --py pipeline.py --output pipeline.yaml
   ```

2. **Upload to Kubeflow**
    - Go to the Kubeflow UI → **Pipelines** → **Upload Pipeline**
    - Select `pipeline.yaml`

3. **Run the Pipeline**
    - Click **Create Run**
    - Specify input parameters (e.g., `data_path=/mnt/data`)

---

## **4. Deploy the Model as a Service**
Once trained, deploy the model using **KServe (formerly KFServing)**.

1. **Install KServe**
   ```bash
   oc apply -f "https://github.com/kserve/kserve/releases/download/v0.10.0/kserve.yaml"
   ```

2. **Create an InferenceService**
   ```yaml
   apiVersion: serving.kserve.io/v1beta1
   kind: InferenceService
   metadata:
     name: sklearn-iris
   spec:
     predictor:
       sklearn:
         storageUri: "pvc://model-storage/model.joblib"
   ```

3. **Test the Model**
   ```bash
   curl http://sklearn-iris-default.<cluster-domain>/v1/models/sklearn-iris:predict -d '{"instances": [[5.1, 3.5, 1.4, 0.2]]}'
   ```

---

## **5. Monitoring & CI/CD Integration**
- **Monitoring**: Use **Prometheus + Grafana** (pre-installed in OKD)
- **CI/CD**: Trigger pipelines via **Tekton** or **Jenkins**

---

## **6. Cleanup**
```bash
oc delete kubeflow kubeflow -n kubeflow
oc delete project kubeflow
```

---

## **Conclusion**
✅ **Kubeflow on OKD/OpenShift** provides:
- **End-to-end MLOps pipelines** (data prep → training → deployment)
- **Scalable Kubernetes-native workflows**
- **Integration with KServe, Tekton, and monitoring tools**

Would you like a **more specific example** (e.g., TensorFlow, PyTorch, or AutoML)? Let me know! 🚀