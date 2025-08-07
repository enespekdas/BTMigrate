import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import auth.login  # 🔐 Authentication işlemi import anında gerçekleşir

from core.cache_initializer import initialize_cache
from workflow.orchestrator import start_orchestration
from utils.logger import setup_logging
from generator.prepare_workbook import prepare_workbook  # (isteğe bağlı)
from excel.output_writer import initialize_output_workbook  # ✅ Output Excel başlatıcı

def main():
    setup_logging()  # ✅ Artık sadece burada loglama başlatılıyor

    # 🧪 Hazırlık aşaması (normalize Excel üretimi)
    prepare_workbook()

    # 🧠 Cache başlat
    #cache = initialize_cache()

    # 📄 Output Excel'i başlat
    #initialize_output_workbook()  # ✅ Eklendi

    # 🚀 Orkestrasyonu başlat
    #start_orchestration(cache)

if __name__ == "__main__":
    main()
