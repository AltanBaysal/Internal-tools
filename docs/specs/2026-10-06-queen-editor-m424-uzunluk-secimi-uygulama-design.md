# Madde 424 — Video panelinde uzunluk seçimi, uygulama turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 424 · v9-1d · **Tur:** 2/2 — kod.
**Üstüne kurulduğu:** [m424 test turu](2026-10-06-queen-editor-m424-uzunluk-secimi-testler-design.md) —
kurallar, seçilenler ve testler orada.

## Yaklaşımlar

- **Seçilen — tek bir kanca, iki ekran.** `useVideoLength(project, videoRow)` uzunluğu okur, bellekte
  tutar, ve seçimi yazar; H3 olup olmadığına da o bakar. Video paneli de karenin sayfası da yalnız
  `seconds`'ın `null` olup olmadığına bakar: *"söylenecek bir uzunluk var mı"* tek yerde karar verir.
- **Elenen — uzunluğu proje ekranında tutup panele ve kareye prop olarak vermek:** karenin sayfası
  proje ekranının içinde değil *(App.jsx)*; ikisine ayrı yoldan ulaşmak iki kural yazdırırdı.
- **Elenen — basınca yazmayı beklemek:** daha az parça, ama tasarım seçimin hemen değişmesini istiyor,
  ve tünelin gecikmesi kadar donan bir düğme bozuk görünür.

## Birimler

### Yeni — `frontend/src/features/photo_generation/useVideoLength.js`

- **Bellek:** modülde `CONFIRMED = new Map()` — proje başına sunucunun son doğruladığı uzunluk (okuma
  ya da yazma başarılı olunca). Kanca ilk değerini oradan alır.
- **H3:** `videoRow?.reads_references === true`. Değilse okumaz, ve `seconds` `null`.
- **Okuma:** H3'te her kuruluşta `getVideoLength`. Cevap gelir: belleğe ve ekrana — bu kuruluşta bir
  basış olmadıysa. Hata: sessiz.
- **`choose(seconds)`:** hemen gösterir; `saveVideoLength`; yazılırsa belleğe; yazılamazsa ekranı
  belleğin değerine döndürür ve hatayı fırlatır — kartı panel çizer.
- **Döner:** `{ seconds: h3 ? bilinen : null, choose }`.

### `frontend/src/shared/api.js`

- `getVideoLength(project)` → `body.seconds`; `saveVideoLength(project, seconds)` → PUT
  `{ seconds }`. Referanstan'ın kaydının yanında: ikisi de projenin bir ayarı.

### `LayerPanel.jsx`

- `useVideoLength(project, layer === "video" ? producer : null)` — ses paneline video satırı
  verilmez.
- **Blok** Model'in altında, `length !== null` iken: `Mono` başlık *"Video uzunluğu"* (`data-label`,
  öteki başlıklarla aynı), sekmelerinkiyle aynı `wf-segment` (`display: flex`, düğmeler `flex: 1`);
  düğmeler `4 sn`, `aria-label` *"4 saniye"*, seçili olan `is-on`. Sekmelerin dallanmasından önce:
  iki sekmede de aynı yerde.
- **Basış:** kart yuvası boşalır; `choose` reddedilirse yeşil kart ve sayacı gider, kırmızı kartta
  hatanın cümlesi (`err.message` — `shared/api.js`'in verdiği, sunucunun ya da ağın).
- **Cümleler:** `lengthSaid = length === null ? "" : " " + length + " sn."` Kareden'in cümlesinin
  ve kopya uyarısının sonuna; Referanstan'ın satırı *"… kart."* ve sonuna.
- Bileşenin başındaki yorum *"the length is fixed"* diyor — artık doğru değil, düzeltilir.

### `PhotoDetail.jsx`

- `useProducers()` — ziyaret boyunca hatırlanıyor; karenin sayfası bir istek daha yapar
  (`/api/producers`), dönüşte bellekten çizer.
- `useVideoLength(project, video satırı)`.
- Yeniden üret'in notunun sonuna `lengthSaid`; Tekrar dene'nin altına, `openState === "failed" &&
  open === "video" && length !== null` iken *"Aynı kare yeniden denenir."* + `lengthSaid`.

## Dokunulmayan

Sunucu, `dist`, CSS (tasarımın `.lengths` kuralı sekmelerin satır içi stiliyle aynı — panel o yolu
kullanıyor), kuyruk paneli, galeri, Eklendi kartı, oynatıcı.

## Doğrulama

Dört satır. Test turunun 24 kırmızısı yeşile döner; öteki her şey yeşil kalır.
