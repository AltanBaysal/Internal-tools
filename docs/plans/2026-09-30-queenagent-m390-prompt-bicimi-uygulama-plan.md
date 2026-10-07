# Madde 390 — prompt biçimi: uygulama planı

> **Ajanlar için:** superpowers:executing-plans ile görev görev uygulanır; adımlar `- [ ]` ile izlenir.

**Amaç:** `THE_CHECKS`'te kullanıcının sözünü v9 öncesi gibi çift tırnağa almak, ve kırmızı testi yeşile çevirmek.

**Yaklaşım:** `prompt.py`'de tek satırlık metin düzeltmesi; başka hiçbir şeye dokunulmaz.

**Araçlar:** pytest.

**Spec:** [2026-09-30-queenagent-m390-prompt-bicimi-uygulama-design.md](../specs/2026-09-30-queenagent-m390-prompt-bicimi-uygulama-design.md)

## Genel kısıtlar

- Yalnız biçim; modele söylenen hiçbir şey değişmez, kelime sayısı değişmez.
- Testler dört satırla koşulur, yazıldığı gibi, paralel: `python -m pytest queen-agent -q` ·
  `npm test --prefix queen-agent/frontend` · `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend`.
- Commit mesajında çift tırnak yok, amend yok. dist değişmez (frontend'e dokunulmuyor).

---

### Görev 1: Söz tırnak içinde

**Dosyalar:**
- Değişir: `queen-agent/backend/features/workspace/domain/prompt.py` (`THE_CHECKS`'in ikinci maddesi)
- Test: `queen-agent/backend/tests/test_skills.py::test_a_word_the_user_says_is_written_in_quotation_marks` (commit'li, kırmızı)

- [ ] **Adım 1: Metni düzelt**

Önce:

```python
    "than one turn, and when the user says continue, carry on from there.\n"
```

Sonra (v9 öncesindeki `one \"you decide\"` gibi kaçışlı çift tırnak):

```python
    "than one turn, and when the user says \"continue\", carry on from there.\n"
```

- [ ] **Adım 2: Dört satırı koş, yeşili gör**

Beklenen: queen-agent pytest'te üç yeni test geçer, hiçbir test düşmez; kelime tavanı testi geçer.

- [ ] **Adım 3: Commit**

```
git add queen-agent/backend/features/workspace/domain/prompt.py docs/specs/2026-09-30-queenagent-m390-prompt-bicimi-uygulama-design.md docs/plans/2026-09-30-queenagent-m390-prompt-bicimi-uygulama-plan.md
git commit -m "feat: Madde 390 -- the checks quote the user's word, as the texts before v9 do"
```
