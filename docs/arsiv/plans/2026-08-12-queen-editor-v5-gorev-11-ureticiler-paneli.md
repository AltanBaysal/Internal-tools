# Görev 11 — Şerit yeni düzeni + Üreticiler paneli · Uygulama Planı

> **Çalıştıran ajan için:** GEREKLİ ALT BECERİ: superpowers:executing-plans.

**Amaç:** Şeridin en altına Üreticiler ikonu ve paneli gelir; panel üç üreticiyi kurulu olup
olmadıklarıyla sayar. Şerit tasarımın geometrisine oturur.

**Mimari:** Arka uçta yeni bir feature (`producers`) — hiçbir feature'ı import etmez, elindeki tek
şey "kurulu musun" diye sorulabilen bir port. Ön yüzde `features/producers/` altında panel ve hook.

**Spec:** [Görev 11 tasarımı](../specs/2026-08-12-queen-editor-v5-gorev-11-ureticiler-paneli-design.md)

## Global kısıtlar

- **Full TDD:** önce kırmızı test.
- **`feature ↛ feature`**: `producers` feature'ı `photo_generation`'ı import etmez; somut üretici
  yalnız `main.py`'de bağlanır.
- Üretici anahtarları arka ucun sözcükleri: `photo` · `video` · `audio`.
- Dil ayrımı: yorum/test adı/commit **İngilizce**, kullanıcı metni **Türkçe**.
- Test komutları: `npm test --prefix queen-editor/frontend -- --run` ·
  `python -m pytest queen-editor -q` · derleme `npm run build --prefix queen-editor/frontend`.
- **Tek commit**, görevin sonunda, `dist/` ile birlikte.

---

### Görev 1: Üreticiler kendini sayar

**Dosyalar:**
- Oluştur: `queen-editor/backend/features/producers/__init__.py`,
  `.../producers/domain/__init__.py`, `.../producers/domain/ports.py`,
  `.../producers/domain/producers.py`,
  `.../producers/domain/usecases/__init__.py`,
  `.../producers/domain/usecases/list_producers.py`,
  `.../producers/presentation/__init__.py`, `.../producers/presentation/routes.py`
- Değiştir: `queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py`
- Değiştir: `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_producers.py` (yeni),
  `queen-editor/backend/tests/test_comfy_photo_generator.py`

**Arayüzler:**
- Üretir: `list_producers(producers) -> [{"id", "name", "installed"}]` — üretim sırasında.
- Üretir: `ComfyPhotoGenerator.installed() -> bool`.

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

`test_producers.py`:

```python
"""Which producers this machine has, and which of them are installed."""
import pytest

from backend.features.producers.domain.usecases.list_producers import list_producers


class FakeProducer:
    def __init__(self, installed=True, boom=None):
        self._installed = installed
        self._boom = boom

    def installed(self):
        if self._boom:
            raise RuntimeError(self._boom)
        return self._installed


def test_all_three_are_listed_in_the_order_the_engine_works_in():
    rows = list_producers({})

    assert [row["id"] for row in rows] == ["photo", "video", "audio"]
    assert [row["name"] for row in rows] == [
        "Fotoğraf üreticisi", "Video üreticisi", "Ses üreticisi"]


def test_a_producer_that_says_it_is_installed_is_installed():
    rows = list_producers({"photo": FakeProducer(installed=True)})

    assert rows[0]["installed"] is True


def test_a_producer_that_says_it_is_not_is_not():
    rows = list_producers({"photo": FakeProducer(installed=False)})

    assert rows[0]["installed"] is False


def test_a_kind_with_no_producer_at_all_is_not_installed():
    rows = list_producers({})

    assert [row["installed"] for row in rows] == [False, False, False]


def test_a_producer_that_cannot_answer_is_not_quietly_called_missing():
    # Saying "not installed" would invite a download nobody needs; the caller has to hear the
    # renderer's own words instead.
    with pytest.raises(RuntimeError):
        list_producers({"photo": FakeProducer(boom="Bağlantı yok")})
```

`test_comfy_photo_generator.py`'ye, o dosyanın kendi sahte istemcisiyle:

```python
def test_the_photo_producer_is_installed_when_the_renderer_lists_a_model():
    generator = ComfyPhotoGenerator(FakeClient(checkpoints=["nova.safetensors"]), PATH, 1)

    assert generator.installed() is True


def test_the_photo_producer_is_not_installed_when_the_renderer_lists_none():
    generator = ComfyPhotoGenerator(FakeClient(checkpoints=[]), PATH, 1)

    assert generator.installed() is False
```

Sahte istemcinin adı ve kurucusu o dosyada nasılsa aynen kullanılır.

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `python -m pytest queen-editor -q`

- [ ] **Adım 3: Feature'ı yaz**

`producers/domain/ports.py`:

```python
"""What this feature needs from a producer -- and it is one question.

Deliberately not the photo feature's PhotoGenerator: this feature never imports another, and what
it holds is whatever the composition root hands it.
"""
from typing import Protocol


class Producer(Protocol):
    def installed(self) -> bool:
        """Is this producer's model group on this machine?"""
```

`producers/domain/producers.py`:

```python
"""The three producers, in the order the engine works in.

The ids are the layer names the rest of the app already uses, so a job's type is also the name of
the producer that can do it -- no translation table in between.
"""
PHOTO = "photo"
VIDEO = "video"
AUDIO = "audio"

ORDER = (PHOTO, VIDEO, AUDIO)
NAMES = {PHOTO: "Fotoğraf üreticisi", VIDEO: "Video üreticisi", AUDIO: "Ses üreticisi"}
```

`producers/domain/usecases/list_producers.py`:

```python
"""What the Üreticiler panel draws: three rows, each with a name and an answer.

A kind with no producer object at all is not installed -- the same rule the engine already applies
when it refuses to dispatch a job type nobody can do. A producer that cannot answer at all is not
quietly called missing: the error travels up, because "not installed" would invite a download that
would fix nothing.
"""
from backend.features.producers.domain.producers import NAMES, ORDER


def list_producers(producers):
    return [{"id": kind, "name": NAMES[kind],
             "installed": bool(producers.get(kind)) and producers[kind].installed()}
            for kind in ORDER]
```

`producers/presentation/routes.py`:

```python
"""The Üreticiler panel's one endpoint."""
from flask import Blueprint, jsonify


def make_producers_blueprint(list_producers):
    bp = Blueprint("producers", __name__)

    @bp.get("/api/producers")
    def producers():
        try:
            return jsonify({"producers": list_producers()})
        except Exception as exc:
            # Whatever the renderer said or failed to say, verbatim -- the panel prints it instead
            # of three rows it cannot vouch for.
            return jsonify({"error": str(exc)}), 502

    return bp
```

`comfy_photo_generator.py`:

```python
    def installed(self):
        """Is the photo model group on this machine? The renderer's own list is the answer."""
        return bool(self._client.checkpoints())
```

- [ ] **Adım 4: Composition root'a bağla**

`main.py`:

```python
_producers_bp = make_producers_blueprint(
    list_producers=partial(list_producers, _producers),
)
```

ve `create_app(blueprints=[_projects_bp, _photo_bp, _producers_bp])`.

- [ ] **Adım 5: Koş, yeşili gör**

Koş: `python -m pytest queen-editor -q`

---

### Görev 2: Panel üç satırı çizer

**Dosyalar:**
- Oluştur: `queen-editor/frontend/src/features/producers/useProducers.js`,
  `queen-editor/frontend/src/features/producers/ProducersPanel.jsx`,
  `queen-editor/frontend/src/features/producers/ProducersPanel.test.jsx`
- Değiştir: `queen-editor/frontend/src/shared/api.js`

**Arayüzler:**
- Üretir: `listProducers(project?)` yok — proje sorusu değil: `listProducers()`.
- Üretir: `useProducers()` → `{ producers, error }`; `producers === null` demek henüz bilinmiyor.

- [ ] **Adım 1: Testi yaz (kırmızı test)**

`ProducersPanel.test.jsx`:

```jsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ProducersPanel from "./ProducersPanel.jsx";

const THREE = [
  { id: "photo", name: "Fotoğraf üreticisi", installed: true },
  { id: "video", name: "Video üreticisi", installed: false },
  { id: "audio", name: "Ses üreticisi", installed: false },
];

describe("ProducersPanel", () => {
  it("says what each producer installs and what it is for", () => {
    render(<ProducersPanel producers={THREE} error={null} />);

    expect(screen.getByText(
      "Her üretici kendi model grubunu kurar. Kullanmadığın kurulmaz.")).toBeTruthy();
    expect(screen.getByText("Fotoğraf üreticisi")).toBeTruthy();
    expect(screen.getByText("Video üreticisi")).toBeTruthy();
    expect(screen.getByText("Ses üreticisi")).toBeTruthy();
  });

  it("marks an installed producer and offers the others a way in", () => {
    render(<ProducersPanel producers={THREE} error={null} />);

    expect(screen.getByText("✓ kurulu")).toBeTruthy();
    expect(screen.getAllByText("Kur")).toHaveLength(2);
  });

  it("keeps the Kur button held until the flow behind it exists", () => {
    render(<ProducersPanel producers={THREE} error={null} />);

    expect(screen.getAllByText("Kur")[0].closest("button").disabled).toBe(true);
  });

  it("draws no row it cannot vouch for when the answer never came", () => {
    render(<ProducersPanel producers={null} error="Sunucuya ulaşılamadı — kontrol et." />);

    expect(screen.queryByText("Fotoğraf üreticisi")).toBeNull();
    expect(screen.getByText("Üretici durumu okunamadı")).toBeTruthy();
  });
});
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

- [ ] **Adım 3: Hook'u ve paneli yaz**

`api.js`:

```js
// Which producers this machine has, and which of them are installed. Not a project's question --
// the models live next to the renderer, not in a project folder.
export async function listProducers() {
  const body = await request("/api/producers");
  return body.producers;
}
```

`useProducers.js`:

```js
import { useEffect, useState } from "react";

import { listProducers } from "../../shared/api.js";

// Asked once when the panel mounts: what is installed changes only when something is installed,
// and that is a moment the app knows about (see Görev 12).
export function useProducers() {
  // null = not known yet; the panel draws neither rows nor an error until the answer lands.
  const [producers, setProducers] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let alive = true;
    listProducers()
      .then((rows) => { if (alive) { setProducers(rows); setError(null); } })
      .catch((err) => { if (alive) setError(err.message); });
    return () => { alive = false; };
  }, []);

  return { producers, error };
}
```

`ProducersPanel.jsx`:

```jsx
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Note } from "../../vendor/kit.jsx";

const ROW = { padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8 };

// Artboard: one row per producer, each saying whether its model group is on this machine. No
// removing and no sizes in this version -- the design leaves both out on purpose.
export default function ProducersPanel({ producers, error }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <Note size={12} style={{ color: "var(--ink-3)" }}>
        Her üretici kendi model grubunu kurar. Kullanmadığın kurulmaz.
      </Note>

      {/* Three rows or none: two right answers and one wrong one is worse than saying nothing. */}
      {error ? (
        <StatusErrorCard text="Üretici durumu okunamadı" raw={error} />
      ) : (producers || []).map((producer) => (
        <div key={producer.id} className="wf-stroke" style={ROW}>
          <Note size={12} style={{ color: "var(--ink-2)" }}>{producer.name}</Note>
          {producer.installed ? (
            <Note size={12} style={{ color: "var(--ok)" }}>✓ kurulu</Note>
          ) : (
            // Held until Görev 12 gives it something to do: a button that answers a press with
            // nothing at all would be worse than one that says it is not ready.
            <Btn hl disabled style={{ justifyContent: "center" }}>Kur</Btn>
          )}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

---

### Görev 3: Şerit yeni geometrisine ve altıncı ikona geçer

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/glyphs.jsx`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`
- Test: `SidePanel.test.jsx`

- [ ] **Adım 1: Testi yaz (kırmızı test)**

```jsx
  it("puts the producers panel at the foot of the rail", () => {
    renderColumn();

    const rail = [...document.querySelectorAll("[aria-label]")].map((b) => b.ariaLabel);
    expect(rail.at(-1)).toBe("Üreticiler");
  });

  it("opens the producers panel with its own heading", () => {
    renderColumn();

    fireEvent.click(screen.getByLabelText("Üreticiler"));

    expect(screen.getByRole("heading", { name: "Üreticiler" })).toBeTruthy();
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

- [ ] **Adım 3: İkonu ve satırı ekle**

`glyphs.jsx` — kutu ikonu:

```jsx
// A crate: what a producer's model group arrives in.
export const ProducersGlyph = ({ size }) => (
  <Glyph name="producers" size={size}>
    <path d="M7 1.9 12.1 4.4v5.2L7 12.1 1.9 9.6V4.4L7 1.9z" stroke="currentColor"
          strokeWidth="1.3" strokeLinejoin="round" />
    <path d="M1.9 4.4 7 6.9l5.1-2.5M7 6.9v5.2" stroke="currentColor" strokeWidth="1.3"
          strokeLinejoin="round" />
  </Glyph>
);
```

`SidePanel.jsx` — panel listesi, geometri ve boşluk:

```jsx
const PANELS = [
  { id: "photo", title: "Fotoğraf üret" },
  { id: "queue", title: "Kuyruğu takip et", heading: "Kuyruk" },
  { id: "agent", title: "AI agent" },
  // Set apart at the foot: it is about the machine, not about this project's work.
  { id: "producers", title: "Üreticiler", apart: true },
];
const GLYPH = { photo: PhotoGlyph, queue: QueueGlyph, agent: AgentGlyph,
                producers: ProducersGlyph };
```

Hücre ölçüsü ve seçili işareti tasarımın geometrisine geçer:

```jsx
const RAIL = {
  width: 48,
  flexShrink: 0,
  borderLeft: "1px solid var(--border)",
  background: "var(--bg-2)",
  display: "flex",
  flexDirection: "column",
  alignItems: "stretch",
  paddingTop: 12,
  boxSizing: "border-box",
};

const BUTTON = {
  position: "relative",
  width: "100%",
  height: 46,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "none",
  border: "none",
  padding: 0,
  cursor: "pointer",
  // The selected cell's mark is a full-height edge; the others carry the same width in nothing at
  // all, so the icons do not shift when the selection moves.
  borderRight: "2px solid transparent",
};
```

```jsx
    <button type="button" aria-label={panel.title} aria-current={active ? "page" : undefined}
            onClick={() => onSelect(panel.id)}
            style={{ ...BUTTON, color: active ? "var(--accent)" : "var(--ink-3)",
                     ...(active ? { borderRightColor: "var(--accent)" } : {}),
                     ...(panel.apart ? { marginTop: "auto", marginBottom: 12 } : {}) }}>
      <Glyph />
    </button>
```

(Eski `active && <span …/>` işareti kalkar.)

Panelin gövdesine üreticiler dalı eklenir:

```jsx
        {open === "producers" && <ProducersPanel {...producers} />}
```

`SidePanel` `producers` prop'unu alır; `ProjectScreen` `useProducers()`'ı çağırıp geçirir.

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

---

### Görev 4: Kapanış

- [ ] **Adım 1: İki takımı da koş** · **Adım 2: Derle** · **Adım 3: Tek commit**

```bash
git add -A
git commit -F - <<'MSG'
feat(queen-editor): the rail asks which producers this machine has

Video and audio bring a question the app has had no place for: which engine is
actually on this machine? A producer is a graph plus the model group it needs,
so the answer is whether those files are here -- and the only thing that can
answer it is the producer itself.

So the producers get a panel of their own at the foot of the rail, and a
feature of their own behind it: it imports nobody, and holds whatever the
composition root hands it. A kind with no producer at all is simply not
installed, which is the rule the engine already applies when it refuses a job
it cannot dispatch.

A producer that cannot answer is not quietly called missing -- that would
invite a download that would fix nothing. The panel draws no rows at all and
prints the renderer's own sentence instead.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
MSG
```

## Öz denetim

**1. Spec kapsaması:** Karar 1 (üretici cevaplar) → Görev 1; karar 2 (kendi feature'ı) → Görev 1'in
klasör yapısı ve Görev 2'nin `features/producers/`'ı; karar 3 (cevapsızlık) → Görev 1'in 502'si ve
Görev 2'nin hata testi; karar 4 (pasif Kur) → Görev 2'nin üçüncü testi. Madde 8'in geometrisi →
Görev 3.

**2. Yer tutucu taraması:** `test_comfy_photo_generator.py`'nin sahte istemci adı o dosyanın kendi
kalıbına bırakıldı — orada var olan bir kalıp.

**3. Tür tutarlılığı:** `installed` her yerde bool; üretici anahtarları `photo`/`video`/`audio` ve
`producers.ORDER` ile şeridin `PANELS` kimlikleri aynı sözcükler; `ProducersGlyph` Görev 3'ün iki
yerinde de aynı ad.
