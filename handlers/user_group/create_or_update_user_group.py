# handlers/user_group/create_or_update_user_group.py

from typing import Optional
from api.user_group import create_user_group, assign_role_to_user_group_for_smart_rule
from utils.universal_cache import UniversalCache
from utils.logger import log_message, log_debug, log_error
from config.settings import USER_GROUP_DEFAULT_PERMISSIONS

def create_or_update_user_group(row: dict, smart_rule_id: int, cache: UniversalCache) -> Optional[int]:
    """
    Safe name'e göre user group cache'te var mı bakar.
    Yoksa yeni grup oluşturur ve ID'yi döner.
    Sonrasında SmartRule için Role ataması yapılır.
    """
    row_number = row.get("PamEnvanterSatır", -1)
    safe_name = (row.get("safe name") or "").strip()

    if not safe_name:
        log_message(f"[Row {row_number}] ⚠️ Safe name boş, user group oluşturulmayacak.")
        return None

    all_groups = cache.get_cached_data("UserGroup") or []
    for group in all_groups:
        group_name = (group.get("Name") or "").strip().lower()
        if group_name == safe_name.lower():
            group_id = group.get("GroupID") or group.get("UserGroupID") or group.get("ID")
            log_message(f"[Row {row_number}] ✅ User group zaten mevcut: {safe_name}")
            log_message(f"[Row {row_number}] 🔍 UserGroupID: {group_id}")

            # ✅ Rol ataması yap
            assign_role_to_user_group_for_smart_rule(group_id, smart_rule_id, row_number)
            return group_id

    # Yeni oluşturulacak payload
    payload = {
        "groupType": "BeyondInsight",
        "groupName": safe_name,
        "description": safe_name,
        "isActive": True,
        "Permissions": USER_GROUP_DEFAULT_PERMISSIONS,
        "SmartRuleAccess": [
            {
                "SmartRuleID": smart_rule_id,
                "AccessLevelID": 3
            }
        ]
    }

    log_debug(f"[Row {row_number}] 🧱 User group oluşturma payload: {payload}")
    log_message(f"[Row {row_number}] 🚀 Yeni user group oluşturuluyor: {safe_name}")

    try:
        group_id = create_user_group(payload, cache)
        if group_id:
            assign_role_to_user_group_for_smart_rule(group_id, smart_rule_id, row_number)
        return group_id
    except Exception as e:
        log_error(row_number, f"❌ User group oluşturulurken hata: {str(e)}", error_type="UserGroup")
        return None
