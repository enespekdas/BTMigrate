import json
import os

TRACK_FILE_PATH = "data/generated_objects.json"
_initialized = False  # sadece bir kez silinmesini sağlamak için flag

def add_created_object(object_type: str, object_id: int):
    global _initialized
    if not object_id:
        return

    # İlk kez çağrıldığında dosyayı temizle
    if not _initialized:
        if os.path.exists(TRACK_FILE_PATH):
            os.remove(TRACK_FILE_PATH)
        with open(TRACK_FILE_PATH, "w") as f:
            json.dump({}, f)
        _initialized = True

    # Dosyayı oku
    with open(TRACK_FILE_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    if object_type not in data:
        data[object_type] = []

    if object_id not in data[object_type]:
        data[object_type].append(object_id)

    with open(TRACK_FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)
