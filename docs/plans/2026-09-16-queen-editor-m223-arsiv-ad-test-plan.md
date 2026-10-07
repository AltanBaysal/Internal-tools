# Madde 223 · Arşivdeki ad tutulmuş sayılacak — test turunun planı

**Spec:** [test turu](../specs/2026-09-16-queen-editor-m223-arsiv-ad-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. Testler henüz olmayan şunlara göre yazılıyor:

- `DriveProjectStore.is_archived(name)` — arşivde bu adla bir proje var mı.
- `DriveProjectStore.create` ile `.rename`'in arşivi de dolu sayması: ikisi de `None` döner, yani
  bugünkü *"dolu"* cevabının aynısı — çağıran için yeni bir dönüş değeri yok.
- `name_rules.archive_taken(name)` — redin Türkçe cümlesi, tek yerde.
- Ön yüzde bir **işlem hatası** satırı: `handleArchive` / `handleRestore` yakalar, sunucunun cümlesi
  listenin üstünde durur, liste yerinde kalır.

**Sebebi neden ayrı bir soru:** `create` *"dolu"* derken hangi dolu olduğunu söylemiyor, ve iki
durumun iki cümlesi var. Kullanım bu yüzden **yalnız red yolunda** `is_archived`'a soruyor — başarılı
bir açılış fazladan hiçbir şey sormuyor, ki Drive'da her soru bir gidiş geliş *(madde 225)*.

## Adımlar

**1 · `test_project_store.py` — olgu 1–5.**

| Test | Ne bekler |
|---|---|
| `a name the archive holds cannot be created` | `create("balo")` → `None`, arşivde `balo` varken |
| `and nothing is left behind in the root` | kökte `balo` klasörü **yok** — kontrol `mkdir`'den önce |
| `a project cannot be renamed onto an archived name` | `rename("düğün", "balo")` → `None`, `düğün` yerinde |
| `a free name is still created` | eskisi gibi `Project` döner |
| `a name a live project holds is still taken` | eskisi gibi `None` |
| `is_archived answers both ways` | arşivdeki ad için true, ötekiler için false |

**2 · `test_project_usecases.py` — olgu 6–10.** `FakeProjectStore` `is_archived`'ı öğrenir ve
`create`/`rename` arşivdeki adda `None` döner.

| Test | Ne bekler |
|---|---|
| `creating onto an archived name is refused` | `NameTaken` |
| `and the sentence says the name is in the archive` | cümlede *arşiv* geçer, ad geçer |
| `renaming onto an archived name is refused the same way` | aynı sınıf, **aynı cümle** |
| `a name a live project holds keeps the old sentence` | *"Bu ad zaten kullanılıyor…"* — değişmedi |
| `restoring works whenever the root is free` | `restore_project` hata atmıyor |

Dördüncüsü bu turun en sessiz çivisi: yeni cümle eskisinin **yerine** geçerse, dolu bir proje adına
çarpan kullanıcı arşivde olmayan bir şeyi aramaya gider.

**3 · `test_projects_routes.py` — olgu 11–12.** Arşivdeki adla `POST /api/projects` ve
`POST /api/projects/<p>/rename`: ikisi de **409**, gövdedeki `error` sunucunun cümlesi. Yeni bir kod
yok — dolu ad zaten 409.

**4 · `ProjectsScreen.test.jsx` — olgu 13–16.** `archiveProject` / `restoreProject` reddedilecek
biçimde sahtelenir.

| Test | Ne bekler |
|---|---|
| `a failed archive says what the server said` | cümle ekranda, birebir |
| `a failed restore says the same way` | aynı |
| `the list is still there after a failure` | kartlar duruyor — `StatusErrorCard` listeyi silmiyor |
| `the next success clears the line` | başarılı işlemden sonra cümle yok |

**5 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-editor'ün **iki takımı da kırmızı**, queen-agent'ın ikisi yeşil.

**6 · Kırmızı commit'lenir.**

## Değişen dosyalar

`queen-editor/backend/tests/test_project_store.py`,
`queen-editor/backend/tests/test_project_usecases.py`,
`queen-editor/backend/tests/test_projects_routes.py`,
`queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`.
