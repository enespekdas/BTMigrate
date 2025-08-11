# handlers/managed_account/oracle_managed_account.py

from typing import Optional
from utils.universal_cache import UniversalCache
from config.settings import DEFAULT_PASSWORD, WORKGROUP_ID
from api.managed_account import (
    get_managed_accounts_by_system_id,
    create_oracle_managed_account_api_call
)
from utils.report import ma_success, ma_error

def create_oracle_managed_account(row: dict, cache: UniversalCache) -> Optional[int]:
    row_number = row.get("PamEnvanterSatır", -1)
    try:
        ip_address = row.get("ip address")
        username = row.get("username") or ""
        port_raw = row.get("port", 1521)

        # ‘pam’ ile başlamayan kullanıcılar dispatcher’da zaten atlanıyor.
        # Yine de burada koruma:
        if not username.lower().startswith("pam"):
            return None

        # Ortak kolonlar
        row["MA - Tür"] = "Oracle"
        row["MA - Kullanılan Account"] = username
        row["MA - AutoChange Durumu"] = "Kapalı"
        row["MA - Linkleme Durumu"] = "-"  # Oracle'da link yok

        try:
            port = int(float(port_raw))
        except Exception:
            ma_error(row_number, row, -420, f"Port değeri geçersiz: {port_raw}", "OracleManagedAccount")
            return None

        all_managed_systems = cache.get_all_by_key("ManagedSystem")
        matched_systems = [s for s in all_managed_systems if (s.get("IPAddress") or "").strip() == ip_address]

        if len(matched_systems) == 0:
            ma_error(row_number, row, -421, f"IP ile eşleşen managed system bulunamadı. IP: {ip_address}", "OracleManagedAccount")
            return None
        if len(matched_systems) > 1:
            ma_error(row_number, row, -422, f"Aynı IP ile birden fazla managed system bulundu. IP: {ip_address}", "OracleManagedAccount")
            return None

        managed_system_id = matched_systems[0].get("ManagedSystemID")
        existing_accounts = get_managed_accounts_by_system_id(managed_system_id)
        matched_account = next((acc for acc in existing_accounts if (acc.get("AccountName") or "").lower() == username.lower()), None)

        if matched_account:
            managed_account_id = matched_account.get("ManagedAccountID")
            ma_success(row_number, row, already=True, message=f"Oracle managed account zaten var: {username}")
            return managed_account_id

        payload = {
            "AccountName": username,
            "Password": DEFAULT_PASSWORD,
            "PasswordRuleID": 0,
            "WorkgroupID": WORKGROUP_ID,
            "Port": port,
            "UseOwnCredentials": True,
            "AutoManagementFlag": False
        }
        response = create_oracle_managed_account_api_call(managed_system_id, payload)
        managed_account_id = response.get("ManagedAccountID") if response else None

        if managed_account_id:
            ma_success(row_number, row, created=True, message=f"Oracle managed account oluşturuldu: {username}")
            return managed_account_id

        ma_error(row_number, row, -423, "Oracle create API boş döndü.", "OracleManagedAccount")
        return None

    except Exception as e:
        ma_error(row_number, row, -499, f"Oracle managed account exception: {str(e)}", "OracleManagedAccount")
        return None
