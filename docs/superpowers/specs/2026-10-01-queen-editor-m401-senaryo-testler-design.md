# Madde 401 — Karenin senaryosu kartta görünür, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`. Yer, tasarımın üç varyasyonundan `alt`
*(kullanıcı, 30 Eylül — "alt olan olsun")*. Tasarım 196 — queen-design'ın `queen-editor-v1` dalı,
`fotograf-detayi/index.html`'in `senaryoCard()`'ı, `.sen-sep`, `.sen-btn`, `.sen-card` CSS'i ve
`senaryoBtn`; `glyphs.js`'in `scenario` ikonu; tasarımcının spec'i
`2026-09-29-queen-editor-senaryo-design.md`.

## Bugün ne oluyor

397'den beri `GET /api/projects/<p>/frames`'in her kartında `scene` alanı var: karenin senaryosu,
senaryosu yoksa `""`; kopyalar ve varyantlar kaynak karenin senaryosunu taşıyor. Karenin sayfası
*(`PhotoDetail.jsx`)* bu alanı hiç okumuyor: sekme şeridinde yalnız *Foto*, *Video*, *Ses* var.

## Kurallar

1. **Düğme şeridin sonunda:** *Foto*, *Video*, *Ses*'in sağında, ince bir çizgiyle ayrılmış *(1px,
   `--border` rengi — tasarımın `.sen-sep`'i)* bir *"Senaryo"* düğmesi — ikon ve söz. **Kendi
   görünüşünde:** sekmelerin çerçevesi *(`wf-stroke`)* ve zemini yok.
2. **Kapalı başlar.** Basınca kart açılır, bir daha basınca kapanır. Düğme hâlini `aria-pressed` ile
   söyler; açıkken rengi vurgu *(`--accent`)*, kapalıyken `--ink-3` — tasarımdaki gibi.
3. **Kart resmin üstünde, resmin kendi kutusunun alt kenarında** *(`alt`)*: solda, sağda ve altta
   12px. Zemini sayfanın resmin üstüne koyduğu öteki koyu kutularınki *(`rgba(10, 8, 7, .72)`)*.
   Tıklamayı almaz *(`pointer-events: none`)*: videoda resmin kendisi oynat/durdur düğmesi.
4. **Videoda ve seste kart oynatıcının saatinin üstünde:** kutusu oynatıcının sahnesi
   *(`[data-scene]`)*, alttan 40px — saatle çizginin, ya da dalga şeklinin şeridini paylaşmaz.
5. **Resmi henüz olmayan karede** — kuyrukta, üretiliyor ya da hata almış — kart yer tutucunun
   üstünde durur *(tasarım: `square()`'in `.wf-img`'i)*. Katman üretilirken resim kaldığında kart o
   resmin üstünde.
6. **Senaryosu olmayan karede** kart *"Bu karenin senaryosu yok"* der, soluk *(beyazın `.55`
   saydamlığı)*.
7. **Yalnız okunur:** senaryo bir yazı kutusunda değil.
8. **Hâli kalır:** açık ya da kapalı, sekme değişince ve oklarla başka kareye geçince aynı kalır —
   tasarımdaki `senaryoAcik` gibi, 399'un *Ayrıntılar*'ı gibi. Geçilen karede kart o karenin
   senaryosunu okur.
9. **Galeri değişmez.**

## Yazılacak testler — `PhotoDetail.test.jsx`

Yeni blok, *"PhotoDetail — the frame's scenario (madde 401)"*, 399'un bloğunun ardına. Düğme rolüyle
ve adıyla bulunur: `getByRole("button", { name: "Senaryo" })`; kart `[data-scenario]` ile. İki
senaryo cümlesi sabit — `SCENE` ve ikinci kare için `SECOND_SCENE`; kartlar sunucunun biçiminde
*(`scene: ""` senaryosuz kart)*.

1. **Yeni** `puts a Senaryo button after the three tabs, set apart by a thin line` — `[data-strip]`'in
   son çocuğu düğme, ondan önceki 1px genişliğinde, zemini `var(--border)`; düğmede `wf-stroke` yok,
   zemini `none`, içinde `[data-glyph=scenario]`.
2. **Yeni** `starts closed, with nothing laid over the picture` — `aria-pressed` `"false"`,
   `[data-scenario]` yok.
3. **Yeni** `opens the frame's scenario over the picture on a press, and closes it on the next` —
   basınca kartta `SCENE`, ve hiçbir yazı kutusunun değeri `SCENE` değil *(7. kural)*; bir daha
   basınca kart yok.
4. **Yeni** `lights the button while the card is open` — `aria-pressed` ve renk: `--ink-3`, basınca
   `--accent`.
5. **Yeni** `lays the card along the photo's bottom edge, in the page's translucent dark` — kartın
   ebeveyni fotoğrafı tutan kutu *(içinde `P0_0.png`, `position: relative`)*; kart `absolute`, sol,
   sağ, alt `12px`; zemin `rgba(10, 8, 7, .72)`; `pointer-events: none`.
6. **Yeni** `lifts the card over the player's clock on the %s tab` — `it.each(["Video", "Ses"])`: kart
   `[data-scene]`'in içinde, alt `40px`.
7. **Yeni** `keeps the card on the picture while a layer is made over it` — `RENDERING`, Video
   sekmesi: kartın ebeveyninde fotoğraf ve `[data-making]` var.
8. **Yeni** `lays the card on the holder of a frame that is %s` — `it.each`: kuyrukta, üretiliyor,
   hata almış kare; kartın ebeveyni `wf-img` yer tutucusu.
9. **Yeni** `says so, dimmed, on a frame with no scenario` — `scene: ""`: kartta *"Bu karenin
   senaryosu yok"*, yazının rengi `rgba(255, 255, 255, .55)`.
10. **Yeni** `keeps the card open when the tab changes` — foto sekmesinde açılır, Video'ya geçilir:
    `aria-pressed` `"true"`, kart sahnede, cümle aynı.
11. **Yeni** `keeps the card open while the arrows walk to another frame, and reads the new one's` —
    `[LAYERED + SCENE, SECOND + SECOND_SCENE]`, açılır, sayfa `P1_0`'a geçer *(aynı sayfa, yeni kare —
    `rerender`)*: `aria-pressed` `"true"`, kartta `SECOND_SCENE`.

Renkler jsdom'da boşluklu ve `0.72` biçiminde okunabildiği için `rgba` beklentileri düzenli ifadeyle
yazılır — `LayerPlayer.test.jsx`'in yaptığı gibi.

## Değişen testler

Yok. Kart kapalı başladığı için sayfanın öteki testleri onu görmez; sekmeler adlarıyla bulunuyor
(`tab("Foto")`…), ve *"Senaryo"* onlardan biri değil.

## Bekçiler

Sekmeler *(sekizer piksel, açık sekmenin rengi)*, sahne, oyuncu, *Ayrıntılar*, prompt kutuları,
düğmeler ve galeri: dosyaların öteki testleri. Bugün de geçiyor, bu turda da geçmeli.

## Test yazılmayan

- **`ust` ve `kose`** — yapılmıyor *(kullanıcı: "alt olan olsun")*.
- **Tasarımın `?acik=` ve `?kare=` adresleri** — tuvalin, bir kartı açık çizebilmek için. Uygulamanın
  adresinde karenin kimliği var, kartın hâli yok: hâl sayfada duruyor, ve oklar sayfayı açık tutuyor.
  Galeriden yeniden açılan kare kapalı başlar — 2. test.
- **Düğmenin renk geçişi** *(`transition: color .12s`)* — jsdom zamanı çizmiyor.
- **Sunucu** — `scene` alanı 397'nin, testleri orada.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor/frontend`'de yeni testler kırmızı *(düğme yok, kart yok)*,
dosyanın öteki testleri yeşil; öteki üç satır yeşil.
