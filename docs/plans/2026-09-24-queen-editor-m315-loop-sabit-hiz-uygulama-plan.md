# Madde 315 — Loop kuralı sabit hız da istiyor, implementasyon turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `73f11ff0`'ın kırmızısı yeşile dönsün.

**Spec:** [m315 implementasyon turu](../specs/2026-09-24-queen-editor-m315-loop-sabit-hiz-uygulama-design.md)

---

## Görev 1: `xai_prompt_writer.py`

**Dosya:** `queen-editor/backend/features/photo_generation/data/xai_prompt_writer.py`

- [ ] **Adım 1: Yorumun sonuna, `LOOP_RULE = """`'un hemen üstüne:**

```python
#
# The last sentence asks for one speed to the end (madde 315). Most generators ease the subject
# toward stillness in the last frames, and asking for a cycle does not forbid that; H3's own loop
# advice asks for a constant speed too. Words can lessen the ease, not remove it -- the fix that does
# gives the seam a few frames of motion from both sides, and waits in the backlog.
```

- [ ] **Adım 2: `LOOP_RULE`'un son satırı olarak:**

```
Keep the same speed from the first frame to the last: the motion must not slow down toward the end.
```

## Görev 2: Koşu, commit'ler

- [ ] **Adım 1: Dört satırı koş** — dördü de yeşil.
- [ ] **Adım 2: Yeşil commit** — `xai_prompt_writer.py`, bu spec ve bu plan: `feat(m315): …`.
- [ ] **Adım 3: Yol haritası** — 315 ✅, *Kapandı* notu, *Durum: 24/24*; ayrı `docs(m315)` commit'i.
