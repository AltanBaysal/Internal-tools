# Madde 353 — All projects ekranı · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m353-all-projects-testler-design.md) — kararlar
orada; bu belge onları koda çevirir. Kırmızı testler `61cd5c44`'te. FOUNDATION ve CODE-STANDARD okundu:
kural sunucuda kalır (Karar 4), ekran sunucunun sırasını ve "son sohbet"ini yalnız okur; dosya başına
tek iş; ölü kod kalmaz.

**Kullanıcıdan gereken:** hiçbir şey.

## Ön uç

### Yeni: `features/workspace/AllProjectsScreen.jsx`

`AllProjectsScreen({ projects, loading, error, onNewProject, onOpenProject })`, tasarımın
`projects/index.html`'inin `frameHtml` / `bodyHtml` / `sectionHtml` / `rowOpenHtml`'inin React'i:

- `error` varsa yalnız `.empty` › `p.empty__error` sunucunun sözüyle (tasarımın *failed* kalıbı; cümle,
  `Try again`, `Copy` 364'ün).
- Yoksa `.screen` › `.screen__column` › `.all-projects__head` (`h1.screen__title` `All projects`,
  `button.empty__action` `+ New project`). Yüklenirken başka bir şey yok. Yüklendiyse proje yoksa
  `p.all-projects__empty` `No projects yet.`; varsa `Pinned` ve `Recent` bölümleri.
- Bölüm (dosyanın kendi küçük bileşeni): satırı yoksa hiçbir şey; varsa `.all-projects__section` ›
  `.all-projects__label` ve `.all-projects__list` › `.all-projects__row` › `button.all-projects__row-open`
  (`title` ad) › `__row-name`, `__row-meta` (`countOf(chats, "chat") · countOf(files, "file")`),
  `__row-when` (`relativeTime(lastActivity)`).
- Bölmek sunucunun sırasını değiştirmez: `filter(pinned)` ve `filter(!pinned)`.

### Yeni: `features/workspace/countOf.js`

`countOf(many, word)` — onay penceresi ile satırın ortak kuralı ("one of a thing is one"); App'teki yerel
kopya buraya taşınır.

### Yeni: `features/workspace/OpenProject.jsx`

`/p/<id>`'nin kendi ekranı olmadığı için (tasarım 170) onu açan küçük bileşen:
`OpenProject({ projectId, navigate })`. Takılınca `readChats(projectId)` ile sohbet listesini bir kez
okur, `navigate(`/p/${id}/c/${chats[0]?.id ?? "new"}`, { replace: true })`. Okuma başarısız olursa
`.screen` › `.screen__column` › `p.list-error` sunucunun sözü. Temizlikte bir bayrak kalkar: cevap
ayrıldıktan sonra gelirse kimseyi taşımaz (B9). Bileşen olması durumunu (hata) adrese bağlar: başka bir
adrese gidince söner, sıfırlanır. `navigate` `useRoute`'un sabit fonksiyonu, bu yüzden effect yalnız
proje değişince yeniden koşar.

**Neden kendi okuması:** `useProjectChats`'in `useList`'i proje değişince yeni cevap gelene kadar önceki
projenin satırlarını tutuyor ve `loading` false kalıyor; ona bakan bir yönlendirme başka projenin
sohbetini açardı. `useList`'i yol başına anahtarlamak dosya rayının spinner'ını da değiştirirdi — 353'ün
işi değil.

### `useChatLists.js`

`deleteChat` ve `deleteJson` kalkar; `readChats(projectId)` (`getJson`) gelir. Başlık yorumu proje
ekranını anmaz.

### `useProjects.js`

`createProject` oluşturduktan sonra listeyi sunucudan yeniden okur (`await reload()`), sona eklemez:
sıra sunucunun (B10). Dönen değer yine yeni proje.

### `App.jsx`

- `NoProjectsScreen`, `ProjectScreen`, `Skeleton`, `deleteChat` import'ları; `firstLoad`, `atFork`,
  `landing` ve kök çatalın effect'i; `askToDeleteChat`; yerel `countOf` kalkar.
- Kenar çubuğu yalnız `route.view !== "root"` iken çizilir.
- `main`: `root` → `AllProjectsScreen` (`onNewProject` = oluştur, sonra `/p/<id>/c/new`'e push;
  `onOpenProject` = `openProject`). `project` → proje listede varsa `OpenProject`; liste gelmiş ve
  yoksa `That project does not exist.` (`.screen__missing`, bugünkü cümle). `chat` → `ChatScreen`,
  artık ilk yüklemeyi beklemeden (proje listesine ihtiyacı yok; iskelet kalktı).
- İçinde bulunulan proje silinince `navigate("/", { replace: true })`.
- `ChatScreen`'in `onBack`'i `navigate("/")`.
- Yorumlar: proje ekranını anan cümleler şimdiki doğruya çevrilir (Style: yorum yalnız bugünü söyler).

### `FilePanel.jsx`, `FileRail.jsx`, `FileRow.jsx`

`FilePanel`'in `back` seçeneği ve `×` dalı kalkar; hep `←`. `FileRail` `back` vermez; `RefreshFiles`
artık yalnız rayın, `export`'u kalkar. Üçünün proje ekranını anan yorumları düzelir.

### `workspace.css`

- Kalkar: `.panel`, `.reader__close` (ve `:hover`), `.skeleton--screen` ve üç çocuğu, `.screen-layout`,
  `.chat-list`, `.chat-row*`, `.screen__title-row`, `.screen__delete` (ve `:hover`), `.project-grid*`,
  `.column__title`, `.file-list__bar`, `.empty__title`, `.empty__line`; dar adımda `.screen-layout`,
  `.panel`, `.project-grid`, `.screen-layout--reading` kuralları; sıkı adımda `.chat-row__when`.
- Gelir: `kit.css`'in `.all-projects__head`, `__section`, `__label`, `__list`, `__row`, `__row:hover`,
  `__row-open`, `__row-name`, `__row-meta`, `__row-when`, `__empty` kuralları, değerleriyle; `data-hover`
  seçicileri tasarımın tuvaline ait, alınmaz. Arama, sekme, `⋯`, yeniden adlandırma ve Undo kuralları
  kendi maddelerinin.
- `.empty` ve `.empty__action`'ın yorumları şimdiki kullanımı söyler.

### Silinen dosyalar

`ProjectScreen.jsx`, `NoProjectsScreen.jsx`. `Skeleton.jsx` kalır: sohbet ekranı kullanıyor (355
kaldırıyor).

## Sunucu

- `routes.py`: `DELETE /api/projects/<id>/chats/<id>` kapısı ve `delete_chat` import'u kalkar.
- `domain/usecases/delete_chat.py` silinir.
- `FileChatStore.delete`, onun `TRASH_DIR`'ı ve `unique_name` import'u kalkar; `ports.py`'de
  `ChatStore.delete` kalkar.
- `list_chats.py`'nin docstring'i proje ekranını anmaz.

## Belge

`CODE-STANDARD.md`'nin tablosu: `trash/<name>` satırı "on a file's delete". Proje silinince proje
kökteki `trash/`'e bütün taşınır; o satır proje içindeki çöpü anlatıyor.

## `dist`

Derlenmez — Claude derler (koşunun kuralı).

## Nasıl görülür

Dört satır, paralel: queen-agent'ın iki süiti yeşil, queen-editor'ünkiler de.

Adım adım dökümü [uygulama planında](../plans/2026-09-29-queenagent-m353-all-projects-uygulama-plan.md).
