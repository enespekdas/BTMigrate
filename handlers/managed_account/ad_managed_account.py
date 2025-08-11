# handlers/managed_account/ad_managed_account.py

from typing import Optional
from utils.universal_cache import UniversalCache
from config.settings import DEFAULT_PASSWORD, WORKGROUP_ID
from api.managed_account import (
    get_managed_accounts_by_system_id,
    create_ad_managed_account_api_call
)
from handlers.managed_account.ad_account_link_to_managed_system import (
    link_ad_account_to_managed_system
)
from utils.report import ma_success, ma_error, ma_set_link_status

def create_ad_managed_account(row: dict, cache: UniversalCache) -> Optional[int]:
    row_number = row.get("PamEnvanterSatır", -1)
    domain = (row.get("domain") or "").lower()
    username = row.get("username") or ""
    managed_account_id = None

    try:
        all_managed_systems = cache.get_all_by_key("ManagedSystem")

        domain_controller = next(
            (
                s for s in all_managed_systems
                if s.get("EntityTypeID") == 3 and (
                    (s.get("DnsName") or "").lower().endswith(domain)
                    or (s.get("HostName") or "").lower().endswith(domain)
                )
            ),
            None
        )

        # Ortak kolonlar
        row["MA - Tür"] = "AD"
        row["MA - Kullanılan Account"] = username
        row["MA - AutoChange Durumu"] = "Kapalı"

        if not domain_controller:
            ma_error(row_number, row, -300, f"Domain controller bulunamadı. Domain: {domain}", "ADManagedAccount")
            return None

        domain_system_id = domain_controller.get("ManagedSystemID")
        if not domain_system_id:
            ma_error(row_number, row, -301, f"Domain controller ManagedSystemID None. record={domain_controller}", "ADManagedAccount")
            return None

        existing_accounts = get_managed_accounts_by_system_id(domain_system_id)
        matched_account = next(
            (acc for acc in existing_accounts if (acc.get("AccountName") or "").lower() == username.lower()),
            None
        )

        if matched_account:
            managed_account_id = matched_account.get("ManagedAccountID")
            ma_success(row_number, row, already=True, message=f"AD managed account zaten var: {username}")
        else:
            payload = {
                "DomainName": domain,
                "AccountName": username,
                "DistinguishedName": "None",
                "PasswordRuleID": 0,
                "Password": DEFAULT_PASSWORD,
                "WorkgroupID": WORKGROUP_ID,
                "ObjectID": "None",
                "UserPrincipalName": username,
                "SAMAccountName": username,
                "AutoManagementFlag": False
            }
            response = create_ad_managed_account_api_call(domain_system_id, payload)
            managed_account_id = response.get("ManagedAccountID") if response else None
            if managed_account_id:
                ma_success(row_number, row, created=True, message=f"AD managed account oluşturuldu: {username}")
            else:
                ma_error(row_number, row, -302, "AD create API boş döndü.", "ADManagedAccount")
                return None

        # 🔗 Linkleme (başarısızlık hata detayı olarak eklenir ama MA genel durumu bozulmaz)
        try:
            link_ad_account_to_managed_system(row, managed_account_id, cache)
            # link handler kendi içinde ma_set_link_status çağıracak
        except Exception as link_error:
            ma_set_link_status(row, False, f"Linkleme exception: {str(link_error)}")

        return managed_account_id

    except Exception as e:
        ma_error(row_number, row, -399, f"AD managed account exception: {str(e)}", "ADManagedAccount")
        return None
