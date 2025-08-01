import os


# API_BASE_URL = "https://pam.test.local/BeyondTrust/api/public/v3"
# VERIFY_SSL = False  # Test ortamı için False, prod'da True yapılabilir
# WORKGROUP_ID = 2
# DEFAULT_TIMEOUT = 30
# DEFAULT_RELEASE_DURATION = 120
# DEFAULT_PORTS = {
#     "windows": 445,
#     "linux": 22,
#     "mssql": 1433,
#     "oracle": 1521
# }
# LOG_DIR = "logs/"





API_BASE_URL = "https://bt.quasys.local/BeyondTrust/api/public/v3"
VERIFY_SSL = False

AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "PS-Auth key=043f1686e106b3f64c0fcb07b1a66168f09675aa74d7f6999c6109e2628ffe734cc0e26a7c476d6ee217713ff168beabb9f8438bd31637a75f96fd7bd0350ce1; runas=btadmin;"
}

AUTH_BODY = {}  # Eğer JSON body gerekiyorsa
WORKGROUP_ID = 2 

VERIFY_SSL = False  # Local test ortamı için

PAM_ENVANTER_FILE_PATH = "data/PamEnvanter.xlsx"
OS_ENVANTER_FILE_PATH = "data/OsEnvanter.xlsx"
SAFE_USER_FILE_PATH = "data/PamSafeUser.xlsx"
BTMIGRATE_WORK_FILE_PATH = "data/btmigrate_work.xlsx"


IGNORED_ROW_COLUMNS  = [
    "PamEnvar", "username", "remote", "reason", "os_type"
]

RESULT_ROW_COLUMNS = [
    "PamEnvar", "username", "ip address", "hostname", "application", "OS",
    "safe name", "members", "database", "port", "type", "domain"
]

EXCLUDED_SAFE_MEMBERS = [
    "SGOM",
    "PasswordManager",
    "Y_UCUNCUOGLU",
    "Uploader",
    "PSMAppUsers",
    "OZCAN",
    "API_USR",
    "E_YILDIZ41",
    "S_OZCAN"
    # 👆 exclude etmek istediğin kullanıcıları buraya ekle
]

# Windows Managed System create template
WINDOWS_MANAGED_SYSTEM_TEMPLATE = {
    "PlatformID": "1",
    "EntityTypeID": 1,
    "AssetID": None,
    "DatabaseID": None,
    "DirectoryID": None,
    "CloudID": None,
    "FunctionalAccountID": "",#buraya Functional Account id si gelecek
    "HostName": "",      # Buraya hostname adı gelecek
    "DnsName": "",       # Buraya hostname adı gelecek
    "IPAddress": "",     # Buraya IP adresi gelecek
    "Port": "3389",
    "Timeout": "30",
    "SshKeyEnforcementMode": "0",
    "PasswordRuleID": "0",
    "ReleaseDuration": "120",
    "MaxReleaseDuration": "10079",
    "ISAReleaseDuration": "120",
    "AutoManagementFlag": "true",
    "CheckPasswordFlag": "false",
    "ChangePasswordAfterAnyReleaseFlag": "false",
    "ResetPasswordOnMismatchFlag": "false",
    "ChangeFrequencyType": "first",
    "ChangeFrequencyDays": "30",
    "ChangeTime": "23:30",
    "RemoteClientType": "None",
    "IsApplicationHost": "false"
}

# # Linux Managed System create template
LINUX_MANAGED_SYSTEM_TEMPLATE = {
    "EntityTypeID": 1,
    "HostName": "",
    "DnsName": "",
    "IPAddress": "",
    "SystemName": "",
    "PlatformID": 2,
    "Port": 22,
    "Timeout": 30,
    "ReleaseDuration": 120,
    "MaxReleaseDuration": 10079,
    "ISAReleaseDuration": 120,
    "AutoManagementFlag": "",
    "FunctionalAccountID": "",
    "LoginAccountID": "null",
    "ElevationCommand": "null",
    "SshKeyEnforcementMode": 0,
    "CheckPasswordFlag": "false",
    "ChangePasswordAfterAnyReleaseFlag": "false",
    "ResetPasswordOnMismatchFlag": "false",
    "ChangeFrequencyType": "first",
    "ChangeFrequencyDays": 30,
    "ChangeTime": "23:30",
    "AccountNameFormat": 0,
    }

## Oracle Managed System template
ORACLE_MANAGED_SYSTEM_TEMPLATE = {
    "EntityTypeID": 2,
    "AssetID": None,
    "DatabaseID": None,
    "DirectoryID": None,
    "CloudID": None,
    "HostName": "",
    "DnsName": "",
    "IPAddress": "",
    "InstanceName": "",
    "IsDefaultInstance": False,
    "Template": None,
    "ForestName": None,
    "UseSSL": None,
    "OracleInternetDirectoryID": None,
    "OracleInternetDirectoryServiceName": None,
    "SystemName": "",
    "PlatformID": 8,
    "NetBiosName": None,
    "Port": 0,
    "Timeout": 30,
    "Description": "",
    "ContactEmail": None,
    "PasswordRuleID": 0,
    "DSSKeyRuleID": 0,
    "ReleaseDuration": 120,
    "MaxReleaseDuration": 10079,
    "ISAReleaseDuration": 120,
    "AutoManagementFlag": False,
    "FunctionalAccountID": None,
    "LoginAccountID": None,
    "ElevationCommand": None,
    "SshKeyEnforcementMode": 0,
    "CheckPasswordFlag": False,
    "ChangePasswordAfterAnyReleaseFlag": False,
    "ResetPasswordOnMismatchFlag": False,
    "ChangeFrequencyType": "first",
    "ChangeFrequencyDays": 30,
    "ChangeTime": "23:30",
    "AccountNameFormat": 0,
    "RemoteClientType": "None",  # ✅ bu özel enum, string olmalı!
    "ApplicationHostID": None,
    "IsApplicationHost": False,
    "AccessURL": None
}

## MSSQL Managed System template

MSSQL_MANAGED_SYSTEM_TEMPLATE = {
    "EntityTypeID": 2,
    "AssetID": None,
    "DatabaseID": None,
    "DirectoryID": None,
    "CloudID": None,
    "HostName": "",
    "DnsName": "",
    "IPAddress": "",
    "InstanceName": "",
    "IsDefaultInstance": False,
    "Template": None,
    "ForestName": None,
    "UseSSL": None,
    "OracleInternetDirectoryID": None,
    "OracleInternetDirectoryServiceName": None,
    "SystemName": "",
    "PlatformID": 11,
    "NetBiosName": None,
    "Port": 1433,
    "Timeout": 30,
    "Description": None,
    "ContactEmail": None,
    "PasswordRuleID": 0,
    "DSSKeyRuleID": 0,
    "ReleaseDuration": 120,
    "MaxReleaseDuration": 10079,
    "ISAReleaseDuration": 120,
    "AutoManagementFlag": False,
    "FunctionalAccountID": 0,
    "LoginAccountID": None,
    "ElevationCommand": None,
    "SshKeyEnforcementMode": 0,
    "CheckPasswordFlag": False,
    "ChangePasswordAfterAnyReleaseFlag": False,
    "ResetPasswordOnMismatchFlag": False,
    "ChangeFrequencyType": "first",
    "ChangeFrequencyDays": 30,
    "ChangeTime": "23:30",
    "AccountNameFormat": 0,
    "RemoteClientType": "None",
    "ApplicationHostID": None,
    "IsApplicationHost": False,
    "AccessURL": None
}