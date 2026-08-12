# Queen Editor v5 · Görev 30 — Export koşusu · Uygulama planı

> Tasarım: [Görev 30 spec](../specs/2026-08-12-queen-editor-v5-gorev-30-export-kosusu-design.md).

**Hedef:** export gerçekten koşsun, ilerlesin, hata verince temizlensin, iptal edilebilsin.

**Mimari:** yeni port `VideoExporter`; data'da `FfmpegVideoExporter`; use case
`run_export` + `export_state`; kendi işçisi `ExportRunner`; uçlar `POST …/export/<mode>`,
`GET …/export/status`, `POST …/export/cancel`.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — İşçi ve koşu

**Dosyalar:** yeni `export_runner.py`, `domain/usecases/run_export.py`, `domain/ports.py`,
`data/photo_store.py`, test: yeni `tests/test_export.py`

**Arayüz:**

```python
class ExportRunner:          # one per mode; mirrors PhotoRunner's shape
    def start(self, mode, job) -> None    # refuses a second run of the same mode (Busy)
    def report(self, mode, **state) -> None
    def cancel(self, mode) -> None
    def cancelled(self, mode) -> bool
    def state(self) -> dict               # {"merged": {...}, "separate": {...}}


def run_export(runner, store, record, plan_store, order_store, exporter, now, project, mode):
    """Writes the project's videos into a fresh dated folder. Returns the folder."""
```

- [ ] **Adım 1 — kırmızı testler** (sahte exporter, sahte store):

```python
def test_separate_export_numbers_the_videos_from_the_foot_of_the_gallery():
    ...
    assert [target for _v, _a, target in exporter.pieces] == [
        f"{folder}/01.mp4", f"{folder}/02.mp4"]


def test_a_frame_with_a_sound_is_written_with_it():
    assert exporter.pieces[0][1] == "0_a_V1_0_S1_0.wav"


def test_a_frame_with_no_video_is_skipped():
    ...

def test_merged_export_writes_one_file_named_after_the_project():
    assert exporter.merged == ([f"{folder}/01.mp4"], f"{folder}/düğün.mp4")


def test_a_failed_export_takes_its_half_written_folder_with_it():
    with pytest.raises(RuntimeError):
        run_export(...)
    assert store.removed_dirs == [folder]


def test_cancelling_stops_between_pieces_and_removes_the_folder():
    ...

def test_the_state_counts_what_has_been_written():
    assert runner.state()["separate"] == {"state": "done", "written": 2, "total": 2,
                                          "target": folder, "error": None}
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:** `run_export`:

```python
def run_export(runner, store, record, plan_store, order_store, exporter, now, project, mode):
    frames = exportable(list_frames(record, store, plan_store, order_store, project))
    folder = store.make_export_folder(project, now())
    runner.report(mode, state="running", written=0, total=len(frames), target=folder)
    pieces = []
    try:
        for index, frame in enumerate(frames, start=1):
            if runner.cancelled(mode):
                store.remove_dir(folder)
                return runner.report(mode, state="idle", written=0, target=None)
            target = f"{folder}/{index:02d}.mp4"
            exporter.piece(store.file_path(project, frame["layers"]["video"]),
                           audio_of(store, project, frame), target)
            pieces.append(target)
            runner.report(mode, written=index)
        if mode == MERGED:
            runner.report(mode, state="merging")
            exporter.merge(pieces, f"{folder}/{project}.mp4")
    except Exception as exc:
        # Half a folder is worse than none: it is removed before the screen is told (madde 94).
        store.remove_dir(folder)
        runner.report(mode, state="error", error=str(exc))
        raise
    runner.report(mode, state="done")
    return folder
```

`PhotoStore`'a: `file_path(project, name)`, `make_export_folder(project, stamp)`,
`remove_dir(path)`; `DriveStorage`'a karşılıkları.

- [ ] **Adım 4:** yeşil.

---

## Görev 2 — ffmpeg ve uçlar

**Dosyalar:** yeni `data/ffmpeg_video_exporter.py`, `presentation/routes.py`, `main.py`,
testler: `tests/test_ffmpeg_exporter.py`, `tests/test_photo_routes.py`

- [ ] **Adım 1 — kırmızı testler:** komutu sahte `run` ile yakala:

```python
def test_a_silent_piece_is_copied_rather_than_re_encoded():
    assert calls[0][:6] == ["ffmpeg", "-y", "-i", "0.mp4", "-c", "copy"]


def test_a_sound_is_laid_over_the_video():
    assert "-shortest" in calls[0]


def test_the_command_output_is_what_a_failure_says():
    with pytest.raises(RuntimeError) as caught:
        exporter.piece(...)
    assert "ffmpeg: no such file" in str(caught.value)
```

Yol testleri: `POST …/export/separate` → 202; koşarken ikinci istek 409; `GET …/export/status`
ilerlemeyi verir; `POST …/export/cancel` 202.

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:** `FfmpegVideoExporter(run=subprocess.run)`; komutlar:

```python
# Stream copy: the pieces are already the size and codec the graph made them, and re-encoding
# would cost minutes and quality for nothing.
["ffmpeg", "-y", "-i", video, "-c", "copy", target]
["ffmpeg", "-y", "-i", video, "-i", audio, "-c:v", "copy", "-c:a", "aac", "-shortest", target]
["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", target]
```

Hata: dönüş kodu sıfır değilse `RuntimeError(stderr tail)` — kendi sebebini uydurmaz.

- [ ] **Adım 4:** yeşil.

---

## Görev 3 — Ekran: ilerleme, sonuç, iptal

**Dosyalar:** `ExportScreen.jsx`, `shared/api.js`, test: `ExportScreen.test.jsx`

- [ ] **Adım 1 — kırmızı testler:** basınca `startExport("düğün", "separate")` çağrılıyor ·
  koşarken butonun yerinde "1 / 3 yazıldı…" · öteki buton basılabilir · bitince yeşil kartta
  "✓ Export tamamlandı" ve hedef · hata kırmızı kartta sebebiyle · koşarken "Galeriye dön"
  onay soruyor ve onaylayınca `cancelExport` çağrılıyor.

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:** `api.js`: `startExport`, `getExportState`, `cancelExport`. Ekran durumu 1 sn'de
bir sorar (koşarken); buton içeriği moda göre ilerleme; yeşil/kırmızı kart; çıkışta
`ConfirmModal width={400}` (tasarım 380 diyor; kit 320/400 taşıyor — 400 seçilir ve spec'e not
düşülür).

- [ ] **Adım 4:** yeşil.

---

## Görev 4 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): the export writes the videos it promised
```
