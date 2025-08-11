# handlers/managed_account/ad_account_link_to_managed_system.py

from api.managed_account import link_managed_account_to_system
from utils.report import ma_set_link_status, ma_error

def link_ad_account_to_managed_system(row: dict, managed_account_id: int, cache):
    row_number = row.get("PamEnvanterSatır", -1)
    ip_address = row.get("ip address")

    all_managed_systems = cache.get_all_by_key("ManagedSystem")
    matched = [s for s in all_managed_systems if (s.get("IPAddress") or "").strip() == ip_address]

    if len(matched) == 0:
        ma_set_link_status(row, False, f"IP eşleşmesi bulunamadı. IP: {ip_address}")
        return
    if len(matched) > 1:
        ma_set_link_status(row, False, f"Aynı IP ({ip_address}) ile birden fazla managed system bulundu.")
        return

    managed_system_id = matched[0].get("ManagedSystemID")
    if not managed_system_id:
        ma_set_link_status(row, False, f"ManagedSystemID yok. Kayıt: {matched[0]}")
        return

    try:
        link_managed_account_to_system(managed_system_id, managed_account_id)
        ma_set_link_status(row, True)
    except Exception as e:
        # API wrapper zaten logluyor olabilir; yine de hata detayı verelim
        ma_set_link_status(row, False, f"Linkleme API hatası: {str(e)}")
