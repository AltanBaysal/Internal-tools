# Uzun hata metni: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3` · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-14-queen-editor-hata-karti-testler-design.md) · commit `f85d8f3`
(3 düşen test + 1 yüklenemeyen dosya)

## Yeni parça

`src/shared/RawOutput.jsx` → `RawOutput({ text })`. İki şey çizer: `data-raw` işaretli kayan mono
kutu, ve altında **Kopyala** düğmesi. Kutunun tavanı ~5 satır; metin ne kadar uzun olursa olsun
bileşenin boyu değişmez.

Kopyalama: `navigator.clipboard.writeText(text)` başarılıysa düğme *"Kopyalandı"*, reddedilirse
*"Kopyalanamadı"* der ve birkaç saniye sonra "Kopyala"ya döner.

**Çağrı basışın kendi görevinde yapılır**, bir mikrogörev sonrasında değil. Pano bir kullanıcı
jestine verilen izindir; bir tık geç gelen yazmayı tarayıcı reddedebilir. (İlk yazışta zincir
`Promise.resolve().then(...)` ile başlıyordu ve test bunu yakaladı — `writeText` basış anında
çağrılmamıştı.) `navigator.clipboard` hiç yoksa çağrı **senkron** patlar; onun için çağrı bir
`try` içinde, sonucu ise bir söze çevrilerek tek yolda karşılanıyor — "pano yok" ile "pano
reddetti" kullanıcı için aynı cevabı gerektiriyor.

## Test'in yakalayamadığı, yine de doğru olması gereken şey

Kit'in `Mono`'su bir `<span>`, yani **satır içi** bir eleman. `max-height` ve `overflow` satır içi
kutulara hiç uygulanmaz: stil yazılı durur, tarayıcı yok sayar. Test `style.overflowY`'ye baktığı
için bu tuzağı **göremez** — geçen bir test ve kaymayan bir kutu.

Onun için kutu `display: "block"` taşır. Bu satır silinirse takım yeşil kalır ve hata geri gelir;
yorumu bunu söyler.

Bu, v12'nin sürükleme dersinin aynısı: jsdom'da doğru görünen bir şeyin tarayıcıda çalıştığı
anlamına gelmiyor. Fark, bu sefer tuzağı yazmadan önce bilmemiz.

## Kullanan iki yer

**`StatusErrorCard`** — `raw`'ı çizen çıplak `<Mono>` yerine `<RawOutput text={raw} />`.

**`QueuePanel`'in "Üretim durdu" kartı** — motorun hatası iki parça: kuralın kendi cümlesi, sonra
servisin çıktısı, aralarında bir satır sonu. İlk satır sondaki gibi düz bir satır olarak kalır,
gerisi kutuya girer. Satır sonu hiç yoksa (tek cümlelik bir hata) kutu çizilmez — sarmalayacak bir
şey yok.

Bölme `describeError`'ın bağlantı hatası için zaten yaptığı işin aynısı; iki hata iki türlü değil
aynı türlü okunuyor.

## Panel kayar

`SidePanel`'in sütunu bugün `overflow: hidden`. `overflowY: auto` olur, `overflowX: hidden` kalır —
madde 107 pencerenin yana kaymamasını şart koşuyor ve panelin yana kayması da onun ihlali olurdu.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `src/shared/RawOutput.jsx` | **yeni** |
| `src/shared/StatusErrorCard.jsx` | ham blok `RawOutput`'a devreder |
| `.../photo_generation/QueuePanel.jsx` | durdu kartı cümleyi ayırır, çıktıyı kutuya verir |
| `.../photo_generation/SidePanel.jsx` | panel dikeyde kayar |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 331 geçen, 0 düşen; `dist/` aynı commit'te yeniden
derlenmiş olur.
