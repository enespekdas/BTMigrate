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



✅ 1. GENEL MİMARİ YAPISI

BTMigrate projesi iki aşamalı çalışmaktadır:

Ön Hazırlık Aşaması

Excel dosyalarından (PamEnvanter, OsEnvanter, PamSafeUser) veriler okunur.

Remote machine işlemleriyle normalize edilerek btmigrate_work.xlsx dosyası oluşturulur.

Bu aşamada hatalı/eksik satırlar ignored_rows sheet'ine yazılır.

Uygulama Aşaması

btmigrate_work.xlsx tek kaynaktır. Satır satır işlenerek aşağıdaki operasyonlar yapılır:

Managed System oluşturma

Managed Account oluşturma

Application atama

Smart Rule oluşturma

User Group oluşturma

Kullanıcıları gruba ekleme

User Group Role atama (SmartRule bazlı)

🔍 2. ÖNEMLİ MODÜlLER ve AKIŞ SIRASI

2.1 Orchestrator

Ana yönlendirici.

Satır satır btmigrate_work.xlsx dosyasını okur.

Her satır için dispatch modüllerini çağırar:

managed_system_dispatcher

managed_account_dispatcher

application_dispatcher

smart_rule_dispatcher

user_group_dispatcher

user_member_dispatcher

2.2 Dispatcher Dosyaları

Platform veya türe göre ilgili handler'a yönlendirir.

Örnek: managed_system_dispatcher.py dosyası, platform windows ise handlers/managed_system/windows.py dosyasını çağırır.

2.3 Handler Dosyaları

Her bir işlemin detaylı yürütüldüğü modüllerdir.

Örnek:

handlers/managed_system/windows.py: Windows için payload oluşturup API çağırır.

handlers/user_group/create_or_update_user_group.py: Grup oluşturur ve rol ataması yapar.

2.4 API Modülleri

Gerçek HTTP istekleri burada yapılır.

Örnek: api/user.py, api/managed_system.py, api/user_group.py

Session, header, cookie ve URL formatlama bu katmanda yapılır.

🚪 3. CACHE MEKANİZMASI

Tüm veriler bir kez çekilir ve UniversalCache sınıfı ile bellekte tutulur.

Kullanılan cache key'leri: ManagedSystem, FunctionalAccount, User, UserGroup, SmartRule, Application

Yineleme/tekrar create işlemleri bu cache yardımıyla engellenir.

💡 4. KARAR NOKTALARI VE KONTROLLER

Remote machine varsa OS envanter lookup yapılır.

OS türüne göre platform belirlenir.

Managed system zaten varsa, yeniden oluşturulmaz.

Functional account eşleşmesi domain + OS bilgisine göredir.

Managed account zaten varsa, yeniden oluşturulmaz.

User grubu varsa tekrar create edilmez ama her durumda smart rule role ataması yapılır.

Kullanıcı cache'te yoksa create edilir.

⚖️ 5. ROL ATAMA MEKANİZMASI

User Group oluşurken, SmartRuleAccess alanı doldurulur.

Ayrıca POST çağırısı ile şöyle bir istek yapılır:

POST /UserGroups/{group_id}/SmartRules/{smart_rule_id}/Roles
{
  "Roles": [{ "RoleID": "3" }],
  "AccessPolicyID": "5000"
}

💾 6. LOG ve HATA YÖNETİMİ

utils/logger.py üzerinden yapılır.

Her satır, hangi adımda başarılı/başarısız oldu loglanır.

log_message, log_error, log_debug_row gibi fonksiyonlar kullanılır.

🔎 7. GELECEK ADIMLAR (TASLAK)

UserGroupPermissions üzerinden detaylı yetkilendirme

ISA Release / AccountGroup linklemeleri

CSV ile çıktı üretimi ve raporlama

Web arayüzü ile tetikleme

Bu yapı modüler arasi bağımlılığı azaltır, yeniden kullanılabilirliği artırır ve test edilebilir yapıyı destekler. Her işlem kademeli ve ayrık yürütülür, hatalar izlenebilir şekilde loglanır.