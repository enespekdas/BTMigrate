# handlers/managed_system/oracle.py

from copy import deepcopy
from config.settings import ORACLE_MANAGED_SYSTEM_TEMPLATE, WORKGROUP_ID
from row_processors.utils import resolve_functional_account_id
from api.managed_system import create_managed_system, add_managed_system_to_cache
from utils.report import ms_success, ms_error  # ✅

def process_oracle_managed_system(row: dict, cache, row_number: int):
    payload = deepcopy(ORACLE_MANAGED_SYSTEM_TEMPLATE)

    fa_id = resolve_functional_account_id(cache, row)
    if not fa_id:
        ms_error(row_number, row, -200, "Functional Account (oracle) bulunamadı.", "OracleHandler")
        return None

    hostname = (row.get("hostname", "") or "").strip()
    ip = (row.get("ip address", "") or "").strip()
    database = (row.get("database", "") or "").strip()

    try:
        port = int(float(row.get("port", 0)))
    except Exception:
        ms_error(row_number, row, -202, f"Port değeri geçersiz: {row.get('port')}", "OracleHandler")
        return None

    system_name = f"{hostname} (Db Instance: {database}, Port:{port})"

    payload["HostName"] = hostname
    payload["DnsName"] = hostname
    payload["IPAddress"] = ip
    payload["InstanceName"] = database
    payload["Port"] = port
    payload["SystemName"] = system_name
    payload["FunctionalAccountID"] = fa_id
    payload["AutoManagementFlag"] = False

    success, response = create_managed_system(payload, WORKGROUP_ID)
    if success:
        add_managed_system_to_cache(cache, response)
        ms_success(row_number, row, created=True,
                   message=f"Oracle Managed System oluşturuldu: {response.get('Name')}")
        return response.get("ManagedSystemID") or response.get("ID")
    else:
        ms_error(row_number, row, -201, f"Oluşturma hatası: {response}", "OracleHandler")
        return None
