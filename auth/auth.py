import requests
from config.settings import API_BASE_URL, AUTH_HEADERS, AUTH_BODY, VERIFY_SSL
from core.logger import log_message, log_error
from core.env import set_env_variable
from core.exceptions import AuthenticationError

def _authenticate():
    try:
        url = f"{API_BASE_URL}/Auth/SignAppin"
        response = requests.post(url, headers=AUTH_HEADERS, json=AUTH_BODY, verify=VERIFY_SSL)
        response.raise_for_status()

        session_id = response.cookies.get("ASP.NET_SessionId")
        if not session_id:
            raise AuthenticationError("Session ID alınamadı. Cookie döndürülmedi.")

        set_env_variable("ASP_NET_SESSION_ID", session_id)
        log_message("✅ Authentication başarılı. Session ID kaydedildi.")

    except requests.exceptions.RequestException as req_err:
        log_error(-1, f"HTTP Hatası: {str(req_err)}", "Authentication")
        raise
    except Exception as e:
        log_error(-2, f"Genel Hata: {str(e)}", "Authentication")
        raise

# Self-executing init
_authenticate()
