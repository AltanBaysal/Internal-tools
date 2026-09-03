# Madde 159 — test turu planı

**Spec:** [m159 craft testler design](../specs/2026-09-03-queenagent-m159-craft-testler-design.md)

Bu tur yalnız test yazar. Büyük olan kısmı silme.

## 1. `test_schema.py` silinir

Anlattığı metin gidiyor.

## 2. `test_tools.py`

- Şema aracının dört testi silinir.
- Roster'dan bir ad çıkar *(18 → 17)*.
- `CRAFT` testleri eklenir: dört açıklamada var, ikisinde yok, `WRITING`'in içinde, içeriği doğru,
  ve dosyanın şeklinden söz etmiyor.
- `schema` modülünün import edilemediği çivilenir.
- **Import test gövdesinin içinde** — dosyanın toplanması düşerse turun bütün kırmızıları görünmez
  olur, ve bu dosyanın kendi kuralı zaten bu.

## 3. `test_stream_answer.py`

Şema çağrısı yirmiye yakın yerde "herhangi bir araç" olarak kullanılıyor. Tek bir yardımcı yazılır:

```python
def a_call(call_id="t1"):
    """Some tool call, for tests that need a round rather than a particular tool."""
    return call("read_file", call_id, name="ghost.md")
```

Olmayan bir dosyanın okuması bir tur harcıyor ve kutuya girmiyor — `files_opened` kaçırılmış okumayı
atlıyor. `ToolCall("read_prompt_structure_schema", "", "Schema")` bekleyen iki assertion
`ToolCall("read_file", "ghost.md", "No file by that name")` olur.

`test_the_schema_reaches_the_box_too` silinir.

## 4. `test_context_box.py` ve `test_modes.py`

İki şema testi silinir; `READS` tek ada iner.

## 5. `test_chats_api.py` ve `test_skills.py`

Aynı değişim; skill testlerinden şema çekenler silinir.

## 6. Koşulur ve kırmızı görülür

CLAUDE.md'nin dört satırı, **sırayla**:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

## 7. Kırmızı commit'lenir

`test(m159): …` — mesajda çift tırnak yok.
