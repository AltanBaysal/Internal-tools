# v14 Görev 32 — Elde cevap varken gösterge yanmaz: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Önceki commit'in yedi kırmızı testini yeşile döndürmek.

**Architecture:** Üç hook, üç modül seviyesinde depo, tek kural. Depoya yazan taraf her zaman state'i
izleyen bir effect; okuyan taraf `useState`'in başlangıç değeri. Düşen istek hiçbir şeye dokunmaz.

**Tech Stack:** React 18, Vite, Vitest + jsdom.

**Spec:** [Görev 32 uygulama spec'i](../specs/2026-08-24-queen-editor-v14-gorev-32-uygulama-design.md)

## Global Constraints

- **Test dosyalarının iddiaları değişmiyor.** Bir istisna çıktı ve kaydı burada:
  `useProjectSettings.test.jsx`'in `carries the server's text on failure` testi, ondan önceki testle
  aynı proje adını kullanıyordu. Hatırlama gelince o ad artık cevaplanmış bir proje oluyor, yani
  testin düşen isteği ilk okuma değil, hatırlananın üstünde düşen bir tazeleme — ve kod onu doğru
  şekilde koruyor. Testin **cümlesi ve iddiası aynı kaldı**, yalnız kendine ait bir proje adı aldı.
  Bu, test döngüsünde fark edilmeliydi: dosyanın kuralı zaten "her test kendi adını ister" idi ve
  mevcut testler ona uymuyordu.
- **Yalnız başarılı cevap hatırlanır.** Düşen istek hiçbir depoya yazılmaz.
- **Düşen tazeleme ekrandakine dokunmaz.**
- **Depo state'i izler** — yazma işi effect'te, `setState`'in içinde değil.
- Dil: kod ve yorumlar **İngilizce**; commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `npm test --prefix queen-editor/frontend`
- Derleme: `npm run build --prefix queen-editor/frontend` · **`dist` aynı commit'e girer.**

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../features/projects/useProjectSettings.js` | kaydın durumu | proje anahtarlı depo |
| `.../features/photo_generation/useModels.js` | model listesi | tek yuvalı depo |
| `.../features/producers/useProducers.js` | üretici satırları | tek yuvalı depo |

---

### Task 1: Kaydın deposu

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/useProjectSettings.js`

**Interfaces:**
- Consumes: `getSettings`, `saveSettings` — değişmiyor.
- Produces: hook'un dışa açık yüzü aynı — `{ status, settings, error, save, reload }`. Değişen tek
  şey `status`'ün ne zaman `loading` olduğu.

- [ ] **Step 1: Depoyu ve mount'un başlangıcını yaz**

`import` satırlarının altına, `useProjectSettings`'in üstüne:

```js
// The last record each project answered with. Opening a frame's detail replaces the whole project
// screen, so this hook is torn down and built again on every step in and out; without this the
// photo panel would wait for an answer the visit already has (madde 32). Keyed by project: one
// project's record is never another's.
//
// Memory only, like the gallery's own two: a reload asks for everything again.
const REMEMBERED = new Map();

// Where a mount starts -- what this project last answered, or nothing yet.
function opening(project) {
  return REMEMBERED.has(project)
    ? { status: "ready", settings: REMEMBERED.get(project), error: null }
    : { status: "loading", settings: null, error: null };
}
```

- [ ] **Step 2: Hook'un gövdesini değiştir**

Bugünkü hâli:

```js
export function useProjectSettings(project) {
  const [state, setState] = useState({ status: "loading", settings: null, error: null });
  // Tracks which project the most recent reload() belongs to. Switching projects quickly can let an
  // earlier project's response resolve after a later one has already loaded -- without this guard it
  // would land (and could later be saved) into the wrong project's screen.
  const currentProject = useRef(project);

  const reload = useCallback(() => {
    currentProject.current = project;
    setState({ status: "loading", settings: null, error: null });
    return getSettings(project)
      .then((settings) => {
        if (currentProject.current !== project) return; // a newer project has since loaded
        setState({ status: "ready", settings, error: null });
      })
      .catch((err) => {
        if (currentProject.current !== project) return;
        setState({ status: "error", settings: null, error: err.message });
      });
  }, [project]);

  useEffect(() => {
    reload();
  }, [reload]);
```

Yerine:

```js
export function useProjectSettings(project) {
  const [state, setState] = useState(() => opening(project));
  // Tracks which project the most recent reload() belongs to. Switching projects quickly can let an
  // earlier project's response resolve after a later one has already loaded -- without this guard it
  // would land (and could later be saved) into the wrong project's screen.
  const currentProject = useRef(project);
  // Which project the state on screen belongs to. The route can swap projects without unmounting,
  // and the previous one's record must not stay up while the new answer flies.
  const shownProject = useRef(project);
  if (shownProject.current !== project) {
    shownProject.current = project;
    setState(opening(project));
  }

  const reload = useCallback(() => {
    currentProject.current = project;
    // Only a project nothing has answered for is emptied: a refresh over a record already on
    // screen is silent, which is the whole of madde 32.
    setState(opening(project));
    return getSettings(project)
      .then((settings) => {
        if (currentProject.current !== project) return; // a newer project has since loaded
        setState({ status: "ready", settings, error: null });
      })
      .catch((err) => {
        if (currentProject.current !== project) return;
        // Losing a refresh costs the user nothing, and emptying the panel over it would be the
        // opposite of quiet -- a dead tunnel is the status poll's to report, and it does.
        if (REMEMBERED.has(project)) return;
        setState({ status: "error", settings: null, error: err.message });
      });
  }, [project]);

  useEffect(() => {
    reload();
  }, [reload]);

  // Whatever the record becomes is what a later mount starts from. One effect rather than a write
  // beside every setState: only an answer that really arrived may be remembered, and `ready` is
  // the one state that means exactly that.
  useEffect(() => {
    if (state.status === "ready") REMEMBERED.set(project, state.settings);
  }, [project, state]);
```

- [ ] **Step 3: Kaydın üç testinin yeşile döndüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `useProjectSettings.test.jsx` **7 tests, 0 failed**. `useModels` ve `useProducers` hâlâ
2'şer failed.

---

### Task 2: Model listesinin deposu

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/useModels.js`

**Interfaces:**
- Consumes: `listModels`, `failureText` — değişmiyor.
- Produces: dışa açık yüz aynı — `{ models, error, reload }`.

- [ ] **Step 1: Yuvayı yaz**

`useModels`'in üstündeki yorum bloğunun altına:

```js
// What the machine last answered. One slot rather than a map: the renderer's list belongs to the
// machine, not to a project. Kept for the length of a visit -- coming back from a frame builds this
// hook again, and the box saying yükleniyor… over a list the screen already had is the flicker this
// removes (madde 32).
let remembered = null;
```

- [ ] **Step 2: Gövdeyi değiştir**

Bugünkü hâli:

```js
export function useModels() {
  // null = not known yet (first fetch still flying), [] = nothing installed, or nothing readable.
  const [models, setModels] = useState(null);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  const reload = useCallback(() => (
    listModels()
      .then((list) => { if (alive.current) { setModels(list); setError(null); } })
      .catch((err) => { if (alive.current) { setModels([]); setError(failureText(err)); } })
  ), []);

  useEffect(() => {
    alive.current = true;
    reload();
    return () => { alive.current = false; };
  }, [reload]);

  return { models, error, reload };
}
```

Yerine:

```js
export function useModels() {
  // null = not known yet (first fetch still flying), [] = nothing installed, or nothing readable.
  const [models, setModels] = useState(remembered);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  const reload = useCallback(() => (
    listModels()
      .then((list) => { if (alive.current) { setModels(list); setError(null); } })
      .catch((err) => {
        if (!alive.current) return;
        // Only a first read empties the box, so the panel can stop waiting and the queue stays
        // usable. Over a list the visit already has, a refresh that fell over changes nothing.
        if (!remembered) setModels([]);
        setError(failureText(err));
      })
  ), []);

  useEffect(() => {
    alive.current = true;
    reload();
    return () => { alive.current = false; };
  }, [reload]);

  // An empty list is a real answer -- nothing installed -- and an unreadable one looks exactly like
  // it. The error beside it is what tells them apart, so only a list that arrived without one is
  // remembered.
  useEffect(() => {
    if (models && !error) remembered = models;
  }, [models, error]);

  return { models, error, reload };
}
```

- [ ] **Step 3: Model listesinin iki testinin yeşile döndüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `useModels.test.jsx` **4 tests, 0 failed**. `useProducers` hâlâ 2 failed.

---

### Task 3: Üretici satırlarının deposu

**Files:**
- Modify: `queen-editor/frontend/src/features/producers/useProducers.js`

**Interfaces:**
- Consumes: `listProducers`, `failureText` — değişmiyor.
- Produces: dışa açık yüz aynı — `{ producers, error, install }`.

- [ ] **Step 1: Yuvayı yaz**

`useProducers`'in üstündeki yorumun altına:

```js
// What the machine answered, as the rows stand now. One slot rather than a map: what is installed
// belongs to the machine. Kept for the length of a visit, so coming back from a frame does not put
// the panel through not-knowing again for an answer that cannot have changed (madde 32).
let remembered = null;
```

- [ ] **Step 2: Başlangıcı yuvadan al ve deponun yazımını ekle**

Bugünkü hâli:

```js
export function useProducers() {
  // null = not known yet; the panel draws neither rows nor an error until the answer lands.
  const [producers, setProducers] = useState(null);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    listProducers()
      .then((rows) => {
        if (!alive.current) return;
        setProducers(rows);
        setError(null);
      })
      .catch((err) => { if (alive.current) setError(failureText(err)); });
    return () => { alive.current = false; };
  }, []);
```

Yerine:

```js
export function useProducers() {
  // null = not known yet; the panel draws neither rows nor an error until the answer lands.
  const [producers, setProducers] = useState(remembered);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    listProducers()
      .then((rows) => {
        if (!alive.current) return;
        setProducers(rows);
        setError(null);
      })
      // A read that fell over leaves the rows where they are: null on a first visit, and whatever
      // the visit already has on any later one.
      .catch((err) => { if (alive.current) setError(failureText(err)); });
    return () => { alive.current = false; };
  }, []);

  // The rows as they stand, not as they arrived: Kur writes its sentence onto one of them, so what
  // is on screen is no longer what the server gave. Remembering the answer instead of the state
  // would take that sentence away on the way back. Only a real answer ever gets here -- a failed
  // read leaves this null.
  useEffect(() => {
    if (producers) remembered = producers;
  }, [producers]);
```

- [ ] **Step 3: Takımın tamamen yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **0 failed**, 568 tests.

---

### Task 4: Derle, doğrula, commit'le

- [ ] **Step 1: Ön yüzü derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Değişen her şeyi gör**

Run: `git status --short`

Expected: üç hook dosyası, `dist/` altındakiler ve `docs/superpowers`. **Test dosyaları bu listede
olmamalı.**

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): a visit asks each of these three only once

Coming back from a frame asked for the project record, the model list and the
producer rows all over again, and all three passed through not-knowing on the
way: a ring in the photo panel, yukleniyor in the model box, producer rows and
their install notes blinking out. The answers were already in hand.

Each hook keeps what it was told for the length of a visit and starts a later
mount from it, then asks again quietly behind the screen. The record is keyed
by project, because one project's record is never another's; the two lists
belong to the machine and take a single slot each.

Only an answer that really arrived is kept. That is easy to get wrong for the
model list, where a failed read empties the box and an empty box is also a real
answer -- nothing installed. The error beside it is what separates them.

The producers store follows the rows rather than the answer: Kur writes its
sentence onto a row, so keeping what the server said would rub that sentence
out on the way back.

A refresh that falls over changes nothing on screen. Losing one costs the user
nothing, and a dead tunnel is already reported by the status poll. With nothing
remembered yet, a failed first read answers exactly as it did before.

How often these are asked for has not changed. What changed is what the screen
does while the answer is on its way.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** Üç depo → Task 1–3. Yalnız başarılı cevabın hatırlanması → Task 1 Step 2 (`ready`),
Task 2 Step 2 (`!error`), Task 3 Step 2 (`producers` yalnız cevapla dolar). Depo state'i izler →
üçünde de effect. Proje değişimi → Task 1 Step 2 (`shownProject`). Derlenmiş çıktı → Task 4.

**Ad tutarlılığı:** Üç hook da dışa açık yüzünü koruyor. Depo adları dosya içinde kalıyor;
`useProjectSettings`'inki `REMEMBERED`, `useGeneration`'ın aynı işi yapan deposuyla aynı adı taşıyor
ve ikisi ayrı modülde durduğu için çakışmıyorlar.

**Bilerek dışarıda:**

- **İsteği hiç göndermemek.** Üretici listesi için çekici: makinede kurulu olan uygulama ayaktayken
  değişemiyor. Ama bu ayrı bir karar ve testlerin hiçbiri istemiyor; üç hook'un aynı kuralı
  taşıması, birinin sessizce ayrılmasından iyi.
- **Deponun ne zaman boşaltıldığı.** Boşaltılmıyor: bir ziyaret bitince sayfa zaten gidiyor.
  `KEPT` ve `shownPictures` de aynı sebeple hiçbir şey atmıyor.
