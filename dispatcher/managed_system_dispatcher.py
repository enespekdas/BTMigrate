# dispatcher/managed_system_dispatcher.py

from utils.logger import log_error_row, log_message_row
from api.managed_system import get_managed_system_by_ip
from handlers.managed_system.windows import process_windows_managed_system
from handlers.managed_system.linux import process_linux_managed_system
from handlers.managed_system.oracle import process_oracle_managed_system
from handlers.managed_system.mssql import process_mssql_managed_system

def dispatch_managed_system(row: dict, cache, row_number: int):
    ip = row.get("ip address")
    os_value = row.get("OS", "").strip()
    os_info = os_value.lower()

    # her halükarda tür bilgisini Excel'deki OS'e göre yaz
    row["MS - Tür"] = os_value if os_value else "Bilinmiyor"

    if not ip:
        log_error_row(row_number, -99, "IP adresi eksik", "Dispatcher")
        row["MS - Genel Durum"] = "❌"
        row["MS - Zaten Var mı?"] = "Hayır"
        row["MS - Oluşturuldu mu?"] = "Hayır"
        return

    existing = get_managed_system_by_ip(cache, ip)
    if existing:
        name = existing.get("Name")
        log_message_row(row_number, f"✅ Zaten mevcut → {name}")
        row["MS - Genel Durum"] = "✅"
        row["MS - Zaten Var mı?"] = "Evet"
        row["MS - Oluşturuldu mu?"] = "Hayır"
        return

    row["MS - Zaten Var mı?"] = "Hayır"  # çünkü yukarıda existing None

    try:
        if os_info == "windows":
            process_windows_managed_system(row, cache, row_number)
        elif os_info == "linux":
            process_linux_managed_system(row, cache, row_number)
        elif os_info == "oracle":
            process_oracle_managed_system(row, cache, row_number)
        elif os_info == "mssql":
            process_mssql_managed_system(row, cache, row_number)
        else:
            raise Exception(f"Tanımsız OS tipi: {os_info}")

        # Eğer buraya geldiyse handler hata vermemiştir
        row["MS - Genel Durum"] = "✅"

        if not row.get("MS - Oluşturuldu mu?"):
            row["MS - Oluşturuldu mu?"] = "Hayır"  # handler unutursa fallback

    except Exception as e:
        log_error_row(row_number, -101, f"Managed system dispatch hatası: {str(e)}", "Dispatcher")
        row["MS - Genel Durum"] = "❌"
        row["MS - Oluşturuldu mu?"] = "Hayır"
