# Madde 297 — Referans havuzu, test turunun planı

**Spec:** [m297 test turu](../specs/2026-09-21-queen-editor-m297-referans-havuzu-testler-design.md)

Üç **yeni** test dosyası: `backend/tests/test_references.py`,
`backend/tests/test_reference_usecases.py`, `backend/tests/test_reference_routes.py`. Var olan
hiçbir test dosyasına dokunulmuyor — referans kapıları kendi blueprint'inde olduğu için kartların
`make_client`'ı kıpırdamıyor.

## Adımlar

1. **`test_references.py`** — beş kural testi, `domain/references.py`'ı çağırarak.

2. **`test_reference_usecases.py`** — sahte bir depo *(`FakeReferenceStore`)* ve sahte bir
   `FakeStore` *(`project_exists` için)* ile yedi test. Sahteler bu dosyanın kendi başında durur:
   `test_photo_usecases.py`'ın sahteleri kartlar içindir, ve oradan almak iki dosyayı birbirine
   bağlardı.

3. **`test_reference_routes.py`** — kendi istemcisini kurar: gerçek `DriveStorage`, gerçek depo,
   gerçek kullanım senaryoları, ve yalnız referans blueprint'i. Yeniden başlatma, aynı klasöre
   ikinci bir istemci kurarak modellenir — `give_it_a_video`'nun ikinci bir `DrivePhotoRecord`
   kurmasıyla aynı numara.

4. **Dört test satırı koşulur.**

## Beklenen kırmızı

Üç dosya da **toplamada** düşer: ne `domain/references.py`, ne kullanım senaryoları, ne
`data/reference_store.py`, ne de blueprint var. 296'da olduğu gibi tek tek kırmızıları görmek
implementasyon turunun işi: modüller doğar, takım koşulur, ve testler kendi hatalarını söyler.
Var olan 981 testin hiçbiri kıpırdamaz.

## Bu turda yapılmayacaklar

Kod yok, `main.py` yok.
