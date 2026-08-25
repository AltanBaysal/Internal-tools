# v14 Görev 37 — Export fotoğrafları da taşır: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Önceki commit'in dört kırmızı testini yeşile döndürmek.

**Architecture:** İki dosya, iki iş. Depo `photos/` klasörünü ve yazmayı üstleniyor — varsa atlıyor,
yazarken atomik davranıyor. Alan katmanı yalnız "bu karenin fotoğrafını `01.png` olarak koy" diyor;
klasörün adını hiç bilmiyor.

**Tech Stack:** Python (`os`, `shutil`, `tempfile`), pytest.

**Spec:** [Görev 37 uygulama spec'i](../specs/2026-08-25-queen-editor-v14-gorev-37-uygulama-design.md)

## Global Constraints

- **Test dosyaları değişmiyor.** `test_export.py` ve `test_photo_store.py` bir önceki commit'te ne
  yazıldıysa o kalır.
- **`photos/` adı yalnız depoda geçer.** Alan katmanı yol kurmaz.
- **Uzantı kaynağınki.** `.png` koda yazılmaz.
- **Yazma atomik.** Geçici ada kopyala, sonra hedefe taşı. "Varsa atla" tek başına yetmez.
- **Patlamış fotoğraf için kontrol eklenmiyor** — gerekçesi spec'te; ulaşılamayan dal olurdu.
- Dil: kod ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- Commit mesajında **çift tırnak yok** — PowerShell here-string'i kırıyor (CLAUDE.md).
- Test: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`.
- **`dist` tazelenmiyor** — bu iş arka yüzde, ön yüz kaynağı hiç açılmıyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/backend/features/photo_generation/data/photo_store.py` | dosyaların diskte nerede durduğu | `PHOTOS_DIR` sabiti + `copy_photo` |
| `queen-editor/backend/features/photo_generation/domain/usecases/run_export.py` | export koşusunun sırası ve adlandırması | uzantı yardımcısı + döngüye bir çağrı |

İki dosya, çünkü sınır burada: yol ve dosya sistemi deponun, sıra ve ad alanın. Deponun kendi
belgesi bunu zaten söylüyor — *"Named here rather than in the domain, which knows nothing about
paths."*

---

### Task 1: Depo `photos/`'a atomik olarak yazsın

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/data/photo_store.py:1-20` (içe aktarmalar
  ve sabitler) ve `:64-66` (`remove_dir`'in altı)

**Interfaces:**
- Consumes: dosyada zaten duran `os`, `shutil` ve `EXPORT_DIR` sabiti.
- Produces: `DrivePhotoStore.copy_photo(source, folder, filename)` — `folder/photos/filename`'e
  yazar, hedef zaten oradaysa hiçbir şey yapmaz. Dönüş değeri yok. Task 2 bu imzayı çağırır ve
  `test_export.py`'nin sahtesi de aynısını taşır.

- [ ] **Step 1: `tempfile`'ı içe al ve klasör adını sabitle**

Dosyanın başı bugün:

```python
import shutil

from backend.features.photo_generation.domain.photo_name import number_of

# The project folder's own export area; a run makes a dated folder inside it (design v3, madde 92).
EXPORT_DIR = "export"
```

Yerine:

```python
import shutil
import tempfile

from backend.features.photo_generation.domain.photo_name import number_of

# The project folder's own export area; a run makes a dated folder inside it (design v3, madde 92).
EXPORT_DIR = "export"
# The pictures ride inside the export in a folder of their own, so the mp4s stay a bare sequence.
PHOTOS_DIR = "photos"
```

`import os` dosyanın en başında zaten var (11. satır civarı, `import shutil`'in üstünde) — dokunma.

- [ ] **Step 2: `copy_photo`'yu yaz**

`remove_dir` bugün:

```python
    def remove_dir(self, path):
        """Take a folder and everything in it. Used on a failed or cancelled export."""
        shutil.rmtree(path, ignore_errors=True)
```

Bunun **altına**, `export_dir`'in **üstüne**:

```python
    def copy_photo(self, source, folder, filename):
        """Put one picture in the export's photos folder, unless it is already there.

        Both export modes can run at once and a folder named down to the minute is one folder for
        both, so two threads asking for the same 01.png is the expected case rather than a corner
        one. Which is why there are two answers here and not one.

        Already there means nothing to do: the other mode has written the very same bytes, and
        writing them again buys nothing.

        And the write itself lands in one move. Two threads can both find the target missing and
        both start writing; two copies into one path is a half file. Copying to a name of its own
        and then moving it over means the target is never seen half written, whichever thread gets
        there last.
        """
        photos = os.path.join(folder, PHOTOS_DIR)
        os.makedirs(photos, exist_ok=True)
        target = os.path.join(photos, filename)
        if os.path.exists(target):
            return
        handle, temporary = tempfile.mkstemp(dir=photos)
        os.close(handle)
        shutil.copyfile(source, temporary)
        os.replace(temporary, target)
```

`os.replace` seçildi, `os.rename` değil: Windows'ta `rename` var olan bir hedefin üstüne yazmaz ve
atar. `os.replace` iki işletim sisteminde de aynı davranır.

- [ ] **Step 3: Deponun testinin yeşile döndüğünü gör**

Run: `python -m pytest queen-editor/backend/tests/test_photo_store.py -q`

Expected: **9 passed** — dosyanın sekiz eski testi ve
*test_a_photo_already_in_the_export_is_not_written_again*.

Son iddia (`iterdir() == ["01.png"]`) düşerse geçici dosya sızmış demektir: `os.replace` çalışmamış
ya da hiç çağrılmamıştır.

- [ ] **Step 4: Commit yok**

Bu görev tek başına commit edilmiyor; depoya kimse fotoğraf vermiyor. Task 2 ile tek commit'e girer.

---

### Task 2: Export her karenin fotoğrafını da bıraksın

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/run_export.py:1-11`
  (modülün belgesi), `:34-38` (`_audio_of`'un üstü) ve `:49-60` (döngü)

**Interfaces:**
- Consumes: Task 1'in `store.copy_photo(source, folder, filename)`'ı; ve dosyada zaten duran
  `layers`, `store.file_path(project, filename)`, `exportable()`.
- Produces: dışarıya yeni bir şey değil. `run_export`'un imzası ve dönüş değeri aynı kalıyor.

- [ ] **Step 1: Uzantı yardımcısını yaz**

`_audio_of` fonksiyonunun **üstüne**, `MERGED = "merged"` sabitinin altına:

```python
def _extension(filename):
    """The picture's own suffix, dot included, or nothing at all.

    The number belongs to the export and the suffix to the file: writing .png into the code would
    name the first jpg wrongly, and nothing on screen would say so.

    Read from the name rather than from the path -- a file's name is what this layer has, and where
    it sits on disk is the store's business.
    """
    head, dot, tail = filename.rpartition(".")
    return f".{tail}" if dot and head else ""
```

`head and dot` birlikte soruluyor: noktası olmayan bir ad (`"resim"`) ve noktayla başlayan bir ad
(`".gizli"`) uzantısız sayılır.

- [ ] **Step 2: Döngüye fotoğrafın kopyalanmasını ekle**

Döngünün gövdesi bugün:

```python
            target = store.export_path(folder, f"{index:02d}.mp4")
            exporter.piece(store.file_path(project, frame["layers"][layers.VIDEO]),
                           _audio(store, project, frame), target)
            pieces.append(target)
            runner.report(mode, written=index)
```

Yerine:

```python
            target = store.export_path(folder, f"{index:02d}.mp4")
            exporter.piece(store.file_path(project, frame["layers"][layers.VIDEO]),
                           _audio(store, project, frame), target)
            pieces.append(target)
            # The picture goes in under its video's own number, so the photos folder reads as the
            # same sequence and nothing has to be matched up by hand. A frame that somehow has no
            # picture leaves none: its video is written all the same.
            photo = frame.get("layers", {}).get(layers.PHOTO)
            if photo:
                store.copy_photo(store.file_path(project, photo), folder,
                                 f"{index:02d}{_extension(photo)}")
            runner.report(mode, written=index)
```

Sırası önemli: kopyalama `runner.report`'tan önce. Patlarsa `written` o kareyi saymamış olur, ve
zaten `except` klasörü alıp götürüyor.

**Patlamış fotoğraf için `_audio_of` gibi bir kontrol eklenmiyor:** fotoğrafı patlamış bir kareden
video üretilemez, dolayısıyla `exportable()` onu zaten dışarıda bırakıyor. Ulaşılamayan bir dal
olurdu.

- [ ] **Step 3: Modülün belgesini düzelt**

Dosyanın başındaki belge bugün ilk satırında şunu diyor:

```python
"""Write the project's videos out: one file per frame, or one file for all of them.
```

Yerine:

```python
"""Write the project's videos out: one file per frame, or one file for all of them -- and the
pictures they were made from, in a folder of their own.
```

Aynı belgenin ikinci paragrafı (*"Nothing is moved. Every file written here is a copy…"*) fotoğraf
için de doğru; değişmiyor.

- [ ] **Step 4: Arka yüz takımının tamamen yeşil olduğunu gör**

Run: `python -m pytest queen-editor -q`

Expected: **715 passed.** Dört kırmızının dördü de yeşile döndü.

*test_a_frame_with_no_video_leaves_no_photo_either* düşerse dur: fotoğraf `exportable()`'ın
listesinin dışından kopyalanıyor demektir, yani çağrı döngünün içinde değil.

- [ ] **Step 5: Ön yüz takımının da yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **582 passed.** Bu döngü ön yüze hiç dokunmuyor; koşulma sebebi CLAUDE.md'nin iki sabit
satırı.

- [ ] **Step 6: Yol haritasını işaretle**

Modify: `docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md`

37. maddenin satırındaki iş adının başına `✅ ` ekle — 34, 35 ve 36'nın satırlarındaki biçimin
aynısı:

```
| 37 | ✅ **Export fotoğrafları da taşır.** …
```

Aynı belgenin başlığındaki ilerleme sayısını da bir artır: `34/36` yazan yer `35/36` olur.

- [ ] **Step 7: Colab turu listesine satır ekle**

Modify: `docs/superpowers/plans/2026-08-24-queen-editor-v14-colab-turu.md`

Export bu listede kendi başlığını taşımıyor — *"Export ekranı bu koşuda hiç açılmadı"* diyen satır
**Hata sanılmayacaklar** bölümünde. Madde 37 o cümleyi kısmen geçersiz kılıyor: ekran değişmiyor ama
exportun çıktısı değişiyor, ve bu ancak bir export alınarak görülebilir.

`## 7 · Kuyruk` bölümünün **altına**, `## Hata sanılmayacaklar` başlığının **üstüne** yeni bir
bölüm:

```markdown
## 8 · Export

- [ ] **Fotoğraflar exportun içinde** (37). Bir export alınır ve klasöre bakılır: içinde `photos/`
      var, içindekiler `01.png`, `02.png`… diye numaralanmış ve yanlarındaki `01.mp4`, `02.mp4`
      ile birebir eşleşiyor. Videosu olmayan karenin fotoğrafı orada yok.
- [ ] **İki mod aynı anda** (37). Birleşik ve ayrı export aynı dakika içinde başlatılır; ikisi de
      bittiğinde `photos/` içinde her fotoğraf tek kopya, hiçbiri yarım değil.
```

Aynı belgedeki **Hata sanılmayacaklar** bölümünün export satırı da düzeltilir. Bugün:

```markdown
- **Export ekranı** bu koşuda hiç açılmadı — kullanıcı düzgün bulduğu için tüm export farkları
  düştü.
```

Yerine:

```markdown
- **Export ekranı** bu koşuda hiç açılmadı — kullanıcı düzgün bulduğu için tüm export farkları
  düştü. Ekran hâlâ değişmedi; 37. madde exportun *çıktısını* değiştiriyor ve turda 8. bölümde
  görülüyor.
```

- [ ] **Step 8: Değişen her şeyi gör**

Run: `git status --short`

Expected: `photo_store.py`, `run_export.py`, yol haritası, Colab turu, ve `docs/superpowers`
altındaki iki yeni belge. `test_export.py`, `test_photo_store.py` ve `dist/` bu listede
**olmamalı.**

- [ ] **Step 9: Commit**

```bash
git add queen-editor/backend docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): an export takes the pictures with it

An export folder now holds a photos folder beside its mp4s, and every frame the
sequence carries leaves its picture in it under the video's own number. The
folder reads as the same sequence twice over: 01.mp4 and 01.png are one frame,
and nothing has to be matched up by hand.

The suffix is the file's own rather than a png written into the code. A number
that belongs to the export and a suffix that belongs to the picture is the
whole naming rule, and the first jpg would otherwise have been filed under a
name it does not have.

Which frames: the ones the sequence holds, exactly. A frame with no video has
no number to be filed under, so its picture stays behind -- the photos folder
is the mp4 list, picture for picture.

The store owns the folder and the write; the domain only says which picture
goes in as which name. Where a file sits on disk was never this layer's
business, and a folder name in two places is a folder name that goes stale in
one of them.

Two answers to the same question, because both export modes can run at once and
a folder named down to the minute is one folder for both. A picture already
there is left alone -- the other mode wrote the very same bytes. And the write
lands in one move, copied to a name of its own and then moved over, because two
threads can both find the target missing and two copies into one path is a half
file. The check alone would have been an answer with a gap in it.

Nothing else about a run changes. The copy sits beside its video inside the
same step, so a failure takes the folder the way a failed video always did, and
the counter goes on counting videos.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:**

| Spec'te ne diyor | Planda nerede |
|---|---|
| Alan yol kurmaz, `photos/` depoda | Task 1 Step 1, Task 2 Step 2 |
| Numara videonunki | Task 2 Step 2 |
| Uzantı kaynağınki, addan okunuyor | Task 2 Step 1 |
| Varsa atla | Task 1 Step 2 |
| Yazma atomik | Task 1 Step 2 |
| Fotoğrafı olmayan kare atlanır | Task 2 Step 2'nin `if photo` dalı |
| Patlamış fotoğraf kontrolü yok | Task 2 Step 2, Global Constraints |
| İptal, hata ve sayaç değişmiyor | Task 2 Step 2'nin sıra notu, commit mesajı |
| Test dosyaları değişmiyor | Global Constraints, Task 2 Step 8 |
| `dist` tazelenmiyor | Global Constraints, Task 2 Step 8 |

Spec'te olup planda karşılığı olmayan madde yok. Yol haritası ve Colab turu adımları spec'te değil,
CLAUDE.md'nin numaralandırma ve tur kuralından geliyor.

**Yer tutucu yok:** Kod adımlarında gerçek kod, doğrulama adımlarında gerçek komut var; beklenen
sayılar (9, 715, 582) yazılı.

**Ad tutarlılığı:** `copy_photo(source, folder, filename)` iki görevde de aynı imzayla geçiyor ve
bir önceki commit'in sahtesindekiyle birebir aynı. `PHOTOS_DIR` yalnız depoda, `_extension` yalnız
alan katmanında geçiyor; ikisi de tanımlandıkları adımda ve kullanıldıkları adımda aynı yazımla.

**Bilerek dışarıda:** ön yüz ve `ExportScreen`. Özetin cümlesi video sayıyor ve bu iş onu
değiştirmiyor.
