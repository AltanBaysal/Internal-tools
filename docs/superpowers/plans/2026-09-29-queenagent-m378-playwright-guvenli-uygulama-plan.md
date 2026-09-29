# Madde 378 — Playwright MCP güvenli kullanılır · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 378'in dört kırmızı testini yeşile getirmek, ve kuralları CLAUDE.md'ye yazmak.

**Architecture:** Kod yok; üç ayar dosyası ve bir belge. `.mcp.json` tarayıcının gidebileceği yerleri
sayar, `.claude/settings.json` tarayıcı dışında kod çalıştıran aracı reddeder, `.gitignore`
tarayıcının çıktısını git'ten uzak tutar, CLAUDE.md ayarın tutamadığı kuralı söyler.

**Tech Stack:** Claude Code proje ayarı, Playwright MCP `0.0.82`, git.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m378-playwright-guvenli-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- İzinli adresler tam olarak: `http://127.0.0.1:*;https://fonts.googleapis.com;https://fonts.gstatic.com`.
- CLAUDE.md İngilizce; bayrakların nedenini tekrar etmez, test dosyasını anar.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Ayarlar ve CLAUDE.md, yeşil

**Files:**
- Modify: `.mcp.json`
- Create: `.claude/settings.json`
- Modify: `.gitignore` — sonuna
- Modify: `CLAUDE.md` — `Commands` bölümündeki Playwright paragrafı
- Test: `queen-agent/backend/tests/test_playwright_mcp.py` (değişmez)

**Interfaces:**
- Consumes: testlerin beklediği üç biçim — `args`'ta `"--allowed-origins"` ve hemen ardından `;` ile
  ayrılmış adresler; `permissions.deny` listesi; `.playwright-mcp/` satırı.
- Produces: yok.

- [ ] **Step 1: `.mcp.json`**

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@0.0.82", "--isolated", "--headless",
        "--allowed-origins", "http://127.0.0.1:*;https://fonts.googleapis.com;https://fonts.gstatic.com"
      ]
    }
  }
}
```

- [ ] **Step 2: `.claude/settings.json`**

```json
{
  "permissions": {
    "deny": ["mcp__playwright__browser_run_code_unsafe"]
  }
}
```

- [ ] **Step 3: `.gitignore`'ın sonuna**

```
# What Playwright MCP writes as it looks: snapshots, console logs, screenshots.
.playwright-mcp/
```

- [ ] **Step 4: CLAUDE.md — paragrafın altına üç madde**

Bugünkü paragraf yerinde kalır; altına:

```markdown
- **It opens only the tools running on this machine, never an address on the internet.** The flag
  listing what it may reach is no security boundary — the package says so, and it misses redirects
  — so the rule is this line, not the list. An address the list does not hold is the user's call.
- **Never use `browser_run_code_unsafe`**: it runs outside the browser, and
  [.claude/settings.json](.claude/settings.json) denies it. For code inside the page, use
  `browser_evaluate`.
- **Give a screenshot no file name.** Unnamed output lands in `.playwright-mcp/`, which git
  ignores; a named one lands in the repo's root.
```

- [ ] **Step 5: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `python -m pytest queen-agent -q` 933 geçti. `python -m pytest queen-editor -q` yalnız
377'nin iki kırmızısı. Ön uçların ikisi yeşil. `git status` `.playwright-mcp/`'yi artık göstermiyor.

- [ ] **Step 6: Commit**

```powershell
git add .mcp.json .claude/settings.json .gitignore CLAUDE.md docs/superpowers/specs/2026-09-29-queenagent-m378-playwright-guvenli-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m378-playwright-guvenli-uygulama-plan.md
git commit -m @'
feat: Madde 378 -- Claude's browser reaches only this machine and its fonts, and runs no code outside itself

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```

- [ ] **Step 7: Kullanıcı Claude Code'u yeniden açınca, tarayıcıda**

- Bir internet adresine `browser_navigate` başarısız oluyor.
- `http://127.0.0.1:8100` açılıyor, ve ekran görüntüsünde başlık Newsreader'la çiziliyor.
- `browser_run_code_unsafe` reddediliyor.

Üçü görülünce 378 işaretlenir, ve Durum bir artar.
