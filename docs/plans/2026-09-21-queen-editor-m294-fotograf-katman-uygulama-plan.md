# Madde 294 — Fotoğraf katmanı, implementasyon turunun planı

**Spec:** [m294 implementasyon turu](../specs/2026-09-21-queen-editor-m294-fotograf-katman-uygulama-design.md)

İki dosya: `domain/usecases/list_frames.py`, `presentation/routes.py`. Test dosyalarına dokunulmaz —
turun testleri `a4748173`'te yazıldı.

## Adımlar

1. **Yuvanın durumunu okuyan küçük bir yardımcı** — `list_frames` içinde bir işin kendi hücresini ve
   durumunu veren tek satır. Bugün aynı okuma iki yerde geçiyor *(açan işi bulurken ve kartı elerken)*,
   ve bu madde ikisini bir araya getiriyor.

2. **`opening` sözlüğü kapanmış işleri atlar.** `setdefault` çağrısından önce bir süzgeç: durumu
   `SHOWN`'da değilse ve açık değilse o iş kartı açamaz.

3. **Galeri döngüsü sadeleşir.** Eleme kontrolü kalkar — kart `opening`'de yoksa zaten satır açmaz.
   Döngü `opening.get(fid) is not frame` ile yürür.

4. **`file` süzgeçten geçer:** `photo["file"] if photo and layers.is_taken(photo["status"])`.

5. **`REMOVABLE` fotoğrafı alır**, yanındaki yorum düzeltilir.

6. **Modül açıklaması** kartın ne zaman galeride olduğunu söyleyen cümleyle güncellenir.

7. **Dört test satırı koşulur.**

## Beklenen yeşil

Turun beş testi döner. Özellikle bakılacaklar: 292'nin altı testi, `test_the_gallery_stops_reporting_-
a_deleted_layer`, ve galerinin sıralama testleri.

## Bu turda yapılmayacaklar

Ekran, `QUEUEABLE`, `remove_frames`.
