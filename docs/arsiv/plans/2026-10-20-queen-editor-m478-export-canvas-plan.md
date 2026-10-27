# Madde 478 — Export'un tuvali, plan

> **Koşum:** bu oturumda, ana klasörde, `feat/queen-editor-v10` dalında, adım adım, test önce (TDD).
> Adımlar `- [ ]` ile işaretlenir. Commit ana ajanın.

**Hedef:** birleşik export her parçayı kendi süzgecinde 1920 × 1080'lik tuvale oturtur ve concat
süzgeciyle tek çağrıda birleştirir: yatay 16:9 parça tuvali bantsız doldurur, dikey parça bantlı
kalır, ikisi bir arada birleşir.

**Spec:** [m478](../specs/2026-10-20-queen-editor-m478-export-canvas-design.md)

**Araçlar:** pytest, vitest. ffmpeg bu makinede yok; testler komutu okur.

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce** yazılır ve yalnız bugün doğru olanı söyler.
- Dosyalar Read / Edit / Write ile değişir. Kabuk yalnız pytest, npm ve git status / diff için.
- İki suite birer birer koşulur.
- Notebook değişmez. Frontend'de yalnız `ExportScreen.jsx`'in bir yorumu; `dist` yeniden kurulur ve
  değişmediği `git status`'ta görülür.

---

## Görev 1: testler — `backend/tests/test_export.py`

- [ ] `STAMP` sabiti yerine parça sayısına ve sese göre beklenen grafiği kuran bir yardımcı
  (`expected_graph(n, sounded)`), `FIT`'e `setsar=1`.
- [ ] Birleştirme komutu: her parça `-threads 1 -i`, uyarı yazısı son girdi, `-map [v] -r 24`; sesli
  kümede (bir parçası sesli olanda da) `-map [a] -c:a aac -b:a 192k`, sessizde ses eşlemesi yok.
  CPU ve GPU kodlayıcısıyla.
- [ ] `SOUND_BITRATE` iki H3 grafiğinin `audio_bitrate`'ine eşit.
- [ ] Yatay 1024 × 576, dikey 576 × 864 ve karışık küme: hepsi aynı süzgeçle, red yok, boyut sorusu
  yok, tek yazan çağrı.
- [ ] `decrease`'in hesabı (`scale_eval.c`'nin formülü, testin içinde) H3'ün `SIZES`'ında: yatay
  1920 × 1080 / bant 0, dikey 720 × 1080 / bant 600.
- [ ] `MERGED_FPS` iki H3 grafiğinin Director `frame_rate`'ine eşit.
- [ ] Liste dosyası yazılmıyor; sessiz parçaya sessizlik ve birleştirmenin onu okuması komuttan
  okunur (`FakeRun.joined` artık `-i`'lerden).
- [ ] Kalkanlar: boyut sorusu, boyut reddi, `pieces.txt` testleri.
- [ ] Kırmızı.

## Görev 2: `ffmpeg_video_exporter.py`

- [ ] `MERGED_FPS = 24`, `SOUND_BITRATE = "192k"`; `_stamp` → `_filtergraph(count, sounded)`: parça
  başına `FIT`, concat süzgeci, uyarı yazısı.
- [ ] `merge`: `_evened_out` → girdiler (`-threads 1 -i`) → tek `_ffmpeg_run`, çıkışta
  `-r MERGED_FPS` (parçanın zincirindeki `fps` son kareyi düşürüyor, QA ffmpeg 7.1'le ölçtü);
  `size`, boyut reddi, `pieces.txt` kalkar.
- [ ] Kare sayısı gerçek ffmpeg 7.1'le, `tmp/qa-m478/` betikleriyle (repo dışı): sessiz, sesli,
  karışık hızlı kümeler tam sayıda kare.
- [ ] `_evened_out` sesli olup olmadığını da döner.
- [ ] Bayat yorumlar: 480x720 → 1024 × 576 / 576 × 864; concat demuxer'dan söz edenler.
- [ ] `run_export.py`'deki `JOINED` yorumunda `pieces.txt`.
- [ ] `ExportScreen.jsx`'in birleştirme yorumu; `npm run build`, `dist` değişmemeli.
- [ ] Yeşil.

## Görev 3: Bitiş

- [ ] `python -m pytest queen-editor -q`, sonra `npm test --prefix queen-editor/frontend`.
- [ ] `git status` / `git diff` ile değişen dosyaları gözden geçir.
