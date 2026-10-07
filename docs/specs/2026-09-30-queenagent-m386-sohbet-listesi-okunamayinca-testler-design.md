# Madde 386 — Kenar çubuğu okuyamadığı sohbet listesine "yok" demez · test turu

**Kaynak:** [yol haritasının 386'sı](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (Dalga 8) —
Dalga 5'te bulundu; *(kullanıcı, 30 Eylül — "bunlarıda düzelt")*. Üstüne kurulduğu: 362 (kenar
çubuğu: `+ New chat`, projenin bütün sohbetleri, hiç yoksa `No chats yet.`), 364 (proje listesi
okunamayınca `Couldn't load projects.`, `Try again` ve `Copy`; `ProjectsFailure.jsx`,
`CopyButton.jsx`), 365 (`Search chats`).

**Kullanıcıdan gereken:** hiçbir şey. Karar kullanıcının ("bunlarıda düzelt", ve maddenin *"proje
listesindeki gibi"*si); geri kalanı teknik, ve koşu subagent'ta.

## Bugün ne oluyor

Kenar çubuğunun listesi `useChatLists.js`'in `useProjectChats`'inden gelir; o da `shared/useList.js`'i
kullanır. `useList` okunamayan listenin hatasını `error`'da tutar, ama `useProjectChats` onu
bırakır: yalnız `items` ve `reload` döner. Okuma düşünce kenar çubuğu boş bir dizi görür ve
`No chats yet.` der — sohbetler diskte dururken.

## Ne kanıtlanacak

Projenin sohbet listesi okunamayınca kenar çubuğunda, satırların yerinde, `No chats yet.` değil:
okunamadığını söyleyen tek cümle, altında `Try again` ve `Copy`. `Try again` listeyi yeniden okur;
okuma gelince satırlar gelir, cümle gider. `Copy` gelen hatayı olduğu gibi panoya koyar.

## Kararlar

1. **Cümle `Couldn't load chats.`** Tasarımda (`queen-design-v3/projects/queen-agent/`) kenar
   çubuğunun listesi okunamayınca ne çizileceği yok: `shell.js` yalnız satırları, `No chats yet.`'i
   ve `No chats match "…".`'yı çiziyor; `BEHAVIOUR.md` ve `DESIGN-STANDARD.md` de bir şey
   söylemiyor, `APP-BUGS.md`'nin 29–31'i bu tür durumlar için *"not drawn"* diyor. Madde *"proje
   listesindeki gibi"* dediği için 364'ün kalıbı alınır, kenar çubuğunun ölçüsünde: tasarımın
   172'sindeki `Couldn't load projects.`'in sohbetler için olanı. Sunucunun ham sözü ekranda değil,
   `Copy`'de — 364'teki gibi; ekrandaki cümle bir sebep uydurmaz.
2. **Cümle satırların yerinde, `.sidebar__chats`'in içinde durur**; satırlar da `No chats yet.` de
   `No chats match "…".` de o sırada yoktur. Neden: liste bilinmiyor. `useList` okuma düşünce eldeki
   listeyi bırakır — başka bir projeden gelinmişse o projenin satırları; göstermek başka bir yalan
   olurdu. All projects de 364'te listenin yerine cümleyi koyuyor.
3. **`Search chats` kutusu yerinde kalır**, kenar çubuğunun iskeleti değişmez (`+ New chat`,
   arama, `.sidebar__chats`, katlama). Yazılan bir şey cümleyi değiştirmez; Enter hiçbir sohbeti
   açmaz — ekranda satır yokken gizli bir satırı açmak, üstelik başka projeninkini, yanlış olurdu.
4. **`Try again` 364'ün düğmesi** (`failure__retry`, her hatanın kahverengisi), **`Copy` app'in tek
   `CopyButton`'ı**, kendi sınıfıyla: `sidebar__copy` — okuyucunun `reader__copy`'si ve All
   projects'in `empty__copy`'si gibi; `Copied` accent, `Could not copy` kırmızı.
5. **Kenar çubuğunun ölçüsü:** cümle `No chats yet.`'in yerini ve boyunu alır (13px), rengi
   `.empty__error`'ın kahverengisi (`#8a5237`). İki düğme yan yana, ama en dar adımda (172px, iç
   boşluklarla ~128px) sığmayabilir: satır kırılabilir (`flex-wrap: wrap`).
6. **Katlanmış kenar çubuğu değişmez**: ikon sütununda liste yok, cümle de yok.
7. **`Try again` App'in elindeki okumayı yeniden yapar** (`useList`'in `reload`'u). Okuma sürerken
   ne görüneceği bu maddenin değil: `useList` hatayı yeni okumanın başında siler (kendi testi
   *"a fresh attempt clears the failure before it starts"*), dosya listesinin `Refresh`'i de böyle.
   Raporda açık nokta.

## Testler ne tutar

### Ön uç — `Sidebar.test.jsx`

`RAW = "HTTP 500: <!doctype html>\n<title>500 Internal Server Error</title>"` — `failure.js`'in bir
Flask 500 sayfasından çıkardığı, All projects'in testindeki gibi.

| # | Ne |
|---|---|
| K1 | `chats={[]}`, `error={RAW}`: `Couldn't load chats.` var, sınıfı `sidebar__error`, `.sidebar__chats`'in içinde; `No chats yet.` yok; `HTTP 500` ekranda yok |
| K2 | Cümlenin altında iki düğme, sırayla `Try again` (`failure__retry`) ve `Copy` (`ghost sidebar__copy`); `Try again` → `onRetry` çağrılır |
| K3 | `Copy` → `navigator.clipboard.writeText(RAW)`; düğme `Copied` der |
| K4 | `chats={CHATS}`, `error`: satır yok, cümle var; `zebra` yazılınca `No chats match "zebra".` yok, cümle duruyor |
| K5 | `chats={CHATS}`, `error`: Enter → `onOpenChat` çağrılmaz |
| K6 | `error`'la iskelet yine `sidebar__new-chat`, `sidebar__search`, `sidebar__chats`, `sidebar__foot` |

### Ön uç — `workspace.css.test.js`

| # | Ne |
|---|---|
| C1 | `.sidebar__error`: `font-size: 13px`, `color: #8a5237`, `margin: 0` |
| C2 | `.sidebar__actions`: `display: flex`, `flex-wrap: wrap` |
| C3 | `.sidebar__copy[data-said="yes"]` accent, `[data-said="no"]` destructive |

### Ön uç — `App.test.jsx`

| # | Ne |
|---|---|
| A1 | `/api/projects/p1/chats`'in ilk okuması 500; `/p/p1/c/new`'de kenar çubuğu `Couldn't load chats.` der, `No chats yet.` demez; `Try again` → ikinci okuma iki sohbeti verir, satırlar gelir, cümle gider |

## Tutmadıkları

- Okuma sürerken (ilk girişte ya da `Try again`'den sonra) kenar çubuğunun ne gösterdiği — Karar 7.
- Sunucu: değişmiyor; liste okunamayınca sunucunun ne dediği zaten `failure.js`'in işi.
- `dist` — koşuyu yöneten derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend`'de K1–K5, C1–C3 ve A1
kırmızı; K6 bugün de yeşil (kenar çubuğu `error`'ı bilmiyor, iskelet aynı) — hatanın iskeleti
bozmadığını tutar. Öteki üç süit yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-30-queenagent-m386-sohbet-listesi-okunamayinca-testler-plan.md).
