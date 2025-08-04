# handlers/user_member/add_user_to_group.py

from typing import List, Optional
from math import isnan
from api.user import create_user, add_user_to_group
from utils.universal_cache import UniversalCache
from utils.logger import log_message, log_error, log_debug_row
from utils.object_tracker import add_created_object  # ✅ JSON takibi için eklendi


def parse_member_field(members_field) -> List[str]:
    """
    Excel'den gelen members alanını işler ve geçerli kullanıcı isimlerini döner.
    Boş, NaN veya geçersiz veriler filtrelenir.
    """
    log_debug_row(-1, f"🧪 parse_member_field() → Tip: {type(members_field)}, Değer: {members_field}")

    if members_field is None:
        return []

    if isinstance(members_field, float) and (isnan(members_field) or members_field == 0.0):
        return []

    try:
        raw = str(members_field).strip()
        if raw.lower() in ("nan", "none", ""):
            return []

        result = []
        for m in raw.split(","):
            s = str(m).strip()
            if s and not s.replace("_", "").isdigit():
                result.append(s.lower())
        return result

    except Exception as e:
        log_debug_row(-1, f"❌ parse_member_field exception: {str(e)}")
        return []


def find_or_create_user(member_name: str, domain: str, cache: UniversalCache) -> Optional[int]:
    """
    Kullanıcıyı cache'te arar. Yoksa create eder ve cache'e ekler.
    """
    all_users = cache.get_cached_data("User") or []

    for user in all_users:
        if (user.get("UserName") or "").strip().lower() == member_name.lower():
            log_debug_row(-1, f"🧪 Cache'te bulundu: {member_name} → ID: {user.get('UserID')}")
            return user.get("UserID")

    user_id = create_user(member_name, domain, cache)
    if user_id:
        all_users.append({"UserName": member_name, "UserID": user_id})
        cache.cache_data("User", all_users)
        log_message(f"✅ Yeni kullanıcı cache'e eklendi: {member_name} (ID: {user_id})")
    return user_id


def add_members_to_user_group(row: dict, user_group_id: int, cache: UniversalCache) -> List[int]:
    """
    Excel'den gelen bir satıra göre user group'a üye ekler.
    Kullanıcı yoksa oluşturur.
    Dönen değer: Gruba başarıyla eklenen kullanıcıların ID'leri
    """
    row_number = row.get("PamEnvanterSatır", -1)
    raw_members = row.get("members")
    domain = str(row.get("domain") or "").strip()

    log_debug_row(row_number, f"➡️ Girdi üyeleri: {raw_members} (Tip: {type(raw_members)}) → GroupID={user_group_id}")
    member_names = parse_member_field(raw_members)
    log_debug_row(row_number, f"🧪 Normalize üyeler: {member_names}")

    if not member_names:
        log_message(f"[Row {row_number}] ⚠️ User group'a eklenecek kullanıcı yok.")
        return []

    user_ids = []
    for member in member_names:
        user_id = find_or_create_user(member, domain, cache)
        if user_id:
            user_ids.append(user_id)
        else:
            log_error(row_number, f"❌ Kullanıcı bulunamadı veya oluşturulamadı: {member}", error_type="UserGroupMember")

    if not user_ids:
        log_error(row_number, "❌ Hiçbir geçerli kullanıcı bulunamadı, user group'a üye eklenmeyecek.", error_type="UserGroupMember")
        return []

    for uid in user_ids:
        try:
            add_user_to_group(uid, user_group_id)
            log_message(f"[Row {row_number}] ➕ Kullanıcı (ID={uid}) gruba eklendi (GroupID={user_group_id})")

            # ✅ JSON silme için User-Group eşleşmesini kaydet
            add_created_object("UserGroupMembership", {"UserID": uid, "GroupID": user_group_id})

        except Exception as e:
            failed_name = member_names[user_ids.index(uid)] if user_ids.index(uid) < len(member_names) else "?"
            log_error(
                row_number,
                f"❌ Kullanıcı (ID={uid}) gruba eklenemedi (GroupID={user_group_id}) → Kullanıcı: {failed_name} → Hata: {str(e)}",
                error_type="UserGroupMember"
            )

    return user_ids  # ✅ JSON log için gerekli olan bu
