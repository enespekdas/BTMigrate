# BTMigrate Projesi

Bu proje, BeyondTrust PAM ortamına toplu managed system ve account geçişini (migrasyon) otomatikleştirmek için geliştirilmiştir. Kaynak veriler Excel dosyaları üzerinden alınır ve BeyondTrust API'leri kullanılarak ilgili kaynaklar oluşturulur.

---

## 🔧 Proje Yapısı

├── api/ # BeyondTrust API çağrılarını içerir
│ ├── functional_account.py # FunctionalAccount verisi çekme ve cache işlemleri
│ └── managed_system.py # ManagedSystem verisi oluşturma ve çekme işlemleri
├── auth/
│ └── login.py # BeyondTrust sistemine login olup Session ID alır
├── config/
│ └── settings.py # Ortak ayarlar (API URL, SSL doğrulama, dosya yolları)
├── core/
│ ├── env.py # Ortam değişkenlerini yönetir
│ └── exceptions.py # Özel exception tanımları
├── data/
│ ├── btmigrate_work.xlsx # Hazırlanmış kaynak Excel (normalize edilmiş veri)
│ ├── OsEnvanter.xlsx # OS bilgilerini içeren envanter
│ ├── PamEnvanter.xlsx # PAM hesaplarını içeren temel envanter
│ └── PamSafeUser.xlsx # Ortak kasa (safe) üyeliklerini içerir
├── excel/
│ ├── excel_loader.py # Excel dosyalarını okuyan yardımcı fonksiyonlar
│ └── init.py
├── generator/
│ ├── prepare_workbook.py # Excel'lerden normalize çalışma dosyasını üretir
│ └── init.py
├── logs/ # Log dosyaları burada tutulur (otomatik oluşur)
├── main.py # Uygulamanın giriş noktası
├── row_processors/
│ ├── oracle_handler.py # Oracle sunucular için özel IP/hostname eşlemesi
│ ├── remote_machine_handler.py # RemoteMachines kolonunu işleyip eşleşme yapar
│ ├── utils.py # Row işlemlerinde kullanılan yardımcı fonksiyonlar
│ └── init.py
├── utils/
│ ├── logger.py # Loglama yardımcıları
│ ├── network_utils.py # IP/hostname eşlemesi ve DNS kontrolleri
│ ├── string_utils.py # Metin işleme yardımcıları
│ ├── universal_cache.py # Tüm cache mekanizması burada tutulur
│ └── validators.py # Veri doğrulama yardımcıları
├── folder_structure.txt # tree komutuyla alınmış klasör yapısı çıktısı
├── README.md # Bu dosya — proje açıklamaları
└── tree.md # Alternatif olarak klasör yapısını gösteren markdown



---

## 🔁 Temel Akış

1. `generator/prepare_workbook.py`:  
   Excel dosyalarını okuyarak normalize edilmiş `btmigrate_work.xlsx` dosyasını oluşturur.

2. `main.py`:  
   Orkestrasyonu başlatır. Authentication olur, managed system yaratımı ve ileride smart rule/user işlemleri buradan tetiklenir.

3. `api/`:  
   BeyondTrust API işlemleri yapılır. Session ID `auth/login.py` üzerinden alınır.

4. `row_processors/`:  
   Normalize Excel üzerindeki her satırı işler. IP/hostname lookup, OS eşleşmesi, functional account eşlemesi gibi görevler burada yapılır.

---

## 📦 Kullanılan Excel Dosyaları

- **PamEnvanter.xlsx**:  
  PAM ortamındaki uygulama hesapları (`address`, `username`, `remoteMachines`, `platformId`, `database`, `port`).

- **OsEnvanter.xlsx**:  
  Hostname-IP-OS-Domain eşleşmelerini içerir.

- **PamSafeUser.xlsx**:  
  Safe (ortak kasa) üyelik eşleşmeleri (`safeName`, `memberName`).

- **btmigrate_work.xlsx**:  
  Otomatik oluşturulur. Normalize edilmiş, işlenmeye hazır veri içerir.

---

## 🔐 Oturum ve Güvenlik

- Session ID `auth/login.py` tarafından alınır ve çevresel değişkene yazılır.
- Local test ortamı için `VERIFY_SSL = False` kullanılır.  
  Uyarı bastırmak için:
  ```python
  import urllib3
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
