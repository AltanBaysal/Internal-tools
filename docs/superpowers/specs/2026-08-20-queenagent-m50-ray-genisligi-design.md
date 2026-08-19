# Madde 50 — Sağ ray sürüklenerek ayarlanır · Tasarım

**Madde:** [v3 yol haritası Madde 50](../plans/2026-08-18-queenagent-v3-roadmap.md) ·
**Kaynak:** [test bulguları, bulgu 2](../research/2026-08-18-queenagent-test-bulgulari.md)
**Kullanıcı kararı:** 19 Ağustos — "ray aslında alta inmesin hep sağda kalmalı VS Code gibi düşün;
sürükle, bir miktarın altına gelince direkt kapansın".

---

## Ne değişiyor

Bugün rayın genişliği stylesheet'te sabit (320px, okurken 560px) ve pencere 1000px'in altına
inince ray sohbetin **altına** iniyor (v2 Madde 33). Kullanıcı VS Code davranışını istedi:

- ray **her genişlikte sağda** kalır — alta inme kuralı düşer,
- sol kenarından sürüklenerek genişler/daralır, seçilen genişlik oturumca kalır,
- en az genişliğinin altına sürüklenirse kapanır,
- pencere ikisine birden yetmeyince de kapanır.

## Üç sayı ve nereden geldikleri

| Sayı | Ne | Neden bu |
|---|---|---|
| `DEFAULT_RAIL_WIDTH` | 320px | Bugünkü genişlik; hiçbir şey sürüklenmemişken görülen. Stylesheet de aynı sayıyı taşır (bir şey söylenmediğinde geçerli olan), ve bir kilit testi ikisini birbirine bağlar — iki kopya, birbirini tutmuyorsa yalandır. |
| `MIN_RAIL_WIDTH` | 220px | Rayın 18px'lik iki yan boşluğu düşünce satıra 184px kalır: dosya adı ve altındaki `project file · 2h ago` satırı hâlâ okunur. Altında satır kendi kendini keser. |
| `MAX_RAIL_WIDTH` | 560px | Okuyucu açıkken rayın çizildiği genişlik. Liste, uğruna yer açılan belgeden geniş olamaz. |
| `RAIL_CLOSES_BELOW` | 860px | Kabuk bu genişlikteyken kenar çubuğu 226px (narrow adımı), rayın en azı 220px; sohbete 414px kalır. Altında sohbet, yanındaki raydan dar olur — o zaman ray gitmelidir. |

Üçü tek dosyada (`railWidth.js`), stylesheet'te değil: ikisi de çalışma anında hesaplanıyor.

## Kapanmanın tek kuralı, iki sebebi

Kapalılık **türetilir**, ayrıca yazılmaz:

```
folded = kullanıcı katladı  ||  kabuk ikisine birden dar
```

Böylece pencere daralınca ray gider, genişleyince kullanıcının bıraktığı hâl **aynen** geri gelir.
Daralmanın kullanıcının kararını üzerine yazması, sonra da genişleyince kimsenin katlamadığı katlı
bir ray bırakması olurdu.

Dar kabukta şeridin başlığı **denetim değil etikettir** — açılacak yer yokken açan bir düğme
yalandır. Ray okuyucu gösterirken başlığın zaten etiket olması aynı kuralın aynı sebebi.

## Kim ölçer, kim karar verir

Ray sürüklemeyi ölçer ve **istenen** genişliği bildirir; `App` karar verir. Sebep: kapalılık zaten
`App`'in durumu (`railCollapsed`), ve "en azının altında kapanır" kuralı kapalılık hakkındadır.
Ray'ın aritmetiği, App'in kararı.

Karar tek saf fonksiyonda: `railWidthFor(desired)` ya bir sayı verir ya da `null` — *bu bir genişlik
değil, kapanmadır*.

## Sürükleme neden fare olayı

`mousedown` + `window`'a bağlanan `mousemove`/`mouseup`. Pointer olayları dokunmatiği de kapsardı ama
jsdom'da `setPointerCapture` yok; bu bir masaüstü iç aracı ve fare olayları jsdom'da eksiksiz.

## Tutamağın olmadığı iki hâl

- **Katlıyken** — 46px'lik şerit sürüklenmek için değil, basılmak için orada.
- **Okurken** — genişlik o an belgenin, kullanıcının değil. Okuyucu kapanınca sürüklenen genişlik
  geri gelir.

## Düşen CSS kuralları

`.app-shell--narrow` altındaki şu kurallardan **sohbet rayına ait olanlar** düşer, proje ekranının
paneline ait olanlar **kalır** — bu madde proje ekranına dokunmuyor:

- `.chat-layout` sütuna dönmez (`.screen-layout` döner),
- `.rail` / `.rail--open` tavan, üst çizgi ve `width: auto` almaz (`.panel` alır),
- katlı rayın yatay satır hâli tümüyle gider — şerit her genişlikte dikeydir,
- okurken `.rail--open`'ın tavanı kalkma kuralı gider (`.panel`'inki kalır).

`.app-shell--narrow .chat-layout--reading .chat { display: none }` **kalır**: dar kabukta 560'lık bir
okuyucunun yanında sohbete anlamlı yer kalmıyor, ve bu kural rayın nerede durduğundan bağımsız.

## Bilerek yapılmayan

- Kaydetme yok: genişlik oturum boyu yaşar, `railCollapsed` gibi. Diske yazmak ayrı bir karar.
- Klavye ile boyutlandırma yok. Tutamak `role="separator"` taşır, ama ok tuşlarıyla genişletme bu
  maddenin isteği değil.
- Dokunmatik sürükleme yok — yukarıdaki sebep.
