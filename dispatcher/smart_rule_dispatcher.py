# dispatcher/smart_rule_dispatcher.py

from typing import Optional
from handlers.smart_rule.smart_rule_handler import handle_smart_rule
from utils.report import sr_init, sr_error

def dispatch_smart_rule(row: dict, managed_account_id: int, cache) -> Optional[int]:
    sr_init(row)
    try:
        return handle_smart_rule(row, managed_account_id, cache)
    except Exception as e:
        row_number = row.get("Satır No", row.get("PamEnvanterSatır", -1))
        sr_error(row_number, row, -900, f"Smart Rule Dispatcher exception: {str(e)}", "SmartRuleDispatcher")
        return None
