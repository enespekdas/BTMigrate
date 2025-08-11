# handlers/user_member/add_user_to_group.py

from typing import List, Optional, Tuple
from math import isnan
from api.user import create_user, add_user_to_group
from utils.universal_cache import UniversalCache
from utils.logger import log_message, log_error, log_debug_row
from utils.object_tracker import add_created_object
from utils.report import user_success, user_error, USER_COLS  # ✅

def parse_member_field(members_field) -> List[str]:
    log_debug_row(-1, f"🧪 parse_member_field() → Tip: {type(members_field)}, Değer: {members_field}")
    if members_field is None:
        return []
    if isinstance(members_field, float) and (isnan(members_field) or members_field == 0.0):
        return []
    try:
        raw = str(members_field).strip()
        if raw.lower() in ("nan", "none", ""):
            return []
        raw = raw.replace(";", ",")
        # normalize + dedupe, sırayı koru
        seen, result = set(), []
        for part in raw.split(","):
            s = part.strip()
            if s and not s.replace("_", "").isdigit():
                s = s.casefold()
                if s not in seen:
                    seen.add(s)
                    result.append(s)
        return result
    except Exception:
        return []

def find_or_create_user(member_name: str, domain: str, cache: UniversalCache) -> Tuple[Optional[int], bool]:
    all_users = cache.get_cached_data("User") or []
    for user in all_users:
        if (user.get("UserName") or "").strip().casefold() == member_name.casefold():
            log_debug_row(-1, f"🧪 Cache'te bulundu: {member_name} → ID: {user.get('UserID')}")
            return user.get("UserID"), False

    user_id = create_user(member_name, domain, cache)
    if user_id:
        all_users.append({"UserName": member_name, "UserID": user_id})
        cache.cache_data("User", all_users)
        log_message(f"✅ Yeni kullanıcı cache'e eklendi: {member_name} (ID: {user_id})")
        return user_id, True
    return None, False

def add_members_to_user_group(row: dict, user_group_id: int, cache: UniversalCache) -> List[int]:
    """
    Kullanıcı yoksa oluşturur, sonra gruba ekler.
    Dönüş: başarılı bulunan/oluşturulan kullanıcı IDs.
    """
    row_number = row.get("Satır No", row.get("PamEnvanterSatır", -1))
    raw_members = row.get("members")
    domain = str(row.get("domain") or "").strip()

    log_debug_row(row_number, f"➡️ Girdi üyeleri: {raw_members} (Tip: {type(raw_members)}) → GroupID={user_group_id}")
    member_names = parse_member_field(raw_members)
    log_debug_row(row_number, f"🧪 Normalize üyeler: {member_names}")

    # Üye yoksa: step atlandı → ℹ️
    if not member_names:
        log_message(f"[Row {row_number}] ℹ️ User group'a eklenecek kullanıcı yok.")
        row[USER_COLS["genel"]] = "ℹ️"
        return []

    errors: List[str] = []
    any_failed = False
    user_ids: List[int] = []
    pairs: List[Tuple[str, Optional[int]]] = []

    created_count = 0
    existed_count = 0
    added_count = 0

    for member in member_names:
        if not domain:
            any_failed = True
            errors.append(f"Domain boş → {member}")
            log_error(row_number, f"[USER] Domain boş: {member}", error_type="UserGroupMember")
            continue

        uid, created = find_or_create_user(member, domain, cache)
        pairs.append((member, uid))
        if uid:
            user_ids.append(uid)
            if created: created_count += 1
            else:       existed_count += 1
        else:
            any_failed = True
            errors.append(f"Kullanıcı bulunamadı/oluşmadı → {member}")
            log_error(row_number, f"[USER] Kullanıcı bulunamadı/oluşturulamadı: {member}", error_type="UserGroupMember")

    total_resolved = created_count + existed_count
    if total_resolved == 0:
        any_failed = True
        errors.append("Hiçbir geçerli kullanıcı yok (create/bulma başarısız).")
        user_error(row_number, row, -7901, "Hiçbir geçerli kullanıcı bulunamadı; üyelik yapılmadı.", "UserGroupMember",
                   created_any=False, existed_all=False, added_all=False)
        return []

    # Gruba ekleme
    for name, uid in pairs:
        if not uid:  # başarısız olanlar zaten kaydedildi
            continue
        try:
            add_user_to_group(uid, user_group_id)
            log_message(f"[Row {row_number}] ➕ Kullanıcı (ID={uid}) gruba eklendi (GroupID={user_group_id})")
            added_count += 1
            add_created_object("UserGroupMembership", {"UserID": uid, "GroupID": user_group_id})
        except Exception as e:
            any_failed = True
            errors.append(f"Gruba ekleme hatası → {name} (ID={uid}): {str(e)}")
            log_error(row_number, f"[USER] Kullanıcı gruba eklenemedi: {name} (ID={uid}) / GroupID={user_group_id} / Hata: {str(e)}",
                      error_type="UserGroupMember")

    created_any = created_count > 0
    existed_all = (created_count == 0 and total_resolved > 0)
    added_all   = (added_count == total_resolved and total_resolved > 0 and not any_failed)

    if any_failed or errors:
        user_error(row_number, row, -7902, " ; ".join(errors), "UserGroupMember",
                   created_any=created_any, existed_all=existed_all, added_all=added_all)
    else:
        user_success(row_number, row, created_any=created_any, existed_all=existed_all, added_all=added_all,
                     message=f"{total_resolved} kullanıcı işlendi, tamamı gruba eklendi.")

    return user_ids
