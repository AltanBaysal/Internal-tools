# Madde 296 — İlk kare, implementasyon turunun planı

**Spec:** [m296 implementasyon turu](../specs/2026-09-21-queen-editor-m296-ilk-kare-uygulama-design.md)

On dosya: yeni `data/ffmpeg_stills.py`, `domain/ports.py`, `domain/run_loop.py`, kuyruğa açılan yedi
kapı, ve `main.py`. Testlere dokunulmaz — turun testleri `e3607a90`'da yazıldı.

## Adımlar

1. **`FfmpegStills`** yazılır.

2. **Takım koşulur** — döngüye dokunmadan. Beklenen: araç testleri yeşil, altı döngü testi
   `TypeError: make_job() got an unexpected keyword argument 'stills'`. Kırmızı commit'in
   göremediği kırmızı budur.

3. **`ports.Stills`** eklenir.

4. **`run_loop`:** `make_job` `stills=None` alır; videonun satırından sonra yuva boşsa resim
   yazılır, `try` içinde.

5. **Yedi kapı** parametreyi taşır — her biri iki satır.

6. **`main.py`** aracı kurar ve altı `partial`'a verir.

7. **Dört test satırı koşulur.**

## Beklenen yeşil

Turun on testi döner. Özellikle bakılacaklar: `test_producer_contract.py`'ın uçtan uca koşusu
*(orada `stills` yok, yani hiçbir şey çıkarılmamalı)* ve videolu bütün döngü testleri.
