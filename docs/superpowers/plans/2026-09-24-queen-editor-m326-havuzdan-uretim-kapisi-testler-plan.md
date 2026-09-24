# Madde 326 — Havuzdan üretim kapısı, test turunun planı

**Hedef:** Spec'in tek testi, iki video modeliyle — kırmızı.

**Spec:** [m326 test turu](../specs/2026-09-24-queen-editor-m326-havuzdan-uretim-kapisi-testler-design.md)

## Görev 1: Test

`test_composition_root.py`'nin sonuna:

```python
@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_hands_a_reference_run_to_the_use_case(import_main, video_model):
    """Madde 326: main.py hung this door with an argument queue_references does not take, and every
    press came back 500 -- the door's own tests wire it by hand. A missing project is the use case's
    first question, so its answer proves the call got in."""
    main = import_main(video_model)

    response = main.app.test_client().post("/api/projects/m326-yok/references/produce",
                                           json={"prompts": '["a"]', "variants": 1})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m326-yok"}
```

## Görev 2: Koşu ve kırmızı commit

- [ ] Dört satır — `queen-editor` pytest'te iki kırmızı *(500)*, geri kalan yeşil.
- [ ] `test(m326): …(red)`.
