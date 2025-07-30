from api.managed_system import get_managed_system_by_ip
from config.settings import EXCEL_COLUMN_MAP

def process_managed_system(row):
    try:
        ip_address = str(row.get(EXCEL_COLUMN_MAP["ip"], "")).strip()
        if not ip_address:
            return "Geçersiz Veri", "Excel satırında IP Address boş"

        matched_system = get_managed_system_by_ip(ip_address)

        if matched_system:
            return "Zaten Kayıtlı", f"Zaten kayıtlı: {ip_address}"
        else:
            # 🎯 Create işlemi burada yapılabilir:
            print("managed system create et")
            # create_status, create_msg = create_managed_system(row)
            #return "Oluşturulacak", f"{ip_address} yeni kayıt olabilir"
            # if create_status:
            #     return "Oluşturuldu", f"{ip_address} başarıyla eklendi."
            # else:
            #     return "Oluşturulamadı", f"Hata: {create_msg}"

    except Exception as e:
        return "Hata", f"Managed System kontrol hatası: {str(e)}"
