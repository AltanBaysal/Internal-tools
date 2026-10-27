# Madde 334 — Playwright MCP bu depoda · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Depo kökündeki `.mcp.json` altı testi yeşile getirir, ve CLAUDE.md sunucuyu tanıtır.

**Architecture:** Tek bir ayar dosyası, queen-design'ınkinin aynısı; CLAUDE.md'nin `Commands`
bölümüne bir paragraf, nedenleri testin dosyasına bırakarak.

**Tech Stack:** Claude Code'un proje kapsamlı MCP ayarı (`.mcp.json`), `@playwright/mcp` `0.0.82`, npx.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m334-playwright-mcp-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi.
- Sürüm `@playwright/mcp@0.0.82`; bayraklar `--isolated`, `--headless`; başka bayrak yok.
- CLAUDE.md İngilizce; bayrakların nedeni orada tekrar yazılmaz.
- Commit mesajında çift tırnak yok; amend yok. Ön uca dokunulmuyor, `dist` derlenmez.

---

### Task 1: Ayar ve not

**Files:**
- Create: `.mcp.json`
- Modify: `CLAUDE.md` — `## Commands` bölümünün sonu, `## Writing a roadmap`'ten önce
- Test: `queen-agent/backend/tests/test_playwright_mcp.py` (kırmızı, `3c643337`)

**Interfaces:**
- Consumes: testlerin okuduğu biçim — `mcpServers.playwright.command` ve `mcpServers.playwright.args`.
- Produces: Claude Code'un yeniden açılınca bulacağı `playwright` sunucusu.

- [ ] **Step 1: `.mcp.json`'ı yaz**

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@0.0.82", "--isolated", "--headless"]
    }
  }
}
```

- [ ] **Step 2: CLAUDE.md'ye paragrafı ekle**

`## Commands` bölümündeki derleme kod bloğunun hemen altına:

```markdown
**Playwright MCP is Claude's own browser**, for looking at a running tool the way the user does. It
is defined in [.mcp.json](.mcp.json), so Claude Code offers the server on its first start in this
repo and asks once to approve it. The version is pinned and raised by hand; why each flag is there
is in [test_playwright_mcp.py](queen-agent/backend/tests/test_playwright_mcp.py), which holds them.
```

- [ ] **Step 3: Dört satırı koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent'ın arka ucu 929 yeşil; iki ön uç yeşil. queen-editor'ün arka ucunda tek
kırmızı kalır — `test_a_roadmap_can_still_reach_everything_it_links_to`, bu maddeden önce vardı
*(`d9c2d6f5`)* ve ayrı bir madde olarak soruluyor.

- [ ] **Step 4: Commit'le**

```powershell
git add .mcp.json CLAUDE.md docs/specs/2026-09-29-queenagent-m334-playwright-mcp-uygulama-design.md docs/plans/2026-09-29-queenagent-m334-playwright-mcp-uygulama-plan.md
git commit -m @'
feat: Madde 334 -- the repo root defines Claude's Playwright MCP, pinned and headless

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
