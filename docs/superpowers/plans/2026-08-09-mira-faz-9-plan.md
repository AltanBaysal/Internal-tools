# Mira Faz 9 (Dosya görünür) — Uygulama Planı

**Hedef:** Kesikli kart, cevabın altındaki dosya kartı, proje **Files** sütunu (Madde 20) ve
sohbetteki 320px ray (Madde 21).

**Mimari:** Liste dizinin kendisidir; ayrı bir kayıt dosyası yok. Akış iki yeni olay taşır —
`file-start` (araç çağrıldı) ve `file` (yazıldı). Mesaj hangi dosyaları doğurduğunu hatırlar.

**Kaynak spec:** [Faz 9](../specs/2026-08-09-mira-faz-9-dosya-gorunur-design.md)

## Global Kısıtlar

- Dosya listesi dizinden gelir; hiçbir yerde ikinci bir kayıt tutulmaz.
- Göreli zaman tarayıcıda hesaplanır.
- `run_tool` artık `ToolResult(text, created)` döndürür — cümleyi ayrıştırmak kırılgan olurdu.
- Commit: `git add <yollar>` → `git commit -m <mesaj> -- <aynı yollar>`.

---

### Task 1: Dosya listesi (arka uç)

**Dosyalar:** Oluştur `domain/file.py`, `domain/usecases/list_files.py` · Değiştir
`domain/ports.py`, `data/file_file_store.py`, `presentation/routes.py` · Test
`backend/tests/test_files_api.py`

`File(name, ext, modified_at)`; `ext` uzantının ilk üç harfi, küçük harf. `list_files` yeniden
eskiye sıralar (`modified_at`, eşitlikte ad).

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS

---

### Task 2: Akıştaki iki olay ve mesajın hatırlaması

**Dosyalar:** Değiştir `domain/tools.py`, `domain/chat.py`, `domain/usecases/append_message.py`,
`domain/usecases/stream_answer.py`, `data/file_chat_store.py`, `presentation/routes.py` · Test
`test_tools.py`, `test_stream_answer.py`, `test_chats_api.py` (güncelleme)

- `ToolResult = namedtuple("ToolResult", "text created")`, `created` varsayılan `None`.
- `Message.files: tuple = ()`; `file_chat_store` alanı yazar ve okur (boşsa yazmaz — boş liste
  diskte gürültü).
- `append_message(..., files=())`.
- `stream_answer` çağrıyı görünce `FileStarted()` verir, araç dönünce `FileWritten(name)` verir;
  `_sse` ikisini `file-start` ve `file` olaylarına çevirir. Tip üzerinden ayrım, mevcut kalıbın aynısı.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS

---

### Task 3: Ekranlar

**Dosyalar:** Oluştur `features/workspace/useFiles.js`, `features/workspace/FileRow.jsx`,
`features/workspace/FileRail.jsx` · Değiştir `ChatScreen.jsx`, `ProjectScreen.jsx`, `App.jsx`,
`useChat.js`, `workspace.css` · Test `FileRail.test.jsx`, `ChatScreen.test.jsx`, `App.test.jsx`

`useChat` iki alan daha verir: `creatingFile` (kesikli kart) ve `createdFiles` (bu turda doğanlar).
`file-start` → `creatingFile = true`; `file` → ada ekle ve `creatingFile = false`; `done` → ikisi de
temizlenir, çünkü sunucunun kaydı zaten kartı taşıyor.

`App` `file` olayında dosya listelerini tazeler — `useFiles`'ın `reload`'u `useChat`'e bir
`onFileCreated` geri çağrısı olarak geçer.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS · derle

---

## Öz-denetim

**Spec kapsaması.** On cümle: 1-2 Task 1 · 3-6 Task 2 · 7-10 Task 3.

**Ad tutarlılığı.** Olay adları `file-start` / `file` rotada, `sse.js` tüketicisinde ve `useChat`'te
aynı. `File(name, ext, modified_at)` → HTTP'de `name` / `ext` / `modifiedAt`, çeviri yalnız rotada.

**Risk.** `Message.files` diske yeni bir alan ekliyor; eski sohbet dosyalarında bu alan yok, o yüzden
okurken `raw.get("files", [])` kullanılmalı — yoksa Faz 8'de yazılmış sohbetler açılmaz.
