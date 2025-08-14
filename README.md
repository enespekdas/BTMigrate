Manage System:
EXCEL1 - Device Inventory Report
EXCEL2 - Pam Accounts
Kullanılacak sütunlar(EXCEL1)
-> Hostname -> Tek bir hostname gelecek
-> IP -> Tek bir IP adresi gelecek
-> OS -> Platform seçimi
-> Domain -> functional account seçimi
 
Kullanılacak sütunlar(EXCEL2)
-> RemoteMachine -> RemoteMachine ";" ile parse edilerek bulunan her değer Excel1 içerisinde IP veya Hostname sütununda aranacak.
 
NOT: Kaybak veri excel2 olacak, excel2 üzerinde bulunan makinelerin bilgileri Excel1 üzerinden alınacak
NOT: IP, OS boş olanları ignore et
NOT: Excel içerisindeki tüm domain'ler için functional account yaratıldığını kontrol et
NOT: IP dolu fakat hostname boş ise nslookup ile hostname bakılır, var ise hostname kayıt edilir yok ise hostname alanına IP adresi girilir
NOT: IP bilgisinin IP formatına uygun olduğunu kontrol et, uygun değilse logla ve ignore et
NOT: Network cihazları için ayrı bir liste verilecek
 
 
Domain Manage Account:
EXCEL2 - Pam Accounts
Kullanılacak sütunlar
-> userName
-> remoteMachine
-> address -> içerisinde domain bilgisi var. Manage account yaratılırken domain seçiminde kullanılacak
-> safeName -> Smart group yaratalım eğer smart group zaten yaratıldıysa sadece içerisine ekleyelim. Aynı zamanda userGroup adı olacak
-> Password
 
NOT: userName alanı "PAM" ile başlıyor ise domain manage account. Öncelikle PAM ile başlayanları filtrele. 
NOT: userName, remoteMachine, address boş olanları ignore et ve logla
NOT: RemoteMachine içerisindeki bilgileri ";" noktalı virgül kullanarak split et
NOT: her remoteMachine için domain linkleme yapılacak. remoteMachine içerisindeki bir IP ya da hostanem manage system altında yoksa, logla ve ignore et
NOT: Manage account create etmeden önce tüm domainler için active directory manage system eklenmeli ve functional account seçilmeli.
NOT: PAMTEST ortamında script denemeleri sırasında auto manage mutlaka kapat veya yetkisiz bir functional account ver..!!
NOT: PAM PROD ortamında geçiş sırasında auto manage kapat ve manage by own password işaretle ve create sırasında şifre set et..!!
NOT: Script çalıştırmadan önce TEST ortamı database backup alalım. Kirli bir veride tekrar geri alabilmek adına. 
NOT: Testler için 3-5 tane manage system ve manage account silerek tekrar çalıştıralım ve sadece eksikleri yarattığını görelim.
 
 
Database Manage System(MSSQL):
EXCEL2 - Pam Accounts
Kullanılacak sütunlar
-> RemoteMachine  -> DNS ve IP olacak
NOT: RemoteMachine "thynet.thy.com" ile bitiyorsa MSSQL Manage System olarak ekle. Bu konu netleştirilecek.
NOT: MSSQL platformlarının hepsi 1433 kullandığını varsayıcaz. 
NOT: MSSQL sistemleri için ayrı bir liste verilecek
 
Database Manage System(ORACLE):
EXCEL2 - Pam Accounts
Kullanılacak sütunlar
-> address -> DNS ve IP olacak
-> port -> port
-> platformId -> platform tipi seçerken kullanacağız
 
NOT: sadece "PAM*" prefix ile başlayan hesaplar filtrelenecek
NOT: "port" bilgisi boş gelebilir. Port bilgisi boş gelenleri ignore et ve logla.
NOT: Excel üzerinde sadece hostname bilgisi var, bu hostname bilgisi nslookup ile IP bilgisi bakılarak manage system bu şekilde açılacak. 
NOT: "oracle*" prefix ile başlayan platform'lar için oracle seçilecek.
 
 
Database Manage Account(ORACLE):
EXCEL2 - Pam Accounts
Kullanılacak sütunlar
-> userName
-> database
-> port
-> address
 
NOT: "database" sütunu mutlaka dolu olmalı. Database hesaplarını filtrelerken bu alanların dolu olanlarını alacağız.
NOT: sadece "PAM*" prefix ile başlayan hesaplar filtrelenecek
 
 
Database Manage Account(MSSQL):
EXCEL2 - Pam Accounts
Kullanılacak sütunlar
-> RemoteMachine
-> userName
 
NOT: RemoteMachine içerisinde "thynet.thy.com" var ise buradaki account MSSQL link accountudur.
NOT: userName alanındaki AD heasabını manage system'e linkle
 
 
Local  Manage Account:
 
Kullanılacak sütunlar
-> userName
-> address
-> safeName -> Smart group yaratalım eğer smart group zaten yaratıldıysa sadece içerisine ekleyelim
 
NOT: userName, address boş olanları ignore et ve logla



----------------

Otomasyon Notlar : 
- THY De default autoapprove ataması yapmamış. 
- IP adresi bulup hostname bulamamasına ragmen ekleme yapmamış . 
- MSSQL Tespiti için IP ve host bulma işlemi tamamlandıktan sonra thynet.thy.com kontrolü yapılacak. 
- pam ile başlamayan ve address kolonunda thynet.thy.com olmayan hesapların tamamı lokal hesaptır. 
- username alanında pam içermiyorsa fakat address alanında thynet.thy.com var ise bunu domain hesap olarak alacağız. 
- PlatformID kısmında web30 geçiyorsa eğer bu thyweb30.crop  domaininde demektir. 
- PlatformID kısmında TCI geçiyorza -> tci.aero.local demektir. 
- Eğer OS bilgisi device envanterde bulunamadıysa bunu platformID kolonundan bulucaz. 
	- Eğer unix geçiyorsa Linux demektir. 
	- Eğer windows geçiyorsa windows demektir. 

---------------


pam ile başlamayan herşey local hesaptır. local olması için address kolonunda thynet.thy.com olmayacak . username alanı da pam ile başlamayacak . 


username alanında pam içermeyen , address kolonunda thynet.thy.com varsa domain hesap olarak alacağız. 



Address kolonunda bulunan ip adres veya hostname  bilgisini al device envanterden os bilgisini ve domain bilgisini bul. 
Eğer domain bilgisi bulunamadıysa bu makinenin ? 

E platform id kolonunda eğer web30 geçiyorsa web30 demektir. 

TCI geçiyorsa -> tci.aero.local

TEKNIK geçiyorsa -> teknik.thynet.thy.com -> thynet.thy.com dakini kullanabiliriz. 

WEB30 -> thyweb30.corp gibi bir 


OS bilgisini Devise envanterde bulamazsak PlatformID kolonundan bulucaz. 

unix geçiyorsa bu Linux makinedir. -> configden al , parametrik yap. 

windows geçiyorsa platform id de bu da windowstur. 
