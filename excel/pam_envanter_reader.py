import pandas as pd
from config.settings import PAM_ENVANTER_FILE_PATH
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
