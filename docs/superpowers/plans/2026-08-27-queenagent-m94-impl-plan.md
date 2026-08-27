# Madde 94 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-27-queenagent-m94-tek-skill-uygulama-design.md](../specs/2026-08-27-queenagent-m94-tek-skill-uygulama-design.md)
**Bu turda yeni test yazılmaz.** `5173366`'nın dokuz kırmızısı yeşile döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
`npm run build --prefix queen-agent/frontend`

---

## 1 · `backend/features/workspace/domain/skills.py`

### Silinen

`CREATE_SCENARIO`, `CREATE_CHARACTER_PROMPT`, `SPLIT_INTO_FRAMES`, `GENERATE_PROMPTS`,
`VERIFY_PROMPTS` sabitleri ve `INSTRUCTIONS`'taki beş satırı. Dosya sırayla şunları taşıyor:
docstring, `RULEBOOK`, `GENERATE_PROMPTS_PLUS`, tek satırlık `INSTRUCTIONS`, `instruction_for`.

### Docstring

Bugünkü metnin son cümlesi *"and the two skills that produce those say so in as many words"* — tek
metin kaldı. Docstring bu hâle geliyor:

```python
"""What each skill tells the model, and nothing about when it is told.

A product behaviour like prompt.py, so it lives in the domain. Every text is written in the mood
"this is how you do this job" rather than "do this": a selected skill stays selected after a message
is sent, and an instruction in the imperative would start producing something the moment the user
typed "thanks". What to do comes from the user's own sentence.

The instruction texts are English, like the rest of QueenAgent's own words. What the model writes
back follows the user's language (prompt.py); the exception is what an image model reads -- the
prompts and the structure file -- and the skill that produces those says so in as many words.

One text since Madde 94. Five others stood here and were deleted: what they said about how to work
now sits in prompt.py, where it holds whatever is selected, and what they said about their own task
either lives in the text below or went with them on purpose. The picker still exists and still has
an empty state -- having no skill selected is ordinary, and the list will grow again.
"""
```

### `RULEBOOK`'un üstündeki yorum

Bugün *"One text, two readers: the structured skill checks itself against it before it builds, and
Verify applies it whenever it is asked to. Two copies would come apart on the first change to
either."* diyor. İkinci okuyucu gitti, ama sabitin ayrı durmasının bir sebebi kaldı:

```python
# Its own constant rather than a paragraph in the text below: these are the rules, and keeping them
# in one place is what makes them countable and quotable. Verify was the second reader until Madde
# 94; the one that stayed applies them before it builds.
```

### `INSTRUCTIONS`

```python
INSTRUCTIONS = {
    "generate-prompts-plus": GENERATE_PROMPTS_PLUS,
}
```

`instruction_for` ve docstring'i değişmiyor.

## 2 · `frontend/src/features/workspace/skills.js`

Dosya bu hâle iniyor:

```javascript
// One row since Madde 94, which deleted the other five. Not zero rows: having no skill selected is
// an ordinary state, so even a one-row list carries two -- and the list will grow again.
//
// The second line says what a skill does and, where it applies, that a file comes out of it: a file
// appearing unasked is the surprising part, so the menu says it before the user finds out.
export const SKILLS = [
  {
    id: "generate-prompts-plus",
    name: "Generate prompts+",
    detail: "Build from parts, so a character never drifts.",
  },
];

// No skill is the ordinary state, so the empty case is the button's own word rather than a gap. A
// record can still name one of the five: the button says its id rather than going blank.
export function skillName(id) {
  if (!id) return "Skills";
  return SKILLS.find((skill) => skill.id === id)?.name ?? id;
}
```

`skillName`'in gövdesi değişmiyor; yalnız yorumu `?? id` kolunun artık gerçek bir kullanıcısı
olduğunu söylüyor.

## 3 · Derleme

```
npm run build --prefix queen-agent/frontend
```

`skills.js` bir ön yüz kaynağı. CLAUDE.md derlenmiş çıktının kaynakla **aynı commit'te** inmesini
istiyor: defter bu depoyu klonluyor ve hiç derlemiyor, yani derlenmemiş bir değişiklik orada
görünmüyor. `queen-agent/frontend/dist` commit'e giriyor.

## 4 · Doğrulama

| Ölçü | Beklenen |
|---|---|
| `python -m pytest queen-agent -q` | yalnız `test_notebook`'un ikisi kırmızı |
| `npm test --prefix queen-agent/frontend` | hepsi yeşil |

Dokuz kırmızının karşılığı:

| Test | Silme |
|---|---|
| `test_a_deleted_skill_carries_nothing` × 5 | `INSTRUCTIONS`'ın beş satırı |
| `test_only_one_skill_is_offered` | aynı beş satır |
| `test_the_rulebook_has_one_reader_now` | `VERIFY_PROMPTS` |
| `the one skill left is the one that builds` | `SKILLS`'in beş satırı |
| `a deleted skill keeps its id on the screen` | aynı beş satır |

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`GENERATE_PROMPTS_PLUS` ve `RULEBOOK`'un metinleri açılmaz** — yalnız `RULEBOOK`'un üstündeki
  yorum değişiyor, çünkü söylediği şey artık doğru değil.
- **`prompt.py`, `modes.py`, `tools.py`, `stream_answer.py` açılmaz.**
- **`SkillPicker.jsx`, `ChatScreen.jsx`, `ProjectScreen.jsx`, `App.jsx` açılmaz.**
- **Diskteki kayıtlar dönüştürülmez.**
