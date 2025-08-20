from typing import List, Tuple, Optional
from utils.validators import is_valid_ip
from utils.logger import log_error_row
from utils.network_utils import resolve_hostname, resolve_ip
from config.settings import EXCLUDED_SAFE_MEMBERS, DEFAULT_DOMAIN_IF_MISSING

def is_empty(val: str) -> bool:
    val = (val or "").strip().lower()
    return val in ["", "nan", "none", "null"]

def _parse_mssql_item(item: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    MsSQL item formatları:
      host
      host:port
      host\\instance
      host\\instance:port
    Döner: (host, instance, port)
    """
    raw = item.strip()
    if not raw:
        return "", None, None
    if "\\" in raw:
        host_part, rest = raw.split("\\", 1)
        inst = rest
        port = None
        if ":" in rest:
            inst, port = rest.split(":", 1)
        return host_part.strip(), (inst or "").strip() or None, (port or "").strip() or None
    host = raw
    port = None
    if ":" in raw:
        host, port = raw.split(":", 1)
    return host.strip(), None, (port or "").strip() or None

def _pick_domain_from_host(hostname_or_fqdn: str) -> str:
    if hostname_or_fqdn and "." in hostname_or_fqdn:
        parts = hostname_or_fqdn.split(".")
        if len(parts) >= 2:
            domain = ".".join(parts[1:]).strip()
            if domain:
                return domain
    return ""

def _pick_domain(domain_from_host: str, os_envanter_domain: str) -> str:
    if domain_from_host:
        return domain_from_host
    if os_envanter_domain:
        return os_envanter_domain
    if DEFAULT_DOMAIN_IF_MISSING:
        return DEFAULT_DOMAIN_IF_MISSING
    return "nonDomain"

def process_mssql_machines(
    index: int,
    pam_row: dict,
    os_envanter: List[dict],
    safe_user_list: List[dict],
    mssql_envanter: List[dict],
) -> Tuple[List[List], List[List]]:
    """
    MsSQL kolonunu işler; her item için 'mssql' tipli satır üretir.
    Arama sırası:
      1) MsSQL envanter (host/IP & instance bağımsız lineer)
      2) OsEnvanter
      3) DNS (resolve_ip / resolve_hostname)
    Kurallar:
      - IP bulunamazsa: ignore
      - Hostname bulunamazsa: hostname = IP
      - port yoksa: 1433
      - OS = 'mssql', type = 'mssql', application = ''
    """
    result_rows: List[List] = []
    ignored_rows: List[List] = []

    username = str(pam_row.get("UserName") or pam_row.get("userName") or "").strip()
    safe_name = str(pam_row.get("SafeName") or pam_row.get("safeName") or "").strip()
    mssql_raw = str(pam_row.get("MsSQL") or "").strip()

    # Şimdilik aynı kural: pam ile başlamayan kullanıcı MSSQL akışında ignore
    if not (username or "").lower().startswith("pam"):
        reason = "pam ile başlamayan domain tipi kullanıcı (MsSQL akışı)."
        log_error_row(index, -20, f"{reason} (username={username})", error_type="Validation")
        ignored_rows.append([index, username or "-", mssql_raw or "-", "-", "-", reason, "mssql"])
        return result_rows, ignored_rows

    excluded = [x.strip().lower() for x in EXCLUDED_SAFE_MEMBERS]
    members = ",".join([
        str(m.get("memberName") or "").strip()
        for m in safe_user_list
        if str(m.get("safeName") or "").strip() == safe_name
        and (str(m.get("memberName") or "").strip().lower() not in excluded
             or str(m.get("memberName") or "").strip().lower() == safe_name.strip().lower())
    ])

    items = [
        x.strip()
        for x in mssql_raw.split(";")
        if x.strip().lower() not in ["", "nan", "none", "null"]
    ]

    for raw_item in items:
        host, instance, port = _parse_mssql_item(raw_item)
        if is_empty(host):
            reason = f"Geçersiz host (MsSQL item: {raw_item})"
            log_error_row(index, -33, reason, error_type="MsSQLValidation")
            ignored_rows.append([index, username, raw_item, "-", "-", reason, "mssql"])
            continue

        # Port normalize
        if is_empty(port):
            port = "1433"
        else:
            try:
                int(port)
            except Exception:
                reason = f"Geçersiz port formatı (MsSQL item: {raw_item})"
                log_error_row(index, -32, reason, error_type="MsSQLValidation")
                ignored_rows.append([index, username, raw_item, "-", "-", reason, "mssql"])
                continue

        # ---- IP & Hostname bulma (MsSQL -> OsEnvanter -> DNS) ----
        ip_address = ""
        hostname = ""
        inv = None  # MsSQL envanter eşleşmesi
        os_match = None  # OsEnvanter eşleşmesi

        if is_valid_ip(host):
            ip_address = host

            # 1) MsSQL envanter: IP -> Hostname
            inv = next((r for r in mssql_envanter
                        if str(r.get("IP") or r.get("IP Address") or "").strip() == ip_address), None)
            hostname = (str(inv.get("Hostname") or inv.get("Host") or inv.get("DNS") or "") if inv else "").strip()

            # 2) OsEnvanter: IP -> Hostname (DNS'ten önce)
            if not hostname:
                os_match = next((r for r in os_envanter
                                 if str(r.get("IP Address") or "").strip() == ip_address), None)
                hostname = (str(os_match.get("Hostname") or "") if os_match else "").strip()

            # 3) DNS: IP -> Hostname
            if not hostname:
                hostname = resolve_hostname(ip_address) or ""

            # Hostname hala yoksa IP’yi hostname olarak kullan
            if is_empty(hostname):
                hostname = ip_address

        else:
            hostname = host

            # 1) MsSQL envanter: Hostname -> IP
            inv = next((r for r in mssql_envanter
                        if str(r.get("Hostname") or r.get("Host") or r.get("DNS") or "").strip().lower() == hostname.lower()), None)
            ip_address = (str(inv.get("IP") or inv.get("IP Address") or "").strip() if inv else "")

            # 2) OsEnvanter: Hostname -> IP (DNS'ten önce)
            if is_empty(ip_address):
                os_match = next((r for r in os_envanter
                                 if str(r.get("Hostname") or "").strip().lower() == hostname.lower()), None)
                ip_address = (str(os_match.get("IP Address") or "").strip() if os_match else "")

            # 3) DNS: Hostname -> IP
            if is_empty(ip_address):
                ip_address = resolve_ip(hostname) or ""

            # IP hala yoksa ignore
            if is_empty(ip_address):
                reason = f"IP ve/veya hostname tespit edilemedi (MsSQL item: {raw_item})."
                log_error_row(index, -31, reason, error_type="MsSQLValidation")
                ignored_rows.append([index, username, raw_item, hostname or "-", "-", reason, "mssql"])
                continue

        # IP format kontrolü
        if not is_valid_ip(ip_address):
            reason = f"Geçersiz IP adresi (MsSQL item: {raw_item}) -> {ip_address}"
            log_error_row(index, -33, reason, error_type="MsSQLValidation")
            ignored_rows.append([index, username, raw_item, hostname or "-", "-", reason, "mssql"])
            continue

        # ---- Domain belirleme (FQDN -> MsSQL env -> OsEnvanter -> DEFAULT/nonDomain) ----
        domain_from_host = _pick_domain_from_host(hostname)

        domain_from_mssql = ""
        if inv:
            domain_from_mssql = str(inv.get("Domain") or inv.get("Forest") or inv.get("Realm") or "").strip()

        if not os_match:
            os_match = next(
                (r for r in os_envanter
                 if str(r.get("IP Address") or "").strip() == ip_address
                 or str(r.get("Hostname") or "").strip().lower() == hostname.lower()),
                None
            )
        inv_domain = str(os_match.get("Domain") or "").strip() if os_match else ""

        domain = _pick_domain(domain_from_host or domain_from_mssql, inv_domain)

        # ---- Çıkış satırı ----
        row_data = [
            index,            # PamEnvanterSatır
            username,         # username
            ip_address,       # ip address
            hostname,         # hostname
            "",               # application
            "mssql",          # OS
            safe_name,        # safe name
            members,          # members
            (instance or ""), # database (instance)
            str(port),        # port
            "mssql",          # type
            domain            # domain
        ]
        result_rows.append(row_data)

    return result_rows, ignored_rows
