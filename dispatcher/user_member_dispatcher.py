# dispatcher/user_member_dispatcher.py

from utils.universal_cache import UniversalCache
from handlers.user_member.add_user_to_group import add_members_to_user_group
from utils.logger import log_error

def dispatch_user_members(row: dict, user_group_id: int, cache: UniversalCache) -> None:
    """
    Excel'den gelen 'members' alanına göre kullanıcıları user group'a ekler.
    Her kullanıcı önce cache'te aranır, yoksa oluşturulur, ardından gruba eklenir.
    """
    row_number = row.get("PamEnvanterSatır", -1)
    try:
        add_members_to_user_group(row, user_group_id, cache)
    except Exception as e:
        log_error(row_number, f"❌ User group üyeleri eklenemedi: {str(e)}", error_type="UserGroupMember")
