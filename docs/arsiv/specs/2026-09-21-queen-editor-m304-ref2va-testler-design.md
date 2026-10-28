# Madde 304 — Üretici REF2VA'yı koşuyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok.

## Madde ne diyor

> H3 üreticisi `mode`'u `REF2VA` yapıyor, havuzun fotoğraflarını ComfyUI'ye yükleyip timeline'a
> yazıyor, mp4'ü alıyor. **Grafik değişmiyor**; fotoğraf referansının alanları elimizdeki
> export'tan okunuyor.

Export okundu ve alanlar doğrulandı *(`workflow_video_h3_api.json`)*: `mode` düz bir metin girdisi
*(`I2VA` / `FL2VA`)*, ve timeline satırı `{id, enabled, order, slot, start, duration, type, value,
thumbnail, source_width, source_height}` taşıyor. Yani REF2VA için **yeni export gerekmiyor**:
kip bir dize, ve `ref2va_model` yuvası zaten dolu.

## Referanslar üreticiye nasıl gidiyor

Üretici portu bir alan daha alıyor: **`references`** — `(ad, baytlar, tip)` üçlüleri, havuzun kendi
sırasında. Bütün üreticiler alıyor ve çoğu kullanmıyor, çünkü **kuyruğun tek bir çağrı şekli var**
*(port'un kendi kuralı, `source` ve `end` de öyle)*.

Döngü onları **işin sırası gelince** okuyor, plandan değil: kullanıcının kararı buydu — *"tekrar
dene havuzun o anki hâliyle üretir, kart kendi referanslarını hatırlamaz"*. Döngüye bir çağrılabilir
veriliyor *(`references(project)`)*, `stills` ve `writers`'ın gittiği yoldan.

**Yalnız referans kipindeki iş** onları alıyor; sıradan bir video işi bugünkü gibi kaynak
fotoğrafıyla üretiliyor.

## Üretici ne yapıyor

Referans geldiğinde:
- `mode` → **REF2VA**, ve **kaynak fotoğraf istenmiyor** — referans modunda kart fotoğrafsız doğar.
- Havuzun **fotoğrafları** yükleniyor ve timeline satırları onlardan yazılıyor: `type: "image"`,
  `value` yüklenen ad, `slot`/`order`/`start` sıradaki yeri, `enabled: true`, `duration: 1` —
  export'un kendi alanları.
- **Prompt olduğu gibi yazılıyor**: I2VA/FL2VA'nın resim cümlesi eklenmiyor, çünkü REF2VA'nın
  prompt'u kullanıcının kendi altı bölümlü metni *(yol haritasının kararı)*.
- Video ve ses referansları **bu maddede yok** — 305 onları ekliyor.

**`source_width` / `source_height` yazılmıyor:** yüklenen dosyanın boyutunu üretici bilmiyor ve
uydurmak yanlış bir sayı yazmak olurdu. Grafikte `ref_image_size` girdisi ayrıca duruyor, yani
ölçeği node'un kendisi biliyor. Bu bir **karar**, ve kullanıcı koşunun sonunda Colab'da denerken
görülecek.

## Yazılacak testler

### `backend/tests/test_comfy_h3_video_generator.py`

1. **referanslarla `mode` REF2VA oluyor.**
2. **her fotoğraf referansı yükleniyor ve timeline'a sırasıyla yazılıyor.**
3. **kaynak fotoğraf istenmiyor.**
4. **prompt olduğu gibi gidiyor** — resim cümlesi eklenmiyor.
5. **referanssız üretim bugünkü gibi** *(bekçi)*.

### `backend/tests/test_photo_usecases.py`

6. **referans kipindeki iş havuzun dosyalarını alıyor.**
7. **sıradan video işi referans almıyor.**

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` kırmızı.
