# Madde 296 — İlk kare, test turunun planı

**Spec:** [m296 test turu](../specs/2026-09-21-queen-editor-m296-ilk-kare-testler-design.md)

İki test dosyası: `backend/tests/test_frame_queue.py` *(döngü)* ve yeni
`backend/tests/test_ffmpeg_stills.py` *(araç)*. Kaynak koda dokunulmuyor.

## Adımlar

1. **Sahte çıkarıcı** — `test_frame_queue.py` içinde, kendisine gelen baytları saklayan ve sabit bir
   PNG döndüren küçük bir sınıf. Patlaması istenen testte aynı sınıf bir hata fırlatır; ikinci bir
   sahte yazmaya gerek yok.

2. **Altı döngü testi**, dosyanın video bölümünün ardına. Kurgu oradaki testlerin kendi
   yardımcılarıyla yapılır — yeni bir proje kurgusu icat edilmez.

3. **`test_ffmpeg_stills.py`** — `test_ffmpeg_audio.py`'ın `FakeRun`'ı aynı şekilde yazılır: iki
   dosya iki aracı denediği için ortak bir yardımcıya taşınmaz, ve o dosyanın kendi kurgusu
   okunabilirliğinin yarısı.

4. **Dört test satırı koşulur.**

## Beklenen kırmızı

Altı kırmızı: `stills` diye bir argüman yok *(TypeError)* ve `FfmpegStills` diye bir sınıf yok
*(ImportError)*. Üç bekçi testi — resmi olan kart, kırmızı yuva, port verilmemiş hâl — bugün de
yeşil geçer, ama ilk ikisi `stills` argümanını verdiği için onlar da `TypeError` ile düşer. Yani
**kırmızı sayısı sekiz**, ve düşme sebebi hepsinde aynı: henüz yok.

## Bu turda yapılmayacaklar

Kod yok, port yok, `main.py` yok.
