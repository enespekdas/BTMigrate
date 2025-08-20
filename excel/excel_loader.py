import pandas as pd
from config.settings import (
    PAM_ENVANTER_FILE_PATH,
    OS_ENVANTER_FILE_PATH,
    SAFE_USER_FILE_PATH,
    BTMIGRATE_WORK_FILE_PATH,
    MSSQL_ENVANTER_FILE_PATH,  # ✅
)
from utils.logger import log_message, log_error

def read_pam_envanter():
    try:
        df = pd.read_excel(PAM_ENVANTER_FILE_PATH)
        log_message(f"📘 PamEnvanter yüklendi: {PAM_ENVANTER_FILE_PATH} (Toplam {len(df)} satır)")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        log_error(-2, f"PamEnvanter bulunamadı: {PAM_ENVANTER_FILE_PATH}", error_type="Excel")
        return []
    except Exception as e:
        log_error(-3, f"PamEnvanter okuma hatası: {str(e)}", error_type="Excel")
        return []

def read_os_envanter():
    try:
        df = pd.read_excel(OS_ENVANTER_FILE_PATH)
        log_message(f"📘 OsEnvanter yüklendi: {OS_ENVANTER_FILE_PATH} (Toplam {len(df)} satır)")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        log_error(-4, f"OsEnvanter bulunamadı: {OS_ENVANTER_FILE_PATH}", error_type="Excel")
        return []
    except Exception as e:
        log_error(-5, f"OsEnvanter okuma hatası: {str(e)}", error_type="Excel")
        return []

def read_safe_user_list():
    try:
        df = pd.read_excel(SAFE_USER_FILE_PATH)
        log_message(f"📘 PamSafeUser yüklendi: {SAFE_USER_FILE_PATH} (Toplam {len(df)} satır)")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        log_error(-6, f"PamSafeUser bulunamadı: {SAFE_USER_FILE_PATH}", error_type="Excel")
        return []
    except Exception as e:
        log_error(-7, f"PamSafeUser okuma hatası: {str(e)}", error_type="Excel")
        return []

def read_btmigrate_workbook():
    try:
        df = pd.read_excel(BTMIGRATE_WORK_FILE_PATH)
        return df.to_dict(orient="records")
    except Exception as e:
        log_error(-20, f"btmigrate_work.xlsx okunamadı: {str(e)}", error_type="ExcelRead")
        return []

# ✅ Yeni: MsSQL envanter okuyucu (Sadece okur, handler içinde lineer aranır)
def read_mssql_envanter():
    try:
        df = pd.read_excel(MSSQL_ENVANTER_FILE_PATH)
        log_message(f"📘 MsSQLEnvanter yüklendi: {MSSQL_ENVANTER_FILE_PATH} (Toplam {len(df)} satır)")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        log_error(-8, f"MsSQLEnvanter bulunamadı: {MSSQL_ENVANTER_FILE_PATH}", error_type="Excel")
        return []
    except Exception as e:
        log_error(-9, f"MsSQLEnvanter okuma hatası: {str(e)}", error_type="Excel")
        return []
