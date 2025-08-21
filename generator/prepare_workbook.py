import os
from openpyxl import Workbook
from typing import List
from excel.excel_loader import (
    read_pam_envanter,
    read_os_envanter,
    read_safe_user_list,
    read_mssql_envanter,   # ✅ sadece okuyoruz
)
from utils.logger import log_message, log_error
from row_processors.remote_machines_handler import process_remote_machines
from row_processors.mssql_machines_handler import process_mssql_machines

def is_empty(val: str) -> bool:
    val = (val or "").strip().lower()
    return val in ["", "nan", "none", "null", "-"]

def _append_rows(ws, rows: List[List]):
    for r in rows:
        ws.append(r)

# ✅ MsSQL item'larından host set'i çıkar (host/IP normalizasyonu)
def _extract_mssql_hosts_set(mssql_raw: str) -> set[str]:
    """
    MsSQL hücresindeki değerleri ';' ile parçalar ve sadece host kısmını alır.
    Destek: host, host:port, host\\instance, host\\instance:port
    Dönüş: lower-case host set
    """
    hosts = set()
    for item in (mssql_raw or "").split(";"):
        s = item.strip()
        if not s or s.lower() in ["nan", "none", "null", "-"]:
            continue
        # host\instance[:port] veya host[:port]
        if "\\" in s:
            host_part = s.split("\\", 1)[0]
        else:
            host_part = s
        # Güvenlik: host_part'ta port kaldıysa ayıkla
        if ":" in host_part:
            host_part = host_part.split(":", 1)[0]
        host = host_part.strip().lower()
        if host:
            hosts.add(host)
    return hosts

# ✅ Remote item MSSQL ile çakışıyor mu? (kısa/FQDN eşleştirme heuristiği)
def _remote_is_in_mssql(remote_item: str, mssql_hosts: set[str]) -> bool:
    r = (remote_item or "").strip().lower()
    if not r:
        return False
    if r in mssql_hosts:
        return True
    # "short vs fqdn" eşleştirme
    if "." not in r:
        # remote kısa, mssql fqdn olabilir
        for h in mssql_hosts:
            if h.startswith(r + "."):
                return True
    else:
        # remote fqdn, mssql kısa olabilir
        short = r.split(".", 1)[0]
        if short in mssql_hosts:
            return True
    return False

# 🆕 Domain'i boş olan valid satırlara PAM satırındaki address'i yaz
def _fill_missing_domain_with_address(valid_rows: List[List], fallback_domain: str) -> List[List]:
    """
    headers_main yapısı:
    [0] PamEnvanterSatır, [1] username, [2] ip address, [3] hostname,
    [4] application, [5] OS, [6] safe name, [7] members,
    [8] database, [9] port, [10] type, [11] domain
    """
    if is_empty(fallback_domain):
        return valid_rows

    DOMAIN_COL_IDX = 11
    out = []
    for row in valid_rows:
        if len(row) <= DOMAIN_COL_IDX:
            # Beklenen uzunlukta değilse olduğu gibi geçir
            out.append(row)
            continue

        current_domain = str(row[DOMAIN_COL_IDX] if row[DOMAIN_COL_IDX] is not None else "").strip()
        if is_empty(current_domain):
            row = list(row)  # defensif kopya
            row[DOMAIN_COL_IDX] = fallback_domain
        out.append(row)
    return out

def prepare_workbook():
    pam_data = read_pam_envanter()
    os_data = read_os_envanter()
    safe_user_data = read_safe_user_list()
    mssql_envanter_records = read_mssql_envanter()  # ✅ liste olarak

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
        username = str(row.get("UserName") or row.get("userName") or "").strip()
        safe_name = str(row.get("SafeName") or row.get("safeName") or "").strip()
        remote_raw = str(row.get("RemoteMachines") or row.get("remoteMachines") or "").strip()
        mssql_raw = str(row.get("MsSQL") or "").strip()

        # 🆕 Fallback domain olarak PAM satırındaki "address" alınır
        fallback_domain_from_address = str(row.get("address") or row.get("Address") or "").strip()

        if is_empty(username):
            reason = "Username alanı boş."
            log_error(-11, f"{reason} (row={i})", error_type="PrepareValidation")
            ws_ignored.append([i, "-", remote_raw or "-", "-", "-", reason, "-"])
            continue

        if is_empty(safe_name):
            reason = "SafeName alanı boş."
            log_error(-12, f"{reason} (row={i})", error_type="PrepareValidation")
            ws_ignored.append([i, username, remote_raw or "-", "-", "-", reason, "-"])
            continue

        valid_rows: List[List] = []
        ignored_rows: List[List] = []

        # ✅ MsSQL host set'ini çıkar (Remote ile çakışanları filtrelemek için)
        mssql_hosts = _extract_mssql_hosts_set(mssql_raw) if not is_empty(mssql_raw) else set()

        # ✅ RemoteMachines akışı — MSSQL'de olan hostları AYIKLA
        if not is_empty(remote_raw):
            remotes = [
                r.strip() for r in remote_raw.split(";")
                if r.strip().lower() not in ["", "nan", "none", "null", "-"]
            ]
            remotes_filtered = [
                r for r in remotes
                if not _remote_is_in_mssql(r, mssql_hosts)
            ]

            if remotes_filtered:
                try:
                    # Row'un kopyasında sadece RemoteMachines'i filtreleyip gönder
                    row_for_remote = dict(row)
                    row_for_remote["RemoteMachines"] = ";".join(remotes_filtered)
                    row_for_remote["remoteMachines"] = ";".join(remotes_filtered)

                    v_rows, i_rows = process_remote_machines(
                        index=i,
                        pam_row=row_for_remote,
                        os_envanter=os_data,
                        safe_user_list=safe_user_data
                    )
                    # 🆕 Domain boşsa address ile doldur
                    v_rows = _fill_missing_domain_with_address(v_rows, fallback_domain_from_address)

                    valid_rows += v_rows
                    ignored_rows += i_rows
                except Exception as e:
                    reason = f"remote_machines_handler hatası: {str(e)}"
                    log_error(-20, reason, error_type="RemoteMachineHandler")
                    ws_ignored.append([i, username, remote_raw or "-", "-", "-", reason, "-"])
            # else: tüm remotes MSSQL ile çakıştığı için remote handler'ı atla

        # MsSQL akışı (envanter sadece liste — handler içinde lineer arama yapacak)
        if not is_empty(mssql_raw):
            try:
                v_rows, i_rows = process_mssql_machines(
                    index=i,
                    pam_row=row,
                    os_envanter=os_data,
                    safe_user_list=safe_user_data,
                    mssql_envanter=mssql_envanter_records,  # ✅ listeyi geçir
                )
                # 🆕 Domain boşsa address ile doldur
                v_rows = _fill_missing_domain_with_address(v_rows, fallback_domain_from_address)

                valid_rows += v_rows
                ignored_rows += i_rows
            except Exception as e:
                reason = f"mssql_machines_handler hatası: {str(e)}"
                log_error(-30, reason, error_type="MsSQLHandler")
                ws_ignored.append([i, username, mssql_raw or "-", "-", "-", reason, "mssql"])

        if is_empty(remote_raw) and is_empty(mssql_raw):
            reason = "RemoteMachines ve MsSQL alanları boş."
            log_error(-13, f"{reason} (row={i})", error_type="PrepareValidation")
            ws_ignored.append([i, username, "-", "-", "-", reason, "-"])

        _append_rows(ws_main, valid_rows)
        _append_rows(ws_ignored, ignored_rows)

    output_path = os.path.join("data", "btmigrate_work.xlsx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    log_message(f"✅ Çalışma Excel'i oluşturuldu: {output_path}")
