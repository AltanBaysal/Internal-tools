# Madde 336 — Yalnız Queen Flash kalır · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Arka ucun ve ön ucun yalnız `deepseek-flash`'ı bildiğini, eski adların ona düştüğünü ve
*Queen Pro*'nun hiçbir yerde seçilemediğini tutan iddialar, kırmızı.

**Architecture:** Model adlarını sabitleyen testler yeni ada döner: `test_config.py` arka ucun
tablosunu, `models.test.js` ön ucun listesini, seçiciyi kullanan dört test dosyası da menünün
satırlarını ve seçilen id'yi tutar. Kayıt olan eski adlara (diskteki mesajlar) dokunulmaz.

**Tech Stack:** pytest; vitest + Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m336-yalniz-flash-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; hata cümlesi Türkçe.
- Bu turda `config.py` ve `models.js` değişmez; `dist` derlenmez.
- Fiyat yazısı (`$0.22 / $0.66 per 1M`) olduğu gibi kalır — v9-4b'nin.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Arka ucun tablosu

**Files:**
- Modify: `queen-agent/backend/tests/test_config.py`

**Interfaces:**
- Produces: uygulama turunun karşılayacağı şey — `config.MODELS`'un anahtarları tam olarak
  `{"grok-4.3", "deepseek-flash"}`, `DEFAULT_MODEL == PROMPT_MODEL == "deepseek-flash"`.

- [ ] **Step 1:** `test_the_default_model_is_the_cheaper_queen` → `test_the_default_model_is_deepseek_flash`,
  beklenen `"deepseek-flash"`; yorumdaki *two models* cümlesi Madde 336'ya döner.
- [ ] **Step 2:** Grok testinin arkasına ekle:

```python
def test_deepseek_is_wired_under_the_one_name_it_has_today():
    # Madde 336. DeepSeek closed deepseek-v4-pro on 14 September and answers it with Flash, and
    # deepseek-v4-flash is only an alias now -- so the table holds the name the model has today and
    # nothing else of DeepSeek's. Grok stays, knowingly (above).
    assert set(config.MODELS) == {"grok-4.3", "deepseek-flash"}
```

- [ ] **Step 3:** `test_the_three_models_resolve_to_their_provider` → `test_the_two_models_resolve_to_their_provider`
  ve `test_each_model_names_the_key_it_spends`: DeepSeek satırları tek satıra, `deepseek-flash`.
- [ ] **Step 4:** `PROMPT_MODEL`, `engine_for("deepseek-flash")` ve geri düşüş testi `"deepseek-flash"` bekler.
- [ ] **Step 5:** Sona ekle:

```python
def test_a_chat_that_named_an_old_deepseek_id_is_answered_by_flash():
    # Messages on disk name deepseek-v4-flash or deepseek-v4-pro, and those chats must still be
    # answered: both ids are gone from the table, so the unknown-id rule takes them to the default.
    assert config.engine_for("deepseek-v4-flash")[0] == "deepseek-flash"
    assert config.engine_for("deepseek-v4-pro")[0] == "deepseek-flash"
```

### Task 2: Ön ucun listesi ve seçici

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/models.test.js`
- Modify: `queen-agent/frontend/src/features/workspace/ModelPicker.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` (seçici testleri)
- Modify: `queen-agent/frontend/src/features/workspace/ProjectScreen.test.jsx` (seçici testi)
- Modify: `queen-agent/frontend/src/App.test.jsx` (model testleri)

**Interfaces:**
- Produces: `MODELS` tek satır `{ id: "deepseek-flash", name: "Queen Flash", detail: "$0.22 / $0.66 per 1M" }`;
  `DEFAULT_MODEL === "deepseek-flash"`.

- [ ] **Step 1: `models.test.js`**

```js
test("one model is offered", () => {
  // Madde 336. DeepSeek closed deepseek-v4-pro on 14 September and answers it with Flash, so Queen
  // Pro left the menu; Flash stays under the name DeepSeek gives it today.
  expect(MODELS.map((model) => model.id)).toEqual(["deepseek-flash"]);
});
```

Ad ve fiyat testi `[["Queen Flash", "$0.22 / $0.66 per 1M"]]`; varsayılan `"deepseek-flash"`;
`modelName("deepseek-flash")` → `"Queen Flash"`.

- [ ] **Step 2: `ModelPicker.test.jsx`** — elinde model olan testler `deepseek-flash` ile; menünün
  satırları `["Queen Flash"]`; *choosing one hands the id over* menüde olmayan `grok-build-0.1`'den
  Queen Flash'a basar ve `deepseek-flash` bekler; seçili satırı basmak da `deepseek-flash` verir.
- [ ] **Step 3: `ChatScreen.test.jsx`** — *shows what it is handed* `grok-4.3` ile düğmede `grok-4.3`'ü;
  *passed up* `grok-4.3`'ten Queen Flash'a basar, `deepseek-flash` bekler.
- [ ] **Step 4: `ProjectScreen.test.jsx`** — `model="deepseek-flash"`, Queen Flash satırına basar,
  `deepseek-flash` bekler.
- [ ] **Step 5: `App.test.jsx`** — yeni sohbetin mesajı `"deepseek-flash"`; *picking a model asks
  the server for nothing* Queen Flash satırına basar; yeni test:

```js
test("Queen Pro is on offer nowhere", async () => {
  // Madde 336: DeepSeek closed deepseek-v4-pro on 14 September and answers it with Flash, so a Pro
  // row would name one model and be answered by another.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Queen Flash/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /Queen Flash/ }));
  expect(screen.getByText("MODELS")).toBeTruthy();
  expect(screen.queryByText("Queen Pro")).toBeNull();
});
```

### Task 3: Kırmızıyı gör, commit'le

- [ ] **Step 1: Dört satırı paralel koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent'ın arka ucunda `test_config.py`'nin yeni ada bakan testleri kırmızı; ön ucunda
`models.test.js`, `ModelPicker.test.jsx`'in menü ve id testleri, `ProjectScreen`'in ve `ChatScreen`'in
id testi, `App.test.jsx`'in yeni sohbet ve *Queen Pro* testleri kırmızı. queen-editor'ün arka ucu
377'nin bilinen iki kırmızısı; ön ucu yeşil.

- [ ] **Step 2: Commit**

```powershell
git add queen-agent/backend/tests/test_config.py queen-agent/frontend/src docs/superpowers/specs/2026-09-29-queenagent-m336-yalniz-flash-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m336-yalniz-flash-testler-plan.md
git commit -m @'
test(queen-agent): Madde 336 red -- only deepseek-flash is wired and offered, old ids fall back to it, Queen Pro is nowhere

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
