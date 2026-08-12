# Queen Editor v5 · Görev 25 — Prompt düzenleme ve Yeniden üret · Uygulama planı

> Tasarım: [Görev 25 spec](../specs/2026-08-12-queen-editor-v5-gorev-25-yeniden-uret-design.md).
> Önce kırmızı test, sonra en küçük kod.

**Hedef:** detaydaki prompt düzenlenip "Yeniden üret — yeni kare" ile yeni bir kare olarak kuyruğa
girsin.

**Mimari:** kopya karenin ortak parçaları `domain/copy_frame.py`'ye taşınır; yeni use case
`domain/usecases/regenerate.py` onları kullanır; uç nokta `POST /api/projects/<p>/regenerate`.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — Ortak parça: kopya kare

**Dosyalar:** `domain/copy_frame.py`, `domain/usecases/queue_layer.py`,
test: `tests/test_photo_name.py` (var olan `next_id` testleri duruyor)

- [ ] `copy_frame.py`'ye taşınanlar (adlarından alt çizgi kalkar):

```python
def family(frame):      # was queue_layer._family
def placed(gallery, born):   # was queue_layer._placed
def known_ids(record, plan_store, project):   # was queue_layer._known_ids


def carry_layers(record, project, copy, frame, kind, now):
    """Give the new frame everything below the layer that is about to be made.

    A video copy shares the picture, a sound copy shares the picture and the video (madde 102).
    The rows point at the source's own files: one picture, two frames holding it.
    """
    words = frame.get("prompts", {})
    for under in queue.ORDER[:queue.ORDER.index(kind)]:
        file = frame.get("layers", {}).get(under)
        if not file:
            continue
        record.append(project, {"file": file, "frame": copy, "layer": under,
                                "status": queue.DONE, "prompt": words.get(under, ""),
                                "negative": frame.get("negative", ""),
                                "seed": frame.get("seed"), "createdAt": now()})
```

`queue_layer.py` bu dörtten okur; kendi kopyaları silinir.

- [ ] `python -m pytest queen-editor -q` → yeşil (davranış değişmedi).

---

## Görev 2 — `regenerate`

**Dosyalar:** yeni `domain/usecases/regenerate.py`, `presentation/routes.py`, `main.py`,
testler: `tests/test_photo_usecases.py`, `tests/test_photo_routes.py`

**Arayüz:**

```python
def regenerate(runner, store, record, plan_store, order_store, producers, new_seed, now,
               project, file, kind, prompt, log=None, writers=None) -> str
```

- [ ] **Adım 1 — kırmızı testler:**

```python
def test_regenerating_with_the_same_prompt_stays_in_the_family():
    store, record, plan_store = video_project((0, "a"))

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "0_a.png", layers.PHOTO, "p")

    assert born == "P0_1"
    job = plan_store.appended[-1][0]
    assert (job["type"], job["prompt"], job["seed"]) == ("photo", "p", 7)


def test_a_changed_prompt_takes_the_next_prompt_number():
    store, record, plan_store = video_project((0, "a"))

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "0_a.png", layers.PHOTO, "başka bir şey")

    assert born == "P1_0"


def test_the_new_frame_stands_next_to_its_source():
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    order = FakeOrderStore()

    regenerate(sync_runner(), store, record, plan_store, order,
               {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
               "düğün", "0_a.png", layers.PHOTO, "p")

    assert order.order == ["1_a", "P0_1", "0_a"]


def test_regenerating_a_video_gives_the_new_frame_the_sources_photo():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "0_a.png", layers.VIDEO, "kadın dönüyor")

    assert record.slots("düğün")[born]["photo"]["file"] == "0_a.png"
    # The source keeps its own video: nothing is overwritten.
    assert record.slots("düğün")["0_a"]["video"]["status"] == "done"


def test_a_layer_the_frame_cannot_carry_is_refused():
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(LayerMissing):
        regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                   {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                   "düğün", "0_a.png", layers.AUDIO, "ses")


def test_regenerating_a_frame_the_gallery_does_not_know_is_refused():
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(FrameMissing):
        regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                   {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                   "düğün", "yok.png", layers.PHOTO, "p")
```

Yol testi:

```python
def test_regenerate_answers_with_the_new_frames_name(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = client.post("/api/projects/düğün/regenerate",
                       json={"file": "P0_0.png", "layer": "photo", "prompt": "a"})

    assert resp.status_code == 202
    assert resp.get_json()["frame"] == "P0_1"
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `regenerate.py`:**

```python
"""Make a layer again -- as a new frame, never over the one that is there.

"üret = ekle" holds here too (madde 77): the source frame and its files stay exactly as they are and
the result enters the gallery beside it. What makes this different from the panels is only where the
prompt comes from: the user typed it.

Which number the new frame takes is madde 99's rule: the same prompt is another variant of the same
family, a changed prompt is a new prompt and takes the next number.
"""
```

```python
class LayerMissing(Exception):
    """The frame does not carry what this layer would be made from (message is user-facing)."""


def regenerate(runner, store, record, plan_store, order_store, producers, new_seed, now,
               project, file, kind, prompt, log=None, writers=None):
    gallery = list_frames(record, store, plan_store, order_store, project)
    source = next((f for f in gallery if f["file"] == file), None)
    if source is None:
        raise FrameMissing(f"Bu kare galeride yok: {file}")
    under = queue.ORDER[:queue.ORDER.index(kind)]
    if source["status"] != "done" or any(u not in source.get("layers", {}) for u in under):
        raise LayerMissing(f"Bu karede {kind} üretilemez: altındaki katman yok.")

    number, _variant = family(source)
    said = (source.get("prompts", {}).get(kind) or "").strip()
    if prompt.strip() == said:
        # The same words: another variant of the same prompt's family.
        born = next_id(known_ids(record, plan_store, project), number)
    else:
        # New words are a new prompt: it takes the next number and starts its own family.
        born = frame_id(next_number(store, plan_store, record, project), 0)

    carry_layers(record, project, born, source, kind, now)
    plan_store.append(project, [{
        "id": born, "type": kind, "number": number_of(born), "variant": variant_of(born),
        "prompt": prompt,
        # Only a photo carries a negative and a seed of its own; the other layers are made from
        # what is under them.
        "negative": source.get("negative", "") if kind == layers.PHOTO else "",
        "seed": new_seed() if kind == layers.PHOTO else None,
        "model": source.get("model", "") if kind == layers.PHOTO else "",
    }])
    order_store.write(project, placed([f["id"] for f in gallery], {source["id"]: [born]}))
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers)
    return born
```

- [ ] **Adım 4 — `routes.py`:**

```python
    @bp.post("/api/projects/<project>/regenerate")
    def post_regenerate(project):
        body = request.get_json(silent=True) or {}
        layer = body.get("layer")
        if layer not in queue.ORDER:
            return jsonify({"error": f"Böyle bir katman yok: {layer}"}), 404
        prompt = body.get("prompt")
        try:
            frame = regenerate(project, body.get("file"), layer,
                               prompt if isinstance(prompt, str) else "")
        except ProjectMissing as exc: 404
        except FrameMissing as exc: 404
        except LayerMissing as exc: 400
        except Busy as exc: 409
        return jsonify({"job": "running", "frame": frame}), 202
```

`main.py`'de partial'ı bağla (`new_seed` foto işiyle aynı üreteç).

- [ ] **Adım 5:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 3 — Ön yüz: düzenleme ve buton

**Dosyalar:** `shared/api.js`, `useGeneration.js`, `PhotoDetail.jsx`,
test: `PhotoDetail.test.jsx`

- [ ] **Adım 1 — kırmızı testler:**

```jsx
describe("PhotoDetail — regenerating", () => {
  it("lets the prompt be edited and marks the box as changed", async () => {
    await open("P0_0.png", { frames: [LAYERED] });

    const box = screen.getByDisplayValue("kırmızı elbise");
    fireEvent.change(box, { target: { value: "mavi elbise" } });

    expect(box.style.borderColor).toBe("var(--accent)");
  });

  it("sends the open layer and the edited text", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P0_1" });
    await open("P0_0.png", { frames: [LAYERED] });

    fireEvent.change(screen.getByDisplayValue("kırmızı elbise"),
                     { target: { value: "mavi elbise" } });
    await act(async () => {
      fireEvent.click(screen.getByText("Yeniden üret — yeni kare"));
    });

    expect(regenerateFrame).toHaveBeenCalledWith("düğün", "P0_0.png", "photo", "mavi elbise");
    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
    expect(screen.getByText("yeniden üretilecek — kuyrukta")).toBeTruthy();
  });

  it("forgets the editing when another frame is opened", async () => {
    // The arrows swap the frame under a mounted page: the box belongs to the frame, not the page.
    ...
  });
});
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:** `api.js`'e `regenerateFrame(project, file, layer, prompt)`; hook'a `regenerate`;
`TextBlock` düzenlenebilir hâle gelir (`textarea`, `onChange`, değişince `borderColor`), buton
`wf-btn--hl` ve `sent` durumu, rozet `StatusPill` kalıbında ama kendi metniyle.

- [ ] **Adım 4:** yeşil.

---

## Görev 4 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): a frame is made again as a frame of its own
```
