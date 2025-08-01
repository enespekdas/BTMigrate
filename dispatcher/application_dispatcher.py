from utils.logger import log_message
from handlers.application.assign_application import assign_applications_to_managed_account


def dispatch_application_assignment(row: dict, managed_account_id: int, cache):
    application_string = row.get("application")

    if not application_string:
        log_message(f"ℹ️ Application sütunu boş, atama yapılmayacak. (AccountID: {managed_account_id})")
        return

    log_message(f"🚀 Application atama başlatıldı. (AccountID: {managed_account_id})")
    assign_applications_to_managed_account(managed_account_id, application_string, cache)
