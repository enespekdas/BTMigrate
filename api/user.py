# api/user.py

import os
import requests
from typing import Optional
from config.settings import API_BASE_URL, VERIFY_SSL, AD_BIND_USER, AD_BIND_PASSWORD
from utils.logger import log_error, log_message
from utils.universal_cache import UniversalCache

USER_KEY = "User"

def get_all_users(cache: UniversalCache):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (users).", error_type="UserAPI")
        return []

    url = f"{API_BASE_URL}/Users"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        users = response.json()

        cache.cache_data(USER_KEY, users)
        log_message(f"📥 User listesi API'den alındı ve cache'e yazıldı. ({len(users)} kayıt)")
        return users

    except Exception as e:
        log_error(-1, f"User listesi alınırken hata oluştu: {str(e)}", error_type="UserAPI")
        return []

def create_user(user_name: str, domain: str, cache: UniversalCache) -> Optional[int]:
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (create user).", error_type="UserAPI")
        return None

    url = f"{API_BASE_URL}/Users/"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    payload = {
        "UserType": "ActiveDirectory",
        "UserName": user_name,
        "ForestName": domain,
        "DomainName": domain,
        "BindUser": AD_BIND_USER,
        "BindPassword": AD_BIND_PASSWORD,
        "UseSSL": "false"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, verify=VERIFY_SSL)
        response.raise_for_status()
        created = response.json()
        user_id = created.get("UserID") or created.get("ID")

        if user_id:
            log_message(f"✅ Kullanıcı oluşturuldu: {user_name} (ID: {user_id})")
            current = cache.get_cached_data(USER_KEY) or []
            current.append({"UserName": user_name, "UserID": user_id})
            cache.cache_data(USER_KEY, current)
            return user_id

        log_error(-1, f"Kullanıcı oluşturuldu ama ID alınamadı. Yanıt: {created}", error_type="UserAPI")
        return None

    except Exception as e:
        log_error(-1, f"Kullanıcı oluşturma hatası: {str(e)}", error_type="UserAPI")
        return None

def add_user_to_group(user_id: int, group_id: int):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (add user to group).", error_type="UserAPI")
        return

    url = f"{API_BASE_URL}/Users/{user_id}/UserGroups/{group_id}"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.post(url, headers=headers, data='', verify=VERIFY_SSL)
        response.raise_for_status()
        log_message(f"✅ Kullanıcı (ID: {user_id}) gruba (ID: {group_id}) başarıyla eklendi.")

    except Exception as e:
        log_error(-1, f"Kullanıcı gruba eklenirken hata oluştu: {str(e)}", error_type="UserAPI")
