# test_fa_dump.py

from api.functional_account import get_all_functional_accounts
from utils.logger import setup_logging
from utils.universal_cache import UniversalCache
import auth.login  # Session ID'yi set eder

setup_logging()

# Yeni cache oluştur ve fonksiyona geçir
cache = UniversalCache()
get_all_functional_accounts(cache)

fa_list = cache.get_cached_data("FunctionalAccount")
print(f"Toplam {len(fa_list)} Functional Account bulundu:\n")

for fa in fa_list:
    domain = fa.get('DomainName')
    desc = fa.get('Description')
    fa_id = fa.get('Id')
    print(f"→ ID={fa_id}, Domain={domain}, Description={desc}")
