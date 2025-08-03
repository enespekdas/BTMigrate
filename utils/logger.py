import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(LOG_DIR, f"btmigrate_{timestamp}.log")
    error_log_file = os.path.join(LOG_DIR, f"btmigrate_error_{timestamp}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    info_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    info_handler.setLevel(logging.DEBUG)
    info_handler.setFormatter(formatter)

    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    logging.info(f"🚀 Loglama başlatıldı: {log_file_path}")
    logging.info(f"🚨 Hatalar ayrıca burada: {error_log_file}")

# Standart log fonksiyonları
def log_message(msg):
    logging.info(msg)

def log_error(code, msg, error_type="General"):
    logging.error(f"[{error_type}] Kod: {code} Message: {msg}")

def log_debug(msg):
    logging.debug(msg)

# Satıra özel log fonksiyonları
def log_message_row(row_number, msg):
    logging.info(f"Row {row_number}: {msg}")

def log_error_row(row_number, code, msg, error_type="General"):
    logging.error(f"Row {row_number}: [{error_type}] Kod: {code} Message: {msg}")

def log_debug_row(row_number: int, message: str):
    logging.debug(f"[DEBUG] Row {row_number}: {message}")
