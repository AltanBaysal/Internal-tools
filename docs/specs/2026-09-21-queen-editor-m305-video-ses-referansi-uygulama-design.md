# Madde 305 — Video ve ses referansları, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:**
[m305 test turu](2026-09-21-queen-editor-m305-video-ses-referansi-testler-design.md),
`5a9b63a7` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Tek dosya

`data/comfy_h3_video_generator.py`, ve içinde tek bir yer: havuzdan satır yazan döngü.

**Tip tablosu** üreticinin içinde duruyor — havuzun sözcükleri *(`picture`/`video`/`audio`)* ile
node'un alan değerleri *(`image`/`video`/`audio`)* burada buluşuyor, çünkü node'un sözlüğünü bilen
tek yer burası.

**`media_mode`** yalnız video satırına ekleniyor, değeri `video_audio`.

Gerisi 304'te kuruldu ve dokunulmuyor: sıra tek sayaç, `trim_*` yazılmıyor, yükleme yolu aynı.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil.
