# core/cache_initializer.py

from api.managed_system import get_all_managed_systems
from api.functional_account import get_all_functional_accounts
from utils.universal_cache import UniversalCache
from utils.logger import log_message, log_error

def initialize_cache() -> UniversalCache:
    cache = UniversalCache()

    # ✅ Managed Systems
    try:
        managed_systems = get_all_managed_systems(cache)
        cache.cache_data("ManagedSystem", managed_systems)
        cache.build_index("ManagedSystem", "Name")
        cache.build_index("ManagedSystem", "IPAddress")
        log_message(f"✅ ManagedSystem cache yüklendi. ({len(managed_systems)} kayıt)")
    except Exception as e:
        log_error(-1, f"❌ ManagedSystem cache yüklenirken hata: {str(e)}", error_type="Cache")

    # ✅ Functional Accounts
    try:
        functional_accounts = get_all_functional_accounts(cache)
        log_message(f"✅ FunctionalAccount cache yüklendi. ({len(functional_accounts)} kayıt)")
    except Exception as e:
        log_error(-2, f"❌ FunctionalAccount cache yüklenirken hata: {str(e)}", error_type="Cache")

    return cache
