# Madde 424 — Video panelinde uzunluk seçimi, test turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 424 · v9-1d · **Tur:** 1/2 — yalnız testler.
**Üstüne kurulduğu:** [m422 test turu](2026-10-06-queen-editor-m422-h3-uzunlugu-testler-design.md),
[m422 uygulama turu](2026-10-06-queen-editor-m422-h3-uzunlugu-uygulama-design.md) — projenin uzunluğu,
kapısı, ve her H3 video işinin onu taşıması.

**Kullanıcıdan gereken — yok.** Madde hizalı; kararları yol haritasının *Maddelerin kararları → v9-1*
bölümünde, kullanıcının sözleriyle. Görünüş ve sözler tasarımcının 206'sından *(queen-design
`queen-editor-v2`; ana klasörün `tmp/queen-design-queen-editor-v2/`'sinde `proje-ekrani-tam/`,
`fotograf-detayi/`, `docs/superpowers/specs/2026-10-05-queen-editor-uzunluk-design.md`)*, davranışlar
`BEHAVIOUR.md`'nin *Decided here* maddesinden ve *Video panel*, *Photo detail* bölümlerinden. Sunucunun
kapısı 422'de kuruldu; bu parça ona dokunmaz. Ekranın H3'ü nereden bildiği, uzunluğu ne zaman okuduğu ve
neyi tarayıcıda tuttuğu teknik kararlar, Claude'un.

## Kullanıcının sözü

*"videoları veya 4 8 12 arasında seçebilmek video uzunlupunu"*, *"h3e özel"*, *"tek seçim video
panelinde"*, *"varsalın 8 olsun"*, *"evet hatıkasnsjın"* *(5 Ekim)*. Tasarım turunda: *"Evet, iki sekme
de"*, karenin sayfasından üretilen H3 videosu için *"Evet"*, kuyrukta bekleyen için *"Eklendiği
uzunlukta"*.

## Bugün ne oluyor

Sunucu projenin uzunluğunu tutuyor ve her H3 video işine koyuyor *(422)*:
`GET /api/projects/<proje>/video-length` → `{"seconds": 8}` (kayıt yoksa 8);
`PUT …/video-length`, gövde `{"seconds": 4|8|12}` → `204`; başka değer `400` *"Video uzunluğu 4, 8 ya da
12 saniye olmalı."*; proje yoksa `404` *"Proje yok: …"*. Ekran kapıyı hiç çağırmıyor: video panelinde
seçim yok, *Kuyruğa ekle*'nin altındaki cümle ve karenin sayfasının notları uzunluk söylemiyor;
`shared/api.js`'te kapıya giden bir fonksiyon yok.

## Kurallar

### Seçim

1. **Yalnız H3 oturumunda, Model'in hemen altında.** Küçük başlık *"Video uzunluğu"*, altında panel
   genişliğinde bir `wf-segment`: *4 sn · 8 sn · 12 sn*, biri `is-on`; düğmelerin erişilebilir adı
   *"4 saniye"*, *"8 saniye"*, *"12 saniye"*. Kareden'de sıra: Model · Video uzunluğu · Kapsam · Üretim
   modu · Varyant; Referanstan'da: Model · Video uzunluğu · Referanslar · Prompt listesi · Varyant
   *(206)*.
2. **Seçili olan projenin kaydı** — sunucunun söylediği; kayıt yoksa sunucu 8 der.
3. **Basınca seçim hemen değişir ve projeye yazılır** *(206 — "Bir düğmeye basınca seçim hemen
   değişir")*. Paneldeki başka hiçbir kutu sıfırlanmaz.
4. **Sekme değişince yerinde kalır**, seçimiyle.
5. **Panel yeniden kurulunca** — kapanıp açılınca, kareye girip dönünce, proje yeniden açılınca — seçim
   projenin kaydından gelir.
6. **Çizilmediği yerler — yer de ayrılmaz:** WAN oturumu; model henüz okunmamışken; ses paneli
   *(206)*; ve uzunluk henüz okunmamışken ya da okunamadıysa *(aşağıda)*. Bu hâllerde uzunluk da
   okunmaz — yalnız H3'te sorulur.
7. **Kurulu olmayan H3 de H3:** video üreticisi kurulu değilken Model kutusu yine *MiniMax H3* der, ve
   seçim çizilir *(BEHAVIOUR.md — "the video panel's Model box names it either way"; tasarımın
   `lengthShown`'u yalnız modele bakar)*.

### Cümleler

8. **Kuyruğa ekle'nin altındaki cümle uzunlukla biter**, yalnız H3'te ve uzunluk biliniyorken; WAN'da
   ve model okunmamışken bugünkü gibi *(206)*:
   - *"2 loop video üretilecek — her video kendine döner. 8 sn."*, *"… her video sıradaki karede biter.
     8 sn."*, *"… her kare kendi videosunu alır. 8 sn."*;
   - kopya uyarısı: *"1 loop video üretilecek — videolu 1 kare için yeniler kopya kare olur, eskisi
     durur. 8 sn."*;
   - Referanstan: *"2 prompt × 3 varyant = 6 kart. 8 sn."*
9. **Sayıyla birimi ayrılmaz:** aradaki boşluk bölünmez (` `), düğmelerde de — *"The space is
   unbreakable so the number never ends one line with its unit alone on the next"* (tasarımın yorumu).
10. **Referanstan'ın satırı noktayla biter, her oturumda:** *"… = 6 kart."* — tasarım 206'da cümleye
    noktayı koydu, uzunluk ondan sonra yeni bir cümle olarak gelir. Bugün uygulamada nokta yok.
11. **Eklendi kartı uzunluk taşımaz:** *"2 loop video kuyruğa eklendi"* *(206)*.

### Karenin sayfası

12. **Yeniden üret'in notu H3'te projenin uzunluğunu söyler:** *"Yeni bir kare açılır — P0_0 kopyası,
    loop video. 12 sn."* — karenin değil projenin uzunluğu. WAN'da ve model okunmamışken bugünkü gibi.
13. **Tekrar dene, video sekmesinde ve H3'te, bir not alır:** *"Aynı kare yeniden denenir. 8 sn."*
    *(206 — "bugün bu düğmenin notu yok, uzunluğun söylenebileceği tek yer burası")*. WAN'da, model
    okunmamışken, uzunluk bilinmezken ve fotoğraf sekmesinde not yok.

### Hata

14. **Yazılamayan seçim:** sunucunun cümlesi panelin kırmızı kartında, *Kuyruğa ekle*'nin altında —
    panelin öteki hatalarının yeri —, ve seçim projenin kayıtlı uzunluğuna geri döner. Bir sonraki
    basış kartı kaldırır.
15. **Okunamayan uzunluk:** seçim çizilmez, cümle ve notlar uzunluk söylemez, kart çıkmaz.

## İki türlü okunabilen yerler — seçilenler

- **Ekran H3'ü nereden bilir?** Üreticiler listesinin video satırındaki `reads_references`'tan.
  Sunucu onu `config.VIDEO_MODEL == "h3"` diye yazıyor *(`list_producers.py`)* — `main.py`'nin her H3
  video işine uzunluk koyduğu koşulun aynısı. Modelin adı (*"MiniMax H3"*) kutunun sözü, kural değil
  *(madde 324'ün aynı kararı)*. Video satırı yoksa — üreticiler henüz okunmamış — model okunmamış.
- **Uzunluk okunana kadar?** Seçim çizilmez, yer ayrılmaz, cümle uzunluk söylemez — tasarımın okunmamış
  model kuralının aynısı: boş bir yer *"seçim yüklenemedi"* gibi okunur, ve 8 göstermek kayıt 12 iken
  yalan olur.
- **Okunamazsa?** Sessiz: seçim çizilmez. Referanstan'ın kaydının kuralı — okunamayan bir okuma yalnız
  bir ön doldurmayı kaybeder; sunucuya ulaşılamıyorsa galerinin yoklaması bunu zaten aynı kartta
  söylüyor. Kuyruğa giden iş yine sunucunun kayıtlı uzunluğuyla çıkar.
- **Basınca beklemek mi, hemen göstermek mi?** Hemen *(206)*; yazılamazsa geri döner ve kart çıkar
  (kural 14). Kayıtlı olmayan bir uzunluğu seçili göstermek yalan olur.
- **Panel her açılışta yeniden mi okur?** Evet — kayıt diskte. Ama ziyaret boyunca proje başına son
  doğrulanan uzunluk bellekte (modülde bir `Map`, uygulamanın öteki ekran hafızaları gibi): yeniden
  kurulan panel onu hemen çizer, blok her açılışta geç gelip altındakileri itmez; sunucunun cevabı gelince
  o geçer. Okuma yoldayken kullanıcı bastıysa basış geçer.
- **Karenin sayfası modeli nereden bilir?** Panelin bildiği yerden: üreticiler listesi
  (`useProducers` — ziyaret boyunca hatırlanıyor) ve aynı uzunluk. Tasarım ikisini adresle taşıyor;
  uygulamanın adresi yalnız kareyi taşır.
- **Oynatıcı karenin kendi uzunluğunu gösterir** *(206)* — uygulamada zaten öyle: süre videonun
  kendisinden okunuyor *(BEHAVIOUR.md, Photo detail)*. Bu maddede değişmez.

## Arayüz — uygulama turunun vereceği

- **`frontend/src/shared/api.js`** — `getVideoLength(project)` → saniye; `saveVideoLength(project,
  seconds)`.
- **`frontend/src/features/photo_generation/useVideoLength.js`** — `useVideoLength(project, videoRow)`
  → `{ seconds, choose }`: `seconds` yalnız H3'te ve uzunluk biliniyorken bir sayı, yoksa `null`;
  `choose(seconds)` hemen gösterir, yazar, yazılamazsa geri döner ve hatayı fırlatır.
- **`LayerPanel.jsx`** — seçim bloğu, cümlelerin sonu, yazılamayan seçimin kartı.
- **`PhotoDetail.jsx`** — iki notun sonu.

## Nasıl kanıtlanıyor

`LayerPanel.test.jsx` ve `PhotoDetail.test.jsx` `shared/api.js`'i taklit ediyor; iki yeni fonksiyon
taklide girer — `getVideoLength`, `saveVideoLength`, karenin sayfasında `listProducers` de. Sunucunun
cevabı test başına verilir: bekletilir, reddedilir. Panel props'la çizilir; video satırı sunucunun
biçiminde (`reads_references`). Bellek proje başına olduğu için her test kendi proje adını kullanır;
belleği deneyen testler aynı adı bilerek iki kez. `api.js`'in kendisi `fetch` yerine konan sahteyle
*(CODE-STANDARD, Tests)*.

## Yazılacak testler

### `frontend/src/shared/api.test.js`

1. **Projenin video uzunluğu kendi adresinde okunur ve yazılır** — GET `{"seconds": 12}` → 12; PUT,
   gövde `{"seconds": 4}`; ikisi de `/api/projects/d%C3%BC%C4%9F%C3%BCn/video-length`.

### `frontend/src/features/photo_generation/LayerPanel.test.jsx`

**Değişen** — Referanstan'ın satırı noktayla biter (kural 10), model okunmamışken:

2. *"counts the cards the press would make"* → *"2 prompt × 3 varyant = 6 kart."*
3. *"reads a Python list with a name in front…"* → *"2 prompt × 1 varyant = 2 kart."*
4. *"reads a tuple, in either quote"* → aynı.
5. *"leaves the blank items out of the count"* → aynı.

**Yeni — "the H3 video length (madde 424)"**

6. **H3'te Model'in hemen altında, sekmenin kutularının üstünde; kaydın 8'i seçili** — başlıklar Model,
   Video uzunluğu, Kapsam, Üretim modu, Varyant; düğmeler sırayla `4 sn`, `8 sn`,
   `12 sn`; *8 saniye* `is-on`, öteki ikisi değil; kapı projenin adıyla soruldu.
7. **Referanstan'da aynı yerde** — Model, Video uzunluğu, Referanslar, Prompt listesi, Varyant.
8. **Kayıtlı uzunluk seçili gelir** — sunucu 12: *12 saniye* `is-on`.
9. **Basılan hemen seçilir ve projeye yazılır** — yazma bekletilir: *12 saniye* `is-on`, *8 saniye*
   değil; `saveVideoLength(proje, 12)`.
10. **Sekme değişince seçim yerinde** — Kareden'de 12; Referanstan'da 12; Kareden'de yine 12.
11. **Başka hiçbir kutu sıfırlanmaz** — Standart ve 3 varyant seçiliyken 12'ye basılır: *"6 video
    üretilecek — her kare kendi videosunu alır. 12 sn."*
12. **Yeniden kurulan panel bildiği uzunlukla açılır, ve sunucunun cevabı geçer** — ilk panel 12 okur
    ve kapanır; ikinci okuma bekletilir: 12 seçili; cevap 4: 4 seçili.
13. **Okuma yoldayken basılan uzunluk okumanın cevabıyla ezilmez** — ikinci panelde okuma bekletilir,
    4'e basılır, okuma 12 der: 4 seçili.
14. **WAN'da seçim yok, uzunluk okunmaz, cümle bugünkü gibi** — başlıklar Model, Kapsam, Üretim modu,
    Varyant; *"2 loop video üretilecek — her video kendine döner."*; kapı sorulmadı.
15. **Model okunmamışken de** — video satırı yok: aynı üç şey.
16. **Video üreticisi kurulu değilken H3'te seçim çizilir.**
17. **Uzunluk okunana kadar seçim ve cümlenin sonu yok** — okuma bekletilir.
18. **Okunamayan uzunluk seçimi de cümlenin sonunu da düşürür, kart çıkarmaz** — okuma reddedilir.
19. **Ses panelinde seçim yok, uzunluk okunmaz, cümle bugünkü gibi** — *"1 ses üretilecek — her kare
    kendi sesini alır."*
20. **Cümle uzunlukla biter** — parametreli: Loop *"2 loop video üretilecek — her video kendine döner.
    8 sn."*, Sonrakine bağla *"… her video sıradaki karede biter. 8 sn."*, Standart *"2 video
    üretilecek — her kare kendi videosunu alır. 8 sn."*; sondaki boşluk bölünmez (`8 sn.`).
21. **Kopya uyarısı da** — *"1 loop video üretilecek — videolu 1 kare için yeniler kopya kare olur,
    eskisi durur. 8 sn."*
22. **Seçilen uzunluk söylenir** — 12'ye basılınca *"… kendine döner. 12 sn."*
23. **Referanstan'ın satırı da** — *"2 prompt × 3 varyant = 6 kart. 8 sn."*
24. **Eklendi kartı uzunluk taşımaz** — *"2 loop video kuyruğa eklendi"*.
25. **Yazılamayan seçim sunucunun cümlesini kartta söyler, ve seçim kayıtlıya döner** — yazma
    *"Proje yok: …"* ile reddedilir: kırmızı kartta o cümle; *8 saniye* `is-on`, *12* değil.
26. **Bir sonraki basış kartı kaldırır** — 4'e basılır ve yazılır: kart yok, 4 seçili.

### `frontend/src/features/photo_generation/PhotoDetail.test.jsx`

Taklide `listProducers` ve `getVideoLength` girer; her testin başında üreticiler boş liste, uzunluk 8 —
öteki testler bugünkü gibi kalır.

**Yeni — "the length a new video gets (madde 424)"**

27. **H3'te Yeniden üret'in notu projenin uzunluğunu söyler** — loop video, proje 12: *"Yeni bir kare
    açılır — P0_0 kopyası, loop video. 12 sn."*
28. **WAN'da not bugünkü gibi** — *"Yeni bir kare açılır — P0_0 kopyası, loop video."*
29. **H3'te kırmızı videonun Tekrar dene'si notunu alır** — *"Aynı kare yeniden denenir. 8 sn."*
30. **WAN'da Tekrar dene'nin notu yok.**
31. **Fotoğraf sekmesinin Tekrar dene'sinin notu yok** — fotoğrafı kırmızı kare, H3.
32. **Uzunluk okunamazken Yeniden üret'in notu uzunluk vaat etmez** — H3, okuma reddedilir, kendi
    adıyla bir proje: not bugünkü gibi.
33. **Uzunluk okunamazken Tekrar dene'nin notu yok** — aynı şartlarla kırmızı video.

## Kırmızı beklenen

- 1: `api.getVideoLength is not a function`.
- 2 – 5: satır *"… kart"*, nokta yok.
- 6 – 13, 16, 20 – 23, 25, 26: seçim yok, cümleler uzunluk söylemiyor.
- 27, 29: notlar uzunluk söylemiyor; Tekrar dene'nin notu yok.
- Bugün de yeşil olanlar, kuralı tutmak için: 14, 15, 17, 18, 19, 24, 28, 30, 31, 32, 33.
- Sayı: 24 kırmızı (1; 2 – 5; 6 – 13, 16, 20'nin üç durumu, 21 – 23, 25, 26; 27, 29), 11 yeşil.
- Öteki her şey yeşil; öteki üç satır yeşil.

## Bilinçli olarak yapılmayan

- Sunucuda değişiklik — kapı 422'nin, olduğu gibi. Eksik bir kapı görülmedi.
- `dist` — koşunun birleşmesinde kurulur.
- Oynatıcının uzunluğu — uygulamada zaten videodan okunuyor.
- Kuyruk panelinde ve galerinin kutucuklarında uzunluk — tasarım istemiyor *(206)*.
- Uzunluğu `sessionStorage`'da tutmak — tasarımın taklidi; uygulamada projenin kaydı.
- Seçimi WAN'a açmak — *"h3e özel"*.
