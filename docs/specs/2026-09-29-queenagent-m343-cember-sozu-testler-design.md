# Madde 343 — Çemberin sözü, ve dolmanın önceden duyurusu · test turu

**Kaynak:** [yol haritasının 343'ü (v9-2i)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
kararları v9-1 ve v9-2'nin, tasarımı queen-design'ın `queen-agent-v3` dalında 146 ve 182 —
`DESIGN-STANDARD.md`'nin *The gauge* bölümü, `shell.js`'in `fullness` ve `gauge`'i, `kit.css`'in
`.composer__gauge` ve `.context-gauge__words`'ü.

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı, tasarım seçildi *(182: `note`)*.

## Ne kanıtlanacak

Bugün çemberin ipucu `82% of the context ceiling`, yuvarlanmış, ve çember hep yalnız durur. Olacak:

- **İpucu `This chat is N% full`**, çemberin `title`'ı ve `aria-label`'ı — fareyle üstüne gelen ve
  ekran okuyucu aynı cümleyi okur. Tavanda ve ötesinde `This chat is full`.
- **N aşağı yuvarlanır, en az 1, tavandan önce en çok 99** *(tasarım)*: sohbet dolmadan 100 demez,
  dörtte beşe gelmeden 80 demez. Tavanda ve ötesinde N 100, çember dolu.
- **Dörtte beşten, 40.000'den itibaren çemberin yanında `N% full`** (`context-gauge__words`), ekran
  okuyucudan gizli — o çemberin cümlesini zaten okur. Altında çember yalnız. Tavanda yazı yok: dolu
  sohbetin bildirimi v9-1c'nin.
- **Yazının görünüşü tasarımınki:** DM Mono (`--font-mono`), 11.5px, `#6b6259`; çemberden 6px uzakta
  (`.composer__gauge`'in `gap`'i).

Ölçü değişmez: çember sunucunun `context.sent`'ini ve `context.ceiling`'ini okur. Neyin sayıldığı
337'nin (v9-1a) işi.

## Dörtte beş nerede durur

FOUNDATION'ın 4. kararı: kurallar arka uçta, ekran bir görünüş. **Dörtte beş bir görünüş kararı, ve
ön uçta durur.** Nedeni:

- **Hiçbir şeyi durdurmaz, açmaz, kapamaz.** Sohbet 40.000'de de tur alır; eşik yalnız çemberin
  yanında bir yazının görünüp görünmeyeceğini söyler. FOUNDATION ön uçta kalanları sayarken tam bunu
  sayar: "what is shown".
- **Tavanın ikinci bir kopyası değil.** Eşik tavanın payı (0.8), ve tavanı sunucu sayıyla birlikte
  gönderiyor; tavan değişirse eşik onunla kayar. Sunucunun kuralı — sohbet dolu mu, tur alır mı —
  `chat.py`'nin `is_full`'unda kalır, ve dolu sohbetin bildirimi v9-1c'de onu sunucudan okur.
- **Aynı sebeple N'nin yuvarlanışı ve `This chat is full` cümlesi de görünüş:** paydan yazı yapmak
  biçimlendirme. Tavanda 100 demek `sent >= ceiling`'in aritmetiği; bir şeyi reddetmez.

## Testler ne tutar, ne tutmaz

**Tutar** — `queen-agent/frontend/src/features/workspace/ContextGauge.test.jsx`:

| # | Ne |
|---|---|
| 1 | 41.000 / 50.000'de ipucu `This chat is 82% full`, ve `aria-label` aynı cümle *(bugünkü `82% of the context ceiling` testi bununla değişir)* |
| 2 | Aşağı yuvarlanır: 49.990'da `This chat is 99% full` — yuvarlansa 100 derdi |
| 3 | En az 1: 100 / 50.000'de `This chat is 1% full` |
| 4 | Tavanın ötesinde, 60.000'de ipucu `This chat is full` *(bugünkü "dolu, taşkın değil" testine eklenir)* |
| 5 | 39.990'da yazı yok — yuvarlansa 80 olurdu, ve eşik dörtte beşten önce görünmez |
| 6 | 40.000'de çemberin yanında `80% full`, `aria-hidden="true"` |
| 7 | Tavanda, 50.000'de yanında yazı yok |

Bugünkü iki test yerinde kalır: 41.000'de `--filled` 0.82, `sent` 0 iken çember yok.

**Tutar** — `queen-agent/frontend/src/features/workspace/workspace.css.test.js`:

| # | Ne |
|---|---|
| 8 | `.context-gauge__words`: `font-family: var(--font-mono)`, `font-size: 11.5px`, `color: #6b6259` |
| 9 | `.composer__gauge`: `gap: 6px` |

**Tutmaz:** yazının ekranda gerçekten çemberin yanında durduğunu — jsdom CSS çalıştırmaz; o tarayıcıda
görülür. Sunucunun gönderdiğini — değişmiyor.

## Bu turda yazılmayanlar

- `ContextGauge.jsx` ve `workspace.css` değişmez; uygulama turunda.
- ChatScreen.jsx'e dokunulmaz: çember oradan aynı iki sayıyla beslenir.
- `dist` derlenmez: yöneten birleştirirken bir kez derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` yeni testlerde kırmızı
verir — 1, 2, 3, 4, 6, 8, 9; 5 ve 7 bugün de yeşil, çünkü bugün yazı hiç yok, ve uygulama turunda
yazıyı getiren kod onları bozmamalı. Arka uç süitleri değişmez: queen-agent yeşil, queen-editor
377'nin bilinen iki kırmızısıyla. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m343-cember-sozu-testler-plan.md).
