# Madde 361 — Ad sorma ekranı · test turu

**Kaynak:** [yol haritasının 361'i (v9-2r)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de, tasarımı queen-design'ın `queen-agent-v3` dalında 135, 153, 169, 195 —
`projects/queen-agent/new-project/index.html`, `BEHAVIOUR.md`'nin *Bar* ve *Name project* bölümleri,
`DESIGN-STANDARD.md`'nin *Bar* ve *Screen and empty*'si, `kit.css`'in `.empty__*` kuralları. Üstüne
kurulduğu: 338 (`Bar.jsx`, sağdaki `ghost bar__exit`), 353 (All projects, `+ New project`, App'in
yönlendirmesi, `useProjects.createProject`).

**Kullanıcıdan gereken:** hiçbir şey. Koşu subagent'ta; iki yöne okunabilen kararlar aşağıda
*Kararlar*'da yazılı ve raporda Claude'a gider.

## Ne kanıtlanacak

Her `+ New project` — All projects'teki ve kenar çubuğunda *Projects*'in yanındaki `+` — önce ad
soran ekrana gider; ekranın ortasında başlık `Name your project`, hiç proje yokken `Name your first
project`. Enter ya da `Create project` projeyi yazılan adla açar ve boş sohbetine götürür; boş ad bir
şey yapmaz. Bir proje varken üst çubuğun sağında `Cancel`, ve Esc de aynısını yapar: ikisi geldiği
yere döner. Sunucu projeyi yazılan adla doğurur.

## Kararlar

1. **Sunucu adı alır, ve adsız proje doğmaz.** Bugün `POST /api/projects` gövde okumuyor ve
   `New project N` yazıyor (Madde 191). Tasarım bu yüzden iki istek atıyor — önce oluştur, sonra
   `PATCH` ile adlandır (`BEHAVIOUR.md`, *Name project*) —, ama o yol ikinci istek düşerse ortada
   `New project N` adlı bir proje bırakır. Doğrusu tek istek: `POST /api/projects` `{"name": …}`
   alır, adı kırpar; ad yoksa ya da boşsa `400` ve PATCH'inkiyle aynı söz, `a project needs a
   name`, ve hiçbir şey yazılmaz. Kural domain'de, `create_project`'te: adı PATCH'le aynı kurala
   bağlanır (kırpılır, boşsa `InvalidProjectName`).
2. **Madde 191'in numaralaması kalkar.** Ad sormayan hiçbir yol kalmıyor, o yüzden `New project N`'yi
   üreten `_next_name`, `_numbered` ve `NEW_PROJECT_NAME` ölü kod olur ve gider; onları tutan testler
   de. `create_project`'in imzası `name` alır; onu çağıran öteki testler (`test_append_message`,
   `test_delete_project`, `test_stream_answer`) bir ad verir — bu turda imza henüz ad almadığı için
   onlar da kırmızı düşer, ve bu bekleniyor.
3. **Ekranın adresi `/new`.** Tasarımın adresi `new-project/`; uygulamada `parsePath("/new")`
   `{ view: "new", projectId: null, chatId: null }` verir. Ekranda kenar çubuğu yok (All projects gibi,
   hiçbir proje açık değil), üst çubuğun ortası boş.
4. **Her oluşturma yolu buraya gelir:** All projects'in `+ New project`'i ve kenar çubuğunun `+`'sı
   (362'ye kadar duruyor) `/new`'e gider, tarihe yazılır (push); hiçbiri istek atmaz. "Proje yokken"
   ayrı bir yol değil: All projects `No projects yet.` der (353) ve aynı `+ New project` ekranı açar,
   bu kez `Name your first project` başlığıyla. Uygulama proje yokken de All projects ile açılır —
   tasarımın 167'si ve 353.
5. **Başlık** `projects.length`'ten: hiç proje yoksa `Name your first project`, varsa
   `Name your project`. Arşivdekiler de sayılır — gidilecek bir yer onlarla da var (363'ün Archived
   sekmesi).
6. **Ekran** tasarımın `screen()`'i: `.empty` içinde `.empty__box`; başlık alanın kendi etiketi
   (`<label class="empty__title" for=…>`, yanında ayrı bir "Project name" yazısı yok); altında
   `.empty__line` — `Chats live inside a project, and the files they create stay there.`; sonra
   `.empty__row` içinde yan yana `.empty__field` (placeholder `Project name`, `autocomplete="off"`) ve
   `.empty__action` `Create project`. Ekran açılınca odak alanda.
7. **Enter ya da `Create project`** kırpılmış ad boş değilse projeyi o adla açar: istek gider, liste
   yeniden okunur (353'ün yolu, sıra sunucunun), ve yeni projenin boş sohbeti `/p/<id>/c/new` açılır —
   `/new`'in yerine yazılır (replace): ad sorma ekranı işini bitirdi, geri tuşu ona dönüp ikinci bir
   proje açtırmaz. Shift + Enter bir şey yapmaz (tasarımın `onEnter`'ı). **Boş ya da yalnız boşluk olan
   ad** hiçbir istek atmaz, ekranda kalır. **İlk basış yoldayken ikinci bir basış** (çift Enter)
   ikinci bir proje açmaz.
8. **`Cancel`** üst çubuğun sağında, `Exit project`'in yerinde ve görünüşünde (`ghost bar__exit`),
   yalnız bir proje varken. Esc de aynısını yapar. İkisi **geldiği yere** döner: All projects'ten
   gelindiyse `/`, kenar çubuğunun `+`'sından gelindiyse o sohbetin adresi; adres elle yazıldıysa ya
   da sayfa `/new`'de yenilendiyse bilinen bir köken yok, `/`. Dönüş de `/new`'in yerine yazılır
   (replace), oluşturmadaki gibi. Hiç proje yokken çubuğun sağı boş ve Esc bir şey yapmaz (tasarım
   195: "İlk açılışta çıkılacak yer olmadığı için `Cancel` yok").
9. **`Bar`** sağdaki düğmenin adını alır (`exit`); verilmezse proje açıkken `Exit project`, değilse
   hiçbir şey — tasarımın `shell.bar`'ı gibi. Bugünkü çağrılar değişmez.
10. **Yüklenirken ve hata:** liste gelene kadar ekran hiçbir şey çizmez (spinner 364'ün). Liste
    okunamazsa ya da sunucu oluşturmayı reddederse, All projects'in bugünkü hâli gibi `.empty`
    içinde `.empty__error` sunucunun kendi sözüyle; cümle, `Try again` ve `Copy` 364'ün.
    `useProjects`'in tek `error`'u hem listenin hem eylemlerin hatası — bugünkü düzen, değişmez.
11. **CSS:** tasarımın `kit.css`'inden `.empty__box` (420 genişlik, sola yaslı), `.empty__title`
    (Newsreader, 34, 400; kutuda altında 8), `.empty__line` (14.5, `--muted`; kutuda altında 22),
    `.empty__row` (flex, 10 aralık), `.empty__field`. `.empty__title` ve `.empty__line` 353'te
    `NoProjectsScreen`'le gitmişti; `workspace.css.test.js`'in "kalan kural yok" listesinden çıkarlar.
    Tasarımda bu iki sınıfın yalnız kutudaki hâli uygulamada kullanılıyor, o yüzden kutunun
    boşlukları doğrudan kurallarına yazılır.

## Testler ne tutar

### Sunucu

**`test_project_usecases.py`** — numaralamanın yedi testi (*born with the default name*, *three in a
row count up*, *a deleted number…*, *a renamed project gives its number back*, *a project with a
name of its own holds no number*, *a number somebody typed…*, *separated by a space*) ve
`NEW_PROJECT_NAME` kalkar. `_born` bir ad verir. Yeni:

| # | Ne |
|---|---|
| S1 | `test_a_new_project_is_born_with_the_name_it_was_given` — ad, id, createdAt; ad kırpılmış (`"  Harbour  "` → `Harbour`) |
| S2 | `test_a_project_is_not_born_without_a_name` — `""`, `"   "` ve `None` `InvalidProjectName`; depoya hiçbir şey eklenmedi |
| S3 | `test_the_numbering_is_gone` — modülde `NEW_PROJECT_NAME` yok |

*created project is handed to the store* ad vererek kalır.

**`test_projects_api.py`** — `POST` her yerde bir adla (`_create(client, name)`); *projects opened one
after another are told apart by name* (numaralama) kalkar. Yeni:

| # | Ne |
|---|---|
| S4 | `test_created_project_appears_in_the_list` yeniden: `{"name": "Harbour"}` → 201, ad `Harbour`, listede aynısı |
| S5 | `test_a_project_needs_a_name_to_be_born` — gövdesiz, `{}` ve `{"name": "  "}` 400, `a project needs a name`, liste boş |

**`test_append_message.py`, `test_delete_project.py`, `test_stream_answer.py`** — `create_project`
çağrıları `name=` verir; iddiaları değişmez.

### Ön uç — `useRoute.test.js`

| # | Ne |
|---|---|
| R1 | `/new` `{ view: "new", projectId: null, chatId: null }` |

### Ön uç — `Bar.test.jsx`

| # | Ne |
|---|---|
| B1 | Proje yokken `exit="Cancel"`: ortada `.bar__project` yok, sağda `Cancel`, sınıfı `ghost bar__exit`; basınca `onExit` |

### Ön uç — yeni `NameProjectScreen.test.jsx`

| # | Ne |
|---|---|
| N1 | Başlık `Name your project` alanın etiketi (`getByLabelText`), `.empty__title`; `.empty__line`'ın cümlesi; placeholder `Project name`; `Create project` `.empty__action`; hepsi `.empty > .empty__box` içinde |
| N2 | `first` ile başlık `Name your first project` |
| N3 | Açılınca odak alanda |
| N4 | Ad yazılıp Enter → `onCreate("Harbour")`, kırpılmış; `Create project` da aynısı |
| N5 | Boş ya da boşluk: Enter ve düğme `onCreate`'i çağırmaz; Shift + Enter de çağırmaz |
| N6 | `onCreate` yoldayken (bitmeyen söz) ikinci Enter ve düğme yeniden çağırmaz |
| N7 | `loading` iken alan ve başlık yok |
| N8 | `error` iken sunucunun sözü `.empty__error`'da, alan yok |

### Ön uç — `App.test.jsx`

353'ün *+ New project makes a project and opens its draft…* testi kalkar (ad sormadan oluşturuyordu);
`serverWithProjects`'in `POST`'u gövdedeki adı doğurur. Yeni:

| # | Ne |
|---|---|
| A1 | All projects'te `+ New project` → adres `/new`, istek yok, kenar çubuğu yok, başlık `Name your project`, çubuğun sağında `Cancel` |
| A2 | Ad yazılıp Enter → tek `POST`, gövdesi `{"name":"Harbour"}`; adres `/p/p9/c/new`, çubuğun ortasında `Harbour`; `/new` push, sohbetin adresi replace; `Exit project`'ten sonra All projects'te `Harbour` listenin başında |
| A3 | Boş adla Enter → istek yok, adres `/new` |
| A4 | `Cancel` → `/`, All projects, istek yok |
| A5 | Esc → `/`, All projects |
| A6 | Bir sohbetteyken kenar çubuğunun `+`'sı → `/new`, istek yok; `Cancel` o sohbetin adresine döner |
| A7 | Elle yazılan `/new`: ekran çiziliyor, `Cancel` `/`'e döner |
| A8 | Proje yokken `+ New project` → `Name your first project`, çubuğun sağında düğme yok, Esc adresi değiştirmez |
| A9 | Sunucu oluşturmayı reddedince sunucunun sözü ekranda, adres `/new` |

### Ön uç — `workspace.css.test.js`

"Kalan kural yok" listesinden `.empty__title` ve `.empty__line` çıkar. Yeni:

| # | Ne |
|---|---|
| C1 | `.empty__box`: `width: 420px`, `text-align: left` |
| C2 | `.empty__title`: `var(--font-heading)`, `34px`, `400`, `margin: 0 0 8px` |
| C3 | `.empty__line`: `14.5px`, `var(--muted)`, `margin: 0 0 22px` |
| C4 | `.empty__row`: `display: flex`, `gap: 10px` |
| C5 | `.empty__field`: `flex: 1`, `1px solid var(--line)`, `var(--surface)`, `var(--radius-control)`, `padding: 10px 12px`, `14.5px` |

## Tutmadıkları

- Ad sorma ekranının spinner'ı, `Couldn't load projects.`, `Try again`, `Copy` (364); kenar
  çubuğunun `+`'sının kalkması (362).
- `dist` — Claude derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `python -m pytest queen-agent -q` S1–S5'te ve `create_project`'e
ad veren öteki testlerde kırmızı; `npm test --prefix queen-agent/frontend` R1, B1, N1–N8 (dosya
yok), A1–A9 ve C1–C5'te kırmızı; queen-editor'ün iki süiti yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m361-ad-sorma-testler-plan.md).
