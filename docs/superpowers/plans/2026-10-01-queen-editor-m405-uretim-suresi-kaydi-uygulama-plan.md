# Madde 405 — Üretim süresi kaydı, uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 8a894daf'ın kırmızı testlerini yeşile çevirmek: üretilen satır modelin süresini taşır, kayıt hücreye, galeri karta, kopya ikize taşır.

**Architecture:** Döngünün log için yaptığı ölçüm üreticinin çağrısına daraltılır ve satıra yazılır; okuyucular `mode`/`endsOn`'un yolundan gider.

**Tech Stack:** Python, Flask, pytest.

**Spec:** [m405 uygulama turu](../specs/2026-10-01-queen-editor-m405-uretim-suresi-kaydi-uygulama-design.md)

## Global Constraints

- Alan adı `renderSeconds`; değer `round(saniye, 1)`.
- Frontend ve dist değişmez.
- Yorumlar İngilizce, yalnız NEDEN'i ve bugün doğru olanı söyler.
- Testler yalnız dört satırla, aynen, paralel.

---

### Task 1: Döngü — `queen-editor/backend/features/photo_generation/domain/run_loop.py`

- [ ] **Step 1:** Turun başındaki `started = clock()` silinir.
- [ ] **Step 2:** Üretim kolunda, `pool` hesaplandıktan sonra, `producer.generate` çağrısının hemen önüne:

```python
                    # The model's own seconds and nothing else: no queue wait, no prompt writing,
                    # no Drive read of what the layer is made from (madde 405).
                    started = clock()
                    data = producer.generate(...)
```

- [ ] **Step 3:** Üretilen satıra, `"createdAt": now(),` arkasına:

```python
                                        "renderSeconds": round(rendered - started, 1),
```

- [ ] **Step 4:** `make_job` docstring'inin `log` paragrafı: aynı ölçümün satıra da yazıldığını söyler.

### Task 2: Kayıt — `data/photo_record.py`, `domain/ports.py`

- [ ] **Step 1:** `slots()` içinde `endsOn` bloğunun arkasına:

```python
            if isinstance(row.get("renderSeconds"), (int, float)):
                # Only a layer produced since madde 405 says how long it took; older lines say
                # nothing, and nothing is filled in for them.
                cell["renderSeconds"] = row["renderSeconds"]
```

- [ ] **Step 2:** `slots()` docstring'i ve port'un `slots` docstring'i `renderSeconds`'ı anar.

### Task 3: Galeri — `domain/usecases/list_frames.py`

- [ ] **Step 1:** `card()` içinde `"endsOn": ...` arkasına:

```python
                # How long the model worked on each layer (madde 405); a layer with no time is
                # absent, which is what an old or a red layer reads as.
                "renderSeconds": _per_layer(cells, "renderSeconds"),
```

- [ ] **Step 2:** `_per_layer` docstring'i üç kullanıcıyı anar.

### Task 4: Kopya — `domain/copy_frame.py`

- [ ] **Step 1:**

```python
CARRIED = (("modes", "mode"), ("endsOn", "endsOn"), ("renderSeconds", "renderSeconds"))
```

ve üstündeki yorum süreyi de anar.

### Task 5: Yeşil koş, commit'le

- [ ] **Step 1:** Dört satır, aynen, paralel. Beklenen: hepsi yeşil.
- [ ] **Step 2:** Spec, plan ve kod tek commit'te; konu satırı, boş satır, `Co-Authored-By` son satır.
