# Madde 218 · Üretim yatay olacak — test turunun planı

**Spec:** [test turu](../specs/2026-09-16-queen-editor-m218-yatay-uretim-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. İkisi henüz olmayan davranışa göre yazılıyor:

- `merge`, birleştirmeden önce her parçanın ölçüsünü `ffprobe` ile sorar.
- Ayrışan ölçüde `RuntimeError`, içinde parça adları ve ölçüleri.

## Adımlar

**1 · `test_workflow_asset.py` — grafikler (olgular 1–5).** Üç grafik okunuyor; ölçüler node'lardan
alınıyor.

| Test | Ne bekler |
|---|---|
| `the photo graph renders the landscape size` | `1` → 1536, `11` → 864 |
| `both video graphs render the same landscape size` | `208` ve `328` → `Xi/Xf` 848, `Yi/Yf` 480, ve birbirine eşit |
| `the photo and the video agree on the shape of the frame` | iki oran arasındaki fark **< %1** |
| `every graph makes a landscape frame` | üçünde de genişlik > yükseklik |

Üçüncüsü mevcut `test_both_video_graphs_agree_on_how_long_a_render_runs`'ın eşi: orada süre, burada
oran — ikisi de bir grafiğin tek başına değiştirilmesine karşı.

**2 · `test_export.py` — birleştirme (olgular 6–10).** `FakeRun` ölçü sorulduğunda cevap verecek
hâle geliyor: dosya adına göre `stdout`, çünkü bugünkü hâli her çağrıya boş dönüyor.

| Test | Kurulum | Ne bekler |
|---|---|---|
| `merging asks every piece how big it is` | iki parça, aynı ölçü | her parça için bir `ffprobe` çağrısı, dosya adıyla |
| `merging hands ffmpeg a list and takes it away again` *(var olan)* | aynısı | `concat` komutu **değişmemiş** — çağrı sırası kaydığı için son çağrıya bakar |
| `mixed sizes stop the merge and name what was found` | `848x480` ve `480x720` | `RuntimeError`, içinde iki dosya adı ve iki ölçü |
| `a size that cannot be read says what ffprobe said` | `ffprobe` exit 1, stderr'de bir cümle | o cümle hatanın içinde |
| `nothing is merged when the sizes disagree` | aynı karışık kurulum | hiçbir `ffmpeg` çağrısı yok, `pieces.txt` diskte kalmamış |

**3 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: **yalnız `python -m pytest queen-editor` kırmızı**. Ön yüz bu maddeden etkilenmiyor
*(galeri karesi `1/1`, oynatıcı `16/9`)*, queen-agent hiç.

**4 · Kırmızı commit'lenir.**

## Değişen dosyalar

`queen-editor/backend/tests/test_workflow_asset.py`,
`queen-editor/backend/tests/test_export.py`.
