import requests
import os
from typing import Optional
from config.settings import API_BASE_URL, VERIFY_SSL
from utils.logger import log_error, log_message, log_debug
from utils.universal_cache import UniversalCache

FUNCTIONAL_ACCOUNTS_KEY = "FunctionalAccount"  # ✅ Key normalize edildi

def get_all_functional_accounts(cache: UniversalCache):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (functional accounts).", error_type="FunctionalAccountAPI")
        return []

    url = f"{API_BASE_URL}/FunctionalAccounts"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()

        accounts = response.json()
        cache.cache_data(FUNCTIONAL_ACCOUNTS_KEY, accounts)

        log_message(f"📥 FunctionalAccount listesi API'den alındı ve cache'e yazıldı. ({len(accounts)} kayıt)")
        return accounts

    except requests.exceptions.RequestException as req_err:
        log_error(-2, f"HTTP Hatası (FA): {str(req_err)}", error_type="FunctionalAccountAPI")
    except Exception as e:
        log_error(-3, f"Genel Hata (FA): {str(e)}", error_type="FunctionalAccountAPI")

    return []

def get_functional_account_id(cache: UniversalCache, domain: str, os_info: str) -> Optional[int]:
    accounts = cache.get_cached_data(FUNCTIONAL_ACCOUNTS_KEY)

    domain = (domain or "").lower()
    os_info = (os_info or "").lower()

    log_debug(f"[FA Lookup] Gelen domain: {domain}, OS: {os_info}")

    for acc in accounts:
        acc_domain = (acc.get("DomainName") or "").lower()
        acc_desc = (acc.get("Description") or "").lower()

        if domain == acc_domain and os_info in acc_desc:
            log_debug(f"[FA Lookup] Eşleşen FA: {acc}")
            return acc.get("FunctionalAccountID")

    log_debug(f"[FA Lookup] Eşleşme yok. Aranan Domain: '{domain}', OS içinde: '{os_info}'")
    return None
