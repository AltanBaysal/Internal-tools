# Madde 425 — Agent'ın sohbeti ekranda, uygulama turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 425 · v9-4d · **Tur:** 2/2 — kod.
**Testler:** [m425 test turu](2026-10-06-queen-editor-m425-sohbet-ekrani-testler-design.md) — kurallar
orada; bu belge yalnız nasıl yapıldığını söyler. Sunucuya dokunulmaz, `dist` kurulmaz.

## Yaklaşımlar

1. **Seçilen — veri bir hook'ta, çizim bir bileşende, ikisi yeni `features/agent/`'ta.**
   `useAgentChat(project)` sunucuyla konuşur, yoklamayı yürütür ve ekranın hafızasını tutar;
   `AgentPanel` çizer, kaydırmayı ve odağı tutar. CODE-STANDARD'ın ön yüz biçimi *("components +
   hooks (data access)")*, ve `useGeneration` / `GeneratePanel` ikilisinin yolu. Agent kendi özelliği,
   sunucudaki `features/agent/` gibi; `SidePanel` onu üreticiler panelini aldığı gibi başka bir
   özellikten alır.
2. *Elendi —* tasarımın `sohbet.js`'ini taşımak: sayfanın sahte agent'ı, saatten hesaplanan adımları ve
   `sessionStorage`'ı onun omurgası; uygulamada agent sunucuda, adımlar sunucunun kaydında.
3. *Elendi —* sohbeti `useGeneration`'ın yoklamasına bağlamak: o, galerinin ve işçinin; agent başka
   bir şey, başka bir zamanda çalışır. İkisini tek döngüye koymak iki ayrı kuralı bir yerde düğümler.
4. *Elendi —* sürekli yoklama: panel açıkken her saniye — agent çalışmazken her istek boşa.

## Dosyalar

### `frontend/src/shared/api.js` — altı kapı

`newChat(project)` → `POST …/chats`; `listChats(project)` → `GET …/chats`'ın `chats`'ı;
`openChat(project, chat)` → `GET …/chats/<id>`; `askQuestion(project, chat, text)` → `POST
…/questions`, gövde `{"text"}`; `stopAgent(project, chat)` → `POST …/stop`; `workingChats(project)` →
`GET …/chats/working`'in `working`'i. Hepsi `request()`'ten: hata sunucunun cümlesi, ulaşılamazsa
*"Sunucuya ulaşılamadı — bağlantıyı kontrol et."*.

### `frontend/src/features/agent/useAgentChat.js` — `useAgentChat(project)`

**Hafıza:** modülde bir `Map`, proje başına `{ open, list, drafts }` — açık sohbetin kimliği, liste
açık mı, sohbet başına taslak. Bellekte: yenileme unutur (spec'in seçimi).

**Durum:** `chat` (açık sohbet, sunucunun son söylediği; bilinmiyorsa `null`), `working` (kimlikler),
`list`, `rows`, `draft`, `pending` (yoldaki sorunun metni), `failure` (`{ text, question?, poll? }`).
`busy` = açık sohbet çalışıyor ya da sorusu yolda.

**Açmak:**
- `take(chat)` — sunucunun verdiği sohbet açık olur: hafızaya yazılır, liste kapanır, taslağı gelir,
  kart gider.
- `show(id)` — önce `workingChats`, sonra `openChat`, sonra `take` *(spec, kural 27)*.
- `first()` — `listChats`; satır varsa `show(ilki)`, yoksa `take(await newChat())`.
- `reopen()` — hafızada açık sohbet varsa `show(o)`, yoksa `first()`.
- Bağlanınca: hafızada liste açıksa `openList()`, değilse `reopen()`.

**Basışlar:**
- `write(text)` — taslak, hem durumda hem hafızada.
- `send()` — kırpılmış metin boşsa hiçbir şey; değilse taslak boşalır, `pending` olur, kart gider;
  `askQuestion`: cevap gelince sohbet o, kimlik çalışanlara eklenir; hata gelince
  `failure = { text, question }`; her iki yolda `pending` biter.
- `stop()` — soru yoldaysa hiçbir şey; değilse `stopAgent`: sohbet o, kimlik çalışanlardan çıkar,
  kart gider.
- `startNew()` — `take(await newChat())`.
- `openList()` — `list` açık, `rows` yeniden okunur; `toggleList()` — açıksa `reopen()`, değilse
  `openList()`.

**Yoklama:** `working` boş değilken bir `useEffect` `POLL_MS` sonrasına bir tur kurar; bağımlılıkları
`project`, `working`, `list` ve açık sohbetin kimliği. Tur: `workingChats`; konuşma görünüyorsa ve
açık sohbet ya etkinin gördüğü `working`'de ya da yenisinde ise `openChat`; sonra `setChat`,
`setWorking(yeni)` — yeni dizi etkiyi yeniden kurar, yani döngü kendiliğinden sürer, boş dizi onu
bitirir. Turun kartı (`poll: true`) iyi bir turda gider. Ulaşamayan tur kartı koyar ve `working`'i aynı
içerikle yeni bir dizi yapar: bir ıska döngüyü bitirmez *(useGeneration — "One bad poll must not kill
the chain")*. Temizlikte zamanlayıcı silinir ve havadaki turun cevabı düşer: sohbet değişmişse eski
sohbet geri gelmez.

### `frontend/src/features/agent/AgentPanel.jsx` — `AgentPanel({ project, heading })`

- **Başlık satırı** `qe-chat-head`: `heading`, sonra `qe-chat-tools`'ta *Yeni sohbet* ve *Sohbetler*
  (`is-on`, `aria-pressed`).
- **Gövde** `qe-chat`: liste açıksa liste; değilse sohbet biliniyorsa konuşma ve kutu; ikisi de değilse
  ve hata varsa kart.
- **Konuşma** `qe-chat-log`: sorular — `pending` varsa sona bir soru gibi eklenir —, her biri kardeş
  öğeler olarak balon, adım bloğu, sonuç. Son soru sonucusuzsa ve `busy` ise canlı: bitmemiş son adımı
  `is-live`, yoksa *"Çalışıyor…"* satırı. Sonra `failure.question` balonu ve kart. Hiçbiri yoksa
  *"Projeyle ilgili bir şey sor."*.
- **Kutu:** `textarea` (`aria-label="Soru"`), düğme `qe-chat-go` — `busy` iken `wf-btn--primary` ve ■,
  değilse `wf-btn--hl` ve ↑; ↑ kırpılmış taslak boşsa kapalı. Simgeler tasarımın SVG'leri. Enter
  (Shift'siz) varsayılanı engeller ve `busy` değilse gönderir; düğme `busy` ise durdurur, değilse
  gönderir; ikisinde de odak kutuya döner.
- **Liste** `qe-chat-list`: satırlar, açık sohbetinki `is-on`, tarih `formatModified`'la; çalışan
  sohbette `role="img"` nokta; boşsa *"Henüz sohbet yok."*; altında kart.
- **Kaydırma:** bir `follow` ref'i — konuşma en alttaydı mı —, kaydırma olayında ölçülür (≤ 4 px).
  Sohbet ya da görünüm değişince ve soru gönderilince `true`. Her çizimden sonra (`useLayoutEffect`):
  son öğe konuşmadan uzun bir cevapsa konuşma onun adım bloğunun başına, değilse `follow` ise en alta.
  `qe-chat-log` `position: relative`, yani `offsetTop` konuşmanın başından.
- **Odak:** *Yeni sohbet* bir bayrak koyar; sohbet çizilince kutu odağı alır.

### `frontend/src/features/photo_generation/SidePanel.jsx`

Başlığı bir değişkende kurar; agent panelinde onu `AgentPanel`'e verir, öteki panellerde kendi çizer.
`AgentPanel` `../agent/AgentPanel.jsx`'ten; `photo_generation/AgentPanel.jsx` silinir. Bileşenin
yorumu artık *"the agent that has not been designed yet"* diyemez.

### `frontend/src/shared/app.css`

Tasarımın `kit.css`'indeki sohbet bloğu (`qe-chat` … `qe-chat-row-date`), olduğu gibi; `qe-dot` ve
`qe-thin-scroll` zaten burada. `vendor/` tasarım projesinin dosyaları için; `qe-` sınıfları bu dosyada
yaşıyor.

## Bir sonuç, açıkça

- **Yoklama yalnız bu sekmenin bildiği agent'ı izler.** Başka bir sekmede başlatılan agent, bu sekmede
  bir sohbet açılınca ya da bir tur dönünce görülür.
- **Sohbet okumak her yoklamada `chats.jsonl`'ı Drive'dan okur** — sunucuda önbellek yok (417). Saniyede
  bir okuma, yalnız açık sohbet çalışırken.
- **Yenilemede açık sohbet ve taslak unutulur** — spec'in seçimi; tasarım ikisini `sessionStorage`'da
  tutuyordu.

## Bilinçli olarak yapılmayan

- Sunucu, `dist`, yol haritası.
- `key={project}`: proje ekranı başka bir projeye hep `/`'dan geçerek açılır, yani panel yeniden
  bağlanır (`App.jsx`).
- Yükleniyor halkası: sohbet gelene kadar başlık satırı tek başına durur; tasarımda bu hâl yok.
- Yoldaki soruyu durdurmak, Esc, yeniden dene, silme, markdown.
