import os
from openpyxl import Workbook
from excel.excel_loader import (
    read_pam_envanter,
    read_os_envanter,
    read_safe_user_list
)
from utils.logger import log_message, log_error
from row_processors.remote_machine_handler import process_remote_machine_row
from row_processors.oracle_handler import process_oracle_row  # ✅ Oracle handler eklendi

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
    headers_ignored = ["PamEnvanterSatır", "username", "remote", "reason"]

    ws_main.append(headers_main)
    ws_ignored.append(headers_ignored)

    for i, row in enumerate(pam_data, start=1):
        username = str(row.get("userName", "")).strip().lower()
        remote_raw = str(row.get("remoteMachines", "")).strip()
        platform_id = str(row.get("platformId", "")).strip().lower()

        valid_rows = []
        ignored_rows = []

        # ✅ 1. Oracle satırı mı?
        if platform_id.startswith("oracle"):
            valid_rows, ignored_rows = process_oracle_row(i, row, safe_user_data)

        # ✅ 2. Remote machine'li PAM satırı mı?
        elif username.startswith("pam") and remote_raw and remote_raw.lower() not in ["nan", "none", "null"]:
            valid_rows, ignored_rows = process_remote_machine_row(i, row, os_data, safe_user_data)

        # ⛔️ 3. Diğerleri atlanır
        else:
            continue

        for r in valid_rows:
            ws_main.append(r)

        for ir in ignored_rows:
            ws_ignored.append(ir)

    output_path = os.path.join("data", "btmigrate_work.xlsx")
    wb.save(output_path)
    log_message(f"✅ Çalışma Excel'i oluşturuldu: {output_path}")
