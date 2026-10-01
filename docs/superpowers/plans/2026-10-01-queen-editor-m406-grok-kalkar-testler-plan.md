# Madde 406 — Grok ve xAI anahtarı kalkar, test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Grok'un ve xAI anahtarının Queen Editor'den kalktığını söyleyen testler, kırmızı.

**Mimari:** Yokluk bir taramayla sınanır — QueenAgent 383'ün `test_retired_provider.py`'sinin aynısı,
Queen Editor'ün klasöründe. Yalnız kalkan şeyi sınayan testler silinir; yazarların dosyasının testi
yeni adından içe aktarır.

**Araçlar:** pytest, vitest.

**Spec:** [m406 test turu](../specs/2026-10-01-queen-editor-m406-grok-kalkar-testler-design.md)

## Genel kısıtlar

- Yalnız testler; kod dosyasına dokunulmaz.
- Aranan: `grok|xai|x\.ai`, büyük-küçük harf fark etmez.
- Taramadan çıkanlar: `dist`, `node_modules`, `__pycache__`, noktalı klasörler; `package-lock.json`,
  `BACKLOG.md`, taramanın kendisi.
- Yeni modül adı: `backend.features.photo_generation.data.prompt_writer`.
- Test adları ve yorumlar İngilizce; assert mesajları Türkçe.
- Dört satır CLAUDE.md'deki gibi, paralel, borusuz.

---

### Görev 1: Tarama

**Dosya:** Oluştur `queen-editor/backend/tests/test_retired_provider.py`

- [ ] QueenAgent'ın `queen-agent/backend/tests/test_retired_provider.py`'sinin aynısı; docstring 406'yı
  ve BACKLOG'un neden atlandığını söyler; `_TOOL` queen-editor klasörü; `_SKIPPED_FILES =
  {"package-lock.json", "BACKLOG.md"}`. Üç test: `test_the_sweep_reads_the_tool`,
  `test_no_path_names_the_retired_provider`, `test_no_file_mentions_the_retired_provider`.

### Görev 2: Notebook testleri

**Dosya:** `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

- [ ] Sil: `test_the_xai_key_is_probed_like_everything_else_from_outside`,
  `test_the_xai_probe_runs_in_config_not_after_the_downloads`,
  `test_a_dead_key_stops_a_run_that_is_installing_video`,
  `test_a_dead_key_only_warns_when_video_is_not_being_installed`,
  `test_the_probe_says_what_xai_answered_rather_than_guessing_why`,
  `test_the_key_is_trimmed_where_it_is_read`.
- [ ] `test_the_deepseek_key_is_read_from_secrets_and_trimmed` docstring'i: "-- trimmed where it is
  pasted, like the xAI key." → "-- trimmed where it is pasted, because the paste is what carries the
  newline."

### Görev 3: Kompozisyon kökü

**Dosya:** `queen-editor/backend/tests/test_composition_root.py`

- [ ] İki `monkeypatch.setenv("QE_XAI_API_KEY", "")` satırı silinir.
- [ ] WAN testinin docstring'i: "Madde 404: DeepSeek writes WAN's prompt too. With no key the sentence
  names the model the writer asks -- and no request leaves."

### Görev 4: xAI istemcisinin testi

- [ ] `git rm queen-editor/backend/tests/test_xai_client.py`

### Görev 5: Yazarların modülü

**Dosya:** `queen-editor/backend/tests/test_video_prompt_writer.py`

- [ ] Satır 1: `from backend.features.photo_generation.data.prompt_writer import (`
- [ ] Üç fonksiyon-içi import: `from backend.features.photo_generation.data import prompt_writer`, ve
  `xai_prompt_writer.` → `prompt_writer.`

### Görev 6: Hata cümlesi örnekleri

- [ ] `test_photo_usecases.py:1537` → `RuntimeError("DeepSeek HTTP 401\ninvalid key")`
- [ ] `ProjectScreen.test.jsx:450-451` → `// 2026-08-13: a dead key stopped the run …` ve
  `error: "DeepSeek HTTP 400"`
- [ ] `useGeneration.test.jsx:39` ve `:456` → `"DeepSeek HTTP 400"`

### Görev 7: Kırmızıyı gör ve commit'le

- [ ] Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] Beklenen: queen-editor pytest'te taramanın iki testi kırmızı ve `test_video_prompt_writer.py`
  toplanamıyor (`prompt_writer` yok); öteki üç satır yeşil.
- [ ] Commit: `test(queen-editor): Madde 406 red -- grok and the xAI key go …`, spec ve plan ile.
