import os
import logging
from logging.handlers import RotatingFileHandler

from .config import setting

def setup_logging():
    logger = logging.getLogger("fastapi_app")
    logger.setLevel(logging.INFO)

    # 2. Định dạng log (Format)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 3. File Handler (Ghi vào file, xoay vòng file)
    file_handler = RotatingFileHandler(
        setting.log_file, 
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # 4. Stream Handler (Để log hiện ra cả ở terminal khi dev)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # 5. Thêm handlers vào logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger

# Khởi tạo instance logger để dùng chung toàn app
logger = setup_logging()