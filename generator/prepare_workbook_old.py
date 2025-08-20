import os
from openpyxl import Workbook
from excel.excel_loader import (
    read_pam_envanter,
    read_os_envanter,
    read_safe_user_list
)
from utils.logger import log_message, log_error
from row_processors.remote_machine_handler import process_remote_machine_row
from row_processors.oracle_handler import process_oracle_row


def is_empty(val: str) -> bool:
    val = (val or "").strip().lower()
    return val in ["", "nan", "none", "null"]


def prepare_workbook():
    pam_data = read_pam_envanter()
    os_data = read_os_envanter()
    safe_user_data = read_safe_user_list()

    if not pam_data:
        log_error(-10, "PamEnvanter boş geldi, işlem iptal.", error_type="Prepare")
        return

    wb = Workbook()
    ws_main = wb.active
    ws_main.title = "btmigrate_work"

    ws_ignored = wb.create_sheet(title="ignored_rows")

    headers_main = [
        "PamEnvanterSatır", "username", "ip address", "hostname",
        "application", "OS", "safe name", "members",
        "database", "port", "type", "domain"
    ]
    headers_ignored = [
        "PamEnvanterSatır", "username", "remote", "hostname",
        "domain", "reason", "os_type"
    ]

    ws_main.append(headers_main)
    ws_ignored.append(headers_ignored)

    for i, row in enumerate(pam_data, start=1):
        valid_rows = []
        ignored_rows = []

        username = str(row.get("userName", "")).strip()
        platform_id = str(row.get("platformId", "")).strip().lower()
        remote_raw = str(row.get("remoteMachines", "")).strip()
        database = str(row.get("database", "")).strip()

        # ⛔️ Username geçersizse → ignore
        if is_empty(username):
            reason = "Username alanı boş olduğundan dolayı ignore edilmiştir."
            log_error(i, reason, error_type="PrepareValidation")
            ignored_rows.append([
                i,
                "-",
                remote_raw or "-",
                "-", "-", reason, "-"
            ])

        # ✅ 1. Oracle satırı mı?
        elif platform_id.startswith("oracle") and not is_empty(database):
            try:
                valid_rows, ignored_rows = process_oracle_row(i, row, safe_user_data)
            except Exception as e:
                reason = f"process_oracle_row hatası: {str(e)}"
                log_error(i, reason, error_type="OracleHandler")
                ignored_rows.append([
                    i, username, remote_raw or "-", "-", "-", reason, "oracle"
                ])

        # ✅ 2. RemoteMachines içeren PAM satırı mı?
        elif username.lower().startswith("pam") and not is_empty(remote_raw):
            try:
                valid_rows, ignored_rows = process_remote_machine_row(i, row, os_data, safe_user_data)
            except Exception as e:
                reason = f"process_remote_machine_row hatası: {str(e)}"
                log_error(i, reason, error_type="RemoteMachineHandler")
                ignored_rows.append([
                    i, username, remote_raw or "-", "-", "-", reason, "-"
                ])

        # ⛔️ 3. Diğerleri şimdilik işlenmiyor → ignore sheet'e yaz!
        else:
            reason = "Satır işleme alınmadı: Domain Managed Account, Managed System, MSSQL ve Oracle filtre kurallarına uygun değil."
            log_error(i, reason, error_type="PrepareValidation")
            ignored_rows.append([
                i,
                username or "-",
                remote_raw or "-",
                "-", "-", reason, "-"
            ])

        # ✅ Geçerli satırları ve ignoredları yaz
        for valid in valid_rows:
            ws_main.append(valid)

        for ignored in ignored_rows:
            ws_ignored.append(ignored)

    output_path = os.path.join("data", "btmigrate_work.xlsx")
    wb.save(output_path)
    log_message(f"✅ Çalışma Excel'i oluşturuldu: {output_path}")
