# dispatcher/user_group_dispatcher.py

from utils.universal_cache import UniversalCache
from handlers.user_group.create_or_update_user_group import create_or_update_user_group
from typing import Optional

def dispatch_user_group(row: dict, smart_rule_id: int, cache: UniversalCache) -> Optional[int]:
    """
    Smart Rule ID'ye göre User Group cache kontrolü ve oluşturma işlemini başlatır.
    """
    return create_or_update_user_group(row, smart_rule_id, cache)
