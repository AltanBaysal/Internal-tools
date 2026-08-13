# v12 Görev 2 — Kareler yeniden sürüklenebiliyor: TEST döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v12](../plans/2026-08-14-queen-editor-v12-roadmap.md) · **Döngü:** 1/2
**Bu döngüde kod yazılmıyor** — yalnız testler, ve takım kırmızı commit'leniyor.

## Ne biliyoruz

Kullanıcı iki şeyi denedi ve söyledi:

1. Kart **hiç kalkmıyor** — eğik, gölgeli sürüklenen kart hiç görünmüyor.
2. Basıp **kımıldatmadan bir saniye bekledikten sonra** sürüklemek de bir şey değiştirmiyor.

İkincisi belirleyici: bugünkü mekanizma tam olarak bunu yapmanı bekliyordu.

## Sebep

Kart ancak basılı tutulduktan sonra sürüklenebilir hâle geliyor:

```jsx
draggable={armed === frame.id && !selecting}
onMouseDown={() => !selecting && press(frame.id)}   // 250 ms sonra setArmed(fid)
```

Yani `draggable` basıştan **sonra** açılıyor. Tarayıcı ise bir basışın sürüklemeye dönüşüp
dönüşemeyeceğine `mousedown` anında karar veriyor: o an eleman sürüklenebilir değilse, fare
hareketi bir **metin seçimi** olur ve sonradan açılan `draggable` o basışı geri kazanmaz. Kullanıcı
her seferinde `draggable="false"` bir eleman üstünde basıp çekiyor.

Bu tek başına raporun tamamını açıklıyor — hem "hiç kalkmıyor"u, hem "beklesem de olmuyor"u.

**Ne kadar eminiz:** burada tarayıcı yok, dolayısıyla bu bir çıkarım, gözlem değil. Ama seçilen
çözüm iki hâlde de doğru: `draggable`'ı basıştan önce açık hâle getirmek, bu sebebi ortadan
kaldırır ve başka bir sebep varsa da onun üstünü örtmez — jest hâlâ ya çalışır ya çalışmaz, ve
bunu ölçen şey artık kullanıcının Colab turu olur.

## Testler bunu neden kaçırdı

`Gallery.test.jsx` sürüklemeyi iki yerden sınıyor ve ikisi de gerçek jesti atlıyor:

| Test | Ne yapıyor | Neden kaçırıyor |
|---|---|---|
| `reports the new order when a frame is dropped` | `dragStart` / `dragOver` / `drop` olaylarını **kendi ateşliyor** | Tarayıcının sürüklemeyi başlatıp başlatmayacağını hiç sormuyor — sürükleme başlamış varsayılıyor |
| `arms the tile once it has been held` | basış + 250 ms sonra `draggable` doğru mu | Doğru — ama tarayıcının baktığı **an** yanlış: o an çoktan geçmiş |

İkincisi bu görevin dersi: bir testin doğru şeyi ölçmesi yetmiyor, **doğru anda** ölçmesi gerekiyor.

**Ve bunu jsdom yakalayamaz.** jsdom sürükleme başlatmıyor, dolayısıyla "tarayıcı bu basışı
sürüklemeye çevirir miydi" sorusunun jsdom'da karşılığı yok. Yapılabilecek en iyi şey, tarayıcının
şartını teste çevirmek: **basıldığı anda kart sürüklenebilir olmalı.** Bu görevdeki testler bunu
sınıyor; ötesini yalnız Colab turu söyler ve spec bunu saklamıyor.

## Hangi davranış doğru sayılacak

**Kart hep sürüklenebilir.** Basılı tutma adımı kalkıyor: `armed`, `press`, `release`, `HOLD_MS` ve
onları besleyen fare olayları gidiyor. Geriye tarayıcının anladığı tek şey kalıyor — `draggable`,
basıştan önce açık.

**Tasarımın istediği "basılı tut" düşüyor ve bu bilinçli.** Kaynak yorumu *"tasarım bir tutuş
istiyor; sayı bizim"* diyor. Ama tutuşu HTML5 sürüklemesiyle kurmak mümkün değil — tarayıcı
`mousedown`'da karar veriyor. Tutuşu korumanın tek yolu sürüklemeyi elle yazmak olurdu (fare
olaylarıyla konum takibi, kendi hayalet kartı, kendi bırakma bölgeleri); bu görev bir hatayı
düzeltiyor, sürükleme motoru yazmıyor. Tutuşun asıl derdi — "kaydırayım derken sıra bozulmasın" —
tarayıcının kendi eşiğiyle zaten karşılanıyor: birkaç piksel kımıldamadan sürükleme başlamıyor.

**Seçim açıkken hiçbir şey sürüklenmiyor.** Bu kural duruyor: seçim sürerken basış seçmektir,
sürüklemek değil — tek jest iki anlama gelemez.

## Yazılacak testler

`Gallery.test.jsx` içindeki `describe("Gallery — picking a tile up")` bloğu bu davranışı yazacak
şekilde yeniden yazılır. Dört testin dördü de bugünkü tutuşu sınıyor, dolayısıyla dördü de gidiyor.

1. **Bir kare, dokunulmadan sürüklenebilir.** Galeri çizilir, hiçbir olay atılmaz, karo
   `draggable` olur. Tarayıcının `mousedown` anında sorduğu şeyin testi.
2. **Basmak sürüklenebilirliği değiştirmiyor.** `mouseDown` sonrası da `draggable` — arada
   kazanılan bir hâl olmadığını, yani bir zamanlayıcıya bağlı olmadığını söyler.
3. **Bekleyen kare de sürüklenebilir.** Üretilmemiş kare de kalkar (v5 kararı: sıra üretimin
   sırasıdır, bu yüzden asıl sürüklenmek isteneni piksel yok).
4. **Hatalı kare de sürüklenebilir.**
5. **Motorun elindeki kare de sürüklenebilir** — üretim yarıda kesilmez, kare biter ve yeni yerinde
   durur.
6. **Seçim açıkken hiçbir kare sürüklenmiyor.** Halkaya basılıp bir kare seçilir; başka bir karo
   `draggable` olmaktan çıkar.

`reports the new order when a frame is dropped` ve `does not go to the server for a frame dropped
where it already was` olduğu gibi kalır: bırakma tarafı doğru çalışıyor, kırılan başlama tarafı.

## Kırmızı ne olacak

| Test | Bugün | Nasıl düşüyor |
|---|---|---|
| 1 (dokunulmadan sürüklenebilir) | **kırmızı** | `draggable` `false` — hiçbir kare armed değil |
| 2 (basmak değiştirmiyor) | **kırmızı** | basış sonrası hâlâ `false`, tutuş beklenmiyor |
| 3, 4, 5 (bekleyen / hatalı / çalışan kare) | **kırmızı** | aynı sebep |
| 6 (seçim açıkken sürüklenmez) | yeşil | bugün de sürüklenmiyor — ama bugün *hiçbir* şey sürüklenmiyor, o yüzden bu testin değeri düzeltmeden sonra doğar |

Beş kırmızı. Altıncısı bekçi: seçim kuralının, sürüklenebilirlik açılırken düşmediğini garanti eder.

## Kapsam dışı

- **Sürüklemenin gerçekten başladığı.** jsdom söyleyemez; Colab turu söyler.
- **Bırakma tarafı, sıra kaydı, motorun sırayı okuması.** Hepsinin kendi testleri var ve geçiyorlar.
- **Kendi yazdığımız bir sürükleme motoru.** Tutuşu geri isteyen tek yol bu ve bu görevin işi değil.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` beş düşen test veriyor, hepsi karonun basıldığı anda
sürüklenebilir olmasıyla ilgili; geri kalan takım yeşil. Commit kırmızı gidiyor ve mesajı bunu
söylüyor.
