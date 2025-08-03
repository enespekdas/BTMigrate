# handlers/application/assign_application.py

import re
from utils.logger import log_message
from api.application import assign_application_to_account, is_application_already_assigned
from utils.universal_cache import UniversalCache

def normalize(s: str) -> str:
    """
    Uygulama isimlerini normalize eder:
    - Küçük harfe çevirir
    - Baş-taki ve son-daki boşlukları siler
    - Tüm iç boşlukları kaldırır (ör: 'Oracle  App' → 'oracleapp')
    """
    return re.sub(r"\s+", "", s.lower().strip())

def parse_application_field(application_string) -> list[str]:
    if not application_string:
        return []
    try:
        raw = str(application_string).strip()
        if raw.lower() in ("nan", "none", ""):
            return []
        return [normalize(a) for a in raw.split(",") if a.strip()]
    except Exception:
        return []

def assign_applications_to_managed_account(account_id: int, application_string, cache: UniversalCache):
    app_names = parse_application_field(application_string)
    if not app_names:
        return

    cached_apps = cache.get_cached_data("Application") or []

    for name in app_names:
        matched = False

        for app in cached_apps:
            display_name = normalize(app.get("DisplayName") or "")
            application_id = app.get("ApplicationID")

            if display_name == name:
                if is_application_already_assigned(account_id, application_id):
                    log_message(f"⚠️ Application '{name}' zaten atanmış, atlama yapıldı.")
                    matched = True
                    break

                assign_application_to_account(account_id, application_id)
                log_message(f"✅ Application '{name}' başarıyla atandı (ID: {application_id}).")
                matched = True
                break

        if not matched:
            log_message(f"⚠️ Application '{name}' cache'te bulunamadı, atama yapılmadı.")
    