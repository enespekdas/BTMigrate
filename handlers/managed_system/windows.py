# handlers/managed_system/windows.py

from copy import deepcopy
from config.settings import WINDOWS_MANAGED_SYSTEM_TEMPLATE, WORKGROUP_ID
from row_processors.utils import resolve_functional_account_id
from utils.logger import log_message_row, log_error_row
from api.managed_system import create_managed_system, add_managed_system_to_cache

def process_windows_managed_system(row: dict, cache, row_number: int):
    payload = deepcopy(WINDOWS_MANAGED_SYSTEM_TEMPLATE)

    # ✅ Functional Account ID bul
    fa_id = resolve_functional_account_id(cache, row)
    if fa_id:
        payload["FunctionalAccountID"] = fa_id
    else:
        log_error_row(row_number, -200, "Functional Account ID bulunamadı.", "WindowsHandler")
        return

    # ✅ IP, Hostname vs.
    payload["IPAddress"] = row.get("ip address", "")
    payload["HostName"] = row.get("hostname", "")
    payload["DnsName"] = row.get("hostname", "")  # DNS ve Hostname aynı kullanılacak
    # ✅ İsteğe bağlı alanlar
    payload["ContactEmail"] = ""
    payload["Description"] = f""

    # ✅ Managed System oluştur
    success, response = create_managed_system(payload, WORKGROUP_ID)
    if success:
        add_managed_system_to_cache(cache, response)
        row["MS - Oluşturuldu mu?"] = "Evet"  # 🔍 EXCEL LOG KOLONU
        log_message_row(row_number, f"✅ Managed System oluşturuldu: {response.get('Name')}")
    else:
        log_error_row(row_number, -201, f"Oluşturma hatası: {response}", "WindowsHandler")
