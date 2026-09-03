# Madde 149 · Tur 2 (uygulama) — Uygulama Planı

**Goal:** `8c02872`'nin 13 kırmızısını yeşile çevirmek.

**Spec:** [Tur 2 tasarımı](../specs/2026-09-03-queenagent-m149-ikinci-yol-uygulama-design.md)

## Global Constraints

- **Kırmızı commit'in testleri değişmez.**
- `stream_answer` ve yukarısı dokunulmuyor — dokunmak zorunda kalırsam düzeltme yanlış katmanda.
- Defterin `BRANCH`'i `feat/v6` kalıyor *(kullanıcı isteği)*; o iki kırmızı bu turun işi değil.
- `dist` kaynakla **aynı commit'te**.

### Task 1: `backend/config.py`

- [ ] `OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")`
- [ ] İki satır: `deepseek/deepseek-v4-flash-0731` ve `deepseek/deepseek-v4-pro-0813` —
      `https://openrouter.ai/api/v1`, `OPENROUTER_API_KEY`, ve `extra` olarak DeepInfra sabitlemesi.
- [ ] `engine_for` dördüncü olarak `wiring.get("extra")` döndürüyor.
- [ ] Tablonun yorumu **neden** sabitlendiğini yazıyor: sözleşme seçimi, hız ayarı değil.

### Task 2: `backend/services/xai/client.py`

- [ ] `__init__(self, read_key, model, base_url, extra=None, opener=...)`; `self._extra = extra or {}`.
- [ ] `_request`: `payload = {**self._extra, "model": self._model, **body}`.
- [ ] Yorum sıranın **neden** böyle olduğunu yazıyor — yasak alan listesi tutulmuyor.

### Task 3: `main.py`

- [ ] `extra=config.engine_for(model)[3]`.

### Task 4: `frontend/src/features/workspace/models.js`

- [ ] Beş satır, çiftler yan yana, adlar ve fiyatlar kırmızının beklediği gibi.
- [ ] Dosyanın başındaki yorum üçten beşe geçiyor ve ikinci yolun ne olduğunu söylüyor.

### Task 5: `queenagent.ipynb`

- [ ] CONFIG: `OPENROUTER_API_KEY` try/except ile Secrets'tan, `assert`'i, açılış cümlesi.
- [ ] *"All three from Colab's Secrets store"* → dört.
- [ ] *"Both keys, not one of them (Madde 146)"* → üç anahtar, Madde 149.
- [ ] SERVE: `env`'e `OPENROUTER_API_KEY`, ve *"The two keys"* yorumu → üç.
- [ ] Türkçe `assert` metni, ötekilerin biçiminde, nereden alınacağını söylüyor.

### Task 6: `dist` ve doğrulama

- [ ] `npm run build --prefix queen-agent/frontend`
- [ ] `python -m pytest queen-agent -q` → yalnız defterin 2 kırmızısı
- [ ] `npm test --prefix queen-agent/frontend`
- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend`
- [ ] Commit: kaynak + `dist` + belgeler, defterin kendisi dahil.
