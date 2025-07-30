from excel.reader import df
from core.logger import (
    log_message,
    log_error,
    log_debug,
    log_message_row,
    log_error_row
)
from core.result_writer import write_result_row
from services.managed_system_service import process_managed_system
from api.managed_system import get_all_managed_systems  # ✅ cache’i baştan yükle

def _process_rows():
    if df is None:
        log_error(-4, "DataFrame boş geldi, işlenemiyor", error_type="Processor")
        return

    # ✅ Tüm liste baştan cache'e alınır
    get_all_managed_systems()

    for index, row in df.iterrows():
        step_results = {}
        row_number = index + 1

        try:
            log_message_row(row_number, "🔄 Satır işleniyor")
            log_debug(row.to_string())

            # ✅ 1. Aşama: Managed System işle
            ms_status, ms_msg = process_managed_system(row)
            step_results["ManagedSystem"] = (ms_status, ms_msg)
            log_message_row(row_number, f"[ManagedSystem] {ms_status} | {ms_msg}")

            genel_durum = "Başarılı" if all(v[0] == "Başarılı" for v in step_results.values()) else "Atlandı"

        except Exception as e:
            step_results["ManagedSystem"] = ("Hatalı", str(e))
            log_error_row(row_number, row_number, f"Satır işleme hatası: {str(e)}", error_type="Processor")
            genel_durum = "Hatalı"

        write_result_row(row_number, genel_durum, step_results)

# Self-executing
_process_rows()
