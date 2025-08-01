from api.functional_account import get_functional_account_id
from utils.logger import log_debug

def resolve_functional_account_id(cache, row: dict):
    domain = row.get("domain")
    os_info = row.get("OS")
    database = row.get("database", "")

    # Domain yoksa ve DB sistemiyse OS belirle
    if not domain and database and isinstance(database, str):
        if "oracle" in database.lower():
            os_info = "oracle"
        elif "mssql" in database.lower():
            os_info = "mssql"

    # 🧼 String dönüşümleri
    domain_str = str(domain).strip().lower() if domain and isinstance(domain, str) else ""
    os_info_str = str(os_info).strip().lower() if os_info and isinstance(os_info, str) else ""

    log_debug(f"[FA Lookup] Gelen domain: {domain_str}, OS: {os_info_str}")

    if not os_info_str:
        log_debug("[FA Lookup] OS bilgisi eksik.")
        return None

    fa_id = get_functional_account_id(cache, domain_str, os_info_str)

    if fa_id:
        log_debug(f"[FA Lookup] Eşleşen FA ID: {fa_id}")
    else:
        log_debug(f"[FA Lookup] Eşleşme yok. Aranan Domain: '{domain_str}', OS içinde: '{os_info_str}'")

    return fa_id
