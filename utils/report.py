# utils/report.py
from __future__ import annotations
from typing import Optional, Dict
from utils.logger import log_message, log_error

ERROR_COL = "Hata Detayı"

def _append_error(row: Dict, msg: str):
    if not msg:
        return
    prev = (row.get(ERROR_COL) or "").strip()
    row[ERROR_COL] = (prev + ("\n" if prev else "") + msg)

# ---- MS ----
MS_COLS = {"genel":"MS - Genel Durum","exists":"MS - Zaten Var mı?","created":"MS - Oluşturuldu mu?"}
def ms_init(row: Dict):
    row.setdefault(MS_COLS["genel"], "✅"); row.setdefault(MS_COLS["exists"], "Hayır"); row.setdefault(MS_COLS["created"], "Hayır"); row.setdefault(ERROR_COL, "")
def ms_success(n:int,row:Dict,*,already=False,created=False,message:Optional[str]=None):
    row[MS_COLS["genel"]]="✅"; 
    if already: row[MS_COLS["exists"]]="Evet"
    if created: row[MS_COLS["created"]]="Evet"
    if message: log_message(f"Row {n}: {message}")
def ms_error(n:int,row:Dict,code:int,message:str,error_type:str):
    row[MS_COLS["genel"]]="❌"; row[MS_COLS["created"]]="Hayır"
    _append_error(row,f"[MS:{error_type}] {message}")
    log_error(n,f"[{error_type}] Kod: {code} Message: {message}",error_type=error_type)

# ---- MA ----
MA_COLS = {"genel":"MA - Genel Durum","exists":"MA - Zaten Var mı?","created":"MA - Oluşturuldu mu?"}
def ma_init(row: Dict):
    row.setdefault(MA_COLS["genel"], "✅"); row.setdefault(MA_COLS["exists"], "Hayır"); row.setdefault(MA_COLS["created"], "Hayır"); row.setdefault(ERROR_COL, "")
def ma_success(n:int,row:Dict,*,already=False,created=False,message:Optional[str]=None):
    row[MA_COLS["genel"]]="✅"; 
    if already: row[MA_COLS["exists"]]="Evet"
    if created: row[MA_COLS["created"]]="Evet"
    if message: log_message(f"Row {n}: {message}")
def ma_error(n:int,row:Dict,code:int,message:str,error_type:str):
    row[MA_COLS["genel"]]="❌"; row[MA_COLS["created"]]="Hayır"
    _append_error(row,f"[MA:{error_type}] {message}")
    log_error(n,f"[{error_type}] Kod: {code} Message: {message}",error_type=error_type)
def ma_set_link_status(row: Dict, ok: bool, detail: Optional[str] = None):
    """
    Managed Account linkleme kolonunu tek yerden yönetir.
    ok=True  -> 'MA - Linkleme Durumu' = '✅'
    ok=False -> 'MA - Linkleme Durumu' = '❌' ve (varsa) Hata Detayı'na kısa not ekler.
    """
    row["MA - Linkleme Durumu"] = "✅" if ok else "❌"
    if not ok and detail:
        _append_error(row, f"[MA:Link] {detail}")
# ---- SR ----
SR_COLS = {"genel":"SR - Genel Durum","exists":"SR - Zaten Var mı?","created":"SR - Oluşturuldu mu?","assigned":"SR - Account Ataması Yapıldı mı?"}
def sr_init(row: Dict):
    row.setdefault(SR_COLS["genel"],"✅"); row.setdefault(SR_COLS["exists"],"Hayır"); row.setdefault(SR_COLS["created"],"Hayır"); row.setdefault(SR_COLS["assigned"],"❌"); row.setdefault(ERROR_COL,"")
def sr_success(n:int,row:Dict,*,already=False,created=False,account_assigned=False,message:Optional[str]=None):
    row[SR_COLS["genel"]]="✅"
    if already: row[SR_COLS["exists"]]="Evet"
    if created: row[SR_COLS["created"]]="Evet"
    if account_assigned: row[SR_COLS["assigned"]]="✅"
    if message: log_message(f"Row {n}: {message}")
def sr_error(n:int,row:Dict,code:int,message:str,error_type:str):
    row[SR_COLS["genel"]]="❌"; row[SR_COLS["assigned"]]="❌"
    _append_error(row,f"[SR:{error_type}] {message}")
    log_error(n,f"[{error_type}] Kod: {code} Message: {message}",error_type=error_type)

# ---- APP ----
APP_COLS = {"genel":"App - Genel Durum","unassigned":"App - Atanamayan Uygulama Var mı?"}
def app_init(row: Dict):
    row.setdefault(APP_COLS["genel"],"✅"); row.setdefault(APP_COLS["unassigned"],"Hayır"); row.setdefault(ERROR_COL,"")
def app_success(n:int,row:Dict,*,unassigned_exists=False,message:Optional[str]=None):
    row[APP_COLS["genel"]]="✅"; row[APP_COLS["unassigned"]]="Evet" if unassigned_exists else "Hayır"
    if message: log_message(f"Row {n}: {message}")
def app_error(n:int,row:Dict,code:int,message:str,error_type:str,*,unassigned_exists:bool=True):
    row[APP_COLS["genel"]]="❌"; row[APP_COLS["unassigned"]]="Evet" if unassigned_exists else row.get(APP_COLS["unassigned"],"Hayır")
    _append_error(row,f"[APP:{error_type}] {message}")
    log_error(n,f"[{error_type}] Kod: {code} Message: {message}",error_type=error_type)

# ---- UG ----
UG_COLS = {"genel":"UG - Genel Durum","exists":"UG - Zaten Var mı?","created":"UG - Oluşturuldu mu?","sr_assigned":"UG - SmartRule Ataması Yapıldı mı?","role_done":"UG - Role Ataması Yapıldı mı?"}
def ug_init(row: Dict):
    row.setdefault(UG_COLS["genel"],"✅"); row.setdefault(UG_COLS["exists"],"Hayır"); row.setdefault(UG_COLS["created"],"Hayır"); row.setdefault(UG_COLS["sr_assigned"],"Hayır"); row.setdefault(UG_COLS["role_done"],"Hayır"); row.setdefault(ERROR_COL,"")
def ug_success(n:int,row:Dict,*,already=False,created=False,sr_assigned=False,role_assigned=False,message:Optional[str]=None):
    row[UG_COLS["genel"]]="✅"
    if already: row[UG_COLS["exists"]]="Evet"
    if created: row[UG_COLS["created"]]="Evet"
    if sr_assigned: row[UG_COLS["sr_assigned"]]="Evet"
    if role_assigned: row[UG_COLS["role_done"]]="Evet"
    if message: log_message(f"Row {n}: {message}")
def ug_error(n:int,row:Dict,code:int,message:str,error_type:str):
    row[UG_COLS["genel"]]="❌"
    row[UG_COLS["sr_assigned"]] = row.get(UG_COLS["sr_assigned"],"Hayır") or "Hayır"
    row[UG_COLS["role_done"]]  = row.get(UG_COLS["role_done"],"Hayır") or "Hayır"
    _append_error(row,f"[UG:{error_type}] {message}")
    log_error(n,f"[{error_type}] Kod: {code} Message: {message}",error_type=error_type)

# ---- USER ----
USER_COLS = {"genel":"User - Genel Durum","exists":"User - Zaten Var mı?","created":"User - Oluşturuldu mu?","added":"User - Gruba Eklendi mi?"}
def user_init(row: Dict):
    row.setdefault(USER_COLS["genel"],"✅"); row.setdefault(USER_COLS["exists"],"Hayır"); row.setdefault(USER_COLS["created"],"Hayır"); row.setdefault(USER_COLS["added"],"Hayır"); row.setdefault(ERROR_COL,"")
def user_success(n:int,row:Dict,*,created_any:bool,existed_all:bool,added_all:bool,message:Optional[str]=None):
    row[USER_COLS["genel"]]="✅"
    row[USER_COLS["created"]] = "Evet" if created_any else "Hayır"
    row[USER_COLS["exists"]]  = "Evet" if existed_all else "Hayır"
    row[USER_COLS["added"]]   = "Evet" if added_all else "Hayır"
    if message: log_message(f"Row {n}: {message}")
def user_error(n:int,row:Dict,code:int,message:str,error_type:str,*,created_any:Optional[bool]=None,existed_all:Optional[bool]=None,added_all:Optional[bool]=None):
    row[USER_COLS["genel"]]="❌"
    if created_any is not None: row[USER_COLS["created"]] = "Evet" if created_any else "Hayır"
    if existed_all is not None: row[USER_COLS["exists"]]  = "Evet" if existed_all else "Hayır"
    if added_all is not None:   row[USER_COLS["added"]]   = "Evet" if added_all else "Hayır"
    _append_error(row,f"[USER:{error_type}] {message}")
    log_error(n,f"[{error_type}] Kod: {code} Message: {message}",error_type=error_type)

# ---- Genel Durum ----
def finalize_overall(row: Dict):
    step_cols = [
        MS_COLS["genel"], MA_COLS["genel"],
        SR_COLS["genel"] if 'SR_COLS' in globals() else None,
        APP_COLS["genel"] if 'APP_COLS' in globals() else None,
        UG_COLS["genel"]  if 'UG_COLS'  in globals() else None,
        USER_COLS["genel"] if 'USER_COLS' in globals() else None,
    ]
    vals = [row.get(c) for c in step_cols if c and c in row]
    row["Genel Durum"] = "❌" if any(v == "❌" for v in vals) else "✅"
