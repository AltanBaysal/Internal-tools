# Madde 113 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m113-duzenleme-uygulama-design.md](../specs/2026-08-28-queenagent-m113-duzenleme-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `skills.py` — `GENERATE_PROMPTS_PLUS`

1. Açılış:

```python
    "When the user wants the prompts of a scenario built or changed, this is the skill for both. "
    "A prompt is never written out by hand: characters, outfits and places live in the structure "
```

2. Metnin sonuna, `build_prompts` paragrafından sonra:

```python
    "\n"
    "When the user comes back unhappy with a prompt, changing it is the same road: find the frame "
    "it came from -- the built list runs in the frames' order -- fix what is wrong with "
    "edit_file, and call build_prompts again. What is wrong is either the frame's own action or "
    "camera, or the entry in a map the frame names: a map entry is the one edit that reaches "
    "every frame naming it. The prompt file is written from the structure file every time, so it "
    "is rebuilt rather than patched, and never edited by hand."
```

## B. `skills.js`

```js
    detail: "Build the prompts from a structure file you already have, and change them later.",
```

## C. Doğrulama ve kapanış

1. İki suite; üç kırmızı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `npm run build --prefix queen-agent/frontend` — `dist` kaynakla aynı commit'te.
3. Commit: `skills.py` + `skills.js` + `dist` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **Akış metni ellenmez** *(108 kapandı)*.
- **Şema ellenmez** *(109, 110, 111)*.
- **Test dosyaları değişmez.**
