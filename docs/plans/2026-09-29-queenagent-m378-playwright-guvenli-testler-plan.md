# Madde 378 — Playwright MCP güvenli kullanılır · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tarayıcının yalnız bu makineye ve fontlara gittiğini, tarayıcı dışında kod çalıştırmadığını
ve yazdıklarının git'e girmediğini tutan dört iddia, kırmızı.

**Architecture:** `queen-agent/backend/tests/test_playwright_mcp.py`'ye dört test. Dosya depo kökünü
bir kez hesaplar, ve oradan üç dosyayı okur: `.mcp.json`, `.claude/settings.json`, `.gitignore`.

**Tech Stack:** pytest.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m378-playwright-guvenli-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; hata cümlesi Türkçe (dosyanın öteki testleri gibi).
- Bu turda `.mcp.json`, `.claude/settings.json`, `.gitignore` ve CLAUDE.md değişmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Dört iddia, kırmızı

**Files:**
- Modify: `queen-agent/backend/tests/test_playwright_mcp.py` — açıklama, yol sabitleri, ve sona dört test

**Interfaces:**
- Consumes: dosyanın bugünkü `_args()`'ı.
- Produces: uygulama turunun karşılayacağı üç şey — `.mcp.json`'da `"--allowed-origins"` ve hemen
  ardından `;` ile ayrılmış adresler; `.claude/settings.json`'da `permissions.deny` listesi;
  `.gitignore`'da `.playwright-mcp/` satırı.

- [ ] **Step 1: Açıklamayı ve yol sabitlerini değiştir**

Dosyanın başı şu hâle gelir:

```python
"""Playwright MCP is Claude's own browser, and the repo's root says how it starts (Madde 334) and what
it may reach (Madde 378).

The files examined are the root's .mcp.json, .claude/settings.json and .gitignore. They are collected
here because the items that brought them are QueenAgent's, the same reason test_frontend_toolchain.py
reads the frontend's manifest.

What is held is the shape of each decision, never the value itself: raising the version is an edit in
one place, and a test repeating the number would be the second place to forget. The origins go the
same way -- a new port on this machine passes unchanged, and only an address on the internet turns a
test red, because that one is the user's to decide.
"""
import json
import os
import re

REPO = os.path.dirname(           # the repo
    os.path.dirname(              # queen-agent
        os.path.dirname(          # backend
            os.path.dirname(os.path.abspath(__file__)))))  # tests
MCP = os.path.join(REPO, ".mcp.json")
SETTINGS = os.path.join(REPO, ".claude", "settings.json")
GITIGNORE = os.path.join(REPO, ".gitignore")

PINNED = re.compile(r"^@playwright/mcp@\d+\.\d+\.\d+$")
THIS_MACHINE = re.compile(r"^http://127\.0\.0\.1(:(\d+|\*))?$")
# Both tools' index.html load their fonts from these two; without them every screenshot is drawn in
# a fallback font the user never sees.
FONTS = {"https://fonts.googleapis.com", "https://fonts.gstatic.com"}
```

- [ ] **Step 2: `_args()`'ın altına listeyi okuyan yardımcıyı ekle**

```python
def _allowed_origins():
    args = _args()
    if "--allowed-origins" not in args:
        return []
    return args[args.index("--allowed-origins") + 1].split(";")
```

- [ ] **Step 3: Dosyanın sonuna dört testi ekle**

```python
def test_the_browser_requests_nothing_but_this_machine_and_the_fonts():
    # The package itself says the list is no security boundary and misses redirects. It stops a
    # request made by mistake; the rule it cannot hold -- no internet address is opened -- is in
    # CLAUDE.md.
    origins = _allowed_origins()
    strays = [origin for origin in origins if not THIS_MACHINE.match(origin) and origin not in FONTS]
    assert origins and not strays, (
        f"--allowed-origins yok ya da bu makine ve Google Fonts dışında adres taşıyor: {strays}"
    )


def test_the_tools_and_their_fonts_are_still_reachable():
    origins = _allowed_origins()
    assert any(THIS_MACHINE.match(origin) for origin in origins) and FONTS <= set(origins), (
        "--allowed-origins bu makinenin araçlarını ya da Google Fonts'u dışarıda bırakıyor"
    )


def test_no_code_runs_outside_the_browser():
    # browser_run_code_unsafe runs in the MCP server's own Node process, where the disk and the
    # network are both in reach and --allowed-origins sees nothing.
    with open(SETTINGS, encoding="utf-8") as handle:
        denied = json.load(handle)["permissions"]["deny"]
    assert "mcp__playwright__browser_run_code_unsafe" in denied, (
        ".claude/settings.json browser_run_code_unsafe'i yasaklamıyor"
    )


def test_what_the_browser_writes_stays_out_of_git():
    with open(GITIGNORE, encoding="utf-8") as handle:
        ignored = {line.strip() for line in handle}
    assert ".playwright-mcp/" in ignored, (
        ".gitignore .playwright-mcp/'yi dışarıda tutmuyor -- ekran görüntüleri git'e girer"
    )
```

- [ ] **Step 4: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `python -m pytest queen-agent -q` dört kırmızı — ikisi `--allowed-origins yok`, biri
`FileNotFoundError` (`.claude/settings.json` yok), biri `.playwright-mcp/` iddiası; 334'ün altı testi
yeşil kalır. `python -m pytest queen-editor -q` 377'nin bilinen iki kırmızısı. Ön uçların ikisi yeşil.

- [ ] **Step 5: Kırmızıyı commit'le**

```powershell
git add queen-agent/backend/tests/test_playwright_mcp.py docs/specs/2026-09-29-queenagent-m378-playwright-guvenli-testler-design.md docs/plans/2026-09-29-queenagent-m378-playwright-guvenli-testler-plan.md
git commit -m @'
test(queen-agent): Madde 378 red -- the browser reaches only this machine and its fonts, runs no code outside itself, writes nothing git sees

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
