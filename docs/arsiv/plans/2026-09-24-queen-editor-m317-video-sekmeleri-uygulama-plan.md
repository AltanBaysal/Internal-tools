# Madde 317 — Video panelinin iki sekmesi, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `8db0c72c`'nin kırmızı testleri yeşile dönüyor.

**Yaklaşım:** Sunucuda `settings`'in ikizi, kendi dosyası ve kendi blueprint'iyle; ekranda
LayerPanel'in tepesinde iki sekme ve Referanstan için proje başına bir taslak.

**Spec:** [m317 uygulama turu](../specs/2026-09-24-queen-editor-m317-video-sekmeleri-uygulama-design.md)

## Her yere geçerli kurallar

- Yorum **İngilizce**, yalnız bugün doğru olanı söyler; arayüz metni tasarımdan harfi harfine.
- Testlere dokunulmaz. Kaynakla `dist/` aynı commit'te.

---

## Görev 1: Sunucu

**Oluştur:** `queen-editor/backend/features/projects/data/reference_settings_store.py`

```python
"""ReferenceSettingsStore over DriveStorage -- the only place that knows Referanstan's record file.

settings_store's twin. The photo panel's file is written when a photo batch is sent and this one
when a reference production is, so they never share a file (CODE-STANDARD, Separation of concerns).
Like that one it keeps the prompt text exactly as typed, and reads anything unreadable as empty:
its only job is to refill the boxes.
"""
import json

FILE = "reference_settings.json"


def _empty():
    return {"prompts": "", "variants": None}


def _text(value):
    return value if isinstance(value, str) else ""


def _count(value):
    # bool is an int in Python, and True would silently become "1 variant".
    return value if isinstance(value, int) and not isinstance(value, bool) else None


class DriveReferenceSettingsStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def read(self, project):
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return _empty()
        try:
            data = json.loads(raw)
        except ValueError:
            return _empty()
        if not isinstance(data, dict):
            return _empty()
        return {"prompts": _text(data.get("prompts")), "variants": _count(data.get("variants"))}

    def write(self, project, settings):
        self._storage.write_text(
            project, FILE, json.dumps(settings, ensure_ascii=False, indent=2))
```

**Oluştur:** `queen-editor/backend/features/projects/domain/usecases/save_reference_settings.py`

```python
"""Store Referanstan's boxes as they were sent (madde 317).

save_settings' twin, and unvalidated for the same reason: the file exists to refill the boxes, and a
list the server refuses is still what the user typed. Reading needs no twin -- get_settings asks the
same question of whichever store it is handed.
"""
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def save_reference_settings(store, project, prompts, variants):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    store.write(project, {"prompts": prompts, "variants": variants})
```

**Oluştur:** `queen-editor/backend/features/projects/presentation/reference_settings_routes.py`

```python
"""Referanstan's record over HTTP (madde 317).

A blueprint of its own rather than two more rows in the projects one, the way the reference pool has
its own: the photo panel's settings door, and everything wired to it, stays exactly as it was.
"""
from flask import Blueprint, jsonify, request

from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def make_reference_settings_blueprint(get_reference_settings, save_reference_settings):
    """Both arguments are use cases already bound to a store (see main.py)."""
    bp = Blueprint("reference_settings", __name__)

    @bp.get("/api/projects/<project>/reference-settings")
    def get_reference_record(project):
        try:
            return jsonify(get_reference_settings(project))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500

    @bp.put("/api/projects/<project>/reference-settings")
    def put_reference_record(project):
        body = request.get_json(silent=True) or {}
        prompts, variants = body.get("prompts"), body.get("variants")
        try:
            save_reference_settings(
                project,
                prompts if isinstance(prompts, str) else "",
                # bool is an int in Python, and True would silently mean "1 variant".
                variants if isinstance(variants, int) and not isinstance(variants, bool) else None,
            )
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        # 204: the client already has what it sent; there is nothing to send back.
        return "", 204

    return bp
```

**Değiştir:** `queen-editor/backend/main.py` — üç import *(sıralı yerlerine)*, deponun
`_settings_store`'un altında kurulması, blueprint `_projects_bp`'nin altında, ve `create_app`'in
listesi:

```python
from backend.features.projects.data.reference_settings_store import DriveReferenceSettingsStore
from backend.features.projects.domain.usecases.save_reference_settings import (
    save_reference_settings,
)
from backend.features.projects.presentation.reference_settings_routes import (
    make_reference_settings_blueprint,
)

_reference_settings_store = DriveReferenceSettingsStore(_storage)

# Referanstan's boxes: the photo panel's question, in a file and at a door of their own (madde 317).
_reference_settings_bp = make_reference_settings_blueprint(
    get_reference_settings=partial(get_settings, _reference_settings_store),
    save_reference_settings=partial(save_reference_settings, _reference_settings_store),
)

app = create_app(blueprints=[_projects_bp, _reference_settings_bp, _photo_bp, _references_bp,
                             _producers_bp])
```

## Görev 2: Ekran

**`queen-editor/frontend/src/shared/api.js`** — `saveSettings`'in altına:

```js
// Referanstan's own record (madde 317): what its boxes open with once a visit's draft is gone. An
// address of its own because it is written at a moment of its own -- a reference production, not a
// photo batch.
export async function getReferenceSettings(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/reference-settings`);
}

export async function saveReferenceSettings(project, { prompts, variants }) {
  return request(`/api/projects/${encodeURIComponent(project)}/reference-settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompts, variants }),
  });
}
```

**`production_modes.js`** — `SOURCES`:

```js
// Named for what they are made FROM rather than "Standart / Referans": the Kareden tab already has a
// Standart, which says where a video ends, and one panel cannot carry that word twice. They are the
// video panel's two tabs (madde 317).
export const SOURCES = [
  { id: FROM_FRAME, label: "Kareden" },
  { id: FROM_POOL, label: "Referanstan" },
];
```

**`SidePanel.jsx`** — `LayerPanel`'e `project={project}`.

**`LayerPanel.jsx`:**

1. Import: `import { getReferenceSettings, saveReferenceSettings } from "../../shared/api.js";`
2. `CONFIRM_MS`'in altına:

```js
// What Referanstan's boxes were last holding, per project (madde 317). The photo panel's own rule
// (GeneratePanel's REMEMBERED): this panel is built afresh on every opening and on every step in and
// out of a frame, and without this the prompt list typed there would go with it. Memory only: a
// reload asks the project's record instead.
const DRAFTS = new Map();
```

3. İmza `project`'i alıyor; durum:

```js
  const [source, setSource] = useState(FROM_FRAME);
  // Referanstan's draft, when this visit left one. Only the video panel keeps one.
  const kept = layer === "video" ? DRAFTS.get(project) : undefined;
  const [prompts, setPrompts] = useState(kept?.prompts ?? "");
  // Text, not a number: the field has to survive being cleared while typing.
  const [variants, setVariants] = useState("1");
  // Referanstan's own count. Kareden's opens at one every time, as it always has; this one is kept
  // with the prompt list it multiplies.
  const [poolVariants, setPoolVariants] = useState(kept?.variants ?? "1");
  // Whether the Referanstan boxes hold this visit's words yet -- a kept draft, the project's record,
  // or a keystroke. Until then there is nothing to keep, and the record is still worth asking for.
  const settled = useRef(Boolean(kept));
  const recordAsked = useRef(false);
```

4. `fromPool`'un altında, açık sekmenin sayısı ve iki effect:

```js
  // The box shows, and the press reads, the open tab's own count.
  const shownVariants = fromPool ? poolVariants : variants;

  // The project's record fills the boxes once per visit, the first time the tab is open. What was
  // typed while it flew stays: a draft is one thing, never half the record and half the hand. A
  // record that cannot be read leaves the boxes empty -- all that is lost is a prefill, and a dead
  // server is said by the press, whose write fails first.
  useEffect(() => {
    if (!fromPool || settled.current || recordAsked.current) return;
    recordAsked.current = true;
    getReferenceSettings(project)
      .then((record) => {
        if (settled.current) return;
        settled.current = true;
        setPrompts(record.prompts);
        setPoolVariants(record.variants === null ? "1" : String(record.variants));
      })
      .catch(() => {});
  }, [fromPool, project]);

  // Kept only once settled: a panel built and closed without the tab ever opening would otherwise
  // leave an empty draft, and the record would never be asked again this visit.
  useEffect(() => {
    if (layer === "video" && settled.current) {
      DRAFTS.set(project, { prompts, variants: poolVariants });
    }
  }, [layer, project, prompts, poolVariants]);
```

5. `variants`'ı okuyan her yer `shownVariants`'ı okuyor: `owed`, ret effect'inin bağımlılığı,
   `refusalOf`, sayım satırı, kutunun değeri ve kırmızı kenarı.
6. `handleAdd`:

```js
    const count = Number(shownVariants);
    const files = scope === "selected" && !fromPool
      ? inSelection.map((frame) => frame.file) : null;
    // From the pool the boxes are written down first, the photo panel's way (ProjectScreen's
    // handleGenerate): the record and the work land in the same folder, so a record that cannot be
    // written means the work could not be either, and nothing is sent. The words ride along only
    // when they are what the press is about: every other call keeps the shape it has always had.
    const asked = fromPool
      ? saveReferenceSettings(project, { prompts, variants: count })
        .then(() => onQueue(null, count, sent, prompts))
      : onQueue(files, count, sent);
    asked
      .then((body) => { … bugünkü gibi … })
      .catch((err) => setRefused(err.message))
      .finally(() => setSubmitting(false));
```

7. JSX: sekmeler en üstte, `Üretim` bloğu gidiyor, `Referanslar` başlığı prompt kutusunun önünde,
   kutunun başlığı `Prompt listesi`, kutuya yazmak `settled`'ı kuruyor:

```jsx
      {/* Where the video is made from, as two tabs over the whole panel (madde 317): each tab is a
          form of its own. Only the video panel has them -- a sound is laid over a video that
          already exists, and the pool has nothing to give it. */}
      {layer === "video" && (
        <div className="wf-segment" style={{ display: "flex" }}>
          {SOURCES.map((one) => (
            <button key={one.id} type="button" className={source === one.id ? "is-on" : ""}
                    style={{ flex: 1 }} onClick={() => setSource(one.id)}>
              {one.label}
            </button>
          ))}
        </div>
      )}

      {fromPool && (
        // The pool's own block. What it holds -- the button that opens the pool in the middle -- is
        // madde 318's.
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Mono size={11} data-label style={LABEL}>Referanslar</Mono>
        </div>
      )}
```

```jsx
          onChange={(e) => {
            if (!acceptsVariants(e.target.value)) return;
            if (fromPool) {
              settled.current = true;
              setPoolVariants(e.target.value);
            } else {
              setVariants(e.target.value);
            }
          }}
```

## Görev 3: Koşu, dist ve yeşil commit

- [ ] **Adım 1: Dört satırı koş** — dördü de yeşil. Yeni SidePanel testi de: test turundaki
  `TypeError` kırmızısı sekmelerin yokluğundan geliyorsa şimdi geçer.
- [ ] **Adım 2: Dist** — `npm run build --prefix queen-editor/frontend`.
- [ ] **Adım 3: Yeşil commit** — kod, `dist/`, spec ve bu plan: `feat(m317): …`.
