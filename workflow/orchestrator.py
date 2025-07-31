from excel.pam_envanter_reader import read_pam_envanter
from excel.os_envanter_reader import lookup_machine
from dispatcher.managed_system_dispatcher import dispatch_managed_system
from utils.logger import log_message_row, log_error_row, log_message  # ✅ burada düzeltildi
from core.result_writer import write_result_row, write_unmatched_system
from utils.string_utils import clean_remote
from api.managed_system import get_all_managed_systems
from api.functional_account import get_all_functional_accounts

def process_all_pam_rows():
    get_all_managed_systems()  # Cache'i en başta bir kere yükle
    log_message("[INIT] Functional Account listesi yükleniyor ve cache'e yazılıyor.")

    get_all_functional_accounts()

    pam_rows = read_pam_envanter()
    if not pam_rows:
        print("PamEnvanter boş ya da okunamadı.")
        return

    for i, row in enumerate(pam_rows, start=1):
        log_message_row(i, "📌 ManagedSystem işlemi başlatıldı.")
        step_results = {}

        try:
            process_single_row(i, row, step_results)
            write_result_row(i, "✅", step_results)
        except Exception as e:
            log_error_row(i, -100, str(e), error_type="Orchestrator")
            write_result_row(i, "⛔", step_results)

def process_single_row(row_number, row, step_results):
    remote_raw = row.get("remoteMachines", "")
    remote_list = str(remote_raw).split(";") if remote_raw and str(remote_raw).lower() != "nan" else []
    os_found = False
    account = row.get("userName", "UNKNOWN")
    db_info = row.get("database", "")

    if remote_list:
        for remote in remote_list:
            original = remote.strip()
            if not original:
                continue

            cleaned_remote = clean_remote(original)
            if not cleaned_remote:
                continue

            os_info = lookup_machine(cleaned_remote)

            if os_info:
                os_found = True
                platform = os_info.get("OS", "Bilinmiyor")
                domain = os_info.get("Domain", "Bilinmiyor")
                log_message_row(
                    row_number,
                    f"{original} → CLEAN={cleaned_remote} | MATCH=✔ OS={platform}, Domain={domain}"
                )
                dispatch_managed_system(row_number, row, os_info, step_results)
            else:
                log_message_row(
                    row_number,
                    f"{original} → CLEAN={cleaned_remote} | MATCH=✖ Not found in OsEnvanter"
                )
                log_error_row(
                    row_number, -200,
                    f"OsEnvanter'de eşleşme bulunamadı: {cleaned_remote}",
                    "Lookup"
                )
                write_unmatched_system(row_number, account, original, cleaned_remote, "OsEnvanter'de eşleşme bulunamadı")

    elif db_info and str(db_info).strip().lower() != "nan":
        log_message_row(row_number, "💾 Bu kayıt bir veritabanı sistemine ait. (Örn: Oracle, MSSQL)")
        dispatch_managed_system(row_number, row, None, step_results)

    else:
        msg = "Yönetilmeyen sistem: Windows/Linux/Oracle/MSSQL platformları ile eşleşme sağlanamadı."
        log_error_row(row_number, -201, msg, "Lookup")
        write_unmatched_system(row_number, account, "YOK", "YOK", msg)
