# dispatcher/managed_account_dispatcher.py

from handlers.managed_account.ad_managed_account import create_ad_managed_account
from handlers.managed_account.oracle_managed_account import create_oracle_managed_account
from handlers.managed_account.mssql_managed_account import create_mssql_managed_account
from utils.logger import log_error, log_message
from typing import Optional
def dispatch_managed_account_create(row: dict, cache) -> Optional[int]:
    """
    Managed account dispatch kontrolü:
    - type == 'domain' ve username 'pam' ile başlıyorsa → AD
    - type == 'oracle' → Oracle
    - type == 'mssql' → MSSQL

    Return: Oluşan veya var olan ManagedAccountID (yoksa None)
    """
    try:
        row_type = row.get("type", "").lower()
        username = (row.get("username") or "").lower()
        row_number = row.get("PamEnvanterSatır", -1)

        if row_type == "domain" and username.startswith("pam"):
            return create_ad_managed_account(row, cache)

        elif row_type == "oracle":
            return create_oracle_managed_account(row, cache)

        elif row_type == "mssql":
            return create_mssql_managed_account(row, cache)

        else:
            log_message(f"[Row {row_number}] ℹ️ Atlandı: Şu an için desteklenmeyen managed account tipi. type='{row_type}', username='{username}'")
            return None

    except Exception as e:
        log_error(row.get("PamEnvanterSatır", -1), f"Dispatcher hata: {str(e)}", error_type="ManagedAccountDispatcher")
        return None
