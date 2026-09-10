# Madde 209 — sürüm arayüzde görünür · test turu

**Kaynak:** [yol haritasının Madde 209'u](../plans/2026-09-06-queenagent-v8-roadmap.md).

## Ne kanıtlanacak

Koşudan koşuya atlıyoruz — V6, V7, V8 — ve ekrana bakan biri hangi kuşağı çalıştırdığını
bilmiyor. Tek parça: **koşu numarası, büyük harfle**, kenar çubuğunun wordmark'ının altında.

Bu madde ön uca dokunan tek madde, ve **sırası serbest**: hiçbir maddeye dayanmıyor, hiçbirini
bloklamıyor.

## Sabit nerede durur

`frontend/src/shared/version.js`, tek satırlık bir modül.

**Kenar çubuğunda değil**, çünkü sürüm çubuğun bilgisi değil: çubuk onu **gösteriyor**. Bir koşu
başlarken bu sayıyı değiştirecek kişi, onu bir bileşenin içinde aramamalı. Deponun kendi biçimi de
bu — `modes.js`, `models.js`, `skills.js`, `railWidth.js`: bir olgu, bir dosya.

`shared/` altında çünkü sürüm uygulamanın, `workspace` özelliğinin değil.

## Testler ne tutar, ne tutmaz

**Değeri tutmaz.** `VERSION === "V8"` diye bir test, elle verilen bir kararı **iki** yere yazar:
koşu başlarken ikisini birden değiştirmek gerekir, ve biri unutulursa süit koşuyu değil kendini
korumuş olur. Değer bir karar, davranış değil.

**Biçimi tutar.** `V` ve rakam — `v8`, `8`, `V8.1` ya da `V8-beta` değil. Bunu tutmak bir kararı
kopyalamıyor; **hangi biçimde** yazılacağını söylüyor, ve o biçim maddenin kendi cümlesi:
*"koşu numarası, büyük harfle."*

**Ekranda olduğunu tutar**, sabitin kendisiyle: `getByText(VERSION)`. Böylece V9 geldiğinde test
değişmeden geçer — ama sürüm ekrandan düşerse kırmızı verir.

## Dört iddia

| # | Nerede | Ne |
|---|---|---|
| 1 | `shared/version.test.js` | sabit `V` artı rakam biçiminde |
| 2 | `Sidebar.test.jsx` | sürüm çubuğun marka bloğunda çiziliyor |
| 3 | `Sidebar.test.jsx` | çubuk katlanınca sürüm de gidiyor |
| 4 | `workspace.css.test.js` | ad ile sürüm **alt alta**, ve sürüm bir not gibi okunuyor |

**Üçüncüsü bedava değil:** katlanmış çubuk erken dönüyor, yani bugünkü kodda sürüm zaten
çizilmiyor — ama iddia yazılmazsa yarın marka bloğu katlanmış dala taşındığında kimse fark etmez.
Maddenin kendi cümlesi: *"çubuk katlanınca sürüm de katlanıyor — kendi başına bir yer açmıyor."*

**Dördüncüsü stil değil yerleşim:** *"wordmark'ın altında"* maddenin kendi kararı, ve marka bloğu
bugün bir **satır** *(`display: flex`, `align-items: center`)*. Ad ile sürümü bir sütuna almadan
sürüm wordmark'ın **yanına** düşer. Rengi de iddiaya dahil: `var(--muted)`, deponun not sesi —
`.msg__stamp` ile `.tool-call__head` aynı değişkeni kullanıyor ve testleri onu tutuyor.

## Bu turda yazılmayanlar

- **Kod açılmıyor.** `Sidebar.jsx`, `version.js` ve `workspace.css` uygulama turunda değişir.
- **Derleme tarihi kapsam dışı** *(kullanıcı kararı, 10 Eylül)*: bayat bir klonu ele veren işaret
  gerekli ama bu maddenin işi değil.
- **queen-editor'ün kendi sürümü** kapsam dışı: o kendi `BACKLOG.md`'sinin işi.
- **`dist` bu turda derlenmez** — test turu ön uç kaynağına dokunmuyor, yalnız testlere.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Dört kırmızı**, arka uç 923 yeşilde durur. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-10-queenagent-m209-test-plan.md).
