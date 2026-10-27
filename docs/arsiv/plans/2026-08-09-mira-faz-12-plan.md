# Mira Faz 12 (Yeniden adlandırma) — Uygulama Planı

**Hedef:** Sohbet başlığı ve dosya adı değişebilsin (Madde 27); cevabın altındaki kart listeyle
kesişsin.

**Mimari:** İki `PATCH`. Dosyanın yeni adı diskteki addır; çakışma `unique_name` ile çözülür ve
yanıt kullanılan adı söyler. Hiçbir mesaj yeniden yazılmaz — kart mesajın hafızası ile bugünkü
listenin kesişimi olarak çizilir.

**Kaynak spec:** [Faz 12](../specs/2026-08-09-mira-faz-12-ad-design.md)

## Global Kısıtlar

- Kullanıcının verdiği dosya adı da `safe_name`'den geçer.
- Boş girdi iptal: tarayıcı istek atmaz, sunucu da boş başlığı 400 ile reddeder.
- Test komutları: `python -m pytest d:\code\github\internal-tools\mira -q` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend test`.

---

### Task 1: Yeniden adlandırma (arka uç)

**Dosyalar:** Değiştir `domain/errors.py`, `domain/ports.py`, `data/file_file_store.py`,
`presentation/routes.py` · Oluştur `domain/usecases/rename_chat.py`,
`domain/usecases/rename_file.py` · Test `backend/tests/test_rename.py`,
`backend/tests/test_chats_api.py`, `backend/tests/test_files_api.py`

**Arayüzler:**
- Üretir: `rename_chat(chat_store, pid, cid, title) -> Chat` ·
  `rename_file(file_store, pid, name, wanted) -> File` · `InvalidChatTitle` ·
  `FileStore.rename(pid, name, wanted) -> File | None` (adı değil satırın kendisini döner: mtime'ı
  ikinci bir okumayla sormaya gerek kalmaz)
- Tüketir: `safe_name` (`domain/tools.py`), `unique_name` (`domain/naming.py`),
  `read_body` (Faz 10), `ChatNotFound` / `FileNotFound`.

- [ ] **Adım 1:** testleri yaz — başlık değişimi, boş başlık 400, mtime korunumu, `-2` çakışması,
      kirli ad temizliği, 404'ler.
- [ ] **Adım 2:** kırmızı · **Adım 3:** yaz · **Adım 4:** yeşil · **Adım 5:** commit.

```python
# data/file_file_store.py
def rename(self, project_id, name, wanted):
    path = f"{project_id}/{FILES_DIR}/{name}"
    if not self._store.exists(path):
        return None
    # Numbering a file against itself would turn plan.md into plan-2.md for no reason.
    taken = name if wanted == name else unique_name(self.list_names(project_id), wanted)
    self._store.move(path, f"{project_id}/{FILES_DIR}/{taken}")
    return File(name=taken, ext=extension_of(taken), modified_at=_iso(self._store.mtime(...)))
```

---

### Task 2: `name` düğmesi ve kartın kesişimi (ön yüz)

**Dosyalar:** Değiştir `useChatLists.js`, `useFiles.js`, `FileRow.jsx`, `ProjectScreen.jsx`,
`ChatScreen.jsx`, `App.jsx` · Test `FileRail.test.jsx`, `ProjectScreen.test.jsx`,
`ChatScreen.test.jsx`, `App.test.jsx`

**Arayüzler:**
- Üretir: `renameChat(projectId, chatId, title)` · `useFiles → deleting` yanında `rename(name)`
- Tüketir: Faz 10'un `reading` demeti — ad değişince `reading.open(yeniAd)`.

`ChatScreen` `message.files` listesini `files` ile kesiştirir: `files` boşken (henüz gelmemişken)
kart çizilmez, çünkü listenin cevabı olmadan kartın doğruluğu bilinmiyor.

- [ ] **Adım 1:** testleri yaz · **Adım 2:** kırmızı · **Adım 3:** yaz · **Adım 4:** yeşil ·
      **Adım 5:** derle ve commit.

---

## Öz-denetim

**Spec kapsaması.** §1-2 Task 1 · §3-4 Task 2. Dokuz testin hepsi bir task'a düşüyor (1-6 Task 1,
7-9 Task 2).

**Ad tutarlılığı.** `rename` üç katmanda aynı ad; `wanted` istenen, dönen değer kullanılan.
`InvalidChatTitle` yalnız sohbete ait — projenin `InvalidProjectName`'i duruyor.

**Risk.** Kartın kesişimi, dosya listesi henüz yüklenmeden kartı gizler; ekran bir an kartsız
görünür. Kabul: yanlış bir ad göstermektense bir an geç göstermek yeğdir.
