import os
import json
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

import auth.login  # Session ID'yi otomatik yükle
from config.settings import VERIFY_SSL, API_BASE_URL
from utils.logger import log_message, log_error

# ⚠️ SSL uyarılarını bastır
warnings.simplefilter("ignore", InsecureRequestWarning)

# Session ID'yi al
session_id = os.getenv("ASP_NET_SESSION_ID")
if not session_id:
    raise Exception("Session ID bulunamadı. auth.login doğru çalışmadı.")

headers = {
    "Cookie": f"ASP.NET_SessionId={session_id}"
}

# JSON yolu
json_path = "data/generated_objects.json"
with open(json_path, "r") as f:
    data = json.load(f)

# 🧩 1. Membership'ları sil
memberships = data.get("UserGroupMembership", [])
for item in memberships:
    user_id = item.get("UserID")
    group_id = item.get("GroupID")
    if not user_id or not group_id:
        continue

    url = f"{API_BASE_URL}/Users/{user_id}/UserGroups/{group_id}"
    try:
        response = requests.delete(url, headers=headers, verify=VERIFY_SSL)
        if response.status_code in (200, 204):
            log_message(f"✅ Membership silindi → UserID: {user_id}, GroupID: {group_id}")
        else:
            log_error(-1, f"❌ Membership silinemedi → UserID: {user_id}, GroupID: {group_id} | Status: {response.status_code} | Body: {response.text}", error_type="Cleanup")
    except Exception as e:
        log_error(-1, f"❌ Exception → UserID: {user_id}, GroupID: {group_id} | {str(e)}", error_type="Cleanup")

# 🧹 Unique ID listeleri
unique_user_ids = set([item["UserID"] for item in memberships if "UserID" in item])
unique_group_ids = set([item["GroupID"] for item in memberships if "GroupID" in item])

# 🧩 2. Kullanıcıları sil
for user_id in unique_user_ids:
    url = f"{API_BASE_URL}/Users/{user_id}"
    try:
        response = requests.delete(url, headers=headers, verify=VERIFY_SSL)
        if response.status_code in (200, 204):
            log_message(f"✅ User silindi → UserID: {user_id}")
        else:
            log_error(-1, f"❌ User silinemedi → UserID: {user_id} | Status: {response.status_code} | Body: {response.text}", error_type="Cleanup")
    except Exception as e:
        log_error(-1, f"❌ Exception → UserID: {user_id} | {str(e)}", error_type="Cleanup")

# 🧩 3. Grupları sil
for group_id in unique_group_ids:
    url = f"{API_BASE_URL}/UserGroups/{group_id}"
    try:
        response = requests.delete(url, headers=headers, verify=VERIFY_SSL)
        if response.status_code in (200, 204):
            log_message(f"✅ Group silindi → GroupID: {group_id}")
        else:
            log_error(-1, f"❌ Group silinemedi → GroupID: {group_id} | Status: {response.status_code} | Body: {response.text}", error_type="Cleanup")
    except Exception as e:
        log_error(-1, f"❌ Exception → GroupID: {group_id} | {str(e)}", error_type="Cleanup")

# 🧩 4. SmartRule'ları sil
smart_rule_ids = data.get("SmartRule", [])
for rule_id in smart_rule_ids:
    if not rule_id:
        continue
    url = f"{API_BASE_URL}/SmartRules/{rule_id}"
    try:
        response = requests.delete(url, headers=headers, verify=VERIFY_SSL)
        if response.status_code in (200, 204):
            log_message(f"✅ SmartRule silindi → SmartRuleID: {rule_id}")
        else:
            log_error(-1, f"❌ SmartRule silinemedi → SmartRuleID: {rule_id} | Status: {response.status_code} | Body: {response.text}", error_type="Cleanup")
    except Exception as e:
        log_error(-1, f"❌ Exception → SmartRuleID: {rule_id} | {str(e)}", error_type="Cleanup")

# 🧩 5. ManagedAccount'ları sil
account_ids = data.get("ManagedAccount", [])
for account_id in account_ids:
    if not account_id:
        continue
    url = f"{API_BASE_URL}/ManagedAccounts/{account_id}"
    try:
        response = requests.delete(url, headers=headers, verify=VERIFY_SSL)
        if response.status_code in (200, 204):
            log_message(f"✅ ManagedAccount silindi → AccountID: {account_id}")
        else:
            log_error(-1, f"❌ ManagedAccount silinemedi → AccountID: {account_id} | Status: {response.status_code} | Body: {response.text}", error_type="Cleanup")
    except Exception as e:
        log_error(-1, f"❌ Exception → AccountID: {account_id} | {str(e)}", error_type="Cleanup")

# 🧩 6. ManagedSystem'leri sil
system_ids = data.get("ManagedSystem", [])
for system_id in system_ids:
    if not system_id:
        continue
    url = f"{API_BASE_URL}/ManagedSystems/{system_id}"
    try:
        response = requests.delete(url, headers=headers, verify=VERIFY_SSL)
        if response.status_code in (200, 204):
            log_message(f"✅ ManagedSystem silindi → SystemID: {system_id}")
        else:
            log_error(-1, f"❌ ManagedSystem silinemedi → SystemID: {system_id} | Status: {response.status_code} | Body: {response.text}", error_type="Cleanup")
    except Exception as e:
        log_error(-1, f"❌ Exception → SystemID: {system_id} | {str(e)}", error_type="Cleanup")
