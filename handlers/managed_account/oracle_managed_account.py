from typing import Optional
from utils.logger import log_message, log_error, log_debug
from utils.universal_cache import UniversalCache
from config.settings import DEFAULT_PASSWORD, WORKGROUP_ID
from api.managed_account import (
    get_managed_accounts_by_system_id,
    create_oracle_managed_account_api_call
)

def create_oracle_managed_account(row: dict, cache: UniversalCache) -> Optional[int]:
    try:
        row_number = row.get("PamEnvanterSatır", -1)
        ip_address = row.get("ip address")
        username = row.get("username")
        port = int(float(row.get("port", 1521)))

        log_debug(f"[Row {row_number}] 🔍 Oracle Managed Account işlemi başlatıldı. IP: {ip_address}, Username: {username}")

        if not username or not username.lower().startswith("pam"):
            log_message(f"[Row {row_number}] ℹ️ Atlandı: 'pam' ile başlamayan Oracle username: {username}")
            return None

        all_managed_systems = cache.get_all_by_key("ManagedSystem")
        matched_systems = [
            s for s in all_managed_systems if (s.get("IPAddress") or "").strip() == ip_address
        ]

        if len(matched_systems) == 0:
            log_error(row_number, f"🔗 IP ile eşleşen managed system bulunamadı. IP: {ip_address}", error_type="OracleManagedAccount")
            return None
        elif len(matched_systems) > 1:
            log_error(row_number, f"⚠️ Aynı IP ile birden fazla managed system bulundu. IP: {ip_address}", error_type="OracleManagedAccount")
            return None

        managed_system_id = matched_systems[0].get("ManagedSystemID")
        log_debug(f"[Row {row_number}] 🆔 Bulunan managed system ID: {managed_system_id}")

        existing_accounts = get_managed_accounts_by_system_id(managed_system_id)
        matched_account = next(
            (acc for acc in existing_accounts if (acc.get("AccountName") or "").lower() == username.lower()),
            None
        )

        # Ortak log kolonları
        row["MA - Tür"] = "Oracle"
        row["MA - Kullanılan Account"] = username
        row["MA - AutoChange Durumu"] = "Kapalı"
        row["MA - Linkleme Durumu"] = "-"  # Oracle'da linkleme yapılmıyor

        if matched_account:
            managed_account_id = matched_account.get("ManagedAccountID")
            log_message(f"[Row {row_number}] ✅ Oracle managed account zaten var: {username}")
            row["MA - Zaten Var mı?"] = "Evet"
            row["MA - Oluşturuldu mu?"] = "Hayır"
        else:
            payload = {
                "AccountName": username,
                "Password": DEFAULT_PASSWORD,
                "PasswordRuleID": 0,
                "WorkgroupID": WORKGROUP_ID,
                "Port": port,
                "UseOwnCredentials": True,
                "AutoManagementFlag": False
            }

            log_debug(f"[Row {row_number}] 📦 Payload hazırlandı: {payload}")
            log_message(f"[Row {row_number}] 🚀 Oracle managed account oluşturuluyor: {username}")

            response = create_oracle_managed_account_api_call(managed_system_id, payload)
            managed_account_id = response.get("ManagedAccountID") if response else None

            if managed_account_id:
                row["MA - Zaten Var mı?"] = "Hayır"
                row["MA - Oluşturuldu mu?"] = "Evet"

        return managed_account_id

    except Exception as e:
        log_error(row.get("PamEnvanterSatır", -1), f"💥 Hata (Oracle managed account): {str(e)}", error_type="OracleManagedAccount")
        row["MA - Genel Durum"] = "❌"
        return None
