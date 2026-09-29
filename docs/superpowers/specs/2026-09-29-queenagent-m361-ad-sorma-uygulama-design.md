# Madde 361 — Ad sorma ekranı · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m361-ad-sorma-testler-design.md) ve kırmızı
commit'i `d649fe87`. Bu tur o testlerin anlattığını yazar, fazlasını değil. FOUNDATION'ın 4. kararı:
adın kuralı sunucuda; ekranın boş adı göndermemesi bir kolaylık.

## Sunucu

- **`usecases/create_project.py`** — `create_project(store, new_id, name, now)`: adı kırpar, `None`
  ya da boşsa `InvalidProjectName` — `edit_project`'in yeniden adlandırmadaki kuralıyla aynı.
  `NEW_PROJECT_NAME`, `_next_name`, `_numbered` silinir; modülün `store.list_all()` çağrısı da
  onlarla gider.
- **`usecases/edit_project.py`'ye dokunulmaz.** İki use case'in ortak bir `project_name`'e geçmesi
  denendi, ama `test_edit_project.py` `InvalidProjectName`'i `edit_project` modülünden alıyor; testi
  değiştirmemek için kural iki yerde üç satır olarak kalır — raporda.
- **`presentation/routes.py`** — `POST /api/projects` gövdeyi okur (`get_json(silent=True) or {}`),
  `name`'i use case'e verir; `InvalidProjectName` → `400 {"error": "a project needs a name"}`,
  PATCH'in sözüyle. "Creating takes no input" yorumu gider.

CODE-STANDARD'ın tablosu değişmez: `project.json` yine "on create, on rename" yazılır.

## Ön uç

- **`shared/useRoute.js`** — `parsePath`: `/new` → `{ view: "new", projectId: null, chatId: null }`.
  Başındaki "üç şekil" yorumu dört olur.
- **`Bar.jsx`** — `Bar({ project, exit = project ? "Exit project" : null, onExit })`: ortada proje
  varsa adı, sağda `exit` varsa `ghost bar__exit` düğmesi. Bugünkü çağrılar `exit` vermez, değişmez.
- **`NameProjectScreen.jsx`** (yeni) — `{ first, loading, error, onCreate }`. `loading` → `null`;
  `error` → `.empty > p.empty__error`; yoksa tasarımın `screen()`'i: `.empty > .empty__box`,
  `label.empty__title[for=project-name]`, `p.empty__line`, `.empty__row` içinde
  `input#project-name.empty__field` (`autoFocus`, `autoComplete="off"`, placeholder `Project name`) ve
  `button.empty__action` `Create project`. Basış (Enter — Shift'siz — ya da düğme) kırpılmış ad boş
  değilse ve önceki basış yolda değilse `onCreate(ad)` çağırır; yolda olduğu bir `ref`'te tutulur
  (iki basış aynı render'da gelebilir), `onCreate`'in sözü bitince bırakılır.
- **`useProjects.js`** — `createProject(name)` `postJson("/api/projects", { name })`; gerisi aynı.
- **`App.jsx`**:
  - `namingFrom` state'i, başta `/`: ad sorma ekranına kimin getirdiği. `askForName()` — All
    projects'in ve kenar çubuğunun `+`'sı — `window.location.pathname`'i yazar ve `/new`'e gider
    (push). Adres elle yazıldıysa ya da sayfa `/new`'de yenilendiyse state başlangıçtaki `/`'dir.
    (Bugünkü `askForName` — `window.prompt`'la yeniden adlandıran — adıyla karışmasın diye yeni olan
    `askForNewProject` adını alır.)
  - `leaveNaming()` → `navigate(namingFrom, { replace: true })`. `createNamed(name)` →
    `createProject(name)`, olursa `navigate("/p/<id>/c/new", { replace: true })`.
  - Kenar çubuğu `root`'ta ve `new`'de çizilmez. `main`'de `route.view === "new"` iken
    `<NameProjectScreen first={!projects.length} loading error onCreate={createNamed} />`.
  - `Bar`: `new`'de `exit` bir proje varsa `Cancel`, yoksa `null`, `onExit` `leaveNaming`; ötekilerde
    bugünkü gibi.
  - Esc: dinleyicinin sırasının sonuna — `new`'de ve bir proje varken `leaveNaming`. Kapatılacak
    başka bir şey yokken çalışır; ad sorma ekranında menü, onay ya da seçici açık olamaz.
  - "Made with no name asked" yorumu ve `newProject` gider.
- **`workspace.css`** — `.empty__error`'ın altına tasarımın `kit.css`'inden `.empty__title`,
  `.empty__line`, `.empty__box`, `.empty__row`, `.empty__field`. Kutunun dışında kullanılmadıkları için
  kutudaki boşluklar (8, 22) kurallara doğrudan yazılır; `.empty__line`'ın `max-width: 420px`'i kutu
  zaten 420 olduğu için yazılmaz.

## Riskler ve açık noktalar (raporda)

- 359 `AllProjectsScreen.jsx`'e arama kutusu koydu (`autoFocus`); `Cancel` All projects'e döndüğünde
  odak orada. Bu turda dal birleştirilemedi (izin reddedildi): birleştirmeyi Claude yapar.
- `useProjects`'in tek `error`'u: oluşturma reddedilince ad sorma ekranı sunucunun sözüne döner, yazılan
  ad kaybolur. 364 `Try again` getirir.
