# app/models.py
import pymongo

# MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27018/")
db = client["code_execution_db"]
collection = db["executions"]
