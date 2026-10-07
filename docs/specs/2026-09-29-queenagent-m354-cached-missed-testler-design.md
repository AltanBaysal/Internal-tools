# Madde 354 — Cevabın altında cached ve missed · test turu

**Kaynak:** [yol haritasının 354'ü (v9-2k)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
kararları v9-2'nin, ve v9-10'un *29 Eylül — tasarımdan* notu. Kullanıcının sözü *(backlog'dan, 29
Eylül)*: "abi token gösteriyoruz ya her chatin altında 2 tane gösterlim bir yeşil bir kırmızı yeşil
chached kırmızı missed cahced". Tasarımı queen-design'ın `queen-agent-v3` dalında 189 ve 192 —
`DESIGN-STANDARD.md`'nin *The notes under a message* bölümü ve *Colour* tablosu, `shell.js`'in `stamp`'i,
`kit.css`'in `.msg__stamp-cached` ve `.msg__stamp-missed`'i.

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı; tasarım satırı, renkleri ve sıfır hâlini
söylüyor.

## Ne kanıtlanacak

Bugün biten cevabın altında `11:05 · 13.2k tokens` yazıyor: `sent + answered`, yani önbellekten gelen
tam fiyat ödenmiş gibi *(v9-10'un ilk bulgusu)*. Olacak:

- **Biten cevabın satırı:** saat, sonra önbellekten gelen ve gelmeyen: `09:38 · 49.2k cached · 12.1k
  missed`. `cached` sunucunun `usage.cached`'ı; `missed` `sent`'in geri kalanı, `sent - cached`
  *(`chat.py`'nin `Usage`'ı: `cached` `sent`'in bir parçası)*. Sayıların kısaltması bugünkü gibi
  (`shorten`): binin altı olduğu gibi, üstü `12.1k`.
- **Renk sözle birlikte:** `cached` kendi `span`'ında, `msg__stamp-cached` — yeşil `#536747`;
  `missed` kendi `span`'ında, `msg__stamp-missed` — kırmızı `var(--destructive)`. İkisi de sözlerin
  `span`'ının içinde, yani satırın ilk çocuğu yine sözler *(348'in kuralı yerinde)*.
- **Modelin yazdığı gösterilmez:** `answered` satırda hiçbir biçimde yok; `tokens` kelimesi de biten
  cevapta yok.
- **Sayısı olmayan eski cevapta yalnız saat:** `sent` sıfırsa satır yalnız saat *(tasarım: "`sent` at
  zero, the row keeps only the time")*.
- **Önbellekten hiç gelmeyen de, hepsi gelen de iki sayıyı birden söyler:** `0 cached · 300 missed`,
  `3.1k cached · 0 missed` — tasarımın `stamp`'i ikisini hep birlikte çizer.
- **Süren cevapta tek sayı kalır:** `round 2/16 · 12.3k tokens ·` değişmez *(v9-10: "Süren cevabın
  sayısı burada kalır")*. Bugünkü canlı satır testleri bunu zaten tutuyor; yeni test yok.

**Mimari kararı:** `missed`'i ekran hesaplar, sunucu dördüncü bir alan göndermez. `Usage`'ın belgesi
bunu açıkça seçmiş — iki sayının farkını tutan alan kendi kendine eskir —, ve çıkarma bir kural değil,
iki sayının nasıl gösterileceği *(FOUNDATION, Karar 4: biçim ekranda kalır)*. Arka uç değişmez; yalnız
`routes.py`'deki "the screen draws one number out of it" yorumu uygulama turunda düzelir.

## Testler ne tutar, ne tutmaz

**Tutar** — `queen-agent/frontend/src/features/workspace/Stamp.test.jsx`:

| # | Ne |
|---|---|
| 1 | `usage={{ sent: 61240, cached: 49152, answered: 684 }}`: sözlerin `span`'ı `${clockTime(AT)} · 49.2k cached · 12.1k missed` *(bugünkü "says when and what it spent" testinin yerine)* |
| 2 | Aynı cevapta `.msg__stamp-cached` `49.2k cached`, `.msg__stamp-missed` `12.1k missed`, ve ikisi de sözlerin `span`'ının içinde |
| 3 | Aynı cevapta satırda `684` ve `tokens` yok |
| 4 | `sent: 3072, cached: 3072`: `3.1k cached · 0 missed` |
| 5 | `sent: 0` bütün alanlar sıfırken satır yalnız saat *(bugünkü test yerinde kalır)* |

**Tutar** — `ChatScreen.test.jsx`, Madde 68'in bölümü:

| # | Ne |
|---|---|
| 6 | `{ sent: 12400, cached: 9100, answered: 842 }`: cevabın satırının sözleri `11:05 · 9.1k cached · 3.3k missed` |
| 7 | `{ sent: 300, cached: 0, answered: 42 }`: `11:05 · 0 cached · 300 missed` |
| 8 | Ölçülmemiş cevapta yalnız `11:05`; ekranda `cached` ve `missed` yok |
| 9 | Kullanıcının mesajında `cached` ve `missed` yok |

**Tutar** — `App.test.jsx`:

| # | Ne |
|---|---|
| 10 | Tur bitince, `{ sent: 9000, cached: 3000, answered: 100 }`'ün cevabının altında `3.0k cached` ve `6.0k missed` *(bugünkü `9.1k tokens` yerine)* |

**Tutar** — `workspace.css.test.js`:

| # | Ne |
|---|---|
| 11 | `.msg__stamp-cached`: `color: #536747`; `.msg__stamp-missed`: `color: var(--destructive)` |

**Tutmaz:** rengin ekranda gerçekten yeşil ve kırmızı göründüğünü — jsdom CSS çalıştırmaz; tarayıcıda
görülür. Arka uç: `usage` bugün de üç alanıyla gidiyor, değişmez.

## Bu turda yazılmayanlar

- `Stamp.jsx`, `workspace.css` ve `routes.py`'nin yorumu değişmez; uygulama turunda.
- `dist` derlenmez: yöneten birleştirirken bir kez derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` 1–4, 6–11'de kırmızı
verir. 5, 8 ve 9 bugün de yeşil: üçü de bir yokluğu tutar, ve yeni satır o yokluğu bozmamalı.
Arka uçlar ve queen-editor'ün ön ucu yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m354-cached-missed-testler-plan.md).
