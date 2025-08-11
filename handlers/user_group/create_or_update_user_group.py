# handlers/user_group/create_or_update_user_group.py

from typing import Optional
from api.user_group import (
    create_user_group,
    assign_role_to_user_group_for_smart_rule,
    get_all_user_groups,
    get_user_group_smart_rules,   # ✅ precheck için eklendi
)
from utils.universal_cache import UniversalCache
from utils.logger import log_message, log_debug
from config.settings import USER_GROUP_DEFAULT_PERMISSIONS
from utils.report import ug_success, ug_error, UG_COLS  # ✅


def _is_rule_already_assigned_to_group(group_id: int, smart_rule_id: int) -> bool:
    """Grubun SmartRule listesinde bu kural zaten var mı? (idempotent precheck)"""
    try:
        items = get_user_group_smart_rules(group_id) or []
        # Bazı BT sürümleri "SmartRuleID", bazıları "ID" döndürüyor
        return any(
            (it.get("SmartRuleID") == smart_rule_id) or (it.get("ID") == smart_rule_id)
            for it in items
        )
    except Exception:
        # Precheck başarısız olsa bile akışı durdurmayalım; false dönsün ve denesin
        return False


def _ensure_role(group_id: int, smart_rule_id: int, row_number: int) -> dict:
    """
    SR/Role atamasını idempotent hale getirir:
    - Zaten bağlıysa: ok=True, already=True
    - Değilse atar ve ok=True döner
    - Hata varsa ok=False, error='...'
    """
    # 1) Precheck
    if _is_rule_already_assigned_to_group(group_id, smart_rule_id):
        return {"ok": True, "already": True, "message": "SR/Role zaten atanmış"}

    # 2) Atama
    try:
        result = assign_role_to_user_group_for_smart_rule(group_id, smart_rule_id, row_number)
        # assign fonksiyonu kendi içinde 400 duplicate'i success'e çevirmiyorsa bile
        # buraya geldiysek request başarılıdır.
        return {"ok": True, "created": True}
    except Exception as e:
        # Bazı sürümler duplicate'te 400 döndürüp gövdeye "already/exist" yazabiliyor
        body = str(e).lower()
        if any(k in body for k in ("already", "exist", "duplicate")):
            return {"ok": True, "already": True, "message": "SR/Role zaten var (400 duplicate ignore)"}
        return {"ok": False, "error": str(e)}


def create_or_update_user_group(row: dict, smart_rule_id: int, cache: UniversalCache) -> Optional[int]:
    """
    Safe name'e göre user group cache'te var mı bakar.
    Yoksa yeni grup oluşturur ve ID'yi döner.
    Sonrasında SmartRule için Role atamasını idempotent şekilde yapar.
    Raporlama utils.report üzerinden yapılır.
    """
    row_number = row.get("Satır No", row.get("PamEnvanterSatır", -1))
    safe_name = (row.get("safe name") or "").strip()

    if not safe_name:
        log_message(f"[Row {row_number}] ℹ️ Safe name boş, user group atlanıyor.")
        row[UG_COLS["genel"]] = "ℹ️"
        return None

    # Cache hazır değilse bir kere yükle
    all_groups = cache.get_cached_data("UserGroup")
    if not all_groups:
        all_groups = get_all_user_groups(cache)

    # Lookup (case insensitive)
    target_key = safe_name.casefold()
    existing_group_id = None
    for group in (all_groups or []):
        group_name = (group.get("Name") or "").strip()
        if group_name.casefold() == target_key:
            existing_group_id = group.get("UserGroupID") or group.get("GroupID") or group.get("ID")
            break

    # ✅ Grup zaten var → SR/Role ensure
    if existing_group_id:
        log_message(f"[Row {row_number}] ✅ User group zaten mevcut: {safe_name} (ID: {existing_group_id})")
        result = _ensure_role(existing_group_id, smart_rule_id, row_number)
        if result.get("ok"):
            ug_success(
                row_number, row,
                already=True, created=False, sr_assigned=True, role_assigned=True,
                message=f"User group mevcut ve SR/Role ataması tamam: {safe_name} ({result.get('message','ok')})"
            )
        else:
            ug_error(row_number, row, -861,
                     f"SmartRule/Role ataması başarısız: {result.get('error','bilinmeyen hata')}", "UserGroup")
        return existing_group_id

    # 🆕 Yeni oluştur → create sırasında SmartRuleAccess gönderiyoruz
    payload = {
        "groupType": "BeyondInsight",
        "groupName": safe_name,
        "description": safe_name,
        "isActive": True,
        "Permissions": USER_GROUP_DEFAULT_PERMISSIONS,
        "SmartRuleAccess": [{"SmartRuleID": smart_rule_id, "AccessLevelID": 3}],
    }

    log_debug(f"[Row {row_number}] 🧱 User group oluşturma payload: {payload}")
    log_message(f"[Row {row_number}] 🚀 Yeni user group oluşturuluyor: {safe_name}")

    try:
        group_id = create_user_group(payload, cache)
        if not group_id:
            ug_error(row_number, row, -862, "User group oluşturuldu ama ID alınamadı/None döndü.", "UserGroup")
            return None

        # Bazı sürümler create esnasında SmartRuleAccess'i yok sayabiliyor → ensure et
        result = _ensure_role(group_id, smart_rule_id, row_number)
        if result.get("ok"):
            ug_success(
                row_number, row,
                already=False, created=True, sr_assigned=True, role_assigned=True,
                message=f"User group oluşturuldu ve SR/Role garanti altına alındı: {safe_name} ({result.get('message','ok')})"
            )
        else:
            ug_error(row_number, row, -863,
                     f"SmartRule/Role ataması başarısız: {result.get('error','bilinmeyen hata')}", "UserGroup")

        return group_id

    except Exception as e:
        ug_error(row_number, row, -899, f"User group oluşturulurken hata: {str(e)}", "UserGroup")
        return None
