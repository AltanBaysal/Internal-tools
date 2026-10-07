# Madde 283 · Tekli çıktılar kendi klasörüne — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m283-klasorler-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**`make_videos_dir(folder)` store'a geliyor** — tarihli klasörün içinde `video/`. Klasör
düzenini bilen tek katman store *(CODE-STANDARD: `data/`)*, ve `run_export` yalnız hangi adımın
nereye yazdığını söylüyor.

**`PHOTOS_DIR` artık `"foto"`.** Tek sabit, tek satır — ad iki yerde yazılmıyor. **Eski
export'lara dokunulmuyor:** her export kendi tarihli klasörüne yazıyor, eskiler `photos/` adıyla
duruyor. Türkçe seçilmesinin sebebi kullanıcının onayı ve CODE-STANDARD'ın kuralı: Drive'da
görülen ad kullanıcıya bakan metindir.

**`run_export`'un kesme yeri moda göre:** birleşikte `/tmp` *(235)*, teklide `video/`.

**Ve silme koşulu yola değil moda bağlanıyor** — maddenin tuzağı buydu:

- Bugün: `if cutting != folder: store.remove_dir(cutting)`
- Olacak: `if mode == MERGED: store.remove_dir(cutting)`

Koşul `/tmp`'deki parçalar için yazılmıştı; videolar kendi klasörüne girince **teklide de
sağlanırdı**, ve kullanıcının teslim edilen videolarını silerdi. Aynı düzeltme `_clean`'de de
gerekiyor — orada silmek zararsız *(klasör zaten gidiyor)* ama koşulun anlamı yine moda ait, ve iki
yerde iki farklı kural okunmaz. **FOUNDATION 1**, ve testi var.

## Bunun getirdiği

Tarihli klasör **iki isme** iniyor: teklide `video/` ve `foto/`, birleşikte `<proje>.mp4` ve
`foto/`. Numaralar değişmiyor *(236)*: `foto/03.png` hâlâ `video/03.mp4`'ün fotoğrafı.

## Bu turda değişen

- `data/photo_store.py`: `make_videos_dir` geldi, `PHOTOS_DIR` Türkçeleşti.
- `domain/usecases/run_export.py`: tekli mod `video/`'ya kesiyor, ve silme koşulu moda bağlandı.
