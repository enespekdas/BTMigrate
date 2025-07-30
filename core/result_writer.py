import csv
import os
from datetime import datetime

# 🔹 Kayıt dizini ve dosyası
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULT_FILE = os.path.join(RESULTS_DIR, f"btmigrate_output_{timestamp}.csv")

# 🔹 Aşamalar – kolayca genişletilebilir
STEPS = [
    "ManagedSystem",
    "ManagedAccount",
    "Application",
    "SmartRule",
    "UserGroup",
    "User",
    "RolePermission"
]

# 🔹 Başlıklar
HEADERS = ["Satır No", "Genel Durum"]
for step in STEPS:
    HEADERS.append(f"{step} Durum")
    HEADERS.append(f"{step} Açıklama")

# 🔹 CSV başlığını yaz
with open(RESULT_FILE, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(HEADERS)

# 🔹 Satır ekleyici
def write_result_row(row_number: int, genel_durum: str, step_results: dict):
    """
    step_results örnek:
    {
        "ManagedSystem": ("✅", "Başarılı"),
        "ManagedAccount": ("⛔", "Eksik bilgi"),
        ...
    }
    """
    row_data = [row_number, genel_durum]
    for step in STEPS:
        status, message = step_results.get(step, ("", ""))
        row_data.extend([status, message])

    with open(RESULT_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row_data)
