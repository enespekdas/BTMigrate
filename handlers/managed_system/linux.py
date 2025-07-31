from config.settings import WORKGROUP_ID, LINUX_MANAGED_SYSTEM_TEMPLATE
from api.managed_system import create_managed_system
from api.functional_account import get_functional_account_id

def handle_linux_managed_system(row_number, row, os_info, step_results, cleaned_ip):
    ip = os_info.get("IPAddress", cleaned_ip)
    hostname = os_info.get("HostName", cleaned_ip)
    domain = (os_info.get("Domain") or "").lower()
    os_name = (os_info.get("OS") or "").lower()

    if not ip:
        return False, "IP bilgisi eksik olduğu için Managed System oluşturulamadı."

    payload = LINUX_MANAGED_SYSTEM_TEMPLATE.copy()
    payload["HostName"] = hostname
    payload["SystemName"] = hostname
    payload["DnsName"] = ip
    payload["IPAddress"] = ip
    payload["WorkgroupID"] = WORKGROUP_ID
    payload["Description"] = f"Created by BTMigrate – IP: {ip}"

    functional_account_id = get_functional_account_id(domain, os_name)
    if functional_account_id:
        payload["FunctionalAccountID"] = functional_account_id

    payload = {k: v for k, v in payload.items() if v not in [None, "", "null"]}

    return create_managed_system(row_number, payload)
