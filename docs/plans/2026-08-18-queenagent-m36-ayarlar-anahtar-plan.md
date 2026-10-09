# Madde 36 — Ayarlar ekranı ve xAI anahtarı · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m36-ayarlar-anahtar-design.md](../specs/2026-08-18-queenagent-m36-ayarlar-anahtar-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Madde iki uçlu: **iki tur**, her turda önce yalnız testler (kırmızı), sonra uygulama.

---

## Tur 1 — Arka uç

### Adım 1 — Testler (kırmızı commit)

- yeni `test_settings.py` — ayar dosyası yokken anahtar boş; kaydedilen anahtar geri okunur; boş
  anahtar kaydedilebilir *(silme yolu)*; dosya kökte `settings.json`.
- `test_projects_api.py` — kökteki ayar dosyası projeler listesine **sızmıyor**.
- yeni `test_settings_api.py` — `GET` düz metin anahtarı döndürür; `PATCH` kaydeder ve kaydedilmiş
  hâli döndürür; tanınmayan alan **400**.
- `test_xai_client.py` — anahtar **her istekte** okunur (iki istek, iki ayrı değer); anahtar boşken
  istek **hiç gönderilmez** ve söylenen "No API key is set."

### Adım 2 — Uygulama

yeni `features/settings/{domain,data,presentation}` · `services/xai/client.py` · `config.py`
(`XAI_API_KEY` silinir) · `main.py`.

---

## Tur 2 — Ön uç

### Adım 1 — Testler (kırmızı commit)

- yeni `useSettings.test.jsx` — anahtar okunur, kaydedilir, reddedilen kayıt sunucunun cümlesini
  taşır.
- yeni `SettingsScreen.test.jsx` — başlık, mono etiket, girdi düz metin; Save kaydeder; "Saved."
  çıkar ve girdiye dokununca gider; hata satırı.
- `useRoute.test.js` — `/settings` dördüncü adres.
- `Sidebar.test.jsx` — en altta Settings satırı, basınca `/settings`.
- `ChatScreen.test.jsx` — kartın altındaki Settings satırı **yalnız anahtar yokken**; hata metnine
  bakılmıyor.
- `App.test.jsx` — `/settings` ekranı çiziyor; kaydetmek `PATCH` gönderiyor.
- `workspace.css.test.js` — ayar ekranının ölçüleri uygulamanın kendi öğelerinden.

### Adım 2 — Uygulama

yeni `features/settings/SettingsScreen.jsx` · `useSettings.js` · `shared/useRoute.js` ·
`Sidebar.jsx` · `ChatScreen.jsx` · `App.jsx` · `workspace.css`.

---

## Adım 3 — Belgeler

`CODE-STANDARD.md`: "tek feature var" cümlesi **iki**ye döner, gerekçesiyle; mağaza tablosuna
`settings.json` satırı. `CLAUDE.md`: anahtarın ayarlardan verildiği yazılır.

---

## Kapanış denetimi

- `grep XAI_API_KEY` boş.
- `workspace` hiçbir yerde `settings`'i import etmiyor.
- İstemci anahtarı dize olarak tutmuyor.

## Risk

Canlı anahtarla çalıştığı Madde 35'in 26. adımında görülür.
