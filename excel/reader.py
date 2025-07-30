import pandas as pd
from config.settings import EXCEL_FILE_PATH, SHOW_EXCEL_SAMPLE_ROWS
from core.logger import log_message, log_error

df = None  # Global olarak dışarıya açılacak

def _read_excel():
    global df
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        log_message(f"📊 Excel dosyası okundu: {EXCEL_FILE_PATH} (Toplam satır: {len(df)})")
        if SHOW_EXCEL_SAMPLE_ROWS:
            log_message("📄 İlk 3 satır:\n" + df.head(3).to_string())

    except FileNotFoundError:
        log_error(-2, f"Excel dosyası bulunamadı: {EXCEL_FILE_PATH}", error_type="Excel")
    except Exception as e:
        log_error(-3, f"Excel okuma hatası: {str(e)}", error_type="Excel")

# Self-executing
_read_excel()
