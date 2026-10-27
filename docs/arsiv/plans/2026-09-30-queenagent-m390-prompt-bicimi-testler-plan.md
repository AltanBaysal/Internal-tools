# Madde 390 — prompt biçimi: test planı

> **Ajanlar için:** superpowers:executing-plans ile görev görev uygulanır; adımlar `- [ ]` ile izlenir.

**Amaç:** v9'un modele giden metinlerinde v9 öncesi biçimi bozan tek yeri kırmızı bir testle tutmak.

**Yaklaşım:** `test_skills.py`'ye üç skill için parametreli tek test; yalnız test yazılır.

**Araçlar:** pytest.

**Spec:** [2026-09-30-queenagent-m390-prompt-bicimi-testler-design.md](../specs/2026-09-30-queenagent-m390-prompt-bicimi-testler-design.md)

## Genel kısıtlar

- Yalnız biçim; modele söylenen hiçbir şey değişmez.
- Testler dört satırla koşulur, yazıldığı gibi, paralel: `python -m pytest queen-agent -q` ·
  `npm test --prefix queen-agent/frontend` · `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend`.
- `skip`/`xfail` yok. Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: Kullanıcının sözü tırnak içinde

**Dosyalar:**
- Değişir: `queen-agent/backend/tests/test_skills.py` (dosyanın sonuna)

- [ ] **Adım 1: Testi yaz**

```python
# --- how the texts are written (Madde 390) --------------------------------------------------------
#
# 30 Sep, the user: the prompts written in v9 are to follow the format of the ones before them. Only
# what v9 broke is pinned here; the conventions and the check of every part are in the madde's spec.


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_a_word_the_user_says_is_written_in_quotation_marks(skill):
    # Before v9 the user's own words stand in double quotes -- "You decide", and the refusal's They
    # said: "..." -- so the model reads them as the user's rather than as the text's own. Every
    # skill carries the checks, which is where the phrase is.
    said = instruction_for(skill)
    assert "the user says " in said
    for rest in said.split("the user says ")[1:]:
        assert rest.startswith('"'), (skill, rest[:30])
```

- [ ] **Adım 2: Dört satırı koş, üç yeni testin kırmızı olduğunu gör**

Beklenen: `test_a_word_the_user_says_is_written_in_quotation_marks[edit-prompts|improve|start-a-scenario]`
`assert False` ile düşer (`continue, carry on from there.`); başka test düşmez.

- [ ] **Adım 3: Kırmızıyı commit'le**

```
git add queen-agent/backend/tests/test_skills.py docs/specs/2026-09-30-queenagent-m390-prompt-bicimi-testler-design.md docs/plans/2026-09-30-queenagent-m390-prompt-bicimi-testler-plan.md
git commit -m "test(queen-agent): Madde 390 red -- the user's word in the checks is quoted as before v9"
```
