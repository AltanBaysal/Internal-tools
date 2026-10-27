# Madde 221 · Projeler arşivlenebilecek — test turunun planı

**Spec:** [test turu](../specs/2026-09-16-queen-editor-m221-arsiv-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. Testler henüz olmayan şunlara göre yazılıyor:

- `name_rules.ARCHIVE_DIR = "arsiv"` ve `validate`'in bu adı reddetmesi.
- `DriveStorage.list_dirs(subdir="")`, ve `rename_dir`'ün hedefin üst klasörünü açması.
- `DriveProjectStore.list_archived()`, `.archive(name)`, `.restore(name)`.
- `archive_project(store, halt, name)` ve `restore_project(store, name)`.
- `POST /api/projects/<p>/archive`, `POST /api/projects/<p>/restore`,
  `GET /api/projects/archived`.
- Ön yüzde `onArchive` / `onRestore` ve bir *Arşiv* anahtarı.

## Adımlar

**1 · `test_name_rules.py` — olgu 1–2.** `validate("arsiv")`, `validate("Arsiv")` ve
`validate("ARSIV")` üçü de bir cümle döner; cümle adın ayrılmış olduğunu söyler.

**2 · `test_drive_storage.py` — olgu 3–5.**

| Test | Ne bekler |
|---|---|
| `list_dirs can be asked about a subfolder` | `list_dirs("arsiv")` yalnız oradakileri verir |
| `list_dirs of a folder that is not there is empty` | `[]` — `list_files`'ın bugünkü kuralının aynısı |
| `rename_dir opens the target's parent` | `rename_dir("düğün", "arsiv/düğün")` ilk seferde çalışır |
| `rename_dir still moves rather than copies` | kaynak gitmiş, içindeki dosya hedefte |

**3 · `test_project_store.py` — olgu 6–10.**

| Test | Ne bekler |
|---|---|
| `the archive folder is not a project` | `arsiv/` varken `list()` onu saymaz |
| `the archive lists what was put in it` | `list_archived()` → `Project`, tarihiyle |
| `archiving moves the folder out of the root` | kökte yok, `arsiv/` altında var |
| `restoring brings it back` | tersi |
| `an archived project is not there any more` | `DriveStorage.dir_exists(ad)` false — üretim ve dışa aktarma onu böyle arıyor |

**4 · `test_project_usecases.py` — olgu 11–15.** `FakeProjectStore` arşiv taraflı hâle gelir
*(`archived` sözlüğü, `archive`/`restore`)*.

| Test | Ne bekler |
|---|---|
| `archiving stops a running production first` | `halt` çağrılmış, **ve taşımadan önce** |
| `archiving something that is not there says so` | `ProjectMissing` |
| `archiving onto a name the archive already holds` | `NameTaken` |
| `restoring something the archive does not hold` | `ProjectMissing` |
| `restoring onto a live name` | `NameTaken` |

**5 · `test_projects_routes.py` — olgu 16–19.** Üç yeni uç, ve redlerin kodları `delete`/`rename`
ile aynı: 404 yok, 409 dolu, 500 işletim sistemi.

**6 · Ön yüz — olgu 20–23.** `ProjectCard.test.jsx`'e *Arşivle* ve *Geri al*;
`ProjectsScreen.test.jsx`'e anahtar, arşiv görünümü, ve her iki hareketten sonra listenin yeniden
okunması.

**7 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-editor'ün **iki takımı da kırmızı**, queen-agent'ın ikisi yeşil.

**8 · Kırmızı commit'lenir.**

## Değişen dosyalar

`queen-editor/backend/tests/test_name_rules.py`,
`queen-editor/backend/tests/test_drive_storage.py`,
`queen-editor/backend/tests/test_project_store.py`,
`queen-editor/backend/tests/test_project_usecases.py`,
`queen-editor/backend/tests/test_projects_routes.py`,
`queen-editor/frontend/src/features/projects/ProjectCard.test.jsx`,
`queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`.
