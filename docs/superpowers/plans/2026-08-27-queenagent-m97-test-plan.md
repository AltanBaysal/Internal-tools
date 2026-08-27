# Madde 97 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m97-plan-edit-kipinde-testler-design.md](../specs/2026-08-27-queenagent-m97-plan-edit-kipinde-testler-design.md)
**Bu turda kod yazılmaz.** Bir test kırmızıya döner, bir testin adı düzelir.
**Komut:** `python -m pytest queen-agent -q`

---

## 1 · `backend/tests/test_modes.py`

`test_edit_mode_carries_the_five_it_always_had` bu hâle geliyor — adı da, kümesi de:

```python
def test_edit_mode_can_write_a_plan_too():
    # Madde 97: the flow works in this mode because it writes files, and it keeps its place in a
    # plan. Without the tool here its first step cannot be taken at all.
    assert _offered("edit") == READS | {
        "create_file",
        "edit_file",
        "build_prompts",
        "write_plan",
    }
```

Eski adındaki *"the five it always had"* zaten yalan söylemeye başlamıştı: 96 kipe altıncıyı verdi.

## 2 · `backend/tests/test_stream_answer.py` — ad düzeltmesi

```python
def test_a_turn_that_names_no_mode_carries_the_writing_tools(tmp_path):
    # The retry road sends no mode of its own, and neither does any caller written before this.
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "Hi"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER))
    assert "create_file" in engine.tools[0]
```

Gövdesi aynı; değişen yalnız sayı sayan ad. Bugün de yarın da yeşil.

## 3 · Yerinde kalan bekçi

`test_only_a_written_plan_ends_the_turn` dokunulmadan duruyor:

```python
    assert ends_the_turn("plan", "write_plan")
    assert not ends_the_turn("edit", "write_plan")
    assert not ends_the_turn("plan", "read_file")
```

Ortadaki satır bu maddenin bekçisi: araç edit kipine girdikten sonra da turu bitirmemeli.

## 4 · Koş

```
python -m pytest queen-agent -q
```

Beklenen: `test_modes.py::test_edit_mode_can_write_a_plan_too` kırmızı, başka hiçbir şey değişmiyor.
**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 5 · Commit

```
test(queen-agent): red for a plan written in the mode that writes
```
