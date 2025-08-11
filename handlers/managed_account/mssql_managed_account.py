# handlers/managed_account/mssql_managed_account.py

from typing import Optional
from utils.universal_cache import UniversalCache
from config.settings import DEFAULT_PASSWORD, WORKGROUP_ID
from api.managed_account import (
    get_managed_accounts_by_system_id,
    create_ad_managed_account_api_call,   # ✅ AD hesabı create edeceğiz
)
from handlers.managed_account.ad_account_link_to_managed_system import (
    link_ad_account_to_managed_system,    # ✅ Aynı link fonksiyonunu kullanıyoruz
)
from utils.report import ma_success, ma_error, ma_set_link_status


def create_mssql_managed_account(row: dict, cache: UniversalCache) -> Optional[int]:
    """
    MSSQL için kullanılacak hesap mantığı:
      1) Domain controller (EntityTypeID == 3) üzerinde AD managed account var mı kontrol et
      2) Yoksa AD managed account'ı DC üzerinde oluştur
      3) Oluşan / mevcut hesabı hedef MSSQL managed system'e linkle
    """
    row_number = row.get("PamEnvanterSatır", -1)
    domain = (row.get("domain") or "").lower()
    username = (row.get("username") or "").strip()
    ip_address = (row.get("ip address") or "").strip()

    try:
        # Ortak rapor kolonları
        row["MA - Tür"] = "AD"  # Hesap AD üzerinde tutuluyor (MSSQL için kullanılacak)
        row["MA - Kullanılan Account"] = username
        row["MA - AutoChange Durumu"] = "Kapalı"
        row["MA - Linkleme Durumu"] = "-"  # Link aşamasında set edilecek

        if not domain:
            ma_error(row_number, row, -420, "Domain bilgisi boş.", "MSSQLManagedAccount")
            return None
        if not username:
            ma_error(row_number, row, -421, "Username bilgisi boş.", "MSSQLManagedAccount")
            return None
        if not ip_address:
            ma_error(row_number, row, -422, "IP address bilgisi boş.", "MSSQLManagedAccount")
            return None

        # 1) Cache’ten domain controller’ı bul
        all_managed_systems = cache.get_all_by_key("ManagedSystem") or []
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
        if not domain_controller:
            ma_error(row_number, row, -423, f"Domain controller bulunamadı. Domain: {domain}", "MSSQLManagedAccount")
            return None

        domain_system_id = domain_controller.get("ManagedSystemID")
        if not domain_system_id:
            ma_error(row_number, row, -424, f"Domain controller ManagedSystemID None. record={domain_controller}", "MSSQLManagedAccount")
            return None

        # 2) DC üzerinde ilgili AD hesabı var mı?
        existing_accounts = get_managed_accounts_by_system_id(domain_system_id)
        matched_account = next(
            (acc for acc in existing_accounts if (acc.get("AccountName") or "").lower() == username.lower()),
            None
        )

        if matched_account:
            managed_account_id = matched_account.get("ManagedAccountID")
            ma_success(row_number, row, already=True, message=f"AD managed account zaten var: {username}")
        else:
            # 2b) Yoksa DC üzerinde AD managed account oluştur
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
                ma_error(row_number, row, -425, "AD create API boş döndü.", "MSSQLManagedAccount")
                return None

        # 3) Hedef MSSQL managed system’i IP’den bul
        mssql_targets = [s for s in all_managed_systems if (s.get("IPAddress") or "").strip() == ip_address]
        if len(mssql_targets) == 0:
            ma_error(row_number, row, -426, f"IP ile eşleşen MSSQL managed system bulunamadı. IP: {ip_address}", "MSSQLManagedAccount")
            return None
        if len(mssql_targets) > 1:
            ma_error(row_number, row, -427, f"Aynı IP ile birden fazla MSSQL managed system bulundu. IP: {ip_address}", "MSSQLManagedAccount")
            return None

        # 4) Link: AD hesabını MSSQL system’e bağla (AD’de yaptığımız fonksiyonu tekrar kullanıyoruz)
        try:
            link_ad_account_to_managed_system(row, managed_account_id, cache)
            # link handler kendi içinde ma_set_link_status çağırıyorsa tekrar yazmaya gerek yok,
            # ama garanti olsun diye aşağıya set edelim (override etmez).
            ma_set_link_status(row, True, "Linkleme başarılı")
        except Exception as link_error:
            ma_set_link_status(row, False, f"Linkleme exception: {str(link_error)}")

        return managed_account_id

    except Exception as e:
        ma_error(row_number, row, -499, f"MSSQL managed account exception: {str(e)}", "MSSQLManagedAccount")
        return None
