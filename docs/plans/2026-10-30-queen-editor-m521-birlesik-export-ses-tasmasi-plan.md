# Madde 521 · Birleşik export'ta ses parçadan parçaya taşmaz — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-20), 521 · v11-20 ·
**Spec:** [2026-10-30-queen-editor-m521-birlesik-export-ses-tasmasi-design.md](../specs/2026-10-30-queen-editor-m521-birlesik-export-ses-tasmasi-design.md)

Önce ölçüm: gerçek ffmpeg'le nedeni bul, taşmayı göster (kırmızı). Sonra test: testler yeni kuralı söyler
(kırmızı), sonra kod (yeşil), sonra aynı ölçüm (yeşil). Ekrana dokunulmaz, `dist` derlenmez.

## 0. Ölçüm (depoda değil, `tmp/m521/`)

- `measure.py`: deponun `FfmpegVideoExporter`'ı, imageio-ffmpeg'in 7.1 ikilisiyle. ffprobe'un yerine
  sesin biçimi `ffmpeg -i`'den, akışın süresi mp4'ün `mdhd`'sinden. Parçaları üretir (`S`/`W`/`M`),
  birleştirir. Her parçanın resim ve ses süresini, birleşik dosyada tekrarlanan kareleri, her sesli
  parçanın sesinin sonraki parçaya ne kadar taştığını yazar.
- `before_exporter.py`: `git show HEAD:…/ffmpeg_video_exporter.py`. `M521_BEFORE=1` ölçümü onunla koşar.
- Önce: `before-1..5.txt`. Sonra: `after-1..5.txt`.

## 1. Testler — `backend/tests/test_export.py`

- `FakeRun` ffprobe'un JSON'unu verir: resim akışı `duration`'ıyla (`lengths`, varsayılan `LENGTH` =
  `"3.000000"`, `None` anahtarı bırakır), ses akışı `sounds`'taki "rate,layout"tan.
- `sound_calls` soruyu `-show_entries`'ten tanır.
- `expected_graph(count, sounded=True)` her parçanın sesini `atrim=end=3.0`'la keser, `[vi][ai]`
  birleştirir.
- `test_the_filtergraph_word_for_word`: ikinci parçanın resmi 5.041667, grafikte iki `atrim`.
- `test_the_question_asked_of_a_piece_is_written_out_word_for_word` (eski adı
  `test_the_sound_question_…`): JSON'lu tek komut.
- Yeni: `test_each_pieces_sound_ends_where_its_picture_ends`,
  `test_the_silence_written_into_a_piece_is_cut_at_its_picture_too`,
  `test_a_join_with_no_sound_cuts_nothing`,
  `test_a_picture_ffprobe_gives_no_length_joins_its_sound_uncut` (`None`, `N/A`).
- Reviewer'dan sonra: `test_silence_names_only_the_shape_ffprobe_gave`,
  `test_silence_with_no_shape_at_all_takes_anullsrcs_own`,
  `test_an_answer_that_is_not_json_says_which_file_and_what_ffprobe_wrote`. `FakeRun` ffprobe'un
  bilmediği değeri yazmaz, `probe_stdout` ham bir cevap verir.

## 2. Kod — `backend/features/photo_generation/data/ffmpeg_video_exporter.py`

- `sound` → `streams`: tek ffprobe çağrısı, `-of json`. `(resmin süresi | None, (rate, layout) | None)`
  döner. Süre `float`, yoksa ya da okunamazsa `None`. JSON olmayan cevap
  `RuntimeError("<parça>: ffprobe JSON yerine şunu yazdı: …")`.
- `_evened_out`: `(parçalar, kesimler | None)`. Kesimler her parçanın resim süresi, sessizlik yazılan
  parça için asıl parçanınki.
- `_filtergraph(count, cuts)`: sesli sette `[i:a]atrim=end=<kesim>[ai]` ve `[vi][ai]…concat`; kesimi
  `None` olan parça `[vi][i:a]`.
- `_with_sound`: `anullsrc`'a yalnız verilen değerler (`r=`, `cl=`).
- `merge`: `sounded` yerine `cuts`. Docstring'ler ve `__init__`'teki ffprobe notu yeni soruyu söyler.

## 3. Bitiş

- BACKLOG'dan iş silinir.
- Ölçüm sonra: `after-*.txt`, spec'teki tablo.
- Takımlar sırayla: `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`
  (ve queen-agent'ın ikisi).
