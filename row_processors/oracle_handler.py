from utils.logger import log_error_row
from utils.network_utils import resolve_ip, resolve_hostname, is_ip

def process_oracle_row(index, pam_row, safe_user_list) -> tuple[list[list], list[list]]:
    result_rows = []
    ignored_rows = []

    platform_id = str(pam_row.get("platformId") or "").strip()
    database = str(pam_row.get("database") or "").strip()
    raw_port = pam_row.get("port")
    port = ""
    if raw_port is not None:
        try:
            port = str(int(float(raw_port)))
        except Exception:
            port = str(raw_port).strip()
    address = str(pam_row.get("address") or "").strip()
    username = str(pam_row.get("userName") or "").strip()
    safe_name = str(pam_row.get("safeName") or "").strip()

    # Oracle ile başlamıyorsa işlem yapılmaz
    if not platform_id.lower().startswith("oracle"):
        return [], []

    # Port boşsa → ignore
    if not port or port.lower() in ["nan", "none", "null", ""]:
        reason = "DB port bilgisi boş"
        log_error_row(index, -31, reason, error_type="Oracle")
        ignored_rows.append([index, username, address or "-", reason, "oracle"])
        return [], ignored_rows

    # Database boşsa → ignore
    if not database or database.lower() in ["nan", "none", "null", ""]:
        reason = "Platform tipi Oracle olarak tespit edildi fakat database alanı boş"
        log_error_row(index, -32, reason, error_type="Oracle")
        ignored_rows.append([index, username, address or "-", reason, "oracle"])
        return [], ignored_rows

    # Address boşsa → ignore
    if not address or address.lower() in ["nan", "none", "null", ""]:
        reason = "Address alanı boş"
        log_error_row(index, -33, reason, error_type="Oracle")
        ignored_rows.append([index, username, "-", reason, "oracle"])
        return [], ignored_rows

    # 🔍 Hostname ve IP çözümleme
    ip_address = ""
    hostname = address

    if is_ip(address):
        ip_address = address
        hostname = resolve_hostname(ip_address) or address
    else:
        hostname = address
        ip_address = resolve_ip(hostname)

    # ❗ IP veya hostname çözümlenememişse → ignore
    if not ip_address or not hostname:
        reason = "IP/Hostname eşleşmesi yapılamadı"
        log_error_row(index, -34, f"{reason} (address={address})", error_type="Oracle")
        ignored_rows.append([index, username, address or "-", reason, "oracle"])
        return [], ignored_rows

    members = ",".join([
        str(m.get("memberName") or "").strip()
        for m in safe_user_list
        if str(m.get("safeName") or "").strip() == safe_name
    ])

    row_data = [
        index,
        username,
        ip_address,
        hostname,
        "oracle",
        "oracle",
        safe_name,
        members,
        database,
        port,
        "oracle",
        ""
    ]

    result_rows.append(row_data)
    return result_rows, []
