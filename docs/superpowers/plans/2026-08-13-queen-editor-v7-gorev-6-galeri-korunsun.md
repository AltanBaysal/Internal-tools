# Görev 6 — Ekran değişince galeri sıfırdan yüklenmesin (uygulama planı)

**Spec:** [Görev 6](../specs/2026-08-13-queen-editor-v7-gorev-6-galeri-korunsun-design.md) ·
**Roadmap:** [v7](2026-08-13-queen-editor-v7-roadmap.md) · Blok 3

**Amaç:** `useGeneration` bir projenin son listesini mount'lar arası hatırlasın; galeri ↔ detay
geçişi beklemesiz olsun.

## Global kısıtlar

- Kod, yorum ve test adları **İngilizce**.
- Sunucu değişmiyor. Ön yüz değişiyor → `npm run build` ve `dist/` **aynı commit'te**.
- Görev sonunda **tek commit**.

## Dosyalar

- **Değiştir:** `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- **Değiştir:** `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx`

---

### Adım 1 — Testleri yaz

`useGeneration.test.jsx` içinde, boş başlangıcı sınayan testin proje adını değiştir (hafıza
projeye göre tutuluyor, "düğün" başka testlerde dolduruluyor):

```jsx
  it("treats the photos as unknown at first and asks for both status and photos on the first poll", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([]);

    // Its own project name: a gallery already answered for is remembered across mounts, so only a
    // project nothing has seen still starts out unknown.
    const { result } = renderHook(() => useGeneration("hiç görülmemiş"));
    expect(result.current.frames).toBeNull();

    await settle();

    expect(result.current.frames).toEqual([]);
    expect(getStatus).toHaveBeenCalledTimes(1);
    expect(listFrames).toHaveBeenCalledWith("hiç görülmemiş");
  });
```

ve üç yeni test ekle:

```jsx
  it("draws the gallery it already had the moment it is mounted again", async () => {
    const rows = [{ id: "P0_0", file: "P0_0.png", status: "done", owed: [], failed: [] }];
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue(rows);

    const first = renderHook(() => useGeneration("hatırlanan"));
    await settle();
    first.unmount();

    // Nothing has answered yet on this mount -- opening a frame's detail and coming back must not
    // blank the screen and start over.
    listFrames.mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useGeneration("hatırlanan"));

    expect(result.current.frames).toEqual(rows);
  });

  it("never hands one project's gallery to another", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "done", owed: [], failed: [] }]);

    const first = renderHook(() => useGeneration("birinci"));
    await settle();
    first.unmount();

    listFrames.mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useGeneration("ikinci"));

    expect(result.current.frames).toBeNull();
  });

  it("remembers the order the tiles were dropped into, not the one before it", async () => {
    const rows = [
      { id: "P0_0", file: "P0_0.png", status: "done", owed: [], failed: [] },
      { id: "P1_0", file: "P1_0.png", status: "done", owed: [], failed: [] },
    ];
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue(rows);
    saveOrder.mockResolvedValue({});

    const first = renderHook(() => useGeneration("sıralı"));
    await settle();
    await act(async () => { await first.result.current.reorder(["P1_0", "P0_0"]); });
    first.unmount();

    listFrames.mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useGeneration("sıralı"));

    expect(result.current.frames.map((frame) => frame.id)).toEqual(["P1_0", "P0_0"]);
  });
```

### Adım 2 — Koş, kırmızı olduğunu gör

`npm test --prefix queen-editor/frontend -- --run` → **FAIL**: yeni üç testten ikisi (hatırlama ve
sıra) düşer, proje ayrımı testi tesadüfen geçer.

### Adım 3 — Hafızayı yaz

`useGeneration.js` başına:

```js
// The last gallery each project answered with. Opening a frame's detail replaces the whole project
// screen, so the hook is torn down and built again on every step in and out; without this the
// screen would blank and refetch each time, though the answer it had was still good. Keyed by
// project: one project's gallery is never another's.
const REMEMBERED = new Map();
```

`frames` durumu ve proje değişimi:

```js
  // null = not known yet (nothing has ever answered for this project), [] = it truly has nothing.
  const [frames, setFrames] = useState(() => REMEMBERED.get(project) || null);
  // Which project the list on screen belongs to. The route can swap projects without unmounting,
  // and the previous one's tiles must not stay up while the new answer flies.
  const shown = useRef(project);
  if (shown.current !== project) {
    shown.current = project;
    setFrames(REMEMBERED.get(project) || null);
  }
```

Aynanın kendisi, kancanın sonlarına doğru (her yol tek yerden geçsin):

```js
  // Whatever the list becomes -- answered, reordered, a frame removed -- is what a later mount
  // starts from. One effect rather than a write next to every setFrames: those are functional
  // updates, and a cache written inside one would be a side effect in a place that must not have
  // any.
  useEffect(() => {
    if (frames) REMEMBERED.set(project, frames);
  }, [project, frames]);
```

### Adım 4 — Koş, yeşil olduğunu gör

`npm test --prefix queen-editor/frontend -- --run` → **PASS** (300+3 test).

### Adım 5 — Derle ve commit

```
npm run build --prefix queen-editor/frontend
git add queen-editor docs/superpowers
git commit -m "fix(queen-editor): the gallery survives a trip to a frame and back"
```
