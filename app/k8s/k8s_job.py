# flask_backend_microservice/app/k8s/job_manager.py
from kubernetes import client as k8s_client, config
from kubernetes.client.exceptions import ApiException  

# Load Kubernetes config
config.load_kube_config()
k8s_api = k8s_client.BatchV1Api()
core_v1_api = k8s_client.CoreV1Api()

def check_job_status(job_name):
    """ Check the status of the job """
    try:
        job = k8s_api.read_namespaced_job(name=job_name, namespace="default")
        if job.status.succeeded == 1:
            return "complete"
        return "pending"
    except ApiException as e:  
        print(f"Kubernetes API Error: {e}")  
        return "pending"
    except Exception as e:  
        print(f"Unexpected error: {e}")
        return "pending"

def get_pod_name(job_name):
    """ Get the pod name associated with the job """
    pods = core_v1_api.list_namespaced_pod(namespace="default", label_selector=f"job-name={job_name}")
    if pods.items:
        return pods.items[0].metadata.name
    return None

def fetch_pod_logs(pod_name):
    """ Fetch the logs from the pod """
    if pod_name:
        logs = core_v1_api.read_namespaced_pod_log(name=pod_name, namespace="default")
        return logs
    return "No logs available"

def create_k8s_job(job_name, decoded_code):
    """ Create Kubernetes job for code execution """
    job_manifest = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": job_name},
        "spec": {
            "template": {
                "spec": {
                    "containers": [{
                        "name": "python-executor",
                        "image": "python:3.9",
                        "command": ["python", "-c", decoded_code],
                    }],
                    "restartPolicy": "Never"
                }
            }
        }
    }

    try:
        k8s_api.create_namespaced_job(namespace="default", body=job_manifest)
        return job_name
    except k8s_client.exceptions.ApiException as e:
        raise Exception(f"Failed to create Kubernetes job: {e}")
