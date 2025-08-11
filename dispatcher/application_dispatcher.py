# dispatcher/application_dispatcher.py

from utils.logger import log_message
from handlers.application.assign_application import assign_applications_to_managed_account
from utils.report import app_init, app_success  # ✅

def dispatch_application_assignment(row: dict, managed_account_id: int, cache):
    application_string = row.get("application")
    row_number = row.get("Satır No", row.get("PamEnvanterSatır", -1))

    # SR/MA/MS’de olduğu gibi: önce default kolonları set et
    app_init(row)

    # Boş/uygunsuz değerlerde erken çıkış ama kolonlar ✓ kalsın
    if not application_string or str(application_string).strip().lower() in ("", "nan", "none"):
        app_success(row_number, row, unassigned_exists=False,
                    message=f"Application alanı boş/uygunsuz; atama yapılmayacak (AccountID:{managed_account_id}).")
        return

    log_message(f"🚀 Application atama başlatıldı. (AccountID: {managed_account_id})")
    # handler sadece iş mantığını yapacak; raporlama oradan yapılacak
    assign_applications_to_managed_account(row, managed_account_id, application_string, cache)
