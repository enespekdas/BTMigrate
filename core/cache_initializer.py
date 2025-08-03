# core/cache_initializer.py

from api.managed_system import get_all_managed_systems
from api.functional_account import get_all_functional_accounts
from api.smart_rule import get_all_smart_rules
from api.application import get_all_applications
from api.user_group import get_all_user_groups
from api.user import get_all_users  # ✅ Yeni eklendi

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

    # ✅ Smart Rules
    try:
        smart_rules = get_all_smart_rules()
        cache.cache_data("SmartRule", smart_rules)
        log_message(f"✅ SmartRule cache yüklendi. ({len(smart_rules)} kayıt)")
    except Exception as e:
        log_error(-3, f"❌ SmartRule cache yüklenirken hata: {str(e)}", error_type="Cache")

    # ✅ Applications
    try:
        applications = get_all_applications(cache)
        log_message(f"✅ Application cache yüklendi. ({len(applications)} kayıt)")
    except Exception as e:
        log_error(-4, f"❌ Application cache yüklenirken hata: {str(e)}", error_type="Cache")

    # ✅ User Groups
    try:
        user_groups = get_all_user_groups(cache)
        log_message(f"✅ UserGroup cache yüklendi. ({len(user_groups)} kayıt)")
    except Exception as e:
        log_error(-5, f"❌ UserGroup cache yüklenirken hata: {str(e)}", error_type="Cache")

    # ✅ Users
    try:
        users = get_all_users(cache)
        log_message(f"✅ User cache yüklendi. ({len(users)} kayıt)")
    except Exception as e:
        log_error(-6, f"❌ User cache yüklenirken hata: {str(e)}", error_type="Cache")

    return cache
