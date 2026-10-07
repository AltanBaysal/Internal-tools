# Madde 236 · Export her fotoğrafı bir kez yazar — test turunun planı

**Spec:** [test turu](../specs/2026-09-17-queen-editor-m236-export-fotograf-tekrari-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Adımlar

**1 · `test_export.py`.** Yeni bir kurulum: kaynağının fotoğrafını gösteren, kendi videosu olan bir
kopya kare. Bugünkü `with_videos` iki ayrı fotoğraflı kare veriyor, yani tekrarı gösteremez.

| Test | Olgu |
|---|---|
| `frames_sharing_one_photo_leave_one_picture_in_the_export` | 1 |
| `a_shared_photo_is_filed_under_the_first_frame_that_uses_it` | 2 |
| `a_copy_frames_video_is_written_all_the_same` | 3 |
| `a_merged_export_writes_the_shared_photo_once_too` | 4 |
| `frames_with_pictures_of_their_own_each_leave_one` | 5 |

**2 · Takım koşulur**, dördü de. Beklenen: yalnız **queen-editor'ün arka ucu kırmızı**.

**3 · Kırmızı commit'lenir.**
