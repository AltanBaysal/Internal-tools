# Madde 236 · Export her fotoğrafı bir kez yazar — test turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Karar 18 Eylül'de verildi: fotoğraf bir kez yazılır, numarası karesinin numarası kalır.

## Bugün ne oluyor

[`run_export.py`](../../../queen-editor/backend/features/photo_generation/domain/usecases/run_export.py)
her kareye sırayla bir numara veriyor ve o karenin fotoğrafını `photos/` klasörüne o numarayla
kopyalıyor. Bir kopya kare kendi fotoğrafını üretmiyor — kaynağının dosyasını gösteriyor — yani aynı
dosya kaç kopya kare varsa o kadar kez, farklı numaralarla yazılıyor.

`copy_photo` hedefi zaten oradaysa yazmıyor, ama burada hedefler farklı: `02.png` ile `03.png` aynı
resim olsa da iki ayrı ad.

## Ne olacak

**Bir fotoğraf dosyası bir kez yazılır**, ve numarası onu ilk kullanan karenin numarası olur.
Sonraki kopya kareler fotoğraf yazdırmaz. Numaralarda boşluk olabilir: `01.png`, `02.png`, `05.png`.

Bu **iki export modunda da** aynı. **Videolara dokunulmuyor:** kopya karenin videosu kendi dosyası
ve dizideki yerini koruyor, yani `03.mp4` hâlâ yazılıyor, yalnız `03.png` yazılmıyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Aynı fotoğrafı paylaşan kareler tek bir fotoğraf yazdırıyor | **kırmızı** |
| 2 | Yazılan fotoğrafın numarası onu ilk kullanan karenin numarası | **kırmızı** |
| 3 | Kopya karenin videosu eskisi gibi yazılıyor, dizide yeri duruyor | yeşil *(bekçi)* |
| 4 | Birleşik export'ta da aynı | **kırmızı** |
| 5 | Farklı fotoğrafları olan kareler bugünkü gibi her birini yazdırıyor | yeşil *(bekçi)* |

## Bu turda değişen

Yalnız testler: `backend/tests/test_export.py`.
