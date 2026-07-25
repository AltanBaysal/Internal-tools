# Queen Editor — Bölüm 2: Bağlantı · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Colab'da arayüz derlenip Flask ile servis edilsin, cloudflared tüneli açılsın; açılan koyu temalı sayfa `/api/health`'e istek atıp "sunucuya bağlı ✓" göstersin.

**Architecture:** Tek origin — Flask hem derlenmiş `frontend/dist`'i (`/`) hem `/api/health`'i servis eder (CORS yok). Backend feature-first iskelet: `web/` altyapı katı (health, app factory), `main.py` composition root. Frontend Vite + React; `App.jsx` yüklenince `shared/api.js` üzerinden health çeker. **Arayüz geliştiricide derlenip `dist/` commit'lenir (ComfyUI deseni); Colab derlemez.** Notebook Bölüm 1'in klonuna Flask + cloudflared ekler.

**Tech Stack:** Python 3 · Flask · pytest · React 18 · Vite 5 (build-time) · Google Colab · cloudflared

**Spec:** [2026-07-25-queen-editor-b2-baglanti-design.md](../specs/2026-07-25-queen-editor-b2-baglanti-design.md)

## Global Constraints

- **Dil ayrımı:** `CODE-STANDARD.md`, kod yorumları/docstring, commit mesajları **İngilizce**; kullanıcıya görünen UI metni ve notebook markdown/`print`/`assert` **Türkçe**.
- **Katman yasakları:** `feature ↛ feature`, `servis ↛ feature`, `servis ↛ servis`. `web/health.py` altyapı — domain/data yok. Bağımlılık yönü `presentation → domain ← data → services`; somut bağlama yalnız `main.py`.
- **Tek origin, CORS yok:** Flask hem `dist/`'i hem `/api`'yi servis eder; `api.js` göreli `/api` çağırır.
- **Derleme (ComfyUI deseni):** arayüz geliştiricide `npm run build` ile derlenir; `frontend/dist/` + `package-lock.json` **commit'lenir**, `node_modules/` commit'lenmez. Colab'da npm/build yok.
- **Vendor dokunulmazlığı:** `frontend/src/vendor/` claude.ai/design projesinden birebir kopya, elle düzenlenmez.
- **Proje kökü = `queen-editor/`:** `pytest` ve `python -m backend.main` buradan çalışır; `backend` bir pakettir.
- **Test komutu:** `queen-editor/` içinden `pytest` — Flask test client, ComfyUI/Drive/tünel gerektirmez.
- **Commit politikası:** Kullanıcı Colab'da doğrulayıp "commit" demeden commit yok. Son task bunu bir kapı olarak taşır.
- **Node id'leri / ComfyUI / Drive:** bu bölümde yok (Bölüm 3-4).

---

### Task 1: CODE-STANDARD.md + .gitignore

**Files:**
- Create: `queen-editor/CODE-STANDARD.md`
- Create: `queen-editor/.gitignore`

**Interfaces:**
- Consumes: (yok)
- Produces: sonraki tüm task'ların uyacağı yapı sözleşmesi.

- [ ] **Step 1: `queen-editor/.gitignore` yaz**

```gitignore
__pycache__/
*.pyc
.pytest_cache/
node_modules/
```
(`dist/` **commit'lenir** — ComfyUI deseni, Colab servis eder; gitignore'a girmez.)

- [ ] **Step 2: `queen-editor/CODE-STANDARD.md` yaz** (İngilizce)

````markdown
# Queen Editor — Code Standard

Two building blocks, feature-first. Read this before adding code.

## Stack
Backend **Flask** (sync) + frontend **React 18** (JSX, built with Vite). We follow ComfyUI's
*deployment* pattern — the frontend is built by the developer and the built `dist/` ships in the
repo; Colab only clones and serves, it never runs npm/build. We deliberately do NOT copy ComfyUI's
*libraries*:
- **React, not Vue** — the UI comes verbatim from the claude.ai/design project, which is React;
  rewriting it in Vue would throw away the approved design for zero gain. We share no code with
  ComfyUI's frontend — we only talk to its HTTP/JSON API, and the browser framework is invisible
  across that boundary.
- **Flask, not aiohttp** — ComfyUI is async because it is a heavy, highly-concurrent engine
  (live websocket node execution, long GPU runs). Our backend is thin: file ops + kick off a job +
  poll status. Sync Flask is simpler and already preinstalled in Colab (nothing extra to install).
  Live progress, when needed, is polling or SSE — not aiohttp's websocket machinery.

Matching ComfyUI's frameworks without its reasons would be cargo-culting: it chose them for its
needs, ours differ. Revisit only if we ever embed the UI *inside* ComfyUI as a custom node.

## Services (`backend/services/`)
A service does one job, lives in its own folder, and knows **no feature**. Examples (land later):
`comfy/` (photo generator: prompt+negative+seed → bytes), `drive/` (read/write/list files).
A service never imports a feature and never imports another service.

## Features (`backend/features/<name>/`)
A user-facing capability, composed of three layers:
- **domain/** — pure rules, port definitions (`Protocol`), use cases. Imports nothing external
  (no `flask`, `requests`, or file-path/schema knowledge).
- **data/** — implements the ports using services; the only place that knows file schemas.
- **presentation/** — Flask routes; translates request/response, no business logic.

Dependency direction: `presentation → domain ← data → services`.
Bans (no exceptions): `feature ↛ feature`, `service ↛ feature`, `service ↛ service`.
Concrete classes are wired only in the composition root (`backend/main.py`).

## Infrastructure (`backend/web/`)
Cross-cutting HTTP plumbing that is not a domain feature: the app factory (`app.py`) and probes
like `health.py`. No `features/` folder is created until a real feature exists (Part 3: projects).

## Frontend (`frontend/src/`)
Same feature-first shape: `features/<name>/` with components + hooks (data access);
`shared/` for the fetch wrapper and app CSS; `vendor/` for verbatim design files.
- **vendor/** is copied from the claude.ai/design project and never hand-edited.

## Language
Code comments, docstrings, this file, and commit messages: **English**.
User-facing UI text and notebook markdown / `print` / `assert`: **Turkish**.

## Tests
Run `pytest` from `queen-editor/`. Domain and use cases test with fake ports — no ComfyUI, no Drive.
````

---

### Task 2: Backend — health API + app factory

**Files:**
- Create: `queen-editor/backend/__init__.py` (boş)
- Create: `queen-editor/backend/web/__init__.py` (boş)
- Create: `queen-editor/backend/config.py`
- Create: `queen-editor/backend/web/health.py`
- Create: `queen-editor/backend/web/app.py`
- Create: `queen-editor/backend/main.py`
- Create: `queen-editor/backend/requirements.txt`
- Create: `queen-editor/pytest.ini`
- Create: `queen-editor/backend/tests/test_health.py`

**Interfaces:**
- Consumes: (yok)
- Produces: `create_app(dist_dir=config.DIST_DIR) -> Flask`; `GET /api/health → 200 {"status": "ok"}`; `config.HOST`, `config.PORT`, `config.DIST_DIR`.

- [ ] **Step 1: `pytest.ini` yaz** (`queen-editor/pytest.ini` — proje kökü, `backend` paket olarak çözülsün)

```ini
[pytest]
pythonpath = .
testpaths = backend/tests
```

- [ ] **Step 2: `backend/requirements.txt` yaz**

```
flask>=3.0
pytest>=8.0
```

- [ ] **Step 3: Boş `__init__.py` dosyalarını yaz**

`queen-editor/backend/__init__.py` ve `queen-editor/backend/web/__init__.py` — ikisi de boş (paket işaretleyici).

- [ ] **Step 4: Failing test yaz** — `queen-editor/backend/tests/test_health.py`

```python
from backend.web.app import create_app


def test_health_returns_ok():
    client = create_app().test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
```

- [ ] **Step 5: Testi çalıştır, fail gör**

Run: `cd queen-editor && pytest -q`
Expected: FAIL — `ModuleNotFoundError: backend.web.app` (henüz yok).

- [ ] **Step 6: `backend/config.py` yaz**

```python
"""Runtime configuration -- the single place for paths and ports."""
import os

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Vite writes the built frontend here; Flask serves it (see web/app.py).
DIST_DIR = os.path.join(os.path.dirname(_BACKEND_DIR), "frontend", "dist")

HOST = "127.0.0.1"
PORT = 8000
```

- [ ] **Step 7: `backend/web/health.py` yaz**

```python
"""GET /api/health -- infrastructure liveness probe, not a domain feature."""
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health():
    return jsonify({"status": "ok"})
```

- [ ] **Step 8: `backend/web/app.py` yaz** (bu task'ta yalnız health; statik servis Task 3'te eklenir)

```python
"""create_app -- the Flask app factory. Registers /api blueprints; static dist
serving is added in the next task."""
from flask import Flask

from backend.web.health import health_bp
from backend import config


def create_app(dist_dir=config.DIST_DIR):
    app = Flask(__name__, static_folder=None)  # dist is served by our own routes
    app.config["DIST_DIR"] = dist_dir
    app.register_blueprint(health_bp)
    return app
```

- [ ] **Step 9: `backend/main.py` yaz**

```python
"""Composition root -- start the Flask server. Run as: python -m backend.main"""
from backend.web.app import create_app
from backend import config

app = create_app()

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)
```

- [ ] **Step 10: Testi çalıştır, geç gör**

Run: `cd queen-editor && pytest -q`
Expected: PASS (1 test).

---

### Task 3: Backend — dist statik servisi (SPA)

**Files:**
- Modify: `queen-editor/backend/web/app.py`
- Create: `queen-editor/backend/tests/test_static.py`

**Interfaces:**
- Consumes: `create_app(dist_dir)` (Task 2)
- Produces: `GET /` → `dist_dir/index.html`; var olan dosya → o dosya; bilinmeyen yol → `index.html` (SPA fallback).

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_static.py`

```python
from backend.web.app import create_app


def test_index_served_from_dist(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><title>QE</title>", encoding="utf-8")
    client = create_app(dist_dir=str(tmp_path)).test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"QE" in resp.data


def test_unknown_path_falls_back_to_index(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><title>QE</title>", encoding="utf-8")
    client = create_app(dist_dir=str(tmp_path)).test_client()
    resp = client.get("/projects/anything")
    assert resp.status_code == 200
    assert b"QE" in resp.data


def test_health_still_works_with_static(tmp_path):
    (tmp_path / "index.html").write_text("x", encoding="utf-8")
    client = create_app(dist_dir=str(tmp_path)).test_client()
    assert client.get("/api/health").get_json() == {"status": "ok"}
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && pytest -q`
Expected: FAIL — `/` 404 (statik route yok).

- [ ] **Step 3: `backend/web/app.py`'ye statik servis ekle**

`create_app` gövdesine, `return app`'ten önce:

```python
    import os
    from flask import send_from_directory

    @app.get("/")
    def index():
        return send_from_directory(app.config["DIST_DIR"], "index.html")

    # Any other path: serve the file if it exists, else fall back to index.html (SPA).
    # /api/* is matched by the more specific health rule first, so it never reaches here.
    @app.get("/<path:path>")
    def static_or_spa(path):
        full = os.path.join(app.config["DIST_DIR"], path)
        if os.path.isfile(full):
            return send_from_directory(app.config["DIST_DIR"], path)
        return send_from_directory(app.config["DIST_DIR"], "index.html")
```

- [ ] **Step 4: Testi çalıştır, hepsi geçsin**

Run: `cd queen-editor && pytest -q`
Expected: PASS (4 test: health + 3 statik).

---

### Task 4: Frontend — Vite + bağlantı sayfası

**Files:**
- Create: `queen-editor/frontend/package.json`
- Create: `queen-editor/frontend/vite.config.js`
- Create: `queen-editor/frontend/index.html`
- Create: `queen-editor/frontend/src/main.jsx`
- Create: `queen-editor/frontend/src/App.jsx`
- Create: `queen-editor/frontend/src/shared/api.js`
- Create: `queen-editor/frontend/src/vendor/styles.css` (tasarımdan birebir)
- Generate + commit: `queen-editor/frontend/package-lock.json` ve `queen-editor/frontend/dist/` (`npm install && npm run build` üretir)

**Interfaces:**
- Consumes: `GET /api/health` (Task 2)
- Produces: derlenmiş `frontend/dist/` (Flask'ın servis edeceği, **commit'lenen** çıktı).

- [ ] **Step 1: `frontend/package.json` yaz**

```json
{
  "name": "queen-editor-frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 2: `frontend/vite.config.js` yaz**

```js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base "./" -> assets load with relative paths, so Flask can serve dist from "/".
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: { outDir: "dist" },
});
```

- [ ] **Step 3: `frontend/index.html` yaz**

```html
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Queen Editor</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 4: `frontend/src/vendor/styles.css` oluştur — tasarımdan birebir**

Tasarım projesinden çek (elle yazma): DesignSync `get_file`, projectId `efad1f83-69d3-4e07-89fa-3783839c81c3`, path `styles.css` → içeriği `queen-editor/frontend/src/vendor/styles.css`'e birebir yaz. Bu dosya "Dark Minimal v2" koyu temasını, `--bg`/font tanımlarını ve `wf-*` sınıflarını (`wf-status`, `wf-hand`, `wf-hl` dahil) taşır.

- [ ] **Step 5: `frontend/src/shared/api.js` yaz**

```js
// Single fetch wrapper -- same-origin "/api", so no base URL and no CORS.
export async function getHealth() {
  const resp = await fetch("/api/health");
  if (!resp.ok) throw new Error(`health ${resp.status}`);
  return resp.json();
}
```

- [ ] **Step 6: `frontend/src/App.jsx` yaz**

```jsx
import { useEffect, useState } from "react";
import { getHealth } from "./shared/api.js";

// Part 2 is a connection proof: on load, call the server and show the result.
const LABEL = {
  checking: "kontrol ediliyor…",
  ok: "sunucuya bağlı ✓",
  error: "sunucuya bağlanılamadı ✗",
};

export default function App() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    getHealth()
      .then(() => setStatus("ok"))
      .catch(() => setStatus("error"));
  }, []);

  const cls =
    "wf-status" +
    (status === "ok" ? " wf-status--hl" : status === "error" ? " wf-status--err" : "");

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 16,
      }}
    >
      <span className="wf-hand" style={{ fontSize: 28 }}>
        <span className="wf-hl">Queen Editor</span>
      </span>
      <span className={cls}>
        {status === "checking" && <span className="dot" />}
        {LABEL[status]}
      </span>
    </div>
  );
}
```

- [ ] **Step 7: `frontend/src/main.jsx` yaz**

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./vendor/styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
```

- [ ] **Step 8: Bağımlılıkları kur + derle + dist'i commit'e hazırla**

Run: `cd queen-editor/frontend && npm install && npm run build`
Expected: `package-lock.json` oluşur, `dist/index.html` + `dist/assets/*` üretilir, hata yok. **`dist/` ve `package-lock.json` commit'lenir** (`node_modules/` gitignore'da). UI her değişince bu adım tekrarlanıp `dist/` yeniden commit'lenir.

---

### Task 5: Notebook — serve + tünel (build yok)

**Files:**
- Modify: `queen-editor/app.ipynb`

**Interfaces:**
- Consumes: Task 2-4 (backend + derlenmiş `frontend/dist` klonla gelir).
- Produces: Colab'da çalışan sayfa + cloudflared linki.

Bölüm 1'in notebook'una eklenir/güncellenir: başlık markdown'ı Bölüm 2'yi anlatır (arayüz derlenmiş gelir, Colab derlemez); klon hücresi `frontend/dist`'in geldiğini fail-loud doğrular; **node ve build hücresi yok**; serve+tünel hücresi eklenir. Hücre içerikleri (kod yorumları İngilizce, çıktı Türkçe):

- [ ] **Step 1: Başlık markdown hücresini güncelle**

```markdown
# Queen Editor — Bağlantı (Bölüm 2)

Repoyu klonlar → **Flask** derlenmiş arayüzü (`frontend/dist`) servis eder → **cloudflared** linki
basar. Açılan sayfa `/api/health` isteği atıp **"sunucuya bağlı ✓"** gösterir. Drive, ComfyUI yok.
Arayüz repoya **derlenmiş** gelir (ComfyUI deseni); Colab'da npm/build çalışmaz.

## Kullanım
1. Bu `app.ipynb`'yi Colab'a yükle (**File → Upload notebook**).
2. 🔑 Secrets'a `GITHUB_TOKEN` ekli olmalı (Bölüm 1 — README).
3. **Runtime → Run all** → en alttaki linke gir.
```

- [ ] **Step 2: Klon hücresine dist doğrulaması ekle**

Klon başarılı olduktan sonra, `print("✓ Klon tamam")` yerine:

```python
# The built frontend ships in the repo (frontend/dist) -- fail loud if it is missing, so a
# forgotten rebuild-and-commit shows up here, not as a blank page.
DIST = os.path.join(CLONE_DIR, "queen-editor", "frontend", "dist", "index.html")
assert os.path.exists(DIST), f"❌ Derlenmiş arayüz yok: {DIST} — frontend'i derleyip commit'le (README)"
print("✓ Klon tamam (derlenmiş arayüz mevcut)")
```

- [ ] **Step 3: Serve + tünel hücresi ekle**

```python
# === Start Flask (background) + cloudflared tunnel ===
# Flask runs as a module from queen-editor/ so `backend` resolves as a package. The cell stays
# OPEN (tail -f): if it ends, Colab calls the runtime idle and kills the tunnel.
import subprocess, time, os, re, urllib.request

APP_DIR = os.path.join(CLONE_DIR, "queen-editor")
APP_PORT = 8000
FLASK_LOG = "/content/flask.log"

# Re-run safety: kill previous instances
subprocess.run(["pkill", "-f", "backend.main"], check=False)
subprocess.run(["pkill", "-f", "cloudflared"], check=False)
time.sleep(2)

logf = open(FLASK_LOG, "w")
subprocess.Popen(["python", "-m", "backend.main"], cwd=APP_DIR, stdout=logf, stderr=subprocess.STDOUT)

ok = False
for i in range(45):
    time.sleep(2)
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{APP_PORT}/api/health", timeout=2)
        ok = True
        break
    except Exception:
        pass
if not ok:
    print("".join(open(FLASK_LOG).readlines()[-30:]))
    raise RuntimeError("❌ Flask 90 sn içinde /api/health'e cevap vermedi — yukarıdaki log'a bak")
print(f"✓ Flask ayakta ({(i + 1) * 2}s)")

if not os.path.isfile("/content/cloudflared"):
    subprocess.run(["wget", "-q", "-O", "/content/cloudflared",
                    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"], check=True)
    subprocess.run(["chmod", "+x", "/content/cloudflared"], check=True)

tunlog = "/content/cloudflared.log"
subprocess.Popen(["/content/cloudflared", "tunnel", "--url", f"http://127.0.0.1:{APP_PORT}"],
                 stdout=open(tunlog, "w"), stderr=subprocess.STDOUT)
link = None
for _ in range(30):
    time.sleep(1)
    if os.path.exists(tunlog):
        m = re.search(r"https://[-\w.]+trycloudflare\.com", open(tunlog).read())
        if m:
            link = m.group(0)
            break
if not link:
    print(open(tunlog).read()[-1000:] if os.path.exists(tunlog) else "(cloudflared log yok)")
    raise RuntimeError("❌ cloudflared linki 30 sn içinde alınamadı")

print(f"\n🔗 Queen Editor: {link}\n")
print("⬆️  Linke gir → 'sunucuya bağlı ✓' görmelisin.\n")
print("📡 Sunucu çalışıyor — BU HÜCREYİ KAPATMA. Canlı log:\n")
try:
    subprocess.run(["tail", "-n", "+1", "-f", FLASK_LOG])
except KeyboardInterrupt:
    print("Hücre durduruldu — Flask hâlâ arka planda (yeni link için tekrar çalıştır).")
```

- [ ] **Step 4: Notebook'un geçerli JSON olduğunu doğrula**

Read ile `queen-editor/app.ipynb` açılır; hücreler (markdown + CONFIG + klon + serve) düzgün ayrışıyorsa geçerli. (Kod mantığının gerçek testi Colab'da.)

---

### Task 6: Colab doğrulaması + commit (kullanıcı kapısı)

**Files:** (yok — doğrulama + commit)

- [ ] **Step 1: Kullanıcı Colab doğrulaması**

Kullanıcı `app.ipynb`'yi Colab'a yükler (Secrets'ta `GITHUB_TOKEN` var), **Run all**. Beklenen:
- Repo klonlanır (dist ile), Flask `/api/health`'e cevap verir, cloudflared linki basılır (npm/build yok).
- Linke girince koyu temalı sayfa: **"sunucuya bağlı ✓"**. Akıcı; yenile → yine bağlı.
- (Negatif) Flask durdurulup sayfa yenilenince **"sunucuya bağlanılamadı ✗"**.

- [ ] **Step 2: Kullanıcı onayıyla commit**

Kullanıcı "çalışıyor, commit" dedikten sonra, açık pathspec ile iki commit (docs / feat) + push:

```bash
# docs
git add -- docs/superpowers/specs/2026-07-25-queen-editor-b2-baglanti-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b2-baglanti.md
git commit -m "docs(queen-editor): Bölüm 2 — bağlantı spec + plan" -- \
  docs/superpowers/specs/2026-07-25-queen-editor-b2-baglanti-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b2-baglanti.md
# feat (queen-editor kodu + derlenmiş dist + güncellenen notebook/README)
git add -- queen-editor/CODE-STANDARD.md queen-editor/.gitignore queen-editor/pytest.ini \
  queen-editor/README.md queen-editor/backend queen-editor/frontend queen-editor/app.ipynb
git commit -m "feat(queen-editor): Bölüm 2 — Flask + Vite, /api/health bağlantısı (dist ship)" -- \
  queen-editor/CODE-STANDARD.md queen-editor/.gitignore queen-editor/pytest.ini \
  queen-editor/README.md queen-editor/backend queen-editor/frontend queen-editor/app.ipynb
git push origin feat/queen-editor-v1
```

(`node_modules/` `.gitignore`'da — commit'e girmez. `frontend/dist/` **commit'lenir** (ComfyUI deseni). `queen-editor/frontend` pathspec'i dist + kaynağı birlikte kapsar. Pathspec kullanılır, `git add` + bare commit değil.)

---

## Doğrulama özeti

| Ne | Nasıl |
|---|---|
| Backend health + statik | `cd queen-editor && pytest` → 4 test geçer |
| Frontend derleniyor | `cd frontend && npm install && npm run build` → dist üretilir |
| Uçtan uca bağlantı | Colab Run all → link → "sunucuya bağlı ✓" |
| Negatif | Flask durunca sayfa "bağlanılamadı ✗" |
| Bölüm 2 kapanır | Kullanıcı Colab'da doğrular → commit + push |
