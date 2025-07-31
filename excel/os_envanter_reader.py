import pandas as pd
from config.settings import OS_ENVANTER_FILE_PATH
from utils.logger import log_message, log_error

def read_os_envanter():
    try:
        df = pd.read_excel(OS_ENVANTER_FILE_PATH)
        log_message(f"📘 OsEnvanter yüklendi: {OS_ENVANTER_FILE_PATH} (Toplam {len(df)} satır)")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        log_error(-2, f"OsEnvanter bulunamadı: {OS_ENVANTER_FILE_PATH}", error_type="Excel")
    except Exception as e:
        log_error(-3, f"OsEnvanter okuma hatası: {str(e)}", error_type="Excel")
    return []

def lookup_machine(ip_or_hostname):
    os_rows = read_os_envanter()
    for row in os_rows:
        hostname = str(row.get("Hostname", "")).strip()
        ip = str(row.get("IP Address", "")).strip()
        os_name = str(row.get("OS", "")).strip()
        domain = str(row.get("Domain", "")).strip()

        if ip_or_hostname == ip or ip_or_hostname.lower() == hostname.lower():
            return {
                "HostName": hostname,
                "IPAddress": ip,
                "OS": os_name,
                "Domain": domain
            }

    return None
