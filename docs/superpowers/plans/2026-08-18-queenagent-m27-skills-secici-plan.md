# Madde 27 — Skills seçici arayüzü · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m27-skills-secici-design.md](../specs/2026-08-18-queenagent-m27-skills-secici-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Madde iki uçlu: **iki tur**, her turda önce yalnız testler (kırmızı gider), sonra uygulama.

---

## Tur 1 — Arka uç

### Adım 1 — Testler (kırmızı commit)

- `test_start_chat.py` — sohbet verilen beceriyle doğar; ilk mesaj da o beceriyi taşır.
- `test_append_message.py` — mesaj hangi beceriyle gönderildiğini kendinde taşır; verilmezse boş.
- `test_file_chat_store.py` — `Chat.skill` ve `Message.skill` diske yazılır ve geri okunur; boşsa
  **yazılmaz**; alanı olmayan eski kayıt okunur.
- `test_set_chat_model.py` → `test_set_chat_choices.py` — tek use case iki alanı da değiştirir;
  yalnız verilen alan değişir, öteki yerinde kalır; olmayan sohbet `ChatNotFound`.
- `test_chats_api.py` — `POST /chats` beceriyi alır; `PATCH` `model` **ya da** `skill` kabul eder,
  ikisi de yoksa 400; sohbet JSON'u beceriyi döndürür; mesajlar kendi becerilerini taşır.
- **Beceri cevabı değiştirmez:** beceri seçili bir sohbette motora giden konuşma değişmez
  *(bu maddenin sınırının kanıtı)*.

### Adım 2 — Uygulama

`chat.py` · `file_chat_store.py` · `set_chat_choices.py` (eski `set_chat_model.py`) ·
`start_chat.py` · `append_message.py` · `routes.py`.

---

## Tur 2 — Ön uç

### Adım 1 — Testler (kırmızı commit)

- yeni `skills.test.js` — altı satır, kimlikler benzersiz, her satırda ad ve açıklama.
- yeni `SkillPicker.test.jsx` — seçim yokken "Skills"; seçiliyken becerinin adı ve sıcak sınıf;
  menüde altı satır + açıklamalar; seçmek `onChange`; **seçiliye basmak temizler** (`""` gönderir).
- `ModelPicker.test.jsx` — açık/kapalı durumu **dışarıdan** gelir; kendi durumunu tutmaz.
- `ChatScreen.test.jsx` — ayakta sırayla Skills · model · Send; proje ve Home'da ikisi de yok.
- `App.test.jsx` — seçim `PATCH` gönderir; sohbet değişince o sohbetin becerisi görünür; yeni sohbet
  son beceriyle doğar; bir menü ötekini kapatır; **Esc sırası** ⋯ → onay → Skills → model → panel.
- `workspace.css.test.js` — `.picker--on` sıcak zemin taşır ve **vurgu rengi değildir**.

### Adım 2 — Uygulama

`skills.js` · `SkillPicker.jsx` · `ModelPicker.jsx` · `ChatScreen.jsx` · `App.jsx` · `useChat.js` ·
`useChatLists.js` · `workspace.css`.

---

## Kapanış denetimi

- `grep set_chat_model` boş.
- Esc zinciri tek yerde mi (App'in tek dinleyicisi); seçicilerde `keydown` yok.
- Bu maddede hiçbir yerde beceri **okunmuyor** — yalnız saklanıyor (`grep skill` motora uzanmıyor).

## Risk

Sıcak tonun sayısı tasarımdan gelmiyor; gözle doğrulama Madde 35.
