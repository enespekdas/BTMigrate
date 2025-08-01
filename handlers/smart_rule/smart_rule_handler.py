# ✅ handlers/smart_rule/smart_rule_handler.py

from config.settings import SMART_GROUP_PREFIX
from utils.logger import log_message, log_error, log_debug
from api.smart_rule import (
    create_smart_rule,
    get_smart_rule_accounts,
    update_smart_rule_accounts
)
from utils.universal_cache import UniversalCache

SMART_RULE_CATEGORY = "SmartRule"

def handle_smart_rule(row: dict, managed_account_id: int, cache: UniversalCache) -> None:
    row_number = row.get("PamEnvanterSatır", -1)
    safe_name = (row.get("safe name") or "").strip()
    if not safe_name:
        log_error(row_number, "❌ safe name alanı boş. Smart Rule oluşturulamaz.", error_type="SmartRule")
        return

    group_name = f"{SMART_GROUP_PREFIX}{safe_name}"
    log_debug(f"[Row {row_number}] 🔍 Smart Rule adı oluşturuldu: {group_name}")

    all_smart_rules = cache.get_all_by_key(SMART_RULE_CATEGORY)
    existing_rule = next(
        (rule for rule in all_smart_rules if (rule.get("Title") or "").strip().lower() == group_name.lower()),
        None
    )

    if existing_rule:
        smart_rule_id = existing_rule.get("SmartRuleID")
        log_message(f"[Row {row_number}] ✅ Smart Rule zaten mevcut: {group_name} (ID: {smart_rule_id})")

        existing_ids = get_smart_rule_accounts(smart_rule_id)
        combined_ids = existing_ids + [managed_account_id]

        if update_smart_rule_accounts(smart_rule_id, combined_ids):
            log_message(f"[Row {row_number}] 📎 Smart Rule account listesi güncellendi: {combined_ids}")
        else:
            log_error(row_number, f"Smart Rule account güncelleme başarısız: {group_name}", error_type="SmartRule")
        return

    payload = {
        "IDs": [managed_account_id],
        "Title": group_name,
        "Category": "Quick Rules",
        "Description": "Quick Rule for Safe name",
        "RuleType": "ManagedAccount"
    }

    log_debug(f"[Row {row_number}] 📦 Smart Rule payload: {payload}")
    log_message(f"[Row {row_number}] 🚀 Smart Rule oluşturuluyor: {group_name}")

    response = create_smart_rule(payload)
    if response:
        cache.get_all_by_key(SMART_RULE_CATEGORY).append(response)
        log_message(f"[Row {row_number}] ✅ Smart Rule başarıyla oluşturuldu: {group_name}")
    else:
        log_error(row_number, f"Smart Rule oluşturulamadı: {group_name}", error_type="SmartRule")
