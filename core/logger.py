import logging
import os
from datetime import datetime

# Log dizini ve dosya yolları
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE_PATH = os.path.join(LOG_DIR, f"btmigrate_{timestamp}.log")
ERROR_FILE_PATH = os.path.join(LOG_DIR, f"btmigrate_error_{timestamp}.log")

def _initialize_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # INFO log handler
    info_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # ERROR log handler
    error_handler = logging.FileHandler(ERROR_FILE_PATH, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Console log handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Handler'ları ekle
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    # Başlangıç log'ları
    logging.info(f"🚀 Loglama başlatıldı: {LOG_FILE_PATH}")
    logging.info(f"🚨 Hatalar ayrıca burada: {ERROR_FILE_PATH}")

# Self-executing
_initialize_logger()

# Fonksiyonlar (standart)
def log_message(msg):
    logging.info(msg)

def log_error(code, msg, error_type="General"):
    logging.error(f"[{error_type}] Kod: {code} Message: {msg}")

def log_debug(msg):
    logging.debug(msg)

# Fonksiyonlar (satır özel)
def log_message_row(row_number, msg):
    logging.info(f"Row {row_number}: {msg}")

def log_error_row(row_number, code, msg, error_type="General"):
    logging.error(f"Row {row_number}: [{error_type}] Kod: {code} Message: {msg}")
