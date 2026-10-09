# Mira Faz 11 (Silme) — Uygulama Planı

**Hedef:** Dosya silme ve **Undo** (Madde 25) · onaylı sohbet silme (Madde 26).

**Mimari:** Silmek `trash/`'e taşımaktır; `os.replace` mtime'ı koruduğu için geri gelen dosya eski
sırasına oturur. Çöpteki ad yanıtta döner ve **şeritte** yaşar — diske hiçbir kayıt yazılmaz.

**Kaynak spec:** [Faz 11](../specs/2026-08-09-mira-faz-11-silme-design.md)

## Global Kısıtlar

- Silme fiziksel değildir (dosya); sohbet fizikseldir ve onay ister.
- Yanıtlar hep JSON, 204 yok.
- `unique_name` tek yerde yaşar: `domain/naming.py`.
- Test komutları: `python -m pytest d:\code\github\internal-tools\mira -q` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend test`.

---

### Task 1: `unique_name` ortak eve taşınır

**Dosyalar:** Oluştur `domain/naming.py` · Değiştir `domain/tools.py` · Test `test_tools.py`
(ithal yolu)

**Arayüzler:** Üretir `unique_name(existing, name)` — `domain/naming.py`.

- [ ] **Adım 1:** `unique_name`'i taşı, `tools.py` içinden `from ...naming import unique_name`.
- [ ] **Adım 2:** Takım yeşil kalmalı — davranış değişmiyor.

---

### Task 2: Silme ve geri alma (arka uç)

**Dosyalar:** Değiştir `services/store/store.py`, `domain/errors.py`, `domain/ports.py`,
`data/file_file_store.py`, `data/file_chat_store.py`, `presentation/routes.py` · Oluştur
`domain/usecases/delete_file.py`, `domain/usecases/restore_file.py`,
`domain/usecases/delete_chat.py` · Test `backend/tests/test_delete.py`,
`backend/tests/test_files_api.py`, `backend/tests/test_chats_api.py`

**Arayüzler:**
- Üretir: `delete_file(file_store, pid, name) -> str` (çöpteki ad) ·
  `restore_file(file_store, pid, trashed, name) -> None` · `delete_chat(chat_store, pid, cid)` ·
  `NameTaken` · `Store.remove(rel)`
- Tüketir: `FileNotFound`, `ChatNotFound` (Faz 10 ve 4'ten).

- [ ] **Adım 1: Testleri yaz**

```python
def test_deleting_moves_the_file_to_the_trash(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "body")
    assert delete_file(files, "p1", "plan.md") == "plan.md"
    assert files.list_names("p1") == []


def test_a_second_delete_of_the_same_name_does_not_lose_the_first(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "first")
    delete_file(files, "p1", "plan.md")
    files.write("p1", "plan.md", "second")
    assert delete_file(files, "p1", "plan.md") == "plan-2.md"


def test_restoring_keeps_the_time_so_the_row_goes_back_where_it_was(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "old.md", "a")
    before = list_files(files, "p1")[0].modified_at
    restore_file(files, "p1", delete_file(files, "p1", "old.md"), "old.md")
    assert list_files(files, "p1")[0].modified_at == before


def test_restoring_onto_a_taken_name_refuses(tmp_path):
    ...
    with pytest.raises(NameTaken):
        restore_file(files, "p1", trashed, "plan.md")


def test_deleting_a_chat_leaves_its_files_alone(tmp_path):
    ...
```

- [ ] **Adım 2: Kırmızı** · **Adım 3: Yaz**

```python
# data/file_file_store.py
TRASH_DIR = "trash"

def delete(self, project_id, name):
    if not self._store.exists(f"{project_id}/{FILES_DIR}/{name}"):
        return None
    # The trash keeps every version it is given: a name already in there is not overwritten.
    trashed = unique_name(self._store.list_dir(f"{project_id}/{TRASH_DIR}"), name)
    self._store.move(f"{project_id}/{FILES_DIR}/{name}", f"{project_id}/{TRASH_DIR}/{trashed}")
    return trashed

def restore(self, project_id, trashed, name):
    ...  # None when the trash has no such name, False when the name is taken again
```

Rotalar: `DELETE …/files/<name>` (404 / `{"trashed": …}`), `POST …/trash/<trashed>/restore`
(404 / 409 / `{}`), `DELETE …/chats/<cid>` (404 / `{}`).

- [ ] **Adım 4: Yeşil** · **Adım 5: Commit**

---

### Task 3: Şerit ve `×` (ön yüz)

**Dosyalar:** Oluştur `features/workspace/DeletedStrip.jsx` · Değiştir `shared/api.js`,
`useFiles.js`, `useChatLists.js`, `FileRow.jsx`, `FileRail.jsx`, `ProjectScreen.jsx`, `App.jsx`,
`workspace.css` · Test `DeletedStrip.test.jsx`, `useFiles.test.jsx`, `FileRail.test.jsx`,
`ProjectScreen.test.jsx`, `App.test.jsx`

**Arayüzler:**
- Üretir: `deleteJson(path)` · `useFiles -> {files, reloadFiles, deleting}` ·
  `deleting = {deleted, error, remove(name), undo()}` · `deleteChat(projectId, chatId)`
- Tüketir: Faz 10'un `reading` demeti — `App` silinen dosya açıksa `reading.close()` çağırır.

`FileRow` bir `onDelete` alır; `×` satırın sağında durur ve `event.stopPropagation()` ile satırı
açmadan siler.

- [ ] **Adım 1: Testleri yaz** — şerit metni ve Undo düğmesi, `×` çağrısı, onaylı sohbet silme
      (iptal edilince hiçbir istek gitmez).
- [ ] **Adım 2: Kırmızı** · **Adım 3: Yaz** · **Adım 4: Yeşil** · **Adım 5: Derle ve commit**

---

## Öz-denetim

**Spec kapsaması.** §1-2 Task 2 · §3 Task 2 (uç nokta) + Task 3 (onay) · §4-5 Task 3 · §6'daki
`unique_name` taşıması Task 1. On bir testin hepsi bir task'a düşüyor (1-7 Task 2, 8-11 Task 3).

**Ad tutarlılığı.** `trashed` sunucudan ön yüze aynı adla gidiyor; `deleted = {name, trashed}`.
`FileStore.delete` çöpteki adı döner, `restore` `None`/`False`/`True` ile üç durumu ayırır ve use
case bunları `FileNotFound` / `NameTaken` / başarıya çevirir.

**Risk.** `DELETE …/files/<name>` ile `GET …/files/<name>` aynı adres, farklı fiil — Flask ayırır.
`×`'in satır tıklamasını tetiklememesi için `stopPropagation` şart; testte de bu var.
