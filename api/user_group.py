# api/user_group.py

import os
import requests
from typing import Optional, Dict, Any, List
from config.settings import API_BASE_URL, VERIFY_SSL
from utils.logger import log_error, log_message, log_debug
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

        current = cache.get_cached_data(USER_GROUPS_KEY) or []
        current.append({
            "Name": payload["groupName"],
            "UserGroupID": group_id
        })
        cache.cache_data(USER_GROUPS_KEY, current)

        return int(group_id) if str(group_id).isdigit() else group_id

    except requests.exceptions.RequestException as e:
        log_error(-1, f"User group oluşturma hatası: {str(e)}", error_type="UserGroupAPI")
        return None


# ✅ PRECHECK: Grubun hangi SmartRule'lara bağlı olduğunu getir
def get_user_group_smart_rules(group_id: int) -> List[dict]:
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (get group smart rules).", error_type="UserGroupAPI")
        return []

    url = f"{API_BASE_URL}/UserGroups/{group_id}/SmartRules"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=VERIFY_SSL)
        response.raise_for_status()
        return response.json() or []
    except requests.exceptions.RequestException as e:
        log_error(-1, f"User group smart rules alınamadı: {str(e)}", error_type="UserGroupAPI")
        return []


def _is_rule_already_assigned(group_id: int, smart_rule_id: int) -> bool:
    try:
        items = get_user_group_smart_rules(group_id)
        # Bazı sürümlerde "SmartRuleID", bazılarında "ID" dönebiliyor
        return any(
            (it.get("SmartRuleID") == smart_rule_id) or (it.get("ID") == smart_rule_id)
            for it in items
        )
    except Exception as e:
        log_debug(f"[UGRole] Precheck hata: {e}")
        return False


def assign_role_to_user_group_for_smart_rule(group_id: int, smart_rule_id: int, row_number: int) -> Dict[str, Any]:
    """
    Belirli bir UserGroup için SmartRule'e Role ataması yapar.
    İdempotent: Önce ilişkili mi diye kontrol eder; varsa POST atmaz.
    400 duplicate durumlarında body "already/exist/duplicate" içeriyorsa başarıya sayar.

    NOT: Şu an canlıda başarıyla çalışan payload'ı koruyoruz:
      payload = {
          "Roles": [{"RoleID": "3"}],
          "AccessPolicyID": "5000"
      }
    """
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        msg = "Session ID bulunamadı (role assign)."
        log_error(row_number, msg, error_type="UserGroupRole")
        return {"ok": False, "error": msg}

    # ✅ Precheck – zaten bağlıysa başarı
    # if _is_rule_already_assigned(group_id, smart_rule_id):
    #     log_message(f"[Row {row_number}] ✅ SR/Role zaten atanmış → GroupID={group_id}, RuleID={smart_rule_id}")
    #     return {"ok": True, "already": True}

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
        if response.status_code == 400:
            # Bazı BT sürümleri duplicate'te 400 döndürür; body'yi inceleyelim
            body = (response.text or "").lower()
            if any(k in body for k in ("already", "exist", "duplicate")):
                log_message(f"[Row {row_number}] ✅ SR/Role zaten var (400 duplicate ignore) → GroupID={group_id}, RuleID={smart_rule_id}")
                return {"ok": True, "already": True}
        response.raise_for_status()
        log_message(f"[Row {row_number}] ✅ SmartRule Role ataması başarılı → GroupID={group_id}, RuleID={smart_rule_id}")
        return {"ok": True}

    except requests.exceptions.RequestException as e:
        msg = f"SmartRule Role atama hatası: {str(e)}"
        log_error(row_number, f"❌ {msg}", error_type="UserGroupRole")
        return {"ok": False, "error": msg}
