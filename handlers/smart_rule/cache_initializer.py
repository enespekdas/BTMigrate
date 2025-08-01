# handlers/cache_initializer.py

from api.smart_rule import get_all_smart_rules
from utils.universal_cache import UniversalCache
from utils.logger import log_message

def initialize_smart_rule_cache(cache: UniversalCache):
    smart_rules = get_all_smart_rules()
    cache.cache_data("SmartRule", smart_rules)
    log_message(f"✅ SmartRule cache yüklendi. ({len(smart_rules)} kayıt)")
