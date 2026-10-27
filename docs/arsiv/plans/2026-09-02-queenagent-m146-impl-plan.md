# Madde 146 · Tur 2 (uygulama) — Uygulama Planı

> Alt-ajan kullanılmaz *(depo kuralı)*; planı bu oturum yürütür.

**Goal:** `769e2e7`'nin çivilediği 38 kırmızıyı, hiçbir yeşili düşürmeden yeşile çevirmek.

**Spec:** [Tur 2 tasarımı](../specs/2026-09-02-queenagent-m146-model-secimi-uygulama-design.md)

## Global Constraints

- Kırmızı commit'in **testleri değişmez.** Bir test yeşil olmuyorsa cevap kodu düzeltmektir.
- Üç id, iki adres, iki anahtar adı: spec'teki tabloda birebir.
- `dist`, ön yüz kaynağıyla **aynı commit'te** *(FOUNDATION 3)*.
- Türkçe yalnız kullanıcının gördüğü yerde; kod ve yorumlar İngilizce.
- Sıra önemli: arka uç aşağıdan yukarı, sonra ön yüz, sonra defter, sonra belgeler.

---

### Task 1: `config.py` — tablo ve çözücü

- [ ] `DEEPSEEK_API_KEY` çevre değişkeninden okunur, `XAI_API_KEY`'in yanında.
- [ ] `XAI_MODEL` kalkar; `MODELS` tablosu ve `DEFAULT_MODEL` gelir.
- [ ] `engine_for(model_id)` → `(model_id, base_url, api_key)`; tanınmayan ve boş varsayılana düşer.
      Anahtarın **adı** tabloda, **değeri** burada okunur.
- [ ] Koş: `python -m pytest queen-agent/backend/tests/test_config.py -q` → 6 yeşil

### Task 2: `xai_engine.py` — taşıyıcıyı seçmek

- [ ] `XaiEngine(clients, default)`; `stream(..., model="")` haritadan seçer, bulamazsa varsayılan.
- [ ] `complete` de aynı şekilde seçer — bugün tek çağıranı yok ama iki yol iki davranış olurdu.
- [ ] Rol çevirisi olduğu gibi kalır.
- [ ] Koş: `python -m pytest queen-agent/backend/tests/test_xai_engine.py -q` → 7 yeşil

### Task 3: `client.py` — iki sağlayıcının iki farkı

- [ ] `_spent()`: `prompt_tokens_details.cached_tokens` **veya** `prompt_cache_hit_tokens`; ikisi de
      yoksa 0.
- [ ] `x-grok-conv-id` yalnız xAI adresine — kararı `base_url` verir, bayrak eklenmez.
- [ ] Koş: `python -m pytest queen-agent/backend/tests/test_xai_client.py -q` → hepsi yeşil

### Task 4: `chat.py` + `file_chat_store.py` — kaydı

- [ ] `Message.model: str = ""`, `skill`'in yanında, gerekçe yorumuyla.
- [ ] Diske yazma: **boşsa alan yazılmaz** *(skill'in kuralı)*; okuma varsayılanla.
- [ ] Sohbetin kökündeki `model` okunmamaya devam eder.
- [ ] Koş: `python -m pytest queen-agent/backend/tests/test_chat.py queen-agent/backend/tests/test_file_chat_store.py -q`

### Task 5: `routes.py` + `stream_answer.py` — yolu

- [ ] Uçta `model=payload.get("model", "")`; cevapta `"model": message.model`.
- [ ] `append_message` bir `model` parametresi alır, `skill`'in yanında.
- [ ] `_current_model(chat)` — `_current_skill`'in aynası; turdan önce bir kez okunur.
- [ ] `engine.stream(..., model=...)`.
- [ ] Koş: `python -m pytest queen-agent -q` → **656 + 27 yeşil, 0 kırmızı**

### Task 6: `models.js` ve `ModelPicker.jsx`

- [ ] `models.js`: `MODELS`, `DEFAULT_MODEL`, `modelName(id)` — boş id varsayılanın adı.
- [ ] `ModelPicker.jsx`: `SkillPicker`'ın şekli; seçili satır temizlemez, `picker--on` almaz.
- [ ] `ModelLabel.jsx` silinir.
- [ ] Koş: `npm test --prefix queen-agent/frontend` → iki yeni dosya yeşil

### Task 7: Ekranlar ve App

- [ ] `ChatScreen.jsx` ve `ProjectScreen.jsx`: `ModelLabel` yerine `ModelPicker`; dört yeni prop.
- [ ] `App.jsx`: `pickerOpen` üçüncü değeri `"model"`; `draftModel` / `lastModel`, `DEFAULT_MODEL`
      ile başlar.
- [ ] `useChat.js`: `send(text, skill, mode, model)`, gövdeye `model`.
- [ ] Koş: `npm test --prefix queen-agent/frontend` → **562 + 11 yeşil, 0 kırmızı**

### Task 8: Defter

- [ ] CONFIG: `DEEPSEEK_API_KEY` Secrets'tan, `assert` ile şart, çıktı satırı iki anahtarı söyler.
- [ ] SERVE: `"DEEPSEEK_API_KEY": DEEPSEEK_API_KEY` env'e.
- [ ] Giriş hücresi tek anahtardan söz etmeyi bırakır.
- [ ] Koş: `python -m pytest queen-agent/backend/tests/test_notebook.py -q`

### Task 9: Belgeler ve `dist`

- [ ] `FOUNDATION.md` Decision 6 iki sağlayıcıyı anlatır; **gerekçe cümlesi değişmez.**
- [ ] Yol haritası 146: *"defter seçtirir"* ve *"ekran değişmiyor"* düzeltilir, **Turlar** satırı
      eklenir, *"Sekiz maddenin hiçbiri ekrana dokunmuyor"* cümlesi 146'yı dışarıda bırakacak
      şekilde düzeltilir.
- [ ] `npm run build --prefix queen-agent/frontend`
- [ ] Dört satırın hepsi koşulur; queen-editor'ün ikisi yeşil kalmalı.
- [ ] Tek commit: kaynak + `dist` + belgeler.
