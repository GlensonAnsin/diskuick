"""Turkish strings, in the order of i18n_keys.KEYS. Best-effort translation - please have a native speaker review."""
from i18n import register_seq

register_seq("tr", "Türkçe", (
    "Panel", "Oyunlar", "Araçlar", "Ayarlar",                                                          # 1-5
    "Siz oynarken sürücünüzü uyanık tutar",
    "Son takılmalar", "Sürücü sağlığı", "Gecikme kontrolü", "Kıyaslama ve otomatik ayar",
    "Davranış", "Görünüm", "Ne zaman çalışsın", "Varsayılan yoğunluk",                                 # 10-14
    "Canlı okuma gecikmesi",
    "Etkin", "Bekliyor", "Kapalı", "Hata", "Devre dışı", "Boşta", "Başlıyor",                          # 16-22
    "Pilde duraklatıldı",
    "Ayarlar'dan bir sürücü seçin", "Oyunlar sekmesinden oyun ekleyin",
    "Bir oyunun başlaması bekleniyor", "Oyun penceresinin odaklanması bekleniyor",
    "Uyanık tutuldu", "Oturumlar", "Kaydedilen takılmalar", "Etkin",                                   # 28-31
    "Henüz takılma kaydedilmedi.",
    "Her nokta o saniyedeki en yavaş okumadır. Kırmızı çizginin üstündeki sıçramalar takılmadır: sürücünün duraksadığı anlar.",
    "Canlı gecikmeyi görmek için bir oyun başlatın (veya “Her zaman açık” seçin).",
    "Veri bekleniyor...",
    "takılma", "şimdi", "Güncelleme var", "İndir",                                                     # 36-39
    "Yüklü oyunları algıla", "Taranıyor...", "Çalışan program ekle…",
    "veya bir program adı yazın, ör. oyun.exe",
    "Ekle", "Sürücü", "Yoğunluk", "Varsayılan",                                                        # 44-47
    "Henüz oyun yok.\nOtomatik bulmak için “Yüklü oyunları algıla”ya tıklayın.",
    "Çalışan bir program seçin", "Önce oyununuzu açın, sonra buradan seçin.",
    "Ara...", "Hiçbir şey bulunamadı", "Algılanan oyunlar", "Yeni oyun bulunamadı.",                   # 51-54
    "Steam, Epic Games ve GOG'a bakıldı. Yine de “Çalışan program ekle” ile ya da exe adını yazarak oyun ekleyebilirsiniz.",
    "Sürücünüzün uyanık tutulacağı oyunları seçin.",
    "Program adı en iyi tahmindir; bir oyun tetiklenmiyorsa kontrol edin.",
    "Tümünü seç", "Seçilenleri ekle", "Kapat",                                                         # 58-60
    "İncelenecek sürücü", "Yenile", "Yönetici olarak yeniden başlat", "Sürücü bilgisi okunuyor...",
    "Windows'un bu sürücü hakkında bildikleri, sade bir dille öneriler ile.",
    "Sağlık", "Sıcaklık", "Aşınma", "Açık kalma süresi", "yok",                                        # 66-70
    "{total} GB'ın {free} GB'ı boş",
    "Sürücü boşta kaldıktan sonra ilk okumanın ne kadar sürdüğünü, uyanık tutma ile ve onsuz ölçer, ardından işe yarayan en hafif ayarı seçer. Yaklaşık 2 dakika sürer. Bu sırada oyun çalıştırmayın.",
    "Otomatik ayarı çalıştır", "Hazırlanıyor…", "İptal", "İptal edildi.", "Test başarısız",            # 73-77
    "Uyanık tutma", "ort. ms", "p95 ms", "maks. ms", "Yok",                                            # 78-82
    "Uyanık tutma, boşta kalma takılmalarını giderir. Önerilen ayar: {p}.",
    "Bu sürücüde boşta kalma takılması algılanmadı; hızlı uyanıyor. Uyanık tutma muhtemelen burada işe yaramaz.",
    "Bu sürücü boşta kaldıktan sonra duraksıyor ancak uyanık tutma belirgin şekilde yardımcı olmadı. Neden başka yerde olabilir; Gecikme kontrolünü deneyin.",
    "{p} değerini varsayılan yap", "Kaydedildi.",                                                      # 86-87
    "Başlat'a bastıktan hemen sonra oyununuza geçin. 10 saniye sonra Diskuick 30 saniye boyunca gerçek diskinizi, işlemcinizi ve belleğinizi izler ve neyin sorunlu göründüğünü söyler.",
    "Gecikme kontrolünü başlat", "{s} sn içinde başlıyor: şimdi oyununuza geçin…", "Ölçülüyor… oynamaya devam edin",
    "Yalnızca gösterge amaçlıdır; ağ ölçülmez.",
    "Yalnızca oyun sırasında", "Her zaman açık",                                                       # 93-94
    "Oyunlarınızdan biri açılınca otomatik başlar, kapanınca durur. Oyunları Oyunlar sekmesinden ekleyin.",
    "Diskuick açık olduğu sürece sürekli çalışır. Basit ama boştayken bile sürücüyü meşgul tutar.",
    "Uyanık tutulacak sürücüler",
    "Sürücünün ne kadar dürtüleceği. Oyunlar bunu geçersiz kılabilir.",
    "Hafif", "Dengeli", "Ağır",                                                                        # 99-101
    "Küçük rastgele okumalar, saniyede yaklaşık 10. En düşük yük: önce bunu deneyin.",
    "Hafif ardışık okumalar, saniyede yaklaşık 20. Biraz daha fazlasına ihtiyaç duyan sürücüler için.",
    "Aralıksız okumalar. En güçlü etki, ancak sürücü hep meşgul.",
    "Okumalar arası saniye (gelişmiş)", "varsayılan",                                                  # 105-106
    "Pozitif bir sayı girin veya varsayılan için boş bırakın.",
    "Pilde duraklat", "Dizüstüler: fiş çekiliyken sürücüyü meşgul tutma.",
    "Yalnızca oyun odaktayken", "Oyundan Alt+Tab ile çıkınca duraklar.",
    "Oyun başlayınca bildir", "Küçük bir tepsi bildirimi.",
    "Windows ile başlat", "Oturum açılışında tepside sessizce çalışır.",
    "Tema", "Sistem", "Koyu", "Açık tema", "Dil",                                                      # 116-120
    "Güncellemeleri denetle",
    "Yalnızca depo adıyla iletişim kurulur; sizinle ilgili hiçbir şey gönderilmez.",
    "Bir sürüm deposu ayarlanana kadar güncelleme denetimi kapalıdır.",
    "Veri klasörünü aç", "Takılma günlüğünü aç",
    "Akıllı yoğunluk açık: seviyeyi sizin yerinize seçer. Kendiniz seçmek için kapatın.",
    "Akıllı",                                                                                          # 127
    "Hızlı tarama için yönetici olarak yeniden başlat",
    "Neyin yer kapladığını en büyükten başlayarak gösterir. Burada hiçbir şey değiştirilmez veya silinmez. Yönetici olarak çalışınca sürücünün dosya tablosunu doğrudan okur (WizTree gibi) ve saniyeler sürer; aksi halde klasörleri tek tek okur, bu bir iki dakika alabilir.",
    "{s} sn sürdü.", "Oyunu yeniden adlandır", "Şunun için gösterilecek ad:",                         # 130-132
    "Gecikme katmanı",
    "Sürücü uyanık tutulurken (bir oyun çalışıyor veya Her zaman açık) ekranın bir köşesinde küçük bir canlı gösterge. Oyuna asla dokunmayan ayrı bir penceredir ve pencereli ile kenarlıksız oyunların üzerinde görünür. Özel tam ekranın üzerinde görünemez (örneğin Battlefield 3): o oyunu kenarlıksız veya pencereli moda alın.",
    "Oyun çalışırken katmanı göster", "Konum", "Önizleme",                                           # 135-137
    "Sol üst", "Sağ üst", "Sol alt", "Sağ alt",
    "Şimdi güncelle", "İndiriliyor… %{p}", "Güncelleme başarısız", "Yeniden dene", "Şimdi denetle",    # 142-146
    "Denetleniyor…", "Güncelsiniz.", "Güncellemeler denetlenemedi.", "Güncelleme var: {v}",
    "Diskuick'i aç", "Çık", "{d}: sürücüsü uyanık tutuluyor",                                         # 151-153
    "Başlangıç ayarı değiştirilemedi",
    "Son oturumlar", "Sürücü müydü? Son oyun oturumlarınızın özeti.",
    "Henüz kayıtlı oturum yok. Bir oyun kapanınca rapor görünür.",
    "En kötü okuma", "takılma", "tepe", "ping",                                                        # 158-161
    "Gecikme işaretleri",
    "Bir oyun takıldığı anda Ctrl+Alt+L tuşlarına basın (veya tepsi menüsünü kullanın). Diskuick, o sırada bilgisayarın ne yaptığını kaydeder.",
    "Henüz gecikme işaretlenmedi.", "Gecikmeyi şimdi işaretle", "Gecikme işaretlendi", "Oturum bitti", # 162-167
    "Kaynak açmak için kapatıldı", "Akıllı yoğunluk",
    "Hafif ile başlar ve yalnızca sürücü takılmaya devam ettiği sürece kademeli artırır, sakinleşince geri indirir. Yukarıdaki seçimi yok sayar (bir oyunun kendi ayarı yine de geçerlidir).",
    "Sürücü uyarıları", "Oyun sürücüsü neredeyse dolduğunda veya artık sağlıklı olmadığında bana haber ver.", # 171-172
    "Klavye kısayolları",
    "Ctrl+Alt+L bir gecikme anını işaretler. Ctrl+Alt+O katmanı gösterir veya gizler.",
    "Sürücü uyanık tutulurken katmanı göster",
    "CPU ve GPU yükünü de göster", "FPS'i de göster",                                                  # 176-177
    "Diskuick.exe'nin yanında PresentMon.exe ve Diskuick'in yönetici olarak çalışması gerekir.",
    "Ağ denetimi (isteğe bağlı)",
    "Gecikmenin internetten kaynaklanıp kaynaklanmadığını kontrol eder. Genel bağlantınızı denetlemek için 1.1.1.1 yazın veya oynadığınız bir sunucunun adresini girin (:bağlantı noktası isteğe bağlıdır, varsayılan 443). Gecikme kontrolü sırasında (ve bir gecikmeyi işaretlediğinizde) Diskuick ping (sunucunun yanıt vermesi ne kadar sürüyor) ve paket kaybını (hiç ulaşmayan yanıtlar) ölçer; böylece ağ sorununu sürücü sorunundan ayırt edebilirsiniz. Yalnızca normal bir bağlantı açılır, saniyede birkaç kez, ve sizinle ilgili hiçbir şey gönderilmez. Kapalı tutmak için boş bırakın.",
    "Ana makine", "Bir ana makine adı veya adres girin, isteğe bağlı olarak :bağlantı noktasıyla.",
    "Oyun modu (isteğe bağlı)",
    "Oyunlarınızdan biri başladığında, bu programlardan nazikçe kapanmalarını ister (yine de kaydetmenizi isteyebilirler) ve oyun bitince yeniden açar. Hiçbir şey zorla kapatılmaz.",
    "Program seçilmedi.", "Kaldır", "Bu program korumalıdır ve kapatılamaz.",                           # 185-187
    "Sonra yeniden aç", "Disk", "Analiz edilecek sürücü", "Tara", "Durdur", "Durduruluyor...", "Yukarı", # 188-194
    "Ad", "Boyut", "Dosyalar", "Üst öğenin %'si", "Gezgin'de aç", "Bu klasörü burada aç",               # 195-200
    "Disk alanı çözümleyici",
    "Neyin yer kapladığını en büyükten başlayarak gösterir. Klasörleri tek tek okur, bu yüzden büyük bir sürücü bir iki dakika sürer. Burada hiçbir şey değiştirilmez veya silinmez.",
    "Başlamak için Tara'ya basın.", "Haritasını burada görmek için bir sürücüyü tarayın.",             # 203-204
    "{drive}: taranıyor ...", "{drive}: taranıyor: şu ana kadar {files} dosya, {size}",
    "{files} dosya ve {folders} klasörde {size} bulundu.", "Kullanılan sürücü: {used}.",
    "Erken durduruldu, bu yüzden kısmi.",
    "Bazı klasörler korumalıdır; dahil etmek için yönetici olarak çalıştırın.",
    "Dosya türleri", "Bu sürücüde en çok yeri hangi dosya türlerinin kapladığı.",                      # 211-212
    "Disk temizleme",
    "Yalnızca güvenli, yeniden oluşturulabilir artıkları siler: geçici dosyalar, önbellekler ve çökme raporları. Kendi dosyalarınıza asla dokunulmaz. İstediklerinizi işaretleyin, boyutları kontrol edin, sonra temizleyin.",
    "Boyutları denetle", "Boyutlar denetleniyor...", "Seçilenleri temizle", "Temizleniyor...",       # 215-218
    "Önce en az bir öğe işaretleyin.", "İşaretli öğeler yaklaşık {size} boşaltır.",
    "Geri Dönüşüm Kutusu kalıcı olarak boşaltılır.",
    "Şuralardan yaklaşık {size} kaldırılsın:\n\n{names}{note}\n\nDevam edilsin mi?",
    "{size} boşaltıldı ({files} dosya). Kullanımdaki öğeler atlandı.",
    "Geçici dosyalar", "Programların Temp klasörünüzde bıraktıkları.",                                # 224-225
    "Windows geçici dosyaları", "Windows'un kendi Temp klasörü. Hepsini temizlemek için yönetici olarak çalıştırın.",
    "Küçük resim önbelleği", "Gezgin, resim önizlemelerini gerektiğinde yeniden oluşturur.",
    "Çökme dökümleri ve hata raporları", "Çöken programlardan kalan tanılama dosyaları.",
    "Tarayıcı önbellekleri", "Chrome, Edge ve Brave önbellekleri. Siteler bir kez biraz daha yavaş yüklenir.",
    "Gölgelendirici önbellekleri", "GPU gölgelendirici önbellekleri. Yeniden oluşturulurken oyunlar bir sonraki başlangıçta kısa süre takılabilir.",
    "Geri Dönüşüm Kutusu", "Geri Dönüşüm Kutusu'ndakileri kalıcı olarak siler.",
    "Geri Dönüşüm Kutusu'na taşı", "klasör", "dosya",                                                  # 238-240
    "Bu {kind} Geri Dönüşüm Kutusu'na taşınsın mı?\n\n{path}\n{size}\n\nGeri Dönüşüm Kutusu'ndan geri yükleyebilirsiniz.",
    "Geri Dönüşüm Kutusu'na taşınıyor...",
    "Geri Dönüşüm Kutusu'na taşınamadı (kullanımda, korumalı veya iptal edildi).",
    "{size} Geri Dönüşüm Kutusu'na taşındı. Dosya türlerini yenilemek için yeniden tarayın.",
    "Hızlı tarama (NTFS dosya tablosu).",
    "Çok daha hızlı tarama için Diskuick'i yönetici olarak çalıştırın.",
    "Klasörler", "Boş",                                                                           # 246-247
    "ör. 1.1.1.1",
))
