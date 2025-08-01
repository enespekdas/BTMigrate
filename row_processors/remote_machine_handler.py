from utils.validators import is_valid_ip
from utils.logger import log_error_row
from utils.network_utils import resolve_hostname, resolve_ip, is_ip
from config.settings import EXCLUDED_SAFE_MEMBERS  # ✅ exclude listesi

def is_empty(val: str) -> bool:
    val = (val or "").strip().lower()
    return val in ["", "nan", "none", "null"]

def process_remote_machine_row(index, pam_row, os_envanter, safe_user_list) -> tuple[list[list], list[list]]:
    result_rows = []
    ignored_rows = []

    username = str(pam_row.get("userName") or "").strip()
    safe_name = str(pam_row.get("safeName") or "").strip()
    database = str(pam_row.get("database") or "").strip()
    raw_port = pam_row.get("port")
    port = ""
    if raw_port is not None:
        try:
            port = str(int(float(raw_port)))
        except Exception:
            port = str(raw_port).strip()
    remote_raw = str(pam_row.get("remoteMachines") or "").strip()

    remote_list = [
        r.strip()
        for r in remote_raw.split(";")
        if r.strip().lower() not in ["", "nan", "none", "null"]
    ]

    members = ",".join([
        str(m.get("memberName") or "").strip()
        for m in safe_user_list
        if str(m.get("safeName") or "").strip() == safe_name
        and (
            str(m.get("memberName") or "").strip().lower() not in [x.lower() for x in EXCLUDED_SAFE_MEMBERS]
            or str(m.get("memberName") or "").strip().lower() == safe_name.strip().lower()
        )
    ])

    for remote in remote_list:
        if "thynet.thy.com" in remote.lower():
            ip_address = ""
            hostname = remote

            if is_ip(remote):
                ip_address = remote
                hostname = resolve_hostname(remote) or remote
            else:
                hostname = remote
                ip_address = resolve_ip(remote)

            if is_empty(ip_address) or is_empty(hostname):
                reason = "IP/Hostname eşleşmesi yapılamadı"
                log_error_row(index, -24, f"{reason} (remote={remote})", error_type="MSSQL")
                ignored_rows.append([index, username, remote, reason, "mssql"])
                continue

            final_port = port if not is_empty(port) else "1433"

            row_data = [
                index,
                username,
                ip_address,
                hostname,
                "mssql",
                "mssql",
                safe_name,
                members,
                database,
                final_port,
                "mssql",
                "quasys.local"
            ]
            result_rows.append(row_data)
            continue

        matched_row = next(
            (r for r in os_envanter
             if str(r.get("IP Address") or "").strip() == remote
             or str(r.get("Hostname") or "").strip().lower() == remote.lower()),
            None
        )

        ip_address = str(matched_row.get("IP Address") or "").strip() if matched_row else ""
        hostname = str(matched_row.get("Hostname") or "").strip() if matched_row else ""
        os_name = str(matched_row.get("OS") or "").strip() if matched_row else ""
        domain = str(matched_row.get("Domain") or "").strip() if matched_row else ""

        if is_empty(ip_address) and not is_valid_ip(remote):
            ip_address = resolve_ip(remote)

        if is_empty(hostname) and is_valid_ip(remote):
            hostname = resolve_hostname(remote)

        if is_empty(ip_address) or is_empty(hostname):
            reason = "IP/Hostname eşleşmesi yapılamadı"
            log_error_row(index, -21, f"{reason} (remote={remote})", error_type="Validation")
            ignored_rows.append([index, username, remote, reason, os_name or "-"])
            continue

        if is_empty(os_name):
            reason = "OS bilgisi bulunamadı"
            log_error_row(index, -22, f"{reason} (ip={ip_address}, hostname={hostname})", error_type="Validation")
            ignored_rows.append([index, username, remote, reason, os_name or "-"])
            continue

        if not is_valid_ip(ip_address):
            reason = f"Geçersiz IP adresi: {ip_address}"
            log_error_row(index, -23, reason, error_type="Validation")
            ignored_rows.append([index, username, remote, reason, os_name or "-"])
            continue

        row_type = "domain" if username.lower().startswith("pam") else ""
        application = "winscp" if os_name.lower() == "linux" else ""

        row_data = [
            index,
            username,
            ip_address,
            hostname,
            application,
            os_name,
            safe_name,
            members,
            database,
            port,
            row_type,
            domain
        ]
        result_rows.append(row_data)

    return result_rows, ignored_rows
