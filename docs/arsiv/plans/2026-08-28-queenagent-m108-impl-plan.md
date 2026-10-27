# Madde 108 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m108-devir-uygulama-design.md](../specs/2026-08-28-queenagent-m108-devir-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/backend/features/workspace/domain/skills.py` — `START_A_SCENARIO`

1. Giriş: `"Four steps in a fixed order"` → `"Five steps in a fixed order"`.
2. Son paragraf (`"That is where this skill stops. …"`) yerine:

```python
    "5. The handoff. The foundation is standing -- characters, places, scenes -- and this skill's "
    "work ends with this message: name the two files, say the scenario is ready, and send the "
    "user to Generate prompts+ in the skills menu, which reads the scene list, writes each scene "
    "as a detailed frame, and builds the prompt list. Frames are never written here, not even "
    "when the user asks for them: writing them in batches and choosing a frame's camera are that "
    "skill's own work, so the ask is answered by pointing there. Like the plan, this step waits "
    "for no approval -- it is the last word."
```

## B. Doğrulama ve kapanış

1. İki suite koşulur; iki kırmızı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `dist` derlenmez — ön yüz değişmiyor.
3. Commit: `skills.py` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **prompt+ metni ve `skills.js` ellenmez** *(113)*.
- **Test dosyaları değişmez.**
