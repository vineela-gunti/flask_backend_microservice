# flask_backend_microservice/app/routes.py
from flask import request, jsonify
import base64
import uuid
from .logger import setup_logger
from .k8s.k8s_job import check_job_status, get_pod_name, fetch_pod_logs, create_k8s_job
import pymongo
import time

logger = setup_logger()

client = pymongo.MongoClient("mongodb://localhost:27018/")
db = client["code_execution_db"]
collection = db["executions"]

class CodeRequest:
    def __init__(self, language, code):
        self.language = language
        self.code = code

def setup_routes(app):
    @app.before_request
    def log_request():
        """ Log the incoming request details """
        logger.info(f"Received {request.method} request for {request.path}")
        logger.info(f"Request data: {request.get_data(as_text=True)}")

    @app.after_request
    def log_response(response):
        """ Log the outgoing response details """
        logger.info(f"Response status: {response.status}")
        logger.info(f"Response data: {response.get_data(as_text=True)}")
        return response

    @app.route("/execute", methods=["POST"])
    def execute_code():
        # Parsing the incoming JSON data
        data = request.get_json()
        logger.info(f"Request payload: {data}")
        code_request = CodeRequest(**data)

        if code_request.language.lower() != "python":
            logger.warning(f"Unsupported language: {code_request.language}")
            return jsonify({"detail": "Only Python is supported"}), 400

        # Decode Base64 Code
        try:
            decoded_code = base64.b64decode(code_request.code).decode("utf-8")
        except Exception:
            logger.error("Failed to decode base64 code")
            return jsonify({"detail": "Invalid base64-encoded code"}), 400

        execution_id = str(uuid.uuid4())

        # Store Code in MongoDB
        logger.info(f"Storing execution details for execution ID: {execution_id}")
        try:
            collection.insert_one({
                "execution_id": execution_id,
                "code": code_request.code,
                "output": None,
                "timestamp": "pending"
            })
            logger.info(f"Execution data stored for ID: {execution_id}")
        except Exception as e:
            logger.error(f"Error storing execution data: {e}")
            return jsonify({"detail": "Failed to store execution data"}), 500

        # Create Kubernetes Job
        job_name = f"code-execution-{execution_id}"
        try:
            logger.info(f"Creating Kubernetes job: {job_name}")
            create_k8s_job(job_name, decoded_code)
        except Exception as e:
            logger.error(f"Failed to create Kubernetes job: {e}")
            return jsonify({"detail": "Failed to create Kubernetes job"}), 500

        # Monitor job completion
        job_status = "pending"
        while job_status != "complete":
            job_status = check_job_status(job_name)
            logger.info(f"Job status: {job_status}")
            time.sleep(2)  # Polling interval

        # Fetch the pod logs after completion
        pod_name = get_pod_name(job_name)
        logs = fetch_pod_logs(pod_name)

        # Update MongoDB with the result
        logger.info(f"Updating MongoDB with logs for execution ID: {execution_id}")
        collection.update_one(
            {"execution_id": execution_id},
            {"$set": {"output": logs, "timestamp": "completed"}}
        )

        return jsonify({"execution_id": execution_id, "message": "Execution started"})
    
    @app.route("/result/<execution_id>", methods=["GET"])
    def get_result(execution_id):
        logger.info(f"Fetching result for execution ID: {execution_id}")
        result = collection.find_one({"execution_id": execution_id})
        if not result:
            logger.warning(f"Execution ID {execution_id} not found")
            return jsonify({"detail": "Execution ID not found"}), 404

        logger.info(f"Execution result found: {result['output']}")
        return jsonify({
            "execution_id": result["execution_id"],
            "code": result["code"],
            "output": result["output"],
            "timestamp": result["timestamp"]
        })
