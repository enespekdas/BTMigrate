import requests
from config.settings import API_BASE_URL, VERIFY_SSL, WORKGROUP_ID
from utils.logger import log_message, log_error
from core.env import get_env_variable
from utils.universal_cache import UniversalCache
import json

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

def get_managed_system_by_name(name: str):
    return cache.get_by_key("ManagedSystem", "Name", name)

def get_managed_system_by_ip(ip_address: str):
    return cache.get_by_key("ManagedSystem", "IPAddress", ip_address)

def add_managed_system_to_cache(system_obj: dict):
    existing_data = cache.get_cached_data("ManagedSystem")
    existing_data.append(system_obj)
    cache.build_index("ManagedSystem", "Name")
    cache.build_index("ManagedSystem", "IPAddress")

def create_managed_system(row_number: int, payload: dict):
    try:
        session_id = get_env_variable("ASP_NET_SESSION_ID")
        if not session_id:
            raise Exception("Session ID ortam değişkeninde bulunamadı.")

        headers = {
            "Content-Type": "application/json",
            "Cookie": f"ASP.NET_SessionId={session_id}"
        }

        url = f"{API_BASE_URL}/Workgroups/{WORKGROUP_ID}/ManagedSystems"

        # 🔍 Debug log: payload
        #log_message(f"🔎 Row {row_number}: Gönderilen payload:\n{json.dumps(payload, indent=2)}")

        response = requests.post(url, headers=headers, json=payload, verify=VERIFY_SSL)
        response.raise_for_status()

        created_system = response.json()
        add_managed_system_to_cache(created_system)

        log_message(f"✅ Row {row_number}: Managed System başarıyla oluşturuldu → {created_system.get('IPAddress')}")
        return True, "Oluşturuldu"
    except Exception as e:
        log_error(row_number, f"Managed System oluşturulamadı: {str(e)}", error_type="ManagedSystemAPI")
        return False, f"Hata: {str(e)}"