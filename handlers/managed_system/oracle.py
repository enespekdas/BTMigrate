from copy import deepcopy
from config.settings import ORACLE_MANAGED_SYSTEM_TEMPLATE, WORKGROUP_ID
from row_processors.utils import resolve_functional_account_id
from utils.logger import log_message_row, log_error_row, log_debug_row
from api.managed_system import create_managed_system, add_managed_system_to_cache

def process_oracle_managed_system(row: dict, cache, row_number: int):
    payload = deepcopy(ORACLE_MANAGED_SYSTEM_TEMPLATE)

    # Functional Account bul (oracle description şart!)
    fa_id = resolve_functional_account_id(cache, row)
    if not fa_id:
        log_error_row(row_number, -200, "Functional Account (oracle) bulunamadı.", "OracleHandler")
        return

    # Excel'den temel bilgiler
    hostname = row.get("hostname", "").strip()
    ip = row.get("ip address", "").strip()
    database = row.get("database", "").strip()

    # Port sayısal dönüşüm (güvenli)
    try:
        port = int(float(row.get("port", 0)))
    except Exception:
        log_error_row(row_number, -202, f"Port değeri geçersiz: {row.get('port')}", "OracleHandler")
        return

    # SystemName formatı
    system_name = f"{hostname} (Db Instance: {database}, Port:{port})"

    # Payload doldurma
    payload["HostName"] = hostname
    payload["DnsName"] = hostname
    payload["IPAddress"] = ip
    payload["InstanceName"] = database
    payload["Port"] = port
    payload["SystemName"] = system_name
    payload["FunctionalAccountID"] = fa_id
    payload["AutoManagementFlag"] = False  # bool olacak

    # Debug log (opsiyonel)
    #log_debug_row(row_number, f"[Payload] {payload}")

    # Oluşturma çağrısı
    success, response = create_managed_system(payload, WORKGROUP_ID)
    if success:
        add_managed_system_to_cache(cache, response)
        log_message_row(row_number, f"✅ Oracle Managed System oluşturuldu: {response.get('Name')}")
    else:
        log_error_row(row_number, -201, f"Oluşturma hatası: {response}", "OracleHandler")
