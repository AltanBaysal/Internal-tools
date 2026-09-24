# Madde 293 — Bağımlılık, implementasyon turunun planı

**Spec:** [m293 implementasyon turu](../specs/2026-09-21-queen-editor-m293-bagimlilik-uygulama-design.md)

Üç dosya, hepsi `domain/`: `layers.py`, `usecases/remove_layer.py`, `usecases/queue_layer.py`.
Test dosyalarına dokunulmaz — turun testleri `e58cb037`'de yazıldı.

## Adımlar

1. **`layers.py` — tablo.** `TAKEN`'ın ardına `NEEDS = {AUDIO: VIDEO}`, ve onu iki yönde okuyan
   `falls_with(kind)`. Sıra `ORDER`'ın sırası olacak, ama `layers.py` `queue`'yu import edemez
   *(tersi doğru: `queue` `layers`'ı okuyor)* — sıra yerel `_ORDER` ile değil, **özyinelemeli inişin
   kendi sırasıyla** verilir: önce katman, sonra ona bağlı olanlar. Bugünkü tek zincirde bu
   `(video, audio)` demek, yani testin beklediği sıra.

2. **`can_produce` tabloyu okur.** Ses özel durumu `under = NEEDS.get(slot)` satırına iner.

3. **`remove_layer` `falls_with`'i okur.** `over` satırı değişir; gerisi aynı kalır, çünkü `over`
   zaten yuva listesi olarak kullanılıyor. `queue` import'u dosyada kalıyor — `DELETED`/`REMOVED`
   hâlâ oradan yazılıyor.

4. **`frames_in_scope` tabloyu okur.** Ses kontrolü `under = layers.NEEDS.get(kind)` üzerinden
   yazılır; bozuk katman kontrolü korunur.

5. **Üç dosyanın açıklamaları düzeltilir** — spec'teki üç madde.

6. **Dört test satırı koşulur.**

## Beklenen yeşil

Turun dört testi döner. Düşen tek bir test bile kuralın taşınırken değiştiği anlamına gelir; özellikle
bakılacaklar: `test_deleting_a_video_takes_the_sound_over_it`, `test_audio_skips_a_video_that_blew_up`,
ve `test_layers.py`'ın bugünkü `can_produce` testleri.

## Bu turda yapılmayacaklar

`REMOVABLE`/`QUEUEABLE` *(294)*, üretici *(304)*, frontend *(hiç dokunulmuyor)*.
