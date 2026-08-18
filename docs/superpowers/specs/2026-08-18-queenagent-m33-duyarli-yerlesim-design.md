# Madde 33 — Duyarlı yerleşim · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 33](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 70, 71, 72, 73 · [tasarım v2 farkları](../research/2026-08-14-mira-tasarim-farklari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · Ölçü pencereden kabuğa geçiyor (fark 70)

Bugün duyarlılık `@media (max-width: …)` ile yazılı; ölçülen şey **tarayıcı penceresi**. Tasarımın
istediği ölçü **kabuğun kendi ölçülen genişliği** — gerekçesi belgede yazılı: aynı ekran gömülü bir
çerçeve içinde de doğru davransın.

Bu bir mekanizma değişikliği: `@media` pencereyi ölçer ve başka bir şeyi ölçemez. Kabuk kendi
genişliğini bir **ResizeObserver** ile ölçer, ölçüsünü basamak sınıflarına çevirir ve sınıflar
`.app-shell`'in üstünde durur. Bütün duyarlı kurallar o sınıfların altına taşınır.

| Basamak | Sınıf | Eşik |
|---|---|---|
| geniş | — | 1000'in üstü |
| dar | `.app-shell--narrow` | ≤ 1000 |
| sıkı | `.app-shell--tight` | ≤ 780 |
| küçük | `.app-shell--compact` | ≤ 640 |

**Sınıflar üst üste biner:** 600px'te üçü de vardır. Böylece her kural yalnız kendi eşiğini yazar;
"640'ta bunlar da geçerli" diye bir tekrar gerekmez.

**Ölçüsüz hâl geniş hâldir.** Ölçü 0 ise (henüz ölçülmedi) hiçbir sınıf konmaz. Sıfır dar bir ekran
değil, **ölçüm yokluğudur**; sıfırı en küçük basamak saymak açılışta bir kare boyunca yanlış
düzeni çizerdi.

CSS'in medya sorgusu kalmıyor: iki mekanizmayı yan yana bırakmak, kenar çubuğunun pencereye, rayın
kabuğa göre davrandığı bir ara hâl üretirdi.

## 2 · 1000 — ray alta iner, sütun teke düşer (fark 71, 72)

- `.chat-layout` ve `.screen-layout` dikey yığılır; ray ve panel alta iner.
- Alta inen bant alanın **%44'ü**, en çok 250px, en az 150px; **kendi içinde** kayar. Sayfanın
  bütünüyle kayması sözleşmenin tek yasağı.
- Katlı ray dikey şerit değil **tek başlık satırı** olur — yığılmış bir düzende dikey şerit hiçbir
  şey anlatmaz.
- Proje ızgarası tek sütuna düşer.
- **Bir dosya açıkken sütun ekrandan tümüyle kalkar ve okuyucu bütün alanı alır** (fark 71). Bugün
  sütun yerinde kalıyor, panel altına ekleniyor ve sayfa uzuyor.

Eşik **1100'den 1000'e** iniyor: bugünkü yığılma eşiği tasarımın verdiği sayı değildi.

"Okurken sütun kalkar" iki ekranda da aynı yolla söyleniyor: yerleşim, okunan bir şey varken bir
**değiştirici sınıf** taşıyor (`chat-layout--reading`, `screen-layout--reading`). Proje ekranı bu
deseni Madde 24'te zaten kurmuştu (`project-grid--reading`); burada bir üst kata çıkıyor. Kardeş
seçici (`:has`) ile yazmak da mümkündü — bileşen zaten neyin okunduğunu biliyor, bilmediği bir şeyi
CSS'e sordurmanın karşılığı yok.

## 3 · 780 — dolgu ve başlık küçülür, zaman kalkar (fark 73)

- Yatay dolgu **32 → 20**: `.screen`, `.chat__header`, `.chat__scroll`, `.chat__composer`,
  `.offline`, `.empty`. Hepsi aynı nefes payı; birini bırakmak düzeni kaydırırdı.
- Proje başlığı **36 → 27**.
- Sohbet satırının zaman damgası **gizlenir** — dar satırda başlık zamandan önce gelir.

**42 → 31 ayağı konusuz:** o başlık Home'undu ve Home Madde 3'te silindi. Boş hâl ekranının 34px'lik
başlığı tasarımın bu maddede konuştuğu bir şey değil; dokunulmuyor.

## 4 · 640 — kenar çubuğunun son basamağı

Genişlik 172px, dolgu 16/10. Bugün de böyle; yalnız mekanizması medya sorgusundan sınıfa geçiyor.

## 5 · Hiçbir genişlikte yatay kaydırma yok

Sözleşmenin cümlesi. Kabuk `overflow: hidden`, ray ve panel alta inince `width: auto` alıyor, uzun
metinler `overflow-wrap` ile kırılıyor. Bu maddede eklenen hiçbir kural yatay bir taşma üretmiyor —
**ve bunu gerçekten gören şey Madde 35'in 21. adımı**, jsdom değil.

## 6 · Katman denetimi

**Ön uç:** yeni `shared/useShellWidth.js` (ölçen kanca + saf `shellSteps`), `App.jsx` (sınıfı
kabuğa koyar), `ChatScreen.jsx` ve `ProjectScreen.jsx` (okuma değiştiricisi), `workspace.css`
(medya blokları sınıflara döner, üç yeni grup).

`shellSteps` **saf**: genişlik → sınıf dizesi. Eşikler orada tek yerde durur ve kancayı kurmadan
sınanır.

**Arka uç:** dokunulmuyor.

## 7 · Kabul ölçütü

1. `shellSteps` eşikleri: 1200 → boş; 1000 → dar; 780 → dar+sıkı; 640 → üçü; **0 → boş**.
2. Kabuk ölçüldükçe sınıfı değişir (ResizeObserver'ın verdiği genişlikle).
3. CSS'te **hiç `@media` yok**; kenar çubuğunun üç basamağı sınıflarla yazılı.
4. Dar basamakta yerleşim dikey yığılır; ray %44 / 250 / 150 ve kendi içinde kayar.
5. Dar basamakta katlı ray tek satır olur.
6. Dar basamakta proje ızgarası tek sütun.
7. Dar basamakta okuma açıkken sohbet ve proje sütunu **çizilmez**, okuyucu alanı doldurur.
8. Sıkı basamakta altı yüzeyin yatay dolgusu 20px, proje başlığı 27px, sohbet satırının zamanı yok.
9. Küçük basamakta kenar çubuğu 172px ve 16/10 dolgu.
10. Okuma değiştiricisi yalnız okunan bir şey varken konur.

## 8 · Risk

**Bu maddenin doğruluğu jsdom'da görülemez.** Testler ölçüyü, sınıfı ve stil sayfasının ne yazdığını
sabitler; gerçekten taşma olup olmadığını yalnız göz görür (Madde 35, adım 21). Bilinen ve kabul
edilen sınır — Madde 8'den beri her ölçü maddesinde aynı.
