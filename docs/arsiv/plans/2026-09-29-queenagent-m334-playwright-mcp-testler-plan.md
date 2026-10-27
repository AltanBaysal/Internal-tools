# Madde 334 — Playwright MCP bu depoda · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Depo kökündeki `.mcp.json`'ın Playwright MCP kararlarını taşıdığını tutan altı test, kırmızı.

**Architecture:** Tek test dosyası, QueenAgent'ın arka uç süitinde; depo kökündeki dosyayı okur, ve
her kararın biçimini tutar — sürüm numarasının kendisini değil.

**Tech Stack:** pytest, Python'un kendi `json`, `os` ve `re` modülleri.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m334-playwright-mcp-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi: süzülmez, tek dosyaya ya da teste daraltılmaz.
- Kod, yorum ve test adları İngilizce; testin kullanıcıya düşen hata cümlesi Türkçe (`test_frontend_toolchain.py`'deki gibi).
- Commit mesajında çift tırnak yok; amend yok.
- Bu turda `.mcp.json` ve CLAUDE.md açılmaz.

---

### Task 1: Altı iddia, kırmızı

**Files:**
- Create: `queen-agent/backend/tests/test_playwright_mcp.py`

**Interfaces:**
- Consumes: yok.
- Produces: uygulama turunun yeşile getireceği altı test; depo kökünde `.mcp.json`, içinde `mcpServers.playwright` — `command` ve `args`.

- [ ] **Step 1: Testleri yaz**

```python
"""Playwright MCP is Claude's own browser, and the repo's root says how it starts (Madde 334).

The file examined is the root's .mcp.json. It is collected here because the item that brought it is
QueenAgent's, the same reason test_frontend_toolchain.py reads the frontend's manifest.

What is held is the shape of each decision, never the version number itself: raising the version is
an edit in one place, and a test repeating the number would be the second place to forget.
"""
import json
import os
import re

MCP = os.path.join(
    os.path.dirname(              # the repo
        os.path.dirname(          # queen-agent
            os.path.dirname(      # backend
                os.path.dirname(os.path.abspath(__file__))))),  # tests
    ".mcp.json",
)

PINNED = re.compile(r"^@playwright/mcp@\d+\.\d+\.\d+$")


def _servers():
    with open(MCP, encoding="utf-8") as handle:
        return json.load(handle)["mcpServers"]


def _args():
    return _servers()["playwright"]["args"]


def test_the_repo_root_defines_a_playwright_server():
    assert "playwright" in _servers(), "depo kökündeki .mcp.json bir playwright sunucusu tanımlamıyor"


def test_it_starts_through_npx():
    assert _servers()["playwright"]["command"] == "npx", "playwright sunucusu npx ile açılmıyor"


def test_the_package_version_is_pinned():
    # @latest, or no version at all, runs whatever npm holds at that moment -- and whatever the
    # package has become, the day it is taken over.
    packages = [arg for arg in _args() if arg.startswith("@playwright/mcp")]
    assert len(packages) == 1 and PINNED.match(packages[0]), (
        "@playwright/mcp sabit bir X.Y.Z sürümüyle bekleniyordu, @latest ya da sürümsüz değil"
    )


def test_the_browser_profile_stays_in_memory():
    assert "--isolated" in _args(), "--isolated yok -- tarayıcının profili diske yazılır"


def test_the_browser_opens_no_window():
    assert "--headless" in _args(), "--headless yok -- tarayıcı bir pencere açar"


def test_it_reaches_neither_the_open_browser_nor_the_whole_disk():
    # --cdp-endpoint would attach to the browser already open, with every session signed into it;
    # --allow-unrestricted-file-access would hand the browser every file on the machine.
    flags = {arg.split("=")[0] for arg in _args()}
    assert not flags & {"--cdp-endpoint", "--allow-unrestricted-file-access"}, (
        "--cdp-endpoint ya da --allow-unrestricted-file-access verilmiş"
    )
```

- [ ] **Step 2: Dört satırı koş, kırmızıyı gör**

CLAUDE.md'deki dört satır, yazıldığı gibi, paralel:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `python -m pytest queen-agent -q` altı kırmızı verir, hepsi `test_playwright_mcp.py`'den ve
hepsi `FileNotFoundError` ile — dosya henüz yok. Öteki üç süit yeşil.

- [ ] **Step 3: Kırmızıyı commit'le**

```powershell
git add queen-agent/backend/tests/test_playwright_mcp.py docs/specs/2026-09-29-queenagent-m334-playwright-mcp-testler-design.md docs/plans/2026-09-29-queenagent-m334-playwright-mcp-testler-plan.md
git commit -m @'
test(queen-agent): Madde 334 red -- the repo root is to define a pinned, headless Playwright MCP

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
