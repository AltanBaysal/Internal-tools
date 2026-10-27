# Madde 97 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-27-queenagent-m97-plan-edit-kipinde-uygulama-design.md](../specs/2026-08-27-queenagent-m97-plan-edit-kipinde-uygulama-design.md)
**Tur 1:** bir kırmızı commit'lendi *(`bd26faa`)*. Bu turda test yazılmaz.
**Komut:** `python -m pytest queen-agent -q`

---

## 1 · `domain/modes.py`

Bugünkü satır:

```python
    EDIT: READS + ("create_file", "edit_file", "build_prompts"),
```

Yerine:

```python
    # write_plan is here too since Madde 97: in this mode a plan is an ordinary file, which is
    # exactly why the tool belongs -- the flow writes one to keep its place and carries on in the
    # same turn.
    EDIT: READS + ("create_file", "edit_file", "build_prompts", "write_plan"),
```

`ends_the_turn` ellenmiyor.

## 2 · Koş

```
python -m pytest queen-agent -q
```

Beklenen: `test_edit_mode_can_write_a_plan_too` yeşil, `test_only_a_written_plan_ends_the_turn`
yeşil kalıyor. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 3 · Commit

```
feat(queen-agent): edit mode can write a plan and keep going
```
