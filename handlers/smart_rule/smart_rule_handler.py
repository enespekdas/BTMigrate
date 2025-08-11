# handlers/smart_rule/smart_rule_handler.py

from typing import Optional
from config.settings import SMART_GROUP_PREFIX
from api.smart_rule import create_smart_rule, get_smart_rule_accounts, update_smart_rule_accounts
from utils.universal_cache import UniversalCache
from utils.report import sr_success, sr_error

SMART_RULE_CATEGORY = "SmartRule"

def handle_smart_rule(row: dict, managed_account_id: int, cache: UniversalCache) -> Optional[int]:
    row_number = row.get("Satır No", row.get("PamEnvanterSatır", -1))
    safe_name = (row.get("safe name") or "").strip()

    if not safe_name:
        sr_error(row_number, row, -501, "safe name alanı boş. Smart Rule oluşturulamaz.", "SmartRule")
        return None

    group_name = f"{SMART_GROUP_PREFIX}{safe_name}"

    all_smart_rules = cache.get_all_by_key(SMART_RULE_CATEGORY) or []
    existing_rule = next(
        (rule for rule in all_smart_rules if (rule.get("Title") or "").strip().lower() == group_name.lower()),
        None
    )

    # 1) Zaten var mı?
    if existing_rule:
        smart_rule_id = existing_rule.get("SmartRuleID")

        existing_ids = get_smart_rule_accounts(smart_rule_id) or []
        if managed_account_id in existing_ids:
            sr_success(row_number, row, already=True, account_assigned=True,
                       message=f"Smart Rule zaten mevcut ve hesap bağlı: {group_name}")
            return smart_rule_id

        # Ekle ve güncelle
        combined_ids = list(set(existing_ids + [managed_account_id]))
        if update_smart_rule_accounts(smart_rule_id, combined_ids):
            # Cache senkronizasyonu (IDs alanı varsa güncelle)
            for rule in all_smart_rules:
                if rule.get("SmartRuleID") == smart_rule_id:
                    rule["IDs"] = combined_ids
                    break
            sr_success(row_number, row, already=True, account_assigned=True,
                       message=f"Smart Rule güncellendi (hesap eklendi): {group_name}")
            return smart_rule_id

        sr_error(row_number, row, -503, f"Smart Rule account güncelleme başarısız: {group_name}", "SmartRule")
        return None

    # 2) Yoksa oluştur
    payload = {
        "IDs": [managed_account_id],
        "Title": group_name,
        "Category": "Quick Rules",
        "Description": f"Quick Rule for {safe_name}",
        "RuleType": "ManagedAccount",
    }

    response = create_smart_rule(payload)
    if response:
        cache_list = cache.get_all_by_key(SMART_RULE_CATEGORY) or []
        cache_list.append(response)
        sr_success(row_number, row, created=True, account_assigned=True,
                   message=f"Smart Rule oluşturuldu: {group_name}")
        return response.get("SmartRuleID")

    sr_error(row_number, row, -502, f"Smart Rule oluşturulamadı: {group_name}", "SmartRule")
    return None
