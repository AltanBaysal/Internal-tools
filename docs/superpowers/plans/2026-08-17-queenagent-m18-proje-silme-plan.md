# Madde 18 — Proje silinir · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m18-proje-silme-design.md](../specs/2026-08-17-queenagent-m18-proje-silme-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Madde büyük, o yüzden **iki döngü**, her biri kırmızı + yeşil:

- **A — arka uç:** silme, çöp düzeni, yol.
- **B — ön yüz:** iki kapı, menü, kutu, silmeden sonra nereye, Esc sırası.

---

## A1 — Arka uç testleri (kırmızı)

**`tests/test_delete.py`** (ya da yeni `test_delete_project.py`)
- silinen projenin dizini `trash/<pid>` altına taşınır; `project.json`, `chats/`, `files/` içeride.
- proje listeden düşer.
- aynı id ikinci kez çöpe giderse üstüne yazılmaz.
- olmayan proje `ProjectNotFound`.

**`tests/test_projects_api.py`** — `DELETE /api/projects/<pid>` 200 ve `{"trashed": …}`; olmayanda
404. Geri yükleme yolu **yok** — `url_map` bunu kanıtlıyor.

## A2 — Arka uç uygulaması

1. `ports.py` — `ProjectStore.delete`.
2. `data/file_project_store.py` — dizini `trash/` altına taşı, `unique_name` ile.
3. `domain/usecases/delete_project.py`.
4. `presentation/routes.py` — `DELETE /api/projects/<pid>`.
5. `main.py` — bir şey gerekiyorsa bağla.

---

## B1 — Ön yüz testleri (kırmızı)

**`Sidebar.test.jsx`** — satır artık kapsayıcı; projeyi açan düğme adıyla bulunuyor; ⋯ düğmesi var
ve menüyü açıyor; menüde "Rename" ve "Delete project".

**Yeni `RowMenu.test.jsx`** — iki seçenek, dış tıklama kapatır, seçim menüyü kapatır.

**`ProjectScreen.test.jsx`** — başlıkta "Delete" düğmesi, `onDelete` çağırır.

**`App.test.jsx`**
- iki kapı da aynı kutuyu açar; kutu sayıları ve tekil hâli söyler.
- onaydan sonra `DELETE` atılır ve proje listeden düşer.
- içinde bulunulan proje silinince kalan ilk projeye gidilir; hiç kalmazsa `/`.
- başka proje silinince adres kıpırdamaz.
- Esc önce menüyü, sonra kutuyu, sonra paneli kapatır.
- hiçbir yerde "Undo" yok.

**`workspace.css.test.js`** — menü 176px ve `position: fixed`; başlık satırı sarar; başlıktaki
"Delete" kırmızı çerçeveli, hover'da dolar.

## B2 — Ön yüz uygulaması

1. `useProjects.js` — `removeProject`.
2. `RowMenu.jsx`.
3. `Sidebar.jsx` — satırın kutusu + ⋯.
4. `ProjectScreen.jsx` — başlık düğmesi.
5. `App.jsx` — onay durumu, silme, gidilecek yer, Esc sırası.
6. `workspace.css`.

### Kapanış denetimi

- `grep Undo` ön yüzde yalnız dosya şeridinde (o Madde 19'da gidiyor).
- `grep addEventListener` `ConfirmDialog.jsx`'te hâlâ boş.

---

## Risk

Kenar çubuğu satırının kutusu değişiyor; var olan testler adı iç düğmede arayacak. Davranış aynı.
