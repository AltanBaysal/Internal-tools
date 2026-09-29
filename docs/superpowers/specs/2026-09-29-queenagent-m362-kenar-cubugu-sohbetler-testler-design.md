# Madde 362 — Kenar çubuğunda yalnız New chat ve sohbetler · test turu

**Kaynak:** [yol haritasının 362'si (v9-2s)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de, tasarımı queen-design'ın `queen-agent-v3` dalında 151 (*solda ilk göze çarpan dolu `+ New
chat`, altında projenin sohbetleri*), 152 (*projenin adı tek bir yerde, çubukta*) ve 168 (*projeler
listesi ve son sohbetler kenar çubuğundan gider*) — `projects/queen-agent/shell.js` (`sidebar`,
`chatRow`), `BEHAVIOUR.md`'nin *Sidebar*'ı, `DESIGN-STANDARD.md`'nin *Sidebar*'ı ve `kit.css`'in
`.sidebar__new-chat`, `.sidebar__chats`, `.sidebar__chat`, `.sidebar__empty` kuralları. Üstüne
kurulduğu: 351 (katlama: panel ikonu en altta, katlanınca `+` ve panel ikonu), 353 (All projects `/`,
`OpenProject`), 360 (kenar çubuğunun proje satırları `⋯`'siz, yalın düğme), 361 (`+` ad sorma
ekranına, `/new`, gider).

**Kullanıcıdan gereken:** hiçbir şey. Koşu subagent'ta; iki yöne okunabilen kararlar aşağıda
*Kararlar*'da yazılı ve raporda Claude'a gider.

## Ne kanıtlanacak

Proje açıkken kenar çubuğu dolu `+ New chat`'le başlar; altında, üstünde etiket olmadan, projenin
bütün sohbetleri — sekiz sınırı yok —, açık olan işaretli; sohbet yoksa `No chats yet.` En altta
351'in katlama satırı. `Projects` etiketi, proje satırları, yanındaki `+` ve `Recent chats` yok.
Katlanınca sütunda yalnız `+` ve panel ikonu.

## Kararlar

1. **Kenar çubuğu yalnız bir proje açıkken çizilir, ve artık bunu bilmez.** App onu yalnız `project`
   ve `chat` görünümlerinde çiziyor (353), ikisinde de adreste proje var. `activeProjectId` yalnız
   `New chat`'i ve katlanmış `+`'yı "proje yoksa" gizlemek, ve proje satırını işaretlemek için
   vardı; ikisi de gidiyor. Tasarımın `shell.sidebar`'ı proje yokken yalnız katlamayı çiziyor, ama
   uygulamada o hâl yok: kenar çubuğu All projects'te ve ad sorma ekranında hiç çizilmiyor. Yani
   *no project selected* üç test, tuttukları durum kalmadığı için kalkar.
2. **Kenar çubuğunun prop'ları:** `chats`, `activeChatId`, `onNewChat`, `onOpenChat`, `collapsed`,
   `onToggle`. `projects`, `activeProjectId`, `onNewProject`, `onOpenProject` gider.
3. **Sıra tasarımın:** `aside.sidebar`'ın çocukları tam olarak `sidebar__new-chat`, `sidebar__chats`,
   `sidebar__foot`. `Search chats` 365'in; bu parçada yok (bugünkü *no search control* testi
   durur).
4. **Etiket yok** (`DESIGN-STANDARD.md`: *no label above them*): `Recent chats` de, `Projects` de
   gider. `.sidebar__chats`'in üst çizgisi tasarımda duruyor; kalır.
5. **Bütün sohbetler** (`BEHAVIOUR.md`: *no eight-chat cap*): sunucunun verdiği sırayla, hepsi;
   liste kendi içinde kayar (`.sidebar__chats`, bugünkü kural).
6. **Boş hâl:** sohbet yoksa `.sidebar__chats`'in içinde `.sidebar__empty`, yazısı `No chats yet.`
   Tasarımın kuralı: `padding: 10px 12px`, `font-size: 13px`, `color: var(--muted)`. Sohbet varken
   cümle yok.
7. **Liste yüklenirken ve okunamayınca ayrı bir hâl yok.** `useList`'in `loading`'i yalnız ilk
   açılışta doğru — All projects'ten bir projeye girilince `false` kalıyor (`APP-BUGS.md` 31) —, ve
   tasarım kenar çubuğu için yükleme ya da hata çizmiyor. Cümle, elde tutulan liste boşken çıkar;
   bu yüzden ilk cevap gelene kadar kısa bir an, ve okuma başarısız olursa `No chats yet.` görünebilir.
   İki yöne okunabilir — raporda.
8. **Projelerin yanındaki `+` ile ad sorma ekranının "geldiği yer"i de gider.** 361'in `namingFrom`'u
   `/new`'e nereden gelindiğini tutuyordu, çünkü iki yol vardı: All projects ve kenar çubuğunun
   `+`'sı. `+` gidince tek yol All projects; `Cancel` ve Esc her zaman `/`'e döner. Davranış
   değişmiyor, ölü bir durum kalkıyor — bugünkü *Cancel*/*Escape* testleri (`/`'e dönüyor) aynen
   geçer; *the sidebar's + asks for the name too…* testi, tuttuğu yol kalmadığı için kalkar.
9. **Proje satırının CSS'i onunla gider:** `.sidebar__projects`, `.sidebar__head`, `.sidebar__label`,
   `.sidebar__add`, `.sidebar__row-open`, `.sidebar__row--active`, `.sidebar__row-name`,
   `.sidebar__row-badge` (ve `--none`), `.dot`. Hiçbirini başka yüzey kullanmıyor.

## Testler ne tutar

### Ön uç — `Sidebar.test.jsx`

**Yeni ya da yeniden yazılan:**

| # | Ne |
|---|---|
| S1 | Kenar çubuğu `+ New chat`'le başlıyor: ilk çocuk `.sidebar__new-chat`, yazısı `+New chat` |
| S2 | Çocuklar sırasıyla `sidebar__new-chat`, `sidebar__chats`, `sidebar__foot` — başka satır yok |
| S3 | Proje listesi yok: `Projects`, `Recent chats`, `New project` düğmesi, `.sidebar__row-open`, `.dot` yok |
| S4 | Sohbetler listeleniyor, açık olan `sidebar__chat--active`; üstlerinde etiket yok |
| S5 | Projenin bütün sohbetleri: 12 sohbetin 12'si de satır |
| S6 | Sohbet yoksa `.sidebar__chats`'in içinde `.sidebar__empty` `No chats yet.` |
| S7 | Sohbet varken `No chats yet.` yok |
| S8 | Katlanınca sohbetler yok, ve sütunda yalnız iki düğme: `New chat` (`+`) ve `Show the sidebar` |

**Kalkan:** *with no project selected only the projects remain*, *folded with no project open, the
fold stands alone*, *New chat is hidden rather than disabled when nothing is selected* (Karar 1);
*every project dot is the same tone*, *a project with no files still holds the badge's place*, *a
project with files shows the count plainly*, *projects are listed by name*, *clicking a project asks
to open it*, *the open project is the marked row*, *no project row carries a ⋯* (satır yok; S3
tutar); *at most eight chats are listed* (yerine S5); *folded, the projects and chats are gone*
(yerine S8); *the project's chats are listed and the open one is marked* (yerine S4).

Kalan testler `projects` ve `activeProjectId` geçmeden render eder.

### Ön uç — `App.test.jsx`

| # | Ne |
|---|---|
| B1 | `/p/p1/c/c1`'de, iki projeli sunucuda: kenar çubuğunda projenin iki sohbeti var; öteki projenin adı sayfada hiç yok; `Projects` ve `New project` yok |
| B2 | Sohbeti olmayan projenin taslağında (`/p/p1/c/new`) kenar çubuğu `No chats yet.` diyor |

**Kalkan:** *the sidebar's + asks for the name too, and Cancel goes back to the chat it came from*
(Karar 8).

**Değişen arama:** kenar çubuğunun açık olduğunu `Projects` yazısından okuyan dört katlama testi
(*the sidebar folds away…*, *Ctrl + . folds…*, *Ctrl + . works while typing…*, *a full stop typed
alone…*) onu `.sidebar__chat` satırındaki `Write the intro`'dan okur. *inside a project no ⋯ stands
anywhere* sayfanın oturduğunu `.sidebar__row-name` yerine çubuğun `.bar__project`'inden bekler.
*nothing is asked of a workspace-wide chat address*'in yorumu `Recent chats`'i anmaz.

### Ön uç — CSS kilitleri (`workspace.css.test.js`)

- C1 — proje listesi her adıyla gitti: Karar 9'daki sınıfların hiçbiri `workspace.css`'te yok,
  `.dot {` de.
- C2 — `.sidebar__empty`: `padding: 10px 12px`, `font-size: 13px`, `color: var(--muted)`.
- C3 — `.sidebar__new-chat` dolu: `background: var(--accent)`.
- *every control rounds by the same variable* `.sidebar__row-open` satırını bırakır.

## Tutmadıkları

- `Search chats` ve katlanmış sütundaki arama ikonu (365).
- Sohbet listesinin yüklenirken ve okunamayınca hâli (Karar 7).
- `dist` — koşuyu yöneten derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` S1–S8'de (S7 dışında —
bugün de `No chats yet.` yok), B1–B2'de, C1–C2'de kırmızı — C3 bugünkü kuralı kilitler, yeşil —;
öteki üç süit yeşil. Kırmızı hâliyle
commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m362-kenar-cubugu-sohbetler-testler-plan.md).
