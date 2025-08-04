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

def start_orchestration(cache: UniversalCache):
    records = read_btmigrate_workbook()

    if not records:
        log_message("❌ btmigrate_work.xlsx dosyası boş veya okunamadı.")
        return

    for i, row in enumerate(records, start=1):
        row["Satır No"] = i
        row["Kullanıcı Adı"] = row.get("username", "")
        row["IP Adresi"] = row.get("ip address", "")
        row["Hostname"] = row.get("hostname", "")
        row["İşletim Sistemi"] = row.get("OS", "")
        row["Domain"] = row.get("domain", "")

        try:
            # ✅ Managed System
            dispatch_managed_system(row, cache, row_number=i)
        except Exception as e:
            row["MS - Genel Durum"] = "❌"
            row["Hata Detayı"] = f"[MS] {str(e)}"

        # try:
        #     # ✅ Managed Account
        #     managed_account_id = dispatch_managed_account_create(row, cache)
        # except Exception as e:
        #     row["MA - Genel Durum"] = "❌"
        #     row["Hata Detayı"] = f"[MA] {str(e)}"

        # try:
        #     # ✅ Smart Rule
        #     if managed_account_id:
        #         smart_rule_id = dispatch_smart_rule(row, managed_account_id, cache)
        # except Exception as e:
        #     row["SR - Genel Durum"] = "❌"
        #     row["Hata Detayı"] = f"[SR] {str(e)}"

        # try:
        #     # ✅ Application
        #     if managed_account_id:
        #         dispatch_application_assignment(row, managed_account_id, cache)
        # except Exception as e:
        #     row["App - Genel Durum"] = "❌"
        #     row["Hata Detayı"] = f"[APP] {str(e)}"

        # try:
        #     # ✅ User Group
        #     if smart_rule_id:
        #         user_group_id = dispatch_user_group(row, smart_rule_id, cache)
        # except Exception as e:
        #     row["UG - Genel Durum"] = "❌"
        #     row["Hata Detayı"] = f"[UG] {str(e)}"

        # try:
        #     # ✅ User Members
        #     if user_group_id:
        #         dispatch_user_members(row, user_group_id, cache)
        # except Exception as e:
        #     row["User - Genel Durum"] = "❌"
        #     row["Hata Detayı"] = f"[USER] {str(e)}"

        # 🔍 Genel Başarı Kontrolü
        if all(row.get(k) == "✅" for k in [
            "MS - Genel Durum", "MA - Genel Durum", "SR - Genel Durum",
            "App - Genel Durum", "UG - Genel Durum", "User - Genel Durum"
        ]):
            row["Genel Durum"] = "✅"
        else:
            row["Genel Durum"] = "❌"

        # 📤 Excel'e yaz
        append_row_to_output(row)
