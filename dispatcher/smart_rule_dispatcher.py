from handlers.smart_rule.smart_rule_handler import handle_smart_rule
from utils.logger import log_error

def dispatch_smart_rule(row: dict, managed_account_id: int, cache) -> None:
    """
    Smart Rule işlemi: safeName ve managed_account_id bilgisine göre SmartRule oluşturur veya varsa kullanır.
    """
    try:
        handle_smart_rule(row, managed_account_id, cache)
    except Exception as e:
        row_number = row.get("PamEnvanterSatır", -1)
        log_error(row_number, f"Smart Rule Dispatcher hatası: {str(e)}", error_type="SmartRuleDispatcher")
