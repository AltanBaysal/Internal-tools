# Madde 394 — Improve · uygulama turu planı

> **Ajanlar için:** bu plan satır satır, bu oturumda yürütülür (superpowers:executing-plans'ın
> biçimiyle); adımlar `- [ ]` kutularıyla.

**Amaç:** Improve'u üçüncü skill olarak kaydetmek ve seçicinin son satırı yapmak; test turunun kırmızı 17 + 3
testini yeşile çevirmek.

**Yapı:** Arka uçta `INSTRUCTIONS`'a bir satır, ön uçta `SKILLS`'e bir satır; iki skill sayan üç yorum üçü
söyler. `dist` yeniden derlenir ve kaynakla aynı commit'e girer.

**Araçlar:** Flask arka ucu (değişmez), React 18 + Vite.

**Spec:** [2026-09-30-queenagent-m394-improve-uygulama-design.md](../specs/2026-09-30-queenagent-m394-improve-uygulama-design.md)

## Genel kısıtlar

- `IMPROVE`, `START_A_SCENARIO`, `EDIT_PROMPTS`'un tek kelimesi değişmez; `prompt.py`'de yalnız bir yorum
  paragrafı değişir.
- Dört test satırı, yazıldığı gibi, paralel; iki `npm` satırı arka planda, özetleri çıktı dosyalarından okunur.
- `skip`, `xfail`, `.skip`, `.todo` yok.
- Yorumlar İngilizce, neden'i ve yalnız bugün doğru olanı söyler; satırlar 100 karakteri geçmez.
- Commit mesajı İngilizce, çift tırnaksız, PowerShell tek tırnaklı here-string ile; amend yok.

---

### Görev 1: Arka uçta kayıt ve iki yorum

**Dosyalar:**
- Değişir: `queen-agent/backend/features/workspace/domain/skills.py`
- Değişir: `queen-agent/backend/features/workspace/domain/prompt.py` (yalnız yorum)

**Arayüz:**
- Üretir: `INSTRUCTIONS["improve"] == prompt.IMPROVE`; `instruction_for("improve")` Improve'un metnini döner.

- [ ] **Adım 1: `skills.py`**

```python
"""Which skill carries which instruction, and nothing about what the instruction says.

The texts themselves are in prompt.py since Madde 189, beside everything else the model is told.
What is left here is the mapping: the picker's ids on one side, a text on the other. It is a
product behaviour like the texts are, so it stays in the domain.

Three texts: two since Madde 101, and Improve since Madde 394. Five others stood beside the first
two and were deleted in Madde 94. The picker still has an empty state -- having no skill selected
is ordinary, and the base text holds anyway.
"""
from backend.features.workspace.domain import prompt

INSTRUCTIONS = {
    "start-a-scenario": prompt.START_A_SCENARIO,
    "edit-prompts": prompt.EDIT_PROMPTS,
    "improve": prompt.IMPROVE,
}
```

- [ ] **Adım 2: `prompt.py`'de skill metinlerinin üstündeki ikinci paragraf**

Eski:

```python
# Two texts since Madde 101. Five others stood beside them and were deleted in Madde 94: what they
# said about how to work now sits in SYSTEM_PROMPT, where it holds whatever is selected. The picker
# still has an empty state -- having no skill selected is ordinary.
```

Yeni:

```python
# Three texts. Two since Madde 101, and Improve since Madde 394: Start a scenario's checks and its
# negative list, copied word for word into a skill of its own for a scenario that already exists --
# the owner's decision, so the copy is meant and is not to be joined back into a shared block.
# Five others stood beside the first two and were deleted in Madde 94: what they said about how to
# work now sits in SYSTEM_PROMPT, where it holds whatever is selected. The picker still has an
# empty state -- having no skill selected is ordinary.
```

### Görev 2: Ön uçta satır ve derleme

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/features/workspace/skills.js`
- Yeniden derlenir: `queen-agent/frontend/dist/`

**Arayüz:**
- Kullanır: `improve` kimliği (Görev 1'deki `INSTRUCTIONS` anahtarıyla aynı).

- [ ] **Adım 1: `skills.js`**

```js
// Three rows: two since Madde 101, and Improve since Madde 394 -- Madde 94 said more would come.
// Not zero rows even at one: having no skill selected is an ordinary state.
//
// The flow comes first because that is the answer to "which do I want": somebody with nothing yet
// takes the flow, somebody who already has prompts takes the editor. Since Madde 186 the two are
// the halves of the work rather than two roads into it -- the flow runs all the way to the built
// file, so nobody comes out of it needing a second row to finish. Improve, last, is not that
// second row: it runs the flow's checks again on a scenario that already exists. Its line is not
// the design's placeholder, which asked for a yes after each step -- Improve's steps wait for none.
export const SKILLS = [
  {
    id: "start-a-scenario",
    name: "Start a scenario",
    detail: "Answer a few questions and get the characters, the places and the prompts.",
  },
  {
    id: "edit-prompts",
    name: "Edit prompts",
    detail: "Fix what is wrong in prompts you already have, and build them again.",
  },
  {
    id: "improve",
    name: "Improve",
    detail: "Check a scenario you already have, fix what fails, and write its negative list again.",
  },
];
```

- [ ] **Adım 2: Derle** — `npm run build --prefix queen-agent/frontend`.

### Görev 3: Yeşili gör ve commit'le

- [ ] **Adım 1: Dört satırı paralel koş** — iki `npm` satırı arka planda.

Beklenen: dört süit de yeşil; test turunun 17 + 3 kırmızısı dahil. Kelime tavanı kırmızıysa pytest gerçek
sayıyı gösterir — metin değişmez; sayım yanlışsa tavan ve gerekçesi o sayıya göre düzeltilir.

- [ ] **Adım 2: Commit** — `prompt.py`, `skills.py`, `skills.js`, `dist`, bu spec ve plan.

```powershell
git add queen-agent/backend/features/workspace/domain/prompt.py queen-agent/backend/features/workspace/domain/skills.py queen-agent/frontend/src/features/workspace/skills.js queen-agent/frontend/dist docs/specs/2026-09-30-queenagent-m394-improve-uygulama-design.md docs/plans/2026-09-30-queenagent-m394-improve-uygulama-plan.md
git commit -m @'
feat(queen-agent): 394 -- Improve is a third skill, last in the picker

Improve checks a scenario that already exists: its text, written with the
owner line by line, is Start a scenario's Steps 6 to 10 copied word for
word and numbered 1 to 5, with the six rules of Step 5 in its context and
the prompts built once before the steps. It is registered beside the other
two, and the picker lists it after Edit prompts with a line that promises
no approval, since its steps wait for none. The comments that counted two
skills say three. dist is rebuilt with the source.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
