# Madde 382 — Arşive giden projenin sabitlemesi kalkar · test turu

**Kaynak:** [yol haritasının 382'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (Dalga 7) —
*(kullanıcı, 30 Eylül — "kalksın")*. Tasarım `projects/queen-agent/`'ta: `data.js`'in
`archiveProject`'i (`archivedAt`'ı yazar, `pinnedAt`'ı siler), `unarchiveProject`'i (yalnız
`archivedAt`'ı siler) ve `restoreProject(id, pinnedAt)`'i (`archivedAt`'ı siler, `pinnedAt`'ı geri
koyar); `projects/index.html`'in `undoing = { id, pinnedAt }`'u, `projectsWithUndo`'su ve `act`'in
`undo` / `unarchive` dalları; `BEHAVIOUR.md`'nin *All projects*'i (*"`Undo` (`data.restoreProject`)
puts it back there, pin order included"*). Üstüne kurulduğu: 339 (`pinned` ve `archived` dosyaları;
sabitlemenin anı `pinned` dosyasının mtime'ı), 346 (listenin sırası sunucunun: önce sabitlendikleri
sırayla sabitliler, sonra son kullanılan), 363 (arşiv, `Undo` satırı, `Unarchive`; sabitlemeyi arşivde
tuttu — bu parçanın kaldırdığı fark).

**Kullanıcıdan gereken:** hiçbir şey. Karar kullanıcının ("kalksın"); geri kalanı teknik, ve koşu
subagent'ta.

## Ne kanıtlanacak

Sabitli bir proje arşive alınınca sabitli değildir: `Unarchive`'la `Recent`'e döner, `Pinned`'e değil.
Arşivin hemen ardından çıkan `Undo` ise onu sabitlemesiyle, `Pinned`'deki eski yerine koyar — başka
sabitli projelerin önüne ya da arkasına kaymadan. `Undo` satırı da arşivden sonra `Pinned`'deki o yerde
durur (363'teki gibi).

## Kararlar

1. **Sabitlemenin anı diskte kalır, ama arşivdeki proje sabitli okunmaz.** Arşiv `pinned` dosyasına
   dokunmaz; `Project.pinned` arşivdeki bir proje için `False` der, liste de öyle (`"pinned": false`).
   Neden: sabitlemenin yeri dosyanın mtime'ı, ve `Undo` o yeri geri istiyor. Dosya arşivde silinirse
   yer ancak tarayıcının hatırladığı anı sunucuya geri yazdırarak — mağazaya mtime yazan yeni bir iş,
   listeye yeni bir `pinnedAt` alanı, ve `Undo` satırını sabitlilerin arasına tarayıcıda dizmek —
   kurulabilir. Dosyayı arşiv boyunca tutmak yeri sunucuda, diskte bırakır (FOUNDATION, ilke 2 ve
   Karar 4). Öteki yol — liste arşivdeki projeyi sabitli söylemeye devam eder, yalnız `Unarchive`
   sabitlemeyi siler — daha az parça, ama sunucunun cevabı "arşivdeki proje sabitli" olurdu; madde
   tam tersini söylüyor.
2. **Arşivdeki proje listede sabitlemesinin yerinde durur.** `list_projects` sabitlilerin bloğunu
   diskteki sabitleme anıyla kurar, arşivde olsun olmasın. Tasarımın `projectsWithUndo`'su `Undo`
   satırını tam orada gösterir; sunucunun sırası bunu verince ekran sıra kurmaz. Bedeli: arşivde sabit
   dosyası kalan proje `Archived` sekmesinde öne dizilir — 363'ten beri de böyle; raporda açık nokta.
3. **`Unarchive` sabitlemeyi siler.** `PATCH {archived: false}` arşivdeki bir projeye gelince, `pinned:
   true` istenmediyse `pinned` dosyası da gider. Arşivde olmayan bir projeye gelen `{archived: false}`
   hiçbir şeyi değiştirmez (339: *istenen zaten duruyorsa bir şey değişmez*) — sabitlemesi kalır.
4. **`Undo`, `PATCH {archived: false, pinned: <arşivden önceki hâli>}`.** Sabitli proje için
   `pinned: true`: dosya zaten orada, 339'un kuralıyla mtime'ı değişmez, ve proje eski yerine döner.
   Sabitsiz proje için `pinned: false` — tek biçim, tasarımın `restoreProject(id, pinnedAt)`'i gibi.
5. **Tarayıcı `Undo` için projenin sabitli olup olmadığını hatırlar**, tasarımın
   `undoing = { id, pinnedAt }`'u gibi: `Archive`'a basıldığı an satırın `pinned`'ı. `Undo` satırı
   bununla `Pinned`'de ya da `Recent`'te durur; sırası sunucunun. `Undo` yeni bir prop'la gider:
   `onRestoreProject(id, pinned)`; App onu `editProject(id, { archived: false, pinned })` yapar.
   `Unarchive` `onArchiveProject(id, false)` kalır.

## Testler ne tutar

### Sunucu — `test_pin_archive.py`

`test_the_archive_leaves_the_pin_alone` kalkar: tuttuğu, bu maddenin kaldırdığı davranış.

| # | Ne |
|---|---|
| S1 | Mağaza: sabitli proje arşive alınınca yeniden açılışta `pinned` `False`; `pinned` dosyası diskte, mtime'ı aynı |
| E1 | Kullanım durumu, sahte port: arşivdeki projeye `archived=False` → depoya `("pinned", id, False)` gider |
| E2 | Arşivdeki projeye `archived=False, pinned=True` → `("pinned", id, False)` gitmez |
| E3 | Arşivde olmayan sabitli projeye `archived=False` → `("pinned", id, False)` gitmez |
| L1 | `list_projects`, sahte port: arşivdeki, sabitleme anı olan proje sabitlilerin arasında kendi anının yerinde; `pinned`'ı `False` |
| A1 | API: sabitle, arşivle → cevap `pinned: false, archived: true`; yeni açılan uygulamanın listesi de; `Unarchive` → `pinned: false`, yeni açılışta da; `pinned` dosyası yok |
| A2 | API: `pa`, `pb` sabitli (ayrı anlar), `pc` sabitsiz; `pa` arşivlenince sıra yine `pa, pb, pc` ve `pa` `pinned: false`; `PATCH {archived: false, pinned: true}` → `pa` sabitli, sıra `pa, pb, pc`, sabitleme dosyasının mtime'ı değişmemiş |

### Ön uç — `AllProjectsScreen.test.jsx`

Yeni sabit `SECOND` — ikinci sabitli proje (`p6`, `Second pin`).

| # | Ne |
|---|---|
| U3 (değişir) | Sabitli `p1` arşivlenir; sunucu onu `pinned: false, archived: true` ile, `SECOND`'dan önce verir → `Pinned`'in satırları `Harbour at dusk archived · Undo`, sonra `Second pin` |
| U4 (değişir) | `Undo` → `onRestoreProject("p2", false)`; cevap gelene kadar `Undo` satırı durur; sonra yok |
| U8 | Sabitli `p1`'in `Undo`'su → `onRestoreProject("p1", true)`; `onArchiveProject` yalnız `("p1", true)` ile çağrılmış |

### Ön uç — `App.test.jsx`

`serverForRows`'un sahte sunucusu sunucunun yeni kurallarını tutar: sabitleme anı arşivde kalır ama
satır `pinned: false` der; sabitliler bloğu anla dizilir; `Unarchive` (`pinned: true` istemeden)
sabitlemeyi siler; zaten sabitli bir projeye `pinned: true` anı kaydırmaz. Başındaki yorum ve 363
bölümünün yorumu buna göre düzelir.

| # | Ne |
|---|---|
| B2 (değişir) | Sabitsiz projenin `Undo`'su ikinci PATCH `{archived: false, pinned: false}` |
| B3 (değişir) | İki sabitli (`Old pier`, `Harbour`), ilki arşivlenir: `Undo` satırı `Pinned`'in başında; `Undo` → PATCH `{archived: false, pinned: true}`; `Pinned` yine `Old pier`, `Harbour` sırasıyla |
| B7 | Sabitli `Old pier` arşivlenir, `Archived`'da `Unarchive` → PATCH `{archived: false}`; `Projects`'te `Old pier` `Recent`'te, `Pinned` bölümü yok |

## Tutmadıkları

- `Archived` sekmesinin sırası (Karar 2) — değişmez, raporda.
- Sabitlemesi 363 döneminde arşivde kalmış projeler: yeni kuralla okunur — arşivde sabitsiz,
  `Unarchive`'la `Recent`'e. Ayrı bir göç yok.
- `dist` — koşuyu yöneten derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `python -m pytest queen-agent -q`'da S1, E1, L1, A1, A2 kırmızı
(E2 ve E3 bugün de yeşil: bugünkü kod sabitlemeye hiç dokunmuyor); `npm test --prefix
queen-agent/frontend`'de U3, U4, U8, B2, B3 kırmızı. B7 bugün de yeşil: kural sunucunun, tarayıcı
`Unarchive`'da bugün de yalnız `{archived: false}` istiyor ve sahte sunucunun cevabını çiziyor — test,
tarayıcının o kuralı kendi kopyalamadığını tutar. queen-editor'ün iki süiti yeşil. Kırmızı
hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-30-queenagent-m382-arsiv-sabitleme-testler-plan.md).
