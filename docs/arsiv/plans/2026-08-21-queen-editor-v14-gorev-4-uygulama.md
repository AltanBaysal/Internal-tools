# v14 Görev 4 — Video panelinde Üretim modu seçicisi: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün kırmızı bıraktığı on üç testi yeşile döndürmek: panelde mod satırı doğsun,
açılışta Standart'ta dursun, ses panelinde hiç görünmesin, ve seçilen mod panelden plan satırına
kadar gitsin.

**Architecture:** Bir yeni sözlük dosyası ve dört dosyalık bir argüman zinciri. Modu **seçen** tek
yer panel; aradaki üç halka (SidePanel, useGeneration, api) yalnız taşıyor; **okuyan** tek yer uç.
Hiçbir ara halka modun ne anlama geldiğini bilmiyor.

**Tech Stack:** React 18, vite; Python 3, Flask.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-4-mod-secicisi-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni ve hata cümleleri **Türkçe**.
- **Katman kuralı:** `production_modes.js` `photo_generation` özelliğinin içinde ve hiçbir şey
  import etmiyor.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor ve aynı commit'e giriyor.** Bu koşunun ilk ön yüz işi.
- Commit **yeşil gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/production_modes.js` | üç modun Türkçe adı | yaratılır |
| `frontend/src/features/photo_generation/LayerPanel.jsx` | modu seçen tek yer | durum, `ModeRow`, satır |
| `frontend/src/features/photo_generation/SidePanel.jsx` | taşıyıcı | argüman geçer |
| `frontend/src/features/photo_generation/useGeneration.js` | taşıyıcı | argüman geçer |
| `frontend/src/shared/api.js` | taşıyıcı | gövdeye anahtar |
| `backend/.../presentation/routes.py` | modu okuyan tek yer | `mode`, `InvalidMode` |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Modların Türkçe adı

**Files:**
- Create: `queen-editor/frontend/src/features/photo_generation/production_modes.js`

**Interfaces:**
- Produces: `STANDARD`, `MODES` (`[{id, label}]`). Task 2 ve 8-9. maddeler buna dayanıyor.

- [ ] **Step 1: Dosyayı yaz**

```js
// The three ways a video can be made, as the user reads them. The identity is the engine's
// (domain/production_mode.py); only the Turkish name lives here.
//
// A list rather than three constants: the panel draws it in order, and Standart comes first because
// it is what a panel opens on.
export const STANDARD = "standard";

export const MODES = [
  { id: STANDARD, label: "Standart" },
  { id: "loop", label: "Loop" },
  { id: "linked", label: "Sonrakine bağla" },
];
```

Kimlik ile etiket ayrı dosyalarda: ekrandaki adı değiştiren, plan dosyasına aylardır yazılan
kelimeyi değiştirmiş olmamalı.

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: değişen bir şey yok — dosyayı henüz kimse import etmiyor. On kırmızı duruyor.

---

### Task 2: Panelin mod satırı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Consumes: Task 1'in `MODES` ve `STANDARD`'ı.
- Produces: `onQueue(files, variants, mode)` — Task 3 bu şekli taşıyor.

- [ ] **Step 1: Import'u ekle**

```jsx
import { MODES, STANDARD } from "./production_modes.js";
```

- [ ] **Step 2: ModeRow'u yaz**

`LayerPanel`'in üstüne, `ScopeRow`'un altına:

```jsx
/** One production mode, drawn the way a scope row is drawn -- with nothing on the right.
 *
 * Not ScopeRow with an empty count: a mode has nothing to count, and saying so with a missing
 * argument would leave the reader deciding what an absent number means.
 */
function ModeRow({ label, active, onPick }) {
  return (
    <button type="button" onClick={onPick}
            className="wf-stroke"
            style={{ display: "flex", alignItems: "center", padding: "8px 10px", background: "none",
                     cursor: "pointer", borderColor: active ? "var(--accent)" : "var(--border)",
                     opacity: active ? 1 : 0.4, width: "100%" }}>
      <Note size={12} style={{ color: "var(--ink-2)" }}>{label}</Note>
    </button>
  );
}
```

- [ ] **Step 3: Durumu ekle**

`scope` durumunun hemen altına:

```jsx
  // Kept by both panels though only the video one shows the row: a sound ends nowhere, so it has
  // nothing to choose -- and one call shape means the server never asks where a request came from.
  const [mode, setMode] = useState(STANDARD);
```

- [ ] **Step 4: Satırı çiz**

Varyant öbeğinin **üstüne**:

```jsx
      {/* Only a video ends on a picture, so only the video panel has this to ask. */}
      {layer === "video" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Mono size={11} style={LABEL}>Üretim modu</Mono>
          {MODES.map((one) => (
            <ModeRow key={one.id} label={one.label} active={mode === one.id}
                     onPick={() => setMode(one.id)} />
          ))}
        </div>
      )}
```

ve varyant öbeğinin yorumu sırayı doğru sayar hâle gelir:

```jsx
      {/* The design's own order: scope, then the mode, then how many of each, then the button. */}
```

- [ ] **Step 5: Modu gönder**

```jsx
    onQueue(scope === "selected" ? inSelection.map((frame) => frame.file) : null, Number(variants),
            mode)
```

- [ ] **Step 6: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: `LayerPanel.test.jsx`'in dokuzu da yeşile döner. `api.test.js`'in biri kırmızı.

---

### Task 3: Argüman zinciri

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- Modify: `queen-editor/frontend/src/shared/api.js`

**Interfaces:**
- Produces: `queueLayer(project, kind, files, variants, mode)`.

- [ ] **Step 1: SidePanel**

```jsx
                      onQueue={(files, variants, mode) => onQueueLayer(open, files, variants, mode)}
```

- [ ] **Step 2: useGeneration**

```js
  const queueLayer = useCallback((kind, files, variants, mode) => (
    postLayer(project, kind, files, variants, mode)
```

- [ ] **Step 3: api.js**

```js
// Hang a layer on every frame in scope. No "files" key means every frame that does not hold it; a
// list means that selection. `variants` is how many each of them gets: the ones past the first are
// born as copy frames. `mode` is how a video ends -- plain, looping, or on the next frame's picture.
export async function queueLayer(project, kind, files, variants, mode) {
  return request(`/api/projects/${encodeURIComponent(project)}/layers/${kind}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...(files === null ? {} : { files }), variants, mode }),
  });
}
```

- [ ] **Step 4: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: ön yüzün tamamı yeşil.

---

### Task 4: Ucun okuduğu mod

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py`

**Interfaces:**
- Consumes: `queue_layer(..., mode=...)` ve `InvalidMode` (2. maddede doğdu).

- [ ] **Step 1: İki import**

```python
from backend.features.photo_generation.domain import layers, production_mode, queue
```

```python
from backend.features.photo_generation.domain.usecases.queue_layer import InvalidMode, InvalidScope
```

- [ ] **Step 2: Gövdeyi oku ve hatayı çevir**

```python
        try:
            # No "variants" key means one per frame, and no "mode" key means a plain video: a
            # client older than either box asks for exactly what it always asked for.
            added = queue_layer(project, kind, files=files, variants=body.get("variants", 1),
                                mode=body.get("mode", production_mode.STANDARD))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except InvalidScope as exc:
            return jsonify({"error": str(exc), "field": "files"}), 400
        except InvalidMode as exc:
            return jsonify({"error": str(exc), "field": "mode"}), 400
        except InvalidVariants as exc:
            return jsonify({"error": str(exc), "field": "variants"}), 400
```

`InvalidMode` `InvalidVariants`'ın **üstünde**: ikisi de `Exception`'dan türüyor ve akraba
değiller, yani sıra bugün önemsiz — ama alanların okunma sırası gövdedeki sırayla aynı kalsın diye
böyle duruyor.

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil.

---

### Task 5: Derlenmiş çıktı

**Files:**
- Modify: `queen-editor/frontend/dist/`

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

Not defteri bu depoyu klonluyor ve derlemiyor (`app.ipynb`'nin klon hücresi `dist/index.html`'i
arıyor). Derlenmemiş bir ön yüz Colab'da eski hâliyle açılır ve mod satırı orada hiç görünmez.

---

### Task 6: Yeşil commit

- [ ] **Step 1: Yol haritasını işaretle**

4. maddenin **İş** hücresi ✅ ile başlar, sayaç `3/31` → `4/31`.

- [ ] **Step 2: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the production mode is picked from the panel

Three rows between the scope and the variant count, opening on Standart. Drawn like the
scope rows but with no count cell: a mode has nothing to count, and saying so with a
missing argument would leave the reader deciding what an absent number means.

The sound panel grows no row -- a sound is laid over the whole of a video and arrives
nowhere -- but keeps the state and always sends the plain mode, so there is one call
shape and the server never asks where a request came from.

The Turkish names live in production_modes.js: madde 8 will read the same three in the
detail info row and madde 9 in the selector there. The identity stays in the domain, so
renaming one on screen never touches what is written in a plan file.

With no mode key the endpoint reads plain, the same way the variant count already does.
InvalidMode answers 400 with field mode, which is what InvalidScope and InvalidVariants
already do.

dist built in this commit: the notebook clones this repo and never builds.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in altı kaynak dosyasının altısı da bir task'ta, artı `dist` Task 5'te.

**Tip tutarlılığı:** `(files, variants, mode)` sırası dört halkada da aynı: panelin `onQueue`'su,
SidePanel'in ok fonksiyonu, `useGeneration.queueLayer`, `api.queueLayer`. Uçta anahtar adı `mode`,
gövdede de `mode`.

**Kontrol edilen tuzak:** `mode` durumu iki panelde de tutuluyor, yalnız videoda çiziliyor. Yalnız
video panelinde tutulsaydı ses panelinin `onQueue`'su iki argümanla çağrılırdı ve çağrı biçimi
ikiye ayrılırdı — sunucunun okuduğu tek şeklin bozulması demek.

**Kontrol edilen tuzak 2:** `ModeRow`'un `justifyContent`'i yok; `ScopeRow`'da `space-between` var
çünkü sağda sayı duruyor. Kopyalanıp bırakılsaydı tek çocuk ortalanmış gibi değil, sola yaslanmış
ama boşluk dağıtımı bozuk görünürdü.

**Kontrol edilen sıra:** Task 1 hiçbir kırmızıyı yeşile çevirmiyor ve bu planda yazılı. Bir adımın
takımı oynatmaması, o adımın atlanabileceği anlamına gelmiyor — Task 2 onsuz derlenmez.
