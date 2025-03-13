import sys
import os
import pytest
import json
import base64
from unittest.mock import patch, MagicMock

# Ensure the app module is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.routes import collection

def test_execute_code_success():
    client = app.test_client()
    encoded_code = base64.b64encode(b'print("Hello, World!")').decode('utf-8')
    data = {"language": "python", "code": encoded_code}

    with patch("app.k8s.k8s_job.k8s_api.create_namespaced_job") as mock_k8s_job, \
         patch("app.routes.collection.insert_one") as mock_mongo_insert, \
         patch("app.routes.check_job_status", return_value="complete"), \
         patch("app.routes.get_pod_name", return_value="test-pod"), \
         patch("app.routes.fetch_pod_logs", return_value="Hello, World!"), \
         patch("app.routes.collection.update_one") as mock_mongo_update:
        
        
        response = client.post("/execute", data=json.dumps(data), content_type="application/json")
        
        assert response.status_code == 200
        assert "execution_id" in response.json
        mock_k8s_job.assert_called_once()
        mock_mongo_insert.assert_called_once()
        mock_mongo_update.assert_called_once()

def test_execute_code_invalid_language():
    client = app.test_client()
    data = {"language": "java", "code": "somecode"}
    response = client.post("/execute", data=json.dumps(data), content_type="application/json")
    
    assert response.status_code == 400
    assert response.json == {"detail": "Only Python is supported"}

def test_execute_code_invalid_base64():
    client = app.test_client()
    data = {"language": "python", "code": "notbase64"}
    response = client.post("/execute", data=json.dumps(data), content_type="application/json")
    
    assert response.status_code == 400
    assert response.json == {"detail": "Invalid base64-encoded code"}

def test_get_result_found():
    client = app.test_client()
    fake_execution = {
        "execution_id": "12345",
        "code": "cHJpbnQoXCJIZWxsbyBXb3JsZFwiKQ==",
        "output": "Hello World",
        "timestamp": "completed"
    }
    
    with patch.object(collection, "find_one", return_value=fake_execution):
        response = client.get("/result/12345")
        
        assert response.status_code == 200
        assert response.json["output"] == "Hello World"

def test_get_result_not_found():
    client = app.test_client()
    
    with patch.object(collection, "find_one", return_value=None):
        response = client.get("/result/99999")
        
        assert response.status_code == 404
        assert response.json == {"detail": "Execution ID not found"}