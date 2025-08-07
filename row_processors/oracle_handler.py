from utils.logger import log_error_row
from utils.network_utils import resolve_ip, resolve_hostname, is_ip
from config.settings import EXCLUDED_SAFE_MEMBERS

def is_empty(val: str) -> bool:
    val = (val or "").strip().lower()
    return val in ["", "nan", "none", "null"]

def process_oracle_row(index, pam_row, safe_user_list) -> tuple[list[list], list[list]]:
    result_rows = []
    ignored_rows = []

    platform_id = str(pam_row.get("platformId") or "").strip().lower()
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

    # Oracle değilse veya database yoksa → işleme alma
    if not platform_id.startswith("oracle") or is_empty(database):
        return [], []

    if is_empty(port):
        reason = "DB port bilgisi boş"
        log_error_row(index, -31, reason, error_type="Oracle")
        ignored_rows.append([index, username, address or "-", "-", "-", reason, "oracle"])
        return [], ignored_rows

    if is_empty(address):
        reason = "Address alanı boş"
        log_error_row(index, -33, reason, error_type="Oracle")
        ignored_rows.append([index, username, "-", "-", "-", reason, "oracle"])
        return [], ignored_rows

    ip_address = ""
    hostname = address

    if is_ip(address):
        ip_address = address
        hostname = resolve_hostname(ip_address) or ip_address
    else:
        hostname = address
        ip_address = resolve_ip(hostname)

    if is_empty(ip_address):
        reason = "IP adresi tespit edilemedi. OS envanterde ve nslookup sonucunda IP bulunamadı."
        log_error_row(index, -34, f"{reason} (address={address})", error_type="Oracle")
        ignored_rows.append([index, username, address or "-", "-", "-", reason, "oracle"])
        return [], ignored_rows

    if is_empty(hostname):
        hostname = ip_address

    # domain ve OS için OS envanter'de arama yapılabilir
    domain = "nonDomain"
    os_name = "oracle"  # Oracle için dummy; zorunlu değil ama consistency için yazılabilir

    members = ",".join([
        str(m.get("memberName") or "").strip()
        for m in safe_user_list
        if str(m.get("safeName") or "").strip() == safe_name
        and (
            str(m.get("memberName") or "").strip().lower() not in [x.lower() for x in EXCLUDED_SAFE_MEMBERS]
            or str(m.get("memberName") or "").strip().lower() == safe_name.strip().lower()
        )
    ])

    row_data = [
        index,
        username,
        ip_address,
        hostname,
        os_name,
        os_name,
        safe_name,
        members,
        database,
        port,
        "oracle",
        domain
    ]

    result_rows.append(row_data)
    return result_rows, ignored_rows
