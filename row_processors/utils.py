from api.functional_account import get_functional_account_id
from utils.logger import log_debug

def resolve_functional_account_id(cache, row: dict):
    domain = row.get("domain")
    os_info = row.get("OS")
    database = row.get("database", "")

    # 💡 Eğer domain boş ama veritabanı varsa, OS tipini belirle
    if not domain and database and isinstance(database, str):
        if "oracle" in database.lower():
            os_info = "oracle"
        elif "mssql" in database.lower():
            os_info = "mssql"

    # 🧼 Normalize string dönüşümleri
    domain_str = str(domain).strip().lower() if isinstance(domain, str) else ""
    os_info_str = str(os_info).strip().lower() if isinstance(os_info, str) else ""

    log_debug(f"[FA Lookup] Aranan → Domain: '{domain_str}', OS: '{os_info_str}'")

    if not os_info_str:
        log_debug("[FA Lookup] OS bilgisi eksik → FA eşleşmesi yapılmadı.")
        return None

    # 🎯 Öncelikli: Domain + OS (description içinde) eşleşmesi
    fa_id = get_functional_account_id(cache, domain_str, os_info_str)

    if fa_id:
        log_debug(f"[FA Lookup] Eşleşen FA bulundu → ID: {fa_id}")
        return fa_id

    # 🔁 Yedek: Sadece OS bilgisiyle (örneğin Oracle domain'siz ise)
    log_debug(f"[FA Lookup] Domain eşleşmedi. Sadece OS ('{os_info_str}') ile fallback denenecek.")
    fa_id_os_only = get_functional_account_id(cache, "", os_info_str)

    if fa_id_os_only:
        log_debug(f"[FA Lookup] (Fallback) OS'e göre FA bulundu → ID: {fa_id_os_only}")
        return fa_id_os_only

    # ❌ Hâlâ yoksa None dön
    log_debug(f"[FA Lookup] (Fallback) Eşleşme bulunamadı. Domain: '{domain_str}', OS: '{os_info_str}'")
    return None
