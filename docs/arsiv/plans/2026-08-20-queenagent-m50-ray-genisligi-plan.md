# Madde 50 — Sağ ray sürüklenerek ayarlanır · Plan (iki tur)

**Tasarım:** [2026-08-20-queenagent-m50-ray-genisligi-design.md](../specs/2026-08-20-queenagent-m50-ray-genisligi-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Tur 1 — Testler (kırmızı commit)

### Önce: kalkan kuralın testlerini emekliye ayır

Dört test v2 Madde 33'ün "ray sohbetin altına iner" kuralını çiviliyor. Kural düştüğü için testleri
de düşer — ama kırmızıyı gizlememek için **kendi commit'inde**, uygulamadan önce:

`workspace.css.test.js`:

1. `a narrow shell scrolls its regions, not the layout` — `.chat-layout` ve `.rail` gruplarını
   okuyor. Yeniden yazılır: yalnız `.screen-layout` ve `.panel`.
2. `reading in a narrow shell takes the whole area rather than lengthening the page` — grup
   `.chat-layout--reading .rail--open` ile başlıyor; yalnız `.panel` kalır. Sohbetin gizlenmesi
   (`display: none`) **kalır**.
3. `under the chat a folded rail is a row, not a column` — **silinir**. Şerit her genişlikte dikey.
4. `the layout and the sidebar now step at the same widths` — `.app-shell--narrow .chat-layout,`
   grubunun varlığına dayanıyor; artık böyle bir grup yok. `1100px`'in geri gelmediğini tutan yarısı
   kalır, kalkan yarısı yerini yeni kilide bırakır.

### Yeni testler

`railWidth.test.js` *(yeni dosya — saf karar)*:

5. iki sınırın arasındaki genişlik olduğu gibi kalır
6. en genişten geniş istenen, en genişte tutulur
7. en dardan dar istenen bir genişlik değildir — `null`, yani kapanma
8. `railFitsIn`: 860 ve üstü ikisine birden yeter, altı yetmez; **ölçüm yokken (0) yeter**, çünkü
   ölçülmemiş bir kabuk dar bir kabuk değildir

`FileRail.test.jsx`:

9. ray verilen genişlikte çizilir (`style.width`)
10. rayın sol kenarında sürüklenecek bir tutamak var (`role="separator"`)
11. tutamağı sola çekmek daha geniş bir ray ister — bildirilen sayı, başlangıç + kat edilen mesafe
12. katlı rayda tutamak yok
13. belge okunurken tutamak yok

`ChatScreen.test.jsx`:

14. genişlik ve tutamağın bildirdiği ray'a kadar iniyor

`App.test.jsx`:

15. tutamağı en azın altına çekmek rayı katlar — sunucuya bir şey gitmez, bu ekranın kendi durumu

`workspace.css.test.js` *(yeni kilitler)*:

16. sohbetin rayı hiçbir adımda sütuna inmez — `.app-shell--narrow` altında `.chat-layout` ya da
    `.rail` adına bir kural kalmamıştır
17. tutamak rayın sol kenarında ve imleci `col-resize`

### Beklenen kırmızı

5-17 kırmızı. 1, 2, 4 yeniden yazıldıkları anda kırmızı olur (CSS henüz eski). 12 ve 13 bugün de
geçer — tutamak hiç yok — ama kuralı tutuyorlar, kalırlar.

---

## Tur 2 — Uygulama (yeşil commit)

- **`railWidth.js`** *(yeni)* — üç sayı, `railWidthFor(desired)`, `railFitsIn(shellWidth)`.
- **`useShellWidth.js`** — ölçtüğü genişliği de döndürür. Adım sınıflarını zaten ondan üretiyor.
- **`App.jsx`** — `railWidth` durumu (320'den başlar); `resizeRail(desired)` `railWidthFor`'a sorar,
  `null` gelirse katlar; çizilen kapalılık `railCollapsed || !railFitsIn(width)` olarak türetilir.
- **`ChatScreen.jsx`** — `railWidth` ve `onResizeRail`'i raya geçirir.
- **`FileRail.jsx`** — açık liste hâlinde tutamağı çizer, `mousedown` ile `window`'a `mousemove` /
  `mouseup` bağlar, istenen genişliği bildirir. Katlıyken ve okurken tutamak yok. Şeridin başlığı,
  açılacak yer yokken etiket olur.
- **`workspace.css`** — düşen kurallar silinir, `.rail__grip` eklenir.

---

## Kapanış denetimi

- Proje ekranının dar-kabuk davranışı değişmedi: `.screen-layout` ve `.panel` kuralları duruyor.
- Dar kabukta ray katlı görünür ama `railCollapsed` yazılmamıştır — pencere genişleyince kullanıcının
  bıraktığı hâl geri gelir.
