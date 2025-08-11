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
from excel.output_writer import append_row_to_output
from utils.object_tracker import add_created_object
from utils.report import (
    finalize_overall,
    ms_error, ma_error, sr_error, app_error, ug_error, user_error,
)

def start_orchestration(cache: UniversalCache):
    """
    Not: ManagedSystem / FunctionalAccount / SmartRule / Application / UserGroup / User
    ön yüklemeleri core/cache_initializer.initialize_cache() içinde yapılıyor.
    Burada sadece adımları çalıştırıyoruz.
    """
    records = read_btmigrate_workbook()
    if not records:
        log_message("❌ btmigrate_work.xlsx dosyası boş veya okunamadı.")
        return

    for i, row in enumerate(records, start=1):
        # Satır meta
        row["Satır No"] = i
        row["Kullanıcı Adı"] = row.get("username", "")
        row["IP Adresi"] = row.get("ip address", "")
        row["Hostname"] = row.get("hostname", "")
        row["İşletim Sistemi"] = row.get("OS", "")
        row["Domain"] = row.get("domain", "")

        managed_account_id = None
        smart_rule_id = None
        user_group_id = None  # ✅ baştan tanımla

        # ✅ Managed System
        try:
            managed_system_id = dispatch_managed_system(row, cache, row_number=i)
            if managed_system_id:
                row["MS - ID"] = managed_system_id
                add_created_object("ManagedSystem", managed_system_id)
        except Exception as e:
            ms_error(i, row, -1999, f"Orchestrator MS exception: {str(e)}", "Orchestrator")

        # ✅ Managed Account
        try:
            managed_account_id = dispatch_managed_account_create(row, cache)
            if managed_account_id:
                add_created_object("ManagedAccount", managed_account_id)
        except Exception as e:
            ma_error(i, row, -2999, f"Orchestrator MA exception: {str(e)}", "Orchestrator")

        # ✅ Smart Rule
        try:
            if managed_account_id:
                smart_rule_id = dispatch_smart_rule(row, managed_account_id, cache)
                if smart_rule_id:
                    add_created_object("SmartRule", smart_rule_id)
        except Exception as e:
            sr_error(i, row, -3999, f"Orchestrator SR exception: {str(e)}", "Orchestrator")

        # ✅ Application
        try:
            if managed_account_id:
                dispatch_application_assignment(row, managed_account_id, cache)
        except Exception as e:
            app_error(i, row, -4999, f"Orchestrator APP exception: {str(e)}", "Orchestrator")

        # ✅ User Group
        try:
            if smart_rule_id:
                user_group_id = dispatch_user_group(row, smart_rule_id, cache)
                if user_group_id:
                    add_created_object("UserGroup", user_group_id)
        except Exception as e:
            ug_error(i, row, -5899, f"Orchestrator UG exception: {str(e)}", "Orchestrator")

        # ✅ User Members
        try:
            if user_group_id:
                user_ids = dispatch_user_members(row, user_group_id, cache)
                for uid in user_ids:
                    add_created_object("User", uid)
        except Exception as e:
            user_error(i, row, -8900, f"Orchestrator USER exception: {str(e)}", "Orchestrator")

        # Üst genel durum
        finalize_overall(row)

        # Excel’e yaz
        append_row_to_output(row)
