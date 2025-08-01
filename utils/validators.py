import re

def is_valid_ip(ip: str) -> bool:
    """
    IPv4 formatını kontrol eder. Örnek: 192.168.1.1
    """
    if not ip:
        return False
    pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    if not re.match(pattern, ip.strip()):
        return False
    parts = ip.strip().split(".")
    return all(0 <= int(part) <= 255 for part in parts)

def is_valid_hostname(name: str) -> bool:
    """
    Hostname belirli karakter setine uygun mu kontrolü.
    """
    if not name or len(name) > 255:
        return False
    if name.endswith("."):
        name = name[:-1]
    allowed = re.compile(r"(?!-)[A-Z\d\-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in name.split("."))

def is_valid_port(port: str) -> bool:
    """
    Port int mi ve 1-65535 arasında mı kontrolü
    """
    try:
        p = int(port)
        return 1 <= p <= 65535
    except:
        return False
