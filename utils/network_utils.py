# utils/network_utils.py

import socket
from functools import lru_cache
from ipaddress import ip_address

def _normalize_hostname(name: str) -> str:
    """
    Hostname normalizasyonu:
    - strip boşluk
    - lower
    - sonda varsa '.' kaldır (FQDN normalizasyonu)
    """
    if not isinstance(name, str):
        name = str(name or "")
    name = name.strip().lower()
    if name.endswith("."):
        name = name[:-1]
    return name

@lru_cache(maxsize=1024)
def resolve_hostname(ip: str) -> str:
    """
    Verilen IP adresi için hostname (FQDN) çözümlemesi yapar.
    Cache'lidir.
    Başarısız olursa "" döner.
    """
    try:
        ip = (ip or "").strip()
        if not ip:
            return ""
        return socket.gethostbyaddr(ip)[0] or ""
    except Exception:
        return ""

@lru_cache(maxsize=1024)
def resolve_ip(hostname: str) -> str:
    """
    Verilen hostname için IP çözümlemesi yapar.
    Cache'lidir.
    Başarısız olursa "" döner.
    """
    try:
        hostname = _normalize_hostname(hostname)
        if not hostname:
            return ""
        return socket.gethostbyname(hostname) or ""
    except Exception:
        return ""

def is_ip(value: str) -> bool:
    """
    IPv4/IPv6 adres doğrulaması.
    """
    try:
        ip_address((value or "").strip())
        return True
    except Exception:
        return False
