# Madde 509 · "Orada mısın?" kalkar, sıra bitince bildirim gelir — tasarım

**Tarih:** 29 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-8),
509 · v11-8 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

[518](2026-10-30-queen-editor-m518-acik-sayfa-isi-gorur-design.md) bu bekçiyi `features/queue_watch/` (`QueueWatch`, `GET /api/queue/watch`) olarak genişletti.

## Kabul koşulu (maddeden)

- 10 dk'lık geri sayım ve "orada mısın?" kutusu yok; kullanıcı ne yaparsa yapsın çıkmıyor.
- Sıra boşalınca, yani sıradaki bütün fotoğraf ve videolar bitince, bir kez tarayıcı bildirimi
  geliyor. Bildirim A100 demiyor.

Kararlar maddede yazılı:

- *"bu özelliği kaldır üretim bitince bildirim atsın yeter bu kadar basit yapalım"*;
- export'un bitişi bildirim getirmez; bildirim A100 demez;
- **sıra boşalmadan durunca da** (*"gelsin"*, yapılırken): sıra bir hatayla ya da kurulu olmayan bir
  model yüzünden durunca da kendi cümlesiyle bildirim gelir; Durdur'a basılınca gelmez.

Ekrandaki sürüm V11 kalır.

## 498'den ne kalır, ne gider

[498](../arsiv/specs/2026-10-27-queen-editor-m498-bosta-bildirim-design.md) üç şey kurmuştu: işlerin
başlayıp bittiğini duyan ve 10 dk sayan bir bekçi, ekranın onu tek bir tutulan istekle (long polling,
491'deki gibi) dinlemesi, ve tarayıcı bildirimi. 509'un istediği tek bir olay: sıra bitti — boşaldı
ya da durdu. O olay için gereken kalır, yalnız sayıma ve kutuya hizmet eden gider.

**Kalan:**

- **Tutulan istek** (50 sn, istemcide 80 sn). Bildirim sekme arka plandayken ve proje listesindeyken
  de gelmeli. Sıranın durumunu ekran bugün yalnız proje, kare ve export ekranında, ve yalnız sıra
  çalışırken soruyor (`useGeneration`); proje listesinde kimse sormuyor. Kullanıcı 27 Ekim'de olayla
  çalışan bir yol istemişti, sorarak değil (*"make it eent dirven dont check it again againü"*).
  Tutulan istek tam bunu yapıyor ve zaten yazılı, denenmiş.
- **Tarayıcı bildirimi** (`notification.js`): izin ilk Kuyruğa ekle basışında istenir, bildirime
  tıklayınca sekme öne gelir. Yalnız başlığı değişir.
- **`App`'te tek dinleyici**, ekranlar arasında kopmadan.

**Adlar değişir:** boşta kalmaktan geriye bir şey kalmadığı için kalan parçalar ne olduklarını söyleyen
adlara taşınır (`git mv`):

| 498'deki ad | 509'daki ad |
|---|---|
| `backend/features/idle/` | `backend/features/queue_ended/` |
| `IdleWatch` | `EndedWatch` |
| `make_idle_blueprint`, `GET /api/idle` | `make_ended_blueprint`, `GET /api/queue/ended` |
| `test_idle_watch.py`, `test_idle_routes.py` | `test_ended_watch.py`, `test_ended_routes.py` |
| `frontend/src/features/idle/` | `frontend/src/features/notification/` |
| `useIdleWatch` | `useEndedNotification` |
| `waitForIdle`, `IDLE_ASK_TIMEOUT_MS` | `waitForEnded`, `ENDED_ASK_TIMEOUT_MS` |
| `tag: "queen-editor-idle"` | `tag: "queen-editor-queue"` |

İki fotoğraf paneli `askPermission`'ı artık `../notification/notification.js`'ten alır.

**Giden:**

| 498'in parçası | Neden gidiyor |
|---|---|
| Geri sayım: `_due`, `WAIT_SECONDS`, enjekte saat, `_ask_if_due` | Sayım yok. |
| `asking` alanı ve `_close` | Açık duran bir soru yok; olay olur ve biter. |
| Buradayım: `here()`, `POST /api/idle/here`, `sayHere()`, sayfa açılışındaki Buradayım | Kutu yok, sayım yok. |
| Kutu: `IdleWatch.jsx` ve testi | Kutu yok. |
| `waiting()` ve `AgentRunner`'ın `waiting` parametresi | Yalnız izin bekleyen ajanın sayımı durdurmaması içindi. |
| Bekçinin `spawn`'ı ve üç işçiye verilmesi | Bekçi her işin başını ve sonunu duymak için işleri kendi iş parçacıklarında çalıştırıyordu. Artık yalnız sıranın bittiğini ve nasıl bittiğini duyuyor, ve bunu yalnız sıranın işçisi bilir. Export ve ajan bekçiyle hiç konuşmaz; üç işçi bugünkü kendi `spawn`'larına döner. |
| Bildirimin cümlesi, *"Sıra 10 dakikadır boş. Colab açık kaldıkça A100 boşa para yiyor."* | Sayım yok, ve bildirim A100 demez. |

## Ne yapılır

### Sunucu

**Sıranın nasıl bittiği nerede bilinir:** sıranın döngüsü (`run_loop.make_job`) dönerken özetinde
söyler:

| Özet | Ne demek | Bildirim |
|---|---|---|
| `done` | borçlu iş kalmadı; kırmızı kalan kareler de geçildi | var |
| `error` | üç denemede cevap gelmedi, sıra durdu; `error` sebebi taşır | var |
| `waiting` | sıradaki işin üreticisi kurulu değil; `waitingFor` hangisi (`photo`, `video`, `audio`) | var |
| `paused` | Durdur | yok: basan ekranın başında |

Döngünün dışında hata atan iş de `error`'dur; `PhotoRunner` onun sözünü `error`'a yazar.

**`PhotoRunner`:** yeni bir `ended` parametresi alır, verilmezse hiçbir şey yapmaz. `_run` işin
durumunu yayımladıktan sonra, durum `TOLD = ("done", "error", "waiting")` içindeyse `ended(state)`'i
yayımladığı durumla çağırır. Hangi bitişin bildirildiği kuraldır ve işçide durur, çünkü o kelimeler
onun; bekçi onları bilmez, yalnız saklar. Liste adlarıyla yazılı ("paused dışında hepsi" değil):
sonra eklenen bir durum, biri karar verene kadar kimseye bir şey söylemez. Önce durum yazılır, sonra
söylenir: bildirimi duyup `/api/status`'u soran ekran aynı durumu görür. Çağrı işçinin kilidinin
dışındadır.

**`features/queue_ended/watch.py`, `EndedWatch`:** bir sayaç, son bitiş ve tutulan istek.

- `ended(state)`: kilit altında sayaç bir artar, `state` son bitiş olur, `notify_all`. Kopya
  gerekmez: işçi yayımladığı bir durumu değiştirmez, yerine yenisini koyar. Sayaç ve son bitiş aynı
  kilitte birlikte yazılır, bu yüzden sayacı 0'dan büyük bir cevapta `last` hep doludur.
- `changed_since(after, timeout)`: `{"ended": sayaç, "last": son bitiş ya da None}`. `after` yoksa
  hemen; varsa sayaç `after`'dan farklı olana ya da `timeout` saniye geçene kadar bekçinin kilidinde
  (`threading.Condition`) bekler.

Kapı (`make_ended_blueprint`): `GET /api/queue/ended?after=<sayaç>` → `{"ended": n, "last": {…}}`, en
çok `ASK_WAIT_SECONDS = 50` sn. `after` yoksa ya da sayı değilse hemen cevaplanır. 50 sn'nin ve 80
sn'nin sebebi 498'de yazılı: Quick Tunnel 100 sn sessiz kalan isteği kapatıyor, ve akan bir cevabı
bitene kadar tuttuğu için SSE olmuyor. `last`, `/api/status`'un zaten verdiği durumun aynısıdır;
yeni bir bilgi açmaz.

`main.py`: `_ended = EndedWatch()`, `PhotoRunner(ended=_ended.ended)`, `ExportRunner()`,
`AgentRunner(_chat_record)`, ve kapı.

### Ekran

`features/notification/useEndedNotification.js` durum tutmaz, yalnız dinler; `App` onu kendisi
çağırır, `<Screen />`'i çizer. Bileşen yok.

- **Açılış:** sayaçsız bir istek; hemen cevaplanır ve başlangıç sayacını verir. Çalmaz.
- **Dinleme:** son duyulan sayaçtan `waitForEnded(after)`, cevap gelir gelmez yeniden. Aynı anda tek
  istek açıktır.
- **Çalma:** cevaptaki sayaç son duyulandan **büyükse** `last`'ın cümlesiyle bildirim. Eşitse (sınırda
  dönen cevap) ya da küçükse (sunucu yeniden başladı, sayaç 0'dan) çalmaz, yeni sayaçtan dinlemeye
  devam eder.
- **Ulaşmayan istek:** 10 sn sonra aynı sayaçtan yeniden. Arada sıra bittiyse sonraki cevap hemen
  gelir ve çalar; olay kaybolmaz, yalnız gecikir. İki istek arasında iki bitiş olduysa tek bildirim
  gelir, sonuncunun cümlesiyle.
- **Cümle** (sözcükler ekranın, hangi bitişin bildirildiği sunucunun):
  - `done`: *Sıradaki bütün fotoğraf ve videolar bitti.*
  - `error`: *Sıra durdu.* ve alt satırda sunucunun `error`'u, olduğu gibi;
  - `waiting`: *Sıra durdu: video üreticisi kurulu değil.* — `photo` fotoğraf, `video` video,
    `audio` ses; bilinmeyen bir tür olduğu gibi yazılır.
- Bildirim: başlık **Queen Editor**, `tag: "queen-editor-queue"`, `renotify: true`. İzin yoksa,
  `Notification` yoksa ya da kurucu hata atarsa (Android Chrome) hiçbir şey olmaz; ekranda başka bir
  şey çıkmaz.

## Maliyet

- **Sıranın bitişi:** bekçinin kilidi altında bir toplama, bir atama ve bir `notify_all`. Disk yok, istek yok.
- **Ekranda:** açık sekme başına tek bir tutulan istek; bir şey olmadığında 50 sn'de bir tünel gidiş
  dönüşü (saatte 72), olay olunca hemen. Sunucuda o istek bir Werkzeug iş parçacığında uyur. Proje,
  sohbet ve dosya sayısından bağımsız, O(1). 498'deki sayfa açılışı `POST`'u ve Buradayım `POST`'u
  gider.
- **Export ve ajan:** bekçiye hiçbir şey söylemez; maliyetleri 498'den önceki gibi.

## Ne kaybolabilir, ne bozulabilir

- Hiçbir şey yazılmaz; sayaç ve son bitiş bellekte yaşar.
- Yeniden başlayan sunucu sayacı 0'a döndürür. Colab'da eski sekme yeni sunucuya hiç ulaşmaz (her
  başlatış yeni bir Quick Tunnel açar). `localhost`'ta eski sekme daha küçük bir sayaç duyar,
  çalmaz, ve ondan dinlemeye devam eder; sonraki bitiş çalar.
- İki istek aynı anda gelirse bekçinin tek kilidinde sırayla görür.
- İşçinin kilidi ile bekçinin kilidi iç içe tutulmaz: `ended()` işçinin kilidinin dışında çağrılır.
- Hata metni bir sırrı taşımaz: `/api/status` onu zaten sıra panelinde gösteriyor.

## Sınırlar

- Durdur'da bildirim yok: Durdur'a basan oradadır.
- İki sekme açıksa ikisi de çalar; tek `tag` olduğu için işletim sisteminde tek bildirim kalır.
- Sekme kapalıyken bildirim gelmez: kapanan sayfa bildirim atamaz
  ([BACKLOG](../../queen-editor/BACKLOG.md), *"Boşta Colab kapansın"*).
- Bildirim kullanıcı ekrana bakarken de gelir; madde bunu ayırmıyor.
- Uzun bir hata metnini işletim sistemi kendisi kısaltır.

## Ne zaman bitti

- Bekçi: sayaçsız istek hemen `{"ended": 0, "last": None}`; `ended()` sayacı artırıyor ve son
  bitişi saklıyor; eski sayaçtan istek hemen, güncel sayaçtan istek sınırda
  cevaplanıyor; tutulan istek `ended()`'a hemen uyanıyor.
- Kapı: `after` sayıysa sınırla, değilse hemen; sınır 100 sn'nin altında.
- `PhotoRunner`: `done`, `error`, `waiting` ve hata atan işte `ended(state)` bir kez, yayımladığı
  durumla ve durum yazıldıktan sonra; `paused`'da çağrılmıyor; `ended` verilmeden çalışıyor.
- `AgentRunner` `waiting` almıyor; `main.py` sıranın işçisine `ended`'ı veriyor, export ve ajan
  kendi `spawn`'larıyla; `GET /api/queue/ended` başta `{"ended": 0, "last": None}`.
- Ekran:
  - açılışta sayaçsız tek istek, sonra cevabın sayacından tek istek;
  - büyüyen sayaçta bir bildirim, aynı sayaçta yok, küçülen sayaçta yok;
  - `done`, `error` ve `waiting`'in her biri kendi cümlesiyle; `waiting`'de üç tür de kendi
    sözcüğüyle (fotoğraf, video, ses);
  - ulaşmayan istekten 10 sn sonra aynı sayaçtan, daha önce değil;
  - StrictMode'da tek tutulan istek; söküldükten sonra çalmıyor;
  - proje listesinde de çalıyor, ve ekran değişince istek kopmuyor (`App.test`);
  - hiçbir ekranda "Orada mısın?" yok.
- Bildirim başlığı **Queen Editor**, metinde "A100" yok.

## Yalnız Colab'da görülecek

- Gerçek bir sıranın bitişinde ve hatayla duruşunda, sekme arka plandayken işletim sisteminin
  bildirimi; tıklayınca sekmenin öne gelmesi.
- Bir export bitince ve Durdur'a basınca bildirim gelmemesi; videolar incelenip silinirken hiçbir kutu
  çıkmaması.
