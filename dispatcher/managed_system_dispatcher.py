# dispatcher/managed_system_dispatcher.py

from utils.logger import log_error_row, log_message_row
from api.managed_system import get_managed_system_by_ip
from handlers.managed_system.windows import process_windows_managed_system
from handlers.managed_system.linux import process_linux_managed_system
from handlers.managed_system.oracle import process_oracle_managed_system
from handlers.managed_system.mssql import process_mssql_managed_system
from typing import Optional

def dispatch_managed_system(row: dict, cache, row_number: int) -> Optional[int]:
    ip = row.get("ip address")
    os_value = row.get("OS", "").strip()
    os_info = os_value.lower()

    row["MS - Tür"] = os_value if os_value else "Bilinmiyor"

    if not ip:
        log_error_row(row_number, -99, "IP adresi eksik", "Dispatcher")
        row["MS - Genel Durum"] = "❌"
        row["MS - Zaten Var mı?"] = "Hayır"
        row["MS - Oluşturuldu mu?"] = "Hayır"
        return None

    existing = get_managed_system_by_ip(cache, ip)
    if existing:
        name = existing.get("Name")
        row["MS - Genel Durum"] = "✅"
        row["MS - Zaten Var mı?"] = "Evet"
        row["MS - Oluşturuldu mu?"] = "Hayır"
        log_message_row(row_number, f"✅ Zaten mevcut → {name}")
        return existing.get("ManagedSystemID")  # ✅ varsa bile ID dön

    row["MS - Zaten Var mı?"] = "Hayır"

    try:
        created_id = None
        if os_info == "windows":
            created_id = process_windows_managed_system(row, cache, row_number)
        elif os_info == "linux":
            created_id = process_linux_managed_system(row, cache, row_number)
        elif os_info == "oracle":
            created_id = process_oracle_managed_system(row, cache, row_number)
        elif os_info == "mssql":
            created_id = process_mssql_managed_system(row, cache, row_number)
        else:
            raise Exception(f"Tanımsız OS tipi: {os_info}")

        row["MS - Genel Durum"] = "✅"
        if not row.get("MS - Oluşturuldu mu?"):
            row["MS - Oluşturuldu mu?"] = "Hayır"
        row["MS - ID"] = created_id  # 🔧 orchestrator kullanacak
        return created_id

    except Exception as e:
        log_error_row(row_number, -101, f"Managed system dispatch hatası: {str(e)}", "Dispatcher")
        row["MS - Genel Durum"] = "❌"
        row["MS - Oluşturuldu mu?"] = "Hayır"
        return None
