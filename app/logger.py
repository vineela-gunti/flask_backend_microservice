# flask_backend_microservice/app/logger.py
import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()  # Logs will appear in terminal as well
        ]
    )
    logger = logging.getLogger(__name__)
    return logger
