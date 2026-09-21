# Madde 287 · Ekran her adımı adıyla ve süresiyle söyleyecek — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m287-adim-sureleri-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · Arka uç — adımların sırası.** Bir koşucuya sahte saat verilir; birleşik koşu sonunda
`state()["merged"]["steps"]` dört adımı sırayla ve süresiyle söyler. Olgu 1, 2, 3.

**2 · Arka uç — tekli koşu.** Aynı sahte saatle, `steps` iki adım: `running`, `photos`. Olgu 4.

**3 · Arka uç — meşgul olmak.** `photos` durumundaki bir modda `start` `False` döner. Olgu 5.

**4 · Arka uç — iptal.** İptal edilen koşunun `steps`'i boş. Olgu 6.

**5 · Arka uç — saat adım başına.** 22 kareli bir koşuda saat okuması adım sayısı kadar. Olgu 7.

**6 · Ayarlanan test.** `test_the_state_counts_what_has_been_written`'a `steps` alanı eklenir;
sorusu aynı kalır.

**7 · Ön yüz — iki yeni cümle.** `photos` → *"Fotoğraflar ekleniyor…"*, `saving` → *"Drive'a
kopyalanıyor…"*, ikisinde de düğme basılamaz. Olgu 8.

**8 · Ön yüz — adım listesi.** `steps` verilen bir durumda ekran adları ve `12,4 sn` biçiminde
süreleri gösterir. Olgu 9.

**9 · Takım:** dört satır paralel. Kırmızı iki yerde: queen-editor arka ucu ve ön yüzü.

**10 · Commit** (kırmızı). `dist` bu turda **build'lenmiyor** — ön yüz kaynağı henüz değişmedi,
yalnız testleri yazıldı.
