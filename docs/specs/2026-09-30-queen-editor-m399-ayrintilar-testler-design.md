# Madde 399 — Karenin bilgileri açılır kapanır bir bölümde, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`: *"tasarımla aynı olsun"* (kullanıcı, 30 Eylül).
Tasarım 200 — queen-design'ın `queen-editor-v1` dalı, `fotograf-detayi/index.html`'in `info()`'su,
`.ayrintilar` CSS'i ve `ayrintilarBtn`; tasarımcının spec'i
`2026-09-29-queen-editor-ayrintilar-design.md`.

## Bugün ne oluyor

Karenin sayfasında sağ sütunun ilk grubu (`data-group="info"`) bütün bilgileri art arda sıralıyor:
*Sıra*, *Dosya adı* — ya da *Dosya adı (planlanan)* —, foto sekmesinde *Model* ve varsa *LoRA*,
modu bilinen bitmiş videoda *Üretim modu*. Hepsi her zaman açık *(`PhotoDetail.jsx`)*.

## Kurallar

1. **Sütun yalnız *Sıra* ile başlar.** *Üretim süresi* 408'de *Sıra*'nın yanına gelir; bu madde
   üst grupta *Sıra*'yı bırakır.
2. **Altında tek bir *"Ayrıntılar"* satırı** — bir düğme, yanında kitin aşağı bakan oku. **Kapalı
   başlar**: galeriden açılan her kare kapalı açılır.
3. **Basınca açılır:** *Dosya adı*, *Model*, *LoRA* ve *Üretim modu* satırın altına gelir, her biri
   bugün hangi koşulda görünüyorsa yine o koşulda; sıraları bugünkü gibi. Ok yukarı döner
   *(`rotate(180deg)`)*. **Bir daha basınca kapanır.**
4. **Hâli kalır:** açık ya da kapalı, oklarla başka kareye geçince ve sekme değişince aynı kalır —
   tasarımdaki `ayrintilarAcik` gibi *(`step()` ve sekme değişimi onu sıfırlamıyor)*.
5. **Satır bir etiket, kutu değil:** yazı sütunun öteki etiketlerinin görünüşünde — büyük harf —, ve
   düğmenin zemini yok *(tasarımcının spec'i — "kutu yok")*.
6. **Sütun üç parça:** üstte bilgi grubu, altında bölüm, en altta üretim grubu — tasarımda da
   `.info`, `.ayrintilar`, `.prod` sütunun üç kardeşi. Bölümün satırla içi arasındaki boşluk 12px
   *(`.ayrintilar { gap: 12px }`)*; öteki ölçüler bugünkü gibi.
7. Prompt kutuları, *Yeni mod*, düğmeler **değişmez**.

## Yazılacak testler — `PhotoDetail.test.jsx`

Yeni blok, *"PhotoDetail — the details section (madde 399)"*. Düğme rolüyle ve adıyla bulunur:
`getByRole("button", { name: "Ayrıntılar" })`; açık mı, `aria-expanded`'dan okunur.

1. **Yeni** `opens the column with the counter alone and the section closed` — `LAYERED`, foto
   sekmesi: `[data-field]` listesi `["Sıra"]`, düğmenin `aria-expanded`'ı `"false"`, *Dosya adı*
   ekranda yok.
2. **Yeni** `opens the frame's facts under the row on a press, and folds them on the next` — basınca
   `aria-expanded` `"true"`, bölümün `[data-field]`'ları `["Dosya adı", "Model", "LoRA"]`; bir daha
   basınca `"false"` ve liste yine `["Sıra"]`.
3. **Yeni** `turns the caret up while the section is open` — okun kutusu (`[data-caret]`) kapalıyken
   dönmüyor, açıkken `rotate(180deg)`.
4. **Yeni** `keeps the section open when the tab changes` — modu `loop` olan kare; foto sekmesinde
   açılır, Video sekmesine geçilir: `aria-expanded` `"true"`, liste `["Sıra", "Dosya adı",
   "Üretim modu"]`.
5. **Yeni** `keeps the section open while the arrows walk to another frame` — `[LAYERED, SECOND]`,
   açılır, sayfa `P1_0`'a geçer *(aynı sayfa, yeni kare — `rerender`)*: `aria-expanded` `"true"`,
   *Dosya adı* `P1_0.png`.
6. **Yeni** `draws the row as a label, with no box` — düğmenin zemini `none`, yazısı büyük harf
   (`textTransform: uppercase`).

## Değişen testler

Bilgiler artık kapalı bölümün içinde; onları okuyan testler önce satıra basar. Beklentileri aynı.

- *the layer tabs* bloğu:
  - `keeps the frame's own name and its place on every tab` — başta bir basış; sekmeler değişirken
    bölüm açık kalıyor *(4. kural)*.
  - `keeps nothing else in the top group` → `keeps nothing else behind the row on the video tab` —
    basış, Video: `["Sıra", "Dosya adı"]`.
  - `says which model the frame was made with`, `says a model by the name it was picked by`,
    `falls back to what the frame stored when the row list is not there`,
    `says which lora the frame was made with (madde 237)`, `says the lora %s by the name it was
    picked by (madde 238)`, `draws no lora row for a frame that never named one`,
    `draws no model row for a frame that never carried one`,
    `keeps the model and the lora on the photo tab alone` — birer basış. *"Yok"* diyen testler de
    basar: kapalı bölümde her satır zaten yok, ve test bir şey söylemez olurdu.
  - `keeps the photo tab's top group to its four rows` → `keeps the photo tab's facts to their four
    rows` — basış; liste `["Sıra", "Dosya adı", "Model", "LoRA"]`.
  - `keeps the open tab when the next frame has that layer too` — *"it really is the next frame"*
    satırı *Dosya adı*'ndaki `P1_0.png`'yi değil, *Sıra*'nın `1 / 2`'sini okur: tabın kalıp
    kalmadığını soran test bölüme basmaz. Bugün de geçer.
- *how the video was made* bloğu, altı testin hepsi: Video sekmesinden önce bir basış.
- *PhotoDetail* bloğu, `shows the position, the file name and the prompt` — dosya adından önce
  basış.
- *a frame that is not a photo yet* bloğu, `calls the file name planned, and only for the frames that
  have no file` ve `keeps the plain label on a produced photo` — basış.
- `splits the column into two groups with nothing between them` →
  `splits the column into its facts, the section and what can be made of it` — sütunun çocukları
  `["info", "details", "production"]`.
- `keeps one vertical rhythm down the column` — üretim grubu artık üçüncü çocuk; bölümün kendi gap'i
  `12px`.

## Bekçiler

Prompt kutuları, kopyalama, *Yeni mod*, *Yeniden üret*, *Tekrar dene*, silme düğmeleri, sekmeler,
sahne ve oklar: dosyanın öteki testleri. Hiçbiri bölüme dokunmuyor, ve bugün de geçiyor.

## Test yazılmayan

- ***Üretim süresi*** — 408'in.
- **Tasarımın `?ayrintilar=` adresi** — tuvalin, bir kartı açık çizebilmek için. Uygulamanın
  adresinde karenin kimliği var, bölümün hâli yok: hâl sayfada duruyor, ve oklar sayfayı açık
  tutuyor. Galeriden yeniden açılan kare kapalı başlar — 1. test.
- **Okun dönüş geçişi** *(`transition: transform .12s`)* — jsdom zamanı çizmiyor.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor/frontend`'de yeni altı test ve bölüme basan değişen testler
kırmızı, `keeps the open tab when the next frame has that layer too` yeşil; öteki üç satır yeşil.
