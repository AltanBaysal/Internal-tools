# Madde 342 — Açık dosyanın başlığı · test turu

**Kaynak:** [yol haritasının 342'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2h);
tasarım: `queen-agent-v3` dalının 154, 155, 176 ve 186'sı, ve `projects/queen-agent/APP-BUGS.md`'nin
48'i. Başlığın çizimi tasarımın `reader/` sayfası, `shell.js`'in `readerHead`'i ve `kit.css`'in
`.reader__*` kuralları.

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı, tasarım okunmuş.

## Ne kanıtlanacak

Bugün açık dosyanın başlığı tek satır: `← ad ↻ ⧉ Download`, ve proje ekranında `←` yerine sonda `×`.
`←` çerçevesiz, `↻` ile `⧉` simge, ad satırın ortasında sıkışıp kesiliyor, ve `.back--inline`'ın
`margin-bottom: 0`'ı `.back`'in `18`'ine kaynak sırasıyla kaybediyor — ok satırın ortasının `9`
üstünde (APP-BUGS 48).

Olacak, tasarımdaki gibi:

- **Başlık iki satır.** Üstte `reader__bar`: solda `←` (`back back--inline`), sağda kendi öbeği
  `reader__tools` içinde yazılı `Refresh` ve `Copy` (`ghost`). Altında kendi satırında
  `reader__name`, çubuğun dışında. Başlığın altında `--line` çizgisi.
- **Üçü aynı boyda:** `←` da `ghost` gibi çerçeveli (`1px solid var(--line)`, `--surface`,
  `--radius-control`, `5px 11px`), ve çubuktaki düğmelerin satır yüksekliği `20px`.
- **Download kalkar**, onunla yalnız onun kullandığı her şey: `FilePanel`'in bekleme ve hata hâli,
  `useFile`'ın `download`'ı ve `save`'i, `.reader__download` kuralı.
- **`Copy` yazıyla cevap verir:** basınca düğmenin kendi yazısı `Copied` ya da `Could not copy`,
  2,5 saniye sonra yine `Copy`. Başka satır eklenmez.
- **`←` satırın ortasında:** kural `.back.back--inline` olur, iki sınıfla `.back`'i yener.

**Proje ekranının paneli** (`back` verilmeyen `FilePanel`) 353'te (v9-2n) ekranla birlikte kalkıyor;
tasarımda onun `×`'i yok. O güne kadar `×` çubukta `←`'nün yerinde durur: aynı satır, aynı iki uç,
ek kural yok. Test yalnız `×`'in çubukta olduğunu tutar.

## Testler ne tutar

**`FilePanel.test.jsx`**

| # | Ne |
|---|---|
| 1 | Başlıkta `Download` adlı düğme yok |
| 2 | Çubukta ilk düğme `←`; `reader__tools` içinde sırayla `Refresh`, `Copy` |
| 3 | `Refresh` ve `Copy` yazılı ve `ghost` sınıflı |
| 4 | `reader__head`'in ilk çocuğu `reader__bar`, sonuncusu ad — çubuğun dışında, kendi satırında |
| 5 | `Copy` basılınca düğmenin yazısı `Copied`; sayfada o kelime tek yerde |
| 6 | Kopyalanamazsa yazısı `Could not copy` |
| 7 | 2,5 saniye sonra yine `Copy` (sahte saat) |
| 8 | Proje ekranının `×`'i çubukta |

Download'ın dört testi (`Download asks for the file`, `preparing is said in words, not spun`,
`while it downloads…`, `a download that fails…`) silinir; "the answer is the icon's own name…"
testi 5'e dönüşür — eskisi kelimenin ekranda *olmamasını* istiyordu, yenisi düğmenin yazısında
olmasını.

**`useFile.test.jsx`**

| # | Ne |
|---|---|
| 9 | `useFile` bir `download` vermiyor |

Kaydetmenin iki testi ve nesne URL'lerinin sahtesi silinir.

**`FileRail.test.jsx`**

| # | Ne |
|---|---|
| 10 | Dosya okunurken rayda `Download` yok |

**`workspace.css.test.js`**

| # | Ne |
|---|---|
| 11 | `.reader__head` sütun, altında `1px solid var(--line)` |
| 12 | `.reader__bar` `space-between`, `align-items: center` |
| 13 | `.back.back--inline` `margin-bottom: 0`; tek sınıflı `.back--inline` kuralı yok |
| 14 | `.reader__bar > .back` `ghost`'un çerçevesini taşıyor |
| 15 | `.reader__bar > button` ve `.reader__tools > button` `line-height: 20px` |
| 16 | `.reader__copy` en az `116px`; `.reader__download` kuralı yok |
| 17 | `.reader__refresh` ya da `.reader__copy` seçen hiçbir kural çerçeveyi ya da zemini (`border: none`, `background: transparent`) almıyor, ve ikisinin kendi `:hover`'ı yok — üstüne gelince `ghost`'unki gibi kenar koyulaşır |

**Çerçeve neden yalnız okuyucunun `←`'sünde:** tasarım çerçeveyi `.back.back--inline`'a yazıyor, ama
uygulamada o sınıf sohbet başlığının `← proje`'sinde de var, ve o ok 347'de (v9-2d) kalkıyor.
Çerçeve oraya da gelseydi bu madde başka bir başlığın görünüşünü değiştirirdi. APP-BUGS 48'in iki
yeri de düzelir — kural iki sınıflı olur —, çerçeve okuyucunun çubuğunda kalır.

## Tutmaz

- **Tarayıcıda görünüş:** jsdom stil hesaplamaz; 11–17 stil dosyasının kilidi. Ölçüye göz Claude'un
  tarayıcısında atılır.
- **Adın kesilmemesi** yapıyla tutulur (4): ad düğmelerle aynı satırda yer için yarışmıyor. Tasarım
  `.reader__name`'de `ellipsis`'i bırakıyor — dar yan panele sığmayan çok uzun bir ad yine kesilir,
  tasarımdaki gibi.
- **Sunucu:** Download'ın okuduğu `GET …/files/<name>` dosyayı açarken ve yenilerken de okunuyor;
  değişmez.

## Bu turda yazılmayanlar

Kod, stil dosyası ve `dist` değişmez; uygulama turunda (`dist`'i koordinatör derler).

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend`'de yeni testler kırmızı;
QueenAgent'ın arka ucu ve queen-editor'ün ön ucu yeşil, queen-editor'ün arka ucu 377'nin bilinen iki
kırmızısıyla. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m342-dosya-basligi-testler-plan.md).
