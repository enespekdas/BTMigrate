import requests
import os
from typing import Optional
from config.settings import API_BASE_URL, VERIFY_SSL
from utils.logger import log_error, log_message
from utils.universal_cache import UniversalCache

FUNCTIONAL_ACCOUNTS_KEY = "FunctionalAccount"  # ✅ Key normalize edildi

def get_all_functional_accounts():
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

        # ✅ UniversalCache'e yaz
        UniversalCache().cache_data(FUNCTIONAL_ACCOUNTS_KEY, accounts)

        log_message(f"[DEBUG] Functional Account cache'e yazıldı. ({len(accounts)} kayıt)")
        return accounts

    except Exception as e:
        log_error(-1, f"Functional Account listesi alınamadı: {str(e)}", error_type="FunctionalAccountAPI")
        return []

def get_functional_account_id(domain: str, os_name: str) -> Optional[int]:
    domain = (domain or "").lower()
    os_name = (os_name or "").lower()

    accounts = UniversalCache().get_cached_data(FUNCTIONAL_ACCOUNTS_KEY)

    if not accounts:
        log_error(-1, "[DEBUG] Functional account listesi cache'te bulunamadı veya boş.", error_type="FunctionalAccountLookup")
        return None

    for fa in accounts:
        fa_domain = (fa.get("DomainName") or "").lower()
        fa_description = (fa.get("Description") or "").lower()

        log_message(f"[DEBUG] FA kontrol → domain='{fa_domain}', desc='{fa_description}', hedef domain='{domain}', os='{os_name}'")

        if fa_domain == domain and os_name in fa_description:
            log_message(f"[DEBUG] ✅ Eşleşme bulundu → FA_ID={fa.get('FunctionalAccountID')}")
            return fa.get("FunctionalAccountID")

    log_message(f"[DEBUG] ❌ Eşleşme bulunamadı → Domain: '{domain}', OS: '{os_name}'")
    return None
