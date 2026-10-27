# Madde 289 · Videolar, fotoğraflar, disclaimer — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m289-ayri-adimlar-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · İptal kendi işlevine.** `_stopped(runner, store, mode, folder, scaffolding)` — iptal
edilmişse temizler, `idle` bildirir, `True` döner. Bugünkü satırların taşınmış hâli; yorum da
onunla birlikte gidiyor.

**2 · Birinci döngü yalnız video.** Fotoğraf satırları çıkıyor; `piece`, `pieces.append` ve
`report(written=index)` kalıyor.

**3 · İkinci döngü yalnız fotoğraf.** Aynı `enumerate(frames, start=1)`, başında `_stopped`
kontrolü, `written` kümesi ve *"bir kez"* kuralı burada.

**4 · Takım:** dört satır paralel. Üç kırmızının yeşile dönmesi, numaralandırmayı ve paylaşılan
fotoğrafı tutan beş testin yeşil kalması beklenir.

**5 · Commit** (yeşil).
