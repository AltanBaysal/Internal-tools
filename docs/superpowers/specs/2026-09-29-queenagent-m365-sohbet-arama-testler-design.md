# Madde 365 — Search chats · test turu

**Kaynak:** [yol haritasının 365'i (v9-2v)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de, tasarımı queen-design'ın `queen-agent-v3` dalında 151 (*`+ New chat`'in altında `Search
chats`, projenin sohbetlerinde arar*), 168 (*`+ New chat`, `Search chats`, projenin sohbetleri*) ve
174 (*katlanınca ikon sütunu: `+` ve arama; arama ikonu açıp arama kutusuna odaklanır*) —
`projects/queen-agent/shell.js` (`matchingChats`, `sidebar`, `answerSidebar`), `BEHAVIOUR.md`'nin
*Sidebar*'ı, `DESIGN-STANDARD.md`'nin *Sidebar* ve *Small marks*'ı, `kit.css`'in `.sidebar__search`,
`.sidebar__search-toggle`, `.sidebar__search-icon` kuralları. Üstüne kurulduğu: 362 (kenar çubuğu
`+ New chat` ve sohbetler), 351 (katlanmış ikon sütunu, `Ctrl + .`, App'in tek dinleyicisi), 359 (All
projects'in araması: büyük-küçük harf ve aksan saymayan kural, `No projects match "…".`), 355
(sohbet açılırken kapalı yazma kutusu; Composer `forwardRef`).

**Kullanıcıdan gereken:** hiçbir şey. Koşu subagent'ta; iki yöne okunabilen kararlar aşağıda
*Kararlar*'da yazılı ve raporda Claude'a gider.

## Ne kanıtlanacak

Proje açıkken `+ New chat`'in altında `Search chats` kutusu durur. Yazınca sohbet listesi, adında
yazılan geçen sohbetlere daralır — büyük-küçük harf ve aksan sayılmaz, baştaki ve sondaki boşluk
da. Eşleşme yoksa listenin yerinde `No chats match "…".` Enter ilk eşleşen sohbeti açar ve kaydı
gelince odak o sohbetin yazma kutusundadır. Esc kutuyu boşaltır. Katlanınca ikon sütununda `+`'nın
altında bir arama ikonu: basınca kenar çubuğu açılır ve odak arama kutusuna gider.

## Kararlar

1. **Sıra tasarımın:** `aside.sidebar`'ın çocukları tam olarak `sidebar__new-chat`,
   `sidebar__search`, `sidebar__chats`, `sidebar__foot`. Kutu bir `input type="text"`, placeholder'ı
   ve `aria-label`'ı `Search chats`, `autocomplete="off"`. Proje açılınca odak almaz: tasarım
   almıyor, ve açılışta odağı alan yazma kutusu değil, hiçbir şey.
2. **Kural bir tane:** 359'un `fold()`'u — büyük-küçük harf ve aksan sayılmaz, sorgu kırpılır —
   iki yerde yazılmaz. Kural `features/workspace/matches.js`'e taşınır, `matches(text, query)`; All
   projects ve kenar çubuğu onu import eder. Kendi testi (`matches.test.js`) kuralı tutar; All
   projects'in bugünkü arama testleri olduğu gibi geçer.
3. **Boş cümle tasarımın:** sorgu (kırpılmış) doluysa ve eşleşme yoksa `.sidebar__chats`'in içinde
   `.sidebar__empty` `No chats match "<kırpılmış sorgu>".` Sorgu boşsa ve sohbet yoksa bugünkü `No
   chats yet.` Sohbeti hiç olmayan projede bir şey yazılırsa da `No chats match "…".` — tasarımın
   `sidebar()`'ı önce sorguya bakıyor. All projects burada farklı (*No projects yet.* önce); kenar
   çubuğu kendi tasarımını izler.
4. **Enter** kutuda ilk eşleşeni açar: `onOpenChat(id, { focusReply: true })`. Sorgu boşsa ilk
   eşleşen listenin ilk sohbeti — tasarımda boş sorgu bütün sohbetler, ve Enter ilkini açar. Eşleşme
   yoksa hiçbir şey olmaz. Listenin sırası sunucunun — en son kullanılan önce —, yani tasarımın 151'i
   ile yol haritasının sözü (*en son açılan* / *ilk eşleşme*) aynı sohbeti açar.
5. **Odak kaydı gelince verilir.** Bir sohbet açılırken yazma kutusu kapalıdır ve kayıt gelince
   yeniden kurulur (355); Enter anında verilen odak kaybolur. App, Enter'in açtığı sohbeti tutar;
   ChatScreen'e `focusReply` yalnız ekrandaki kayıt o sohbetinki olunca doğru gider, ChatScreen yazma
   kutusuna odaklanır ve `onReplyFocused()` der, App de tuttuğunu bırakır. Enter zaten açık olan
   sohbeti açarsa kayıt eldedir, odak hemen gider. **Tıklanarak açılan sohbet odağı taşımaz** —
   tasarım yalnız Enter'de taşıyor.
6. **Esc** kutuda kutuyu boşaltır ve liste bütün hâline döner. Tuşu alan kutunun kendisidir —
   `EditMessage`'in ve satırın yeniden adlandırma kutusunun Esc'i gibi —; App'in tek dinleyicisi
   değişmez.
7. **Sorgu kenar çubuğunundur**, App'in değil: gösterilen, yazılırken ekranın işi (FOUNDATION,
   Karar 4), sunucuya ve adrese gitmez. Kenar çubuğu sohbetler arasında gezilirken ve katlanıp
   açılırken yerinde kaldığı için sorgu da kalır; All projects'e çıkınca kenar çubuğu gider, sorgu da.
8. **Katlanınca** sütunun düğmeleri sırasıyla `New chat`, `Search chats`, `Show the sidebar`. Arama
   düğmesi `sidebar__search-toggle`, içinde CSS'le çizilmiş `sidebar__search-icon`, yazısı yok.
   Basınca `onToggle()` çağrılır; kenar çubuğu açık çizilince odak arama kutusundadır. Katlama
   düğmesiyle ya da `Ctrl + .` ile açılınca odak kutuya gitmez.
9. **CSS tasarımın `kit.css`'inden:** `.sidebar__search` — `width: 100%`, `border: 1px solid
   var(--line)`, `background: var(--surface)`, `border-radius: var(--radius-control)`, `padding: 8px
   10px`, `font-size: 13px`, `color: var(--ink)`. `.sidebar__search-toggle` katlama düğmesiyle tek
   kural ve tek hover (`30 × 30`, saydam, üstüne gelince `#e5dfd5`). `.sidebar__search-icon` `12 ×
   12`, `1.5px solid var(--ink)` çember; sapı `::after`, `5px`, `rotate(45deg)`.
10. **Sunucu değişmez:** arama tarayıcıda, elde tutulan listede. *nothing asks the server to search*
    ve *⌘K is bound to nothing* olduğu gibi geçer.

## Testler ne tutar

### Ön uç — `matches.test.js` (yeni)

| # | Ne |
|---|---|
| M1 | Boş ya da boşluktan ibaret sorgu her ada uyar |
| M2 | Büyük-küçük harf sayılmaz: `HARBOUR` *Harbour at dusk*'a uyar |
| M3 | Aksan sayılmaz, iki yönde de: `cafe` *Café noir*'a, `café` *Cafe*'ye uyar |
| M4 | Sorgunun baştaki ve sondaki boşluğu sayılmaz; adın içinde geçmeyen uymaz |

### Ön uç — `Sidebar.test.jsx`

**Yeni ya da yeniden yazılan:**

| # | Ne |
|---|---|
| S1 | Çocuklar sırasıyla `sidebar__new-chat`, `sidebar__search`, `sidebar__chats`, `sidebar__foot` (bugünkü *under New chat stand the chats…* testi) |
| S2 | Kutu `Search chats` adlı bir textbox: placeholder `Search chats`, `autocomplete` `off`, açılışta odakta değil |
| S3 | Yazınca liste daralır: `missing` → yalnız *Missing values*; büyük-küçük harf ve aksan sayılmaz (`CAFE` → *Café notes*) |
| S4 | Eşleşme yoksa `.sidebar__chats`'in içinde `.sidebar__empty` `No chats match "zebra".` — kırpılmış sorguyla; `No chats yet.` yok |
| S5 | Sohbeti olmayan projede yazılınca da `No chats match "…".` |
| S6 | Enter ilk eşleşeni açmayı ister: `onOpenChat("c2", { focusReply: true })` |
| S7 | Boş kutuda Enter listenin ilk sohbetini açmayı ister |
| S8 | Eşleşme yokken Enter hiçbir şey istemez |
| S9 | Esc kutuyu boşaltır, liste bütün döner |
| S10 | Satıra tıklamak hâlâ yalnız id'yle ister: `onOpenChat("c1")` — odak isteği yok (bugünkü *clicking a chat asks to open it* testi, `toHaveBeenCalledWith("c1")` tam argümanla kalır) |
| S11 | Katlanınca düğmeler sırasıyla `New chat`, `Search chats`, `Show the sidebar` (bugünkü *folded, the chats are gone…* testi) |
| S12 | Katlanmış arama düğmesi: sınıfı `sidebar__search-toggle`, içinde `.sidebar__search-icon`, yazısı boş |
| S13 | Arama düğmesi açmayı ister (`onToggle`), ve açık çizilince odak arama kutusunda |
| S14 | Katlama düğmesiyle açılınca odak arama kutusunda değil |
| S15 | Katlanıp açılınca yazılan sorgu ve daralmış liste yerinde |

**Kalkan:** *the sidebar carries no search control* — tuttuğu hâl bu maddeyle bitiyor. ⌘K'nın
yokluğunu App'in *⌘K is bound to nothing*'i tutmaya devam eder.

### Ön uç — `ChatScreen.test.jsx`

| # | Ne |
|---|---|
| C1 | `focusReply` ile çizilen ekranda odak yazma kutusunda (`Reply...`), ve `onReplyFocused` bir kez çağrılmış |
| C2 | `focusReply` olmadan odak yazma kutusunda değil, `onReplyFocused` çağrılmamış |

### Ön uç — `App.test.jsx`

| # | Ne |
|---|---|
| A1 | `/p/p1/c/c1`'de, iki sohbet (*Write the intro*, *Missing values*): kutuya `missing` yazılınca kenar çubuğunda yalnız *Missing values*; Enter adresi `/p/p1/c/c2` yapar, ve kaydı gelince odak açılmış `Reply...` kutusunda |
| A2 | Aynı sunucuda satıra tıklayarak açılan sohbet odağı yazma kutusuna taşımaz |
| A3 | Katlanmış sütunun `Search chats` düğmesi kenar çubuğunu açar ve odak arama kutusunda |

### Ön uç — CSS kilitleri (`workspace.css.test.js`)

- K1 — `.sidebar__search`: Karar 9'un yedi değeri.
- K2 — arama düğmesi katlama düğmesiyle tek kural: `.sidebar__search-toggle,\n.sidebar__fold {` ve
  `.sidebar__search-toggle:hover,\n.sidebar__fold:hover {`. Bugünkü *the fold is a square button…*
  testi aynı kuralı okumaya devam eder.
- K3 — `.sidebar__search-icon`: `width: 12px`, `height: 12px`, `border: 1.5px solid var(--ink)`,
  `border-radius: 50%`; `::after`: `width: 5px`, `rotate(45deg)`.

## Tutmadıkları

- Esc'in kutuda App'in sırasıyla birlikte çalışması (açık dosya da kapanır mı): App'in dinleyicisi
  değişmiyor; `EditMessage`'in Esc'i bugün de aynı yolda. Raporda.
- `dist` — koşuyu yöneten derler.
- Tarayıcıda görünüş — koşuyu yöneten Playwright'la bakar.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend`'de M1–M4 (modül yok),
S1–S9, S11–S15, C1, A1, A3, K1–K3 kırmızı; S10, C2, A2 bugünkü davranışı tutar, yeşil. Öteki üç
süit yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m365-sohbet-arama-testler-plan.md).
