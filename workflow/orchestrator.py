# workflow/orchestrator.py

from utils.logger import log_message
from excel.excel_loader import read_btmigrate_workbook
from dispatcher.managed_system_dispatcher import dispatch_managed_system
from utils.universal_cache import UniversalCache

def start_orchestration(cache: UniversalCache):
    records = read_btmigrate_workbook()

    if not records:
        log_message("❌ btmigrate_work.xlsx dosyası boş veya okunamadı.")
        return

    for i, row in enumerate(records, start=1):
        dispatch_managed_system(row, cache, row_number=i)
