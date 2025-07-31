from config.settings import WORKGROUP_ID, WINDOWS_MANAGED_SYSTEM_TEMPLATE
from api.managed_system import create_managed_system
from api.functional_account import get_functional_account_id

def handle_windows_managed_system(row_number, row, os_info, step_results, cleaned_ip):
    ip = os_info.get("IPAddress", cleaned_ip)
    hostname = os_info.get("HostName", cleaned_ip)
    domain = (os_info.get("Domain") or "").lower()
    os_name = (os_info.get("OS") or "").lower()

    if not ip:
        return False, "IP bilgisi eksik olduğu için Managed System oluşturulamadı."

    payload = WINDOWS_MANAGED_SYSTEM_TEMPLATE.copy()
    payload["HostName"] = hostname
    payload["DnsName"] = ip
    payload["IPAddress"] = ip
    payload["WorkgroupID"] = WORKGROUP_ID
    payload["Description"] = f"BTMigrate created → {hostname or ip}"

    functional_account_id = get_functional_account_id(domain, os_name)
    if functional_account_id:
        payload["FunctionalAccountID"] = functional_account_id

    return create_managed_system(row_number, payload)
