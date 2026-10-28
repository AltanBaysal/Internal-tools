# Görev 10 — Bitiş, hata ve bilgi kartları · Uygulama Planı

> **Çalıştıran ajan için:** GEREKLİ ALT BECERİ: superpowers:executing-plans.

**Amaç:** Bitiş iki karta ayrılır, hata kartı hepsini birden kuyruğa geri gönderir, kart hâline göre
renk alır ve kendiliğinden süren kuyruk bunu söyler.

**Mimari:** Arka uçta yeni bir kullanım senaryosu (`retry_failed`) var olan `/retry` ucunun dosyasız
hâline bağlanır. Ön yüzde `failures` `[{layer, count}]` olur ve kuyruk paneli kartları çizer.

**Spec:** [Görev 10 tasarımı](../specs/2026-08-12-queen-editor-v5-gorev-10-bitis-hata-kartlari-design.md)

## Global kısıtlar

- **Full TDD:** önce kırmızı test.
- Katman anahtarları arka ucun sözcükleri: `photo` · `video` · `audio`.
- Dil ayrımı: yorum/test adı/commit **İngilizce**, kullanıcı metni **Türkçe**.
- Test komutları: `npm test --prefix queen-editor/frontend -- --run` ·
  `python -m pytest queen-editor -q` · derleme `npm run build --prefix queen-editor/frontend`.
- **Tek commit**, görevin sonunda, `dist/` ile birlikte.

---

### Görev 1: Hepsini kuyruğa geri koyan kullanım senaryosu

**Dosyalar:**
- Oluştur: `queen-editor/backend/features/photo_generation/domain/usecases/retry_failed.py`
- Değiştir: `queen-editor/backend/features/photo_generation/presentation/routes.py:95-106`
- Değiştir: `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`,
  `queen-editor/backend/tests/test_photo_routes.py`

**Arayüzler:**
- Üretir: `retry_failed(runner, store, record, plan_store, producers, now, project, log=None,
  order_store=None) -> int` — kaç işin kuyruğa döndüğü.

- [ ] **Adım 1: Testi yaz (kırmızı test)**

`test_photo_usecases.py`:

```python
def test_retrying_them_all_puts_every_failed_job_back_in_line():
    store, record, generator = FakeStore(), FakeRecord(), FakeGenerator()
    plan_store = FakePlanStore(frames=[frame(0, "a", "ilk"), frame(1, "a", "ikinci"),
                                       frame(2, "a", "üçüncü")])
    record.mark("düğün", "0_a", "photo", "0_a.png", queue.FAILED, "t")
    record.mark("düğün", "1_a", "photo", "1_a.png", queue.DONE, "t")
    record.mark("düğün", "2_a", "photo", "2_a.png", queue.FAILED, "t")

    put_back = retry_failed(sync_runner(), store, record, plan_store,
                            {layers.PHOTO: generator}, lambda: "t2", "düğün")

    assert put_back == 2
    # The one that landed is not made again; the two red ones are.
    assert sorted(name for name, _d in store.saved) == ["0_a.png", "2_a.png"]
```

`test_photo_routes.py`'ye — o dosyanın kendi istemci kalıbıyla:

```python
def test_retry_without_a_file_retries_them_all(client, calls):
    response = client.post("/api/projects/düğün/retry", json={})

    assert response.status_code == 202
    assert calls["retry_failed"] == ["düğün"]
    assert calls["retry_frame"] == []
```

Sahte çağrı defteri ve `client` fikstürü o dosyada nasıl kuruluyorsa aynen kullanılır; yeni uç için
`retry_failed` adlı bir sahte eklenir.

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `python -m pytest queen-editor -q`

- [ ] **Adım 3: Kullanım senaryosunu yaz**

`retry_failed.py`:

```python
"""Put every red job back in line at once.

The queue's own rules do the rest: a job sent back waits behind the ones that never had a turn, and
the engine still finishes a type before it starts the next. Nothing about being retried in bulk
changes where the work lands -- only how many lines are written at once.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def retry_failed(runner, store, record, plan_store, producers, now, project, log=None,
                 order_store=None):
    """Returns how many jobs went back into the queue."""
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    put_back = 0
    for fid, cells in record.slots(project).items():
        for layer, cell in cells.items():
            if cell["status"] != queue.FAILED:
                continue
            record.mark(project, fid, layer, cell["file"], queue.QUEUED, now())
            put_back += 1
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store)
    return put_back
```

- [ ] **Adım 4: Ucu bağla**

`routes.py` — `retry_failed`'ı da alan bir parametre ve gövdeye bakan dallanma:

```python
    @bp.post("/api/projects/<project>/retry")
    def retry(project):
        body = request.get_json(silent=True) or {}
        file = body.get("file")
        try:
            # No file named means all of them: "retry this frame" and "retry" are the same verb
            # with and without an object.
            if file is None:
                retry_failed(project)
            else:
                retry_frame(project, file)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except FrameMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify({"job": "running"}), 202
```

`make_photo_generation_blueprint`'in imzasına `retry_failed` eklenir; `main.py` onu `partial` ile
bağlar (`retry_frame` ile aynı bağımlılıklar, `order_store=_order_store` dahil).

- [ ] **Adım 5: Koş, yeşili gör**

Koş: `python -m pytest queen-editor -q`

---

### Görev 2: Hatalar tür tür sayılır

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/shared/api.js`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
- Test: `useGeneration.test.jsx`, `api.test.js`

**Arayüzler:**
- Üretir: `failures` — `[{ layer, count }]`, üretim sırasında, yalnız `count > 0` olanlar.
- Üretir: `retryAll()` — dosyasız `/retry` çağrısı; `retryFailed(project)` üstünden.

- [ ] **Adım 1: Testi yaz (kırmızı test)**

`useGeneration.test.jsx`:

```jsx
  it("counts what failed for each kind of job", async () => {
    getStatus.mockResolvedValue({ status: "done", project: "düğün" });
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "failed" },
      { id: "P1_0", file: "P1_0.png", status: "failed" },
      { id: "P2_0", file: "P2_0.png", status: "done" },
    ]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.failures).toEqual([{ layer: "photo", count: 2 }]);
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

- [ ] **Adım 3: Sayımı ve çağrıyı yaz**

`api.js`:

```js
// No file named: the server reads that as "all of them" (see the retry endpoint).
export async function retryFailed(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/retry`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
}
```

`useGeneration.js` — `failures` satırının yerine:

```js
  // What failed, kind by kind, in the same shape as what is owed. Only photo jobs can fail today,
  // for the same reason only photo jobs are owed: the gallery is where this is read from.
  const failedByKind = {
    photo: shown.filter((frame) => frame.status === "failed").length,
    video: 0,
    audio: 0,
  };
  const failures = KINDS
    .map((layer) => ({ layer, count: failedByKind[layer] }))
    .filter((card) => card.count > 0);
```

ve yeni eylem:

```js
  // Every red job at once. Same endpoint as one frame's Tekrar dene, with no frame named.
  const retryAll = useCallback(() => (
    retryFailed(project)
      .then(() => { if (alive.current) startPolling(); })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project, startPolling]);
```

`retryAll` dönüş nesnesine eklenir.

- [ ] **Adım 4: Kaydırmayı sil**

`ProjectScreen.jsx` — `showFirstFailure` işlevi ve `onShowFailures` prop'u silinir; `SidePanel` ve
`QueuePanel` imzalarından da düşer. Yerine `onRetryAll={retryAll}` geçer.

- [ ] **Adım 5: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`
`ProjectScreen.test.jsx`'te "galeride göster" bekleyen bir test varsa silinir — davranışı madde 38
kaldırıyor.

---

### Görev 3: İki kart, kendi renkleriyle

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/QueuePanel.jsx`
- Test: `QueuePanel.test.jsx`

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

```jsx
  it("keeps the good news to itself and gives the failures their own card", () => {
    renderPanel({ job: { status: "done", project: "düğün", done: 20, failed: 3, total: 23 },
                  queue: [], failures: [{ layer: "photo", count: 3 }] });

    expect(screen.getByText("Kuyruk tamamlandı")).toBeTruthy();
    expect(screen.getByText("20 kare üretildi")).toBeTruthy();
    expect(screen.queryByText(", 3 hatalı")).toBeNull();
    expect(screen.getByText("3 kare üretilemedi")).toBeTruthy();
    expect(screen.getByText("Hepsini tekrar dene")).toBeTruthy();
  });

  it("draws no red card when nothing failed", () => {
    renderPanel({ job: { status: "done", project: "düğün", done: 20, failed: 0, total: 20 },
                  queue: [], failures: [] });

    expect(screen.queryByText(/üretilemedi/)).toBeNull();
  });

  it("breaks the failures down only when more than one kind failed", () => {
    renderPanel({ failures: [{ layer: "photo", count: 2 }, { layer: "video", count: 1 }] });

    expect(screen.getByText("3 kare üretilemedi — 2 foto · 1 video")).toBeTruthy();
  });

  it("puts every red job back in line at once", () => {
    const onRetryAll = vi.fn();
    renderPanel({ failures: [{ layer: "photo", count: 3 }], onRetryAll });

    fireEvent.click(screen.getByText("Hepsini tekrar dene"));

    expect(onRetryAll).toHaveBeenCalled();
    expect(screen.queryByText(/galeride göster/)).toBeNull();
  });

  it("dresses the finished card in green and the stopped one in red", () => {
    const { container, unmount } = renderPanel({
      job: { status: "done", project: "düğün", done: 20, failed: 0, total: 20 },
      queue: [], failures: [] });
    expect(container.querySelector("[data-run-card]").style.borderColor).toBe("var(--ok)");
    unmount();

    const stopped = renderPanel({ job: { status: "error", project: "düğün", done: 1, total: 3 },
                                  queue: [{ layer: "photo", owed: 2 }] });
    expect(stopped.container.querySelector("[data-run-card]").style.borderColor)
      .toBe("var(--danger)");
  });
```

`renderPanel`'in varsayılan `failures` değeri `[]` olur ve `onRetryAll={() => {}}` eklenir.

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

- [ ] **Adım 3: Kartları yaz**

`QueuePanel.jsx` — hata kartı ve sayımı:

```jsx
// The words the failure card breaks its total down with. Same keys as the queue's cards, because
// it is the same question asked about the other end of the run.
const LAYER_WORD = { photo: "foto", video: "video", audio: "ses" };
```

```jsx
  const failed = (failures || []).reduce((total, kind) => total + kind.count, 0);
  // "3 kare üretilemedi — 2 foto · 1 video". With one kind the breakdown would say the total
  // again, so it is left out.
  const breakdown = (failures || []).length > 1
    ? ` — ${failures.map((k) => `${k.count} ${LAYER_WORD[k.layer]}`).join(" · ")}`
    : "";
```

Görev 9'da kartın dışına çıkarılan altı çizili butonun yerine kendi kartı:

```jsx
      {failed > 0 && (
        <div className="wf-stroke"
             style={{ padding: 14, display: "flex", flexDirection: "column", gap: 8,
                      borderColor: "var(--danger)", background: "var(--danger-bg)" }}>
          <Note size={12} style={{ color: "var(--danger)" }}>
            {failed} kare üretilemedi{breakdown}
          </Note>
          {/* The card does something rather than sending the user somewhere: the failed frames are
              already red in the gallery, so pointing at them was never the useful half. */}
          <Btn sm onClick={onRetryAll}
               style={{ alignSelf: "flex-start", color: "var(--danger)",
                        borderColor: "var(--danger)", background: "none" }}>
            <Icon.Regen /> Hepsini tekrar dene
          </Btn>
        </div>
      )}
```

Koşu kartı kendi rengini alır ve tek aralıklı başlığa geçer:

```jsx
const CARD_TONE = {
  done: { borderColor: "var(--ok)", background: "var(--ok-bg)" },
  stopped: { borderColor: "var(--danger)", background: "var(--danger-bg)" },
};
```

```jsx
      <div data-run-card className="wf-stroke"
           style={{ padding: 14, display: "flex", flexDirection: "column", gap: 8,
                    ...(CARD_TONE[state] || {}) }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Dot state={state} />
          <Mono size={12} style={{ color: state === "stopped" ? "var(--danger)"
            : state === "done" ? "var(--ok)" : "var(--ink-2)" }}>{TITLE[state]}</Mono>
        </div>
```

ve iyi haber yalnız iyi haberi verir:

```jsx
        {state === "done" ? (
          <Note size={12} style={{ color: "var(--ok)" }}>{job.done} kare üretildi</Note>
        ) : state === "empty" ? (
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

---

### Görev 4: Kendiliğinden süren kuyruk bunu söyler

**Dosyalar:**
- Değiştir: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
- Değiştir: `queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`,
  `QueuePanel.jsx`
- Test: `QueuePanel.test.jsx`

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

```jsx
  it("says the queue picked itself up when nobody pressed anything", () => {
    renderPanel({ resumed: true });

    expect(screen.getByText("uygulama açıldı — kuyruk kaldığı yerden sürüyor")).toBeTruthy();
  });

  it("stays quiet about it when the user pressed the button themselves", () => {
    renderPanel();

    expect(screen.queryByText(/kaldığı yerden sürüyor/)).toBeNull();
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

- [ ] **Adım 3: Satırı yaz**

`QueuePanel.jsx` — tür kartlarının hemen altında:

```jsx
      {/* Only for a run nobody asked for. Its life is the run's own: no timer, and no invented
          number of seconds -- the design does not give one. */}
      {resumed && running && (
        <Note size={12} style={{ color: "var(--ink-3)" }}>
          uygulama açıldı — kuyruk kaldığı yerden sürüyor
        </Note>
      )}
```

`resumed` prop'u imzaya eklenir; `SidePanel` onu geçirir.

`ProjectScreen.jsx` — kendiliğinden sürdürmeyi işaretler:

```jsx
  // Whether the queue on screen is one this screen picked up by itself; the panel says so while it
  // flows, and only then.
  const [resumed, setResumed] = useState(false);
```

```jsx
    asked.current = project;
    setResumed(true);
    resume();
```

ve proje değişince sıfırlanır (`asked.current === project` kontrolüyle aynı yerde):

```jsx
  useEffect(() => { setResumed(false); }, [project]);
```

- [ ] **Adım 4: Koş, yeşili gör**

Koş: `npm test --prefix queen-editor/frontend -- --run`

---

### Görev 5: Kapanış

- [ ] **Adım 1: İki takımı da koş**

Koş: `python -m pytest queen-editor -q`
Koş: `npm test --prefix queen-editor/frontend -- --run`

- [ ] **Adım 2: Derle**

Koş: `npm run build --prefix queen-editor/frontend`

- [ ] **Adım 3: Tek commit**

```bash
git add -A
git commit -F - <<'MSG'
feat(queen-editor): the good news and the bad get a card each

A finished queue said both things in one sentence -- twenty made, three not --
and the only thing offered about the three was a link that scrolled the gallery
and left you there. The frames it scrolled to were already red; pointing at
them was never the useful half.

So the green card keeps the good news and the failures get a card of their own,
which does something instead: one press puts every red job back in line. The
server reads a retry with no frame named as all of them, which is the same verb
with and without an object.

The card takes its colour from what it is saying, and a queue that picked
itself up when the app opened now says so -- for exactly as long as that run
lasts, since the design names no number of seconds.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
MSG
```

## Öz denetim

**1. Spec kapsaması:** Karar 1 (tür tür hata) → Görev 2; karar 2 (bağlantı kalkar) → Görev 2
Adım 4 + Görev 3'ün testi; karar 3 (dosyasız uç) → Görev 1; karar 4 (renk) → Görev 3; karar 5
(açılış satırı) → Görev 4.

**2. Yer tutucu taraması:** `test_photo_routes.py`'nin fikstür adları o dosyanın kendi kalıbına
bırakıldı — orada **var olan** bir kalıp, uydurulacak bir şey değil.

**3. Tür tutarlılığı:** `failures` elemanı her yerde `{layer, count}` (kuyruğunki `{layer, owed}`
— iki ayrı soru, iki ayrı ad); `retry_failed` adı senaryoda, rotada, `main.py`'de ve testte aynı;
`data-run-card` yalnız Görev 3'te doğup orada kullanılıyor.
