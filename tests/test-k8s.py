import pytest
from unittest.mock import patch, MagicMock

from app.k8s.k8s_job import check_job_status, get_pod_name, fetch_pod_logs, create_k8s_job

@pytest.fixture
def mock_k8s_api():
    """ Mock Kubernetes API Clients """
    with patch("app.k8s.k8s_job.k8s_api") as mock_k8s, \
         patch("app.k8s.k8s_job.core_v1_api") as mock_core_v1:
        yield mock_k8s, mock_core_v1

def test_check_job_status_complete(mock_k8s_api):
    """ Test checking job status when job is completed """
    mock_k8s, _ = mock_k8s_api
    mock_k8s.read_namespaced_job.return_value.status.succeeded = 1

    status = check_job_status("test-job")
    assert status == "complete"

def test_check_job_status_pending(mock_k8s_api):
    """ Test checking job status when job is still pending """
    mock_k8s, _ = mock_k8s_api
    mock_k8s.read_namespaced_job.return_value.status.succeeded = 0

    status = check_job_status("test-job")
    assert status == "pending"

def test_check_job_status_exception(mock_k8s_api):
    """ Test checking job status when an exception occurs """
    mock_k8s, _ = mock_k8s_api
    mock_k8s.read_namespaced_job.side_effect = Exception("K8s API error")

    status = check_job_status("test-job")
    assert status == "pending"

def test_get_pod_name(mock_k8s_api):
    """ Test getting pod name from a job """
    _, mock_core_v1 = mock_k8s_api
    mock_pod = MagicMock()
    mock_pod.metadata.name = "test-pod"
    mock_core_v1.list_namespaced_pod.return_value.items = [mock_pod]

    pod_name = get_pod_name("test-job")
    assert pod_name == "test-pod"

def test_get_pod_name_no_pods(mock_k8s_api):
    """ Test getting pod name when no pods are found """
    _, mock_core_v1 = mock_k8s_api
    mock_core_v1.list_namespaced_pod.return_value.items = []

    pod_name = get_pod_name("test-job")
    assert pod_name is None

def test_fetch_pod_logs(mock_k8s_api):
    """ Test fetching logs from a pod """
    _, mock_core_v1 = mock_k8s_api
    mock_core_v1.read_namespaced_pod_log.return_value = "Execution output"

    logs = fetch_pod_logs("test-pod")
    assert logs == "Execution output"

def test_fetch_pod_logs_no_pod(mock_k8s_api):
    """ Test fetching logs when no pod is found """
    logs = fetch_pod_logs(None)
    assert logs == "No logs available"

def test_create_k8s_job_success(mock_k8s_api):
    """ Test successful creation of a Kubernetes job """
    mock_k8s, _ = mock_k8s_api
    mock_k8s.create_namespaced_job.return_value = None  # Mock successful job creation

    job_name = create_k8s_job("test-job", "print('Hello, Kubernetes!')")
    assert job_name == "test-job"

def test_create_k8s_job_failure(mock_k8s_api):
    """ Test failure when creating a Kubernetes job """
    mock_k8s, _ = mock_k8s_api
    mock_k8s.create_namespaced_job.side_effect = Exception("Failed to create job")

    with pytest.raises(Exception, match="Failed to create job"):  
        create_k8s_job("test-job", "print('Hello, Kubernetes!')")
