# Madde 86 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-26-queenagent-m86-skill-oturumun-kipi-uygulama-design.md](../specs/2026-08-26-queenagent-m86-skill-oturumun-kipi-uygulama-design.md)
**Bu turda test yazılmaz.** Commit'lenmiş dokuz kırmızı *(`04674a8`)* yeşile döner.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`
**Ve derleme:** `npm run build --prefix queen-agent/frontend` — aynı commit'e girer.

Sıra aşağıdan yukarı: alan gider, sonra onu yazan, sonra onu sunan, sonra onu okuyan. Böylece her
adımda geriye kalan çağrı sayısı azalıyor.

---

## 1. `backend/features/workspace/domain/chat.py`

`Chat`'in `skill` alanı ve onu anlatan yorum gider — 78-81. satırlar:

```python
    # The skill selected right now. Empty is the ordinary state: a chat may have no skill at all,
    # and pressing the selected one again puts it back here. The only thing about a chat that is
    # chosen -- which model answers is one line in config.py since Madde 82.
    skill: str = ""
```

`Message.skill` ve onun yorumu **dokunulmadan kalır**.

## 2. `backend/features/workspace/domain/usecases/set_chat_skill.py`

Dosya silinir: `git rm`.

## 3. `backend/features/workspace/domain/usecases/start_chat.py`

`Chat(...)` çağrısındaki `skill=skill` satırı gider. Parametre ve mesaja yazılışı kalır:

```python
def start_chat(chat_store, project_store, project_id, text, new_id, now, skill=""):
    if project_store.get(project_id) is None:
        raise ProjectNotFound(project_id)
    trimmed = text.strip()
    if not trimmed:
        raise EmptyMessage()
    # The skill lands on the message rather than on the chat: what governed a turn is settled when
    # the turn is sent, and a selection made later must not rewrite an older one.
    chat = Chat(
        id=new_id,
        title=chat_title(trimmed),
        created_at=now,
        messages=(Message(role="user", at=now, text=trimmed, skill=skill),),
    )
    chat_store.add(project_id, chat)
    return chat
```

## 4. `backend/features/workspace/data/file_chat_store.py`

**Yazarken** — 52-56. satırlar gider:

```python
        # A chat that selected no skill writes no field, exactly as a message with no files does.
        # Chats written before Madde 82 carry a model key here; nothing puts one back, so it drops
        # the first time such a chat is written again.
        if chat.skill:
            stored["skill"] = chat.skill
```

Yerine, `stored` sözlüğünün hemen altında tek bir yorum:

```python
        # A chat carries no skill of its own since Madde 86; the key that older records still have
        # here is not written back, so it drops the first time such a chat is written again. The
        # same is true of the model key Madde 82 left behind.
```

**Okurken** — 114-116. satırlar gider:

```python
        # Chats written before this field existed selected nothing, which is what empty means. A
        # model key sitting beside it is simply not read.
        skill=raw.get("skill", ""),
```

Mesajın `skill=message.get("skill", "")` satırı **kalır**.

## 5. `backend/features/workspace/presentation/routes.py`

**Import** — 28. satır gider:

```python
from backend.features.workspace.domain.usecases.set_chat_skill import set_chat_skill
```

**Uç** — 86-98. satırlar bütünüyle gider (`patch_chat`). `ChatNotFound` importunun başka
kullanıcısı var mı diye bakılır; yoksa o da gider.

**Tel** — `_chat_summary`'deki iki satır gider:

```python
        # No default stands in for an absent skill: having none is an ordinary state.
        "skill": chat.skill,
```

Alan `_chat_summary`'de durduğu için hem listeden hem tek sohbetten aynı anda düşüyor.
`_chat_json`'daki mesaj alanı (`"skill": message.skill`) **kalır**.

## 6. `frontend/src/features/workspace/useChat.js`

`choose` gider — 154-161. satırlar — ve döndürülen nesneden `choose` satırı da. İlk satırdaki
import `patchJson`'ı bırakır:

```js
import { getJson, postJson } from "../../shared/api.js";
```

Bu kancada `patchJson`'ın başka kullanıcısı yok *(bakıldı)*.

## 7. `frontend/src/features/workspace/ChatScreen.jsx`

Prop listesine `skill` eklenir, `skillsOpen`'ın hemen üstüne:

```js
  skill,
  skillsOpen,
  onToggleSkills,
```

`SkillPicker`'ın kaynağı değişir ve üstündeki yorum düzeltilir:

```jsx
            /* karar 1's order: Skills · model · Send. The middle one stopped being a control in
               Madde 82 -- one model, nothing to pick. The skill is handed in rather than read off
               the chat: since Madde 86 the selection is the session's, and the session is App's.
               Whether the menu is open is App's too, because Escape closes it in a fixed order
               with the rest. */
```

```jsx
                <SkillPicker
                  skill={skill}
                  open={skillsOpen}
                  onToggle={onToggleSkills}
                  onChange={onSkillChange}
                />
```

## 8. `frontend/src/App.jsx`

**`chooseSkill` gider** — 216-225. satırlar, yorumuyla birlikte.

**`ChatScreen`'e verilenler.** Üç satır değişiyor:

```jsx
            chat={drafting ? DRAFT : chat.chat}
```

```jsx
            /* The selection is the session's since Madde 86: one value, and both screens are
               handed it. What governed a turn is settled when the message is sent. */
            skill={lastSkill}
            skillsOpen={skillsOpen}
            onToggleSkills={toggleSkills}
            onSend={drafting ? startChat : (text) => chat.send(text, lastSkill)}
            onSkillChange={setLastSkill}
```

`ProjectScreen`'in satırları **değişmiyor** — zaten bu şekildeydi.

## Beklenen yeşil

| Nerede | Ne yeşile döner |
|---|---|
| `test_chat.py` | `Chat`'te `skill` alanı yok |
| `test_chats_api.py` | Sohbetin JSON'u `skill` taşımıyor · sohbete PATCH 405 |
| `test_file_chat_store.py` | Diskte `skill` taşıyan eski kayıt okunuyor, alan doğmuyor |
| `ChatScreen.test.jsx` | Seçici verilen skill'i çiziyor |
| `App.test.jsx` | Seçmek istek atmıyor · kayıttaki skill seçiciye girmiyor · seçicide yazan ile gidende yazan aynı · seçim taslaktan sohbete geçiyor |

**İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi, defterdeki `BRANCH` bir
özellik dalını gösterdiği için. Çalışma ağacındaki ayrı bir değişiklik; bu turda dokunulmuyor.

## Derleme

`npm run build --prefix queen-agent/frontend` koşulur ve `dist` **aynı commit'e girer**. Ön yüz
değişiyor, ve defter derlemiyor — derlenmemiş bir ön yüz değişikliği bitmiş sayılmıyor.

## Bilerek yapılmayanlar

- **Test yazılmaz.** Hiçbir test dosyası açılmıyor.
- **`ProjectScreen.jsx` açılmaz.** Skill'i zaten prop olarak alıyor.
- **`SkillPicker`, `Menu`, `skills.js`, `skills.py` açılmaz.** Seçici kalıyor.
- **`stream_answer.py` açılmaz.** Yönergeyi mesajdan alıyordu, almaya devam ediyor.
- **`post_chat` ve `post_message`'ın `skill` alanına dokunulmaz.** İki kapıyı birleştirmek 87'nin
  işi.
- **`ports.py`'deki `Engine.model` parametresine dokunulmaz.** 82'den kalan ayrı bir tutarsızlık ve
  kendi turunu istiyor.
