# Madde 378 — Playwright MCP güvenli kullanılır · test turu

**Kaynak:** [yol haritasının 378'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); 334'ün ayarının
üstüne kurulur.

**Kullanıcıdan gereken:** ayar yazılınca Claude Code'un yeniden açılması — maddenin *bitti sayılır*ı
orada görülür. Test turu için hiçbir şey gerekmiyor.

## Ne kanıtlanacak

334'ün ayarı queen-design'ınkinin aynısı: sürüm sabit, `--isolated`, `--headless`, `--cdp-endpoint`
ve `--allow-unrestricted-file-access` yok. Kullanıcı tarayıcının güvenli kullanılmasını ve normal
internete karışmamasını istedi. queen-design'dan üç şey eksik ya da ikisinde de yok:

- **Tarayıcı her yere gidebiliyor.** Kurulu sürümde `--allowed-origins` var: listede olmayan her
  adrese giden isteği tarayıcıda keser. Liste bu makinedeki araçlar — `http://127.0.0.1:*`, her
  port — ve Google Fonts'un iki adresi: iki aracın `index.html`'i fontlarını oradan çekiyor, ve
  fontsuz ekran yedek fontla çıkar *(kullanıcı, 29 Eylül — "izin verilsin")*.
- **`browser_run_code_unsafe` açık.** Kodu tarayıcıda değil, MCP sunucusunun Node sürecinde
  çalıştırır: diske de internete de oradan ulaşılır, ve yukarıdaki liste onu durdurmaz. queen-design
  onu CLAUDE.md'sinde yasaklıyor; burada `.claude/settings.json`'ın `deny`'ı yasaklar — yazı
  unutulur, ayar unutulmaz.
- **`.playwright-mcp/` git'e girebilir.** Tarayıcının ekran görüntüleri ve sayfa dökümleri oraya
  yazılıyor, ve bugün `git status`'ta görünüyor. queen-design onu `.gitignore`'da tutuyor.

**Liste bir duvar değil:** paketin kendi belgesi `--allowed-origins`'in güvenlik sınırı olmadığını ve
yönlendirmeleri yakalamadığını söylüyor. Bizim araçlar başka bir adrese yönlendirmiyor. Bu yüzden
kural — tarayıcıda internet adresi açılmaz — CLAUDE.md'de de yazılır, uygulama turunda.

## Testler ne tutar, ne tutmaz

**Tutar** — `queen-agent/backend/tests/test_playwright_mcp.py`'ye dört iddia:

| # | Ne |
|---|---|
| 7 | `--allowed-origins` verilmiş, ve listedeki her adres ya `http://127.0.0.1` (portlu ya da `:*`) ya da Google Fonts'un iki adresinden biri |
| 8 | Listede bu makinenin bir adresi ve Google Fonts'un iki adresi var — araçlar ve fontları açılabiliyor |
| 9 | Depo kökündeki `.claude/settings.json` `mcp__playwright__browser_run_code_unsafe`'i `permissions.deny`'da tutuyor |
| 10 | Depo kökündeki `.gitignore`'da `.playwright-mcp/` satırı var |

**Listenin değerini tutmaz, biçimini tutar**, dosyanın öteki testleri gibi: yeni bir yerel port
eklemek testi değiştirmez, ama internetten bir adres eklemek 7'yi kırmızı yapar — o adres kullanıcıyla
konuşulacak bir karar.

**Tarayıcının gerçekten neyi açıp neyi açamadığını tutmaz:** o, Claude Code yeniden açılınca
tarayıcıda görülür.

Dosyanın açıklaması artık yalnız `.mcp.json`'a bakmadığını söyler.

## Bu turda yazılmayanlar

- **`.mcp.json`, `.claude/settings.json` ve `.gitignore` değişmez**; uygulama turunda.
- **CLAUDE.md'nin notu** uygulama turunda.
- **`dist` derlenmez:** ön uca dokunulmuyor.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-agent -q` dört kırmızı verir — 9, dosya olmadığı
için okuyamadan düşer. queen-editor'ün arka ucu 377'nin bilinen iki kırmızısıyla kalır; öteki iki süit
yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m378-playwright-guvenli-testler-plan.md).
