# Madde 304 — Üretici REF2VA'yı koşuyor, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m304 test turu](2026-09-21-queen-editor-m304-ref2va-testler-design.md),
`c1b55ad8` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Port

`PhotoGenerator.generate` bir alan daha alıyor: `references=()`. Dört gerçek üretici de imzayı
alıyor, üçü kullanmıyor — `source` ve `end` de öyle: **kuyruğun tek çağrı şekli var.**

## Döngü

`make_job(..., references=None)` — proje adını alıp havuzun dosyalarını veren bir çağrılabilir.
`stills`'in gittiği yol, aynı yedi kapı.

Yalnız **kipi referans olan** iş onları alıyor. Sıradan bir video işi bugünkü gibi kaynak
fotoğrafıyla üretiliyor, ve referansı boş geçiyor.

`domain/usecases/reference_files.py` — havuzun dosyalarını `(ad, baytlar, tip)` olarak, **havuzun
kendi sırasında** veren küçük bir senaryo. Sıra `list_references`'ın verdiği sıra, yani kullanıcının
sürüklediği sıra: H3 referansları **sıraya göre** numaralandırıyor, ve prompt'taki `<Picture 2>`
oradan sayıyor.

## Üretici

Referans varsa: `mode` **REF2VA**, kaynak fotoğraf istenmiyor, timeline satırları havuzun
**fotoğraflarından** yazılıyor, prompt olduğu gibi giriyor. Yoksa bugünkü iki yol aynen duruyor.

Satırın alanları export'un kendi alanları; `source_width`/`source_height` **yazılmıyor** — üretici
yüklenen dosyanın boyutunu bilmiyor ve uydurmuyor.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil.
