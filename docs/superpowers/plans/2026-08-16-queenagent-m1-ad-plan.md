# Madde 1 — Mira → QueenAgent · Uygulama Planı

**Tasarım belgesi:** [2026-08-16-queenagent-m1-ad-design.md](../specs/2026-08-16-queenagent-m1-ad-design.md)
**Yol haritası:** [QueenAgent v2](2026-08-15-queenagent-v2-roadmap.md), Faz 0 · Madde 1

**İki commit.** Önce yalnız testler (kırmızı gider), sonra implementasyon. Klasör taşıma ikinci
commit'e aittir — testler hâlâ `mira/` altındayken kırmızıya döner, taşıma ve düzeltme birlikte
yeşile çevirir.

---

## Commit 1 — Testler (kırmızı)

Yalnız test dosyalarına dokunulur. Kaynak kodun tek satırı değişmez; bu yüzden testler **başarısız
olarak** commit edilir.

- [ ] **Adım 1: `ChatScreen.test.jsx`**

İki yerde beklenen metin yeni ada çekilir:

- `test("an answer is labelled Mira", …)` → test adı ve `getByText("Mira · 11:05")` beklentisi
  `QueenAgent · 11:05` olur.
- `test("text that is still arriving is drawn as Mira's turn", …)` → test adı `QueenAgent's turn`.

- [ ] **Adım 2: `ProjectScreen.test.jsx`**

`getByText("Files Mira created")` → `Files QueenAgent created`.

- [ ] **Adım 3: `test_store.py`**

Geçici klasör adı `mira-root` → `queenagent-root`. Bu bir davranış beklentisi değil, adlandırma
tutarlılığı; testin anlamı değişmez.

- [ ] **Adım 4: Kırmızıyı doğrula**

```
npm test --prefix mira/frontend
python -m pytest mira
```

Beklenen: **frontend'de iki test kırmızı** (kaynak hâlâ `Mira` yazıyor) —
`ChatScreen.test.jsx`'te etiket beklentisi, `ProjectScreen.test.jsx`'te sütun başlığı. Üçüncü
düzenleme (`QueenAgent's turn`) yalnız test **adı**dır, beklenti değiştirmez ve kırmızıya dönmez.
`pytest` yeşil kalır — `test_store.py`'deki değişiklik yalnız geçici klasör adı.

Ölçülen: frontend 2 kırmızı / 138 yeşil, `pytest` 190 yeşil.

- [ ] **Adım 5: Commit**

```
git add mira/frontend/src/features/workspace/ChatScreen.test.jsx
git add mira/frontend/src/features/workspace/ProjectScreen.test.jsx
git add mira/backend/tests/test_store.py
git commit -m 'test(mira): expect the QueenAgent name in the UI'
```

Mesajda çift tırnak yok.

---

## Commit 2 — İmplementasyon (yeşil)

- [ ] **Adım 1: Klasörü taşı**

```
git mv mira queenagent
```

`git mv` kullanılır ki dosya geçmişi korunsun. Bu adımdan sonra bütün yollar `queenagent/`.

- [ ] **Adım 2: `config.py`**

- `MIRA_ROOT` → `QUEENAGENT_ROOT`
- varsayılan `~/Mira` → `~/QueenAgent`

Başka değer değişmez: `HOST`, `PORT = 8100`, `XAI_API_KEY`, `XAI_MODEL`, `XAI_BASE_URL` aynı.
Yorum satırındaki gerekçeler de aynı kalır — yalnız kökün adı geçen cümle güncellenir.

- [ ] **Adım 3: Arayüz metinleri**

Sekiz dosyada, spec'in 2.3 tablosundaki tam liste:

| Dosya | Değişecek |
|---|---|
| `Sidebar.jsx` | kelime markası |
| `ChatScreen.jsx` | üç yerde mesaj etiketi |
| `FileRail.jsx` | boş hâl cümlesi |
| `HomeScreen.jsx` | composer yer tutucusu |
| `OfflineStrip.jsx` | çevrimdışı cümlesi |
| `ProjectScreen.jsx` | sütun başlığı + boş hâl cümlesi |
| `index.html` | `<title>` |
| `workspace.css` | yorum satırı |

**Yalnız ad değişir.** `"You"` etiketi, etiketin büyük harfe dönmesi ve Home yer tutucusunun
silinmesi başka maddelerin işidir — burada dokunulmaz.

- [ ] **Adım 4: Model yönergesi ve araçlar**

- `domain/prompt.py`: docstring ve `"You are Mira, a small AI workspace…"` cümlesi.
- `domain/tools.py`: docstring.

- [ ] **Adım 5: Paket adı**

`frontend/package.json` içinde `"name": "mira-frontend"` → `"queenagent-frontend"`, sonra lock
dosyası **elle düzenlenmez**, yeniden ürettirilir:

```
npm install --prefix queenagent/frontend
```

- [ ] **Adım 6: Belgeler**

Dört belge, spec'in 2.6'sındaki kapsamla:

- `queenagent/README.md` — başlık, çalıştırma ve test komutlarındaki yollar, değişken tablosu,
  yol haritası bağlantısı v2'ye.
- `queenagent/FOUNDATION.md` — başlık, 5. karardaki kök adı, 7. karardaki cümle.
- `queenagent/CODE-STANDARD.md` — başlık, bağımsızlık paragrafı, mağaza tablosu, tasarım paragrafı,
  dil paragrafı, test yolları.
- `CLAUDE.md` — bölüm başlığı ve gövdesi, `python queenagent/main.py`, bağlantılar.

`docs/superpowers/` altındaki tarihî belgelere **dokunulmaz**.

- [ ] **Adım 7: Yeşili doğrula**

```
python -m pytest queenagent
npm test --prefix queenagent/frontend
```

İkisi de yeşil olmalı.

- [ ] **Adım 8: Kabul denetimi**

| Kontrol | Ölçüt |
|---|---|
| Kod | `queenagent/` altında `Mira`/`MIRA`/`mira` araması sonuç vermiyor (`node_modules` hariç) |
| Kök belge | `CLAUDE.md`'de Mira geçmiyor |
| Tarih | `docs/superpowers/` altındaki v1 belgeleri değişmemiş |
| Katman | Hiçbir dosya katman değiştirmedi; `main.py` aynı sınıfları aynı yerde bağlıyor |
| Testler | İkisi de yeşil |

- [ ] **Adım 9: Commit**

```
git add -A
git commit -m 'refactor(queenagent): rename Mira to QueenAgent across code and docs'
```

- [ ] **Adım 10: Kullanıcıya bildir**

Madde bitti; uygulama artık `python queenagent/main.py` ile açılıyor ve **boş bir çalışma alanıyla**
geliyor (veri göçü yok, karar gereği). Sonraki madde: Faz 1 · Madde 2 — aramanın sökülmesi.
