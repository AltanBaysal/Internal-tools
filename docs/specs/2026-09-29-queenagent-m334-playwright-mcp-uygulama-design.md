# Madde 334 — Playwright MCP bu depoda · uygulama turu

**Kaynak:** [yol haritasının 334'ü (v9-3a)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m334-playwright-mcp-testler-design.md); kırmızı
`3c643337`.

## Ne yazılır

**Depo kökünde `.mcp.json`**, queen-design'ınkiyle aynı:

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

- **Sürüm `0.0.82`:** queen-design'ın sabitlediği, ve bu cihazın npx önbelleğinde duran sürüm;
  indirilecek bir şey yok.
- **Tarayıcı seçilmez:** paketin varsayılanı cihazda kurulu *(`%LOCALAPPDATA%\ms-playwright`)*.

**CLAUDE.md'nin `Commands` bölümüne bir paragraf:** sunucunun ne olduğu, ilk açılışta bir kez
onaylandığı, ve sürümün elle yükseltildiği. Bayrakların nedeni yazılmaz, dosyanın adı verilir:
nedenleri, onları tutan `test_playwright_mcp.py` zaten söylüyor, ve iki yerde yazılan neden birinde
eskir *(CLAUDE.md, Style — "a doc never restates what the code already states")*.

## Yazılmayanlar

- **Yerel QueenAgent'ın nasıl açılacağı:** v9-3b'nin işi.
- **`--browser msedge` gibi bir yedek:** tarayıcı kurulu, ve açılmayan bir tarayıcı görülmedi.
- **İzin ayarı:** Claude Code proje sunucusunu ilk açılışta kendisi sorar; kullanıcının yerel
  ayarına yazılmaz.

## Nasıl görülür

CLAUDE.md'deki dört satır: `python -m pytest queen-agent -q` yeşile döner — 929 test. queen-editor'ün
arka ucundaki tek kırmızı bu maddeden önce vardı ve bu maddenin değil *(v9 roadmap'inin MiniMax
bağlantıları, `d9c2d6f5`)*; ayrı bir madde olarak kullanıcıya soruluyor.

**Maddenin bitti sayılırı testte değil:** Claude Code yeniden açılınca Playwright araçları görünür,
ve Claude bir sayfayı açıp ekran görüntüsünü alır. Kullanıcı yeniden açtıktan sonra Claude bunu
dener, ve madde ancak o zaman işaretlenir.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m334-playwright-mcp-uygulama-plan.md).
