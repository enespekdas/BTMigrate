from handlers.managed_system.windows import handle_windows_managed_system
from handlers.managed_system.linux import handle_linux_managed_system
from api.managed_system import get_managed_system_by_ip
from utils.logger import log_message_row, log_error_row

def dispatch_managed_system(row_number, row, os_info, step_results):
    try:
        cleaned_ip = row.get("CleanedIP") or row.get("IP")
        ip_address = os_info.get("IPAddress") if os_info else cleaned_ip

        if ip_address:
            existing = get_managed_system_by_ip(ip_address)
            if existing:
                msg = f"⚠️ ManagedSystem zaten mevcut: {ip_address}"
                log_message_row(row_number, msg)
                step_results["ManagedSystem"] = ("🟡", msg)
                return

        if not os_info:
            msg = "Veritabanı sistemi (os_info yok) → Platform kontrolü atlandı."
            log_message_row(row_number, msg)
            step_results["ManagedSystem"] = ("ℹ️", msg)
            return

        platform = (os_info.get("OS") or "").strip().lower()
        if not platform:
            msg = "Platform bilgisi alınamadı. (Windows/Linux gibi)"
            log_error_row(row_number, -300, msg, "Dispatcher")
            step_results["ManagedSystem"] = ("⛔", msg)
            return

        log_message_row(row_number, f"🎯 Platform: {platform}")

        if "windows" in platform:
            success, message = handle_windows_managed_system(row_number, row, os_info, step_results, cleaned_ip)
        elif "linux" in platform:
            success, message = handle_linux_managed_system(row_number, row, os_info, step_results, cleaned_ip)
        else:
            msg = f"Platform henüz desteklenmiyor: {platform}"
            log_error_row(row_number, -301, msg, "Dispatcher")
            step_results["ManagedSystem"] = ("⛔", msg)
            return

        step_results["ManagedSystem"] = ("✅" if success else "⛔", message)

    except Exception as e:
        log_error_row(row_number, -302, f"Dispatcher hatası: {str(e)}", "Dispatcher")
        step_results["ManagedSystem"] = ("⛔", "Dispatcher içinde hata oluştu.")
