# Madde 72 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m72-grok-build-tek-model-testler-design.md](../specs/2026-08-26-queenagent-m72-grok-build-tek-model-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**Tek model:** id `grok-build-0.1`, adı `Grok Build`, satırı `$1 / $2 per 1M · 256k`.

---

## A. Kırmızıya dönenler

### 1. `test_config.py` — varsayılan Grok Build

`test_the_default_model_is_the_cheap_one_with_the_long_context` **tamamen** şununla değişiyor:

```python
def test_the_default_model_is_grok_build(tmp_path=None):
    # Pinned like MAX_ROUNDS: this is a decision, and changing it without noticing changes what the
    # user pays and what fits. Grok Build costs $1/$2 against grok-4.3's $1.25/$2.50, and carries
    # 256k of context against its 1M -- a quarter of the room, chosen knowingly (Madde 72).
    #
    # An XAI_MODEL in the environment overrides this and the resolved value is what lands here, so
    # on a machine that sets it this test fails and says something true: the default running here
    # is not the one the repository ships.
    assert config.XAI_MODEL == "grok-build-0.1"
```

`tmp_path` alınmıyor — bugünkü test de almıyor. İmza sade: `def test_the_default_model_is_grok_build():`

**Adı değişiyor**, çünkü eskisi *"uzun bağlamlı ucuz olan"* diyor ve uzun bağlam artık bu modelin
özelliği değil. Yalan söyleyen bir ad testten uzun yaşar.

### 2. `models.test.js` — liste tek satır

```jsx
test("Grok Build is the only model we offer", () => {
  // Madde 72. The others were removed knowingly: Grok Build costs less and the run is meant to
  // stand on one model rather than on a choice nobody was making.
  expect(MODELS.map((model) => model.id)).toEqual(["grok-build-0.1"]);
});
```

### 3. `models.test.js` — sunulmayan model ham id ile okunuyor

`a chat that picked the model we stopped offering still says what it is` testinin beklentisi
`grok-4.5` yerine `grok-4.3` oluyor:

```jsx
test("a chat that picked a model we stopped offering still says what it is", () => {
  // Not hypothetical since Madde 72: grok-4.3 was the default until today, so chats on disk carry
  // it. Removing its row must not make them unreadable -- and showing a display name for a model
  // the menu no longer has would imply it can still be picked.
  expect(modelName("grok-4.3")).toBe("grok-4.3");
});
```

### 4. `ModelPicker.test.jsx` — sunulmayan modelde işaretli satır yok

`the row in use is the marked one` testinin **altına**, yeni:

```jsx
test("a chat on a model we no longer offer marks no row", () => {
  // Marking Grok Build would say this chat answers with it, and it does not: the record keeps
  // grok-4.3 and the server sends that. No row is the honest drawing.
  const { container } = render(<ModelPicker model="grok-4.3" open />);
  expect(container.querySelectorAll(".menu__item--checked").length).toBe(0);
});
```

## B. Fixture göçü — nötr, ama şart

Aşağıdakiler `grok-4.6` / `grok-4.3`'ü fixture olarak kullanıyor ve konuları model değil. İkisi de
bugün listede olduğu için bu düzenlemeler ne kırmızı ne yeşil. **Uygulama turunda yapılsaydı bir
düzine test birden düşerdi ve gerçek bir kırılma gibi okunurdu.**

### 5. `ModelPicker.test.jsx`

| Test | Ne oluyor |
|---|---|
| `closed, it says which model this chat answers with` | `grok-4.3` → `grok-build-0.1`, `/Grok 4.3/` → `/Grok Build/` |
| `a model the list does not know still gets a button` | Dokunulmuyor — `grok-9000` hâlâ bilinmiyor |
| `open, it lists every model under a label` | Fixture `grok-4.6` → `grok-build-0.1`. Döngü `MODELS` üstünde, tek satırla da çalışıyor |
| `the menu says what each model costs` | Fixture aynı şekilde. Açıklamasındaki *"several rows share a price"* cümlesi siliniyor — artık tek satır var |
| `choosing another one hands the id over` | Başlangıç `grok-4.6` → `grok-4.3`; tıklanan satır `Grok Build` kalıyor |
| `choosing the one already in use asks the server for nothing` | `grok-4.6` → `grok-build-0.1`, tıklanan `Grok 4.6` → `Grok Build` |
| `the row in use is the marked one` | `grok-4.6` → `grok-build-0.1`, beklenen metin `Grok Build` |
| `open and shut is asked for from outside` | Fixture ve düğme adı |
| `it takes no keyboard of its own` | Fixture |

### 6. `ChatScreen.test.jsx`

| Satır | Ne oluyor |
|---|---|
| `the composer says which model this chat answers with` | `grok-4.3` → `grok-build-0.1`, `/Grok 4.3/` → `/Grok Build/` |
| `the foot carries Skills, the model and Send, in that order` | `grok-4.6` → `grok-build-0.1`, `"Grok 4.6⌄"` → `"Grok Build⌄"` |
| `while an answer runs the row ends in Stop…` | Aynı ikisi |
| 593. satırdaki `model: "grok-4.6"` | `grok-build-0.1` |

### 7. `ProjectScreen.test.jsx`

`model="grok-4.6"` → `model="grok-build-0.1"`, `"Grok 4.6⌄"` → `"Grok Build⌄"`. İki yerde
*(204-206 ve 226)*.

### 8. `App.test.jsx` — `withModel` ve ona dayanan testler

`withModel` imzası bir varsayılan alıyor ve iki yer değişiyor:

```jsx
function withModel(model = "grok-build-0.1") {
  const chats = [{ id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() }];
  let chat = { id: "c1", title: "Write the intro", messages: [], model };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path === "/api/model") {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ default: "grok-build-0.1" }),
      });
    }
```

`model || "grok-4.6"` kalıbı gidiyor: boş dize geçen çağrı yok, ve varsayılanı iki kere yazmak
ikisinin bir gün ayrılması demek.

Testlerde `/Grok 4.6/` → `/Grok Build/`. **Model değiştirmeyi sınayan dördü** artık sunulmayan bir
modelden başlıyor ve Grok Build'e geçiyor:

| Test | Başlangıç | Tıklanan | Bu turda |
|---|---|---|---|
| `picking a model writes it to the chat it was picked in` | `withModel("grok-4.3")`, düğme `/grok-4.3/` | `Grok Build` | **kırmızı** |
| `a new chat is born with the last model picked in this session` | `withModel("grok-4.3")` | `Grok Build`; POST beklentisi `grok-build-0.1` | **kırmızı** |
| `picking a model closes the menu` | `withModel("grok-4.3")` | `Grok Build` | **kırmızı** |
| `in a draft, picking a model closes the menu too` | `withModel()` — taslağın modeli sunucudan geliyor | `Grok Build` | nötr |

İlk üçünün düğme adı `/grok-4.3/` — **ham id**, çünkü listede karşılığı olmayacak. Bugün orada
`Grok 4.3` yazıyor ve `/grok-4.3/` ona eşleşmiyor, yani üçü de kırmızıya dönüyor.

Dördüncüsü nötr: taslağın modeli sunucudan geliyor ve o zaten `grok-build-0.1`, yani bugün de
yarın da `Grok Build` yazıyor.

Kalan `withModel` kullanıcıları — skill testleri, `one menu closes the other`,
`pressing the model already in use…`, `Escape closes the pickers…`,
`with nothing picked yet a draft follows the server's own setting` — yalnız `/Grok 4.6/` →
`/Grok Build/` alıyor ve nötr kalıyor.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_config.py` | 1 |
| `models.test.js` | 2 |
| `ModelPicker.test.jsx` | 1 |
| `App.test.jsx` — ham id bekleyen üçü | 3 |

Arka uçta **3 failed, 442 passed** — biri bu maddenin, ikisi defterin dalı.
Ön yüzde **6 failed, 507 passed** — bir yeni testle toplam 513.

## Toplu değiştirme yok

`grok-4.6` dört dosyada onlarca kez geçiyor ve bazıları *(Menu, Composer)* `MODELS`'a hiç
bakmıyor. **`replace_all` kullanılmıyor** — 77'de aynı görünen on bir satırdan ikisi değiştirilmek
istenmiş, on biri birden değişmiş ve dokuz sahte kırmızı çıkmıştı.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `config.py` ve `models.js` bu turda açılmıyor.
- **`dist` derlenmez.**
- **`Menu.test.jsx` ve `Composer.test.jsx` açılmıyor.** Oradaki `"Grok 4.6"` rastgele bir metin;
  o bileşenler `MODELS`'ı hiç görmüyor.
- **`test_model_api.py` açılmıyor.** Varsayılanı kendi enjekte ediyor.
- **`ModelPicker.jsx` ve seçiciyi çizen hiçbir ekran açılmıyor.** Seçici duruyor.
