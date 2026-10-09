# Madde 251 · Grafikler de `assets/` altına — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Klasör 249'da açıldı, ve taşınacak dosyalar depoda duruyor.

## Bugün ne oluyor

Beş grafik `queen-editor/` kökünde: `workflow_api.json`, `workflow_video_api.json`,
`workflow_video_first_last_api.json`, `workflow_video_h3_api.json`,
`workflow_video_h3_first_last_api.json`.

Adlarını üç yer söylüyor:

- **`config.py`** — beş sabit, yolu kuran tek yer.
- **Defterin Clone hücresi** — beşini de sayıyor ve `CLONE_DIR/queen-editor/<ad>` var mı diye
  bakıyor; yoksa koşuyu orada durduruyor.
- **`test_producer_contract.py`** — üçünü kökten kendisi kuruyor, `config`'e sormadan. Aynı yolun
  ikinci evi, ve taşınmada kırılacak olan da bu.

## Bu madde davranışı değiştirmiyor

Ekranda, export'ta, üretimde değişen hiçbir şey yok — dosyalar yer değiştiriyor. O yüzden
çivilenecek olgular da davranış değil **yerleşim**: dosya nerede, ve onu arayan yerler oraya mı
bakıyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | `queen-editor/` kökünde grafik JSON'u kalmamış | **kırmızı** |
| 2 | `config`'in adını söylediği beş grafik de duran birer dosya | **yeşil** *(taşımanın silmeye dönüşmediğini tutuyor)* |
| 3 | Defterin Clone hücresi grafikleri `assets/` altında arıyor | **kırmızı** |

**2 bugün de geçiyor, ve bilerek.** 1 tek başına yanlış bir yolla da yeşile döner: dosyaları silmek
de kökü temizler. İkisi birlikte taşımayı zorluyor.

**Defterin kendisi çivileniyor, çünkü onu yalnız Colab kırar.** Uygulama `config`'ten okuyor, yani
yol yanlışsa testler bunu görmez; defter ise klonu kontrol ediyor ve eski yere bakarsa koşu *"Grafik
yok"* diyerek orada durur — bir sonraki oturum bunu ancak Colab'da öğrenir.

## Bu turda değişen

- `backend/tests/test_producer_contract.py`: `no_graph_is_left_in_the_tool_root` *(1)* ve
  `every_graph_config_names_is_a_file` *(2)*. Bu dosyada, çünkü başlığı zaten *"grafikler
  gönderilmiş olanlar"* diyor — grafiklerin nerede durduğu aynı sorunun devamı.
- `backend/tests/test_notebook_installs_the_producer_groups.py`:
  `the_clone_looks_for_the_graphs_under_assets` *(3)*.

Uygulama turunda ayrıca `test_producer_contract.py`'nin kendi üç yolu `config`'in sabitlerine
dönüyor — yeni bir olgu değil, ikinci evin kapanması.
