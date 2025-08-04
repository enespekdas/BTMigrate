# handlers/managed_system/linux.py

from copy import deepcopy
from config.settings import LINUX_MANAGED_SYSTEM_TEMPLATE, WORKGROUP_ID
from row_processors.utils import resolve_functional_account_id
from utils.logger import log_message_row, log_error_row
from api.managed_system import create_managed_system, add_managed_system_to_cache

def process_linux_managed_system(row: dict, cache, row_number: int):
    payload = deepcopy(LINUX_MANAGED_SYSTEM_TEMPLATE)

    fa_id = resolve_functional_account_id(cache, row)
    if fa_id:
        payload["FunctionalAccountID"] = fa_id
        payload["LoginAccountID"] = fa_id
        payload["AutoManagementFlag"] = True  # string değil
    else:
        log_error_row(row_number, -200, "Functional Account ID bulunamadı.", "LinuxHandler")
        return

    hostname = row.get("hostname", "")
    ip = row.get("ip address", "")

    payload["HostName"] = hostname
    payload["DnsName"] = hostname  # IP koyma
    payload["IPAddress"] = ip
    payload["SystemName"] = hostname
    payload["ElevationCommand"] = None

    success, response = create_managed_system(payload, WORKGROUP_ID)
    if success:
        add_managed_system_to_cache(cache, response)
        row["MS - Oluşturuldu mu?"] = "Evet"  # 🔍 Output Excel için
        log_message_row(row_number, f"✅ Linux Managed System oluşturuldu: {response.get('Name')}")
    else:
        log_error_row(row_number, -201, f"Oluşturma hatası: {response}", "LinuxHandler")
