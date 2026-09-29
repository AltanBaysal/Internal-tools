# Madde 342 — Açık dosyanın başlığı · uygulama turu

**Kaynak:** [yol haritasının 342'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2h);
[test turunun spec'i](2026-09-29-queenagent-m342-dosya-basligi-testler-design.md), ve onun
`bbc8ab1b`'de commit'lenen kırmızı testleri. Tasarım: `reader/` sayfası, `shell.js`'in `readerHead`'i,
`kit.css`'in `.reader__*`, `.back.back--inline` ve `.ghost` kuralları.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

Yalnız QueenAgent'ın ön ucu, `features/workspace/` içinde. Yeni dosya yok, dosya silinmiyor —
CODE-STANDARD'ın tabloları değişmez.

**`FilePanel.jsx`** — başlık tasarımın `readerHead`'inin şekli:

```
header.reader__head
  div.reader__bar
    button.back.back--inline  "←"      (rayda)   |  button.reader__close "×"  (proje ekranında)
    div.reader__tools
      button.ghost.reader__refresh  "Refresh"
      button.ghost.reader__copy     "Copy" | "Copied" | "Could not copy"
  span.reader__name
```

- `CopyButton`'ın sözü düğmenin yazısı olur; `aria-label` ve `title` gider, çünkü ad artık yazının
  kendisi. `data-said` ve `disabled` kalır. 2,5 saniyelik dönüş bugünkü gibi.
- Download ve onun hâlleri gider: `onDownload`, `preparing`, `failed`, ve `failed`'in
  `reader__error` satırı. Okumanın `error` satırı kalır.
- Proje ekranının `×`'i `←`'nün yerinde, çubuğun sol ucunda. O ekran 353'te (v9-2n) kalkınca `×` ve
  `.reader__close` onunla gider.
- Download'ı anan yorumlar gerçeğe göre düzelir.

**`useFile.js`** — `save` ve `download` gider; hook `{ name, file, missing, error, open, close,
reload }` verir.

**`FileRail.jsx`, `ProjectScreen.jsx`** — `onDownload={reading.download}` satırı gider.

**Sunucu değişmez:** `GET /api/projects/<id>/files/<name>`'i açma ve yenileme de okuyor.

**`workspace.css`**

- `.back--inline` → `.back.back--inline { margin-bottom: 0; }` (APP-BUGS 48; iki sınıf `.back`'i
  kaynak sırasından bağımsız yener). Sohbet başlığındaki `← proje` de böylece ortada durur; 347 o oku
  kaldırıyor.
- `.reader__head`: sütun, `gap: 10px`, `padding: 18px 28px`, `border-bottom: 1px solid var(--line)`.
- `.reader__bar` (`space-between`, ortada, `gap: 8px`) ve `.reader__tools` (`gap: 8px`) yeni.
- `.reader__bar > .back`: `ghost`'un çerçevesi — `1px solid var(--line)`, `--surface`,
  `--radius-control`, `5px 11px`. Rengi, yazısı ve üstüne gelinceki mürekkebi `.back`'in kalır.
  Çerçeve yalnız burada: `.back--inline` sohbet başlığında da var, ve o başlık bu maddenin değil.
- `.reader__bar > button, .reader__tools > button { flex: none; line-height: 20px; }` — üç düğme
  aynı boyda (`←`'nün 12px oku ile 12,5px yazılar aynı satır yüksekliğinde).
- `.reader__name`: `flex: 1` gider — sütunda dikey büyütürdü. Tasarımdaki gibi `ellipsis` kalır.
- `.reader__download` gider.
- `.file-list__refresh, .reader__refresh, .reader__copy` ortak kuralı ve `:hover`'ı yalnız
  `.file-list__refresh`'e kalır (350 onu sonra taşıyor). Okuyucunun iki düğmesi `.ghost`'un
  çerçevesini ve kenar koyulaşmasını alır.
- `.reader__copy { min-width: 116px; }` — `Could not copy` `Copy`'nin yerini alınca başlık kaymaz.
  `:disabled` ve `[data-said]` kuralları kalır, yorumdaki "icon" "button" olur.

## Karar: `.reader__close`

Tasarımda `×` yok (proje ekranı tasarımda kalktı). Uygulamada ekran 353'e kadar duruyor, o yüzden
`×` ölmüş kod değil. Çubukta sol uçta durmak ek kural istemiyor; sağ uçta durması `reader__tools`'a
ya da ayrı bir hizaya kural ekletirdi.

## Nasıl görülür

Dört satır yeşil: QueenAgent ön ucu `bbc8ab1b`'deki 662 testin hepsi, arka ucu 933, queen-editor ön
ucu 749, arka ucu 1158 + 377'nin iki kırmızısı.

Tarayıcıda: bir sohbette sağ panelden bir dosya açılınca üst satırda solda çerçeveli `←`, sağda
`Refresh` ve `Copy`, üçü aynı boyda ve `←` satırın ortasında; altında ad, altında ince çizgi;
Download yok. `Copy`'ye basınca `Copied`, 2,5 saniye sonra `Copy`.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m342-dosya-basligi-uygulama-plan.md).
