# Madde 435 — WAN Queen Editor'den çıkar, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Queen Editor yalnız H3 videosu üretir; WAN'ın grafikleri, üreticisi, seçimi, Queen AI
metni, notebook'taki indirmesi ve paketleri gider. Eski WAN videoları açılır ve export'a girer.

**Yaklaşım:** Önce kırmızı testler — kalanın yeni hâli —, sonra WAN'ın testleri gider ve kod değişir,
en son frontend ve `dist`.

**Araçlar:** pytest, vitest, Vite.

**Spec:** [m435](../specs/2026-10-08-queen-editor-m435-wan-cikar-design.md)

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce**, ve yalnız bugün doğru olanı söyler.
- Dört satır CLAUDE.md'deki gibi, **birer birer**; `skip` / `xfail` yok.
- Roadmap'e dokunulmaz; commit ana ajanın.

---

## Görev 1: Kırmızı testler

- [ ] `test_workflow_asset.py` — `test_the_only_graphs_shipped_are_the_photo_s_and_h3_s`: assets'teki
  `.json`'lar `workflow_api.json`, `workflow_video_h3_api.json`,
  `workflow_video_h3_first_last_api.json`.
- [ ] `test_composition_root.py` — fixture `QE_VIDEO_MODEL`'i yazmaz; `import_main()` argümansız.
  `test_every_session_makes_its_videos_with_h3`: `_producers["video"]` `ComfyH3VideoGenerator`,
  `_writers["video"]` `H3VideoPromptWriter`, `_video_length` projenin uzunluğu (8).
- [ ] `test_producers.py` — `test_the_video_row_names_h3_and_says_nothing_about_references`:
  `list_producers(GROUPS, files)`'ın video satırı `{id, name, installed, model}`, `model ==
  "MiniMax H3"`; `test_the_video_group_is_h3_s`: `GROUPS["video"]` H3'ün altı dosyası.
- [ ] `test_reference_usecases.py` — `run()` `has_h3`'süz çağırır; reddetme testleri aynı.
- [ ] `test_notebook_installs_the_producer_groups.py` — `test_wan_is_gone_from_the_notebook`:
  `VIDEO_WAN`, `VIDEO_H3`, `VIDEO_MODEL`, `Wan2_1_VAE_fp32`, `umt5_xxl`, `lightx2v`, `SmoothMix`,
  `clip_vision`, `Comfy-Org/Wan_2`, iki WAN grafiği ve 11 paketin depoları defterde geçmiyor.
- [ ] `test_video_prompt_writer.py` — `test_no_wan_writer_is_left`: `prompt_writer`'da
  `VideoPromptWriter` ve `VIDEO_INSTRUCTION` yok.
- [ ] `python -m pytest queen-editor -q` — yalnız bunlar kırmızı.
- [ ] Frontend: `LayerPanel.test.jsx` ve `PhotoDetail.test.jsx`'in video satırları
  `reads_references`'sız; Referanstan'da kurulu bir satırla H3_ONLY'nin çıkmadığı ve düğmenin açıldığı
  test. `npm test --prefix queen-editor/frontend` — uzunluk ve Referanstan testleri kırmızı.

## Görev 2: Backend

- [ ] `assets/workflow_video_api.json`, `assets/workflow_video_first_last_api.json`,
  `data/comfy_video_generator.py`, `tests/test_comfy_video_generator.py` silinir.
- [ ] `config.py`: `VIDEO_WORKFLOW_PATH`, `VIDEO_FIRST_LAST_WORKFLOW_PATH`, `VIDEO_MODEL` gider;
  `VIDEO_TIMEOUT`'un yorumu.
- [ ] `prompt_writer.py`: `VIDEO_INSTRUCTION`, `VideoPromptWriter` gider; modül, `LOOP_RULE`,
  `LINKED_RULE`, `asked`, `_scenario` yorumları.
- [ ] `queue_references.py`: `has_h3`, `NoReferenceProducer` gider; `reference_routes.py`.
- [ ] `producers.py`: `VIDEO_MODEL`. `model_groups.py`: `GROUPS["video"]` H3'ün; `H3_VIDEO`,
  `groups_for`, `video_model_name` gider. `list_producers(groups, files)`.
- [ ] `main.py`: dal, `_video_length`, `queue_references`, üreticiler paneli; yorumlar.
- [ ] Yalnız yorum: `comfy_h3_video_generator.py`, `ports.py`, `run_loop.py`, `video_length.py`,
  `queue_layer.py`, `regenerate.py`, `retry_frame.py`, `ffmpeg_video_exporter.py`.

## Görev 3: WAN'ın testleri gider, kuralları kalanlara

- [ ] `test_workflow_asset.py`: WAN'ın yedi testi ve `VIDEO_MODEL` testi gider; `_graphs` yalnız
  fotoğraf; `test_every_graph_makes_a_portrait_frame` fotoğraf ve iki H3; `H3_VIDEO` →
  `GROUPS["video"]`; `_model_files`'ın GGUF cümlesi.
- [ ] `test_producer_contract.py`: `GRAPHS` üç; `producers_over` H3; iki WAN testi gider.
- [ ] `test_composition_root.py`: parametreler ve WAN testleri gider.
- [ ] `test_producers.py`: WAN ve `groups_for` testleri gider; sahte grup adları.
- [ ] `test_video_prompt_writer.py`: WAN testleri gider; ek döngüsünden ve başarısız cevap testinden
  `VideoPromptWriter` çıkar.
- [ ] `test_reference_usecases.py`: H3'süz red testi gider. `test_reference_routes.py`,
  `test_photo_usecases.py`, `test_video_length.py`: `has_h3` argümanı gider;
  `test_a_session_whose_video_model_takes_no_length_queues_none` gider.
- [ ] `test_notebook_installs_the_producer_groups.py`: iki kutu, iki kontrol, video modelleri bölümü
  ve `QE_VIDEO_MODEL` testleri gider; form ve anahtar testleri H3'ü `INSTALL_VIDEO`'yla sorar; panelin
  dosyaları adın son parçasıyla aranır, H3 testi onunla birleşir.
- [ ] `test_comfy_h3_video_generator.py`, `test_video_length.py`: WAN'ı anan docstring'ler.

## Görev 4: Notebook — `queen-editor/queeneditor.ipynb`

- [ ] Giriş: *"(9 custom node)"*.
- [ ] CONFIG: *Video ~37 GiB*; *Video modelleri* bölümü, iki kutu, iki kontrol ve `VIDEO_MODEL` gider;
  seçim satırı *"video (H3)"*.
- [ ] Klon: üç grafik, *"üç grafik mevcut"*.
- [ ] ComfyUI: başlık *(9)*, `CUSTOM_NODES` 9 satır; pip satırı kalır.
- [ ] Modeller: `CLIPV`, `HF_VIDEO`, `CIVITAI_VIDEO` gider; `INSTALL_VIDEO`'nun arkasında H3; disk
  hesabı; özet klasörleri.
- [ ] Flask: `QE_VIDEO_MODEL` gider.
- [ ] `python -m pytest queen-editor -q` — yeşil.

## Görev 5: Frontend

- [ ] `useVideoLength.js`: satır okununca. `LayerPanel.jsx`: `H3_ONLY` ve dalı gider, yorumlar.
  `PhotoDetail.jsx`: yorum.
- [ ] Testler: WAN satırlı testler gider; *Model* kutusu testi.
- [ ] `npm test --prefix queen-editor/frontend` — yeşil. `npm run build --prefix queen-editor/frontend`.

## Görev 6: Belgeler

- [ ] `CODE-STANDARD.md` miras tablosu; `README.md` CONFIG ve DeepSeek; `BACKLOG.md` loop maddesi.

## Görev 7: Koş

- [ ] Dört satır, birer birer:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```
