# Madde 359 — Projelerde arama · test turu

**Kaynak:** [yol haritasının 359'u (v9-2p)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de, tasarımı queen-design'ın `queen-agent-v3` dalında 135, 142, 167 —
`projects/queen-agent/projects/index.html` (`frameHtml`, `bodyHtml`, `draw`), `data.js`'in `named`'i,
`BEHAVIOUR.md`'nin *All projects*'i, `DESIGN-STANDARD.md`'nin *All projects*'i ve `kit.css`'in
`.all-projects__tools` ile `.all-projects__search`'ü. Üstüne kurulduğu: 353 (`AllProjectsScreen`,
`Pinned` / `Recent`, `No projects yet.`).

**Kullanıcıdan gereken:** hiçbir şey. Koşu subagent'ta; iki yöne okunabilen kararlar aşağıda
*Kararlar*'da yazılı ve raporda Claude'a gider.

## Ne kanıtlanacak

All projects'te başlığın altında `Search projects` kutusu var ve ekran açılınca odak onda. Kutuya
yazınca liste projelerin adına göre daralıyor; eşleşme yoksa `No projects match "…".` yazıyor; kutu
boşalınca liste geri geliyor.

## Kararlar

1. **Yeri ve görünüşü tasarımın:** başlık satırının (`all-projects__head`) altında
   `all-projects__tools`, içinde `input.all-projects__search`, `placeholder` ve `aria-label`
   `Search projects`. Sekmeler aynı satıra 363'te gelir; bu madde satırı yalnız kutuyla kurar.
2. **Yalnız adda arar**, büyük/küçük harf ve aksan gözetmeden, baştaki ve sondaki boşluk atılarak —
   tasarımın `data.js`'indeki `named` gibi (*"Search ignores case and accents, as the ground this was
   ported from does (135)"*). `N chats · N files` ve zaman aranmaz.
3. **Daralan liste bölümlerini korur:** eşleşen sabitlenenler `Pinned`, ötekiler `Recent` altında,
   sunucunun sırasıyla; satırı kalmayan bölüm 353'teki gibi çizilmez.
4. **Eşleşme yoksa** `No projects match "<kırpılmış arama>".`, `.all-projects__empty` içinde —
   tasarımın cümlesi ve yeri.
5. **Hiç proje yokken** yazılan arama `No projects yet.`'ı değiştirmez: tasarımın `bodyHtml`'i önce
   "hiç proje var mı"ya bakar. Yoksa aramanın bulamadığı bir şey değil, olmayan bir şey söylenirdi.
6. **Odak, ekran açılınca kutuda.** Liste henüz yüklenirken de kutu yerinde durur (tasarımın
   `frameHtml`'i onu yüklenirken de çizer; spinner 364'ün), ve odak ekranın açıldığı anda verilir —
   liste gelince bir daha çekilmez, kullanıcı o arada başka yere geçmiş olabilir.
7. **Enter ve Esc bu maddede yok.** Tasarımın sayfasında Enter ilk eşleşeni açar, Esc kutuyu boşaltır;
   ama 359'un satırı ve *Bitti sayılır*'ı onları saymıyor (365, sohbet araması, sayıyor). Raporda
   açık nokta.
8. **Aramanın durumu ekranın kendi durumu** (FOUNDATION, Karar 4: yazarken gösterilen şey arayüzün):
   adrese yazılmaz, sunucuya gitmez. Ekrandan çıkıp dönünce kutu boş başlar.

## Testler ne tutar

### Ön uç — `AllProjectsScreen.test.jsx`

A9 değişir: *no row carries a menu and the screen carries no search yet* → *no row carries a menu
yet* (yalnız `⋯`'nin yokluğu; arama artık var). Yeni:

| # | Ne |
|---|---|
| D1 | Kutu `Search projects` adıyla (`aria-label`) ve yazısıyla (`placeholder`), `.all-projects__tools` içinde, başlık satırının hemen altında |
| D2 | Ekran açılınca odak kutuda (`document.activeElement`) |
| D3 | Yüklenirken de kutu duruyor ve odak onda |
| D4 | `night` yazınca yalnız `Night market` kalıyor, `Pinned` bölümü gidiyor |
| D5 | `HARBOUR` `Harbour at dusk`'ı, `cafe` `Café noir`'ı buluyor; `  pier  ` `Old pier`'ı buluyor |
| D6 | Yalnız ad: `chats` ya da `2h` hiçbir satırı bulmuyor |
| D7 | Eşleşme yoksa `No projects match "zzz".` (kırpılmış), satır ve `No projects yet.` yok |
| D8 | Kutu boşalınca bütün liste ve iki bölüm geri geliyor |
| D9 | Hiç proje yokken arama yazılsa da `No projects yet.` |

### Ön uç — `workspace.css.test.js`

| # | Ne |
|---|---|
| C7 | `.all-projects__tools`: flex, `margin: 0 0 28px` |
| C8 | `.all-projects__search`: `flex: 1`, `border: 1px solid var(--line)`, `border-radius: var(--radius-control)`, `padding: 8px 12px`, `background: var(--surface)`, `font-size: 13.5px` |

Kutu kendi odak çizgisini yazmaz; bunu `app.css.test.js`'in *no surface writes the ring* testi zaten
tutuyor.

## Tutmadıkları

- Enter ve Esc (Karar 7), `Archived` sekmesi ve sayıları (363), spinner ve `Couldn't load projects.`
  (364), satırın `⋯`'si (360).
- `dist` — Claude derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` D1–D9, C7 ve C8'de
kırmızı; öteki üç süit yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m359-projelerde-arama-testler-plan.md).
