# Madde 356 — Açık dosya da çekilerek genişler · test turu

**Kaynak:** [yol haritasının 356'sı](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2o);
kararları v9-2'nin; tasarım: `queen-agent-v3`'ün 158'i ve 177'si. 342'nin (açık dosyanın başlığı) ve
350'nin (`rail__bar`) üstüne kurulur.

**Kullanıcıdan gereken:** hiçbir şey. Görünüş ve davranış tasarımda yazılı, madde hizalandı.

## Ne kanıtlanacak

Bugün sohbetin yanındaki panelin iki hâli iki ayrı genişlikte. Liste `320`'yle başlıyor, sol
kenarındaki tutma yerinden (`rail__grip`, Madde 50) çekilince `220`–`560` arasında kalıyor; `220`'nin
altına çekilince katlanıyor. Genişliği App tutuyor (`railWidth`, `resizeRail`). Dosya açılınca panel
`rail--open` oluyor, stylesheet onu her zaman `560`'ta çiziyor, ve tutma yeri yok
(`FileRail.jsx`'in `railStyle`'ı okurken genişlik yazmıyor).

Tasarımın 158'i ikisini tek genişlik yapıyor: dosya listenin tuttuğu genişlikte açılır — hiç
çekilmediyse `320`'de —, açık dosyanın sol kenarı da çekilir, ve çekilen genişlik dosya kapanınca
listede kalır. 177'si tutma yerini dosyanın metninin üstünde tutar: `.reader`'ın `fadeIn`'i onu
tutma yerinin üstüne çıkarıyordu, tasarım `z-index: 1` koydu.

Tasarımın biçimi (`DESIGN-STANDARD.md`, *File rail*; `BEHAVIOUR.md`, *The open file*; `kit.css`):

- **Okurken panel tutulan genişlikte**, katlı olsun olmasın: `220`'nin altına çekilince panel
  katlanır, ama katlılık dosya kapanınca görünür. App'in kuralı (`railWidthFor`, `resizeRail`)
  değişmez: aynı kural iki tutma yerine cevap verir.
- **Tutma yeri okurken de**, `.reader`'ın yanında, aynı `role="separator"`.
- **`.rail--open`'ın kendi genişliği yok**: hiç çekilmemişken `.rail`'in `320`'si geçer. Tasarımın
  `kit.css`'i `320`'yi `.rail--open`'da bir daha yazıyor; burada yazılmaz, çünkü `.rail`'in `320`'si
  zaten bir kilit testiyle `DEFAULT_RAIL_WIDTH`'e bağlı, ve üçüncü bir kopya o kilidin dışında
  kalırdı.
- **`.rail__grip`'te `z-index: 1`.**
- **Proje ekranının dosya paneli `560`'ta kalır**: yanında liste yok (158).

**Karar — okurken çekerken de `rail--dragging`.** Tasarımın `railClass`'ı okurken yalnız
`rail rail--open` döndürüyor, yani kenar çekilirken genişlik `220ms` geriden gelir. Ama tasarımın
kendi kuralı — `kit.css`'te `.rail--dragging`'in yorumu — "a rail following the pointer has to arrive
with it". Kurala uyulur: okurken çekerken de sınıf `rail rail--open rail--dragging`. Sayfada fark
yalnız çekerken görülen gecikme.

## Testler ne tutar

| # | Dosya | Ne |
|---|---|---|
| 1 | `FileRail.test.jsx` | Okurken panel verilen genişlikte çizilir (`style.width`) |
| 2 | `FileRail.test.jsx` | Okurken, liste katlı olsa da, panel tutulan genişlikte |
| 3 | `FileRail.test.jsx` | Okurken de tutma yeri var (bugünkü *a rail showing a document has no grip* bununla yer değiştirir) |
| 4 | `FileRail.test.jsx` | Okurken tutma yerini sola çekmek daha geniş bir panel ister — listeninkiyle aynı hesap |
| 5 | `FileRail.test.jsx` | Okurken kenar çekilirken panel `rail--open` ve `rail--dragging`, bırakınca yalnız `rail--open` |
| 6 | `App.test.jsx` | Liste `400`'e çekilince dosya `400`'de açılır |
| 7 | `App.test.jsx` | Açık dosyanın kenarı `400`'e çekilir, `←`'dan sonra liste `400`'de |
| 8 | `App.test.jsx` | Okurken `220`'nin altına çekilince dosya tutulan genişlikte açık kalır; `←`'dan sonra panel katlı |
| 9 | `workspace.css.test.js` | `.rail--open`'ın kendi genişliği yok, `display: flex` kalır (bugünkü *…at the design's widest* bununla yer değiştirir) |
| 10 | `workspace.css.test.js` | `.rail__grip`'te `z-index: 1` |

**Kalkan iki test**, tersini söyledikleri için: *a rail showing a document has no grip*
(`FileRail.test.jsx`) ve *while reading, the rail is the document at the design's widest*
(`workspace.css.test.js`). Susturulmaz, silinir; yerlerine 3 ve 9 gelir.

Bugün de yeşil kalanlar bekçi: listenin tutma yeri testleri, *dragging it past its minimum folds it
instead of leaving a sliver*, *opening a file empties the rail, and ← brings the list back*,
`railWidth.test.js`'in sınırları, `.rail`'in `320`'sinin kilidi.

`railWidth.test.js`'teki bir yorum (`560 is what the rail is drawn at while a document is open`)
artık doğru değil; bu turda düzelir, testin kendisi değişmez.

## Tutmaz

- **Görünüşün kendisi** — imlecin kenarda `↔` olması, tutma yerinin gerçekten metnin üstünde
  yakalanması — jsdom'da görülmez; tarayıcıda görülür. 10 yalnız kuralın yazılı olduğunu tutar.
- **`APP-BUGS.md`'nin 45'i ve 46'sı** (dar pencerede kesilen okuyucu; katlayan bir sürüklemeden sonra
  kapalı kalan yumuşama) bu maddenin değil.

## Bu turda yazılmayanlar

- `FileRail.jsx`, `railWidth.js` ve `workspace.css` değişmez; uygulama turunda.
- `dist` derlenmez: birleştirirken conductor derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` kırmızı verir: FileRail'in 1–5'i,
App'in 6–8'i, CSS'in 9'u ve 10'u düşer. Öteki üç süit yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m356-acik-dosya-genisligi-testler-plan.md).
