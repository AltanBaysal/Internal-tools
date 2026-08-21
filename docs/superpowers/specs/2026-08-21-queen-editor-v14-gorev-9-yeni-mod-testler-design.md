# v14 · Görev 9 — Detayda Yeni mod seçicisi · **test turu**

**Kaynak:** [yol haritası v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) 9. madde —
[İstek 3](../plans/2026-08-20-queen-editor-istekler.md) ve
[fark listesi](../research/2026-08-20-queen-editor-tasarim-v4-farklari.md) 94, 95, 96.

## Sorun

Üç fark, tek form.

**94:** yeniden üretilen video hangi modda üretileceği sorulmadan kuyruğa giriyor. Formda "Yeni mod"
seçicisi duracak ve **varsayılanı bu videonun modu** olacak — kullanıcı yalnız prompt'u değiştirip
basarsa mod kendiliğinden korunacak. Mod değişince kutu vurgu rengine dönecek.

**95:** dizinin son karesinde "Sonrakine bağla" seçilebilecek, ama seçilince kutu kırmızıya dönecek,
altında *"Bu son kare — bağlanacak sonraki kare yok."* yazacak ve yeniden üret pasifleşecek.
*(Seçeneği baştan pasif yapmak da, basıldıktan sonra hata vermek de açıkça reddedildi.)*

**96:** düğmelerin altında moda göre değişen tek satır duracak —
*"Yeni bir kare açılır — P11_3 kopyası, loop video."*

Bugün `regenerate` modu hiç tanımıyor: 7. maddenin loop rozeti, yeniden üretilen bir loop videosunda
kayboluyor.

## Kararlar

### 1 · "Filmde sonraki kare" kuralı ortak eve taşınıyor

`queue_layer._frame_after` bugün özel. `regenerate` de aynı soruyu soracak, ve iki kopya iki cevap
demek. **`production_mode.frame_after(gallery, fid)`** oluyor.

Ev olarak `production_mode`, çünkü sorduğu şey bağlı modun kendi kuralı — *bir bağlı video nereye
varır* — ve iki çağıranın ikisi de o modülü zaten içe aktarıyor. `gallery_order` da bir adaydı;
orada durursa galeri sırası bilgisiyle "hedef üretilmiş olmalı" kuralı tek fonksiyonda karışırdı.

### 2 · Mod doğrulaması da oraya taşınıyor

`queue_layer` iki satırla doğruluyor: mod listede mi, ve standart olmayan bir mod video dışı bir
katmana verilmiş mi. `regenerate` aynı ikisini isteyecek.

**`production_mode.validate(mode, kind)`** ve **`production_mode.InvalidMode`**. İstisna da oraya
gidiyor, çünkü modlar hakkında ve artık iki kullanım durumu atıyor. `queue_layer` ve `routes` içe
aktarımlarını oradan yapıyor.

Kendi testi yok: iki kullanım durumunun testleri onu iki uçtan da geçiriyor, ve üçüncü bir test aynı
iki satırı üçüncü kez tarif ederdi.

### 3 · Hedefi sunucu buluyor, istemci göndermiyor

`regenerate` galeriyi zaten okuyor (`list_frames`, ilk satırı). Hedefi oradan buluyor. İstemcinin bir
kimlik göndermesi, aynı kuralın iki tarafta yaşaması olurdu.

### 4 · Bağlanacak kare yoksa sunucu reddediyor

Yeni bir istisna: **`NoNextFrame`** → 400.

Ekran bu isteği zaten göndermiyor; sunucu yine de reddediyor, çünkü alternatif `linkedTo: None`
taşıyan bir iş planlamak — o iş render'a gidip `MissingEndFrame` ile kırmızıya düşerdi ve mesajı
*"Bağlanacak karenin fotoğrafı yok: ?"* olurdu. Soru işareti, sunucunun bilebileceği bir şeyi
bilmemiş gibi yapmak demek.

Bu, tasarımın reddettiği "basıldıktan sonra hata" değil: ekranın kendi kuralı 6. kararda ve buton
oraya varmadan kapanıyor.

### 5 · Ekranın kapanma kuralı sunucununkiyle aynı soruyu soruyor

Tasarım yalnız **son kareyi** anıyor. Ama sunucunun kuralı `frame_after`: bir üstteki kare **var
ve üretilmiş** olmalı. Fotoğrafı henüz üretilmemiş bir sonraki kare, tasarımın hiç düşünmediği
ikinci bir durum.

Yalnız son kareye bakan bir ekran, o durumda isteği geçirir ve sunucu reddeder — yani tasarımın
reddettiği "basıldıktan sonra hata"nın ta kendisi olurdu. Bu yüzden ekran aynı iki koşula bakıyor ve
her birinin kendi cümlesi var:

| Durum | Cümle |
|---|---|
| Galerinin tepesindeki kare | `Bu son kare — bağlanacak sonraki kare yok.` |
| Sonraki karenin fotoğrafı yok | `Sonraki karenin fotoğrafı henüz üretilmedi.` |

İkincisi tasarımda yok; tasarımın kuralını anmadığı duruma uzatmak, o durumu sessizce hataya
bırakmaktan iyi.

### 5b · "Son kare" galerinin tepesidir

Film galeriyi ters okuyor (`export_summary.exportable`), yani galerinin **tepesi** filmin son
karesi. Detay sayfasının sayacı da orada `N / N` yazıyor — ikisi zaten aynı şeyi söylüyor.

### 6 · Seçici bir kutu, satır listesi değil

Panelinki satır listesi (4. madde). Buradaki `<select>` — fark 94 "kutu" diyor ve rengin dönmesinden
söz ediyor, ki bu bir kenarlık. Uygulamanın kendi açılır kutusu `wf-input` sınıflı bir `<select>`
(GeneratePanel'in Model satırı), aynısı kullanılıyor.

### 7 · Modun ismi ortak eve taşınıyor

6. maddede `MODE_WORDS` panelde doğmuştu, çünkü cümleyi kuran tek yer oradaydı. Şimdi ikinci bir yer
aynı ismi istiyor: *"…, loop video."*

**`production_modes.js`** `nounOf(mode, plain)` kazanıyor. Kuyruk cümlesi (`her video kendine
döner.`) panelde kalıyor — onu söyleyen hâlâ tek yer.

`plain` bir argüman, çünkü standart modun ismi katmanın kendi ismi: panelde `video` ya da `ses`,
detayda her zaman `video`.

### 8 · Blok yalnız video sekmesinde

Seçici, sebep satırı ve "ne doğacak" satırı — üçü de yalnız video sekmesinde. Foto ve ses
sekmelerinde form bugünkü gibi.

Sebebi: modu olan tek katman video. Fotoğrafın "ne doğacak" satırı için tasarımın bir cümlesi yok ve
uydurmak, tasarımı genişletmek değil tahmin etmek olurdu.

### 9 · Kopyalanan kare kimliğiyle anılıyor

*"P11_3 kopyası"* — uzantısız, yani kimlik. Kopyalanan şey kare, ve `regenerate` de kaynağı
kimliğiyle adlandırıyor.

## Yazılacak testler

**Ortak kural — `test_production_mode.py`**

1. `frame_after` bir üstteki kareyi veriyor.
2. Galerinin tepesinde `None`.
3. Sonraki kare üretilmemişse `None`.

**Yeniden üretim — `test_photo_usecases.py`**

4. Verilen mod planlanan işe yazılıyor.
5. Bağlı modda hedef de yazılıyor.
6. Tepedeki karede bağlı mod reddediliyor.
7. Bilinmeyen mod reddediliyor.
8. Video dışı katmana standart olmayan mod reddediliyor.
9. Mod verilmeyince işe mod yazılmıyor.

**Uç — `test_photo_routes.py`**

10. Bilinmeyen mod uçta 400 dönüyor — gövdedeki alanın kurala ulaştığının kanıtı.
11. Bağlanacak kare yoksa 400 dönüyor.

Modun **doğru** geçtiği uçta gözlenemiyor: uç testlerinin üretici haritasında video yok, iş kuyrukta
bekliyor ve kare hiçbir mod taşımıyor. Onu 4. ve 5. testler kullanım durumu seviyesinde tutuyor;
uçtan istenen tek şey alanın okunduğu.

**Ekran — `PhotoDetail.test.jsx`**

12. Video sekmesinde "Yeni mod" var ve bu videonun modunda açılıyor.
13. Modu yazılmamış video Standart'ta açılıyor.
14. Kutuya dokunulmadan basınca bu videonun modu gidiyor.
15. Değiştirilince yenisi gidiyor.
16. Değişince kutu vurgu rengine dönüyor.
17. Son karede bağla: kutu tehlike rengi, sebep görünüyor, buton pasif.
18. Sonraki karenin fotoğrafı yoksa aynı kapanma, kendi cümlesiyle.
19. Ortadaki bir karede bağla açık kalıyor.
20. Butonun altındaki satır ne doğacağını söylüyor.
21. Satır modu izliyor.
22. Foto sekmesinde ne kutu ne satır var.
23. Ses sekmesinde de yok.

## Bitti sayılır

Dört komutun dördü de koşuyor, kırmızılar commit ediliyor. Kaynak dosyalara bu turda dokunulmuyor.

Ön yüzde on kırmızı; on ikinin ikisi (foto ve ses sekmesinin yokluğu) doğuştan yeşil.

**Python tarafı bir sayı vermiyor:** `NoNextFrame` henüz yok, iki test modülü içe aktarılamıyor ve
pytest oturumu keserek geri kalan ~650 testi hiç koşturmuyor. Bunun bedeli gerçek ve turun
sonucuna yazılıyor. Alternatifi, istisnayı boş bir iskelet olarak kaynağa eklemekti — yani turun tek
kuralını çiğnemek ve uygulama turunun işini önden yapmak.
