# handlers/managed_system/windows.py

from copy import deepcopy
from config.settings import WINDOWS_MANAGED_SYSTEM_TEMPLATE, WORKGROUP_ID
from row_processors.utils import resolve_functional_account_id
from api.managed_system import create_managed_system, add_managed_system_to_cache
from utils.report import ms_success, ms_error  # ✅

def process_windows_managed_system(row: dict, cache, row_number: int):
    payload = deepcopy(WINDOWS_MANAGED_SYSTEM_TEMPLATE)

    fa_id = resolve_functional_account_id(cache, row)
    if not fa_id:
        ms_error(row_number, row, -200, "Functional Account ID bulunamadı.", "WindowsHandler")
        return None
    payload["FunctionalAccountID"] = fa_id

    payload["IPAddress"] = row.get("ip address", "")
    payload["HostName"] = row.get("hostname", "")
    payload["DnsName"] = row.get("hostname", "")
    payload["ContactEmail"] = ""
    payload["Description"] = ""

    success, response = create_managed_system(payload, WORKGROUP_ID)
    if success:
        add_managed_system_to_cache(cache, response)
        ms_success(row_number, row, created=True,
                   message=f"Managed System oluşturuldu: {response.get('Name')}")
        return response.get("ManagedSystemID") or response.get("ID")
    else:
        ms_error(row_number, row, -201, f"Oluşturma hatası: {response}", "WindowsHandler")
        return None
