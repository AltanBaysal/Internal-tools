# Madde 105 — Skill seçimi sohbetin olur · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m105-skill-sohbetin-testler-design.md) —
altı kırmızı `77fe91f`'te. Sınırın kendisi orada; bu belge yalnız kodun nereye oturduğunu söylüyor.

## `remembered.js` — `useRememberedMap(name)`

`useRemembered`'ın üstüne kurulur: tek tarayıcı anahtarı, içinde JSON harita. Okuma hoşgörülü —
parse edilemeyen ya da harita olmayan değer boş haritadır; yazma fonksiyonel güncellemeyle gider,
iki hızlı seçim birbirini ezmez. Dönen çift `[harita, hatırla(anahtar, değer)]`.

## `App.jsx` — tek değer ikiye ayrılır

- `lastSkill` *(oturumun tek değeri, Madde 86 + 100)* gider. Yerine:
  - `chatSkills` — `useRememberedMap("chat-skills")`: sohbet başına seçim, tarayıcıda.
  - `draftSkill` — düz state: **doğacak sohbetin** değeri; taslağın ve proje ekranının seçicisi
    bunu tutar.
- Yürürlükteki seçim: taslakta `draftSkill`, gerçek sohbette `chatSkills[route.chatId] ?? ""` —
  ekranın gösterdiği ile mesajın taşıdığı hâlâ tek değer *(Madde 86'nın ilkesi, sohbet sınırında)*.
- Seçim değişimi: taslakta `setDraftSkill`, sohbette `rememberChatSkill(route.chatId, değer)`.
  Proje ekranı doğrudan `setDraftSkill` kullanır — orada `route.chatId` yok.
- **Doğum** *(Madde 88'in `born` çengeli)*: `draftSkill` doluysa yeni doğanın girdisine yazılır,
  sonra bırakılır — bir sonraki taslak boş başlar.
- Madde 86/100'ü anlatan yorumlar yeni sınıra göre düzeltilir.

## Bilerek böyle

- **Kayıttaki `skill` alanı seçiciye dönmüyor** — o geçmişin kaydı; harita tek kaynak kalır.
- **Silinen sohbetin girdisi haritada kalır** — okunmayan öksüz girdi zararsız, temizliği ayrı bir
  iş olurdu.
- **Eski `queenagent.skill` anahtarı okunmaz** — öksüz, zararsız.

## Görülür hâli

Altı kırmızı yeşerir; suite'lerde başka kırmızı kalmaz *(defter çifti hariç)*. `dist` aynı
commit'te derlenir.
