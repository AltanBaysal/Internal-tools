# Madde 433 · ComfyUI cevap vermeyince: hücre kendi ComfyUI'sine bakar, uygulama hatayı basıp bekleyerek yeniden dener — tasarım

**Tarih:** 8 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
433 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Kod için hiçbir şey: ne kadar bekleneceği ve neyin bekleneceği 8 Ekim'de, koşu sırasında Claude
tarafından kararlaştırıldı *(aşağıda)*. Kullanıcı roadmap bitince Colab'da dener.

## Ne, neden

Kullanıcı, 8 Ekim: *"comfy içidne evet başarıl diyor collabte sonra başlamıyor o probleme sahibiz
buan bir bak ama collbat hata olmadığı için queen editorde görüyoruz o da hata verirse bir log bassin
yeniden denesin"*. Colab'daki ComfyUI hücresi "hazır" diyor, ama ComfyUI ayağa kalkmıyor. Sorun ancak
Queen Editor'de, kuyruğun kırmızı kartında görünüyor: `ComfyUI'ye bağlanılamadı —
http://127.0.0.1:8188`.

### Uygulamada bugün

ComfyUI'ye giden her istek `ComfyClient._send`'den geçer. `requests` bir `ConnectionError` atarsa
`_send` onu `ComfyUnreachable`'a çevirir (madde 230). Üretim döngüsü `run_loop.make_job` düşen bir
denemede `attempts += 1` yapar ve hemen `continue` eder; arada bekleme yok. 127.0.0.1:8188'de kimse
dinlemiyorsa bağlantı anında reddedilir, ve üç deneme bir saniyenin çok altında biter. Başlamakta olan
bir ComfyUI'yi bekleyemez — hücre ona 90 sn veriyor. Yeniden deneme ancak ComfyUI aynı saniye içinde
geri gelirse işe yarar.

**Maddenin cümlesine bir düzeltme.** Bağlantının kendi hatası kartta var. Madde 230'dan beri kırmızı
kartın katlanan kutusunda şunlar duruyor: `ComfyUI'ye bağlanılamadı — <adres>`, altında `requests`'in
kendi cümlesi, sonra `comfyui.log`'un son 30 satırı. Ama bu yalnız üçüncü denemenin hatası. Eksik
olan iki şey var:

- Sunucunun canlı log'u, yani Flask hücresinin *Canlı log*'u: oraya hiçbir denemenin hatası düşmüyor.
- İlk iki deneme: onların hatası hiçbir yere basılmıyor.

### Hücrede bugün

ComfyUI hücresi sırayla şunu yapar:

1. `pkill -f 'python main.py'`, sonra 2 sn bekler.
2. Yeni ComfyUI'yi başlatır.
3. 90 sn boyunca 2 sn'de bir `/system_stats`'a bakar, ve ilk cevapta "hazır" der.
4. 90 sn'de cevap gelmezse log'un son 30 satırını basar ve `RuntimeError` atar.

Ama hücrenin baktığı şey port, süreç değil:

- **Başlattığı süreci (`proc`) hiç sormuyor.** Portta cevap veren her ComfyUI "hazır" dedirtir; 2 sn
  içinde kapanmamış eski bir ComfyUI da. O durumda yenisi 8188'i alamaz ve kapanır. Eski ComfyUI da
  kapanınca portta kimse kalmaz, ama hücre "hazır" demiştir.
- **Başlattığı süreç açılırken kapanırsa bunu görmez.** 90 sn'yi doldurur, ancak ondan sonra düşer.
- **Son bakışın hatasını yutuyor** (`except Exception: pass`). Hücrenin hatası, portun ne dediğini
  söylemiyor.

İlk incelemenin bulduğu kusur kodda doğrulandı: hücre, kendisinin başlatmadığı bir ComfyUI için de
"hazır" diyebiliyor. Kullanıcının yaşadığı hatanın sebebi bu mu, gösterilmedi. Kusurun "hazır"
dedirtmesi için eski sürecin SIGTERM'den sonra 2 sn'den uzun süre HTTP'ye cevap vermeye devam etmesi
gerekir. Python'un varsayılanında SIGTERM süreci hemen bitirir, ve ölmekte olan bir süreç cevap veremez.
Eski sürecin bu kadar dayandığını gösteren bir şey elde yok. Madde 230'un adayları da hâlâ açık:
çöküş, OOM, Manager'ın yeniden başlatması. Bu madde sebebi kapatmıyor, görünür kılıyor. Hücre kendi
sürecine bakar, ve uygulama her düşen denemeyi canlı log'a basar.

## Olacak

### 1. Queen Editor: her düşen deneme canlı log'a basılır; ComfyUI cevap vermediyse 45 sn sonra yeniden denenir

**Her düşen deneme**, sebebi ne olursa olsun, sunucunun canlı log'una basılır. Bu, `⏱` satırının
düştüğü yerdir. Basılan iki parça var:

- Bir satır olgu: katmanın adı, kaçıncı deneme olduğu, ve ne zaman yeniden deneneceği.
- Altında **atılan hata**: türü ve mesajının tamamı, `Tür: mesaj` biçiminde.

`ComfyUnreachable` için mesajın tamamı şunları taşır: adres, `requests`'in kendi cümlesi ve
`comfyui.log`'un son 30 satırı.

```
⚠ 3_a.png · deneme 1/3 düştü — 45 sn sonra yeniden denenecek
ComfyUnreachable: ComfyUI'ye bağlanılamadı — http://127.0.0.1:8188
HTTPConnectionPool(host='127.0.0.1', port=8188): Max retries exceeded with url: /prompt (Caused by NewConnectionError('…: Failed to establish a new connection: [Errno 111] Connection refused'))
--- comfyui.log · son 30 satır ---
…
```

Satırın sonu duruma göre değişir:

- Beklemesiz bir yeniden denemede: `— yeniden deneniyor`.
- Üçüncü denemede: yalnız `⚠ 3_a.png · deneme 3/3 düştü`. Arkasından ne olduğunu kart söyler: ya
  kuyruk durur, ya kare kırmızı olur.

Durdur'la kesilen bir render düşüş değildir. Bugünkü gibi `paused` olur, ve satır basılmaz.

**Bekleme yalnız ComfyUI cevap vermediyse ya da cevap verirken bozulduysa** olur. Bu üç durum var:

- ComfyUI'ye bağlanılamadı (`ComfyUnreachable`). Süresinde kurulamayan bağlantı da buna girer:
  `requests`'in `ConnectTimeout`'u bir `ConnectionError`'dır.
- ComfyUI bir isteğe **HTTP 5xx** döndü.
- ComfyUI bir isteğe süresi içinde cevap vermedi (`requests`'in `ReadTimeout`'u).

Bu durumlarda her yeniden denemeden önce **45 sn** beklenir, sonuncudan sonra beklenmez. Üç deneme
böylece 90 sn'ye yayılır; bu, hücrenin başlamakta olan bir ComfyUI'ye verdiği süredir. Claude
önerdi ve koşu sırasında 8 Ekim'de seçti. Kullanıcı beklenmedi *(kullanıcı, 8 Ekim — "roadmpş sonuna
kdar koş benş bekleme")*.

**Bugünkü gibi beklemeden yeniden denenenler:**

- ComfyUI'nin düştü dediği render (`ComfyExecutionError`).
- ComfyUI'nin bir isteğe verdiği **4xx** cevabı, örneğin reddettiği bir grafik. ComfyUI, listesinde
  olmayan bir model için `POST /prompt`'a 400 döner. Beklemek bu cevabı değiştirmez.
- `node_errors`.
- **Render süresinin dolması.** Burada ComfyUI her `/history` bakışına cevap verdi; yalnız prompt
  süresinde bitmedi.
- Prompt yazarının hatası. DeepSeek'in kutusu zaten 5 kez dener (madde 416).
- MMAudio'nun, ffmpeg'in ve Drive'ın hataları.

**Durdur beklemeyi keser.** Bekleme saniye saniye yapılır, ve her saniyede durdurma isteğine bakılır.
Basılınca döngü bugünkü gibi `paused` ile durur, ve iş borçlu kalır.

**Kart değişmez.** Üçüncü denemeden sonra durma cümlesi ve kutusu bugünkü gibidir. Mesajların metni de
değişmez. HTTP hatası ve isteğin zaman aşımı, işaretlenebilsin diye ComfyUI servisinin kendi türlerine
sarılır (`ComfyHttpError`, `ComfyTimeout`), ama metinleri kelimesi kelimesine aynı kalır.

**İşaret, `frame_level` gibi:** ComfyUI servisi kendi hatasını `no_answer` ile işaretler. Döngü bunu
`getattr` ile okur, böylece domain servisi import etmez. Başka hiçbir şey işaretlenmez; bekleme bu
yüzden ComfyUI'ye dardır.

### 2. Colab: ComfyUI hücresi kendi başlattığı ComfyUI'ye bakar

Hücrenin kodu `colab/comfy.py`'ye taşınır: `start_comfy(root, port, log_path)`. Amaç pytest altında
koşabilmesi; madde 314'ün `install_node`'u da böyle taşındı. Hücre `start_comfy`'yi çağırır, ve
import ortak yardımcılar hücresinde yapılır. Modülde yalnız başlatma ve bakış var.

1. **Önce eski ComfyUI gider ve port boşalır.**
   - `pkill -TERM -f "python main.py"` gönderilir.
   - Sonra saniyede bir porta bağlanılır, en çok 30 sn. Port yalnız bağlantı **reddedilince** boş
     sayılır.
   - Port boşalmazsa `pkill -KILL` gönderilir, ve 30 sn daha beklenir.
   - Yine boşalmazsa hücre, yeni ComfyUI başlatılmadan düşer:
     `❌ 8188 portu 60 sn sonra hâlâ bağlantı kabul ediyor — yeni ComfyUI bu portu alamaz`.

   Neden: port boşken başlatılan ComfyUI'den başka kimse orada cevap veremez. Log dosyası da, eski
   süreç hâlâ içine yazarken baştan açılmamış olur. İlk açılışta ortada eski bir ComfyUI yoktur;
   bağlantı hemen reddedilir, ve beklenmez.
2. **ComfyUI başlar.** Komut bugünküyle aynı (`python main.py --listen 127.0.0.1 --port 8188`), ve
   çıktısı `COMFY_LOG`'a gider. `ComfyUI başlatıldı (PID …), log: …` satırı da bugünkü gibi basılır.
3. **"Hazır" yalnız kendi süreci yaşıyorken ve `/system_stats` cevap verirken söylenir.** Hücre 2
   sn'de bir, en çok 45 kez bakar (90 sn, bugünkü gibi). Her seferinde önce `/system_stats`'a bakılır,
   sonra başlattığı sürecin yaşayıp yaşamadığı sorulur. Üç sonuç olabilir:
   - **Süreç kapandıysa** hücre hemen düşer, port cevap verse bile: `❌ ComfyUI kapandı — exit <kod>`,
     altında ComfyUI'nin log'unun son 30 satırı.
   - **90 sn'de cevap gelmezse** hücre düşer: `❌ ComfyUI 90 sn içinde cevap vermedi`, altında son
     bakışın hatası `Tür: mesaj` olarak (ör. `URLError: <urlopen error [Errno 111] Connection
     refused>`), sonra log'un son 30 satırı.
   - **Cevap gelirse** `✅ ComfyUI hazır (Ns)` basılır, bugünkü gibi.

Hata, hücrenin `RuntimeError`'ı olarak görünür. Hücre kırmızı biter, Run all orada durur, ve Flask
açılmaz; bugün 90 sn dolunca da öyle oluyor.

## Sınırlar

- **"Hazır"dan sonra ölen ComfyUI'yi Colab göstermez**, çünkü hücre bitmiştir. Bunun görüldüğü yer
  Queen Editor: canlı log'daki satır ve kart, ikisi de `comfyui.log`'un son 30 satırıyla. SIGKILL ile
  ölen bir süreç (ör. OOM) log'a bir şey yazamaz.
- **`GET /history`'nin durum koduna bakılmıyor**, bugün de bakılmıyor. ComfyUI orada 5xx dönerse hata
  bir JSON okuma hatası olarak gelir, işaretsiz kalır, ve beklenmeden yeniden denenir. Bunu değiştirmek
  o kartın metnini de değiştirirdi; bu maddeye girmedi.
- **Bekleme sırasında karenin canlı sayacı saymayı sürdürür.** Düşen denemenin başladığı andan sayar:
  `startedAt`, `submit`'ten önce yazılıyor. Sonraki deneme sayacı sıfırlar. Kaydedilen render süresi
  etkilenmez, çünkü o yalnız inen denemenin süresi. Ekran değişmez; frontend'e ve `dist`'e dokunulmaz.
- **8188'i başka bir süreç tutuyorsa SIGKILL de onu bulmaz.** `"python main.py"` kalıbına uymayan bir
  süreç portu tutarsa hücre portun dolu olduğunu söyleyerek düşer.
- **Hücre 90 sn'de düşünce başlattığı ComfyUI'yi öldürmez,** bugünkü gibi. Hücrenin bir sonraki
  çalıştırılışı onu kapatır.
- **Kullanıcının yaşadığı hatanın sebebi bu maddede gösterilmedi.**

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `backend/services/comfy/errors.py` | `ComfyUnreachable` `no_answer` taşır. Yeni türler: `ComfyHttpError` (durum kodu 5xx ise `no_answer`) ve `ComfyTimeout` (`TimeoutError`, `no_answer`) |
| `backend/services/comfy/client.py` | `_send` `requests.Timeout`'u `ComfyTimeout`'a çevirir. `upload_image` ve `submit` `ComfyHttpError` atar; `_view`, `vram_total` ve `interrupt` `raise_for_status`'un hatasını aynı sözlerle ona sarar |
| `backend/features/photo_generation/domain/policy.py` | `NO_ANSWER_WAIT = 45`, `retry_wait(exc)` |
| `backend/features/photo_generation/domain/run_loop.py` | Düşen her deneme `log`'a basılır. Gerekirse 45 sn, saniye saniye beklenir, Durdur'a bakılarak. `make_job` `sleep` alır |
| `colab/comfy.py` | Yeni: `start_comfy` |
| `queeneditor.ipynb` | Ortak yardımcılar `start_comfy`'yi import eder, ComfyUI hücresi onu çağırır |
| `CODE-STANDARD.md` | *Notebook code* bölümü `comfy.py`'yi de sayar |

`run_queue` ve `main.py` değişmez: `make_job`'ın `sleep`'inin varsayılanı `time.sleep`, ve `log` zaten
`_timing`.

## Testler

Hiçbir test gerçek bir saniye beklemez: döngünün `sleep`'i ve `colab.comfy`'nin `time.sleep`'i sahte.

- **`test_policy.py`:** `no_answer` taşıyan bir hata 45 sn bekletir. Taşımayan bir hata
  (`RuntimeError`, `frame_level`'lı bir hata, `TimeoutError`) bekletmez.
- **`test_comfy_client.py`:**
  - Bağlanılamayan sunucu `no_answer`.
  - `submit`'in 500'ü `no_answer`, 400'ü değil; ikisinin metni de bugünkü gibi
    `POST /prompt -> HTTP <kod>\n<gövde>`. `upload_image`'ın 500'ü de `no_answer`.
  - `/view`'ın 503'ü `no_answer`, 404'ü değil, ve metin `requests`'in kendi `raise_for_status`
    cümlesi. Bunun için sahte cevabın `raise_for_status`'u gerçek `requests.HTTPError`'ı atar. Bugünkü
    sahte bir `RuntimeError` atıyordu. Gerçek `requests` ise `RuntimeError` olmayan bir `HTTPError`
    atar, ve bugünkü `test_interrupt_raises_on_http_error` yalnız sahte yüzünden yeşildi. Gerçekçi
    sahteyle o test kod değişmeden kırmızı olur; `ComfyHttpError` bir `RuntimeError` olduğu için
    değişince yine yeşil.
  - `/system_stats`'ın 502'si `no_answer`.
  - Süresinde cevap gelmeyen istek (`requests.ReadTimeout`) `no_answer`, bir `TimeoutError`, ve metni
    `requests`'inki.
  - Render süresinin dolması `no_answer` değil, ve hâlâ bir `TimeoutError`.
  - `node_errors` `no_answer` değil.
  - ComfyUI'nin düştü dediği render `no_answer` değil.
- **`test_failed_attempts.py` (yeni) — döngü:**
  - Düşen her deneme canlı log'a kendi hatasını basar: türü ve çok satırlı mesajının tamamı. Üç
    deneme, üç satır.
  - ComfyUI cevap vermeyince her yeniden denemeden önce 45 sn beklenir. Toplam 90 sn, saniye saniye;
    üçüncüden sonra beklenmez, ve kuyruk durur.
  - Satır beklemeyi söyler: ilk iki satırda `45 sn sonra yeniden denenecek`, üçüncüde hiçbir şey.
  - Beklemede geri gelen ComfyUI'yle kare yapılır: iki düşüş, 90 sn, kare `done`.
  - ComfyUI'nin düştü dediği kare beklemeden yeniden denenir: bekleme yok, kare kırmızı, satırda
    `yeniden deneniyor`.
  - İşaretsiz bir hata, ör. prompt yazarınınki, beklemeden yeniden denenir.
  - Durdur'la kesilen render düşüş değildir: `log` verilmişken hiçbir `⚠` satırı basılmaz,
    beklenmez, ve durum `paused`. Bu test kod yazıldıktan sonra eklendi, ve hemen yeşildi. Satır bir
    anlığına durdurma kontrolünün üstüne taşındı: yalnız bu test kırmızı oldu.
  - Durdur beklemeyi keser: üçüncü saniyede basılınca üç saniye beklenmiş olur, producer bir kez
    çağrılır, ve durum `paused`.
  - `test_photo_usecases.py`'nin `test_a_frame_that_blew_up_writes_no_timing_line`'ı `log`'un boş
    kalmasını bekliyordu. Artık düşen denemeler oraya yazıyor, bu yüzden test sabitlediği şeye
    daraltılır: hiçbir `⏱` satırı yok.
- **`test_colab_comfy.py` (yeni) — hücrenin kodu.** `pkill`, `Popen`, `urlopen`, porta bağlantı ve
  `time.sleep` sahte. Log dosyası gerçek, `tmp_path`'te. Sahte süreç ona bayt yazar, ComfyUI'nin
  devraldığı tanımlayıcıdan yazdığı gibi; hücre de dosyayı bu yüzden `"wb"` ile açar.
  - Başlattığı süreç cevap verince hazır: bugünkü komut, `cwd` ComfyUI'nin klasörü, çıktı log'a,
    `ComfyUI hazır (6s)`, ve süreç geri döner.
  - Eski ComfyUI gitmeden yenisi başlamaz: `pkill -TERM`, port boşalana kadar saniyede bir bakış,
    sonra `Popen`.
  - İlk açılışta portta kimse yoksa beklenmez: tek bakış, sonra `Popen`.
  - Gitmeyen eski ComfyUI SIGKILL ile kapatılır: 30 sn sonra `pkill -KILL`, sonra başlatma.
  - Hiç boşalmayan port hücreyi bir şey başlatmadan düşürür: `Popen` çağrılmaz, ve hata portu ve 60
    sn'yi söyler.
  - Başlatmadığı bir ComfyUI için "hazır" demez: port cevap verse de kendi süreci kapandıysa hücre
    `exit <kod>` ve log ile düşer, `hazır` basılmaz.
  - Açılırken kapanan ComfyUI hücreyi hemen düşürür: ikinci bakışta, kendi log'unun son 30 satırıyla
    (ilk 10 satır yok).
  - Hiç cevap vermeyen ComfyUI 90 sn sonra düşürür: 45 bakış, son bakışın hatası `Tür: mesaj`, ve
    log.
- **`test_notebook_installs_the_producer_groups.py`:** defter ComfyUI'yi `start_comfy` ile başlatır,
  ve onu klondan import eder; madde 314'ün `install_node` testi gibi.
- Bugünkü testlerin hepsi yeşil kalır.

## Bitti sayılır

- Yeni testler kod değişmeden kırmızı, değişince yeşil; bugünkü testler baştan sona yeşil. Kod
  değişmeden de yeşil olan beş istemci testi bugünkü davranışı sabitler: `submit`'in 400'ü,
  `/view`'ın 404'ü, render süresinin dolması, `node_errors` ve düşen render `no_answer` değil.
  Döngünün ve politikanın testlerinin hepsi kod değişmeden kırmızı: `make_job` `sleep` almıyor, ve
  `retry_wait` yok.
- Dört satır yeşil.
- Colab'da, kullanıcının denemesinde görülecek: ComfyUI hücresi ancak kendi başlattığı ComfyUI cevap
  verince "hazır" der, açılmazsa kırmızı düşer ve ComfyUI'nin log'unu basar. Queen Editor ComfyUI'ye
  bağlanamayınca canlı log'da her denemenin hatası görünür, ve 45 sn sonra yeniden dener.
