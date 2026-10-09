# Madde 227 · Arşiv bir işaret olacak — test turunun planı

**Spec:** [test turu](../specs/2026-09-16-queen-editor-m227-arsiv-isaret-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. Testler henüz olmayan şunlara göre yazılıyor:

- `arsiv.json` — kökte, arşivlenen adların listesi; okunamayan dosya boş liste.
- `DriveProjectStore.archive/restore`'un klasöre değil o dosyaya yazması, ve yalnız `Project` /
  `False` dönmesi *(`NameTaken` yolu kalkıyor)*.
- `rename`'in işareti taşıması, `delete`'in düşürmesi.
- Depo açılırken `arsiv/` altındakileri köke geri getiren onarım.
- `archive_project(store, name)` — `halt` parametresi **gidiyor**.
- Arşivdeki kartın normal kart olması.

## Adımlar

**1 · `test_project_store.py` — olgu 1–9.** 221'den kalan üç test sorusunu değiştiriyor:
*"klasör kökten çıktı"* → **çıkmadı**, *"artık yok sayılıyor"* → **sayılmıyor**, ve iki ad çakışması
testi *(`archiving the same name twice`, `restoring onto a live name`)* **siliniyor** — çakışacak bir
hedef kalmadı.

| Test | Ne bekler |
|---|---|
| `archiving leaves the folder exactly where it was` | kökte duruyor, içindeki dosya yerinde |
| `an archived project is still there for everything that asks by name` | `dir_exists` → True |
| `restoring only lifts the mark` | klasör hiç kıpırdamamış |
| `renaming an archived project carries the mark along` | yeni ad arşivde, eski ad hiçbir yerde |
| `deleting an archived project drops its mark` | aynı adla açılan yeni proje arşivde doğmuyor |
| `an unreadable mark file reads as an empty archive` | bozuk JSON → `list()` yine çiziliyor |
| `is_archived reads the mark` | işarete göre true/false |

**2 · `test_project_store.py` — olgu 10–14, göç.** `arsiv/<proje>/dosya` elle kurulur, depo açılır.

| Test | Ne bekler |
|---|---|
| `a project left under the old archive folder is carried back` | kökte, ve `list_archived()`'da |
| `with its files` | dosya eksiksiz |
| `a name that is taken is carried back beside it` | `<ad> (arşiv)`, ikisi de duruyor |
| `the emptied folder is removed` | `arsiv/` yok |
| `nothing happens when there never was one` | hata yok, liste aynı |

**3 · `test_project_usecases.py` — olgu 15.** `archiving stops a running production first` **gider**
ve yerine tersi gelir: `archive_project` `halt` diye bir şey çağırmaz, çünkü artık almıyor.

**4 · `test_projects_routes.py` — olgu 16–17.** Arşivlenen bir projenin ayarları `GET`/`PUT`
ediliyor ve üretim `POST` ediliyor: üçü de **404 değil**. 221'in *"dosyayı kaybetmeden"* testi de
dosyanın **yerinde** olduğunu bekler hâle gelir.

**5 · `test_name_rules.py`** — kural aynı, cümlesi değil: `arsiv` hâlâ reddediliyor ama sebebi artık
onarımın oraya bakması. Test cümlenin adın ayrıldığını söylediğini tutmayı sürdürür.

**6 · Ön yüz — olgu 18–20.** `ProjectCard.test.jsx`: arşivdeki kartta kalem ve çöp **var**, orta
düğme *Geri al*. `ProjectsScreen.test.jsx`'teki *"an archived card offers only the way back"* testi
bunun tersini soruyordu — sorusu değişiyor.

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

`queen-editor/backend/tests/test_project_store.py`,
`queen-editor/backend/tests/test_project_usecases.py`,
`queen-editor/backend/tests/test_projects_routes.py`,
`queen-editor/backend/tests/test_name_rules.py`,
`queen-editor/frontend/src/features/projects/ProjectCard.test.jsx`,
`queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`.
