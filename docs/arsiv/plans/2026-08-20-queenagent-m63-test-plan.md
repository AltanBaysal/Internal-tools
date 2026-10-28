# Madde 63 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-20-queenagent-m63-test-design.md](../specs/2026-08-20-queenagent-m63-test-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adımlar

### 1. `FileRail.test.jsx` — üç test eklenir

| Test | Ne soruyor | Bugün |
|---|---|---|
| `an open file takes the rail over` | Okuyucu var, listeden hiçbir satır yok | Kırmızı — `sources.txt` orada |
| `while reading, the rail says nothing about a list` | `Project files` hiç geçmiyor | Kırmızı — etiket duruyor |
| `while reading, there is nothing to delete` | Hiçbir `Delete …` düğmesi yok | Kırmızı — yandaki satırlar taşıyor |

Üçü de **olumlu bir iddiayla birlikte** yazılıyor: her biri önce okuyucunun gerçekten orada
olduğunu doğruluyor. Yoksa hiçbir şey çizmeyen bir ray da bu üç testi geçerdi — yokluk iddiası tek
başına neyin doğru olduğunu söylemez.

### 2. `workspace.css.test.js` — iki test eklenir

- `.rail__list` kuralının **kalmadığı**. `rule()` yardımcısı kullanılamaz: kendisi kuralın
  varlığını iddia ediyor, yani silinmiş bir kuralı sormak yardımcının kendi assert'ini düşürür ve
  test yanlış sebeple kırmızı olur. Doğrudan `CSS` metnine sorulur.
- `.rail--open`'ın **boşluk taşımadığı**. `gap`, iki şeyi ayırmak içindi; ayrılacak iki şey yok.

Bunlar davranış testi değil, **kilit** — dosyanın diskten okunması bunu baştan söylüyor. Ama ikisi
de bugün gerçekten kırmızı, çünkü ikisi de var olan bir şeyin yokluğunu iddia ediyor.

### 3. `App.test.jsx` — bir test eklenir

Uçtan uca, ve kararın dayandığı sözü tutan tek test: sohbette dosya açılır → rayda `Project files`
de bir satır da kalmaz → `←` basılır → ikisi de geri gelir.

App seviyesinde, çünkü geri dönüşü sağlayan `close` rayın değil App'in; ray onu yalnız çağırıyor.
Mevcut `withRail()` yardımcısı kullanılır.

## Beklenen kırmızı

**Altı test.** FileRail üç, biçem iki, App bir. Hepsi arayüz tarafında; backend'e dokunulmuyor,
yani `python -m pytest queen-agent -q` **382'de yeşil kalmalı** — kalmazsa bu maddenin kapsamı
sızmış demektir ve orada durulur.

**Sonuç: 6 kırmızı / 480**, ve backend 382'de kaldı. Altısı da doğru sebeple düşüyor — her hata
mesajı orada olmaması gereken şeyi gösteriyor, boş bir ekranı değil.

Bir de koşarken düzeltildi: `.rail__list` testi önce `not.toContain` ile soruluyordu ve bu
kadar büyük bir dosyada başarısız bir `toContain` **stylesheet'in tamamını** basıyor. Kuralı bir
gün geri ekleyen kişiye kendi eklediği satırı göstermek gerekiyordu, yirmi bin satırı değil —
satır listesine çevrildi, iddia aynı kaldı.

## Bu turda yapılmayan

Hiçbir üretim kodu, hiçbir biçem satırı, hiçbir belge. Ve **silinecek olan hiçbir eski test**:
`another file can be reached without closing the one open`, `the row of the file being read is the
marked one`, `a rail row deletes while a file is open beside it`, `the row of the file being read
carries no ×`, `an open file widens the rail rather than taking it over`, `while reading, the list
keeps its label and loses its control` — hepsi yerinde durur ve yeşil kalır. Anlattıkları davranış
hâlâ orada; ikinci turda onunla birlikte giderler.

Bu commit'te `FileRail.test.jsx` kendi kendisiyle çelişir: hem "liste yanında durur" hem "liste
yok" der. Kırmızı commit'in tanımı bu.
