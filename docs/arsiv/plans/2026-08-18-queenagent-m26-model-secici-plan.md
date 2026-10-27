# Madde 26 — Model seçici · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m26-model-secici-design.md](../specs/2026-08-18-queenagent-m26-model-secici-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Madde iki uçlu, o yüzden **iki tur**: önce arka uç (kırmızı → yeşil), sonra ön uç (kırmızı → yeşil).
Her turda önce yalnız testler commit edilir.

---

## Tur 1 — Arka uç

### Adım 1 — Testler (kırmızı commit)

- `test_start_chat.py` — sohbet verilen modelle doğar; model verilmezse boş kalır.
- `test_file_chat_store.py` — model diske yazılır ve geri okunur; **alanı olmayan eski kayıt** okunur
  ve modeli boş gelir.
- yeni `test_set_chat_model.py` — modeli değiştirir; olmayan sohbet `ChatNotFound`.
- `test_stream_answer.py` — motora sohbetin modeli verilir; sohbet boşsa `None` geçer.
- `test_xai_engine.py` / `test_xai_client.py` — model çağrı başına taşınır; verilmezse ayardaki
  kullanılır.
- `test_chats_api.py` — `POST /chats` modeli alır; `PATCH …/chats/<cid>` modeli değiştirir ve 404
  verir; sohbet JSON'u modeli **çözülmüş** döndürür.
- yeni `test_model_api.py` — `GET /api/model` varsayılanı söyler.

### Adım 2 — Uygulama

`chat.py` · `ports.py` · `set_chat_model.py` · `start_chat.py` · `stream_answer.py` ·
`file_chat_store.py` · `xai_engine.py` · `client.py` · `routes.py` · `web/app.py` · `config.py`
yorumu.

---

## Tur 2 — Ön uç

### Adım 1 — Testler (kırmızı commit)

- yeni `models.test.js` — yedi satır, kimlikler benzersiz, her satırda ad ve fiyat.
- `Menu.test.jsx` — başlık çizilir; satır açıklaması çizilir; seçili satır `✓` taşır.
- `Composer.test.jsx` — `foot` yuvası Send'in **solunda** çizilir; verilmezse ayak yalnız Send'dir.
- yeni `ModelPicker.test.jsx` — kapalıyken modelin adı; basınca menü; seçmek `onChange` çağırır;
  seçili olana basmak da onu seçer *(model temizlenemez, Skills'ten farkı budur)*.
- `ChatScreen.test.jsx` — seçici sohbet composer'ında var; proje ve Home'da yok.
- `App.test.jsx` — seçim `PATCH` gönderir; sohbet değişince o sohbetin modeli görünür; yeni sohbet
  son seçimle doğar.

### Adım 2 — Uygulama

`models.js` · `ModelPicker.jsx` · `Menu.jsx` · `Composer.jsx` · `ChatScreen.jsx` · `App.jsx` ·
`shared/api.js` · `workspace.css`.

---

## Kapanış denetimi

- `grep XAI_MODEL` — yorumu "yeni sohbetin varsayılanı" diyor.
- Menüdeki yedi kimlik ile spec'teki tablo birebir aynı.
- Sidebar'ın menüsü başlıksız ve işaretsiz çizilmeye devam ediyor.

## Risk

Kimlikler ve fiyatlar 18 Ağustos 2026'nın okuması. Yanlış kimlik xAI'nin kendi sözleriyle patlar.
