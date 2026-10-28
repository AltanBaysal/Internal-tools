# Madde 331 · H3'ün video prompt yazarı `dynv2` yazmıyor — test turunun planı

**Spec:** [test turu](../specs/2026-09-24-queen-editor-m331-dynv2-yok-testler-design.md) ·
**Tur:** 1/2 — yalnız testler, kaynak kod değişmiyor.

**Hedef:** talimatın `dynv2`'den hiç söz etmediğini soran test kırmızı commit'leniyor; üreticinin elle
eklenen `dynv2`'yi öne alan testleri bekçi olarak yeşil kalıyor.

## Görev 1 — `test_video_prompt_writer.py`

**Dosya:** `queen-editor/backend/tests/test_video_prompt_writer.py` — 85–94. satırlardaki test.

- [ ] **Adım 1: testi değiştir.** `test_the_h3_instruction_opens_with_dynv2_unless_the_scene_is_calm`
  yerine:

```python
def test_the_h3_instruction_never_asks_for_dynv2():
    """Madde 331: the writer leaves the trigger out of every scene -- the user's call, "hiç
    yazılmasın ... istediğin prompt'a elle eklersin". Asked of what the writer actually sends, loop
    included, so no rule appended to the instruction can bring the word back. Adding it by hand still
    works: the producer puts a leading dynv2 first (test_comfy_h3_video_generator)."""
    _instruction, writer = _h3()
    client = FakeClient()

    for mode in ("standard", "loop"):
        writer(client).write({"photo": "kırmızı elbiseli kadın"}, mode)

    for sent, _photo in client.calls:
        assert "dynv2" not in sent, f"Talimat hâlâ dynv2 istiyor:\n{sent}"
```

- [ ] **Adım 2: dört satırı koş**, yazıldığı gibi ve paralel:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'te yalnız `test_the_h3_instruction_never_asks_for_dynv2` kırmızı —
`Talimat hâlâ dynv2 istiyor`; geri kalan her şey yeşil.

- [ ] **Adım 3: commit** — test dosyası, spec ve bu plan:

```
test(m331): the H3 writer's instruction never asks for dynv2, standard or loop (red)
```
