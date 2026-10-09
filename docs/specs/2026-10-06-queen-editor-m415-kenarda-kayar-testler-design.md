# Madde 415 — Kart sürüklenirken galeri kenarda kayar, test turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 415 · v9-7 · **Tur:** 1/2 — yalnız testler.

**Kullanıcıdan gereken — yok.** Madde 5 Ekim'de hizalandı: kart sürüklenirken imleç alt kenara
yaklaşınca sayfa aşağı, üst kenara yaklaşınca yukarı kayar *(kullanıcı — Claude'un önerisine: "bu
olur")*; yalnız galeri *(referans havuzu için: "bu promplem değil")*. Kenarın genişliği ve hız teknik
karar, Claude'un. Sonucu kullanıcı koşunun sonunda kendi eliyle dener.

## Bugün ne oluyor

- **Kayan, galerinin kendi kutusu.** Proje ekranı pencere boyunda (`100vh`); pencere kaymaz, galeri
  [ProjectScreen.jsx](../../queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx)'in
  `data-scroll` kutusunda kayar (`overflowY: auto`). Referans havuzu da aynı kutuda: havuz açıkken
  galeri `hidden`.
- **Kutu sürüklemeyi hiç dinlemiyor.** [Gallery.jsx](../../queen-editor/frontend/src/features/photo_generation/Gallery.jsx)'in
  sürüklemesi tarayıcının kendi sürükle-bırakı: her kutucukta `dragStart`, `dragOver`, `drop`,
  `dragEnd`. İmleç kutunun kenarına gelince hiçbir şey kutuyu kaydırmıyor — kart yalnız ekrandaki
  kartlar kadar taşınabiliyor *(kullanıcı, 25 Eylül — "sürükleyince aşağı kaymıyor ekran, ve ekrandaki
  kartlar kadar hareket ettirebiliyoruz")*.

## Kurallar

1. **Galeride bir kart sürüklenirken imleç kutunun alt kenarına 80 px'ten yakınsa kutu aşağı, üst
   kenarına 80 px'ten yakınsa yukarı kayar.** Kenar, kutunun ekrandaki kenarı — başlığın altı ve
   pencerenin dibi.
2. **Kart kenarda durdukça kutu kaymaya devam eder.** Tarayıcı, imleç kıpırdamasa da sürükleme
   sürdükçe `dragover`'ı tekrarlar *(HTML'in sürükle-bırak modeli: her 350 ms ± 200 ms)*; her `dragover`
   kutuyu bir adım, 20 px kaydırır.
3. **Kenarlardan uzakta kutu durur.**
4. **Sürükleme bitince kayma da biter** — `dragover` gelmez, ve geride çalışan bir şey kalmaz.
5. **Referans havuzu açıkken kutu kenarda kaymaz** — havuzun satırları bugünkü gibi.
6. **Sürüklemenin kendisi değişmez:** bırakılan yer, gönderilen sıra, seçimle birlikte taşıma.

## Nasıl kanıtlanıyor

Ekran testiyle, gerçek kutu ve gerçek galeriyle: `ProjectScreen` `listFrames`'in verdiği karelerle
açılır. jsdom yerleşim yapmaz — kutunun ekrandaki yeri sahte: `getBoundingClientRect` üstü 100,
altı 700 der. jsdom `scrollTop`'u verildiği gibi tutar *(useKeptScroll'un testi de buna dayanıyor)*;
her test kutuyu 300'e koyup başlar.

**İmlecin yüksekliği:** jsdom'da `DragEvent` yok, ve Testing Library'nin `fireEvent.dragOver`'ı yerine
düz bir `Event` kurup `clientY`'yi düşürüyor. Testler `dragover` adlı bir `MouseEvent` gönderir — React
onu sürükleme olayı olarak okur, `clientY` içinde. Kartın kalkışı bugünkü testler gibi
`fireEvent.dragStart`'la.

## Yazılacak testler — `frontend/src/features/photo_generation/ProjectScreen.test.jsx`

Yeni bir `describe`, dosyanın sonunda: *the gallery scrolls while a card is held at its edge (madde
415)*. Üç kare, ikisi arada; sürüklenen, ortadaki.

1. **Alt kenarda aşağı kayar** — kart kalkıyor, imleç 690'da (kutunun dibinden 10 px yukarıda):
   `scrollTop` 300'den büyük.
2. **Üst kenarda yukarı kayar** — imleç 110'da: `scrollTop` 300'den küçük.
3. **Kart kenarda durdukça kaymaya devam eder** — 690'da iki `dragover`: ikincisinden sonra
   `scrollTop` birincisinden sonrakinden büyük.
4. **Kenarlardan uzakta durur** — imleç 400'de: `scrollTop` 300.
5. **Referans havuzunu bugünkü gibi bırakır** — havuz açık, içinde bir resim; havuzun kartı kalkıyor,
   imleç 690'da: `scrollTop` 300.

## Kırmızı beklenen

- 1, 2, 3 kırmızı — kutu bugün sürüklemeyi dinlemiyor, `scrollTop` 300'de kalıyor.
- 4 ve 5 **yeşil**: bugünü kilitliyorlar — kayma kenarın dışına ve havuza taşmasın diye.
- Öteki her şey yeşil; öteki üç satır yeşil.

## Bilinçli olarak yapılmayan

- Hız kenara yaklaştıkça artmaz: tek adım, tek hız.
- Zamanlayıcı yok: kaymayı tarayıcının kendi tekrarladığı `dragover` yürütür, sürükleme bitince
  durduracak bir şey kalmaz.
- "En üstteki kart en alta" jsdom'da gösterilemez — yerleşim yok, her kart zaten erişilebilir;
  bırakılan yerin sırası `Gallery.test.jsx`'in bugünkü testlerinde. Ekranda Playwright'la bakılır.
- `dist`'e ve yol haritasına dokunulmaz.
