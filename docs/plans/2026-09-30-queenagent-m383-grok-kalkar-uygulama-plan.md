# Madde 383 — Grok ve xAI anahtarı kalkar · uygulama turu planı

> **Ajanlar için:** bu plan satır içinde, tek oturumda uygulanır (CLAUDE.md: istenmedikçe alt ajan
> yok). Adımlar `- [ ]` ile işaretlenir.

**Amaç:** `efbe762f`'deki kırmızı testleri, Grok'u ve xAI anahtarını QueenAgent'tan kaldırarak yeşile
çevirmek.

**Mimari:** Taşıyıcı ve motor yeni adlarına taşınır, sohbet kimliği port'tan taşıyıcıya kadar
kalkar, tablo tek satıra iner; notebook ve belgeler tek anahtarı anlatır.

**Teknoloji:** Python (Flask, urllib), Jupyter notebook JSON'u.

**Spec:** [2026-09-30-queenagent-m383-grok-kalkar-uygulama-design.md](../specs/2026-09-30-queenagent-m383-grok-kalkar-uygulama-design.md)

## Genel kısıtlar

- `backend.services.model.client`: `ModelClient`, `ModelFailed`, `ModelNotConfigured`.
- `backend.features.workspace.data.model_engine`: `ModelEngine`, `ROLE_FOR_MODEL`, `_for_model`.
- `stream(self, messages, tools=None, on_open=None)` — port, motor ve taşıyıcıda aynı.
- `config.MODELS = {"deepseek-flash": {"base_url": "https://api.deepseek.com", "key": "DEEPSEEK_API_KEY"}}`.
- Notebook'un kod hücrelerine yeni yorum eklenmez.
- Yorumlar İngilizce, yalnız bugün doğru olanı söyler; `docs/` altındaki tarihî belgelere dokunulmaz.

---

### Görev 1: Taşıyıcı

**Dosyalar:** `git mv queen-agent/backend/services/xai queen-agent/backend/services/model`

- [ ] Modül belge dizesi: `"""ModelClient -- HTTP transport for an OpenAI-compatible chat completions API.`
- [ ] Sınıf adları: `ModelNotConfigured`, `ModelFailed`, `ModelClient`; bütün `raise` satırları.
- [ ] `_IS_XAI` ve yorumu silinir.
- [ ] `stream(self, messages, tools=None, on_open=None)`; `_request(self, body, tools)`;
  `_request` içindeki başlık paragrafı ve `if conversation_id and ...` iki satırı silinir.
- [ ] `_Calls` belge dizesi: *"A call may come whole in one chunk, which the OpenAI-compatible
  protocol allows. DeepSeek fragments it..."*; `index` cümlesi aynı kalır.
- [ ] `_spent` belge dizesi: iki biçim *"the OpenAI-compatible shape nests the figure under
  prompt_tokens_details, DeepSeek sends prompt_cache_hit_tokens flat..."*.
- [ ] `write_once`'ın *"Two services shape that figure two ways"* cümlesi *"The figure comes in two
  shapes"* olur.

### Görev 2: Motor, port, kullanım, bileşim kökü

- [ ] `git mv .../data/xai_engine.py .../data/model_engine.py`; adlar genel kısıttaki gibi; belge
  dizesi `"""ModelEngine -- the Engine port, backed by the model service."""`; rol yorumu *"the model
  is told OpenAI's"*; `stream` kimliği ne alır ne geçirir.
- [ ] `ports.py`: `conversation_id: str = ""` parametresi ve paragrafı silinir.
- [ ] `stream_answer.py`: `conversation_id=chat_id,` ve üstündeki iki satırlık yorum silinir.
- [ ] `main.py`: `from backend.features.workspace.data.model_engine import ModelEngine`,
  `from backend.services.model.client import ModelClient`; `ModelEngine(` / `ModelClient(`.

### Görev 3: Yapılandırma

- [ ] `config.py`: anahtar yorumu `DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")`'in
  üstüne; `XAI_API_KEY` ve *"The second provider's key"* yorumu silinir; tablodan `grok-4.3`
  satırı ve yorumu silinir; tarihçe yorumu *"...Madde 358 took the picker out, and Madde 383 took
  out the other provider's row with its key..."*.

### Görev 4: Notebook

- [ ] CONFIG: *"All three from Colab's Secrets store"* → *"Both"*; `XAI_API_KEY` `try` bloğu,
  *"Both keys, not one of them..."* paragrafı ve `assert XAI_API_KEY` silinir; son `print`:
  `"✓ GITHUB_TOKEN ve DEEPSEEK_API_KEY Secrets'tan okundu"`.
- [ ] Serve: yorum *"Two things the app learns only from here... The key is the whole of what it
  knows about it..."*, *"Which of the two a turn spends..."* cümlesi silinir; ortamdan
  `"XAI_API_KEY": XAI_API_KEY,` silinir.

### Görev 5: Belgeler

- [ ] `README.md`: `export DEEPSEEK_API_KEY=...`.
- [ ] `FOUNDATION.md` 1. karar: `the key in \`DEEPSEEK_API_KEY\``; 6. karara: *"Madde 383 (30
  September) took the first provider out again, with its key and its header, and the layer stayed
  as it was: one provider is behind it now."*
- [ ] `CODE-STANDARD.md`: `` `model/` — HTTP transport to an OpenAI-compatible chat API: a request,
  an SSE stream, a resolved tool call.``; *"holding the API key"*.

### Görev 6: Koş ve commit'le

- [ ] Diskte `services/xai/` yalnız `__pycache__` ile kalmışsa silinir.
- [ ] Dört satır, paralel, yazıldığı gibi; dördü yeşil.
- [ ] Commit: `feat: Madde 383 -- Grok and the xAI key go`, spec ve plan ile.
