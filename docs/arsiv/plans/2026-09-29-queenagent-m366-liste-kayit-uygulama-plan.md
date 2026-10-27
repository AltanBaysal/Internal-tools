# Madde 366 — Liste yeni biçimde çıkar: uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Kırmızı commit'in (`60fe9e35`) testlerini kodla yeşile getirmek.

**Mimari:** `build_prompts` her kare için `{"scene", "photo"}` kaydı döndürür; `render_module` kayıtları üç tırnakla yazar; `build_prompts` aracının tarifi sahneyi anar.

**Teknoloji:** Python, pytest.

**Spec:** [2026-09-29-queenagent-m366-liste-kayit-uygulama-design.md](../specs/2026-09-29-queenagent-m366-liste-kayit-uygulama-design.md)

## Genel kısıtlar

- Kod ve modele giden metin İngilizce; yorum NEDEN'i ve yalnız bugünü söyler.
- Skill metinleri ve kelime tavanları değişmez.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşar. Commit'te çift tırnak yok.

---

### Görev 1: `build_prompts.py`

**Dosya:** `queen-agent/backend/features/workspace/domain/build_prompts.py`

- [ ] **Adım 1:** Modül docstring'inde "hands back strings" → "hands back the list".
- [ ] **Adım 2:** `build_prompts`'un docstring'i ve eklediği satır:

```python
def build_prompts(structure):
    """Every frame as its scene and its photo prompt, or a sentence saying why none can be built."""
    ...
        blocks = [opening] + behind + [closing]
        # The scene rides beside the prompt as it was written (Madde 366): queen-editor writes the
        # video prompt, and the model doing it is shown what the frame was meant to be. A frame
        # without one still builds -- a missing sentence is no reason to lose the list.
        built.append(
            {
                "scene": frame.get("scene", ""),
                "photo": BREAK.join(tags for tags in map(_tags, blocks) if tags),
            }
        )
```

- [ ] **Adım 3:** `render_module`:

```python
def render_module(records):
    """The file the user copies out of: a record per frame, each value in triple quotes."""
    lines = ["PROMPTS = ["]
    for record in records:
        lines.append("    {")
        lines.extend(f'        "{field}": """{_quoted(record[field])}""",' for field in ("scene", "photo"))
        lines.append("    },")
    lines.append("]")
    return "\n".join(lines) + "\n"
```

### Görev 2: `prompt.py`

**Dosya:** `queen-agent/backend/features/workspace/domain/prompt.py`

- [ ] `BUILD_PROMPTS`'un ilk satırı:
  `"Build the prompt list from a structure file: for each frame, its scene sentence and its prompt.\n"`

### Görev 3: Yeşil

- [ ] Dört satır, paralel, olduğu gibi; dördü de yeşil.
- [ ] Commit: `feat: Madde 366 -- the prompt list goes out as scene and photo records`
