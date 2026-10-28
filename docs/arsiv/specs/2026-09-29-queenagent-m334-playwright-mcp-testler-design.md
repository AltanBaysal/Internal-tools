# Madde 334 — Playwright MCP bu depoda · test turu

**Kaynak:** [yol haritasının 334'ü (v9-3a)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
kararları aynı belgede, *v9-3 — Playwright MCP*.

**Kullanıcıdan gereken:** ayar yazılınca Claude Code'un yeniden açılması, ve projenin MCP sunucusunun
bir kez onaylanması. Test turu için hiçbir şey gerekmiyor.

## Ne kanıtlanacak

Claude QueenAgent'ı tarayıcıda kendisi açıp kullanabilsin diye Playwright MCP, queen-design'daki
gibi depo kökündeki `.mcp.json`'da tanımlanır: ayar depoda durur, sürüm sabittir, tarayıcı pencere
açmadan çalışır. Testler dosyanın bu kararları taşıdığını tutar. Sunucunun gerçekten bağlandığını
tutmazlar: o, Claude Code yeniden açılınca görülür, ve maddenin *bitti sayılır*ı odur.

## Cihazda bulunan

Maddenin kararı, kurulumun koşuda bulunmasıydı:

- Node `v24.19.0`, npx `11.17.0`.
- `@playwright/mcp` `0.0.82` npx'in önbelleğinde, Playwright'ın tarayıcıları
  `%LOCALAPPDATA%\ms-playwright`'ta. queen-design'ın sabitlediği sürüm bu; indirilecek bir şey yok.

## Testler ne tutar, ne tutmaz

**Tutar:**

- **Sürüm sabit.** Paket `@playwright/mcp@X.Y.Z` diye yazılır — `@latest` ya da sürümsüz değil. Her
  açılışta npm'deki o anki sürümü çekmek, paket bir gün ele geçirilirse o kodu çalıştırmak demek.
- **`--isolated`:** tarayıcının profili diske yazılmaz.
- **`--headless`:** pencere açılmaz; bu tarayıcı Claude'un gözü, kullanıcı kendi tarayıcısına bakıyor.
- **`--cdp-endpoint` yok:** olsaydı Claude kullanıcının açık tarayıcısına, ve onun giriş yapılmış
  bütün oturumlarına bağlanırdı.
- **`--allow-unrestricted-file-access` yok:** tarayıcıya makinenin bütün dosyalarını açardı.
  QueenAgent zaten `localhost`'tan servis ediliyor; `file://` gerekmiyor.

**Sürüm numarasının kendisini tutmaz.** Madde 209'daki gibi: değer bir karar, ve iki yere yazılırsa
sürüm elle yükseltilirken biri unutulur. Biçimi tutar, ve sürüm yükseltilince test değişmeden geçer.

## Nerede

`queen-agent/backend/tests/test_playwright_mcp.py`. `pytest queen-agent` testleri oradan toplar;
baktığı şey depo kökündeki dosya — `test_frontend_toolchain.py`'nin ön ucun `package.json`'ına
baktığı gibi. Madde QueenAgent'ın yol haritasında, o yüzden onun süitinde.

## Altı iddia

| # | Ne |
|---|---|
| 1 | Depo kökünde `.mcp.json` var, JSON olarak okunuyor, ve bir `playwright` sunucusu tanımlıyor |
| 2 | Sunucu `npx` ile açılıyor |
| 3 | Paket `@playwright/mcp@` artı `X.Y.Z` biçiminde bir sürüm |
| 4 | `--isolated` var |
| 5 | `--headless` var |
| 6 | `--cdp-endpoint` ve `--allow-unrestricted-file-access` yok |

Bugün dosya yok, o yüzden altısı da kırmızı: altıncısı da dosyayı okuyamadan düşer.

## Bu turda yazılmayanlar

- **`.mcp.json` açılmıyor**, uygulama turunda yazılır.
- **CLAUDE.md'nin notu** — sunucunun ne olduğu, bayrakların nedeni, sürümün nasıl yükseltileceği —
  uygulama turunda.
- **`dist` derlenmez:** ön uca dokunulmuyor.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-agent -q` altı kırmızı verir, öteki üç süit yeşil
kalır. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m334-playwright-mcp-testler-plan.md).
