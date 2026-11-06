# Madde 514 · MMAudio kalkar — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-13), 514 · v11-13 ·
**Spec:** [2026-10-29-queen-editor-m514-mmaudio-kalkar-design.md](../specs/2026-10-29-queen-editor-m514-mmaudio-kalkar-design.md)

Test önce: önce testler MMAudio'nun yokluğunu ve eski ses işinin davranışını söyler (kırmızı), sonra kod
çıkar (yeşil).

## 1. Sunucu testleri

- Silinir: `test_mmaudio_generator.py`, `test_ffmpeg_audio.py`, `test_audio_chunks.py`,
  `test_colab_sound.py`.
- `test_composition_root.py` — sesin yazıcı testleri çıkar; yeni: `_producers` ve `_writers`'ta ses yok;
  main'in `_producers`/`_writers`'ıyla eski bir ses işi `waiting`/`audio` ile durur ve hiçbir istek gitmez.
- `test_producer_contract.py` — `MMAudioGenerator`, `Sampler`, `Ffmpeg` ve FRAMES'teki ses işi çıkar;
  uçtan uca koşu fotoğraf ve video; "sound" diyen yerler fotoğrafa iner.
- `test_video_prompt_writer.py` — `AudioPromptWriter` ve `AUDIO_INSTRUCTION` testleri çıkar.
- `test_producers.py`, `test_producers_routes.py` — satırlar `photo`, `video`; ses grubu testi yerine
  `GROUPS`'ta ses yok testi.
- `test_photo_routes.py` — `layers/audio` ve `regenerate` `audio` 404; ses silme kalır.
- `test_notebook_installs_the_producer_groups.py` — `SWITCH`'ten ses; assert iki kutu; `HF_AUDIO` satırı;
  sesin kurulum testi yerine "MMAudio defterden gitti" testi.
- `test_colab_downloads.py` — klasör örneğindeki `mmaudio` başka bir klasör olur.
- `test_photo_usecases.py`, `test_mute.py` — export özetinde `silent` yok; `muted` testleri kalır.
- `test_requirements.py` (queen-editor ve queen-agent), `test_ffmpeg_stills.py` — yalnız docstring.

## 2. Sunucu kodu

- Silinir: `mmaudio_sampler.py`, `mmaudio_generator.py`, `ffmpeg_audio.py`, `audio_chunks.py`,
  `colab/sound.py`.
- `prompt_writer.py`, `main.py`, `config.py`, `model_groups.py`, `producers.py`, `ports.py`,
  `comfy_models.py` (`path` → `_path`), `list_producers.py` (docstring), `routes.py`,
  `export_summary.py` (`silent` çıkar).
- `queeneditor.ipynb` — 0., 1., 4., 8. hücreler; 9–11 silinir. Kaynak tek string olarak kalır.

## 3. Ekran

- Testler önce: `SidePanel.test.jsx` (rayda Ses üret yok), `LayerPanel.test.jsx` (ses örnekleri çıkar),
  `ProjectScreen.test.jsx` (başka panele geçiş videodan fotoğrafa), `PhotoDetail.test.jsx` (ses sekmesinde
  Yeniden üret yok, prompt salt okunur, Sesi sil var), `ProducersPanel.test.jsx` (iki satır),
  `ExportScreen.test.jsx` ("sesi yok" satırı yok, "sesi kapalı" var).
- `SidePanel.jsx`, `LayerPanel.jsx`, `PhotoDetail.jsx`, `ExportScreen.jsx`.
- `npm run build --prefix queen-editor/frontend`.

## 4. Belgeler

- `FOUNDATION.md` 6 ve 9, `CODE-STANDARD.md` (miras tablosu, `colab/` listesi, Tests), `README.md`,
  `BACKLOG.md`.

## 5. Bitiş

- `queen-editor/` altında `mmaudio` araması: yalnız 514'ün testleri ve tarihçe.
- İki takım tek tek: `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
