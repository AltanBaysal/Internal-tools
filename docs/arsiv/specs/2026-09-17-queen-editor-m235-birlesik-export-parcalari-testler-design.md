# Madde 235 · Birleşik export parçalarını Drive'a bırakmaz — test turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Kararlar 17 Eylül'de alındı: parçalar Colab'ın diskine yazılıp iş bitince silinecek,
fotoğraflar her hâlükârda kalacak, ayrı export'a dokunulmayacak.

## Bugün ne oluyor

[`run_export.py`](../../../queen-editor/backend/features/photo_generation/domain/usecases/run_export.py)
iki mod için de aynı döngüyü koşuyor: her kare için `store.export_path(folder, "01.mp4")` hedefine
bir parça yazılıyor, fotoğrafı `photos/`e kopyalanıyor, ve mod `merged` ise parçalar sonunda
`<proje>.mp4` olarak birleştiriliyor. Parçalar export klasöründe, yani **Drive'da** kalıyor.

Parçanın kendisi gereksiz değil: ses ayrı bir `.wav` ve birleştirmeden önce videoya gömülmek
zorunda. Gereksiz olan, o ara ürünün Drive'a yazılması.

## Ne olacak

1. **Birleşik export parçalarını Colab'ın kendi diskine yazar.** Depo *(`PhotoStore`)* bir çalışma
   klasörü açar; nerede olduğunu yalnız o bilir, kullanım durumu bilmez.
2. **Birleştirme bitince o klasör kaldırılır.** Drive'daki klasörde `<proje>.mp4` ve `photos/`
   kalır.
3. **Fotoğraflar iki modda da Drive'a yazılır.**
4. **Ayrı export değişmez:** parçaları bugünkü gibi doğrudan export klasörüne yazar, hiçbir şey
   silmez.
5. **Yarım kalan koşu** — hata ya da iptal — bugünkü gibi export klasörünü alır, **ve** çalışma
   klasörünü de bırakmaz.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Birleşik export parçalarını çalışma klasörüne yazıyor, export klasörüne değil | **kırmızı** |
| 2 | Birleştirmenin hedefi Drive'daki `<proje>.mp4` | yeşil *(bekçi)* |
| 3 | İş bitince çalışma klasörü kaldırılıyor, export klasörü duruyor | **kırmızı** |
| 4 | Birleşik export'un fotoğrafları Drive'daki klasörde | yeşil *(bekçi)* |
| 5 | Ayrı export parçalarını export klasörüne yazıyor ve hiçbir şey silmiyor | yeşil *(bekçi)* |
| 6 | Düşen bir birleşik koşu iki klasörü de bırakmıyor | **kırmızı** |
| 7 | İptal edilen bir birleşik koşu iki klasörü de bırakmıyor | **kırmızı** |
| 8 | Depo çalışma klasörünü Drive'ın dışında açıyor ve kaldırabiliyor | **kırmızı** |

## Bu turda değişen

Yalnız testler: `backend/tests/test_export.py` ve `backend/tests/test_photo_store.py`.
