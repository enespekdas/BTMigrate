# dispatcher/managed_system_dispatcher.py

from utils.logger import log_error_row, log_message_row
from api.managed_system import get_managed_system_by_ip
from handlers.managed_system.windows import process_windows_managed_system
from handlers.managed_system.linux import process_linux_managed_system
from handlers.managed_system.oracle import process_oracle_managed_system  # ✅ Oracle importu eklendi
from handlers.managed_system.mssql import process_mssql_managed_system

def dispatch_managed_system(row: dict, cache, row_number: int):
    ip = row.get("ip address")
    if not ip:
        log_error_row(row_number, -99, "IP adresi eksik", "Dispatcher")
        return

    existing = get_managed_system_by_ip(cache, ip)
    if existing:
        log_message_row(row_number, f"✅ Zaten mevcut → {existing.get('Name')}")
        return

    os_info = row.get("OS", "").lower()

    if os_info == "windows":
        return process_windows_managed_system(row, cache, row_number)

    elif os_info == "linux":
        return process_linux_managed_system(row, cache, row_number)

    elif os_info == "oracle":
        return process_oracle_managed_system(row, cache, row_number)

    elif os_info == "mssql":
        return process_mssql_managed_system(row, cache, row_number)

    else:
        log_error_row(row_number, -100, f"Tanımsız OS tipi: {os_info}", error_type="Dispatcher")
