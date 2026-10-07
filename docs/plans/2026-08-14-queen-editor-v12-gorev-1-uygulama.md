# v12 Görev 1 — Tohumsuz iş: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `e1c3d86`'daki beş kırmızı testi yeşile çevirmek.

**Architecture:** Tek dosya. Ses üreticisi bir tohum kaynağı alıyor ve tohumsuz işe iş başına bir
tohum seçiyor.

**Tech Stack:** Python, pytest.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-14-queen-editor-v12-gorev-1-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `e1c3d86`'daki beş test sözleşme.
- Yorum ve docstring **İngilizce**; yorum WHY anlatır.
- Commit mesajında **çift tırnak yok**.
- Komut: `python -m pytest queen-editor/backend/tests -q`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/data/mmaudio_generator.py` | ses işinin nasıl wav olduğu | tohum kaynağı + tohumsuz işin cevabı |

---

### Task 1: Tohum kaynağı ve tohumsuz işin cevabı

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/data/mmaudio_generator.py`

**Interfaces:**
- Produces: `MMAudioGenerator(sampler, ffmpeg, tmp_dir=None, new_seed=None)` — `new_seed` sıfır
  argümanlı, tam sayı döndüren bir çağrılabilir. Testler bu imzayı çağırıyor.

- [ ] **Step 1: `random` import'u ve modülün kendi tohumu**

`import os` satırlarının arasına `import random` (alfabetik: `os`, `random`, `shutil`, `tempfile`).
`FADE_MS` sabitinin altına:

```python
def _random_seed():
    """The seed a sound job never carries. The same range photo jobs are planned in, so a seed is
    a seed wherever it was born."""
    return random.randint(0, 2**31 - 1)
```

- [ ] **Step 2: Yapıcı tohum kaynağını alsın**

```python
    def __init__(self, sampler, ffmpeg, tmp_dir=None, new_seed=None):
        self._sampler = sampler
        self._ffmpeg = ffmpeg
        self._tmp_dir = tmp_dir
        # A port for the test's sake rather than the wiring's: which numbers come out is nobody's
        # choice, but a test cannot prove two jobs got different seeds without knowing them.
        self._new_seed = new_seed or _random_seed
```

- [ ] **Step 3: Tohumsuz iş kendi tohumunu alsın**

`generate()` içinde, `_name, data = source` satırının hemen üstüne:

```python
        # A sound job is planned with no seed of its own -- only photos are seeded, and a layer is
        # made from what is under it. torch's manual_seed takes a long and raises on None, so the
        # missing one is chosen here: once per job, so every piece of one sound shares it, and
        # freshly each time, so two sound variants of one video are two different sounds.
        if seed is None:
            seed = self._new_seed()
```

`_name, data = source` ve sonrası olduğu gibi kalır.

- [ ] **Step 4: Ses üreticisinin kendi testleri**

Run: `python -m pytest queen-editor/backend/tests/test_mmaudio_generator.py -q`
Expected: 13 geçen, 0 düşen.

- [ ] **Step 5: Sözleşme**

Run: `python -m pytest queen-editor/backend/tests/test_producer_contract.py -q`
Expected: 2 geçen, 0 düşen.

---

### Task 2: Takım ve commit

- [ ] **Step 1: Tam takım**

Run: `python -m pytest queen-editor/backend/tests -q`
Expected: 597 geçen, 0 düşen.

- [ ] **Step 2: Commit**

```bash
git add queen-editor/backend docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): let a sound job that carries no seed still be made

The five tests from the previous commit go green.

Only photos are planned with a seed -- a layer is made from what is under it,
not from a number nobody was asked for. The video producer answers that by
leaving the graph its own seed. MMAudio has nothing to leave: manual_seed
takes a long and raises on None, so every sound job died on its first frame
and the queue stopped after three tries.

The sound producer picks the seed that is missing. Once per job, so a long
video cut into pieces stays one sound; freshly each time, so two variants of
one video are two different sounds. The choice sits here rather than in the
sampler, because the sampler is the file a fake torch cannot test -- and its
own docstring already said which seed was this file s decision.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** tohum kaynağı → Step 1-2 · tohumsuz işin cevabı → Step 3. Eksik yok.

**Kontrol edilen sıra:** tohum `source` kontrolünden **sonra** seçiliyor. Öncesinde seçilseydi,
kaynağı olmayan bir iş boşuna bir tohum harcardı — zararsız ama yalan: seçilen tohum hiç
kullanılmayacaktı.

**Kontrol edilen kapsam:** `_sound_for` imzası değişmiyor. Tohum ona zaten parametre olarak
giriyordu; değişen tek şey oraya varan değerin artık hiç `None` olmaması.
