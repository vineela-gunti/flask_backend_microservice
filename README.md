# Backend Microservice for Python Code Execution

This microservice allows clients to submit base64-encoded Python code for execution in a **Kubernetes job** running inside a **Docker container**. The execution results are stored in **MongoDB** and can be retrieved using an execution ID.

## 🚀 Features
- Accepts **Python code** (Base64-encoded) via a REST API.
- Executes the code inside a **Kubernetes job** (secured inside a container).
- Stores code and execution output in **MongoDB**.
- Provides an API to **retrieve execution results**.

---

## 📌 **Prerequisites**
Ensure you have the following installed before setting up the application.

### **Git clone the repository**
```bash
git clone https://github.com/vineela-gunti/flask_backend_microservice.git
cd flask_backend_microservice.git
```
---
### **Docker Installation**
For macOS users:
- Download **Docker Desktop** from [here](https://www.docker.com/products/docker-desktop/).
- Install it based on your system:
  - **Apple Silicon (M1, M2, M3)**
  - **Intel Chip**
- Mount the image manually:
  ```bash
  hdiutil attach ~/Downloads/Docker.dmg
  ```
- Go to **Finder → Applications** and **drag & drop Docker** into the Applications folder.
- Start Docker.

---
For Windows Users:
- Download Docker Desktop from here (https://www.docker.com/get-started/#:~:text=Download%20for%20Windows%20%2D%20AMD64).
- Run the installer and follow the installation steps.
- Ensure WSL 2 Backend is enabled (if using Windows Subsystem for Linux).
- After installation, restart your system.
- Open Docker Desktop and ensure it's running.
---

Verify Docker installation by running:

```bash
docker --version
```
---

### **Minikube Installation (For Kubernetes)**
Install **Minikube** using Homebrew:
```bash
brew install minikube
minikube start
```
This starts a Kubernetes cluster for executing jobs.

---

### **Install Dependencies**

```bash
pip3 install -r requirements.txt
```
---

## 📦 **MongoDB Setup**
Run a MongoDB container using Docker:

```bash
docker run -d -p 27018:27017 --name mongo-container mongo --bind_ip 0.0.0.0
```
Exposing the mongodb container to run on host post 27018 with mongo running on it's default port 27017 inside the container

Check if MongoDB is running:
```bash
docker ps
```
---

## ▶️ **Running the Application**

```bash
python run.py
```
---

## 🧪 **Testing the API manually to check the functionality of the application**
### **Execute Python Code**
```bash
curl -X POST "http://127.0.0.1:8000/execute" \
     -H "Content-Type: application/json" \
     -d '{"language": "python", "code": "cHJpbnQoIkhlbGxvLCBXb3JsZCIp"}'
```
### **Retrieve Execution Results**
```bash
curl -X GET http://127.0.0.1:8000/result/<execution-id?>
```
---

### **Postman Collection Setup**
- Import the postman-collection/flask-backend-api.json file in Postman
- Click on 'Runner' present at the bottom right corner.
- Drag and drop the collection 'Flask Backend API' in the Run order
- Click on 'Start Run'
- To view the response body and other logs, Select View -> Show POstman Console 

---

### **Running Unit Tests**
Unit tests for API checkpoints and MongoDB integration
```bash
python3 -m pytest tests/test-app.py

```
Unit tests for kubernetes integration
```bash
python3 -m pytest tests/test-k8s.py

```

---

## 🛠 **Debugging Issues**
### **Check if the Kubernetes job was created**
```bash
kubectl get jobs
```

### **Check logs of the Kubernetes job**
```bash
kubectl logs job/<job-id>
```
### **Verify if the data is being stored in the MongoDB container**

```bash
docker exec -it mongo-container mongosh
use code_execution_db
show collections
db.executions.find({"execution_id": "<execution-id>"}).pretty()
```

---

### **Scope for Automation**
**Jenkins Integration:** Set up Jenkins CI/CD pipelines to automate application deployment and unit testing.
- **Deployment Pipeline:** The pipeline includes stages such as:
  - Code checkout from version control.
  - Installation of necessary prerequisites.
  - Running the application.
  - Integrating Postman to execute API testing through collections.
- **Testing Pipeline:** Automatically triggered in the post section of the deployment pipeline to run unit tests and ensure the quality of the application.
- **Cleanup Pipeline:** A dedicated pipeline that:
  - Deletes Kubernetes jobs.
  - Stops the application.
  - Removes MongoDB containers to ensure a clean environment.
