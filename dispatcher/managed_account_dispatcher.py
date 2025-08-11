# dispatcher/managed_account_dispatcher.py

from typing import Optional
from handlers.managed_account.ad_managed_account import create_ad_managed_account
from handlers.managed_account.oracle_managed_account import create_oracle_managed_account
from handlers.managed_account.mssql_managed_account import create_mssql_managed_account
from utils.report import ma_init, ma_success, ma_error
from utils.logger import log_message

def dispatch_managed_account_create(row: dict, cache) -> Optional[int]:
    """
    Kurallar:
    - type == 'domain' ve username 'pam' ile başlıyorsa → AD
    - type == 'oracle' → Oracle (username 'pam' ile başlamıyorsa atla)
    - type == 'mssql' → MSSQL
    """
    ma_init(row)

    row_type = (row.get("type") or "").lower()
    username = (row.get("username") or "")
    u_l = username.lower()
    row_number = row.get("PamEnvanterSatır", -1)

    # Görsel/rapor kolonlarını tek yerden set etmeyelim: handler’lar MA - Tür / Kullanılan Account / AutoChange vb. set ediyor.
    try:
        if row_type == "domain" and u_l.startswith("pam"):
            acc_id = create_ad_managed_account(row, cache)
            if acc_id:
                ma_success(row_number, row, created=True, message=f"AD managed account oluşturuldu: {username}")
            else:
                # handler zaten ma_error basmış olabilir; ID gelmediği için garantiye al
                ma_error(row_number, row, -101, "AD managed account oluşturulamadı (ID yok).", "Dispatcher")
            return acc_id

        elif row_type == "oracle":
            if not u_l.startswith("pam"):
                # Politika gereği atla (hata değil bilgi)
                row["MA - Tür"] = "Oracle"
                row["MA - Kullanılan Account"] = username
                row["MA - AutoChange Durumu"] = "Kapalı"
                row["MA - Linkleme Durumu"] = "-"
                log_message(f"[Row {row_number}] ℹ️ Oracle atlandı: 'pam' ile başlamayan kullanıcı → {username}")
                # Genel durum ✓ kalsın (isteğe göre ℹ️ da yapılabilir)
                return None

            acc_id = create_oracle_managed_account(row, cache)
            if acc_id:
                ma_success(row_number, row, created=True, message=f"Oracle managed account oluşturuldu: {username}")
            else:
                ma_error(row_number, row, -102, "Oracle managed account oluşturulamadı (ID yok).", "Dispatcher")
            return acc_id

        elif row_type == "mssql":
            acc_id = create_mssql_managed_account(row, cache)
            if acc_id:
                ma_success(row_number, row, created=True, message=f"MSSQL managed account oluşturuldu: {username}")
            else:
                ma_error(row_number, row, -103, "MSSQL managed account oluşturulamadı (ID yok).", "Dispatcher")
            return acc_id

        else:
            # Desteklenmeyen tip → bilgi; istersen ❌ yapabiliriz.
            log_message(f"[Row {row_number}] ℹ️ Atlandı: Desteklenmeyen managed account tipi. type='{row_type}', username='{username}'")
            row.setdefault("MA - Tür", row_type.upper())
            row.setdefault("MA - Kullanılan Account", username)
            row.setdefault("MA - AutoChange Durumu", "-")
            row.setdefault("MA - Linkleme Durumu", "-")
            return None

    except Exception as e:
        ma_error(row_number, row, -199, f"Dispatcher exception: {str(e)}", "ManagedAccountDispatcher")
        return None
