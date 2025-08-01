# workflow/orchestrator.py

from utils.logger import log_message
from excel.excel_loader import read_btmigrate_workbook
from api.managed_system import get_managed_system_by_ip
from utils.universal_cache import UniversalCache

def start_orchestration(cache: UniversalCache):
    records = read_btmigrate_workbook()

    if not records:
        log_message("❌ btmigrate_work.xlsx dosyası boş veya okunamadı.")
        return

    for i, row in enumerate(records, start=1):
        ip = row.get("ip address")
        if not ip:
            log_message(f"⛔ Satır {i}: IP adresi yok, atlandı.")
            continue

        existing_ms = get_managed_system_by_ip(cache, ip)
        if existing_ms:
            log_message(f"✅ Satır {i}: Managed System zaten var → {existing_ms.get('Name')}")
        else:
            log_message(f"🆕 Satır {i}: Yeni Managed System oluşturulmalı. (IP: {ip})")

        # Burada ileride dispatcher çağrılacak
        break  # 🧪 Test amaçlı sadece ilk satırı işleyip çıkıyoruz
