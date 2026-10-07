# Madde 326 — Havuzdan üretim kapısı, uygulama turunun planı

**Hedef:** `test_the_app_hands_a_reference_run_to_the_use_case`'in iki hâli yeşil.

**Spec:** [m326 uygulama turu](../specs/2026-09-24-queen-editor-m326-havuzdan-uretim-kapisi-uygulama-design.md)

## Görev 1: `main.py`

`_references_bp`'nin `queue_references=partial(...)`'ından son satır gidiyor:

```python
                             log=_timing, writers=_writers, stills=_stills),
```

## Görev 2: Koşu ve yeşil commit

- [ ] Dört satır — hepsi yeşil.
- [ ] `fix(m326): …`.
