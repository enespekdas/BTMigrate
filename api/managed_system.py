import requests
from config.settings import API_BASE_URL, VERIFY_SSL, WORKGROUP_ID
from utils.logger import log_message, log_error
from core.env import get_env_variable
from utils.universal_cache import UniversalCache


def get_all_managed_systems(cache: UniversalCache):
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

        cache.cache_data(cache_key, systems)
        cache.build_index(cache_key, "Name")
        cache.build_index(cache_key, "IPAddress")

        log_message(f"📥 Managed System listesi API'den alındı ve cache'e yazıldı. ({len(systems)} kayıt)")
        return systems

    except requests.exceptions.RequestException as req_err:
        log_error(-10, f"HTTP Hatası: {str(req_err)}", error_type="ManagedSystemAPI")
    except Exception as e:
        log_error(-11, f"Genel Hata: {str(e)}", error_type="ManagedSystemAPI")

    return []


def get_managed_system_by_name(cache: UniversalCache, name: str):
    return cache.get_by_key("ManagedSystem", "Name", name)


def get_managed_system_by_ip(cache: UniversalCache, ip_address: str):
    return cache.get_by_key("ManagedSystem", "IPAddress", ip_address)


def add_managed_system_to_cache(cache: UniversalCache, system_obj: dict):
    existing_data = cache.get_cached_data("ManagedSystem")
    existing_data.append(system_obj)
    cache.cache_data("ManagedSystem", existing_data)  # Güncel listeyi yeniden set et
    cache.build_index("ManagedSystem", "Name")
    cache.build_index("ManagedSystem", "IPAddress")

def create_managed_system(payload: dict, workgroup_id: int):
    try:
        session_id = get_env_variable("ASP_NET_SESSION_ID")
        if not session_id:
            raise Exception("Session ID ortam değişkeninde bulunamadı.")

        headers = {
            "Content-Type": "application/json",
            "Cookie": f"ASP.NET_SessionId={session_id}"
        }

        url = f"{API_BASE_URL}/Workgroups/{workgroup_id}/ManagedSystems"
        response = requests.post(url, json=payload, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()

        return True, response.json()

    except requests.exceptions.RequestException as req_err:
        return False, str(req_err)
    except Exception as e:
        return False, str(e)
