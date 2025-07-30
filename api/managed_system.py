import requests
from config.settings import API_BASE_URL, VERIFY_SSL
from core.logger import log_message, log_error
from core.env import get_env_variable
from utils.universal_cache import UniversalCache

# Global cache instance
cache = UniversalCache()

def get_all_managed_systems():
    cache_key = "ManagedSystem"
    cached_data = cache.get_cached_data(cache_key)
    if cached_data:
        log_message(f"📦 Managed System listesi cache'den alındı. ({len(cached_data)} kayıt)")
        return cached_data

    try:
        session_id = get_env_variable("ASP_NET_SESSION_ID")
        if not session_id:
            raise Exception("Session ID ortam değişkeninde bulunamadı.")

        headers = {
            "Content-Type": "application/json",
            "Cookie": f"ASP.NET_SessionId={session_id}"
        }

        url = f"{API_BASE_URL}/ManagedSystems"
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()

        systems = response.json()

        # ✅ Cache ve index işlemleri
        cache.cache_data(cache_key, systems)
        cache.build_index(cache_key, "Name")
        cache.build_index(cache_key, "IPAddress")  # IP ile arama için index

        log_message(f"📥 Managed System listesi API'den alındı ve cache'e yazıldı. ({len(systems)} kayıt)")
        return systems

    except requests.exceptions.RequestException as req_err:
        log_error(-10, f"HTTP Hatası: {str(req_err)}", error_type="ManagedSystemAPI")
    except Exception as e:
        log_error(-11, f"Genel Hata: {str(e)}", error_type="ManagedSystemAPI")

    return []

def get_managed_system_by_name(name: str):
    return cache.get_by_key("ManagedSystem", "Name", name)

def get_managed_system_by_ip(ip_address: str):
    return cache.get_by_key("ManagedSystem", "IPAddress", ip_address)
