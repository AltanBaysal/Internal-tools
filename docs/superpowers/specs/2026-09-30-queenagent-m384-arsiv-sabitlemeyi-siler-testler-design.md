# Madde 384 — Arşiv sabitlemeyi sunucuda siler; Archived yalnız son kullanıma göre · test turu

**Kaynak:** [yol haritasının 384'ü](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) (*"384 — hizalandı,
390 ile aynı anda"*). Kullanıcının 30 Eylül'deki kararları: *"abi unfoyu frontent yapmasın bir şey
arşivlenince backend otomaik pinini düşürsün logiciği backendde tut"*, *"Archived sekmesi yalnız son
kullanıma göre sıralansın mantıklı böyle olsun"*, ve `Undo` için Claude'un önerisini seçti: *"Recent'e,
sabitlemesiz dönsün … Sabitleme arşivle birlikte tamamen silinir, Undo sadece arşivi geri alır; istersen
bir tıkla yeniden sabitlersin. En sade yol bu, her şey sunucuda kalır. Tek fark: Undo satırı arşivlenir
arşivlenmez Recent'te görünür."*

Üstüne kurulduğu: 339 (`pinned` ve `archived` dosyaları), 346 (listenin sırası sunucunun), 363 (arşiv,
`Undo` satırı, `Unarchive`), ve **geri aldığı** 382: 382 `pinned` dosyasını arşiv boyunca diskte
bıraktı ki `Undo` sabitlemeyi yeriyle geri versin; liste sabitliler bloğunu `pinned_at`'la kurdu;
tarayıcı `undoing = { id, pinned }` tuttu ve `Undo`'yu `onRestoreProject(id, pinned)` →
`PATCH {archived: false, pinned}` yaptı.

**Tasarımdan fark:** tasarımda (`data.js`'in `restoreProject(id, pinnedAt)`'i, `projects/index.html`'in
`projectsWithUndo`'su, `BEHAVIOUR.md`'nin *All projects*'i) `Undo` projeyi sabitlemesiyle ve sabitliler
arasındaki eski yerine koyar. Kullanıcının kararı bunu geçersiz kılar: `Undo` yalnız arşivi geri alır.
`Archived` sekmesinin sırası tasarımla aynı (`archivedProjects`: son kullanım, yeniden eskiye).

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı; kalan kararlar teknik.

## Ne kanıtlanacak

- Sunucu bir projeyi arşive alınca `pinned` dosyasını siler; tarayıcı sabitleme için hiçbir şey
  göndermez.
- Liste arşivdeki projeleri yalnız son kullanıma göre sıralar: arşivdeki hiçbir proje sabitlilerin
  bloğunda durmaz — önceki kuralın diskte bıraktığı bir `pinned` dosyası olsa da.
- `Undo` yalnız `PATCH {archived: false}`; proje `Recent`'e sabitlemesiz döner. `Undo` satırı arşivden
  sonra sunucunun listesinin koyduğu yerde, `Recent`'te durur.
- `Unarchive` de projeyi `Recent`'e sabitlemesiz getirir.

## Kararlar

1. **Arşiv sabitlemeyi kullanım durumunda siler.** `edit_project`, projeyi arşive alan bir istekte
   depodan sabitlemenin kalkmasını ister. Kural domain'de: dosyayı bilen `data/` yalnız işaretleri yazar
   (CODE-STANDARD). Neden domain ve tarayıcı değil: kullanıcının sözü, ve FOUNDATION Karar 4.
2. **382'den kalmış bir sabitleme dosyası** — 363 ve 382 döneminde sabitli bir proje arşive alınınca
   dosya diskte kaldı. Bu yalnız v9 dalıyla koşan yerel verilerde olabilir (notebook `main`'i klonluyor,
   `main`'de arşiv yok), ama Claude'un tarayıcıda denediği kök tam bu durumda bir proje taşıyor olabilir.
   En sade doğru yol iki parça:
   - **Okunuş:** arşivdeki bir proje hiçbir zaman sabitli okunmaz (`Project.pinned`), ve liste
     sabitliler bloğunu `pinned`'le kurar — yani arşivdeki her proje son kullanıma göre dizilir. Böylece
     `Archived` sekmesinin sırası diskte ne kalmış olursa olsun doğru.
   - **Unarchive:** arşivden çıkan projenin sabitlemesi de silinir — yeni verilerde zaten yok, eski bir
     dosya ise böylece temizlenir ve proje `Recent`'e sabitlemesiz döner.
   Ayrı bir göç betiği yok. Arşivde olmayan bir projeye gelen `{archived: false}` hiçbir şeyi
   değiştirmez (339: *istenen zaten duruyorsa bir şey değişmez*).
3. **Tarayıcı yalnız hangi projenin `Undo`'sunun sunulduğunu tutar** — `undoing` yeniden bir id.
   `Undo`, `Unarchive` gibi `onArchiveProject(id, false)`; `onRestoreProject` kalkar. `Undo` satırı
   sunucunun listesinin projeyi koyduğu yerde durur: sunucu arşivde sabitlemeyi sildiği için bu
   `Recent`, son kullanımın yeri. Arşiv isteği dönmeden önceki birkaç milisaniyede liste henüz eskidir
   ve satır projenin eski yerinde görünür; tarayıcı sunucunun kuralını kopyalayıp onu önceden
   `Recent`'e taşımaz (Karar 4) — raporda açık nokta.

## Testler ne tutar

### Sunucu — `test_pin_archive.py`

Kalkanlar (382'nin, kullanıcının geri aldığı davranışı tutuyorlar):
`test_an_archived_project_is_not_pinned_and_its_pin_stays_on_disk`,
`test_undo_asks_for_the_pin_and_keeps_it`, `test_an_archived_project_keeps_its_place_among_the_pins`,
`test_undo_puts_a_pinned_project_back_in_its_place_among_the_pins`.

| # | Ne | Bugün |
|---|---|---|
| S1 | Mağaza: sabitleme dosyası kalmış arşivdeki proje (önceki kuralın bıraktığı) yeniden açılışta sabitli okunmaz | yeşil |
| E1 | Kullanım durumu, sahte port: sabitli projeye `archived=True` → depoya `("pinned", id, False)` gider | kırmızı |
| E2 | Arşivdeki projeye `archived=False` → `("pinned", id, False)` gider (382'nin testi, yorumu değişir) | yeşil |
| E3 | Arşivde olmayan sabitli projeye `archived=False` → `("pinned", id, False)` gitmez (382'nin testi, kalır) | yeşil |
| L1 | `list_projects`, sahte port: sabitli `a`; arşivdeki, sabitleme anı kalmış `b`; sabitsiz `c`; arşivdeki `d` → sıra `a`, sonra son kullanıma göre `d`, `c`, `b`; hiçbir arşivdeki `pinned` değil | kırmızı |
| A1 | API: sabitle, arşivle → cevap `pinned: false, archived: true` ve `pinned` dosyası **o an** yok; yeni açılışta liste de sabitsiz; `Unarchive` → `pinned: false` (382'nin testi, dosya iddiası arşivin hemen ardına da gelir) | kırmızı |
| A2 | API: `pa`, `pb` sabitli, `pc` sabitsiz (oluşturulma günleri 1, 2, 3); `pa` arşivlenince sıra `pb, pc, pa`, `pa` sabitsiz; `Undo` (`PATCH {archived: false}`) → `pa` sabitsiz, arşivde değil, sıra `pb, pc, pa`, dosya yok | kırmızı |
| A3 | API, eski dosya: `pa` sabitli ve arşivde, dosyası duruyor (önceki kuralın bıraktığı hâl, mağazadan yazılır); `pb` arşivde, `pa`'dan sonra kullanılmış → liste `pb, pa` sırasıyla, ikisi de sabitsiz; `Unarchive` `pa` → `pinned: false`, dosya yok | kırmızı |

### Ön uç — `AllProjectsScreen.test.jsx`

| # | Ne | Bugün |
|---|---|---|
| U3 (değişir) | Sabitli `p1` arşivlenir; sunucu onu `pinned: false, archived: true` ile, son kullanımın yerinde verir (`Second pin`, `p1`, `Night market`) → `Pinned`'de yalnız `Second pin`; `Recent`'in satırları `Harbour at dusk archived · Undo`, sonra `Night market` | kırmızı |
| U8 (değişir) | Sabitli `p1`'in `Undo`'su yalnız arşivi geri ister: `onArchiveProject` çağrıları `[["p1", true], ["p1", false]]` | kırmızı |
| U4 (değişir) | `Undo` → `onArchiveProject("p2", false)`; cevap gelene kadar satır durur; sonra yok | kırmızı |

### Ön uç — `App.test.jsx`

`serverForRows`'un sahte sunucusu yeni kuralları tutar: arşiv sabitlemeyi siler; sabitliler bloğu
sabitlendikleri sırayla, gerisi son kullanıma göre; zaten sabitli bir projeye `pinned: true` anı
kaydırmaz. Başındaki yorum ve 363 bölümünün yorumu buna göre düzelir.

| # | Ne | Bugün |
|---|---|---|
| B2 (değişir) | Sabitsiz projenin `Undo`'su ikinci PATCH `{archived: false}` | kırmızı |
| B3 (değişir) | İki sabitli (`Old pier` 30 saat, `Harbour` 40 saat), `Old pier` arşivlenir: `Pinned`'de yalnız `Harbour`; `Recent`'in satırları `Thesis`, `Notes`, `Old pier archived · Undo`; `Undo` → PATCH `{archived: false}`; bölümler `Pinned: Harbour`, `Recent: Thesis, Notes, Old pier` | kırmızı |
| B7 (kalır) | Sabitli `Old pier` arşivlenip `Unarchive` edilince `Recent`'te; PATCH'ler `{archived: true}`, `{archived: false}` | yeşil |

## Tutmadıkları

- Arşiv isteği dönmeden önceki anda `Undo` satırının nerede durduğu (Karar 3).
- CODE-STANDARD'ın `pinned` satırının metni: uygulama turunda düzelir (*on pin; removed on unpin, on
  archive and on unarchive*); tablo testi yalnız dosyaların adlarını denetler.
- `dist` — koşuyu yöneten derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `python -m pytest queen-agent -q`'da E1, L1, A1, A2, A3 kırmızı;
`npm test --prefix queen-agent/frontend`'de U3, U4, U8, B2, B3 kırmızı. S1, E2, E3, B7 bugün de yeşil —
382'nin korunan davranışı. queen-editor'ün iki süiti yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-30-queenagent-m384-arsiv-sabitlemeyi-siler-testler-plan.md).
