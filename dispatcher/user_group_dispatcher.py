# dispatcher/user_group_dispatcher.py

from typing import Optional
from utils.universal_cache import UniversalCache
from handlers.user_group.create_or_update_user_group import create_or_update_user_group
from utils.report import ug_init, ug_error  # ✅

def dispatch_user_group(row: dict, smart_rule_id: int, cache: UniversalCache) -> Optional[int]:
    ug_init(row)  # kolonları defaultla (✅ / Hayır)
    try:
        return create_or_update_user_group(row, smart_rule_id, cache)
    except Exception as e:
        row_number = row.get("Satır No", row.get("PamEnvanterSatır", -1))
        ug_error(row_number, row, -880, f"UserGroup Dispatcher exception: {str(e)}", "UserGroupDispatcher")
        return None
