# handlers/managed_account/ad_account_link_to_managed_system.py

from utils.logger import log_error, log_debug, log_message
from api.managed_account import link_managed_account_to_system

def link_ad_account_to_managed_system(row: dict, managed_account_id: int, cache):
    row_number = row.get("PamEnvanterSatır", -1)
    ip_address = row.get("ip address")

    try:
        all_managed_systems = cache.get_all_by_key("ManagedSystem")

        matched = [
            s for s in all_managed_systems
            if (s.get("IPAddress") or "").strip() == ip_address
        ]

        if len(matched) == 0:
            log_error(row_number, f"🔗 Linkleme için IP eşleşmesi bulunamadı. IP: {ip_address}", error_type="AccountLinker")
            return

        if len(matched) > 1:
            raise Exception(f"🔴 Aynı IP ({ip_address}) ile birden fazla managed system bulundu. Tanım hatalı!")

        managed_system_id = matched[0].get("ManagedSystemID")
        if not managed_system_id:
            log_error(row_number, f"🔗 IP eşleşti ama ManagedSystemID alınamadı. Kayıt: {matched[0]}", error_type="AccountLinker")
            return

        log_message(f"[Row {row_number}] 🔗 Linkleme işlemi başlatıldı → SystemID: {managed_system_id}, AccountID: {managed_account_id}")
        link_managed_account_to_system(managed_system_id, managed_account_id)

    except Exception as e:
        log_error(row_number, f"💥 Linkleme hatası: {str(e)}", error_type="AccountLinker")
