# Madde 226 · Nova Orange ve Nova Anime kaldırılacak — test turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Karar 17 Eylül'de verildi: eski adla kayıtlı bir proje **sessizce Nova 3DCG'ye düşer**.

## Bugün ne oluyor

Tarif dört yerde duruyor, ve testler dördünün eşleştiğini tutuyor:
[`recipes.py`](../../../queen-editor/backend/features/photo_generation/domain/recipes.py), defterde
`PHOTO_CHECKPOINTS`, `PHOTO_RECIPES` ve CONFIG kutuları *(kutu kontrolü de kutulardan türüyor)*.

Kayıtlı bir değer iki yerde yaşıyor. Projenin ayarlarında *(panelin açılışta seçtiği model)*, ve
planın her karesinde *(render'ın okuduğu model)*. Kuyruğa girmiş ya da yeniden üretilen bir kare
`recipe:novaorange` taşıyorsa, render bugün `Tanınmayan tarif` diye duruyor
*(`ComfyPhotoGenerator._recipe`)*.

## Ne olacak

- **İki tarif siliniyor.** Liste `nova3dcg` ve `slime`.
- **Defter yalnız Nova 3DCG'nin checkpoint'ini tanıyor.** Orange ile Anime'nin dosya adları ve
  version id'leri defterden çıkıyor, kutuları da.
- **Eski ad render'da Nova 3DCG'ye düşüyor.** `recipe:novaorange` ya da `recipe:novaanime` taşıyan bir
  kare Nova 3DCG'nin checkpoint'i ve lora dizilimiyle üretiliyor, hata vermeden. Bilinmeyen **başka**
  bir ad yine duruyor: o bir çökme değil, bir koruma *(`test_an_unknown_recipe_stops_the_render`)*.

**Panelin tarafı.** Proje ayarları `projects` özelliğinde duruyor, ve `feature ↛ feature` yasağı
yüzünden tarif kimliklerini orada çeviremeyiz. Bu yüzden eski adla kayıtlı bir projenin panelinde
bugünkü *"Bu model artık kurulu değil."* notu görünür. Not doğru, ve üretmeye basmak artık çökmüyor:
kare Nova 3DCG ile çıkıyor. Kullanıcıya göre bu iki model kullanılmıyordu, yani etkilenen proje
muhtemelen yok. Paneli de susturmak için yasağı delmek, kazancından pahalı.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Tarif listesi yalnız `nova3dcg` ve `slime` | **kırmızı** |
| 2 | Defter Orange ile Anime'nin ne dosyasını ne version id'sini taşıyor | **kırmızı** |
| 3 | `recipe:novaorange` Nova 3DCG'nin checkpoint'iyle ve lora'sıyla render ediliyor | **kırmızı** |
| 4 | `recipe:novaanime` da öyle | **kırmızı** |

Defterin kutu, satır ve kontrol eşleşmesi zaten çivili, ve tarif listesinden türüyor. Olgu 1 yeşile
dönünce o testler dört kutuya karşı kırmızı olacak, ta ki defter de değişene kadar. Bu yüzden
uygulama turu ikisini birlikte değiştiriyor.

## Bu turda değişen

Yalnız testler: `test_photo_usecases.py` *(1)*, `test_notebook_installs_the_producer_groups.py`
*(2 — bugünkü üç checkpoint'i çivileyen test yeniden yazılıyor)*, `test_comfy_photo_generator.py`
*(3, 4)*.
