# flask_backend_microservice/app/__init__.py
from flask import Flask
from .logger import setup_logger
from .routes import setup_routes
from .models import collection  # Import the collection from models.py

app = Flask(__name__)

# Set up logging
logger = setup_logger()

# Register routes
setup_routes(app)

# Export app and collection for testing
__all__ = ["app", "collection"]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
