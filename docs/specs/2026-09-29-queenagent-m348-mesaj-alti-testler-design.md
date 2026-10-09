# Madde 348 — Mesajın altındaki notlar tek satırda · test turu

**Kaynak:** [yol haritasının 348'i (v9-2e)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
kararları v9-2'nin — listenin (4)'ü, kullanıcının sözü: "kalem ile saat alt alta duruyor … tasarım
düzeltecek". Tasarımı queen-design'ın `queen-agent-v3` dalında 139 (179'da `line` seçildi) —
`DESIGN-STANDARD.md`'nin *The notes under a message* bölümü, `shell.js`'in `stamp`'i ve `liveStrip`'i,
`kit.css`'in `.msg__stamp`'i.

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı, tasarım tek düzene indi *(179: `line`)*.

## Ne kanıtlanacak

Bugün kullanıcının mesajının altında iki satır var: önce `‹ 1/2 ›` ile ✎ (`.msg__foot`), altında saat
(`.msg__stamp`). Süren cevabın satırı `round 4/16 · 12.3k tokens · ◌ Pondering…` diye başlar, saatsiz.
Olacak:

- **Her mesajın notları tek satır, `msg__stamp`:** önce sözleri — saat, cevapta ardından harcadığı —
  kendi `span`'ında; sorunun altında ardından, iki ya da daha çok sürüm varsa `versions`, sonra ✎.
  Ayrı `.msg__foot` satırı kalkar.
- **Soru düzeltilirken** satırda saat ve sürümler; ✎ yok *(197'nin kuralı yerinde)*.
- **Cevabın satırında** sürüm oku da ✎ de yok: saat, ve ölçülmüşse harcadığı. Sayının biçimi bugünkü
  gibi kalır — `cached` / `missed` ayrımı v9-2k'nin.
- **Süren cevabın satırı saatle başlar:** beklemenin başladığı saat, sonra `round 4/16 · 12.3k tokens ·`,
  spinner ve kelime. Saat bekleme damgalanmadan önceki ilk çizimde yoksa satır bugünkü gibi `round`'la
  başlar *(tasarımın `liveStrip`'i de öyle)*.
- **Satırın görünüşü tasarımınki:** `.msg__stamp` flex bir satır, `align-items: center`, parçaları 6px
  arayla *(canlı satır bugünkü gibi 7px)*.

## Testler ne tutar, ne tutmaz

**Tutar** — `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx`:

| # | Ne |
|---|---|
| 1 | Düzenlenmiş soru (`BRANCHED`): sorunun `.msg__stamp`'inin çocukları sırayla saatin `span`'ı (`11:04`), `.versions` (`‹2/2›`), `.msg__edit`; ekranda `.msg__foot` yok *(yeni — maddenin "bitti sayılır"ı)* |
| 2 | Sürümsüz soru: satırda saat ve ✎, `.versions` yok *(bugünkü "keeps its pencil" testi `.msg__stamp`'e taşınır)* |
| 3 | Cevabın satırında `.versions` ve `.msg__edit` yok *(bugünkü "no line under it" testi değişir)* |
| 4 | Düzeltilirken satırda saat ve `.versions`, `.msg__edit` yok *(bugünkü testi `.msg__stamp`'e taşınır)* |
| 5 | Ok ve kalem aynı satırda, ok kalemden önce *(bugünkü iki 199 testi `.msg__stamp`'e taşınır)* |
| 6 | Saat 14:32'de başlayan beklemede süren satır `14:32 · round 4/16 · 12.3k tokens · …ing…` *(bugünkü "a word that says nothing" testinin kalıbı saatle başlar)*; yazı gelmeye başlayınca da (`streaming`) satır `14:32 · round 4/16` diye başlar *(yeni)* |
| 7 | `getByText("11:04")`, `"11:05"`, `"14:32"`, `"11:05 · 13.2k tokens"`, `"11:05 · 342 tokens"` gibi sözü bulan testlerde sözün kendi `span`'ı: bulunanın `parentElement`'i `msg__stamp` *(yedi bugünkü test)* |

**Tutar** — `Stamp.test.jsx`:

| # | Ne |
|---|---|
| 8 | `Stamp`'e verilen parçalar sözlerden sonra gelir: çocukları `span` (saat), ardından verilen |
| 9 | `LiveStrip`'e `at` verilince satır `${clockTime(AT)} · round 2/16 · 1.2k tokens` diye başlar; `at` yoksa `round 2/16` diye |

**Tutar** — `MessageFoot.test.jsx`:

| # | Ne |
|---|---|
| 10 | `MessageFoot` kendi satırını çizmez: sürüm ve kalem verilince çizdiği ilk öğe `.versions`, ikincisi `.msg__edit` — ikisi de satırın (`Stamp`'in) doğrudan çocuğu olacak |

**Tutar** — `workspace.css.test.js`:

| # | Ne |
|---|---|
| 11 | `.msg__stamp`: `display: flex`, `align-items: center`, `gap: 6px`; stil dosyasında `.msg__foot` yok *(bugünkü "share one row" testi değişir)* |

**Tutmaz:** satırın ekranda gerçekten tek satır durduğunu — jsdom CSS çalıştırmaz; tarayıcıda
görülür. `App.test.jsx`'in canlı satır testleri `toContain` ile okur, değişmez.

## Bu turda yazılmayanlar

- `Stamp.jsx`, `MessageFoot.jsx`, `ChatScreen.jsx` ve `workspace.css` değişmez; uygulama turunda.
- `dist` derlenmez: yöneten birleştirirken bir kez derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` yeni ve taşınan testlerde
kırmızı verir; 2'nin, 3'ün ve 4'ün "yok" diyen parçaları bugün de doğru olabilir ama her testin
`.msg__stamp` içinden okuduğu bir "var"ı bugün yok. Arka uçlar ve queen-editor'ün ön ucu değişmez,
yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m348-mesaj-alti-testler-plan.md).
