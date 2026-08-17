# Madde 3 — Home kalkar, açılış ilk projeye iner · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m3-home-design.md](../specs/2026-08-17-queenagent-m3-home-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra implementasyon.

---

## Adım 1 — Testler (kırmızı commit)

### 1.1 · Arka uç

**`backend/tests/test_chats_api.py`**

| Test | Ne olur |
|---|---|
| `test_a_message_from_home_opens_a_project_and_a_chat` | **Silinir**, yerine `test_starting_a_chat_from_nowhere_is_gone`: `POST /api/chats` → **405** |
| `test_an_empty_message_from_home_leaves_no_project_behind` | **Silinir** — böyle bir yol kalmıyor |
| `test_a_message_is_appended_to_an_existing_chat` | `_project(client)` + `POST /api/projects/<pid>/chats` ile kurulur |
| `test_appending_nothing_is_400` | aynı şekilde kurulur |
| `test_recent_chats_span_every_project_and_name_theirs` | iki proje kurulur, her birinde bir sohbet |
| `test_the_answer_arrives_as_a_stream_of_events` | aynı şekilde kurulur |
| `test_a_broken_engine_speaks_inside_the_stream` | aynı şekilde kurulur |

Yeni "artık yok" testi (aynı dosya):

```python
def test_the_home_use_case_is_gone():
    # Home'dan mesat atılmıyor, o yüzden projeyi ve sohbeti birlikte açan kural da yok.
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.start_chat_in_new_project  # noqa: F401
```

**`test_append_message.py`, `test_delete.py`, `test_rename.py`, `test_stream_answer.py`** —
`start_chat_in_new_project(...)` çağrıları `create_project(...)` + (gerekiyorsa `edit_project(...)`
ile ad) + `start_chat(...)` ile kurulur. Bu dosyalarda **davranış iddiası değişmez**; yalnız iskele
değişir. Proje adına bakan bir iddia varsa adı `edit_project` ile aynen kurulur.

### 1.2 · Ön yüz

**`features/workspace/HomeScreen.test.jsx` silinir.** Yerine
**`features/workspace/NoProjectsScreen.test.jsx`**:

1. başlık `No projects yet` çizilir
2. tasarımın cümlesi aynen çizilir
3. `+ New project` basılınca `onNewProject` çağrılır
4. composer yok — `queryByPlaceholderText(/Ask anything/)` null
5. kart ızgarası yok — `queryByTestId("skeleton")` null
6. hata varken sunucunun cümlesi çizilir, `No projects yet` **çizilmez** ve düğme yoktur

**`features/workspace/ProjectCard.test.jsx` silinir** (varsa).

**`shared/useRoute.test.js`** — yeni test: `navigate(to, { replace: true })` adresi değiştirir ama
geçmişe yazmaz (`history.replaceState` çağrılır, `pushState` çağrılmaz). `parsePath("/")`'in `home`
dönmesi **aynen kalır**: adres hâlâ `/` olabilir, çatal onu bir ekrana değil bir karara çevirir.

**`App.test.jsx`**

| Test | Ne olur |
|---|---|
| `loaded projects reach both the sidebar and the cards` | **yeniden yazılır** → `the app opens on the first project`: adres `/p/p1` olur, ad kenar çubuğunda ve başlıkta görünür |
| `a message from home opens a project and a chat and goes there` | **silinir** |
| `offline, the strip shows and the composer stays open` | **yeniden yazılır**: `/p/p1` adresinden başlar (boş hâl ekranında composer yok, olmamalı da) |
| *(yeni)* `with no projects the empty screen stands instead of home` | sıfır proje → `No projects yet` görünür, adres `/` kalır |
| *(yeni)* `the fork is not written into history` | bir proje varken çatal `replaceState` kullanır, `pushState` kullanmaz |
| *(yeni)* `nothing is drawn while the list is on its way` | `fetch` askıda → ne `No projects yet` ne proje ekranı |
| *(yeni)* `a list that fails to load says so instead of saying there are none` | `GET /api/projects` 500 → sunucunun cümlesi, `No projects yet` yok |

**Ölçülen kırmızı:**

| Nerede | Kırmızı | Not |
|---|---|---|
| `test_chats_api.py` | 2 | `POST /api/chats` 405 yerine 201; use case hâlâ import ediliyor |
| Arka uç, geri kalan | 0 | yeniden kurulan dört dosya **aynen yeşil** kaldı — iddialar değişmedi, iskele değişti |
| `useRoute.test.js` | 1 | `replace` seçeneği henüz yok |
| `App.test.jsx` | 6 | çatal, boş hâl, `replaceState`, yüklenirken boşluk, hata hâli, `POST /api/chats` |
| `NoProjectsScreen.test.jsx` | 6 | bileşen yok, dosya hiç yüklenemiyor |

İlk yazımda iki App testi **bugünkü kodla da geçiyordu** ("yüklenirken hiçbir şey", "hata hâli"):
ikisi de yalnız `No projects yet`in yokluğuna bakıyordu, o da bugün zaten yok. Ayırt edici iddialar
eklendi — iskelet ızgarası ve Home composer'ı — ve ikisi de kırmızıya döndü.

---

## Adım 2 — Implementasyon

### 2.1 · Arka uç

1. `presentation/routes.py`: `post_chat_anywhere` ve `start_chat_in_new_project` importu gider.
2. `domain/usecases/start_chat_in_new_project.py` **silinir**.

### 2.2 · Ön yüz

3. `shared/useRoute.js`: `navigate(next, options)` — `options.replace` ise `replaceState`, değilse
   `pushState`. Yorum sebebi söyler: `/` bir yer değil bir çataldır.
4. `features/workspace/NoProjectsScreen.jsx` **yeni** — katman: `features/workspace/`.
   ```
   No projects yet                                   (serif 34px)
   Chats live inside a project, and the files they
   create stay there. Create a project to start.
   [+ New project]                                   (dolu vurgu)
   ```
   `error` verildiğinde başlık ve düğme yerine sunucunun cümlesi durur.
5. `features/workspace/HomeScreen.jsx` ve `ProjectCard.jsx` **silinir**.
6. `App.jsx`:
   - `sendFromHome`, `goHome`, `startChatInNewProject` importu gider.
   - Çatal: `route.view === "home"` iken — liste yüklenirken hiçbir şey, proje varsa
     `navigate("/p/" + projects[0].id, { replace: true })` (effect içinde), yoksa
     `<NoProjectsScreen />`.
   - `Sidebar`'ın `onNewChat`'i şimdilik proje kurar mı? **Hayır** — "New chat" kuralı Madde 6'nın
     işi. Bu maddede yalnız **hiç proje yokken gizlenir**.
7. `useChatLists.js`: `startChatInNewProject` gider.
8. `workspace.css`: `.home*` ve `.card*` kuralları gider, `.skeleton--card` gider; `.empty*` gelir.

### 2.3 · Kapanış denetimi

- Bağımlılık yönü: yeni bağ yok, use case→use case bağı `start_chat_in_new_project` ile birlikte
  gitti. `feature ↛ feature`, `service ↛ feature`, `service ↛ service` zorlanmıyor.
- Ölü kod: `ProjectCard`, `HomeScreen`, `.home*`, `.card*`, `.skeleton--card`, `startChatInNewProject`
  (ön yüz + arka uç) — hepsi aynı maddede gidiyor.
- `queenagent/README.md` ve `CLAUDE.md` Home'dan söz ediyor mu — ediyorsa düzeltilir.
- Yol haritasının Madde 3 metni bu kararla güncellenir; 15, 16, 17, 19 ve Madde 33'ün Home ayağı
  konusuz diye işaretlenir.

---

## Risk

Arka uçtaki dört test dosyası `start_chat_in_new_project`'i kurulum kolaylığı olarak kullanıyor.
Yeniden kurarken **iddiaları değiştirmemek** esas: bu maddede kullanıcının göreceği tek arka uç
değişikliği `POST /api/chats`'in kalkmasıdır. Bir testin iddiası değişmek zorunda kalıyorsa, orada
kurulum yanlış kurulmuş demektir.
