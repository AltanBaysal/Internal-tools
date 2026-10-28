# Madde 498 · Sıra boşken bildirim — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-2),
498 · v11-2 · **Dal:** `feat/queen-editor-v11` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Sıra 10 dk boş kalınca ekranda "orada mısın?" çıkıyor ve tarayıcı bildirimi geliyor. Sıra boş
kaldıkça ikisi her 10 dk'da bir yeniden geliyor. Bir export ya da ajanın cevabı sürerken ikisi de
gelmiyor.

Kararlar maddede yazılı:

- tek bir **Buradayım** düğmesi;
- bildirim izni ilk Kuyruğa ekle basışında istenir;
- 10 dk işin bittiği andan sayılır, boş açılışta açılıştan;
- boş kaldıkça her 10 dk'da bir tekrar;
- izin bekleyen ajan iş sayılmaz;
- sunucuda merkezi bir bekçi, olayla çalışır, sorarak değil (*"Olayla, sorarak değil"*), ve ekran
  olayı 491'in long polling'iyle öğrenir.

Colab'ı kapatmak bu maddede yok ([BACKLOG](../../../queen-editor/BACKLOG.md), *"Boşta Colab kapansın"*).

## Bugün kim neyi biliyor

- **Sıra:** `/api/status` sunucunun tek işçisini söyler. Ekran onu yalnız proje, kare ve export
  ekranında, ve yalnız sıra çalışırken sorar. Proje listesi hiçbir şey sormaz.
- **Ajan:** sunucuda, bellekte çalışır (`AgentRunner`). Ekran onu yalnız ajan paneli açıkken, tek proje
  için bilir.
- **Export:** `ExportRunner` süreçte tektir. Ekran onu yalnız export ekranında bilir.

Üç işçinin ortak noktası tek: hepsi işini `spawn` ile kendi iş parçacığında çalıştırır
(`PhotoRunner.start`, `ExportRunner.start`, `AgentRunner.start`). Sunucuda başka arka plan işi yok.

## Ne yapılır

### Sunucu: bekçi, `backend/features/idle/`

`watch.py`'de `IdleWatch`, `presentation/routes.py`'de iki kapı. `main.py` bekçiyi kurar ve üç
işçiye verir; hiçbir özellik başka birini import etmez.

**İş bekçiye nasıl söylenir:** üç işçi `spawn` olarak bekçinin `spawn`'ını alır (`main.py`:
`PhotoRunner(spawn=_idle.spawn)`, `ExportRunner(spawn=_idle.spawn)`,
`AgentRunner(..., spawn=_idle.spawn, waiting=_idle.waiting)`). İşin başlaması, iş parçacığının
açılmasıdır. Bitmesi, işin dönmesidir, hata atarak dönmesi de; `finally`'de söylenir, kaçırılamaz.
Bekçi işçilerin durumunu okumaz, işçiler de bekçiyi bilmez: ellerine verilen `spawn`'ı çağırırlar.
Testlerdeki işçiler kendi `spawn`'larıyla kurulur ve bekçi görmez.

Bu yüzden `PhotoRunner` ve `ExportRunner`'ın kodu değişmez. İşçi başına anahtar ya da "başladı/bitti"
çağrısı da yok: her `spawn` bekçinin kendi saydığı bir iştir.

**İzin bekleyen ajan:** kural tek yerde. `AgentRunner._permit` kullanıcıyı `with self._waiting():`
içinde bekler. Bekçinin `waiting()`'i girişte o iş parçacığının işini "bitti", çıkışta "başladı"
sayar. Cevap da Durdur da bekleyişi bitirir. Durdur'dan sonra iş bir an daha sürer ve döner: o an
açık bir soruyu kapatır, ama Durdur'a basan zaten oradadır. `waiting` verilmeyen `AgentRunner`
(testler) `nullcontext` kullanır. Bekçinin iş parçacıklarının dışında, örneğin testte satır içinde
çalışan işte, `waiting()` hiçbir şey yapmaz.

**Geri sayım:** hiçbir iş yokken bir an tutulur, `_due` = şimdi + 600 sn. Ayrı bir zamanlayıcı
iş parçacığı yok.

| Olay | Geri sayım | Soru |
|---|---|---|
| Sunucu açıldı | başlar | — |
| Bir iş başladı | iptal | açıksa kapanır, sürüm ilerler |
| Son iş bitti | başlar | — |
| Geri sayım doldu | yeniden başlar | sorulur, sürüm ilerler |
| Buradayım | iş yoksa yeniden başlar | açıksa kapanır, sürüm ilerler |

`version` her soruluşta ve her kapanışta ilerler. Böylece 10 dk sonraki ikinci soru da yeni bir
sürümdür ve yeniden çalar.

**Tutulan soru (long polling, 491'deki gibi):** `changed_since(version, limit)`, sürüm `version`'dan
ilerleyene ya da `limit` saniye geçene kadar bekçinin kilidinde (`threading.Condition`) bekler.
Uyanma anı üçünden hangisi önce gelirse odur: geri sayımın dolduğu an, bir olay (`notify_all`), ya
da sınır. Geri sayım soruyu, tutulan bir sorunun içinde doğurur. Hiçbir ekran sormuyorsa kimseye bir
şey söylenmez; ilk soran, durumu olduğu gibi duyar. Geri sayım enjekte edilen saatle ölçülür, testler
sahte saat kullanır. Sorunun ne kadar tutulduğu ise hep gerçek `time.monotonic`'tir: o, tünele
verilmiş bir söz, sayımın parçası değil.

Kapılar:

- `GET /api/idle?after=<sürüm>` → `{"version", "asking"}`. En çok `ASK_WAIT_SECONDS = 50` sn tutulur.
  `after` yoksa ya da sayı değilse hemen cevaplanır.
- `POST /api/idle/here` → Buradayım; aynı şekli döner.

**Neden 50 sn:** Quick Tunnel 100 sn sessiz kalan isteği kapatıyor (491'in araştırması); 50, gidiş
dönüşe yer bırakıyor. QueenAgent 15 sn tutuyor, çünkü onun ekranı bir turun ilerleyişini duymak
istiyor. Buradaki ekran tek bir olayı bekliyor. SSE yok: Quick Tunnel akan bir cevabı bitene kadar
tutuyor (491).

### Ekran: tek bir `IdleWatch`, `App.jsx`'te

`App` bugünkü yönlendirmeyi `Screen`'e taşır ve `<Screen />` ile `<IdleWatch />`'u yan yana çizer.
Kutu dört ekranda da çıkar, ve tek tutulan soru ekranlar arasında gezilirken kopmaz.

`features/idle/useIdleWatch.js` saymaz, yalnız dinler:

- **Açılış:** `sayHere()`, yani Buradayım. Sayfayı yeni açan kişi oradadır, ona "orada mısın?"
  sorulmaz. Bu, maddedeki *"uygulama boş bir sırayla açılırsa açıldığı andan"* kararının ekrandaki
  karşılığı; sunucunun açılışı da geri sayımı başlatır. Başka bir sekmede açık duran soruyu da
  kapatır: biri sayfayı açtıysa oradadır.
- **Dinleme:** cevabın sürümünden `waitForIdle(after)`, cevap gelir gelmez yeniden. Aynı anda tek bir
  istek açıktır.
- **Cevap:** `asking` kutuyu açar ya da kapatır. Yeni bir sürümle gelen `asking: true` bildirimi
  çaldırır; aynı sürüm ikinci kez çaldırmaz.
- **Buradayım:** kutu hemen kapanır, `sayHere()` gider, cevabı alınır.
- **Ulaşmayan istek** (tünel koptu, Colab kapandı): 10 sn sonra aynı sürümden yeniden sorulur. Kart
  çıkmaz.
- **İstemcinin zaman aşımı:** bu istek için 80 sn (`api.js`, `waitForIdle`). Sunucunun 50 sn'sinden
  uzun, tünelin 100 sn'sinden kısa. Öteki isteklerin 10 sn'si bu soruyu her seferinde keserdi.

Kutu `.wf-scrim` üstünde bir kart, `ConfirmModal`'ın yapısında. Başlık **Orada mısın?**, metin
*Sıra 10 dakikadır boş. Colab açık kaldıkça A100 boşa para yiyor.*, tek düğme **Buradayım**
(açılınca odakta). Escape'le ya da dışına tıklayarak kapanmaz.

### Tarayıcı bildirimi (`features/idle/notification.js`)

- **İzin:** iki Kuyruğa ekle düğmesinin (`GeneratePanel`, `LayerPanel`) `handleAdd`'i, aynı
  tıklamanın içinde `askPermission()`'ı çağırır. `LayerPanel`'de çağrı panelin kendi reddinden sonra
  gelir. Yalnız izin `"default"` iken sorulur. `Notification` yoksa hiçbir şey olmaz.
- **Bildirim:** `notify()`. Başlık *Queen Editor — orada mısın?*, metin kutununki;
  `tag: "queen-editor-idle"` ve `renotify: true`. Bildirime tıklayınca sekme öne gelir. İzin yoksa,
  `Notification` yoksa ya da kurucu hata atarsa (Android Chrome), yalnız kutu çıkar.
- **Sekme arka plandayken:** tutulan istek açık kalır, ve cevap gelince bildirim işletim sisteminin
  bildirimi olarak gelir. Sayım sunucuda olduğu için tarayıcının arka plan zamanlayıcı seyreltmesi
  sayımı geciktirmez.
- **Sekme kapalıyken:** hiçbir şey olmaz. Kapanan sayfa bildirim atamaz; Colab'ı boşta kapatmanın
  backlog'da durmasının sebebi de bu.
- Bildirim güvenli bir adres ister: tünelin `https` adresi ve `localhost` güvenli.

## Maliyet

- **Bir işin başlaması ve bitmesi:** bekçinin kilidi altında bir küme işlemi ve bir `notify_all`.
  İstek yok, disk yok.
- **Ekranda:** açık sekme başına tek bir tutulan istek. Bir şey olmadığında 50 sn'de bir tünel gidiş
  dönüşü (saatte 72), olay olunca hemen. Sunucuda o istek bir Werkzeug iş parçacığında uyur, CPU
  harcamaz. Proje, sohbet ve dosya sayısından bağımsız, O(1).
- **Buradayım ve sayfa açılışı:** bir `POST`.
- **Bildirim izni:** istek yok.

## Ne kaybolabilir, ne bozulabilir

- Hiçbir şey yazılmaz; bekçi bellekte yaşar.
- Yeniden başlayan sunucu sayımı baştan başlatır ve sürümü 0'a döndürür. Colab'da eski sekme yeni
  sunucuya hiç ulaşmaz: `colab/server.py`'nin `serve()`'ü her başlatışta yeni bir Quick Tunnel açar.
  Eski sekme ölü adresi 10 sn'de bir sorar; bunun zararı yok. Sürümün 0'a dönmesi yalnız
  `localhost`'ta görünür. Orada sayfa eski sürümden sorar ve farklı bir sürüm duyar; o cevap hemen
  gelir, ve sayfa yeni sürümden dinlemeye devam eder.
- İki istek aynı anda gelirse ikisi de bekçinin tek kilidinde sırayla görür.
- İşçinin kilidinden bekçinin kilidine tek yön var: `_permit` işçinin kilidini tutarken
  `waiting()`'e girer. Bekçi hiçbir zaman bir işçiyi çağırmaz, bu yüzden kilitlenme yok.
- Hata atan iş de `finally`'de bitmiş sayılır.

## Sınırlar

- İki sekme açıksa ikisi de duyar, ikisinde de kutu çıkar. Bildirimde tek `tag` olduğu için ekranda
  tek bildirim kalır. Bir sekmede Buradayım, sunucudaki soruyu kapatır; öteki sekme de bunu duyar ve
  kutusunu kapatır.
- Sekme kapalıysa ve hiçbir sekme sormuyorsa, soru kimseye ulaşmaz.

## Ne zaman bitti

- Bekçi (sahte saatle):
  - iş yokken açılıştan 600 sn sonra soruyor, 599'da sormuyor;
  - boş kaldıkça her 600 sn'de bir yeniden soruyor;
  - Buradayım kapatıp sayımı yeniden başlatıyor; iş sürerken gelen Buradayım (her sayfa açılışı)
    geri sayım açmıyor;
  - iş sürerken sormuyor, son iş bitince sayıyor, ve başlayan iş açık soruyu kapatıyor;
  - hata atan iş de bitiyor;
  - `waiting()` içinde bekleyen iş, iş sayılmıyor; bekleyiş bitince yine iş sayılıyor.
- Tutulan soru (gerçek saatle, saniyenin kesri):
  - sürümü ilerleyince hemen cevaplanıyor, yoksa sınırda;
  - geri sayımın dolmasına, Buradayım'a ve başlayan işe uyanıyor;
  - iş sürerken uyuyan soru, işin bitişiyle açılan geri sayıma da uyanıyor.
- `AgentRunner` izin beklerken `waiting()`'in içinde; cevapla da Durdur'la çıkıyor.
- Kapılar: `after` sayıysa sınırla bekletiyor, değilse hemen cevaplıyor; sınır 100 sn'nin altında.
  `main.py` üç işçiye bekçinin `spawn`'ını, ajana `waiting`'ini veriyor.
- Ekran:
  - açılışta Buradayım diyor ve cevabın sürümünden tek bir istek tutuyor;
  - yeni soruda kutu ve bildirim, aynı soruda ikinci bildirim yok;
  - kapanışta kutu sessizce gidiyor;
  - Buradayım hemen kapatıyor;
  - ulaşmayan istekten 10 sn sonra yeniden soruyor, daha önce değil;
  - sökülüp hemen yeniden kurulunca (StrictMode) tek istek tutuyor;
  - izin yoksa ya da `Notification` yoksa yalnız kutu çıkıyor;
  - kutu proje listesinde de projede de çıkıyor, ve ekran değişince istek kopmuyor (`App.test`).
- İlk Kuyruğa ekle izni soruyor; karar verilmiş izni bir daha sormuyor.

## Yalnız Colab'da görülecek

- Tutulan isteğin Quick Tunnel'dan 50 sn boyunca geçmesi, ve cevabın olay anında gelmesi.
- Tünelin `https` adresinde izin sorusu ve işletim sisteminin bildirimi.
- Sekme arka plandayken bildirimin gelmesi, ve bildirime tıklayınca sekmenin öne gelmesi.
- Gerçek 10 dakika: bir üretim bitince, bir export bitince, ve izin bekleyen bir ajanla.
