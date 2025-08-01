# dispatcher/managed_account_dispatcher.py

from handlers.managed_account.ad_managed_account import create_ad_managed_account
from utils.logger import log_error, log_message

def dispatch_managed_account_create(row: dict, cache) -> None:
    """
    AD managed account kontrolü:
    - type == 'domain'
    - ve username 'pam' ile başlıyorsa
    """
    try:
        row_type = row.get("type", "").lower()
        username = (row.get("username") or "").lower()
        row_number = row.get("PamEnvanterSatır", -1)

        is_ad_account = row_type == "domain" and username.startswith("pam")

        if is_ad_account:
            create_ad_managed_account(row, cache)
        else:
            log_message(
                f"[Row {row_number}] ℹ️ Atlandı: Şu an için desteklenmeyen managed account tipi. type='{row_type}', username='{username}'"
            )

    except Exception as e:
        log_error(row.get("PamEnvanterSatır", -1), f"Dispatcher hata: {str(e)}", error_type="ManagedAccountDispatcher")
