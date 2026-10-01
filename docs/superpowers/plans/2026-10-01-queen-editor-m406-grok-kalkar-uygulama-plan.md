# Madde 406 — Grok ve xAI anahtarı kalkar, uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** `bf294d3a`'nın kırmızı testlerini, grok'un ve xAI anahtarının izlerini silerek yeşile
çevirmek.

**Mimari:** Silme ve bir yeniden adlandırma; yeni kod yok.

**Araçlar:** git, Python, NotebookEdit.

**Spec:** [m406 uygulama turu](../specs/2026-10-01-queen-editor-m406-grok-kalkar-uygulama-design.md)

## Genel kısıtlar

- Yazarların metinlerine dokunulmaz; `prompt_writer.py` içeriği `xai_prompt_writer.py` ile aynı.
- Notebook'un kod hücrelerine yorum eklenmez; yalnız silinen satırlar ve giriş cümlesi değişir.
- `BACKLOG.md`, yol haritası, `tmp/` değişmez; dist derlenmez.
- Dört satır CLAUDE.md'deki gibi, paralel, borusuz.

---

### Görev 1: İstemci ve ayarlar

- [ ] `git rm -r queen-editor/backend/services/xai`
- [ ] `config.py`: 66–72. satırlar (iki yorum ve dört `XAI_*`) silinir; DeepSeek yorumu
  `# Not read from the environment: nothing probes DeepSeek, so nothing outside the app has to ask`
  `# what the app asks.` olur.

### Görev 2: Yazarların dosyası

- [ ] `git mv queen-editor/backend/features/photo_generation/data/xai_prompt_writer.py queen-editor/backend/features/photo_generation/data/prompt_writer.py`
- [ ] `main.py:16` → `from backend.features.photo_generation.data.prompt_writer import (`
- [ ] `services/deepseek/client.py:4` → `features/photo_generation/data/prompt_writer.py).`

### Görev 3: Notebook

- [ ] Giriş hücresi (`34c9ff58`): son Secrets cümlesi →
  `` günde bir yenilenir); video ve ses için `DEEPSEEK_API_KEY` (prompt'larını yazan Queen AI — ``
  `` QueenAgent'ınkiyle aynı secret). ``
- [ ] CONFIG hücresi (`8215086b`): `XAI_API_KEY` try bloğu, `# === xAI ===` bölümü ve sondaki
  `if not XAI_API_KEY:` dalı silinir; hücrenin son satırı `print(f"✓ HF aynası: {HF_MIRROR}")`.
- [ ] Flask hücresi (`e086a5a5`): `flask_env`'den üç `QE_XAI_*` girdisi silinir:

```python
flask_env = {**os.environ, "QE_DRIVE_ROOT": DRIVE_ROOT, "QE_COMFY_URL": COMFYUI_URL,
             "QE_COMFY_ROOT": COMFY_ROOT, "QE_COMFY_LOG": COMFY_LOG,
             "QE_PHOTO_MODELS": ",".join(CHOSEN_MODELS), "QE_VIDEO_MODEL": VIDEO_MODEL,
             "QE_DEEPSEEK_API_KEY": DEEPSEEK_API_KEY}
```

- [ ] `git diff` ile yalnız bu satırların değiştiği görülür.

### Görev 4: README

- [ ] Secrets tablosundan `XAI_API_KEY` satırı silinir.

### Görev 5: Yeşili gör ve commit'le

- [ ] Dört satır, paralel. Beklenen: hepsi yeşil.
- [ ] `queen-editor/` altında büyük-küçük harfsiz `xai|grok` araması: `dist`, `node_modules` dışında
  yalnız `BACKLOG.md`, `package-lock.json`'ın bir özeti ve `test_retired_provider.py`.
- [ ] Commit: `feat(queen-editor): 406 -- grok and the xAI key go …`, spec ve plan ile.
