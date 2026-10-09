# Madde 235 · Birleşik export parçalarını Drive'a bırakmaz — test turunun planı

**Spec:** [test turu](../specs/2026-09-17-queen-editor-m235-birlesik-export-parcalari-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Adımlar

**1 · `test_export.py`.** `ExportStore` sahtesine `make_pieces_dir` eklenir; çağrıldığını yazar ve
Drive'ın dışında bir yol döndürür *(`/tmp/fake-pieces`)*, böylece testler hedefin export klasörü
olmadığını okuyabilir.

| Test | Olgu |
|---|---|
| `a_merged_export_writes_its_pieces_outside_the_drive_folder` | 1 |
| `a_merged_export_joins_into_the_drive_folder` | 2 |
| `a_merged_export_takes_its_pieces_away_and_leaves_the_export_alone` | 3 |
| `a_merged_export_leaves_the_photos_in_the_drive_folder` | 4 |
| `a_separate_export_writes_its_pieces_into_the_drive_folder_and_removes_nothing` | 5 |
| `a_merged_export_that_blows_up_leaves_neither_folder_behind` | 6 |
| `a_cancelled_merged_export_leaves_neither_folder_behind` | 7 |

**2 · `test_photo_store.py`.** `make_pieces_dir` gerçek depoda: Drive kökünün altında olmayan, var
olan bir klasör döndürür, ve `remove_dir` onu kaldırır. Olgu 8.

**3 · Takım koşulur**, dördü de. Beklenen: yalnız **queen-editor'ün arka ucu kırmızı**.

**4 · Kırmızı commit'lenir.**
