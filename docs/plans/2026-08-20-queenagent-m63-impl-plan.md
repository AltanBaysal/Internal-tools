# Madde 63 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-20-queenagent-m63-impl-design.md](../specs/2026-08-20-queenagent-m63-impl-design.md)
· tur 1: [test tasarımı](../specs/2026-08-20-queenagent-m63-test-design.md) ·
[test planı](2026-08-20-queenagent-m63-test-plan.md)

**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adımlar

### 1. `FileRail.jsx`

- Okuma dalı yalnız `<FilePanel>` döndürür. `rail__list` sarmalayıcısı, `rail__head--still`
  başlığı, etiket, sayı ve `FileList` çağrısı gider.
- `FileList`'ten iki ölü karşılaştırma çıkar (tasarım): `selected` ve silmenin okunan satırı
  atlaması.
- Sınıfın tepesindeki yorum düzeltilir: üç durum duruyor ama **liste ikisinde değil birinde**, ve
  `reading` artık "okuyucunun yanındaki liste" değil "yalnız okuyucu". Deponun kuralı — çakışan
  yorum koda uydurulur, `OLD:`/`NEW:` izi bırakılmaz.

### 2. `workspace.css`

- `.rail__list` kuralı silinir.
- `.rail--open`'dan `gap: 16px` çıkar. `display: flex` **kalır** — `.rail--open .reader`'ın
  `flex: 1`'i ona dayanıyor.
- `.rail--open`'ın üstündeki yorum ("okuma rayı boşaltmaz, liste yanında durur") ve içindeki
  padding yorumu ("padding'e ihtiyacı kalan şey liste") yeniden yazılır: ikisi de artık yanlış.

### 3. Anlattığı davranış giden testler

`FileRail.test.jsx`'ten **altı** test silinir:

| Test | Neden |
|---|---|
| `an open file widens the rail rather than taking it over` | Tur 1'in `takes the rail over`'ı yerini aldı |
| `while reading, the list keeps its label and loses its control` | Tur 1'in `says nothing about a list`'i yerini aldı |
| `another file can be reached without closing the one open` | Davranış kalktı |
| `the row of the file being read is the marked one` | Görünecek satır yok |
| `the row of the file being read carries no ×` | Görünecek satır yok |
| `a rail row deletes while a file is open beside it` | Görünecek satır yok |

`workspace.css.test.js`'ten:

- `while reading, the rail is two columns and the list keeps one` — ~~silinir~~ **yeniden yazıldı.**
  Silmeye gidildiğinde görüldü ki `.rail--open`'ın **560 piksellik genişliğini** tutan başka test
  yok; eski test `display: flex` ve listenin 200'ünü soruyordu, 560'ı değil. Silmek, kimsenin
  sormadığı bir sayı bırakırdı. İki iddiaya çevrildi: genişlik 560, ve tek çocukla da flex.
- `the room around the document belongs to the document` — **kalır**, içindeki `.rail__list`
  padding iddiası çıkar. Testin asıl konusu `.panel` ve `.rail--open`'ın padding'i; kalan iki
  iddia hâlâ doğru ve hâlâ değerli.
- `the row being read is marked, and hovering is not the same as being open` — **kalır.**
  `.file-row--selected` uygulamada çağıransız kalıyor ama `FileRow` yeteneği koruyor (tasarım).
  Testin yanına çağıransız kaldığı düşülür, yoksa okuyan biri nerede kullanıldığını arar.

`a rail showing a document has no grip` **kalır**: artık apaçık doğru, ama söylediği şey — okurken
genişlik belgenin — hâlâ bir kural.

`ChatScreen.test.jsx` dokunulmaz: ray satırlarını silen testi `reading` vermiyor, kontrol edildi.

### 4. `dist`

`npm run build --prefix queen-agent/frontend`, ve **aynı commit'te**. Deponun kuralı, ve
`test_dist_is_committed.py` alternatifi reddediyor.

## Beklenen yeşil

Tur 1'in altı kırmızısı. ~~Silinen yedi testle birlikte arayüz toplamı 480'den 473'e düşer.~~

**Sonuç: arayüz 474, backend 382.** Tahmin 473'tü ve fark tek bir sapmadan geliyor: yedinci test
silinmedi, yeniden yazıldı (yukarı bak). Yani düşen altı test, 480 − 6 = 474.

*(Bu ailenin planlarında tahminler yedi kez tutmadı. Sayılar koşudan sonra buraya düzeltiliyor.)*

## Kapanış denetimi

- `queen-agent/frontend/src` altında `rail__list` geçmiyor.
- Okuma hâlinde çizilen tek şey `FilePanel`.
- `selected` prop'unu geçen hiçbir çağıran yok — `FileRow`'un kendi testi hariç, ki o bilerek.
