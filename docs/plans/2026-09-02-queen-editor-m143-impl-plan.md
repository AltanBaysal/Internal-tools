# Madde 143 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-02-queen-editor-m143-panel-uygulama-design.md](../specs/2026-09-02-queen-editor-m143-panel-uygulama-design.md)
**Dal:** `feat/v6`
**Kırmızı commit:** `9d370be`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. `model_groups.py` — satır ve başlık.

Satır:

```python
    # Which checkpoint is on the machine is the user's pick since Madde 140, so this row names a
    # kind of file rather than one file: the graph renders with whichever it was handed, and the
    # panel asks whether there is anything to hand it.
    {"folder": "checkpoints", "suffix": ".safetensors"},
```

Modülün başındaki cümle de düzeliyor: bir satır artık bir dosyayı ya da bir dosya türünü
adlandırıyor.

→ `test_the_photo_group_carries_everything_the_graph_reads` yeşile döner.

## B. `ports.py` — ikinci soru.

```python
    def has_any(self, folder: str, suffix: str) -> bool:
        """Is there a file of this kind here? What a group asks when which one is the user's pick."""
```

## C. `list_producers.py` — şekle bakan tek satır.

```python
        installed = bool(group) and all(
            files.exists(spec["folder"], spec["name"]) if "name" in spec
            else files.has_any(spec["folder"], spec["suffix"])
            for spec in group)
```

Modülün docstring'i de bir cümle kazanıyor: kurulu olmak, grubun her satırının karşılandığı
anlamına geliyor — ve bir satır ya bir dosya ya bir tür istiyor.

→ C1, C2 ve C3 yeşile döner.

## D. `comfy_models.py` — gerçeğin cevabı.

```python
    def has_any(self, folder, suffix):
        """Is there a file of this kind in the folder? Answered with scandir rather than listdir:
        it stops at the first match, and is_file() comes off the entry instead of a second stat.

        A missing folder answers False rather than raising: the notebook creates these on startup,
        but the app also comes up on a machine where nothing was ever installed, and for the panel
        "no folder" and "empty folder" are the same answer.
        """
        directory = os.path.join(self._root, "models", folder)
        try:
            return any(entry.name.endswith(suffix) and entry.is_file()
                       for entry in os.scandir(directory))
        except FileNotFoundError:
            return False
```

## E. Defterin uyarı notu kalkar.

`4d387058` markdown hücresindeki *"Bilinen davranış"* bloğu — `nova3DCG` kutusu boşken panelin
*"kurulu değil"* demesi. Artık doğru değil, ve doğru olmayan bir uyarı yanlış bilgidir.

## F. Koşuldu: **736 yeşil, 0 kırmızı.**

`python -m pytest queen-editor -q` — dört kırmızının dördü döndü, tek seferde, ara kırmızı yok.
Adı geçen dört bekçi de yeşil kaldı: `test_a_kind_with_no_group_is_not_installed`,
`test_one_missing_file_means_not_installed` *(adlı satır hâlâ ad arıyor)*,
`test_every_file_the_panel_counts_is_fetched_by_the_notebook` *(süzgeç bu turda anlamını kazandı —
checkpoint satırı eleniyor, geri kalan dördü aranmaya devam ediyor)*, ve
`test_the_weights_path_is_built_from_the_group_row`.

**Toplam 733'ten 736'ya çıktı**, çünkü kırmızı tur üç yeni test getirmişti *(seçilen model / boş
klasör / yarım indirme)* ve dördüncü kırmızı zaten var olan bir testin yeniden yazılmış hâliydi.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil.**

## G. Yeşil commit.

Dört kaynak dosyası, defter, ve bu turun iki belgesi.

`dist` derlenmiyor: ön yüz değişmiyor.

## Bilerek yapılmayanlar

**Video ve ses grupları** — seçim yok, soru değişmiyor.

**Rotalar, ön yüz, `dist`** — cevabın şekli değişmiyor, `installed` hâlâ `bool`.

**Grafiğin fallback'i** — ayrı soru, ve davranışı yanlış değil.
