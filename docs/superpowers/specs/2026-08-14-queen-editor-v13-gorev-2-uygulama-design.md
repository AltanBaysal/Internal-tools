# v13 Görev 2 — Hatanın kanıtı: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v13](../plans/2026-08-14-queen-editor-v13-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-14-queen-editor-v13-gorev-2-testler-design.md) ·
commit `5858c9e` (yedi test kırmızı)

## Ne geliyor

**Gövde önce metin olarak okunur, JSON'a çevirme onun üstünde denenir.** Bugün `resp.json()`
patladığında elde hiçbir şey kalmıyor; bir gövde iki kez okunamayacağı için ham metni sonradan
kurtarmak da mümkün değil. Sıra tersine dönüyor: `resp.text()` her hâlde ham gövdeyi verir, ayrıştırma
o metnin üstünde çalışır, ve çevrilemeyen gövde artık kaybolmak yerine kanıta girer.

**Hata iki alanla doğar.** Mesaj okunacak cümledir; `evidence` kanıttır — hangi istek, ne döndü,
gövde ne dedi. İkisini tek bir yerde kuran küçük bir yardımcı var, çünkü `request()` iki ayrı daldan
hata fırlatıyor ve ikisinin de aynı şekli taşıması gerekiyor.

**Ağ dalının mesajı tek satıra iner.** Tarayıcının metni ("Failed to fetch") ve zaman aşımı notu
kanıta taşınıyor. Bugün mesajın ikinci satırında duruyorlar; kanıt da eklenirse aynı olgu iki yerde
dururdu.

**`failureText(err)` cümleyi ve kanıtı birleştirir**, ve bunu **yalnız ham kutusu olan paneller
çağırır** — `useGeneration`, `useModels`, `useProducers`. Formlar ve proje listesi `err.message`
okumaya devam eder: `NewProjectModal` hatayı 400 piksellik kutuda tek satırlık bir not olarak
çiziyor, oraya kanıt bloğu koymak onu bozardı.

## Bunun bir şey kaybettirdiği yer

**Ham gövde ne kadar büyükse o kadar taşınıyor.** Altmış satırlık bir ComfyUI cevabı da, bir HTML
hata sayfası da olduğu gibi giriyor. `RawOutput` bunu zaten katlıyor (kendi tavanı ve kaydırması
var, v11'de tam bu yüzden yazıldı), o yüzden panel taşmıyor — ama saklanan metin artık büyük
olabilir. Kabul: repo kuralı kesmeyi değil katlamayı söylüyor.

## Kalan risk, açıkça

**`resp.text()` sahte cevaplarda vardı, gerçek `Response`'ta da var — ama ara katmanlarda olmayabilir.**
Colab'da isteği karşılayan şey Flask; tarayıcı `Response` nesnesini kendisi kuruyor, dolayısıyla
`text()` her hâlde orada. Burada tarayıcı yok, ve bunun doğrulandığı yer Colab turu.

**Kanıt ekrana da yazılıyor.** Ham kutu zaten görünür, yani kullanıcı artık kartın altında HTTP kodu
ve gövde görüyor. Kasıtlı — kutu tam bunun için var — ama turda çirkin durursa ayarlanacak şey
kutunun kendisi olur, kanıtın varlığı değil.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../shared/api.js` | gövde metin olarak okunur, hata `evidence` ile doğar |
| `.../shared/failure_text.js` | iskeletin yerine birleştirme |
| `.../photo_generation/useGeneration.js` | `err.message` yerine `failureText(err)` |
| `.../photo_generation/useModels.js` | aynı tek satır |
| `.../producers/useProducers.js` | aynı tek satır |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 360 geçen, 0 düşen. `dist/` aynı commit'te yeniden
derlenmiş olur. Ölü bir tünelde Kopyala'nın gerçekten hangi isteği ve hangi gövdeyi verdiği Colab
turunun cevabı.
