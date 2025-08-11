# handlers/application/assign_application.py

import re
from utils.logger import log_message
from api.application import assign_application_to_account, get_assigned_applications
from utils.universal_cache import UniversalCache
from utils.report import app_success, app_error  # ✅

def normalize(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").strip().lower())

def parse_application_field(application_string) -> list[str]:
    if not application_string:
        return []
    try:
        raw = str(application_string).strip()
        if raw.lower() in ("nan", "none", ""):
            return []
        return list({normalize(a) for a in raw.split(",") if a.strip()})
    except Exception:
        return []

def _build_app_index(cached_apps: list[dict]) -> dict[str, dict]:
    index = {}
    for app in cached_apps or []:
        key = normalize(app.get("DisplayName"))
        if key:
            index[key] = app
    return index

def assign_applications_to_managed_account(row: dict, account_id: int, application_string, cache: UniversalCache):
    row_number = row.get("Satır No", row.get("PamEnvanterSatır", -1))

    app_names = parse_application_field(application_string)
    if not app_names:
        # dispatcher boşluk kontrolünde zaten success verdi; burada sessiz çık
        return {"assigned": [], "already": [], "not_found": [], "failed": []}

    cached_apps = cache.get_cached_data("Application") or []
    app_index = _build_app_index(cached_apps)

    # mevcut atamalar → tek GET
    existing = get_assigned_applications(account_id)
    existing_ids = {a.get("ApplicationID") for a in existing if a.get("ApplicationID")}

    assigned, already, not_found, failed = [], [], [], []

    for name in app_names:
        app_obj = app_index.get(name)
        if not app_obj:
            not_found.append(name)
            log_message(f"⚠️ Application '{name}' cache'te bulunamadı, atama yapılmadı.")
            continue

        app_id = app_obj.get("ApplicationID")
        if app_id in existing_ids:
            already.append(name)
            log_message(f"ℹ️ Application '{name}' zaten atanmış, atlama yapıldı.")
            continue

        ok = assign_application_to_account(account_id, app_id)
        if ok:
            assigned.append(name)
            existing_ids.add(app_id)
        else:
            failed.append(name)

    # Raporlama (tek noktadan)
    total = len(app_names)
    log_message(
        f"📦 App atama özeti (AccountID:{account_id}) → İstenen:{total}, "
        f"Atanan:{len(assigned)}, Zaten:{len(already)}, Bulunamadı:{len(not_found)}, Başarısız:{len(failed)}"
    )

    if not_found or failed:
        detail = ""
        if not_found:
            detail += f"Bulunamadı={not_found} "
        if failed:
            detail += f"Başarısız={failed}"
        app_error(row_number, row, -720, f"Atanamayan uygulamalar var. {detail.strip()}", "ApplicationAssign", unassigned_exists=True)
    else:
        app_success(row_number, row, unassigned_exists=False, message="Tüm uygulamalar başarıyla atandı veya önceden atanmış.")

    return {
        "assigned": assigned,
        "already": already,
        "not_found": not_found,
        "failed": failed,
    }
