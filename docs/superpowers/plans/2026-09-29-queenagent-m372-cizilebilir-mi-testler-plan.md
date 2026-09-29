# Madde 372 — Kontrol: çizilebilir mi — test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** `THE_CHECKS`'in üçüncü kontrolünü (çizilebilir mi) isteyen testler, kırmızı.

**Mimari:** Yalnız `test_skills.py`. 371'in yardımcısı `_second_check()` kendi bloğunda biter; yeni
bölüm `_third_check()` ile Check 3 bloğunu keser ve olgularını sorar.

**Teknoloji:** pytest.

**Spec:** [testler spec'i](../specs/2026-09-29-queenagent-m372-cizilebilir-mi-testler-design.md)

## Genel kısıtlar

- Dört test satırı, yazıldığı gibi, paralel; boru, filtre, daraltma yok.
- `skip` / `xfail` yok.
- Tavanlar değişmez: akış 1000, Edit prompts 700, Improve 700.
- Test adları ve yorumlar İngilizce.

---

### Görev 1: Check 3'ün testleri

**Dosyalar:**
- Değişir: `queen-agent/backend/tests/test_skills.py` — `_second_check()` ve 371 bölümünün arkası.

- [ ] **Adım 1: `_second_check()` kendi bloğunda biter**

```python
def _second_check():
    # Ends at the blank line that closes its own block, so a check written after it (372) is not
    # read as part of this one.
    checks = _checks()
    start = checks.index(SECOND_CHECK)
    return checks[start : checks.index("\n\n", start)]
```

- [ ] **Adım 2: 371 bölümünün arkasına yeni bölüm**

```python
# --- the third check: can the model draw it (Madde 372) -------------------------------------------
#
# 29 Sep, the user: the image model is very weak -- could it draw the prompt you wrote? The check
# reads the prompts in their final form, after the first two, and simplifies what cannot be drawn.
# A photo prompt is put together by build_prompts from a frame's action and the entries it names, so
# a part is simplified where it comes from: the action through update_frame, an entry through its own
# update_ tool. THE_IMAGE_MODEL already says the model is weak; the check does not say it again.

THIRD_CHECK = "Check 3 -- can it be drawn"


def _third_check():
    checks = _checks()
    start = checks.index(THIRD_CHECK)
    return checks[start : checks.index("\n\n", start)]


def test_the_third_check_comes_after_the_second_and_before_the_closing():
    checks = _checks()
    assert THIRD_CHECK in checks
    assert checks.index(SECOND_CHECK) < checks.index(THIRD_CHECK) < checks.index(CLOSING)


def test_the_third_check_reads_the_prompts_in_their_final_form():
    said = _third_check()
    assert "build_prompts" in said
    assert "final" in said
    assert "photo prompt" in said


def test_the_third_check_simplifies_the_part_where_it_comes_from():
    said = _third_check()
    assert "simplif" in said.lower()
    for tool in ("update_frame", "update_character", "update_outfit", "update_location"):
        assert tool in said, tool


def test_the_third_check_does_not_tell_the_model_is_weak_again():
    from backend.features.workspace.domain.prompt import THE_IMAGE_MODEL

    said = _third_check()
    # Asked after the block is found, so the absence cannot pass on a text nobody wrote.
    assert said.startswith(THIRD_CHECK)
    assert "weak" not in said.lower()
    assert THE_IMAGE_MODEL not in _checks()
```

- [ ] **Adım 3: Dört satırı çalıştır** — `python -m pytest queen-agent -q`,
  `npm test --prefix queen-agent/frontend`, `python -m pytest queen-editor -q`,
  `npm test --prefix queen-editor/frontend`. Beklenen: yalnız yeni dört test kırmızı (`ValueError` ya
  da `AssertionError`); 371'in üç testi yeşil.

- [ ] **Adım 4: Commit**

```
test(queen-agent): Madde 372 red -- the third check asks whether the model can draw it
```
Spec ve plan aynı commit'te.
