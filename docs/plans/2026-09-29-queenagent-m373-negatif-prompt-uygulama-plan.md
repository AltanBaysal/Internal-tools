# Madde 373 — Negatif prompt — uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Kırmızı commit `d0dd9b6b`'nin 13 testini yeşile çevirmek: `THE_CHECKS`'e Check 4, kapanışta
iki dosya, ve negatif listeyi `<kök>-negative.txt`'ye yazan `write_negative` aracı.

**Mimari:** Metin `prompt.py`'de; dosya adı `build_prompts.py`'de, `prompts_name`'in yanında; araç
`tools.py`'de, `_build`'in yanında; mod izni `modes.py`'de. Frontend değişmez.

**Teknoloji:** Python, pytest.

**Spec:** [uygulama spec'i](../specs/2026-09-29-queenagent-m373-negatif-prompt-uygulama-design.md)

## Genel kısıtlar

- Dört test satırı, yazıldığı gibi, paralel; boru, filtre, daraltma yok.
- Testlere dokunulmaz; `skip` / `xfail` yok.
- Tavanlar: akış 1025, Edit prompts 700, Improve 700.
- Modele giden metin İngilizce, kısa, düz.

---

### Görev 1: Metin — `prompt.py`

- [ ] **Adım 1:** `THE_CHECKS`'te Check 3 bloğundan sonra, kapanıştan önce:

```python
    "Check 4 -- the negative prompt\n"
    "- Write one negative prompt for the scenario from its cast as it stands, and give it whole to "
    "write_negative: it is rewritten, never added to.\n"
    "- It keeps one character's features off another, but it works on the whole picture, so never "
    "write a character's own feature: dark skin in it turned the man white.\n"
    "- Write the opposite of that feature instead, in words only its owner fits: pale male, white "
    "man for a dark-skinned man. Where that cannot be done, leave it out: the entries keep a "
    "feature on its owner.\n"
    "- It changes no frame. Show the list and wait for their yes.\n"
    "\n"
```

- [ ] **Adım 2:** Kapanış:

```python
    "When the checks are done, close by naming the prompt file and the negative file, and saying "
    "they are ready. Do not print the prompts back, offer nothing, and ask nothing: this is the "
    "last word."
```

- [ ] **Adım 3:** `THE_CHECKS` docstring'inde "The next check (373) goes in after Check 3…" cümlesi,
  kapanışın son kontrole ait olduğunu söyleyen cümleye iner; sona Check 4'ün gerekçesi eklenir
  (liste bütün resme işler; kendi dosyası çünkü kullanıcı elle kopyalar; bütün yazılır çünkü 374 kadro
  değişince yeniden yazar).

- [ ] **Adım 4:** `BUILD_PROMPTS`'tan sonra:

```python
WRITE_NEGATIVE = (
    "Write a scenario's negative prompt into a text file of its own, beside the prompt list.\n"
    "- One list for the whole scenario. The file holds the tags and nothing else, so the user can "
    "copy it whole.\n"
    "- The file is named after the structure, and each call replaces what it wrote last time: give "
    "the whole list."
)
WRITE_NEGATIVE_TAGS = "The whole negative prompt, as comma-separated tags."
```

### Görev 2: Dosya adı — `build_prompts.py`

```python
def prompts_name(source):
    """The output is the source under a new extension, so a project can hold several scenarios."""
    return f"{_stem(source)}.py"


def negative_name(source):
    """The scenario's negative prompt, beside its prompt list under the same stem (Madde 373)."""
    return f"{_stem(source)}-negative.txt"


def _stem(source):
    stem, dot, _ = source.rpartition(".")
    return stem if dot else source
```

### Görev 3: Araç — `tools.py`, `modes.py`

- [ ] **Adım 1:** import'a `negative_name`; `WRITES_FILES`'a `"write_negative"`.
- [ ] **Adım 2:** `TOOL_SPECS`'in sonuna:

```python
    {
        "type": "function",
        "function": {
            "name": "write_negative",
            "description": prompt.WRITE_NEGATIVE,
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": prompt.THE_STRUCTURES_FILE},
                    "tags": {"type": "string", "description": prompt.WRITE_NEGATIVE_TAGS},
                },
                "required": ["file", "tags"],
            },
        },
    },
```

- [ ] **Adım 3:** `run_tool`'da `build_prompts`'tan sonra `write_negative` → `_write_negative`:

```python
def _write_negative(file_store, project_id, args):
    source = safe_name(args.get("file"))
    if file_store.read(project_id, source) is None:
        return ToolResult("There is no file by that name.", None, source, "No file by that name")
    tags = str(args.get("tags") or "").strip()
    if not tags:
        return ToolResult("A negative prompt needs tags.", None, source, "Refused")
    written = file_store.write(project_id, negative_name(source), tags)
    return ToolResult(f"Wrote {written}.", written, source, "Written")
```

- [ ] **Adım 4:** `run_tool` docstring'i: "the other eighteen".
- [ ] **Adım 5:** `modes.py`'de edit modunun listesine, gerekçesiyle, `"write_negative"`.

### Görev 4: Yeşil ve commit

- [ ] **Adım 1:** Dört satır paralel; beklenen: hepsi yeşil.
- [ ] **Adım 2:** Commit — spec ve plan aynı commit'te:

```
feat: Madde 373 -- the negative prompt is the fourth check, written to a file of its own
```
