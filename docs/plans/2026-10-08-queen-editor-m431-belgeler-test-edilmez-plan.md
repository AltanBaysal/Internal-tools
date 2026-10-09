# Madde 431 — Belgeler test edilmez, plan

> **Koşum:** bu oturumda, ana klasörde, satır satır. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Belge okuyan altı yer, spec'teki listeyle: üçünde test ya da dosya gider, üç taramadan
`.md` dosyaları çıkar.

**Yaklaşım:** Yeni test yazılmaz — madde test kaldırıyor, davranış eklemiyor. Taramalar kendi skip
listelerine bir `.md` satırı alır; adını okuyan üç yer olduğu gibi silinir.

**Araçlar:** pytest, vitest.

**Spec:** [m431](../specs/2026-10-08-queen-editor-m431-belgeler-test-edilmez-design.md)

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce**, ve yalnız bugün doğru olanı söyler.
- Testler yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel koşulur; `skip` / `xfail` yok.
- Yalnız aşağıdaki altı test dosyası değişir; belgelere, `queen-editor/BACKLOG.md`'ye ve yol
  haritasına dokunulmaz; `dist`'e dokunulmaz.

---

## Görev 1: `queen-editor/backend/tests/test_version_record.py`

- [ ] **Dosyayı sil.** Hiçbir dosya ondan içe aktarmıyor.

## Görev 2: `queen-agent/backend/tests/test_pin_archive.py`

- [ ] **`CODE_STANDARD` sabitini sil** — içe aktarmaların altındaki `os.path.join(…, "CODE-STANDARD.md")`.
  `os` dosyada kullanılmaya devam ediyor (`os.utime`, `os.path.getmtime`).
- [ ] **Dosyanın sonundaki `# ---- The standard ----` başlığını ve
  `test_the_standard_names_both_new_files`'ı sil.**

## Görev 3: `queen-agent/frontend/src/shared/app.css.test.js`

- [ ] **Sil:** Madde 379 yorumu, `const STANDARD = read("../CODE-STANDARD.md");`, `the standard
  names every keyframe the frontend defines` ve `the standard forbids no animation, and calls no
  motion the only one`. `read`, `APP` ve `WORKSPACE` kalır.

## Görev 4: `queen-agent/backend/tests/test_retired_provider.py`

- [ ] **Skip listesine `.md`:**

```python
# An integrity hash, where the letters meet by chance.
_SKIPPED_FILES = {"package-lock.json"}
# Documents: tests test only code (madde 431).
_SKIPPED_SUFFIX = ".md"
```

- [ ] **`_written()`'da:**

```python
            if (name not in _SKIPPED_FILES and not name.endswith(_SKIPPED_SUFFIX)
                    and os.path.abspath(path) != _THIS):
                yield path
```

## Görev 5: `queen-editor/backend/tests/test_retired_provider.py`

- [ ] **`_SKIPPED_FILES`'tan `BACKLOG.md` ve yorumun onu anlatan yarısı çıkar; Görev 4'teki iki satır
  eklenir:**

```python
# An integrity hash, where the letters meet by chance.
_SKIPPED_FILES = {"package-lock.json"}
# Documents: tests test only code (madde 431).
_SKIPPED_SUFFIX = ".md"
```

- [ ] **`_written()`'da** Görev 4'teki koşul.

## Görev 6: `queen-editor/backend/tests/test_audio_engine_wiring.py`

- [ ] **Uzantı listesinden `.md` çıkar:**

```python
            if name in SKIP_FILES or not name.endswith((".py", ".json", ".ipynb", ".jsx", ".js",
                                                        ".txt")):
```

- [ ] **Docstring'in ikinci paragrafı, taramanın baktığı kodla:**

```python
"""The sound engine moved out of ComfyUI; these guard the parts a unit test cannot see.

A leftover reference is not a broken import -- it is a name in a string, a path in the code or a
notebook cell, asking for a graph that nothing reads, and that only shows up when it runs. Documents
are not swept: tests test only code (madde 431).
"""
```

## Görev 7: Koş, sayıları oku

- [ ] **Dört satır, paralel, olduğu gibi, depo kökünden.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil, ve sayılar tam kaldırılan testler kadar düşük — `queen-agent` 989 → **988**,
`queen-agent/frontend` 838 → **836** (44 dosya), `queen-editor` 1518 → **1507**,
`queen-editor/frontend` **869**. Başka bir fark, listeden fazlasının ya da eksiğinin gittiğini söyler.

## Görev 8: Commit — ana ajanın

- [ ] Spec, plan ve altı test dosyası — biri silinmiş. Mesajda çift tırnak yok; son satır
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
