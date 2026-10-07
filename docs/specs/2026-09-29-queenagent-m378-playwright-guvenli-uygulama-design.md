# Madde 378 — Playwright MCP güvenli kullanılır · uygulama turu

**Kaynak:** [yol haritasının 378'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m378-playwright-guvenli-testler-design.md); kırmızı
`93f69936`.

## Ne yazılır

**`.mcp.json`'a bir bayrak**, değeriyle:

```json
"args": [
  "@playwright/mcp@0.0.82", "--isolated", "--headless",
  "--allowed-origins", "http://127.0.0.1:*;https://fonts.googleapis.com;https://fonts.gstatic.com"
]
```

- **`http://127.0.0.1:*`**, tek tek portlar değil. Paket `:*`'ı her port diye okuyor
  *(`originOrHostGlob`)*. QueenAgent 8100'de, queen-editor 8000'de dinliyor, ve ikisi de
  `127.0.0.1`'e bağlanıyor *(iki aracın `config.py`'si)*. Yeni bir yerel port ayar istemez.
- **`localhost` yazılmaz:** iki araç da `127.0.0.1`'de açılıyor. `localhost` bir gün gerekirse o gün
  eklenir; test onu zaten kabul etmez, ve eklenmesi bir karar olur.
- **Paketin kodunda gördüğüm:** liste verilince tarayıcının bütün istekleri önce kesilir, sonra her
  adres için yalnız o adresin istekleri geçirilir.

**Depo kökünde yeni bir `.claude/settings.json`:**

```json
{
  "permissions": {
    "deny": ["mcp__playwright__browser_run_code_unsafe"]
  }
}
```

Depoya girer: `settings.local.json` kullanıcının genel git ayarında yok sayılıyor, ve yasak bu
bilgisayara değil depoya ait. Subagent'lar da aynı ayarı okur.

**`.gitignore`'a queen-design'daki satır**, onun açıklamasıyla:

```
# What Playwright MCP writes as it looks: snapshots, console logs, screenshots.
.playwright-mcp/
```

**CLAUDE.md'nin Playwright paragrafına yalnız kodun söyleyemediği** *(Style — "a doc says what the
code cannot")*:

- **Tarayıcıda internet adresi açılmaz**, yalnız bu makinede çalışan araçlar. Listenin kendisi kural
  değil, çünkü paket onun güvenlik sınırı olmadığını ve yönlendirmeleri yakalamadığını söylüyor.
  Listede olmayan bir adres kullanıcının kararı.
- **`browser_run_code_unsafe` yasak**, ve `.claude/settings.json` onu reddediyor. Sayfanın içinde kod
  gerekince `browser_evaluate` kullanılır.
- **Ekran görüntüsüne dosya adı verilmez:** adsız çıktı `.playwright-mcp/`'ye yazılıyor ve git onu
  görmüyor. Adlı çıktı ise deponun köküne yazılıyor *(`--output-dir`'in açıklaması)*, ve `git status`'a
  düşüyor.

Bayrakların nedeni yine test dosyasında kalır; paragraf onu adıyla anmaya devam eder.

## Yazılmayanlar

- **`--block-service-workers`:** bir service worker'ın istekleri listeye takılmaz. Ama ne iki araç ne
  Google Fonts service worker kuruyor; olmayan bir duruma karşı bir bayrak daha olurdu.
- **Tarayıcıyı ağsız bir container'da koşmak:** tam kapalı bir kum havuzu olurdu, ama kullanıcıya
  sorulmadı, ve bir bilgisayar kurulumu gerektirir.
- **`dist` derlenmez:** ön uca dokunulmuyor.

## Nasıl görülür

CLAUDE.md'deki dört satır: `python -m pytest queen-agent -q` yeşile döner, 933 test. queen-editor'ün
arka ucunda yalnız 377'nin iki kırmızısı kalır.

**Maddenin bitti sayılırı testte değil:** kullanıcı Claude Code'u yeniden açınca Claude tarayıcıda
dener:
- bir internet adresi açılmıyor;
- yerel QueenAgent Google fontlarıyla açılıyor;
- `browser_run_code_unsafe` reddediliyor;
- `git status` `.playwright-mcp/`'yi göstermiyor.

Madde ancak o zaman işaretlenir.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m378-playwright-guvenli-uygulama-plan.md).
