# dispatcher/user_member_dispatcher.py

from typing import List, Optional
from utils.universal_cache import UniversalCache
from handlers.user_member.add_user_to_group import add_members_to_user_group
from utils.report import user_init, user_error  # ✅

def dispatch_user_members(row: dict, user_group_id: int, cache: UniversalCache) -> List[int]:
    """
    'members' alanına göre kullanıcıları user group'a ekler.
    """
    user_init(row)  # kolonları defaultla (✅ / Hayır)
    row_number = row.get("Satır No", row.get("PamEnvanterSatır", -1))
    try:
        return add_members_to_user_group(row, user_group_id, cache)  # ID listesi bekliyoruz
    except Exception as e:
        user_error(row_number, row, -7800, f"User members dispatcher exception: {str(e)}", "UserGroupMember")
        return []
