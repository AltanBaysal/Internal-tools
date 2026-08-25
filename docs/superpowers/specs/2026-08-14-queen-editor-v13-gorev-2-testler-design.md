# v13 Görev 2 — Bir hata kendi kanıtını taşıyor: TEST döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v13](../plans/2026-08-14-queen-editor-v13-roadmap.md) · **Döngü:** 1/2
**Bu döngüde mantık yazılmıyor** — testler, ve testlerin koşabilmesi için boş iskelet. Takım kırmızı
commit'leniyor.

## Ne biliyoruz

Kullanıcı ekranda şunu gördü:

```
Sunucuya ulaşılamadı — bağlantıyı kontrol et.
Zaman aşımı (10 sn)
```

Ve ilk sorduğu şey şuydu: *neden ham hata mesajı yapıştırılmıyor.* Haklı bir soru, çünkü bu iki
satır hangi isteğin cevapsız kaldığını söylemiyor — galeri mi, durum mu, model listesi mi.

## Sebep

Kanıt üretilmiyor değil; **yolda düşüyor**. `request()` düz bir `Error` fırlatıyor, ve elindeki üç
bilgiyi de fırlatmadan önce atıyor:

| Ne kayboluyor | Nerede | Sonucu |
|---|---|---|
| Metot ve yol | Hiç yazılmıyor | "Bir istek cevapsız kaldı" — hangisi belli değil |
| Ham gövde | `resp.json()` patlayınca `body = null` | Cloudflare'ın hata sayfası ve `error code: 1033` buharlaşıyor |
| HTTP kodu | Gövdede `error` varsa mesaj yalnız o cümle | 400 mü 500 mü, görünmüyor |

Üçüncüsü sinsi: sunucu bir cümle söylediğinde kod hiç yazılmıyor, ve *"Proje bulunamadı"* mesajı
404'ten de 500'den de aynı görünüyor.

**Kopyala düğmesi zaten var** (`RawOutput`), `StatusErrorCard` onu zaten çiziyor. Eksik olan düğme
değil, düğmenin kopyalayacağı şey.

## Testler bunu neden kaçırdı

`api.test.js` hatanın **mesajını** her dalda sınıyor ve hepsi geçiyor — çünkü mesaj doğru. Hiçbir
test mesajın *yanında* ne taşındığını sormuyor, çünkü taşınan bir şey yoktu. v13'ün iki görevinin
ortak dersi burada da: her katman kendi içinde doğru, kayıp **katmanların arasında**.

Bir de fixture'ların kendisi kanıtı imkânsız kılıyor: sahte cevaplar yalnız `json()` veriyor.
Ham metni saklamak `text()` okumayı gerektiriyor, dolayısıyla bu döngü fixture'ları da genişletiyor
— `json()` yanına `text()`, ikisi birden. Genişleme geriye dönük: bugünkü `request()` hâlâ `json()`
çağırdığı için mevcut testlerin hiçbiri bundan kırmızıya düşmüyor.

## Hangi davranış doğru sayılacak

**Mesaj bir cümledir.** `err.message` okunacak tek satırdır ve kanıt içermez. Bugün ağ dalında
mesajın ikinci satırında duran tarayıcı metni de kanıta taşınıyor: bir yerde bir şey, iki yerde iki
kopya olur.

**Kanıt `err.evidence`'ta durur** ve şu sırayla yazılır:

```
GET /api/projects/d%C3%BC%C4%9F%C3%BCn/frames
502 Bad Gateway
<gövdenin tamamı, olduğu gibi>
```

Sunucudan cevap hiç gelmediyse ikinci satır tarayıcının kendi metni ya da zaman aşımı notudur, ve
üçüncü satır yoktur — çünkü gövde yoktur. **Uydurulan hiçbir sebep yok:** her satır ya bizim
yaptığımız şeydir (hangi isteği attık, kaç saniyede kestik) ya da servisin söylediğidir.

**Ham gövde her hâlde saklanır.** JSON'a çevrilemeyen gövde bugün `null`'a düşüyor; artık metin
olarak okunup kanıta giriyor, JSON'a çevirme denemesi onun üstünde yapılıyor. Tünelin HTML hata
sayfası tam da bu yüzden kaybolmuştu.

**Panele giden metin cümle ve kanıtı birleştirir.** `failureText(err)` cümleyi birinci satıra,
kanıtı altına koyar — `QueuePanel.describeError` ilk satır sonundan bölüp altını `RawOutput`'a
verdiği için kanıt kutuya düşer ve Kopyala onu verir. Ekranda okunan cümle değişmez.

**Formlar `err.message`'ı okumaya devam eder.** `NewProjectModal` hatayı 400 piksellik bir kutuda
tek satırlık bir not olarak çiziyor; oraya kanıt bloğu koymak onu bozardı. Ayrım kasıtlı: kanıt
kutusu olan panel `failureText`'i çağırır, olmayan çağırmaz.

## Yazılacak testler

### `frontend/src/shared/api.test.js` — mevcut dosya genişler

Önce fixture'lar: `okResponse` ve satır içi sahte cevaplar `json()` yanına `text()` kazanır. Bu
kırmızı üretmez, kanıtı mümkün kılar.

**Üç yeni test:**

1. **`names the request that failed`** — bir POST reddedilir; kanıtın ilk satırı `POST` ve yolu
   verir. Metodun sabit yazılmadığını söyleyen test.
2. **`keeps the body a tunnel sent instead of JSON`** — gövde HTML bir hata sayfasıdır; kanıt onu
   olduğu gibi taşır (`error code: 1033` dahil). Bugün kaybolan şeyin ta kendisi.
3. **`keeps the status even when the body carried a sentence`** — gövdede `error` vardır; mesaj o
   cümledir, kanıt yine de `400 BAD REQUEST` satırını taşır.

**İki mevcut test yerinden değişiyor**, çünkü sözleşmeleri değişti — mesaj artık tek satır:

4. `wraps a network refusal in a Turkish prefix and keeps the raw text under it` →
   **`names the request that never answered`**: mesaj yalnız cümledir, tarayıcının metni kanıta
   taşınır, kanıtın ilk satırı metot ve yoldur. HTTP kodu satırı yoktur — cevap gelmedi.
5. `aborts a request that goes 10 seconds without an answer` — kesme davranışı aynı kalır, ama
   mesaj tek satır olarak ve zaman aşımı notu kanıtta sınanır.

**Bir mevcut test bekçi olarak duruyor:** `throws the server's own text when the server rejects a
request` zaten `err.message`'ın sunucunun cümlesi olduğunu söylüyor. Kanıt eklenirken mesaja sızma
olmadığını garanti eden test bu; yeniden yazılmıyor, yerinde bırakılıyor.

### `frontend/src/shared/failure_text.test.js` — yeni dosya

6. **`puts the evidence under the sentence`** — kanıtı olan hata cümle + satır sonu + kanıt olur.
7. **`says just the sentence when there is no evidence`** — kanıtsız hata (kendi attığımız hatalar)
   olduğu gibi kalır; birleştirme boş satır eklemez.

### `frontend/src/features/photo_generation/useGeneration.test.jsx` — mevcut dosya genişler

8. **`keeps the evidence of a failed poll`** — poll'u kanıtlı bir hatayla düşür; hook'un `error`'ı
   cümleyi **ve** kanıtı taşıyor. Kullanıcının çarptığı yol tam olarak bu.

### `frontend/src/features/photo_generation/QueuePanel.test.jsx` — mevcut dosya genişler

9. **`hands the evidence to the copy button`** — kanıtlı bir hata metniyle panel çizilir; ham
   kutunun içeriği kanıtın tamamıdır. **Bugün de geçiyor** — `describeError` ilk satır sonundan
   bölmeyi zaten yapıyor, yani panel tarafı hazır ve kırık olan yalnız yukarısı. Yine de yazılıyor:
   kanıtın panoya gidebildiğini söyleyen tek halka bu, ve bölme kuralı bir gün değişirse burada
   kırılması gerekiyor.

## İskelet

`failure_text.js` yalnız imzasıyla açılır:

```js
// Skeleton only -- the rule lands in the implementation cycle.
export function failureText(err) {
  return err.message;
}
```

`api.js` ve hook'lar bu döngüde **değişmiyor**.

## Kırmızı ne olacak

| Test | Nasıl düşüyor |
|---|---|
| 1, 2, 3 | `err.evidence` `undefined` — kanıt hiç üretilmiyor |
| 4, 5 | mesaj hâlâ iki satır, ve kanıt yok |
| 6 | iskelet yalnız mesajı döndürüyor, kanıtı eklemiyor |
| 8 | hook `err.message`'ı saklıyor, kanıt yok |

**Yedi kırmızı.** İki test bugün yeşil geçiyor ve bilerek kalıyorlar:

| Test | Neden bugün yeşil | Neden yine de yazılıyor |
|---|---|---|
| 7 (kanıtsız hata) | iskelet zaten mesajı döndürüyor | Bekçi: birleştirmenin kanıtsız hataya boş satır eklemediğini söyler |
| 9 (kutuya düşen kanıt) | `describeError` bölmeyi zaten yapıyor | Bekçi: kanıtın panoya gidebildiğini söyleyen tek halka |

Bir de yerinde bırakılan bekçi: `throws the server's own text when the server rejects a request`
bugün de yarın da yeşil, ve mesajın kirlenmediğini söyleyen test o.

## Kapsam dışı

- **`useModels` ve `useProducers`.** Aynı tek satırlık değişikliği alacaklar, ama kullanıcının
  çarptığı yol `useGeneration`; yardımcının kendi testleri ikisini de kapsıyor.
- **Formların hata gösterimi.** `NewProjectModal` ve proje listesi `err.message` okumaya devam
  ediyor; bu görev oraya dokunmuyor.
- **Sunucunun ne döndürdüğü.** Backend değişmiyor; bu görev yalnız gelenin kaybolmamasıyla ilgili.
- **Zaman aşımı değeri ve kuyruk tavanı.** Görev 1'in işi, bitti.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` yedi düşen test veriyor, hepsi kanıtın üretilmesi ve
taşınmasıyla ilgili; geri kalan takım yeşil. Commit kırmızı gidiyor ve mesajı bunu söylüyor.
