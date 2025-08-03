# api/user_group.py

import os
import requests
from typing import Optional
from config.settings import API_BASE_URL, VERIFY_SSL
from utils.logger import log_error, log_message
from utils.universal_cache import UniversalCache

USER_GROUPS_KEY = "UserGroup"

def get_all_user_groups(cache: UniversalCache):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (user group).", error_type="UserGroupAPI")
        return []

    url = f"{API_BASE_URL}/UserGroups"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        groups = response.json()

        cache.cache_data(USER_GROUPS_KEY, groups)
        log_message(f"📥 User group listesi API'den alındı ve cache'e yazıldı. ({len(groups)} kayıt)")
        return groups

    except Exception as e:
        log_error(-1, f"User group listesi alınırken hata oluştu: {str(e)}", error_type="UserGroupAPI")
        return []

def create_user_group(payload: dict, cache: UniversalCache) -> Optional[int]:
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (user group).", error_type="UserGroupAPI")
        return None

    url = f"{API_BASE_URL}/UserGroups"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, verify=VERIFY_SSL)
        response.raise_for_status()

        created = response.json()
        log_message(f"🧪 [DEBUG] UserGroup API response: {created}")

        group_id = created.get("UserGroupID") or created.get("GroupID") or created.get("ID")
        if not group_id:
            log_error(-1, f"User group oluşturuldu ama ID bilgisi alınamadı. Response: {created}", error_type="UserGroupAPI")
            return None

        log_message(f"✅ User group oluşturuldu: {payload['groupName']} (ID: {group_id})")

        current = cache.get_cached_data("UserGroup") or []
        current.append({
            "Name": payload["groupName"],
            "UserGroupID": group_id
        })
        cache.cache_data("UserGroup", current)

        return group_id

    except requests.exceptions.RequestException as e:
        log_error(-1, f"User group oluşturma hatası: {str(e)}", error_type="UserGroupAPI")
        return None

def assign_role_to_user_group_for_smart_rule(group_id: int, smart_rule_id: int, row_number: int):
    """
    Belirli bir UserGroup için SmartRule'e Role ataması yapar (AccessPolicyID: 5000, RoleID: 3).
    """
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(row_number, "Session ID bulunamadı (role assign).", error_type="UserGroupRole")
        return

    url = f"{API_BASE_URL}/UserGroups/{group_id}/SmartRules/{smart_rule_id}/Roles"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    payload = {
        "Roles": [{"RoleID": "3"}],
        "AccessPolicyID": "5000"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, verify=VERIFY_SSL)
        response.raise_for_status()
        log_message(f"[Row {row_number}] ✅ SmartRule Role ataması başarılı → GroupID={group_id}, RuleID={smart_rule_id}")
    except requests.exceptions.RequestException as e:
        log_error(row_number, f"❌ SmartRule Role atama hatası: {str(e)}", error_type="UserGroupRole")
