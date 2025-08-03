# workflow/orchestrator.py

from utils.logger import log_message
from excel.excel_loader import read_btmigrate_workbook
from dispatcher.managed_system_dispatcher import dispatch_managed_system
from dispatcher.managed_account_dispatcher import dispatch_managed_account_create
from dispatcher.smart_rule_dispatcher import dispatch_smart_rule
from dispatcher.application_dispatcher import dispatch_application_assignment
from dispatcher.user_group_dispatcher import dispatch_user_group
from dispatcher.user_member_dispatcher import dispatch_user_members
from utils.universal_cache import UniversalCache

def start_orchestration(cache: UniversalCache):
    records = read_btmigrate_workbook()

    if not records:
        log_message("❌ btmigrate_work.xlsx dosyası boş veya okunamadı.")
        return

    for i, row in enumerate(records, start=1):
        # ✅ Managed System oluştur
        dispatch_managed_system(row, cache, row_number=i)

        # ✅ Managed Account oluştur
        managed_account_id = dispatch_managed_account_create(row, cache)

        if managed_account_id:
            # ✅ Smart Rule oluştur → SmartRuleID alınır
            smart_rule_id = dispatch_smart_rule(row, managed_account_id, cache)

            if smart_rule_id:
                # ✅ Application ataması
                dispatch_application_assignment(row, managed_account_id, cache)

                # ✅ User Group oluştur ve ID al
                user_group_id = dispatch_user_group(row, smart_rule_id, cache)
                log_message(f"[Row {i}] 🔍 UserGroupID: {user_group_id}")  # ➕ Bunu ekle


                # ✅ Kullanıcıları user group'a üye olarak ekle
                if user_group_id:
                    log_message(f"[Row {i}] 🧪 UserMember işlemi başlatılıyor... GroupID={user_group_id}")

                    dispatch_user_members(row, user_group_id, cache)
