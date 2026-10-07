# Madde 371 — Kontrol: yalnız görünen parçalar: test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** İkinci kontrolü *(yalnız görünen parçalar)* tutan testler. Yalnız test; metin ve kod yok.

**Mimari:** Kontrol `prompt.THE_CHECKS`'te duracak; testler kontrolün kendi bloğunu — başlığından
kapanış cümlesine kadar — dilimleyip olgularını orada sorar.

**Teknoloji:** pytest.

**Spec:** [2026-09-29-queenagent-m371-gorunen-parcalar-testler-design.md](../specs/2026-09-29-queenagent-m371-gorunen-parcalar-testler-design.md)

## Genel kısıtlar

- Testler İngilizce; yorum NEDEN'i söyler.
- `skip`/`xfail`/`.skip`/`.todo` yok.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşar.
- Commit mesajında çift tırnak yok, amend yok.
- Başlık birebir: `Check 2 -- visible parts`. Kapanışın başı birebir: `When the checks are done`.

---

### Görev 1: `test_skills.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_skills.py` (370'in bölümünün sonuna,
`test_improve_opens_as_a_persona_on_a_scenario_already_built`'ten sonra)

**Arayüzler:** Kullanır: `_checks()` (aynı dosya, `THE_CHECKS`'i döner).

- [ ] **Adım 1:** Yeni bölüm:

```python
# --- the second check: only what the angle shows (Madde 371) --------------------------------------
#
# 29 Sep, the user: from the angle a frame is seen at, write only the parts of each character that
# show -- a weak model hands a part it cannot place to the other characters. The angle is written into
# the action (Step 5), and a frame names whole entries, so a part is left out by an entry of its own
# (the roadmap's examples: man body no face, an outfit from behind) that the frame's cast then names.

SECOND_CHECK = "Check 2 -- visible parts"
CLOSING = "When the checks are done"


def _second_check():
    checks = _checks()
    return checks[checks.index(SECOND_CHECK) : checks.index(CLOSING)]


def test_the_second_check_comes_after_the_first_and_before_the_closing():
    checks = _checks()
    assert SECOND_CHECK in checks
    assert checks.index("Check 1 -- one moment") < checks.index(SECOND_CHECK)
    assert checks.index(SECOND_CHECK) < checks.index(CLOSING)


def test_the_second_check_reads_what_the_angle_shows():
    said = _second_check()
    assert "angle" in said
    assert "no face" in said
    assert "from behind" in said


def test_a_part_the_angle_hides_goes_through_an_entry_of_its_own():
    # The whole entry stays as it is: other frames show the same person whole, and one change to it
    # reaches every frame naming it.
    said = _second_check()
    for tool in ("add_character", "add_outfit", "update_frame"):
        assert tool in said, tool
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "update_character" not in said
    assert "update_outfit" not in said
```

### Görev 2: Kırmızı

- [ ] Dört satır, paralel, olduğu gibi. Beklenen kırmızı yalnız bu üç test *(`SECOND_CHECK` metinde
  yok: `index` `ValueError` verir ya da `in` iddiası düşer)*; geri kalanı yeşil.
- [ ] Commit: `test(queen-agent): Madde 371 red -- the second check keeps only what the angle shows`
