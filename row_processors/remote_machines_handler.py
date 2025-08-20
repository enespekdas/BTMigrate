from typing import List, Tuple
from utils.validators import is_valid_ip
from utils.logger import log_error_row
from utils.network_utils import resolve_hostname, resolve_ip
from config.settings import EXCLUDED_SAFE_MEMBERS, DEFAULT_DOMAIN_IF_MISSING

def is_empty(val: str) -> bool:
    val = (val or "").strip().lower()
    return val in ["", "nan", "none", "null"]


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


def process_remote_machines(index: int, pam_row: dict, os_envanter: List[dict], safe_user_list: List[dict]) -> Tuple[List[List], List[List]]:
    """
    RemoteMachines alanını işler; 'domain' tipli satırlar üretir.
    OS bilgisi zorunludur. Linux için application = winscp atanır.
    """
    result_rows: List[List] = []
    ignored_rows: List[List] = []

    username = str(pam_row.get("UserName") or pam_row.get("userName") or "").strip()
    safe_name = str(pam_row.get("SafeName") or pam_row.get("safeName") or "").strip()
    remote_raw = str(pam_row.get("RemoteMachines") or pam_row.get("remoteMachines") or "").strip()

    # username pam ile başlamıyorsa (eski kuralı koruyoruz)
    if not (username or "").lower().startswith("pam"):
        reason = "pam ile başlamayan domain tipi kullanıcı"
        log_error_row(index, -20, f"{reason} (username={username})", error_type="Validation")
        ignored_rows.append([index, username or "-", remote_raw or "-", "-", "-", reason, "-"])
        return result_rows, ignored_rows

    # safe user members (exclude filtresi)
    excluded = [x.strip().lower() for x in EXCLUDED_SAFE_MEMBERS]
    members = ",".join([
        str(m.get("memberName") or "").strip()
        for m in safe_user_list
        if str(m.get("safeName") or "").strip() == safe_name
        and (str(m.get("memberName") or "").strip().lower() not in excluded
             or str(m.get("memberName") or "").strip().lower() == safe_name.strip().lower())
    ])

    # RemoteMachines; ile parçala
    remotes = [
        r.strip()
        for r in remote_raw.split(";")
        if r.strip().lower() not in ["", "nan", "none", "null"]
    ]

    for remote in remotes:
        ip_address = ""
        hostname = ""
        os_name = ""
        domain = ""
        row_type = "domain"
        application = ""

        # 1) OS envanter eşleşmesi
        matched = next(
            (r for r in os_envanter
             if str(r.get("IP Address") or "").strip() == remote
             or str(r.get("Hostname") or "").strip().lower() == remote.lower()),
            None
        )
        inv_ip = str(matched.get("IP Address") or "").strip() if matched else ""
        inv_host = str(matched.get("Hostname") or "").strip() if matched else ""
        inv_os = str(matched.get("OS") or "").strip() if matched else ""
        inv_domain = str(matched.get("Domain") or "").strip() if matched else ""

        # IP/Hostname toparla
        if is_valid_ip(remote) and is_empty(inv_ip):
            ip_address = remote
        else:
            ip_address = inv_ip

        # Eksik IP için çözüm
        if is_empty(ip_address) and not is_valid_ip(remote):
            ip_address = resolve_ip(remote) or ""

        fqdn_from_dns = ""
        if not is_empty(inv_host):
            fqdn_from_dns = inv_host
        else:
            # dns resolve
            if is_valid_ip(remote):
                fqdn_from_dns = resolve_hostname(remote) or ""
            elif not is_empty(ip_address):
                fqdn_from_dns = resolve_hostname(ip_address) or ""

        # hostname seç
        if not is_empty(inv_host):
            hostname = inv_host
        elif not is_empty(fqdn_from_dns):
            hostname = fqdn_from_dns
        elif not is_empty(ip_address):
            hostname = ip_address
        else:
            hostname = ""

        # domain seç
        domain = _pick_domain_value(inv_domain, fqdn_from_dns)

        # Zorunlu alan kontrolleri
        if is_empty(ip_address) or is_empty(hostname):
            if is_empty(ip_address) and not is_empty(hostname):
                reason = "IP adresi tespit edilemedi (OS envanter + nslookup başarısız)."
            elif is_empty(hostname) and not is_empty(ip_address):
                reason = "Hostname tespit edilemedi (OS envanter + nslookup başarısız)."
            else:
                reason = "IP ve hostname tespit edilemedi (OS envanter + nslookup başarısız)."
            log_error_row(index, -21, f"{reason} (remote={remote})", error_type="Validation")
            ignored_rows.append([index, username, remote, hostname or "-", domain or "-", reason, inv_os or "-"])
            continue

        if not is_valid_ip(ip_address):
            reason = f"Geçersiz IP adresi: {ip_address}"
            log_error_row(index, -23, reason, error_type="Validation")
            ignored_rows.append([index, username, remote, hostname or "-", domain or "-", reason, inv_os or "-"])
            continue

        # OS zorunlu
        os_name = inv_os
        if is_empty(os_name):
            reason = "OS bilgisi bulunamadı."
            log_error_row(index, -22, f"{reason} (ip={ip_address}, hostname={hostname})", error_type="Validation")
            ignored_rows.append([index, username, remote, hostname or "-", domain or "-", reason, "-"])
            continue

        # Linux için uygulama
        if (os_name or "").lower() == "linux":
            application = "winscp"

        # Çıkış satırı
        row_data = [
            index,                 # PamEnvanterSatır
            username,              # username
            ip_address,            # ip address
            hostname,              # hostname
            application,           # application
            os_name,               # OS
            safe_name,             # safe name
            members,               # members
            "",                    # database
            "",                    # port
            row_type,              # type
            domain                 # domain
        ]
        result_rows.append(row_data)

    return result_rows, ignored_rows
