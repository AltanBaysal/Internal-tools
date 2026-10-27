# Madde 398 — Ses motorunun kurulum hücresi geri bildirim veriyor, implementasyon turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `2458fdde`'nin beş kırmızısı yeşile dönsün, iki bekçisi yeşil kalsın.

**Yaklaşım:** `run` komutu `Popen` ile başlatıyor, stderr'i stdout'a katıyor, çıktıyı ayrı bir iş
parçacığında satırbaşını koruyarak hücreye basıyor, ana iş parçacığında süreyle bekliyor, ve her
çıkışta yarıda kalan komutu durduruyor. Defterde ses motoru hücresi iki `log` satırı alıyor ve `pip`'in
`-q`'su çıkıyor — hücrenin kaynağı NotebookEdit ile bütün olarak yazılıyor.

**Spec:** [m398 implementasyon turu](../specs/2026-09-30-queen-editor-m398-kurulum-geri-bildirimi-uygulama-design.md)

## Her yere geçerli kurallar

- Kod, yorum ve docstring İngilizce, konsol metinleri Türkçe.
- Defterin kod hücrelerinde yorum yok, yalnız bölüm başlıkları. Defter 29.000 karakteri geçmiyor.
- Testler dört satırla koşulur.

**Arayüz:** `run(cmd, label, cwd=None, timeout=3600)` — imza aynı, dönüş yok. `colab/nodes.py`,
`colab/downloads.py` ve defter onu bugünkü gibi çağırıyor; hiçbiri dönüşünü okumuyor.

---

## Görev 1: `colab/console.py`

**Dosya:** Değiştir: `queen-editor/colab/console.py`

- [ ] **Adım 1: İmport'lar.** `import os`, `import subprocess`, `import time`'ın yerine:

```python
import collections
import io
import os
import subprocess
import threading
import time
```

- [ ] **Adım 2: `run`'ın yerine `run` ve `_echo`.**

```python
def run(cmd, label, cwd=None, timeout=3600):
    """A shell call whose output reaches the cell as it comes, and that fails loud with the command's
    own last lines rather than a guessed cause.

    stderr joins stdout, so the two keep the order they were written in: git, pip and curl put their
    progress and their errors on stderr, and where a command hangs is read from that order. pip is a
    Python program, and into a pipe Python holds its lines until it ends; PYTHONUNBUFFERED makes it
    hand each one over as it is written. However this is left -- past the deadline, or the cell
    stopped by the user -- kill leaves nothing running behind the cell; a command that has ended is
    not signalled.
    """
    proc = subprocess.Popen(cmd, shell=isinstance(cmd, str), cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env={**os.environ, "PYTHONUNBUFFERED": "1"})
    tail = collections.deque(maxlen=5)
    echo = threading.Thread(target=_echo, args=(proc.stdout, tail))
    echo.start()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{label}: timeout ({timeout}s)") from None
    finally:
        proc.kill()
        proc.wait()
        echo.join()
    if proc.returncode != 0:
        raise RuntimeError(f"{label}: exit {proc.returncode}\n" + "\n".join(tail))


def _echo(pipe, tail):
    """The command's output onto the cell piece by piece as it comes, its last lines kept for an error.

    newline="" leaves a carriage return as it came, so curl's progress line is redrawn in place rather
    than printed anew every second. errors="replace" shows a byte the locale cannot read as a
    replacement mark: raised, it would end this reader, the pipe would fill, and the command would sit
    blocked until its deadline.
    """
    for piece in io.TextIOWrapper(pipe, newline="", errors="replace"):
        print(piece, end="", flush=True)
        if piece.strip():
            tail.append(piece.rstrip())
```

## Görev 2: Defter

**Dosya:** `queen-editor/queeneditor.ipynb` — bir hücre, NotebookEdit ile.

- [ ] **Adım 1: Ses motoru hücresi (`791a750a`)**, kaynağın tamamı:

```python
# === Ses motoru — MMAudio kütüphanesi ===
import os

MMAUDIO_DIR = "/content/MMAudio"

if not INSTALL_AUDIO:
    log("Ses motoru: atlandı (INSTALL_AUDIO kapalı)")
else:
    if not os.path.isdir(MMAUDIO_DIR):
        log("MMAudio klonlanıyor…")
        run(["git", "clone", "--depth", "1", "https://github.com/hkchengrex/MMAudio.git",
             MMAUDIO_DIR], "clone MMAudio", timeout=300)
    log("MMAudio kuruluyor…")
    run(["pip", "install", "-e", "."], "pip install MMAudio", cwd=MMAUDIO_DIR, timeout=1800)
    log("MMAudio kütüphanesi kuruldu", "OK")
```

- [ ] **Adım 2: `git diff -U0 --word-diff=porcelain queen-editor/queeneditor.ipynb`** — yalnız bu üç
  satır değişmiş olmalı: iki `log` eklendi, `pip`'in satırından `"-q"` çıktı.

## Görev 3: Koşu, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi — dördü de yeşil.
- [ ] **Adım 2: Yeşil commit** — `console.py`, defter, bu spec ve bu plan:
  `feat(queen-editor): Madde 398 -- …`. Yol haritasına bu parçada dokunulmuyor.
