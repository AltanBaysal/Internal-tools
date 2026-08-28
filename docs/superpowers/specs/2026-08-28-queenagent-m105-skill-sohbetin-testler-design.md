# Madde 105 — Skill seçimi sohbetin olur · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 105.
**Belirti** *(kullanıcı, 28 Ağustos)*: bir sohbette seçilen skill o sohbete özel kalmıyor.

## Bugün ve karar

Seçim oturumun tek değeri *(Madde 86'nın `lastSkill`'i)* ve tarayıcı onu tek anahtarla hatırlıyor
*(Madde 100, `queenagent.skill`)*. Madde 105 sınırı değiştiriyor: **seçim seçildiği sohbetin.**

- **Gerçek sohbet:** seçici o sohbetin kendi seçimini gösterir ve gönderilen mesaj onu taşır;
  seçim tarayıcıda **sohbet başına** hatırlanır — tek JSON anahtarı `queenagent.chat-skills`,
  içinde `{sohbetId: skill}`. Madde 86'nın ilkesi sohbet içinde aynen sürer: ekranın gösterdiği ile
  isteğin taşıdığı tek değer.
- **Taslak ve proje ekranı:** ikisinin seçicisi **doğacak sohbetin** değerini tutar *(oturumluk tek
  state)*. Doğumda değer yeni doğanın haritadaki girdisine yazılır ve taslak değeri temizlenir —
  bir sonraki taslak boş başlar. Seçilip doğum olmadan bırakılan değer oturumda durur; temizleyen
  an doğumdur.
- **Değişmeyen:** kayıttaki `skill` alanı seçiciye dönmez *(mevcut test yeşil kalır)* — o geçmiş
  turların kaydı, seçim değil. Eski `queenagent.skill` anahtarı öksüz kalır; okunmaz, zararsız.
- **Madde 100'ün güvencesi yeni sınırda:** sayfa yenilenince sohbetin kendi seçimi yerinde
  *(harita localStorage'da)*. Taslağın henüz doğmamış seçimi yenilemede kaybolur — düşük bahis,
  bilerek kabul.

## Testler

### `useRemembered.test.jsx` — 3 yeni *(hook'un API'sini mıhlar)*

`useRememberedMap(name)` → `[harita, hatırla(anahtar, değer)]`: anahtarlar birbirine karışmaz ·
bir anahtarın tuttuğu ikinci mount'ta geri gelir · bozuk JSON boş haritadır, çökme değil.
*(Hook henüz yok — üçü de kırmızı; dosyanın var olan beşi yeşil kalır.)*

### `App.test.jsx` — 1 ölçüsü değişen + 2 yeni

- **Ölçüsü değişen:** `a new chat is born with the last skill picked in this session` → adı ve
  iddiası tersine döner: `a skill picked in a chat does not ride into a chat born on the project
  screen` — proje ekranından doğan mesajın `skill`'i `""`. *(Bugün taşıyor — kırmızı.)*
- `a skill picked in one chat stays that chat's own`: iki sohbet; birincide seçilen ikincide
  görünmez, dönünce yerinde. *(Bugün ikincide de görünüyor — kırmızı.)*
- `a second draft does not wear the first one's skill`: taslakta seçilip doğum yaşandıktan sonra
  açılan yeni taslak boş. *(Bugün öncekini giyiyor — kırmızı.)*

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `useRemembered.test.jsx` | 3 yeni |
| `App.test.jsx` | 2 yeni + 1 ölçüsü değişen |

Defter çifti bu maddenin değil.

## Bilerek yapılmayanlar

- **Kod yazılmaz** — `remembered.js` ve `App.jsx` bu turda açılmaz.
- **Sunucuya hiçbir şey eklenmez** — mesajın kendi `skill` alanı kaydı zaten taşıyor.
- **`dist` derlenmez.**
