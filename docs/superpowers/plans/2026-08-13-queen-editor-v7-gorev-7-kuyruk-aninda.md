# Görev 7 — Kuyruğa eklenen kare anında görünsün (uygulama planı)

**Spec:** [Görev 7](../specs/2026-08-13-queen-editor-v7-gorev-7-kuyruk-aninda-design.md) ·
**Roadmap:** [v7](2026-08-13-queen-editor-v7-roadmap.md) · Blok 3

**Amaç:** Kuyruğa ekleme cevabı galeriyi de taşısın; ekran ikinci bir tur atmasın.

## Global kısıtlar

- Kod, yorum ve test adları **İngilizce**; kullanıcıya görünen metin Türkçe.
- Kural sunucuda: kareyi ön yüz kurmaz.
- Ön yüz değişiyor → `npm run build` ve `dist/` **aynı commit'te**.
- Görev sonunda **tek commit**.

## Dosyalar

- **Değiştir:** `queen-editor/backend/features/photo_generation/presentation/routes.py`
- **Değiştir:** `queen-editor/backend/tests/test_photo_routes.py`
- **Değiştir:** `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- **Değiştir:** `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx`

---

### Adım 1 — Sunucunun testlerini yaz

`test_photo_routes.py` içine iki test:

```python
def test_queueing_answers_with_the_gallery_it_just_made():
    # Otherwise the screen has to ask for the gallery in a second round-trip, and the frames it
    # was told about are not on screen until that lands.
    client, _drive = make_client()
    resp = client.post("/api/projects/düğün/generate",
                       json={"prompts": '["a"]', "negative": "", "variants": 1})

    assert resp.status_code == 202
    assert resp.get_json()["added"] == 1
    assert [frame["id"] for frame in resp.get_json()["frames"]] == ["P0_0"]


def test_queueing_a_layer_answers_with_the_gallery_too():
    client, _drive = make_client()
    client.post("/api/projects/düğün/generate",
                json={"prompts": '["a"]', "negative": "", "variants": 1})

    resp = client.post("/api/projects/düğün/layers/video", json={})

    assert resp.status_code == 202
    assert "frames" in resp.get_json()
```

(`make_client` bu dosyada zaten var; bir üretim koşusuna ihtiyaç yok, plan yazılması yeter.)

### Adım 2 — Koş, kırmızı olduğunu gör

`python -m pytest queen-editor -q` → **FAIL**: cevapta `frames` yok.

### Adım 3 — Cevaba galeriyi koy

`routes.py`, `post_generate`:

```python
        # 202: a batch runs for minutes, so the request only reports that the work was accepted.
        # "added" is how many frames the queue took -- the panel quotes it back to the user, and
        # "frames" is the gallery those frames landed in: the screen would ask for it in a second
        # round-trip otherwise, and until that lands the frames it was just told about are nowhere.
        return jsonify({"job": "running", "added": added,
                        "frames": list_frames(project)}), 202
```

`post_layer` de aynı şekilde bitirilir.

### Adım 4 — Koş, yeşil olduğunu gör

`python -m pytest queen-editor -q` → **PASS**.

### Adım 5 — Ön yüzün testlerini yaz

`useGeneration.test.jsx`:

```jsx
  it("puts the queued frames on screen without asking for the gallery again", async () => {
    const rows = [{ id: "P0_0", file: "P0_0.png", status: "pending", owed: ["photo"], failed: [] }];
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([]);
    generateBatch.mockResolvedValue({ added: 1, frames: rows });

    const { result } = renderHook(() => useGeneration("kuyruk"));
    await settle();
    listFrames.mockClear();

    await act(async () => { await result.current.generate({ prompts: "a" }); });

    expect(result.current.frames).toEqual(rows);
    expect(listFrames).not.toHaveBeenCalled();
  });

  it("still asks for the gallery on a path that carries none", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listFrames.mockResolvedValue([]);
    resumeBatch.mockResolvedValue({});

    const { result } = renderHook(() => useGeneration("devam"));
    await settle();
    listFrames.mockClear();

    await act(async () => { await result.current.resume(); });

    expect(listFrames).toHaveBeenCalled();
  });
```

`resumeBatch` mock listesinde zaten var; import satırına eklenmesi gerekebilir.

### Adım 6 — Koş, kırmızı olduğunu gör

`npm test --prefix queen-editor/frontend -- --run` → **FAIL**: ilk test galeriyi ikinci kez
istiyor.

### Adım 7 — Kancayı yaz

`useGeneration.js`:

```js
  // Every way of putting the worker back to work ends the same: believe it is running, re-arm the
  // poll, and know what the gallery looks like. A caller that was handed the gallery by the answer
  // that started the run passes it in -- asking for it again would be the same five reads for the
  // same list.
  const startPolling = useCallback((gallery) => {
    setJob({ status: "running", project });
    wasRunning.current = true;
    clearTimeout(timer.current);
    timer.current = setTimeout(poll, POLL_MS);
    if (gallery) setFrames(gallery);
    else refreshFrames();
  }, [project, poll, refreshFrames]);
```

`generate` ve `queueLayer` içinde `startPolling()` yerine `startPolling(body?.frames)`.

### Adım 8 — Tam takım, derleme, commit

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend -- --run
npm run build --prefix queen-editor/frontend
git add queen-editor docs/superpowers
git commit -m "fix(queen-editor): queued frames come back with the answer that queued them"
```
