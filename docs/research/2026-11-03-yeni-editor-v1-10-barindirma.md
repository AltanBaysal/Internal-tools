# Yeni editör — 10. Barındırma

Core'un Colab'da nasıl açıldığı, nasıl ulaşıldığı.

## Başka adımlarda kararlaştırılanlar

- **Notebook başlatıcıdır:** üreticileri (ComfyUI ve eklentileri) kurar, core'u başlatır. Tüneli
  yalnız Pro'da açar ve adresini basar; ücretsiz katmanda tünel açmaz. Core ayarlarını ortamdan okur. Modelleri core indirir (bkz.
  Modeller).
- **Drive'a izin:** Colab'ın giriş penceresiyle, Colab'ı açan hesabın izni; token saklanmaz (4. adım).
- **ComfyUI'yi core başlatır** ve gerekince yeniden başlatır (7. adım).
- **Tünel:** Cloudflare'ın hızlı tüneli, queen-editor'daki gibi; ~100 sn sessiz kalan isteği keser,
  bu yüzden `/wait` en çok 90 sn bekler (7. adım).
- **Birden çok Colab** aynı anda, aynı hesapla; her biri kendi core'u ve UI'ı (4., 9. adım).
- **MCP adaptörü kullanıcının bilgisayarında** çalışır (8. adım).

## Erişim

Core'un adresinde şifre yoktur, queen-editor'daki gibi. Adres rastgeledir ve bir oturum sürer;
adresi bilen her şeyi yapabilir. Risk bilerek kabul edilir: silinen dosyalar Drive'ın çöp kutusuna
gider, kalıcı silinmez.

## Harness'lar

v1'de adaptör Claude Code için kurulur ve onunla denenir: geliştirirken adaptörü onunla
deneyebiliriz. DeepSeek harness'ı koşunun son maddesinde, kullanıcıyla birlikte ayarlanır: hangi
harness olduğu, anahtarı, adaptörü sohbetin klasöründe başlatıp başlatmadığı, resim parçasını modele
verip vermediği (kullanıcı, 6 Kasım).

**Core'un adresi** sohbetin klasöründeki `.queen-studio.json` dosyasındadır (`{"core": "<adres>"}`).
Kullanıcı Colab'ın adresini sohbete yapıştırır, agent dosyaya yazar. Adaptör adresi her listede bu
dosyadan okur; adres değişince adaptörü yeniden başlatmak gerekmez. Her Colab için ayrı klasörde
ayrı bir sohbet açılır; her klasörün kendi dosyası olduğu için sohbetler karışmaz. Bu, harness'ın
adaptörü sohbetin klasöründe başlatmasına dayanır: Claude Code'da yapımda doğrulanacak.

Resim alamayan bir harness'ta adaptör resim göndermez ve bunu söyler; resmi metne çevirmez (8. adım).

## Modeller

- **Nerede:** Colab'ın diskinde, queen-editor'daki gibi; Colab kapanınca silinir, her Colab kendi
  diskine indirir.
- **Kim indirir:** Agent bir modeli `POST /models/{id}/download` ile indirtir; bunu önceden de
  yapabilir (ör. fotoğraflar üretilirken videonun modeli) (kullanıcı, 5 Kasım — "agent indirmeyi
  seçsin böylece önceden hazırlık bile yapabilir"). Modeli kurulu olmayan ve inmeyen bir iş
  verilemez: hata modelin kurulu olmadığını söyler, hint indirme isteğini gösterir (kullanıcı, 5
  Kasım — "hata versin model yok indir diye"). Model inerken verilen iş kabul edilir; sırası gelince
  model inmemişse kuyruk "model iniyor" der ve bekler. Notebook model indirmez ve model seçimi
  sunmaz; bütün modelleri agent indirtir.
- **Yalnız ana model seçilir:** agent ana modeli indirtir; o modelin LoRA'ları ve yardımcı dosyaları
  onunla birlikte iner, çünkü küçüktürler (kullanıcı, 5 Kasım — "loralar direkt insin sadece ana
  model seçilsin loralar çok küçük çünkü").
- **Ekran kartı:** model bu Colab'ın kartında çalışmıyorsa indirme isteği reddedilir; hata bu
  Colab'ın kartını ve modelin çalıştığı kartları söyler (kullanıcı, 5 Kasım — "gidip T4'e H3
  indirmeyelim"). Hangi kartın hangi modeli kaldırdığı queen-editor'daki ölçümlerden ya da Colab'daki
  denemelerden gelir.
- **`GET /models`** indirilebilecek her ana modeli gösterir: ne olduğunu, boyutunu, hangi ekran
  kartlarında çalıştığını; yanında kurulu, iniyor (yüzdesiyle), inemedi (hatasıyla) ya da kurulu
  değil yazar. Agent
  inmesini `GET /models/{id}/wait` ile bekler.
- **İnemezse:** indirme queen-editor'daki gibi 3 kez denenir; olmazsa `GET /models` modeli
  "inemedi" gösterir, kaynağın ya da aracın söylediği hatayla. Sırası gelen işin modeli inemediyse
  kuyruk kendiliğinden durur ve nedenini söyler; işler bekler, kaybolmaz. Agent indirmeyi yeniden
  ister, sonra kuyruğu sürdürür (kullanıcı, 5 Kasım). Hangi modelin hangi dosyalardan, nereden indiği core'daki bir listededir;
  bugün queen-editor'da notebook'tadır.
- **Şifreler:** Hugging Face token'ı ve Civitai cookie'si Colab Secrets'tadır. Core Secrets'ı
  okuyamaz (Secrets yalnız notebook'un kendisine cevap verir); notebook onları açılışta core'a
  ortamdan verir.
- **Süreler:** H3 ~37 GB, ~11 dk; Krea 2 ~20 GB, ~6 dk; bir fotoğraf checkpoint'i ~7 GB, ~2 dk;
  hepsi ~74 GB. Colab'ın diski 200 GB'ın üstündedir; modeller ve 10 GB'lık önbellek sığar.
- **ComfyUI** çalışırken inen dosyayı yeniden başlamadan görür.

## Log

- Core log'u Colab'ın diskine yazar; notebook'un çıktısında da görünür. İçinde: her işin ayrıntılı
  süreleri (üretim, Drive'dan indirme, Drive'a yükleme, toplam; 7. adım) ve hataların ayrıntısı.
- 5 dakikada bir ve core kapanırken, o ana kadarki kısım Drive'a yeni bir dosya olarak gider; yeni
  satır yoksa gitmez:
  `logs/<YYYY-MM-DD HH-MM> <core kimliği>/001.log, 002.log …`. Drive bir dosyanın sonuna eklemeye
  izin vermediği için her gönderim yeni bir parçadır.
- Colab beklenmedik kapanırsa en çok son 5 dakika kaybolur. Bedeli 5 dakikada bir yazma.
- Core log'ları hiç silmez; kullanıcı siler.

## Colab'da ölçülecekler

Drive'ınkiler yapımın başında, ComfyUI'ninkiler başlatıcı yazılınca denenir; sonuç tutmazsa ilgili
adım yeniden açılır.

- **Hangi Colab:** testler ve ölçümler Colab'ın ücretsiz katmanında (T4), Google'ın Colab CLI'ıyla; bir test ya da ölçüm gerektirdiği
  her an, belli noktalarla sınırlı değil. Ücretli katman testte kullanılmaz. Bu testlerde MCP
  adaptörü Colab makinesinin içinde, core'a karşı çalışır.
  Video modelleri T4'e sığmaz: video üretimi sahte ComfyUI'ye karşı test edilir, gerçek videoyu
  kullanıcı sonda Pro'da dener (12. adım).
- **Drive'ın belgelenmemiş davranışları:** 4. adımın "Ölçülmemiş varsayımlar" tablosu, deneyleriyle
  (kimlikle okumanın güncelliği, içerik ve etiketin birlikte yazılması, listenin gecikmesi ve
  sayfaları, ayrılmış kimlikler, eski sürümler ve kota, dört Colab'ın hız sınırı, çağrı süreleri).
  Bu makineden, ayrı bir deneme Google hesabıyla; hesabın token'ı depoda durmaz. Bir kez de Colab'ın
  ücretsiz katmanında.
- **Krea 2 T4'e sığıyor mu.**
- **Model geçişi:** fotoğraf ile video arasında geçişin 10–15 sn sürdüğü (7. adım). Video modeli T4'e
  sığmadığı için kullanıcının Pro'daki son denemesinde ölçülür.
- **ComfyUI'nin açılması:** ~90 sn (7. adım); core'un beklediği süre buna göre.
- **Bellek:** ComfyUI çalışırken core'a ne kadar RAM kaldığı; 4. adımdaki 1 GB'lık proje sınırı buna
  göre.
- **Çalışırken inen model:** SAM yükleyicisinin ve DaSiWa'nın LoRA yükleyicisinin, ComfyUI çalışırken
  inen dosyayı yeniden başlamadan gördüğü.
- **Üretim sırasında indirme:** arkada model inerken üretim süresinin ne kadar yavaşladığı; T4'te
  testte, A100'de kullanıcının Pro'daki son denemesinde.
