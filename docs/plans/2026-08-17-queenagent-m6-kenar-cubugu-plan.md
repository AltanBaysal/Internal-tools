# Madde 6 — Kenar çubuğu kuralı ve logo · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m6-kenar-cubugu-design.md](../specs/2026-08-17-queenagent-m6-kenar-cubugu-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra implementasyon.

---

## Adım 1 — Testler (kırmızı commit)

### 1.1 · Arka uç

**`test_chats_api.py`**
- `test_starting_a_chat_from_nowhere_is_gone` → beklenen **405 değil 404**: `GET /api/chats` de
  gidince adres tümüyle kayboluyor, yöntem değil adres tanınmaz oluyor. *(Madde 5'te 405 doğruydu;
  bu maddede doğrusu değişiyor.)*
- `test_recent_chats_span_every_project_and_name_theirs` → `test_there_is_no_workspace_wide_chat_list`:
  `GET /api/chats` **404**.
- *(yeni)* `test_the_recent_chats_use_case_is_gone`: `ModuleNotFoundError`.

**`test_append_message.py`**
- `test_recent_chats_cross_projects_and_come_newest_first` → **silinir**; çalışma alanı genelinde
  sohbet listesi diye bir kavram kalmıyor.
- `test_a_later_message_lifts_its_chat_to_the_top` → `list_chats` ile **tek proje içinde** yeniden
  yazılır; iddia (sonradan gelen mesaj sohbeti üste taşır) aynen korunur.

### 1.2 · Ön yüz

**`Sidebar.test.jsx`**
- `both section headings are there with no projects at all` → **tersine döner**:
  `with no project selected only the wordmark and the projects remain` — "New chat" ve "Recent
  chats" yok, "Projects" var.
- `recent chats are listed and the open one is marked` ve `clicking a recent chat carries its
  project along` → prop `chats`, proje seçili, `onOpenChat(chatId)` tek argüman.
- `with no projects New chat is hidden rather than disabled` → koşul proje **seçimi** olur.
- *(yeni)* `at most eight chats are listed`.
- *(yeni)* `there is no logo mark`.

**`useRoute.test.js`** — *(yeni)* `a draft chat has an address of its own`:
`parsePath("/p/p1/c/new")` → `{ view: "chat", projectId: "p1", chatId: "new" }`.

**`App.test.jsx`**
- *(yeni)* `New chat opens an empty chat in the project it was pressed in`: adres
  `/p/p1/c/new`, ekranda "New chat" başlığı, sunucuya `chats/new` **sorulmaz**.
- *(yeni)* `the first message in a draft creates the chat and takes its address`: `POST` gider,
  adres `/p/p1/c/c1` olur ve **`pushState` kullanılmaz**.
- `a chat the user confirms is deleted and leaves both lists` → tek listeye iner.
- `nothing asks the server to open a project and a chat at once` → `GET /api/chats` de artık
  istenmemeli; iddia "hiçbir istek `/api/chats` adresine gitmez" olur.

**Ölçülen kırmızı: arka uçta 2, ön yüzde 5 + App'ten en az 2.**

Arka uç 4 değil 2 çıktı: yeniden yazılan iki test (`test_a_projects_chats_come_back_newest_first` ve
`test_a_later_message_lifts_its_chat_to_the_top`) **ilk koşuda yeşil** geldi — proje içi sıralama
zaten böyle çalışıyordu, değişen yalnız hangi listeye bakıldığı. Doğru olan da bu: o iki iddia
korunuyor, kaldırılan kavram çalışma alanı geneli.

`useRoute`'un yeni taslak testi de yeşil geldi — `parsePath` `/p/p1/c/new`'i zaten doğru okuyor;
test var olan davranışı yazıya geçiriyor, yeni bir şey istemiyor.

Ön yüzde `Sidebar.test.jsx` 5 kırmızı verdi; `App.test.jsx`'in sayısı vitest çıktısının kesilmesi
yüzünden okunamadı, ama en az iki yeni test (taslak adresi ve ilk mesaj) orada kırmızıydı.

---

## Adım 2 — Implementasyon

### 2.1 · Arka uç

1. `presentation/routes.py`: `GET /api/chats` ve `list_recent_chats` importu gider.
2. `domain/usecases/list_recent_chats.py` **silinir**.
3. `ChatStore.list_all` portu: başka çağıranı kalmadıysa o da gider — kapanışta denetlenir.

### 2.2 · Ön yüz

4. `useChatLists.js`: `useRecentChats` gider; *"Two lists, two questions"* yorumu artık doğru
   olmadığı için düzeltilir.
5. `Sidebar.jsx`: `sidebar__mark` gider; "New chat" ve "Recent chats" bölümleri
   `activeProjectId` varken çizilir; `chats` prop'u en çok 8 satır çizer; `onOpenChat(chatId)`.
6. `App.jsx`: `useRecentChats` ve `reloadRecentChats` çağrıları gider; kenar çubuğuna
   `projectChats` verilir. `openNewChat` artık `/p/<pid>/c/new`'e gider.
   Taslak hâli: `drafting = route.chatId === "new"`; `useChat`'e `null` geçilir; `ChatScreen`'e
   `{ id: null, title: "New chat", messages: [] }` verilir; `onSend` sohbeti doğurup adresi
   **replace** ile gerçek kimliğe çevirir.
7. `workspace.css`: `.sidebar__mark` gider.

### 2.3 · Kapanış denetimi

- `grep /api/chats` → yalnız "artık yok" testleri kalmalı.
- `ChatStore.list_all` ve `FileChatStore.list_all` ölü kaldıysa gider.
- `ChatScreen`'e yeni bir prop eklenmedi: taslak, normal bir sohbet nesnesinin şekliyle çiziliyor.

---

## Risk

`new`'in gerçek bir kimlik sanılması. Kural tek yerde (`App.jsx`) duruyor ve testi "sunucuya
`chats/new` sorulmaz" diye yazılıyor.
