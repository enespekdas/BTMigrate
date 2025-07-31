# utils/string_utils.py

import re

def clean_remote(value: str) -> str:
    """
    IP veya hostname bilgisini normalize eder.
    Örn: https://myhost.com:8080/path → myhost.com
    """
    if not value or not isinstance(value, str):
        return ""

    value = value.strip()

    # http/https kaldır
    value = re.sub(r'^https?://', '', value)

    # ? ile başlayan query string'i sil
    value = value.split("?")[0]

    # / veya : gördüğünde split al, ilkini al
    value = re.split(r"[:/]", value)[0]

    return value.strip()
