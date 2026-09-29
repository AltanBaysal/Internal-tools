# Madde 365 — Search chats · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m365-sohbet-arama-testler-design.md) ve kırmızı
commit'in testleri. Bu tur o testlerin anlattığını yapar, fazlasını değil. FOUNDATION ve
CODE-STANDARD okundu: arama ekranın işi (Karar 4 — *what is shown while typing* UI'ın), sunucuya
dokunulmaz; kod `features/workspace/`'te kalır, `shared/`'a bir şey girmez — kuralı yalnız bu
feature kullanıyor.

## Yaklaşımlar — odak hangi yoldan yazma kutusuna gider

1. **App tutar, ChatScreen verir (seçilen).** App Enter'in açtığı sohbetin id'sini tutar
   (`replyFor`); ChatScreen'e `focusReply` yalnız ekrandaki kaydın id'si o olunca doğru gider.
   ChatScreen bir effect'le Composer'ın `focus()`'unu çağırır ve `onReplyFocused()` der; App
   `replyFor`'u bırakır. Kararı veren tek yer App — adresi ve sohbeti bilen o.
2. *Composer'a hep `autoFocus`:* her açılışta — tıklamada da, sayfa yüklenirken de — odak kutuya
   gider; A2'yi kırar ve tasarımın söylemediğini yapar.
3. *Yalnız bir boolean:* Enter anında `focusReply` doğru olunca, adresin değiştiği ilk render'da
   ekranda hâlâ eski sohbetin kaydı var (useChat'in effect'i henüz boşaltmadı); odak eski kutuya
   gider, kutu kayıt okunurken kapanıp yeniden kurulunca kaybolur. Id karşılaştırması bunu önler.

## Parçalar

### `features/workspace/matches.js` (yeni)

359'un `fold()`'u buraya taşınır; tek dışa açılan `matches(text, query)`:
`fold(text).includes(fold(query.trim()))`. Boş sorgu her şeye uyar.

### `AllProjectsScreen.jsx`

`fold` gider; süzme `matches(project.name, query)`. `asked` yalnız cümle için kalır.

### `Sidebar.jsx`

- `query` state'i kenar çubuğunun; katlanınca da bileşen yerinde kaldığı için sorgu kalır.
- Açık: `+ New chat`, `input.sidebar__search` (`type="text"`, placeholder ve `aria-label` `Search
  chats`, `autoComplete="off"`), `.sidebar__chats`, katlama satırı. Liste
  `chats.filter((chat) => matches(chat.title, query))`. Boşsa `.sidebar__empty`: kırpılmış sorgu
  doluysa `No chats match "<sorgu>".`, değilse `No chats yet.`
- Kutunun tuşları: Enter → listenin ilki varsa `onOpenChat(id, { focusReply: true })`; Escape →
  `setQuery("")`. Esc'i kutu alır, `EditMessage` gibi; App'in dinleyicisi değişmez.
- Katlı: `+`, sonra `button.sidebar__search-toggle` (`aria-label` `Search chats`, içinde
  `span.sidebar__search-icon`), sonra katlama satırı. Arama düğmesi bir ref'e (`seeking`) *kutu
  istendi* yazar ve `onToggle()` der. `collapsed`'a bağlı bir effect, açık çizildiğinde ve istek
  varsa isteği siler ve kutuya odaklanır (`preventScroll`, tasarımın 155'i). Katlama düğmesi ve
  `Ctrl + .` isteği yazmaz.

### `Composer.jsx`

Textarea'ya bir ref; `useImperativeHandle` `submit`'in yanına `focus`'u koyar
(`focus({ preventScroll: true })`).

### `ChatScreen.jsx`

İki yeni prop: `focusReply`, `onReplyFocused`. Erken dönüşten (`missing`) önce bir effect:
`focusReply` doğruysa `box.current.focus()` ve `onReplyFocused()`.

### `App.jsx`

- `const [replyFor, setReplyFor] = useState(null)`.
- Kenar çubuğunun `onOpenChat(chatId, how)`'u: `setReplyFor(how?.focusReply ? chatId : null)`,
  sonra `openChat`. Tıklama isteği siler — başarısız bir açılıştan kalan istek sonraki açılışa
  binmesin.
- ChatScreen'e `focusReply={replyFor !== null && chat.chat?.id === replyFor}` ve
  `onReplyFocused={() => setReplyFor(null)}`.

### `workspace.css`

- `.sidebar__search` — `kit.css`'teki gibi: `width: 100%`, `border: 1px solid var(--line)`,
  `background: var(--surface)`, `border-radius: var(--radius-control)`, `padding: 8px 10px`,
  `font-family: inherit`, `font-size: 13px`, `color: var(--ink)`. Odak halkası `app.css`'in.
- `.sidebar__fold` kuralı ve hover'ı `.sidebar__search-toggle,\n.sidebar__fold` olur.
- `.sidebar__search-icon` (`12 × 12`, `1.5px solid var(--ink)`, `border-radius: 50%`,
  `position: relative`, `display: block`, `box-sizing: border-box`) ve `::after` sapı (`right: -4px`,
  `bottom: -1px`, `width: 5px`, `height: 0`, `border-top: 1.5px solid var(--ink)`,
  `transform: rotate(45deg)`).
- `.sidebar--collapsed` ve `Sidebar.jsx`'in katlama yorumları arama düğmesini anar.

## Hata ve kenar hâlleri

- Enter'in açtığı sohbet okunamazsa (`missing`, hata) `focusReply` hiç doğru olmaz; istek bir
  sonraki tıklamada silinir.
- Enter açık sohbeti yeniden açarsa kayıt elde, odak hemen gider.
- Arama sunucuya gitmez; `⌘K` bağlanmaz.

## Koşuda çıkan iki eski test

Kod yazılınca `App.test.jsx`'in iki eski testi düştü; ikisi de sahte düzenin, davranış değil:

- *the card in the transcript opens the file…*'in sahte sunucusu sohbet listesini de proje
  listesiyle (`[PROJECT]`) cevaplıyordu; başlıksız satır `matches`'te patladı. Gerçek sunucu her
  sohbeti başlığıyla verir (`routes.py`, `file_chat_store.py`), yani kodda koruma yerine sahte
  sunucu `/chats`'e sohbeti verir.
- *Continue here trims the chat…* sayfadaki tek textbox'ın yazma kutusu olduğunu varsayıyordu;
  `Search chats` de textbox. Sorgu `.chat`'in içine daraltıldı.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel; dördü de yeşil. Adım adım dökümü
[uygulama planında](../plans/2026-09-29-queenagent-m365-sohbet-arama-uygulama-plan.md).
