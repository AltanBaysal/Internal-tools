# Madde 506 — Projeleri toplu arşivle/sil, plan

**Hedef:** All projects'te seçilen projeler tek işlemle arşivleniyor, arşivden çıkıyor ya da (sorulup)
siliniyor; bir toplu işlem tek istek.

**Spec:** [m506](../specs/2026-10-27-queen-agent-m506-toplu-arsiv-sil-design.md)

## Kısıtlar

- Toplu işlem başına bir istek, cevabı liste; ayrı liste okuması yok.
- Silmede çöp bir kez listelenir: port'un `delete`'i `delete_many` olur (ana ajanın onayı).
- Tek projenin kapıları ve testleri aynı kalır.
- Önce test kırmızı, sonra kod.

### Görev 1: Depo

**Dosyalar:** `backend/features/workspace/data/file_project_store.py`, `domain/ports.py`,
`tests/test_file_project_store.py`

- [ ] Eski `delete` testleri `delete_many([id])`'e; yeni testler: çöp bir kez listelenir, bilinmeyen ve
  tekrarlanan kimlik, aynı çağrıda numaralandırma, disk yarıda düşünce yalnız çöpe gidenlerin satırı.
- [ ] `delete_many(ids)`: tekilleştir, kilit altında kayıtlar, çöpü bir kez listele, taşı + kaydı yaz,
  `finally`'de tek `_change`.
- [ ] Port: `delete` → `delete_many`.

### Görev 2: Kullanım durumları

**Dosyalar:** `domain/usecases/delete_project.py`, `edit_project.py`, `tests/test_delete_project.py`,
`tests/test_pin_archive.py`

- [ ] Testler: çok projeli silme; tur dönen proje hepsini durdurur; toplu arşiv sabitlemeyi götürür ve
  bilinmeyen kimliği atlar.
- [ ] `delete_project` → `delete_many([id])`; yeni `delete_projects`; yeni `archive_projects`.

### Görev 3: Kapılar

**Dosyalar:** `presentation/routes.py`, `tests/test_projects_api.py`

- [ ] Testler: `PATCH /api/projects` ve `POST /api/projects/delete` listeyle cevaplar; `409`; `400`'ler.
- [ ] `listed()` yardımcısı (GET ile ortak), `_ids(payload)`, iki kapı, `PROJECTS_BUSY`, `NOT_IDS`,
  `NOT_ARCHIVED`.

### Görev 4: Seçim ve çubuk

**Dosyalar:** `frontend/src/features/workspace/AllProjectsScreen.jsx`, `ProjectRow.jsx`,
`AllProjectsScreen.test.jsx`

- [ ] Testler (kırmızı): kutucuk, `is-picking`, Ctrl/Cmd, Shift aralığı, `mousedown`, çubuk, sekme,
  toplu arşiv/ret/arşivden çıkarma, Delete teslimi, arama.
- [ ] `ProjectRow`: kutucuk, `picked`/`picking`/`onPick`, Ctrl / Shift (seçimin yerine) / Ctrl+Shift
  (ekler) tıklaması, satırda ve kutucukta Shift `mousedown`.
- [ ] `AllProjectsScreen`: `picked`, `anchor`, `chosen`, `pick`, `asking` (tek basışla ortak),
  `archiveChosen`, `changeTab`, başlıkta çubuk.

### Görev 5: İstekler ve soru

**Dosyalar:** `useProjects.js`, `App.jsx`, `App.test.jsx`

- [ ] Testler (kırmızı): tek `PATCH`/`POST` ve ardından `GET` yok; soru sayılarla, tekil; Cancel; ret.
- [ ] `useProjects`: `changeMany` (rette bir `GET`), `archiveProjects`, `removeProjects`.
- [ ] `App`: `askToDeleteMany`, iki yeni prop.

### Görev 6: CSS

**Dosyalar:** `workspace.css`, `workspace.css.test.js`, `shared/app.css.test.js`

- [ ] Testler: kutucuğun görünürlük kuralları, Delete'in rengi, `:focus-visible` sayımı 3.
- [ ] `.all-projects__actions`, `__bulk`, `__bulk-count`, `__bulk-delete`, `__row-pick`, `.is-picked`.

### Görev 7: Dist, takımlar, yol haritası

- [ ] `npm run build --prefix queen-agent/frontend`.
- [ ] `npm test --prefix queen-agent/frontend` — yeşil.
- [ ] `python -m pytest queen-agent -q` — dist testi dışında yeşil (commit'e kadar beklenen).
- [ ] Yol haritasında 506 ✅, başlık "5/5 bitti". Commit'i ana ajan atar.
