# handlers/managed_account/ad_managed_account.py

from utils.logger import log_message, log_error, log_debug
from utils.universal_cache import UniversalCache
from config.settings import DEFAULT_PASSWORD, WORKGROUP_ID
from api.managed_account import (
    get_managed_accounts_by_system_id,
    create_ad_managed_account_api_call
)
from handlers.managed_account.ad_account_link_to_managed_system import (
    link_ad_account_to_managed_system
)

def create_ad_managed_account(row: dict, cache: UniversalCache) -> None:
    try:
        row_number = row.get("PamEnvanterSatır", -1)
        domain = (row.get("domain") or "").lower()
        username = row.get("username")

        log_debug(f"[Row {row_number}] 🔍 AD Managed Account işlemi başlatıldı. Domain: {domain}, Username: {username}")

        # 1️⃣ Domain controller managed system ID'sini bul
        all_managed_systems = cache.get_all_by_key("ManagedSystem")
        log_debug(f"[Row {row_number}] 💾 Cache'ten alınan managed systems: {len(all_managed_systems)} kayıt")

        domain_controller = next(
            (
                s for s in all_managed_systems
                if s.get("EntityTypeID") == 3
                and (
                    (s.get("DnsName") or "").lower().endswith(domain)
                    or (s.get("HostName") or "").lower().endswith(domain)
                )
            ),
            None
        )

        if not domain_controller:
            log_error(row_number, f"❌ Domain controller bulunamadı. Domain: {domain}", error_type="ADManagedAccount")
            return

        log_debug(f"[Row {row_number}] 🔍 Bulunan domain controller: {domain_controller}")

        domain_system_id = domain_controller.get("ManagedSystemID")
        if domain_system_id is None:
            log_error(
                row_number,
                f"❌ Domain controller ManagedSystemID None döndü. domain_controller: {domain_controller}",
                error_type="ADManagedAccount"
            )
            return

        # 2️⃣ Mevcut managed account var mı kontrol et
        existing_accounts = get_managed_accounts_by_system_id(domain_system_id)
        log_debug(f"[Row {row_number}] 🔄 Mevcut managed account sayısı: {len(existing_accounts)}")

        matched_account = next(
            (acc for acc in existing_accounts if (acc.get("AccountName") or "").lower() == username.lower()),
            None
        )

        if matched_account:
            managed_account_id = matched_account.get("ManagedAccountID")
            log_message(f"[Row {row_number}] ✅ AD managed account zaten var: {username}")
        else:
            # 3️⃣ Payload hazırla
            payload = {
                "DomainName": domain,
                "AccountName": username,
                "DistinguishedName": "None",
                "PasswordRuleID": 0,
                "Password": DEFAULT_PASSWORD,
                "WorkgroupID": WORKGROUP_ID,
                "ObjectID": "None",
                "UserPrincipalName": username,
                "SAMAccountName": username
            }

            log_debug(f"[Row {row_number}] 📦 Payload hazırlandı: {payload}")
            log_message(f"[Row {row_number}] 🚀 AD managed account oluşturuluyor: {username}")

            # 4️⃣ API çağrısı ve ManagedAccountID dönüşü
            response = create_ad_managed_account_api_call(domain_system_id, payload)
            managed_account_id = response.get("ManagedAccountID") if response else None

        # 5️⃣ Linkleme işlemi
        if managed_account_id:
            link_ad_account_to_managed_system(row, managed_account_id, cache)

    except Exception as e:
        log_error(row.get("PamEnvanterSatır", -1), f"💥 Hata (AD managed account): {str(e)}", error_type="ADManagedAccount")
