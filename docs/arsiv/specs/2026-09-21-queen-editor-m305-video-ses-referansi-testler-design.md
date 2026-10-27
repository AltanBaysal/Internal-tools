# Madde 305 — Video ve ses referansları da giriyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Bir ara REF2VA'ya konmuş bir Export (API) dosyası istenecekti;
**node'un kaynağı okununca gerek kalmadı** *(21 Eylül)*.

## Madde ne diyor

> Timeline'a video ve ses satırları da yazılıyor. **Alanları node'un kaynağından okundu**: bir satır
> `type` *(`image` · `video` · `audio`)*, `value`, `slot`, `order`, `enabled`, `trim_start` /
> `trim_end`, `duration`, `start`, `id` taşıyor. Yalnız video satırında bir alan daha var:
> **`media_mode`** — `video` · `audio` · `video_audio`.

304 fotoğrafları yazdı ve satırın şeklini kurdu; bu madde **üç tipi birden** yazıyor.

## Kararlar

**Tip eşleşmesi:** havuzun `picture` → `image`, `video` → `video`, `audio` → `audio`. Havuzun
sözcükleri H3'ün etiketleri *(`<Picture N>`)*, satırın sözcükleri node'un kendi alan değerleri; ikisi
bir yerde eşleşiyor, ve o yer üreticidir.

**`media_mode` yalnız video satırında**, ve değeri **`video_audio`**: havuzdaki bir video
referansının hem görüntüsü hem sesi H3'e gitsin — kullanıcı onu havuza *"bunun gibi olsun"* diye
koyuyor, ve yarısını atmak için bir sebep yok. Arayüzdeki V / A / V+A düğmelerinin karşılığı bu
alan.

**`trim_start` / `trim_end` yazılmıyor:** node'un kendi varsayılanları `0` ve `None`, yani kırpma
yok — ve havuza giren klip zaten sınırlardan geçmiş *(298)*. Kırpma kullanıcının isteyeceği bir şey
olursa kendi maddesi olur.

**Yükleme yolu aynı:** video ve ses de fotoğraf gibi ComfyUI'ye yükleniyor ve adıyla anılıyor —
üreticinin bugünkü `upload_image` yolu. *(Node dosyayı adıyla arıyor; bu yolun video ve ses için de
çalıştığı Colab'da görülecek — koşunun sonunda kullanıcı deniyor.)*

**Sıra tek sayaç:** `slot` ve `order` havuzun kendi sırasından, tipe bakmadan — H3 referansları
**tipe göre ayrı** numaralandırıyor *(`<Picture 1>`, `<Video 1>`)*, ama satırın `order`'ı
timeline'daki yeri. Yani sayaç listenin kendisi.

## Yazılacak testler — `backend/tests/test_comfy_h3_video_generator.py`

1. **üç tip de timeline'a yazılıyor**, her biri kendi `type` değeriyle.
2. **üçü de yükleniyor.**
3. **`media_mode` yalnız video satırında**, ve `video_audio`.
4. **sıra havuzun sırası** — `slot` ve `order` tipe bakmadan artıyor.
5. **`trim_start`/`trim_end` yazılmıyor** — node'un varsayılanına dokunulmuyor.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` kırmızı.
