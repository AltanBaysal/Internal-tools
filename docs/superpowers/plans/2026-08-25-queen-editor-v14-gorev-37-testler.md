# v14 Görev 37 — Export fotoğrafları da taşır: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Exportun fotoğrafları hiç taşımadığını anlatan üç kırmızı test ile bir yeşil tutucuyu
yazmak — kod hiç değişmeden.

**Architecture:** İki test dosyası, çünkü kural iki katmana bölünüyor. Alan katmanı fotoğrafı doğru
numarayla depoya veriyor (`test_export.py`); depo aynı hedefe ikinci kez yazmıyor
(`test_photo_store.py`). Sahte depo "varsa atla" kuralını taklit etmiyor — etseydi test kendi
sahtesini sınardı.

**Tech Stack:** Python, pytest.

**Spec:** [Görev 37 test spec'i](../specs/2026-08-25-queen-editor-v14-gorev-37-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `run_export.py` ve `photo_store.py` bu döngüde hiç açılmıyor. Üç test kırmızı
  commit'lenir; `skip`/`xfail` yok.
- **Mevcut testlerin cümlesi değişmiyor.** Yalnız `ExportStore` sahtesi yeni bir metot kazanıyor —
  o metot bugün hiç çağrılmıyor, dolayısıyla bugünkü hiçbir testi etkilemiyor.
- **Sahte depo kuralı taklit etmiyor.** `ExportStore.copy_photo` her çağrıyı kaydeder ve hiçbirini
  atlamaz.
- **Uzantı varsayılmıyor** — `.png` sabit yazılmaz, kaynağınki korunur.
- Dil: test kodu ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- Commit mesajında **çift tırnak yok** — PowerShell here-string'i kırıyor (CLAUDE.md).
- Test komutu birebir: `python -m pytest queen-editor -q`.
- **`dist` tazelenmiyor** — bu iş arka yüzde, ön yüz kaynağı hiç açılmıyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/backend/tests/test_export.py` | export koşusunun alan katmanı | sahteye bir metot, üç test |
| `queen-editor/backend/tests/test_photo_store.py` | deponun disk üzerindeki davranışı | bir test |

İki dosya, çünkü sınanan iki ayrı şey: biri "doğru şeyi doğru adla istiyor mu", öteki "aynı dosyaya
ikinci kez yazıyor mu". İkincisi ancak gerçek dosya sistemiyle görülebilir ve o dosya `tmp_path`
testlerinin evi.

---

### Task 1: Alan katmanının üç testi

**Files:**
- Modify: `queen-editor/backend/tests/test_export.py:17-35` (`ExportStore`) ve dosyanın sonu

**Interfaces:**
- Consumes: dosyada zaten duran `with_videos()`, `export()`, `FakeExporter`, `FOLDER` sabiti
  (`"/fake/düğün/export/2026-08-12 14-32"`), ve `test_photo_usecases`'ten gelen `FakeRecord`.
- Produces: `ExportStore.copy_photo(source, folder, filename)` — sahte depo metodu, her çağrıyı
  `store.photos` listesine `(source, folder, filename)` üçlüsü olarak yazar ve hiçbir şeyi atlamaz.
  Uygulama döngüsü gerçek deponun aynı imzayı taşımasını bu satırdan öğrenir.

- [ ] **Step 1: Sahte depoya metodu ekle**

`ExportStore` bugün:

```python
class ExportStore(FakeStore):
    """FakeStore with the paths an export asks for, and a note of what it removed."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.removed = []
```

Yerine:

```python
class ExportStore(FakeStore):
    """FakeStore with the paths an export asks for, and a note of what it wrote and removed."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.removed = []
        self.photos = []

    def copy_photo(self, source, folder, filename):
        """Every call is written down and none is skipped.

        The real store refuses a target that is already there, and that refusal is tested against a
        real folder next door. A fake that copied the rule would leave these tests sinning against
        their own double instead of the code.
        """
        self.photos.append((source, folder, filename))
```

`copy_photo`'yu `remove_dir`'in **altına**, sınıfın sonuna yaz — sırası dosyada okuma sırasını
bozmaz.

- [ ] **Step 2: Üç testi yaz**

`test_a_frame_with_no_video_is_skipped`'in **altına**, `test_merged_export_writes_one_file...`'in
**üstüne**:

```python
def test_every_exported_frame_leaves_its_photo_beside_its_video():
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter())

    # The number is the video's own: the frame written as 01.mp4 puts its picture in as 01.png, so
    # the photos folder reads as the same sequence and nothing has to be matched up by hand.
    assert store.photos == [
        ("/fake/düğün/0_a.png", FOLDER, "01.png"),
        ("/fake/düğün/1_a.png", FOLDER, "02.png"),
    ]


def test_a_photo_keeps_the_extension_it_was_saved_with():
    store, record, plan_store = with_videos()
    record.append("düğün", {"file": "2_a.jpg", "frame": "2_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "2_a_V1_0.mp4", "frame": "2_a", "layer": "video",
                            "status": "done"})

    export(store, record, plan_store, FakeExporter())

    # The number belongs to the export, the extension to the picture. Writing .png into the code
    # would name the first jpg wrongly and there would be nothing on screen to say so.
    assert store.photos[-1] == ("/fake/düğün/2_a.jpg", FOLDER, "03.jpg")


def test_a_frame_with_no_video_leaves_no_photo_either():
    store, record, plan_store = with_videos()
    record.append("düğün", {"file": "2_a.png", "frame": "2_a", "layer": "photo", "status": "done"})

    export(store, record, plan_store, FakeExporter())

    # The photos folder is the video list, picture for picture: a frame the sequence does not hold
    # has no number to be filed under.
    assert len(store.photos) == 2
```

**Üçüncü karenin neden `03` olduğu:** `with_videos()` iki kare kuruyor (`0_a`, `1_a`) ve
`exportable()` galeriyi ayağından okuyor, yani sıra `0_a`, `1_a`, `2_a`. Üçüncü test kareyi
videosuz eklediği için o listeye hiç girmiyor; ikincisi videosuyla eklediği için üçüncü sırada
duruyor.

**`FakeRecord.append`'in neden yeterli olduğu:** `test_a_frame_with_no_video_is_skipped` bugün tam
olarak bu yolu kullanıyor — kaydı `record.append` ile büyütüyor ve `plan_store`'a dokunmuyor.

- [ ] **Step 3: Üçünün de kırmızı olduğunu gör**

Run: `python -m pytest queen-editor/backend/tests/test_export.py -q`

Expected: **2 failed.** Düşenler:

- *test_every_exported_frame_leaves_its_photo_beside_its_video* — `store.photos` boş; beklenen iki
  satır.
- *test_a_photo_keeps_the_extension_it_was_saved_with* — `store.photos` boş, `[-1]` `IndexError`
  atıyor.

Yeşil kalması gereken: *test_a_frame_with_no_video_leaves_no_photo_either* — bugün hiç fotoğraf
kopyalanmadığı için `len(store.photos)` sıfır… **ve bu 2'ye eşit değil, yani o da düşer.**

Bu yüzden tutucunun iddiası `len(store.photos) == 2` değil olamaz: bugün hiçbir fotoğraf
kopyalanmıyor. Tutucu ancak uygulamadan sonra anlam kazanır ve **bu turda kırmızıdır** — üçü de
kırmızı. Spec'in "yeşil tutucu" satırı burada düzeltiliyor: bugünün davranışı hiç kopyalamamak
olduğu için üç testin üçü de bugün düşer, ve tutucunun koruduğu şey uygulama döngüsünde
"bütün kareler"e kaymamak olur.

**Beklenen: 3 failed.**

- [ ] **Step 4: Commit yok**

Bu görev tek başına commit edilmiyor; Task 2 ile tek commit'e girer.

---

### Task 2: Deponun testi, sonra commit

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_store.py` (dosyanın sonu)

**Interfaces:**
- Consumes: dosyada zaten duran `store_at(path)` yardımcısı ve pytest'in `tmp_path`'i.
- Produces: gerçek `DrivePhotoStore.copy_photo(source, folder, filename)` beklentisi — Task 1'in
  sahtesiyle **aynı imza**.

- [ ] **Step 1: Testi dosyanın sonuna ekle**

```python
def test_a_photo_already_in_the_export_is_not_written_again(tmp_path):
    store = store_at(tmp_path)
    (tmp_path / "düğün").mkdir()
    store.save("düğün", "0_a.png", b"PNG")
    folder = store.make_export_folder("düğün", "2026-08-12 14-32")
    source = store.file_path("düğün", "0_a.png")

    store.copy_photo(source, folder, "01.png")
    # The design lets a merged export and a separate one run side by side, and a folder named down
    # to the minute is one folder for both. The second one finds the picture already there.
    store.copy_photo(source, folder, "01.png")

    landed = tmp_path / "düğün" / "export" / "2026-08-12 14-32" / "photos" / "01.png"
    assert landed.read_bytes() == b"PNG"
    assert [path.name for path in landed.parent.iterdir()] == ["01.png"]
```

`photos/` alt klasörünün adı burada yazılı çünkü deponun ürettiği yol testin gördüğü tek şey;
alan katmanı o adı hiç bilmiyor.

- [ ] **Step 2: Kırmızı olduğunu gör**

Run: `python -m pytest queen-editor/backend/tests/test_photo_store.py -q`

Expected: **1 failed** — `AttributeError: 'DrivePhotoStore' object has no attribute 'copy_photo'`.

- [ ] **Step 3: Bütün arka yüzü koştur**

Run: `python -m pytest queen-editor -q`

Expected: **4 failed, 711 passed** — toplam 715. Düşenlerin dördü bu turda yazılanlar; başka hiçbir
test düşmemeli. Düşerse dur: `ExportStore`'a eklenen metot bugün hiç çağrılmıyor ve hiçbir şeyi
etkileyemez.

- [ ] **Step 4: Ön yüz takımının da yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **582 passed.** Bu döngü ön yüze hiç dokunmuyor; koşulma sebebi CLAUDE.md'nin iki sabit
satırı.

- [ ] **Step 5: Değişen her şeyi gör**

Run: `git status --short`

Expected: `test_export.py`, `test_photo_store.py`, yol haritası, ve `docs/superpowers` altındaki iki
yeni belge. `run_export.py`, `photo_store.py` ve `dist/` bu listede **olmamalı.**

Yol haritası listede çünkü 37. madde ona bu turda yazıldı — spec kaynağından türer, tersi değil.

- [ ] **Step 6: Commit**

```bash
git add queen-editor/backend docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for an export that carries no pictures

An export writes videos and nothing else. What leaves the machine is a
sequence of mp4s, and the pictures they were made from stay behind in the
project folder.

Four tests, all four red. Three are the domain's: every frame the sequence
holds hands its picture over under the video's own number, the extension is the
picture's own rather than a png written into the code, and a frame with no
video hands over nothing. The number belongs to the export and the extension to
the file, so the photos folder reads as the same sequence as the mp4s beside it
and the first jpg is not named wrongly.

The fourth is the store's, and it is the answer to what happens when both
export modes run at once. The design lets them, and a folder named down to the
minute is one folder for both -- so the second mode finds the picture already
there and must leave it alone.

That rule sits in the store rather than in the domain on purpose. A domain that
asked and then wrote would leave a gap between the two, and two threads copying
into one path is a half written file. Inside the store the answer and the write
are one act, which is also why it is tested against a real folder rather than a
double.

The double in the export tests copies nothing and skips nothing: it writes down
every call. A fake that carried the rule would leave those three tests marking
their own homework.

The roadmap gains item 37 in this commit: a spec derives from its source, never
the other way round.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:**

| Spec'te ne diyor | Planda nerede |
|---|---|
| Fotoğraf videosunun numarasıyla veriliyor | Task 1 Step 2, test 1 |
| Uzantı varsayılmıyor | Task 1 Step 2, test 2 |
| Videosu olmayan kare bir şey vermiyor | Task 1 Step 2, test 3 |
| Aynı hedefe ikinci kopyalama yazmıyor | Task 2 Step 1 |
| Kural depoda, alanda değil | Task 2 **Interfaces**, commit mesajı |
| Sahte kuralı taklit etmiyor | Task 1 Step 1'in docstring'i, Global Constraints |
| İptal/hata ve sayaç test edilmiyor | Bilerek dışarıda (aşağıda) |
| Kod değişmiyor | Global Constraints, Task 2 Step 5 |
| `dist` tazelenmiyor | Global Constraints, Task 2 Step 5 |

**Spec'ten sapan tek yer:** spec üçüncü testi "yeşil tutucu" diye yazıyor. Task 1 Step 3 bunu
düzeltiyor — bugün hiç fotoğraf kopyalanmadığı için o test de düşer. Sapma planda açıkça yazılı ve
beklenen sayı ona göre (**4 failed**).

**Yer tutucu yok:** Her adımda çalıştırılacak gerçek kod ve gerçek komut var; beklenen sayılar
(4 failed, 711 passed, 715, 582) ve beklenen hata (`AttributeError`) yazılı.

**Ad tutarlılığı:** `copy_photo(source, folder, filename)` iki görevde de aynı imzayla geçiyor —
Task 1 sahtesini, Task 2 gerçeğini bekliyor. `store.photos`, `store_at`, `with_videos`, `export`,
`FakeExporter`, `FOLDER` hepsi dosyalarda bugün duran adlar.

**Bilerek dışarıda:** iptal, hata ve ilerleme sayacı — üçünün de mevcut testleri var ve bu iş
hiçbirini değiştirmiyor. Ön yüz de açılmıyor.
