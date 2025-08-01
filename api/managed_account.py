# api/managed_account.py

import requests
import os
from config.settings import API_BASE_URL, VERIFY_SSL
from utils.logger import log_error, log_message

def get_managed_accounts_by_system_id(system_id: int):
    """
    Belirtilen ManagedSystem ID'ye ait mevcut managed account'ları getirir.
    """
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (get_managed_accounts_by_system_id).", error_type="ADManagedAccountAPI")
        return []

    url = f"{API_BASE_URL}/ManagedSystems/{system_id}/ManagedAccounts"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        log_error(-1, f"GET ManagedAccounts hata (system_id={system_id}): {str(e)}", error_type="ADManagedAccountAPI")
        return []

def create_ad_managed_account_api_call(system_id: int, payload: dict):
    """
    Yeni bir AD managed account oluşturur.
    """
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (create_ad_managed_account_api_call).", error_type="ADManagedAccountAPI")
        return

    url = f"{API_BASE_URL}/ManagedSystems/{system_id}/ManagedAccounts"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()

        log_message(f"[ManagedAccountAPI] ✅ AD Managed Account oluşturuldu: {payload.get('AccountName')}")

    except requests.exceptions.RequestException as e:
        log_error(-1, f"POST ManagedAccount hata: {str(e)}", error_type="ADManagedAccountAPI")

def link_managed_account_to_system(system_id: int, account_id: int):
    """
    Managed Account → Managed System linkleme çağrısı
    """
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (link_managed_account_to_system).", error_type="ADManagedAccountAPI")
        return

    url = f"{API_BASE_URL}/ManagedSystems/{system_id}/LinkedAccounts/{account_id}"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.post(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        log_message(f"[ManagedAccountAPI] 🔗 Linkleme başarılı → SystemID: {system_id}, AccountID: {account_id}")
    except requests.exceptions.RequestException as e:
        log_error(-1, f"🔗 Linkleme API hatası: {str(e)}", error_type="ADManagedAccountAPI")