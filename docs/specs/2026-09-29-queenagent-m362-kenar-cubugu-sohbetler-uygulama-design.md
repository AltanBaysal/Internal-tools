# Madde 362 — Kenar çubuğunda yalnız New chat ve sohbetler · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m362-kenar-cubugu-sohbetler-testler-design.md) —
kararlar orada; bu belge testlerin istediğini nasıl kurduğunu söyler. Yalnız ön uç; sunucu
değişmez.

## Ne değişir

### `Sidebar.jsx`

- Prop'lar: `chats = []`, `activeChatId`, `onNewChat`, `onOpenChat`, `collapsed`, `onToggle`.
  `projects`, `activeProjectId`, `onNewProject`, `onOpenProject` gider (test spec'i, Karar 1–2).
- Açık: `sidebar__new-chat` (`+` ve `New chat`), `sidebar__chats`, `Fold`. `sidebar__chats`'in
  içinde sohbet varsa her biri için bugünkü `sidebar__chat` düğmesi, yoksa
  `<p className="sidebar__empty">No chats yet.</p>`. `Recent chats` etiketi, `MOST_CHATS` ve
  `.slice` gider.
- Katlı: `sidebar__new-chat--icon` ve `Fold`; `activeProjectId` koşulu gider.
- Dosyanın başındaki yorum (*with none selected they are absent…*) doğru değil artık; yerine neden
  yalnız sohbetler olduğu (tasarım 151, 152, 168), ve kenar çubuğunun yalnız bir proje açıkken
  çizildiği. `Fold`'un *as .dot is* yorumu `.dot` gidince yalan olur: *the app carries no icon
  files* kalır.

### `App.jsx`

- `<Sidebar>`'a yalnız yeni prop'lar gider.
- `namingFrom` / `setNamingFrom` gider (test spec'i, Karar 8). `askForNewProject` yalnız
  `navigate("/new")`; `leaveNaming` ve Escape `navigate("/", { replace: true })`. Yorumlar: ad
  sorma ekranına tek yol All projects, dönüş oraya. Escape'in bağımlılık listesinden `namingFrom`
  çıkar.

### `useChatLists.js`

- `useProjectChats`'in yorumu *first eight* diyor; artık kenar çubuğu hepsini çiziyor. Yorum: açık
  projenin sohbetleri, kenar çubuğu için.

### `workspace.css`

- Gider: `.sidebar__projects`, `.sidebar__head`, `.sidebar__label`, `.sidebar__head .sidebar__label`,
  `.sidebar__add` (ve `:hover`), `.sidebar__row-open` (ve `:hover` / `.sidebar__row--active`),
  `.sidebar__row-name`, `.sidebar__row-badge`, `.sidebar__row-badge--none`, `.dot`.
- `.sidebar__chats`'in üstündeki yorum (*Projects take at most 40%…*) gider; kural aynen kalır —
  tasarımın `kit.css`'iyle aynı: üst çizgi, `flex: 1`, kendi içinde kayar.
- Yeni `.sidebar__empty`, tasarımın kuralı: `padding: 10px 12px; margin: 0; font-size: 13px;
  color: var(--muted); line-height: 1.5`.
- `.sidebar--collapsed`'ın yorumu (*Every other row here is a name or a title*) doğru kalıyor.

## Neyi değiştirmez

- `dist` — koşuyu yöneten derler.
- Sohbet listesinin yüklenirken/okunamayınca hâli (test spec'i, Karar 7).
- `DESIGN-STANDARD.md`'nin tablosunda `#3a342e` *Project names in the sidebar* gibi satırlar
  tasarımcının belgesinde; bu depoda kopyası yok.

## Nasıl görülür

Dört satır, paralel; dördü de yeşil. Tarayıcıda: bir projenin sohbetinde kenar çubuğu dolu
`+ New chat`, altında çizgi ve projenin bütün sohbetleri, açık olan koyu zeminli; sohbeti olmayan
projenin taslağında `No chats yet.`; `Projects`, proje satırları ve `+` yok.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m362-kenar-cubugu-sohbetler-uygulama-plan.md).
