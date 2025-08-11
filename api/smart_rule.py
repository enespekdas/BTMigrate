# ✅ api/smart_rule.py

import requests
import os
from typing import List, Optional
from config.settings import API_BASE_URL, VERIFY_SSL
from utils.logger import log_error, log_message

SMART_RULES_KEY = "SmartRule"

def get_all_smart_rules():
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (SmartRule).", error_type="SmartRuleAPI")
        return []

    url = f"{API_BASE_URL}/SmartRules"
    headers = {"Cookie": f"ASP.NET_SessionId={session_id}"}

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        try:
            return response.json() or []
        except Exception:
            return []
    except requests.exceptions.RequestException as e:
        log_error(-1, f"GET SmartRules hata: {str(e)}", error_type="SmartRuleAPI")
        return []

def create_smart_rule(payload: dict) -> Optional[dict]:
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (create_smart_rule).", error_type="SmartRuleAPI")
        return None

    url = f"{API_BASE_URL}/QuickRules"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        log_message(f"[SmartRuleAPI] ✅ SmartRule oluşturuldu: {payload.get('Title')}")
        try:
            return response.json()
        except Exception:
            return None
    except requests.exceptions.RequestException as e:
        log_error(-1, f"POST SmartRule hata: {str(e)}", error_type="SmartRuleAPI")
        return None

def get_smart_rule_accounts(smart_rule_id: int) -> List[int]:
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (get_smart_rule_accounts).", error_type="SmartRuleAPI")
        return []

    url = f"{API_BASE_URL}/QuickRules/{smart_rule_id}/ManagedAccounts"
    headers = {"Cookie": f"ASP.NET_SessionId={session_id}"}

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        try:
            accounts = response.json() or []
        except Exception:
            accounts = []
        return [acc.get("ManagedAccountID") for acc in accounts if acc.get("ManagedAccountID")]
    except requests.exceptions.RequestException as e:
        log_error(-1, f"GET SmartRuleAccounts hata: {str(e)}", error_type="SmartRuleAPI")
        return []

def update_smart_rule_accounts(smart_rule_id: int, account_ids: List[int]) -> bool:
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (update_smart_rule_accounts).", error_type="SmartRuleAPI")
        return False

    url = f"{API_BASE_URL}/QuickRules/{smart_rule_id}/ManagedAccounts"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    payload = {
        "AccountIDs": list(set(account_ids))
    }

    try:
        response = requests.put(url, json=payload, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        log_message(f"[SmartRuleAPI] ✅ SmartRule güncellendi. ID={smart_rule_id}, AccountIDs={payload['AccountIDs']}")
        return True
    except requests.exceptions.RequestException as e:
        log_error(-1, f"PUT SmartRuleAccounts hata: {str(e)}", error_type="SmartRuleAPI")
        return False
