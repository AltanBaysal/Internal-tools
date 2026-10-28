# Madde 5 — Yeniden adlandırmalar, `← back` ve yardım notları gider · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m5-adlandirma-design.md](../specs/2026-08-17-queenagent-m5-adlandirma-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra implementasyon.

---

## Adım 1 — Testler (kırmızı commit)

### 1.1 · Arka uç

**`tests/test_rename.py` silinir.** İçindeki her şey sohbet ve dosya yeniden adlandırmasıydı; proje
yeniden adlandırmasının kendi dosyası (`test_edit_project.py`) zaten var.

**`tests/test_chats_api.py`**
- `test_a_chat_can_be_renamed_over_http` → `test_a_chat_cannot_be_renamed`: `PATCH` **405**.
- *(yeni)* `test_the_chat_rename_use_case_is_gone`: `ModuleNotFoundError`.

**`tests/test_files_api.py`**
- `test_renaming_over_http_answers_with_the_name_used` ve
  `test_renaming_a_file_that_is_gone_is_a_404` → tek bir `test_a_file_cannot_be_renamed`: `PATCH`
  **405**.
- *(yeni)* `test_the_file_rename_use_case_is_gone`: `ModuleNotFoundError`.
- *(yeni)* `test_the_store_offers_no_rename`: `FileFileStore`'da `rename` diye bir şey yok.

### 1.2 · Ön yüz

**`ProjectScreen.test.jsx`**
- `a chat row can be asked for a new title` → `a chat row offers no rename`.
- *(yeni)* `the screen starts with its title` — `← back` yok.
- *(yeni)* `nothing is written under the composer` — mono not yok.
- *(yeni)* `a full file list carries no advice under it` — öğüt satırı yok, boş hâl cümlesi durur.

**`FileRail.test.jsx`** — `the name button asks to rename that row` → `a file row offers no rename`.

**`ChatScreen.test.jsx`** — *(yeni)* `nothing is written under the composer`; geri başlığının
durduğunu söyleyen test varsa **korunur**, yoksa eklenir.

**`App.test.jsx`**
- `renaming the open file keeps the panel on it` → **silinir**.
- `an empty answer to the rename prompt sends nothing` → **silinir** (dosya yeniden adlandırmaydı;
  projenin aynı testi `an empty prompt sends nothing` olarak duruyor).

**Ölçülen kırmızı: arka uçta 5, ön yüzde 6** — tahminle aynı.

| Nerede | Kırmızı |
|---|---|
| `test_chats_api.py` | 2 (405, modül yok) |
| `test_files_api.py` | 3 (405, modül yok, store'da `rename` yok) |
| `ProjectScreen.test.jsx` | 4 (iki `← back`, not, öğüt satırı) |
| `ChatScreen.test.jsx` | 1 (not) |
| `App.test.jsx` | 1 (hiçbir satırda yeniden adlandırma yok) |

`ChatScreen`'in "geri yolu duruyor" testi **ilk koşuda yeşil geldi** — doğrusu da bu: o düğme
kalıyor, test onu koruyor. `FileRail`'in ve `ProjectScreen`'in "satırda yeniden adlandırma yok"
testleri de yeşil geldi, çünkü prop verilmediğinde düğme zaten çizilmiyordu; düğmeyi asıl sökecek
kırmızı `App.test.jsx`'te, gerçek prop bağlıyken duruyor.

---

## Adım 2 — Implementasyon

### 2.1 · Arka uç

1. `domain/usecases/rename_chat.py`, `domain/usecases/rename_file.py` **silinir**.
2. `domain/errors.py`: `InvalidChatTitle` gider (başka kullanıcısı olmadığı doğrulanır).
3. `domain/ports.py`: `FileStore.rename` bildirimi gider.
4. `data/file_file_store.py`: `rename` metodu gider.
5. `presentation/routes.py`: iki `PATCH` rotası ve importları gider.

### 2.2 · Ön yüz

6. `Composer.jsx`: `note` prop'u ve satırı gider.
7. `FileRow.jsx`: `onRename` ve "name" düğmesi gider.
8. `FileRail.jsx`, `ChatScreen.jsx`: `onRenameFile` geçişi gider.
9. `ProjectScreen.jsx`: iki `← back`, `onBack`, sohbet satırının "name" düğmesi, `onRenameChat`,
   `onRenameFile`, `note`, `file-list__note` paragrafı gider.
10. `App.jsx`: `renameFile`, `retitleChat`, `renameChat` importu, `useFiles`'tan `rename`,
    `leaveProject` ve ilgili prop'lar gider.
11. `useChatLists.js`: `renameChat` gider. `useFiles.js`: `rename` gider.
12. `workspace.css`: `.row-act`, `.composer__note`, `.file-list__note` gider. **`.back` kalır.**

### 2.3 · Kapanış denetimi

- `.back` hâlâ `ChatScreen`'de kullanılıyor mu — evet olmalı.
- `unique_name` ve `store.move` hâlâ silme/geri alma yolunda mı — evet olmalı.
- `grep -i rename` sonrası kalan tek geçerli kullanım proje yeniden adlandırması olmalı.

---

## Risk

Fazla silmek. `.back`, `unique_name`, `store.move` ve `FilePanel`'in `←` düğmesi silinenlere benziyor
ama hepsinin yaşayan kullanıcısı var; kapanış denetimi bunları tek tek yoklar.
