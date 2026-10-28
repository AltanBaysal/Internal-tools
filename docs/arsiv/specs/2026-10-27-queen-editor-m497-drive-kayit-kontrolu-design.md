# Madde 497 · Drive'a kayıt olmayınca hata verip dursun — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-3),
497 · v11-3 · **Dal:** `feat/queen-editor-v11` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Fotoğraf, video ya da export Drive'a kaydedilirken Drive bağlı değilse ya da Drive doluysa, ekranda
bir hata çıkıyor ve o sırada süren iş duruyor. Hata, sistemin kendi sözünü taşıyor. Kaydı yapılamayan
iş ekranda bitmiş görünmüyor.

## Sebep

Kullanıcının gördüğü: fotoğraflar bitmiş göründü, bozuklar silindi, Colab kapatıldı; yeniden açılınca
fotoğrafların yarısı yoktu, bir kısmı "fotoğraf bulunamadı" diyen kırık kareydi. Hiç hata görülmedi.
O gün Drive doluydu, ve Colab sekmesinde de bir uyarı görülmedi *(kullanıcı, 27 Ekim)*.

**(a) — Colab'ın Drive bağlantısı kaydı önce kendi diskine alıyor, Google'a sonra gönderiyor. Sebep
bu.**

- Google'ın kendi Colab kodu, `google/colab/drive.py`: `flush_and_unmount`'un açıklaması *"Unmount
  Google Drive and flush any outstanding writes to it"*. DriveFS'i `--push_changes_and_quit` ile
  çalıştırıyor ve gönderemezse `ValueError('flush_and_unmount failed')` veriyor. Yani uygulamanın
  yazması döndükten sonra da Google'a gitmemiş yazmalar olabiliyor. Notebook bunu hiç çağırmıyor.
- Colab'ın SSS'si (research.google.com/colaboratory/faq.html, *Quota (storage)*): kota aşılınca
  işlemler G/Ç hatasıyla düşer ve bildirim Colab'ın arayüzünde çıkar. Kullanıcı Colab sekmesine değil
  tünelin sayfasına bakıyor.
- 472 bunu kabul edilen bir sınır olarak yazmıştı (v10-1, 8 — *"evet sıkıntı yok"*): "kaydedildi",
  bağlantının dosyanın tamamını kabul etmesi demek; Google'a yükleme sonra gelir.
- Kayıp yalnız yeniden açılışta göründü: oturumdaki galeri aynı bağlantıdan okuyordu ve dosyaları
  görüyordu. Kırık kareler de buna uyuyor: kayıt satırı (`photos.jsonl`) Drive'a ulaşmış, fotoğraf
  dosyası ulaşmamış.

**(b) — bozuk bir karenin silinmesi paylaşılan dosyayı götürüyor: sebep değil.** Üç silme
(`remove_frames`, `remove_layer`, `fix_photo`) silinecek dosyaları baştan `layers.files_to_unlink` ile
seçiyor, ve o başka bir (kare, katman) hâlâ tutuyorsa dosyaya dokunmuyor; `test_layers.py` bunu
deniyor. Silme dosyayı oturumun içinde götürür, kayıp o zaman aynı oturumda görünürdü.

**Yalnız Colab'da görülebilecek olan:** DriveFS'in `fsync`'i Google'a yüklemeyi bekliyor mu (472'nin
20 `order.json` denemesi bunu ölçecekti, hâlâ açık); dolu Drive'da yazmanın kendisi mi düşüyor yoksa
yalnız sonraki gönderim mi.

## Ne yapılır

Kullanıcının kararı *(27 Ekim — "şimdilik apiye geçmeyelim boşverelim onu sadece drive mounted mı diye
bakalım bir de drive dolu mu diye baklaım daha önce bunlardan patladık sadece")*: kayıttan önce iki
kontrol. **Biri, "Drive bağlı mı", 472'den beri var; bu madde yalnız ikincisini, "Drive'da yer var
mı"yı ekler.**

**Ne zaman:** her kayıttan önce, kaydın içinde *(kullanıcı, 27 Ekim — "1 den devam edleim o zaman")*.
Arka planda paralel bir bakış da konuşuldu; yer bakışı tek bir sistem çağrısı olduğu ve kaydı fark
edilir biçimde bekletmediği, arka plandaki bir bakış ise iki bakış arasındaki kayıtları kaçıracağı için
kullanıcı kayıttan önce bakmayı seçti.

### 1. Drive bağlı mı — zaten var (472)

`Storage._check` her işlemden önce kökü bir kez `stat` ediyor ve aygıt kimliğini ilk kullanımdakiyle
karşılaştırıyor. Hata, kökün yokluğu ya da başka bir aygıt işlemi `StorageError` ile, OS'un cümlesiyle
durduruyor; yazmalar kökü ve projeyi açmıyor. QueenAgent'ın 490'da `store.py`'ye koyduğu kontrol de
tam bu (`RootUnreachable`). Bu madde ona dokunmaz; testleri (`test_storage.py`, "the mount check")
zaten her açık yöntemi kapsıyor.

### 2. Drive'da yer var mı — yeni, `Storage`'ın her yazmasında

**Her yazma, istisnasız, önce yer sorar:** bir kayıt (`write_bytes`, `write_text`, `save_file`) ve
eklenen bir satır (`append_line`). Bağlantı kontrolünden sonra, hedefe bir şey yazılmadan önce
`_room` kökün boş yerini `shutil.disk_usage(kök).free` ile sorar ve yazılacak bayt sayısıyla
karşılaştırır. Boş yer azsa kapının kendi cümlesi, bağlantının bildirdiği iki sayıyla:

```
StorageError("Drive'da yer yok: <hedefin yolu> için <boyut> bayt gerekiyor, Drive'ın bildirdiği boş yer <boş> bayt")
```

Bu OS'un cümlesi değil, kapının; sayılar bağlantının. Hiçbir şey yazılmaz: geçici dosya açılmaz, var
olan hedef ve kayıt dosyası olduğu gibi kalır. `disk_usage`'ın kendisi düşerse o `OSError` olduğu gibi
yükselir; "yer var" sayılmaz.

Boyut:
- `write_bytes` / `write_text`: verinin bayt uzunluğu;
- `save_file`: kaynağın boyutu, kaynak bir kez açılıp açık dosyadan (`os.fstat`) okunur. Kaynak ya
  ffmpeg'in makinede kestiği bir parça, ya da export'un projeler kökünden kopyaladığı bir fotoğraf
  (`copy_photo`) — o da Drive bağlantısında; tek açılış, ona ikinci bir gidiş dönüş eklemez;
- `append_line`: satırın ve satır sonunun UTF-8 bayt uzunluğu.

| İş | Yazma | Kontrol |
|---|---|---|
| Fotoğraf, videonun ilk karesi, video, ses | `photo_store.save` → `write_bytes` | `_save` → `_room` |
| Export'un fotoğrafları, ayrı videoları, birleşik dosyası | `copy_photo` / `copy_video` / `copy_export` → `save_file` | `_save` → `_room` |
| `plan.json`, `order.json` ve öteki kayıtlar | `write_text` | `_save` → `_room` |
| `photos.jsonl`'in satırları (üretilen katman, düşen render, yazılan prompt, silme, kopya kare), `chats.jsonl` | `append_line` | `_room` |

Satırlar da kontrol edilir, çünkü çoğu bir dosya kaydının ardından gelmiyor: düşen bir renderin
satırı, yazılan bir prompt, kopya karenin satırları ve her sohbet satırı kendi başına yazılıyor.
Üretilen bir katmanın satırı ise dosyasından sonra yazılıyor; dosya reddedilince satır hiç yazılmaz —
kullanıcının kırık kareleri bu sırayla bir daha olmaz.

**DriveFS'in bildirdiği boş yer — doğrulanmadı.** Colab'da Drive bağlantısının boş yerinin hesabın
Drive kotasından kalan olduğu varsayılıyor; `disk_usage` onu okur. Bunun böyle olduğunu ve dolu bir
Drive'da `free`'nin gerçekten 0'a indiğini yalnız kullanıcının Colab denemesi gösterebilir.

### 3. Ekrana ve işin durmasına giden yol — bugünkü

Yeni bir şey yok, testlerle sabitlenir:

- **Fotoğraf ve video:** `run_loop` kaydı denemelerin `try`'ının dışında yapıyor. Yükselen
  `StorageError` `job()`'dan çıkar, `PhotoRunner._run` onu `{"status": "error", "error": "<cümle>"}`
  yapar, `QueuePanel` durmuş kuyruğun kartında cümleyi gösterir. Satır kayıttan sonra yazıldığı için
  reddedilen karenin `done` satırı yok: kare ekranda bitmiş görünmez, sırada kalır, ve yeniden
  başlatınca yeniden çizilir *("normal hata davranışı neyse o")*.
- **Export:** `run_export`'un hatası `ExportRunner._run`'da `{"state": "error", "error": "<cümle>"}`
  olur, `ExportScreen` gösterir; yarım export bugünkü gibi geri alınır (474).
- **Ekrandan yapılan kayıtlar** (sıra, ayarlar): `web/app.py`'nin `OSError` işleyicisi → `503
  {"error": "<cümle>"}`; `api.js` bu cümleyi hatanın `message`'ı yapar.

Durmuş kuyruğun hatası yalnız sıra panelinde görünür, başka bir yerde değil *(kullanıcı, 27 Ekim —
"sıra panelinde görünüyorsa yeter hata")*; bu madde ekrana bir uyarı şeridi eklemez.

### 4. Frontend — Kuyruğa ekle sunucunun cümlesini gösterir

QA'nın gördüğü: Kuyruğa ekle önce ayarları yazar (`PUT …/settings`); Drive dolu olunca sunucu `503
{"error": "Drive'da yer yok: …settings.json için 107 bayt gerekiyor, … 10 bayt"}` döndü, ama
`GeneratePanel` yalnız sabit *"Kuyruğa eklenemedi — tekrar dene"* yazdı. Cümle `error` olarak panele
geliyordu (`ProjectScreen`'in `saveError`'ı, ya da `useGeneration`'ın `failureText`'i), panel onu
kullanmıyordu. Madde *"ekran sunucunun cümlesini gösterir, sabit bir metin değil"* diyor.

Düzeltme: reddedilen bir Kuyruğa ekle, kare sayfasının reddedilen istekleri gibi, paylaşılan
`StatusErrorCard`'la çizilir — başlıkta ne denendiği (*"Kuyruğa eklenemedi"*), altında sunucunun kendi
sözü, katlanmış ve kopyalanabilir. Yeni bir yardımcı yok.

Cümle reddin kendisinde tutulur. `useGeneration`'ın `error`'u durum yoklamasıyla ortak: başarılı bir
yoklama onu siler. Bu projenin bir koşusu sürerken kare isteğinin kendisi reddedilirse (örneğin dolu
Drive `plan.json`'a eklemeyi reddeder), kart bir yoklamada cümlesini kaybederdi. Bu yüzden her ret
kendi sözünü getirir: `generate`'in reddi de, ayarların yazmasının reddi de (`ProjectScreen`'in
`handleGenerate`'i) `null` yerine `{ error: failureText(err) }` ile döner. Panelin `refused`'ı `null`
ya da o söz; kart yalnız ondan çizilir (`raw={refused}`). `saveError` öteki paneller için kalır.

Kart, kare isteğinin reddinde cümleyle birlikte `failureText`'in kanıt satırlarını da taşıdığı için
uzun. Prompt kutusu altındakine yer veren bir esnek kutu (`minHeight: 0`), ve QA 1280×720'de kartın
onu 22 px'e indirdiğini, tek satırını kestiğini gördü. Kutunun bloğuna bir taban konur (`PROMPT_FLOOR`,
96 px: etiket ve kutunun yaklaşık üç satırı); daha dar ekranda panel kayar, ki zaten kayıyor
(`SidePanel`'in `PANEL`'i, `overflowY: auto`). Bu bir yerleşim kuralı ve jsdom yerleşim hesaplamadığı
için testle görülmez; Playwright'ta 1280×720'de görülür.

Öteki ekran yazmalarına bakıldı; sunucunun cümlesini sabit bir metinle değiştiren başka yer yok:

- `useGeneration`'ın bütün yazmaları (sıra, silme, kopya, katman, yeniden üret, tekrar dene, durdur,
  boşalt) `setError(failureText(err))`; `LayerPanel` `error`'u ve kendi `refused`'ını olduğu gibi,
  `QueuePanel` "İstek reddedildi" başlığının altında `raw` olarak, kare sayfası "Kare silinemedi" gibi
  başlıkların altında `raw` olarak gösteriyor.
- `ExportScreen` "Export başarısız"ın altında koşunun `error`'unu, `ReferencePanel`, `NameModal`,
  `ProjectsScreen` `err.message`'ı gösteriyor.
- Sessizce yutulanlar (`.catch(() => {})`) okumalar ve export'tan çıkarken gönderilen iptal; sonuncusu
  bilerek (*"a refused cancel must not trap the user here"*). Bu maddenin konusu değiller.

`dist` yeniden kurulur.

## Bu maddenin yakalamadığı

**DriveFS'in arka plan gönderiminin düşmesi.** Kontroller kayıttan önce yapılır: kayıt anında bağlantı
kopuk ya da Drive dolu değilse, kayıt "kaydedildi" der, ve dosyayı Google'a sonra gönderen DriveFS'in
düşmesi uygulamaya hiç ulaşmaz. Bunu görmek için her kayıttan sonra dosyanın Google'a ulaştığını
Drive API'ye sormak gerekiyordu; kullanıcı 27 Ekim'de istemedi, v10'da (472, 9) da reddetmişti. Somut
olarak:

- Drive dolarken yolda olan baytlar: DriveFS'in bildirdiği boş yer henüz gönderilmemiş yazmaları
  düşüyor mu, bilinmiyor. Düşmüyorsa, Drive'ın dolduğu sıradaki birkaç kayıt kontrolden geçip sonra
  gönderilemeyebilir.
- Gönderim bitmeden kapatılan Colab.

## Maliyet

Koddan sayıldı, ölçülmedi. Colab'da her dosya sistemi çağrısı DriveFS'e bir gidiş dönüş.

| İşlem | Bugün | Sonra |
|---|---|---|
| Bir kayıt (`write_bytes` / `write_text`) | stat + `mkstemp` + `fsync` + `replace` = 4 | + `statvfs` = 5 |
| `save_file` | kök stat + kaynağın açılışı + `mkstemp` + `fsync` + `replace` | + `statvfs`; boyut zaten açık olan kaynaktan (`fstat`) okunur, kaynağa ikinci bir açılış ya da yol stat'ı yok — `copy_photo`'da kaynak Drive'da olduğu için bu önemli |
| `append_line` | stat + `open` + `fsync` = 3 | + `statvfs` = 4 |
| Okumalar, listeler, silmeler | aynı | aynı |

Yazma başına O(1); proje, kare ve dosya sayısından bağımsız. Bir fotoğraf turu bir kayıt + bir satır
olduğu için turda iki çağrı artar.

## Ne kaybolabilir, ne bozulabilir

- **Yer yokken kayıt ya da satır:** hiçbir şey yazılmaz, eski dosya ve kayıt dosyası yerinde kalır;
  kare sırada kalır.
- **Toplu üretimde (batch) ikinci resim reddedilirse:** birincinin dosyası ve satırı yazılmıştır; o
  bitmiştir. Ötekiler sırada kalır.
- **Export ortasında:** bugünkü düşen export gibi, yalnız kendi yazdıklarını geri alır.
- **Aynı anda iki kayıt:** ikisi de boş yeri ayrı sorar; ikisinin toplamı sığmıyorsa ikisi de
  geçebilir. Arada kalan, yukarıdaki "yolda olan baytlar"la aynı sınır.
- **Sır, URL'den gelen ad:** bu madde ikisine de dokunmuyor; ad sınırı bugünkü gibi `_file`'da.

## Bitti sayılır

1. Testler gösteriyor ki:
   - Drive'ın bildirdiği boş yer yazılacaktan azsa `write_bytes`, `write_text`, `save_file` ve
     `append_line` `StorageError` ile, iki sayıyı söyleyerek duruyor; hedef ya da kayıt dosyası
     olduğu gibi kalıyor ve geçici dosya kalmıyor;
   - boş yer tam yetiyorsa yazma yapılıyor;
   - boş yeri sormanın kendisi düşerse o hata yükseliyor ve hiçbir şey yazılmıyor;
   - fotoğrafın ve videonun kaydı reddedilince kuyruk `error` durumuna kapının cümlesiyle, olduğu
     gibi geçiyor, ve karenin `done` satırı yazılmıyor;
   - export'un Drive'a kaydı reddedilince export `error` durumuna cümleyle geçiyor ve yarım export
     geri alınıyor;
   - Kuyruğa ekle reddedilince panel "Kuyruğa eklenemedi" başlığının altında sunucunun cümlesini
     gösteriyor, "tekrar dene" yazmıyor; ayarların yazması Drive'ca reddedilince cümle ekranda ve
     kareler gönderilmiyor; reddedilen kare isteğinin cümlesi, yoklama ortak hatayı silince de
     kartta kalıyor.
2. `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend` yeşil; `dist`
   yeniden kurulmuş.
3. **Colab denemesi — kullanıcının, koşunun sonunda:**
   - Bir hücrede `import shutil; shutil.disk_usage("/content/drive/MyDrive")`: `total` Drive'ın
     kotası, `free` Drive'ın web'inde görülen boş yer olmalı.
   - Drive'ı kaydın sığmayacağı kadar doldurup (ya da boş yeri az bir hesapla) bir fotoğraf
     üretmek: kuyruk "Drive'da yer yok: …" ile duruyor, kare bitmiş görünmüyor.
   - Uygulama açıkken `from google.colab import drive; drive.flush_and_unmount()`, sonra bir üretim
     ya da export: ekranda "Kök klasöre ulaşılamıyor: …" çıkıyor ve iş duruyor.
