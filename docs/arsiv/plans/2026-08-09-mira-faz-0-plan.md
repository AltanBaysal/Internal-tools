# Mira Faz 0 (İskelet) — Uygulama Planı

> **Ajan işçiler için:** Bu plan `superpowers:executing-plans` ile madde madde uygulanır. Adımlar
> takip için kutucuk (`- [ ]`) sözdizimindedir.

**Hedef:** `mira/` aracını ayağa kaldırmak — Flask iskeleti, React iskeleti, CSS temeli, test koşum
düzeni ve üç belge; görünür çıktısı tasarımın zemin renginde boş bir sayfa.

**Mimari:** Sync Flask app factory kendi statik rotalarıyla `frontend/dist/`'i servis eder ve bilinmeyen
yolları `index.html`'e düşürür; `/api/*` daha özel bir kural olduğu için bu düşüşe takılmaz. Somut
sınıflar yalnız `main.py`'de bağlanır — `web/` hiçbir feature ithal etmez. Ön yüz Vite ile derlenen
React 18'dir; geliştirmede Vite kendi sunucusunda çalışıp `/api`'yi Flask'a proxy'ler.

**Yığın:** Python 3 · Flask · pytest · React 18 · Vite 5 · Vitest 3 · Testing Library · jsdom

**Kaynak spec:** [Faz 0 — İskelet](../specs/2026-08-09-mira-faz-0-iskelet-design.md)

## Global Kısıtlar

- Bütün kod, yorum, docstring, test adı ve arayüz metni **İngilizce**. Bu belgeler Türkçe.
- Bağımlılık yönü `presentation → domain ← data → services`; `web/` hiçbir feature ithal etmez.
- Renk, yarıçap ve odak kuralı tek yerde: `frontend/src/shared/app.css`. Hiçbir bileşen kendi odak
  stilini yazmaz.
- Vurgu rengi `#B5623C` yalnız birincil eylemi işaretler.
- Port `8100` (queen-editor `8000`'i kullanıyor). Kök dizin repo dışında, `MIRA_ROOT` ile adlanır.
- `frontend/dist/` ve `node_modules/` git'e girmez.
- **Commit adımı yoktur** — bu koşuda commit'ler en sonda topluca atılır.
- Yorum ne yaptığını değil **niçin** yaptığını anlatır; koda uymayan yorum kodu değil, yorumu bozar.

---

### Task 1: Backend paketi ve sağlık yoklaması

**Dosyalar:**
- Oluştur: `mira/pytest.ini`
- Oluştur: `mira/backend/__init__.py`, `mira/backend/web/__init__.py`,
  `mira/backend/services/__init__.py`, `mira/backend/features/__init__.py`
- Oluştur: `mira/backend/config.py`
- Oluştur: `mira/backend/web/health.py`
- Oluştur: `mira/backend/web/app.py`
- Test: `mira/backend/tests/test_health.py`

**Arayüzler:**
- Üretir: `create_app(dist_dir=config.DIST_DIR, blueprints=()) -> flask.Flask` ·
  `health_bp: flask.Blueprint` · `config.DIST_DIR`, `config.HOST`, `config.PORT`, `config.ROOT`,
  `config.XAI_API_KEY`

- [ ] **Adım 1: Başarısız testi yaz**

`mira/backend/tests/test_health.py`:

```python
from backend.web.app import create_app


def test_health_returns_ok():
    client = create_app().test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
```

- [ ] **Adım 2: Testi koş, başarısız olduğunu gör**

`mira/` dizininden: `pytest backend/tests/test_health.py -v`
Beklenen: FAIL — `ModuleNotFoundError: No module named 'backend'`

- [ ] **Adım 3: pytest yapılandırması ve boş paketler**

`mira/pytest.ini`:

```ini
[pytest]
pythonpath = .
testpaths = backend/tests
```

Boş dosyalar: `mira/backend/__init__.py`, `mira/backend/web/__init__.py`,
`mira/backend/services/__init__.py`, `mira/backend/features/__init__.py`.

`services/` ve `features/` bugün boş: Faz 1 ilk gerçek içeriği koyar, paket dosyası şimdiden var ki
ithal yolu ilk günden doğru olsun.

- [ ] **Adım 4: config, health ve app factory**

`mira/backend/config.py`:

```python
"""Runtime configuration -- the single place for paths, ports and engine settings."""
import os

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Vite writes the built frontend here; Flask serves it (see web/app.py).
DIST_DIR = os.path.join(os.path.dirname(_BACKEND_DIR), "frontend", "dist")

HOST = "127.0.0.1"
PORT = 8100  # queen-editor owns 8000 and both can run on this machine at the same time

# Every project is a folder under this root. It lives outside the repo so user data never lands in
# the source tree and `git status` never sees it.
ROOT = os.environ.get("MIRA_ROOT", os.path.join(os.path.expanduser("~"), "Mira"))

# Read here so the whole app has one source for it; the engine that uses it arrives in Faz 6.
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
```

`mira/backend/web/health.py`:

```python
"""GET /api/health -- infrastructure liveness probe, not a domain feature."""
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health():
    return jsonify({"status": "ok"})
```

`mira/backend/web/app.py`:

```python
"""create_app -- the Flask app factory: /api blueprints + static dist serving."""
import os

from flask import Flask, send_from_directory

from backend import config
from backend.web.health import health_bp


def create_app(dist_dir=config.DIST_DIR, blueprints=()):
    app = Flask(__name__, static_folder=None)  # dist is served by our own routes
    app.config["DIST_DIR"] = dist_dir
    app.register_blueprint(health_bp)
    # Features are injected by the composition root: this infrastructure layer must not import any
    # feature (CODE-STANDARD.md).
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    @app.get("/")
    def index():
        return send_from_directory(app.config["DIST_DIR"], "index.html")

    # Any other path: serve the file if it exists, else fall back to index.html (SPA). /api/* is
    # matched by the more specific blueprint rules first, so it never reaches here.
    @app.get("/<path:path>")
    def static_or_spa(path):
        full = os.path.join(app.config["DIST_DIR"], path)
        if os.path.isfile(full):
            return send_from_directory(app.config["DIST_DIR"], path)
        return send_from_directory(app.config["DIST_DIR"], "index.html")

    return app
```

- [ ] **Adım 5: Testi koş, geçtiğini gör**

`mira/` dizininden: `pytest backend/tests/test_health.py -v`
Beklenen: PASS (1 test)

---

### Task 2: Statik servis ve SPA geri düşüşü

**Dosyalar:**
- Test: `mira/backend/tests/test_static.py`

**Arayüzler:**
- Tüketir: Task 1'in `create_app(dist_dir=...)` imzası

Bu task'ın kendi üretim kodu yoktur: Task 1'in rotalarını dört ayrı iddiaya bağlar. Ayrı durmasının
sebebi, dördüncü testin bir kazayı kollaması — statik rota `/api/*`'i yutarsa bütün uç noktalar
sessizce `index.html` döndürür ve hata Faz 6'ya kadar görünmez.

- [ ] **Adım 1: Başarısız testleri yaz**

`mira/backend/tests/test_static.py`:

```python
from backend.web.app import create_app


def _dist(tmp_path):
    """A throwaway dist/ so the tests never depend on a real build."""
    (tmp_path / "index.html").write_text("<!doctype html><div id=root></div>", encoding="utf-8")
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "app.js").write_text("console.log(1)", encoding="utf-8")
    return create_app(dist_dir=str(tmp_path)).test_client()


def test_root_serves_index(tmp_path):
    resp = _dist(tmp_path).get("/")
    assert resp.status_code == 200
    assert b"id=root" in resp.data


def test_existing_asset_is_served_as_is(tmp_path):
    resp = _dist(tmp_path).get("/assets/app.js")
    assert resp.status_code == 200
    assert b"console.log(1)" in resp.data


def test_unknown_path_falls_back_to_index(tmp_path):
    resp = _dist(tmp_path).get("/projects/anything")
    assert resp.status_code == 200
    assert b"id=root" in resp.data


def test_api_route_is_not_swallowed_by_the_spa_fallback(tmp_path):
    resp = _dist(tmp_path).get("/api/health")
    assert resp.get_json() == {"status": "ok"}
```

- [ ] **Adım 2: Testleri koş**

`mira/` dizininden: `pytest -v`
Beklenen: 5 test PASS (Task 1'in testi + bu dördü). Hepsi Task 1'in kodunu doğruluyor; yeni üretim
kodu gerekmiyor. Bir tanesi bile kırmızıysa hata Task 1'dedir, burada değil.

---

### Task 3: Kompozisyon kökü

**Dosyalar:**
- Oluştur: `mira/main.py`

**Arayüzler:**
- Tüketir: `create_app`, `config.HOST`, `config.PORT`
- Üretir: `python mira/main.py` ile çalışan bir sunucu

- [ ] **Adım 1: main.py yaz**

```python
"""Composition root -- the only place that wires concrete classes together."""
from backend import config
from backend.web.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)
```

- [ ] **Adım 2: Testleri koş**

`mira/` dizininden: `pytest -v`
Beklenen: 5 test PASS — `main.py` hiçbir testi bozmadı.

Sunucuyu şimdi elle açmaya gerek yok: `dist/` henüz üretilmedi, açılış Task 4'ten sonra denenir.

---

### Task 4: Ön yüz iskeleti ve CSS temeli

**Dosyalar:**
- Oluştur: `mira/frontend/package.json`, `mira/frontend/vite.config.js`, `mira/frontend/index.html`
- Oluştur: `mira/frontend/src/main.jsx`, `mira/frontend/src/App.jsx`,
  `mira/frontend/src/test-setup.js`, `mira/frontend/src/shared/app.css`
- Test: `mira/frontend/src/App.test.jsx`

**Arayüzler:**
- Üretir: `App` (varsayılan dışa aktarım) · `.app-shell` sınıfı · `app.css`'teki renk değişkenleri
  (`--canvas`, `--sidebar`, `--surface`, `--accent`, `--accent-strong`, `--ink`, `--muted`, `--line`)
  ve kare-dizileri (`riseIn`, `blink`, `spin`, `slideIn`) — sonraki bütün fazlar bunları kullanır,
  yenisini icat etmez.

- [ ] **Adım 1: Paket ve yapılandırma dosyaları**

`mira/frontend/package.json`:

```json
{
  "name": "mira-frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@testing-library/dom": "^10.4.1",
    "@testing-library/react": "^16.3.2",
    "@vitejs/plugin-react": "^4.3.1",
    "jsdom": "^29.1.1",
    "vite": "^5.4.0",
    "vitest": "^3.2.7"
  }
}
```

`mira/frontend/vite.config.js`:

```js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base "/" -> assets load from an absolute path, which the nested routes need. Flask serves dist at
// the root and falls back to index.html for unknown paths, so a relative "./assets/..." would
// resolve against /projects/<id>/ on a reload, hit that fallback and load index.html as the module
// script -- a blank page.
export default defineConfig({
  plugins: [react()],
  base: "/",
  build: { outDir: "dist" },
  // Dev only: the UI runs on Vite's own server and talks to Flask across ports. The built app is
  // served by Flask itself, so this proxy never applies in use.
  server: { proxy: { "/api": "http://127.0.0.1:8100" } },
  // Vitest reuses this config, so tests get the same JSX transform as the build. Test files live
  // next to their source and are never imported, so they stay out of dist/.
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
  },
});
```

`mira/frontend/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Mira</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400&display=swap" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Adım 2: Bağımlılıkları kur**

`mira/frontend/` dizininden: `npm install`
Beklenen: `node_modules/` oluşur, hata yok.

- [ ] **Adım 3: Başarısız testi yaz**

`mira/frontend/src/test-setup.js`:

```js
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Testing Library only auto-cleans when vitest runs with globals; we keep globals off, so unmount
// between tests by hand -- otherwise every render stacks up in the same jsdom document.
afterEach(cleanup);
```

`mira/frontend/src/App.test.jsx`:

```jsx
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import App from "./App.jsx";

test("renders the shell", () => {
  render(<App />);
  expect(screen.getByTestId("app-shell")).toBeTruthy();
});
```

- [ ] **Adım 4: Testi koş, başarısız olduğunu gör**

`mira/frontend/` dizininden: `npm test`
Beklenen: FAIL — `Failed to resolve import "./App.jsx"`

- [ ] **Adım 5: CSS temelini yaz**

`mira/frontend/src/shared/app.css`:

```css
/* The design's visual language, in one place. Colours, radii and the focus ring are defined here
   and nowhere else: a component that writes its own focus outline breaks the app-wide rule. */
:root {
  --canvas: #f7f5f1;
  --sidebar: #efebe4;
  --surface: #fffdfa;
  --accent: #b5623c;
  --accent-strong: #8f4a2c;
  --ink: #22201d;
  --muted: #8b8378;
  --line: #e2dcd2;

  --radius-control: 8px;
  --radius-card: 12px;
  --radius-pill: 20px;

  --font-heading: "Newsreader", Georgia, serif;
  --font-body: "DM Sans", system-ui, sans-serif;
  --font-mono: "DM Mono", monospace;
}

* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
}

body {
  background: var(--canvas);
  color: var(--ink);
  font-family: var(--font-body);
  -webkit-font-smoothing: antialiased;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  color: var(--accent-strong);
}

:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: var(--radius-control);
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-thumb {
  background: #ded7cd;
  border-radius: 8px;
  border: 3px solid transparent;
  background-clip: content-box;
}

/* The only motion the design allows: opacity fades and the rail's width transition. Nothing here
   moves a laid-out element sideways. */
@keyframes riseIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes blink {
  0%,
  80%,
  100% {
    opacity: 0.25;
  }
  40% {
    opacity: 1;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.app-shell {
  display: flex;
  height: 100%;
  min-height: 600px;
  width: 100%;
  overflow: hidden;
  background: var(--canvas);
}
```

- [ ] **Adım 6: App ve giriş noktasını yaz**

`mira/frontend/src/App.jsx`:

```jsx
import "./shared/app.css";

// Faz 0 paints the canvas and nothing else -- the sidebar and the screens arrive in Faz 2.
export default function App() {
  return <div className="app-shell" data-testid="app-shell" />;
}
```

`mira/frontend/src/main.jsx`:

```jsx
import React from "react";
import { createRoot } from "react-dom/client";

import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

- [ ] **Adım 7: Testi koş, geçtiğini gör**

`mira/frontend/` dizininden: `npm test`
Beklenen: PASS (1 test)

- [ ] **Adım 8: Derle ve uygulamayı elle aç**

`mira/frontend/` dizininden: `npm run build` → `dist/` oluşur.
`mira/` dizininden: `python main.py` → `http://127.0.0.1:8100`
Beklenen: tasarımın zemin renginde (`#F7F5F1`) boş bir sayfa; konsolda hata yok.

---

### Task 5: Belgeler ve git ayarı

**Dosyalar:**
- Oluştur: `mira/FOUNDATION.md`, `mira/CODE-STANDARD.md`, `mira/README.md`, `mira/.gitignore`
- Değiştir: `CLAUDE.md` (kök) — Mira bölümü

**Arayüzler:**
- Üretir: sonraki bütün fazların uyacağı yazılı kurallar

- [ ] **Adım 1: `mira/.gitignore`**

```gitignore
__pycache__/
*.pyc
.pytest_cache/
node_modules/

# The frontend is built on the machine that runs it -- unlike queen-editor, nothing here ships
# pre-built.
frontend/dist/
```

- [ ] **Adım 2: `mira/FOUNDATION.md`**

İlkeler queen-editor'ünkilerle aynı sırada ve aynı gerekçeyle yazılır (kullanıcının emeği kutsaldır ·
gerçek diskte durur · correctness > simplicity > generality > performance · kod yeniden
üretilebilirlik için yazılır). Kararlar Faz 0 spec'inin 7. bölümündeki yedi maddedir; her karar
**neden** cümlesiyle ve **sonuç** cümlesiyle yazılır. Ürün kararları (ekran, akış, davranış) bu
dosyaya girmez — onların yeri spec'lerdir.

- [ ] **Adım 3: `mira/CODE-STANDARD.md`**

Bölümler Faz 0 spec'inin 8. bölümünde sayılı: Yığın · Bağımsızlık · Katmanlar (tek feature
`workspace` kararının gerekçesiyle) · Diskteki gerçek · Ön yüz (`vendor/` yok, tasarım görsel
şartnamedir) · Dil · Testler.

Dil bölümü queen-editor'den **ayrıştığını açıkça** yazar: Mira'nın arayüz metni İngilizcedir, çünkü
tasarımın bütün metinleri İngilizce yazılmıştır ve çevirmek tasarımı kaynak olmaktan çıkarır.

- [ ] **Adım 4: `mira/README.md`**

Üç şey: ne olduğu (bir cümle), nasıl çalıştırıldığı (kurulum → derleme → açılış, `MIRA_ROOT` ve
`XAI_API_KEY` dahil), testlerin nasıl koşulduğu. Kural anlatmaz, belgelere bağlantı verir.

- [ ] **Adım 5: Kök `CLAUDE.md`'ye Mira bölümü**

queen-editor bölümünün ardına `## mira — Mira (web UI)` eklenir: bir cümlelik tanım, üç bağlantı
(`FOUNDATION.md`, `CODE-STANDARD.md`, yol haritası) ve queen-editor'den **ayrışan iki kural** —
arayüz dili İngilizce, `dist/` commit edilmez. Bu iki satır olmazsa komşu aracın kuralları buraya
sızar.

- [ ] **Adım 6: Kapanış doğrulaması**

`mira/` dizininden: `pytest -v` → 5 test PASS
`mira/frontend/` dizininden: `npm test` → 1 test PASS
`git status` → `dist/` ve `node_modules/` görünmüyor.

---

## Öz-denetim

**Spec kapsaması.** Faz 0 spec'inin 11 bölümü: klasör düzeni (Task 1, 4) · çalıştırma ve derleme
(Task 3, 4) · Flask iskeleti (Task 1, 2) · React iskeleti (Task 4) · CSS temeli (Task 4) · testler
(Task 1, 2, 4) · FOUNDATION (Task 5) · CODE-STANDARD (Task 5) · CLAUDE.md (Task 5) · kabul kriteri
(Task 4 Adım 8, Task 5 Adım 6) · Faz 1'e bırakılanlar (plan dışı, doğru).

**Ad tutarlılığı.** `create_app(dist_dir, blueprints)` Task 1'de tanımlanıyor, Task 2 ve 3 aynı imzayı
kullanıyor. `config.ROOT` yalnız tanımlanıyor, Faz 1 kullanacak. `App` varsayılan dışa aktarım,
`App.test.jsx` ve `main.jsx` aynı adı ithal ediyor. CSS değişkenleri ve kare-dizileri Task 4'te
tanımlanıp sonraki fazlara devrediyor.

**Yer tutucu yok.** Task 5'in üç belgesi içerik listesiyle tarif edilmiştir, bunlar düz yazı
dosyalardır ve kaynakları spec'in 7. ve 8. bölümleridir; kod adımlarının hepsinde gerçek kod var.
