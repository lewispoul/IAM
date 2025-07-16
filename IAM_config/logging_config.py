
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Configure le système de logging"""
    log_dir = "/home/lppou/IAM/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configuration du logger principal
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                os.path.join(log_dir, 'iam.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()
