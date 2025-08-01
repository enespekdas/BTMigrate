# cache_initializer.py

from api.managed_system import get_all_managed_systems
from utils.universal_cache import UniversalCache
from utils.logger import log_message, log_error

def initialize_cache() -> UniversalCache:
    cache = UniversalCache()

    try:
        managed_systems = get_all_managed_systems(cache)  # ✅ Parametre eklendi
        cache.cache_data("ManagedSystems", managed_systems)
        cache.build_index("ManagedSystems", "IPAddress")
        cache.build_index("ManagedSystems", "Name")
        log_message("✅ ManagedSystem cache yüklendi. ({} kayıt)".format(len(managed_systems)))
    except Exception as e:
        log_error(-1, f"❌ ManagedSystem cache yüklenirken hata: {str(e)}", error_type="Cache")

    return cache
