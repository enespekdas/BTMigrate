# dispatcher/managed_system_dispatcher.py

from typing import Optional
from utils.logger import log_message_row
from api.managed_system import get_managed_system_by_ip
from handlers.managed_system.windows import process_windows_managed_system
from handlers.managed_system.linux import process_linux_managed_system
from handlers.managed_system.oracle import process_oracle_managed_system
from handlers.managed_system.mssql import process_mssql_managed_system
from utils.report import ms_init, ms_success, ms_error  # ✅ merkezi

def dispatch_managed_system(row: dict, cache, row_number: int) -> Optional[int]:
    ms_init(row)  # ✅ varsayılanları tek yerden (Genel Durum = ✅)

    ip = row.get("ip address")
    os_value = (row.get("OS") or "").strip()
    os_info = os_value.lower()

    row["MS - Tür"] = os_value if os_value else "Bilinmiyor"

    if not ip:
        ms_error(row_number, row, -99, "IP adresi eksik", "Dispatcher")
        return None

    # 1) Zaten mevcut mu?
    existing = get_managed_system_by_ip(cache, ip)
    if existing:
        name = existing.get("Name")
        ms_success(row_number, row, already=True, message=f"✅ Zaten mevcut → {name}")
        return existing.get("ManagedSystemID")

    # 2) Yoksa handler'ı çağır
    try:
        created_id: Optional[int] = None
        if os_info == "windows":
            created_id = process_windows_managed_system(row, cache, row_number)
        elif os_info == "linux":
            created_id = process_linux_managed_system(row, cache, row_number)
        elif os_info == "oracle":
            created_id = process_oracle_managed_system(row, cache, row_number)
        elif os_info == "mssql":
            created_id = process_mssql_managed_system(row, cache, row_number)
        else:
            ms_error(row_number, row, -100, f"Tanımsız OS tipi: {os_info}", "Dispatcher")
            return None

        if created_id:
            ms_success(row_number, row, created=True, message="Managed System oluşturuldu.")
            row["MS - ID"] = created_id
            return created_id

        # Handler başarısız ama exception atmadı
        ms_error(row_number, row, -101, "Oluşturma başarısız (ID dönmedi).", "Dispatcher")
        return None

    except Exception as e:
        ms_error(row_number, row, -102, f"Dispatch exception: {str(e)}", "Dispatcher")
        return None
