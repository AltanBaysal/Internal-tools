# Madde 363 — Arşiv · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m363-arsiv-testler-design.md) — kararlar
orada; bu belge onları kırmızı commit'teki (`4a3adfd3`) testleri yeşile getiren en kısa koda çevirir,
fazlasını değil. FOUNDATION ve CODE-STANDARD'a uyar: sunucuya dokunulmaz (339 hazır), sıra sunucunun
(Karar 4), ekranın tuttuğu yalnız gösterdiği — sekme ve `Undo`'nun teklifi.

## Dosyalar

| Dosya | Ne değişir |
|---|---|
| `ProjectRow.jsx` | `onArchive` prop'u; arşivdeki satırın gövdesi; iki menü; `UndoRow` |
| `AllProjectsScreen.jsx` | sekmeler; `tab` ve `undoing` durumu; boş cümleler; satırın `Undo` hâli |
| `App.jsx` | `onArchiveProject={(id, archived) => editProject(id, { archived })}` |
| `workspace.css` | tasarımın `kit.css`'inden sekmeler, sayı, arşivdeki satırın yazısı, `Undo` satırı |
| `shared/app.css.test.js` | bir kilit: aşağıda |

**`app.css.test.js`'in bir kilidi bu parçada değişir.** *accent-coloured text takes the text hover*
`workspace.css`'in `--accent-link-hover`'ı hiç içermediğini tutuyordu, çünkü karar 16 geri alma
bağlantısını kaldırmıştı ve accent renkli tek kelime oydu. 363 aynı türden bir kelimeyi, `Undo`'yu,
tasarımın hover'ıyla geri getiriyor (`kit.css`: `.all-projects__undo button:hover` →
`--accent-link-hover`). Kilidin dayandığı durum kalmadığı için test ilk hâline döner: accent renkli
yazı — `a` ve `Undo` — yazının hover'ını alır. Kırmızı turda görülmedi, çünkü hover'ı yazan kod
yeşil turda geldi.

Sunucu, `useProjects` ve `Menu` değişmez: `editProject` PATCH'ten sonra listeyi yeniden okuyor ve
promise'ini döndürüyor; `Menu`'nün `divided`'ı var.

## `ProjectRow.jsx`

- **Satırın gövdesi üç hâl:** yeniden adlandırılıyorsa `RenameField` (bugünkü); değilse
  `project.archived` ise `<div className="all-projects__row-text">`, değilse bugünkü açan düğme. İkisi
  aynı üç sütunu taşır (`-row-name`, `-row-meta`, `-row-when`); üç `span` iki yerde yazılmasın diye
  küçük bir `Columns({ project })` onları çizer.
- **Menü:** arşivdeyse `Rename`, `Unarchive` → `onArchive(id, false)`, `Delete` (`divided`, `danger`);
  değilse `Rename`, `Pin`/`Unpin`, `Archive` → `onArchive(id, true)`, `Delete`. `Delete` bugünkü öğe,
  iki listede de aynı nesne.
- **`UndoRow({ name, onUndo })`**, aynı dosyada adlı export: satırın biçiminde
  (`all-projects__row all-projects__undo`) `<span><strong>{name}</strong> archived</span>`, `" · "`,
  ve `autoFocus`'lu `Undo` düğmesi. Satırın bir hâli olduğu için satırın dosyasında.

## `AllProjectsScreen.jsx`

- **Durum:** `tab` (`"projects"` | `"archived"`, başı `"projects"`) ve `undoing` (arşivlenip `Undo`'su
  teklif edilen projenin id'si ya da `null`). İkisi de ekranın: ekrandan çıkınca bileşen gider, ikisi de
  sıfırlanır (Karar 2 ve 11'in *ekrandan çıkınca*'sı).
- **Ayrım:** `archived = projects.filter(p => p.archived)`; `Projects`'in gösterdiği
  `projects.filter(p => !p.archived || p.id === undoing)` — `Undo` satırı listede projenin kendi yerinde
  durur, çünkü sunucu arşivde de sırayı ve sabitlemeyi değiştirmiyor; yeri yeniden hesaplanmaz.
- **Sayılar:** `Projects` arşivde olmayanları, `Archived` arşivdekileri sayar; `loading` iken boş.
- **Sekmeler** `.all-projects__tools`'ta aramadan sonra `.all-projects__tabs`'ta iki düğme:
  `{label} <span className="all-projects__count">…</span>`, açık olan `is-on`. Basmak `undoing`'i
  bırakır ve sekmeyi değiştirir.
- **`ProjectList`** `any` (hiç proje var mı), `shown`, `archivedTab`, `query`, `row` alır: hiç proje
  yoksa `No projects yet.`; aramayla süzülen boşsa aranan varsa `No projects match "…".`, yoksa
  `No archived projects.` ya da `Every project is archived.`; `Archived`'da tek `.all-projects__list`,
  `Projects`'te bugünkü iki bölüm.
- **`row(project)`:** `project.id === undoing` ise `UndoRow`, değilse `ProjectRow`. Satıra giden üç
  sarmalayıcı:
  - `openMenu(id)` — `undoing`'i bırakır, sonra `onOpenMenu(id)` (Karar 11: bir sonraki iş).
  - `archive(id, archived)` — `archived` ise `undoing = id`; sonra `onArchiveProject(id, archived)`.
  - `undo(id)` — `await onArchiveProject(id, false)`, sonra `undoing` hâlâ `id` ise bırakır. Liste
    gelmeden bırakmak projeyi bir an kaybettirirdi (Karar 10); *hâlâ `id` ise*, beklerken başka bir
    projenin arşivlenip teklifinin başlamış olabilmesi yüzünden.
- Dosyanın başındaki yorum `Archived`'ı artık *363'ün* diye değil, olduğu gibi anlatır.

## `workspace.css`

Tasarımın `kit.css`'inden, olduğu gibi: `.all-projects__tabs`, `.all-projects__tab`, `:hover`,
`.is-on`, `.all-projects__count` aramanın kuralından sonra; `.all-projects__row-text` açan düğmeninkinden
sonra; `.all-projects__undo`, `.all-projects__undo button`, `:hover` rename alanınınkinden sonra.
Tasarımın `[data-hover]` seçicisi yalnız tuvalin (basılmış hâli gösteriyor), alınmaz. `.all-projects__tools`'un
yorumu *363'te katılır* yerine bugünü söyler.

## Nasıl görülür

Dört satır, paralel: queen-agent frontend'in 30 kırmızısı yeşil, geri kalan her şey yeşil kalır.
Adım adım [uygulama planında](../plans/2026-09-29-queenagent-m363-arsiv-uygulama-plan.md).
