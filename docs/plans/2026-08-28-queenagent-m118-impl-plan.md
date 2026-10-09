# Madde 118 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m118-kurucu-uygulama-design.md](../specs/2026-08-28-queenagent-m118-kurucu-uygulama-design.md)
**Testler kırmızı commit'te** *(tur 1)*; bu tur yalnız `skills.py`'a dokunur.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/features/workspace/domain/skills.py` — `START_A_SCENARIO` 5. adım

*"...so the ask is answered by pointing there."* ile *"Like the plan, this step waits for no
approval"* arasına:

```python
    "skill's own work, so the ask is answered by pointing there. build_prompts is never called "
    "here either: the builder is that skill's too, and the file this flow leaves holds no frames "
    "for it to build from. The handoff offers nothing and asks nothing -- it states what is "
    "standing and where the work continues, and the next move is the user's in the skills menu. "
    "Like the plan, this step waits for no approval -- it is the last word."
```

## Beklenen yeşil

`test_skills.py` iki yenisiyle beraber tamamı; `test_notebook`'un ikisi dal yaşadıkça kırmızı ve
bu maddenin değil. Frontend'e dokunulmadı, suite olduğu gibi yeşil.

## Bilerek yapılmayanlar

- **`modes.py`, taban yönerge, 2. adımın teklifi ellenmez** — gerekçeleri tasarımda.
- **`dist` derlenmez.**
