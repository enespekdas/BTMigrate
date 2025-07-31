import csv
import os
from datetime import datetime
from config.settings import MIGRATION_STEPS as STEPS

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULT_FILE = os.path.join(RESULTS_DIR, f"btmigrate_output_{timestamp}.csv")
FAILED_FILE = os.path.join(RESULTS_DIR, f"btmigrate_basarisiz_{timestamp}.csv")
TRACK_FILE = os.path.join(RESULTS_DIR, f"btmigrate_track_{timestamp}.csv")

HEADERS = ["Satır No", "Genel Durum"]
for step in STEPS:
    HEADERS.append(f"{step} Durum")
    HEADERS.append(f"{step} Açıklama")

with open(RESULT_FILE, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(HEADERS)

with open(FAILED_FILE, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Excel Satır", "Account", "RemoteMachine", "Temizlenmiş Sistem", "Durum Notu"])

with open(TRACK_FILE, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Excel Satır", "Account", "RemoteMachine", "Platform"])

def write_result_row(row_number: int, genel_durum: str, step_results: dict):
    row_data = [row_number, genel_durum]
    for step in STEPS:
        status, message = step_results.get(step, ("", ""))
        row_data.extend([status, message])
    with open(RESULT_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row_data)

def write_unmatched_system(row_number: int, account: str, original: str, cleaned: str, reason: str):
    row_data = [row_number, account, original, cleaned, reason]
    with open(FAILED_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row_data)

def write_track_system(row_number: int, account: str, remote_machine: str, platform: str):
    row_data = [row_number, account, remote_machine, platform]
    with open(TRACK_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row_data)
