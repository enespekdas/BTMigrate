# handlers/managed_system/mssql.py

from copy import deepcopy
from config.settings import MSSQL_MANAGED_SYSTEM_TEMPLATE, WORKGROUP_ID
from row_processors.utils import resolve_functional_account_id
from api.managed_system import create_managed_system, add_managed_system_to_cache
from utils.report import ms_success, ms_error  # ✅

def process_mssql_managed_system(row: dict, cache, row_number: int):
    payload = deepcopy(MSSQL_MANAGED_SYSTEM_TEMPLATE)

    # Functional Account ID kontrolü
    fa_id = resolve_functional_account_id(cache, row)
    if not fa_id:
        ms_error(row_number, row, -200, "Functional Account (mssql) bulunamadı.", "MssqlHandler")
        return None

    # Hostname & IP kontrolü
    hostname = (row.get("hostname", "") or "").strip()
    ip = (row.get("ip address", "") or "").strip()
    if not hostname or not ip:
        ms_error(row_number, row, -201, "Hostname veya IP eksik", "MssqlHandler")
        return None

    # Port kontrolü → default 1433
    port_raw = row.get("port", "")
    port = 1433  # ✅ Default değer
    if port_raw not in ("", None):
        try:
            # Excel float gibi gelen değerleri normalize et (örn: 1453.0 → 1453)
            port = int(float(str(port_raw).strip()))
        except Exception:
            ms_error(row_number, row, -202, f"Port değeri geçersiz, default 1433 kullanılacak: {port_raw}", "MssqlHandler")
            port = 1433

    # SystemName formatı
    system_name = f"{hostname} (Db Instance: {hostname}, Port:{port})"

    # Payload doldurma
    payload["HostName"] = hostname
    payload["DnsName"] = hostname
    payload["IPAddress"] = ip
    payload["InstanceName"] = hostname
    payload["Port"] = port
    payload["SystemName"] = system_name
    payload["FunctionalAccountID"] = fa_id
    payload["AutoManagementFlag"] = False

    # API çağrısı
    success, response = create_managed_system(payload, WORKGROUP_ID)
    if success:
        add_managed_system_to_cache(cache, response)
        ms_success(row_number, row, created=True,
                   message=f"MSSQL Managed System oluşturuldu: {response.get('Name')}")
        return response.get("ManagedSystemID") or response.get("ID")
    else:
        ms_error(row_number, row, -203, f"Oluşturma hatası: {response}", "MssqlHandler")
        return None
