# Madde 350 — Dosya listesinde yazılı Refresh, başlığın satırında · test turu

**Kaynak:** [yol haritasının 350'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (v9-2m);
kararları v9-2'nin; tasarım: `queen-agent-v3`'ün 154'ü ve 175'i. 340'ın (spinner) ve 342'nin (açık
dosyanın başlığı) üstüne kurulur.

**Kullanıcıdan gereken:** hiçbir şey. Görünüş tasarımda yazılı, madde hizalandı.

## Ne kanıtlanacak

Bugün dosya listesinin `↻`'ı listenin kutusunun içinde, kendi satırında (`file-list__bar`) sağ üstte
duruyor; üstünde `PROJECT FILES 5 ›` başlığı. Tasarımın 154'ü onu yazılı bir `Refresh` yapıyor,
açık dosyanın `Refresh`'i gibi çerçeveli (`ghost`); 175'i kutudan çıkarıp başlığın satırına, sağına
alıyor. Kutu doğrudan ilk dosyayla başlıyor. Katlanınca `Refresh` yok.

Tasarımın biçimi (`DESIGN-STANDARD.md`, *File rail and reader*; `kit.css`; `shell.js`'in `railHead`'i):

- **`rail__bar`** — başlığın satırı: `display: flex`, `align-items: center`, `gap: 8px`,
  `margin-bottom: 12px`. İçinde önce `rail__head` (katlama düğmesi, ya da genişlik yüzünden katlıyken
  `rail__head--still` etiketi), yanında `ghost file-list__refresh`. Katlıyken yalnız başlık.
- **`rail__head`** — `flex: 1`: satırı `Refresh`'le paylaşır, katlıyken satırı tek başına doldurur.
  Listenin altındaki 12'lik boşluk artık satırın, başlığın değil.
- **`file-list__refresh`** — yalnız `ghost`: tasarımda kendi kuralı yok. Bugünkü `border: none`,
  `background: transparent` ve kendi `:hover`'ı çerçeveyi siliyor; kalkar.
- **`file-list`** — ilk çocuğu ilk dosya; yüklenirken 340'ın spinner'ı.

**Proje ekranı** (`ProjectScreen.jsx`) aynı bileşeni (`RefreshFiles`) çiziyor, ve v9-2n'de kalkıyor.
Karar: onun `Refresh`'i de yazılı ve çerçeveli olur — iki ekran tek düğmeyi paylaşıyor, `↻`'ı yalnız
onun için tutmak bir bileşen ve bir kural fazlası olurdu. Yeri değişmez: kendi kutusunun sağ üstünde
kalır, çünkü o ekranın başlığı bir düğme değil ve ekran zaten gidiyor.

## Testler ne tutar

| # | Dosya | Ne |
|---|---|---|
| 1 | `FileRail.test.jsx` | `Refresh` başlığın satırında (`rail__bar`), başlığın hemen sağında |
| 2 | `FileRail.test.jsx` | `Refresh` yazılı ve çerçeveli: yazısı `Refresh`, sınıfında `ghost` |
| 3 | `FileRail.test.jsx` | Kutunun ilk satırı ilk dosya; kutuda `Refresh` yok |
| 4 | `FileRail.test.jsx` | Yüklenirken kutunun ilk çocuğu spinner'ın yeri |
| 5 | `ProjectScreen.test.jsx` | Proje ekranının `Refresh`'i de yazılı ve çerçeveli |
| 6 | `workspace.css.test.js` | `.rail__bar`: flex, ortalı, `margin-bottom: 12px` |
| 7 | `workspace.css.test.js` | `.rail__head` `flex: 1`; ne o ne `.rail__head--still` kendi `margin-bottom`'unu ya da `width: 100%`'ü taşır |
| 8 | `workspace.css.test.js` | Hiçbir kural listenin `Refresh`'inden `ghost`'un çerçevesini almaz (342'nin okuyucu testinin eşi) |

Bugün de yeşil kalanlar bekçi: *folded, there is no Refresh either* (katlıyken yok), *the open list
carries a Refresh, and pressing it asks*, *while the spinner turns, the heading and Refresh stand
where they are*, proje ekranının iki Refresh testi.

## Tutmaz

- **Görünüşün kendisi** — satırın yüksekliği, düğmenin başlıkla hizası — jsdom'da görülmez;
  tarayıcıda görülür.
- **Proje ekranında `Refresh`'in yeri** değişmez; ekran v9-2n'de kalkar.

## Bu turda yazılmayanlar

- `FileRail.jsx`, `ProjectScreen.jsx` ve `workspace.css` değişmez; uygulama turunda.
- `dist` derlenmez: birleştirirken conductor derler.

## Nasıl görülür

CLAUDE.md'deki dört satır. `npm test --prefix queen-agent/frontend` kırmızı verir: FileRail'in 1'i,
2'si, 3'ü ve 4'ü, proje ekranının 5'i, CSS'in 6'sı, 7'si ve 8'i düşer. Öteki üç süit yeşil. Kırmızı
hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m350-liste-refresh-testler-plan.md).
