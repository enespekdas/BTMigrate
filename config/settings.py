import os


API_BASE_URL = "https://bt.quasys.local/BeyondTrust/api/public/v3"
VERIFY_SSL = False

AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "PS-Auth key=043f1686e106b3f64c0fcb07b1a66168f09675aa74d7f6999c6109e2628ffe734cc0e26a7c476d6ee217713ff168beabb9f8438bd31637a75f96fd7bd0350ce1; runas=btadmin;"
}

AUTH_BODY = {}  # Eğer JSON body gerekiyorsa
WORKGROUP_ID = 2 

VERIFY_SSL = False  # Local test ortamı için

EXCEL_FILE_PATH = os.path.join("templates", "data.xlsx")

SHOW_EXCEL_SAMPLE_ROWS = True  # Geliştirme ortamında True, prod'da False yapılabilir


# STEP bazlı işlem adımları -> Output da çıkan csv için gerekli olan kolon isimleri.
MIGRATION_STEPS = [
    "ManagedSystem",
    "ManagedAccount",
    "Application",
    "SmartRule",
    "UserGroup",
    "User",
    "RolePermission"
]


EXCEL_COLUMN_MAP = {
    "ip": "IPAdress",
    "hostname": "Hostname",
    "username": "Username",
    "os": "OS",
    "domain": "Domain",
    "application": "Application",
    "safeName": "Safe Name",
    "users": "Erişecek Kullanıcılar",
    "port": "Port",
    "databaseName": "DatabaseName",
}