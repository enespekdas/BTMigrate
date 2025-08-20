from utils.validators import is_valid_ip
from utils.logger import log_error_row
from utils.network_utils import resolve_hostname, resolve_ip, is_ip
from config.settings import EXCLUDED_SAFE_MEMBERS, MSSQL_DOMAIN_SUFFIX, DEFAULT_DOMAIN_IF_MISSING

def is_empty(val: str) -> bool:
    val = (val or "").strip().lower()
    return val in ["", "nan", "none", "null"]

def _normalize_port(raw_port) -> str:
    if raw_port is None:
        return ""
    try:
        return str(int(float(raw_port)))
    except Exception:
        return str(raw_port).strip()

def _pick_domain_value(domain_from_inventory: str, fqdn_from_dns: str) -> str:
    """
    Domain önceliği:
      1) OS Envanter'den gelen domain (varsa)
      2) DNS'ten gelen FQDN içinden çıkarılabilen suffix (ör. host.domain)
      3) Ayarda DEFAULT_DOMAIN_IF_MISSING varsa o
      4) "nonDomain"
    """
    dom = (domain_from_inventory or "").strip()
    if dom:
        return dom

    # fqdn'den domain çıkarma: "host.domain.tld" -> "domain.tld"
    if fqdn_from_dns and "." in fqdn_from_dns:
        parts = fqdn_from_dns.split(".")
        if len(parts) >= 2:
            candidate = ".".join(parts[1:]).strip()
            if candidate:
                return candidate

    if DEFAULT_DOMAIN_IF_MISSING:
        return DEFAULT_DOMAIN_IF_MISSING

    return "nonDomain"

def _is_mssql(domain: str, hostname: str, remote_raw: str) -> bool:
    """
    MSSQL tespiti veri toplandıktan sonra yapılır.
    - domain suffix MSSQL_DOMAIN_SUFFIX ile bitiyorsa True
    - hostname FQDN olarak bu suffix ile bitiyorsa True
    - domain/hostname bulunamadıysa ve remote_raw içinde bu suffix geçiyorsa (yedek sinyal) True
    """
    suffix = (MSSQL_DOMAIN_SUFFIX or "").strip().lower()
    if not suffix:
        return False

    dom = (domain or "").strip().lower()
    host = (hostname or "").strip().lower()
    remote = (remote_raw or "").strip().lower()

    if dom.endswith(suffix):
        return True
    if host.endswith(suffix):
        return True
    if suffix in remote:
        return True

    return False

def process_remote_machine_row(index, pam_row, os_envanter, safe_user_list) -> tuple[list[list], list[list]]:
    result_rows = []
    ignored_rows = []

    username = str(pam_row.get("userName") or "").strip()
    safe_name = str(pam_row.get("safeName") or "").strip()
    database = str(pam_row.get("database") or "").strip()
    port = _normalize_port(pam_row.get("port"))
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
        ip_address = ""
        hostname = ""
        os_name = ""
        domain = ""
        row_type = "domain"
        application = ""

        # ❌ Kullanıcı adı pam ile başlamıyorsa ignore et
        if not username.lower().startswith("pam"):
            reason = "pam ile başlamayan domain tipi kullanıcı"
            log_error_row(index, -20, f"{reason} (username={username})", error_type="Validation")
            ignored_rows.append([index, username, remote, "-", "-", reason, "-"])
            continue

        # -----------------------
        # 1) VERİ TOPLAMA AŞAMASI
        # -----------------------
        matched_row = next(
            (r for r in os_envanter
             if str(r.get("IP Address") or "").strip() == remote
             or str(r.get("Hostname") or "").strip().lower() == remote.lower()),
            None
        )

        ip_address = str(matched_row.get("IP Address") or "").strip() if matched_row else ""
        hostname_from_inv = str(matched_row.get("Hostname") or "").strip() if matched_row else ""
        os_name = str(matched_row.get("OS") or "").strip() if matched_row else ""
        domain_from_inv = str(matched_row.get("Domain") or "").strip() if matched_row else ""

        # 🔧 EKSİK FİX: remote bir IP ise ve envanterden IP bulunamadıysa, ip_address'i remote'tan başlat
        if is_valid_ip(remote) and is_empty(ip_address):
            ip_address = remote

        # Eksikler için DNS çözümleme
        if is_empty(ip_address) and not is_valid_ip(remote):
            ip_address = resolve_ip(remote)

        fqdn_from_dns = ""
        if is_empty(hostname_from_inv):
            if is_valid_ip(remote):
                fqdn_from_dns = resolve_hostname(remote) or ""
            elif not is_empty(ip_address):
                fqdn_from_dns = resolve_hostname(ip_address) or ""
        else:
            fqdn_from_dns = hostname_from_inv  # envanterde FQDN olabilir

        # Hostname belirle (öncelik: inventory hostname -> DNS FQDN -> IP)
        if not is_empty(hostname_from_inv):
            hostname = hostname_from_inv
        elif not is_empty(fqdn_from_dns):
            hostname = fqdn_from_dns
        elif not is_empty(ip_address):
            hostname = ip_address
        else:
            hostname = ""

        # Domain belirle
        domain = _pick_domain_value(domain_from_inv, fqdn_from_dns)

        # -----------------------
        # 2) ZORUNLU ALAN KONTROLLERİ
        # -----------------------
        if is_empty(ip_address) or is_empty(hostname):
            if is_empty(ip_address) and not is_empty(hostname):
                reason = "IP adresi tespit edilemedi. OS envanter ve nslookup başarısız."
            elif is_empty(hostname) and not is_empty(ip_address):
                reason = "Hostname tespit edilemedi. OS envanter ve nslookup başarısız."
            else:
                reason = "IP ve hostname tespit edilemedi. OS envanter ve nslookup başarısız."
            log_error_row(index, -21, f"{reason} (remote={remote})", error_type="Validation")
            ignored_rows.append([index, username, remote, hostname or "-", domain or "-", reason, os_name or "-"])
            continue

        if not is_valid_ip(ip_address):
            reason = f"Geçersiz IP adresi: {ip_address}"
            log_error_row(index, -23, reason, error_type="Validation")
            ignored_rows.append([index, username, remote, hostname or "-", domain or "-", reason, os_name or "-"])
            continue

        # -----------------------
        # 3) TİP (CLASSIFICATION) — OS boşsa bile istisnayı burada uygula
        # -----------------------
        if _is_mssql(domain, hostname, remote):
            row_type = "mssql"
            if is_empty(os_name):
                os_name = "mssql"
        else:
            row_type = "domain"

        # -----------------------
        # 4) OS BOŞ KONTROLÜ (MSSQL/Oracle İSTİSNASI DAHİL)
        # -----------------------
        # Oracle zaten prepare_workbook akışında ayrı handler’dan geçiyor.
        # Burada yalnız MSSQL istisnası var. MSSQL değil ve OS hala boşsa ignore et.
        if is_empty(os_name) and row_type != "mssql":
            reason = "OS bilgisi bulunamadı"
            log_error_row(index, -22, f"{reason} (ip={ip_address}, hostname={hostname})", error_type="Validation")
            ignored_rows.append([index, username, remote, hostname or "-", domain or "-", reason, "-"])
            continue

        # Uygulama ataması (Linux kuralı)
        if (os_name or "").lower() == "linux":
            application = "winscp"

        # -----------------------
        # 5) ÇIKIŞ SATIRI
        # -----------------------
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
