# handlers/managed_system/mssql.py

from copy import deepcopy
from config.settings import MSSQL_MANAGED_SYSTEM_TEMPLATE, WORKGROUP_ID
from row_processors.utils import resolve_functional_account_id
from utils.logger import log_message_row, log_error_row
from api.managed_system import create_managed_system, add_managed_system_to_cache


def process_mssql_managed_system(row: dict, cache, row_number: int):
    payload = deepcopy(MSSQL_MANAGED_SYSTEM_TEMPLATE)

    # Functional Account ID eşleştir
    fa_id = resolve_functional_account_id(cache, row)
    if not fa_id:
        log_error_row(row_number, -200, "Functional Account (mssql) bulunamadı.", "MssqlHandler")
        return

    # Zorunlu alanlar
    hostname = row.get("hostname", "").strip()
    ip = row.get("ip address", "").strip()

    if not hostname or not ip:
        log_error_row(row_number, -201, "Hostname veya IP eksik", "MssqlHandler")
        return

    # Port güvenli dönüşüm
    port_raw = row.get("port", "")
    try:
        port = int(float(port_raw)) if port_raw else 1433
    except Exception:
        log_error_row(row_number, -202, f"Port değeri geçersiz: {port_raw}", "MssqlHandler")
        return

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

    # Create çağrısı
    success, response = create_managed_system(payload, WORKGROUP_ID)
    if success:
        add_managed_system_to_cache(cache, response)
        log_message_row(row_number, f"✅ MSSQL Managed System oluşturuldu: {response.get('Name')}")
    else:
        log_error_row(row_number, -203, f"Oluşturma hatası: {response}", "MssqlHandler")
