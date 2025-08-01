import socket

def resolve_hostname(ip: str) -> str:
    """
    Verilen IP adresi için hostname çözümlemesi yapar.
    """
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ""

def resolve_ip(hostname: str) -> str:
    """
    Verilen hostname için IP çözümlemesi yapar.
    """
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        return ""
def is_ip(value: str) -> bool:
    try:
        socket.inet_aton(value)
        return True
    except socket.error:
        return False