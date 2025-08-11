# api/application.py

import requests
import os
from config.settings import API_BASE_URL, VERIFY_SSL
from utils.logger import log_error, log_message
from utils.universal_cache import UniversalCache

APPLICATIONS_KEY = "Application"

def get_all_applications(cache: UniversalCache):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (applications).", error_type="ApplicationAPI")
        return []

    url = f"{API_BASE_URL}/Applications"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        applications = response.json()
        cache.cache_data(APPLICATIONS_KEY, applications)
        log_message(f"📥 Application listesi API'den alındı ve cache'e yazıldı. ({len(applications)} kayıt)")
        return applications
    except requests.exceptions.RequestException as e:
        log_error(-1, f"Application listesi alınamadı: {str(e)}", error_type="ApplicationAPI")
        return []

def assign_application_to_account(account_id: int, application_id: int):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(account_id, "Session ID bulunamadı (assign app).", error_type="ApplicationAPI")
        return False

    url = f"{API_BASE_URL}/ManagedAccounts/{account_id}/Applications/{application_id}"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.post(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        log_message(f"✅ ApplicationID {application_id} → ManagedAccountID {account_id} ataması başarılı.")
        return True
    except requests.exceptions.RequestException as e:
        log_error(account_id, f"Application ataması başarısız: {str(e)}", error_type="ApplicationAPI")
        return False

def is_application_already_assigned(account_id: int, application_id: int) -> bool:
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(account_id, "Session ID bulunamadı. Application kontrolü yapılamadı.", error_type="ApplicationAPI")
        return False

    url = f"{API_BASE_URL}/ManagedAccounts/{account_id}/Applications"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        existing_apps = response.json()
        return any(app.get("ApplicationID") == application_id for app in existing_apps)
    except Exception as e:
        log_error(account_id, f"Application kontrolü başarısız: {e}", error_type="ApplicationAPI")
        return False

# ✅ yeni: mevcut atamaları tek seferde al
def get_assigned_applications(account_id: int):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(account_id, "Session ID bulunamadı. Mevcut application'lar alınamadı.", error_type="ApplicationAPI")
        return []

    url = f"{API_BASE_URL}/ManagedAccounts/{account_id}/Applications"
    headers = {"Cookie": f"ASP.NET_SessionId={session_id}"}

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        return response.json() or []
    except Exception as e:
        log_error(account_id, f"Mevcut atamalar alınamadı: {e}", error_type="ApplicationAPI")
        return []
