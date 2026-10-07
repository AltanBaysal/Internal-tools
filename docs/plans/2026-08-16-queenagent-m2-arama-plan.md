# Madde 2 — Arama gider · Uygulama Planı

**Tasarım belgesi:** [2026-08-16-queenagent-m2-arama-design.md](../specs/2026-08-16-queenagent-m2-arama-design.md)

**İki commit.** Önce "artık yok" testleri (kırmızı gider), sonra söküm.

---

## Commit 1 — Testler (kırmızı)

Silinen bir şeyin testi, **yokluğunu** iddia eden testtir. Kaynak hâlâ aramayı taşıdığı için bu
iddialar başarısız olur.

- [ ] **Adım 1: `Sidebar.test.jsx`**

Var olan arama testleri, yokluk iddiasına çevrilir: kenar çubuğunda "Search" metni ve "⌘K" rozeti
**bulunmaz**; ad ile "New chat" arasında başka düğme yoktur.

- [ ] **Adım 2: `App.test.jsx`**

⌘K/Ctrl+K'ya basmak hiçbir katman açmaz. Var olan arama akışı testleri (katmanı aç, yaz, sonuca
tıkla) silinir — davranış artık yok, testi de yok.

Esc davranışının **kalan** hâli açıkça test edilir: dosya paneli açıkken Esc paneli kapatır.

- [ ] **Adım 3: `test_files_api.py`**

`/api/search` çağrısı yapan iddia, uç noktanın **404** döndüğü iddiasına çevrilir.

- [ ] **Adım 4: Kırmızıyı doğrula**

```
npm test --prefix queenagent/frontend
python -m pytest queenagent
```

Beklenen: kenar çubuğu, ⌘K ve `/api/search` iddiaları kırmızı.

- [ ] **Adım 5: Commit** — `test(queenagent): expect search to be gone`

---

## Commit 2 — Söküm (yeşil)

- [ ] **Adım 1: Ön yüz dosyalarını sil**

`SearchPanel.jsx`, `SearchPanel.test.jsx`, `useSearch.js`.

- [ ] **Adım 2: `App.jsx`**

İçe aktarımlar, `searching` durumu, `pickHit`, ⌘K dinleyicisi, `onSearch` bağlantısı ve katmanın
çizimi gider. Esc dinleyicisi kalır ama yalnız açık dosya panelini kapatır.

- [ ] **Adım 3: `Sidebar.jsx`**

"Search" düğmesi ve rozeti gider; `onSearch` özelliği imzadan kalkar.

- [ ] **Adım 4: `workspace.css`**

Arama katmanının ve sonuç satırlarının stilleri gider.

- [ ] **Adım 5: Arka uç**

`search.py` ve `hit.py` silinir; `routes.py`'den `/api/search` ve çeviri gövdesi gider;
`test_search.py` silinir.

- [ ] **Adım 6: Ölü yorum ve belgeler**

`useRoute.js`'in yorumundan arama gerekçesi çıkar; `CODE-STANDARD.md`'den arama örneği düşer;
`FOUNDATION.md` aynı ölçüyle gözden geçirilir.

- [ ] **Adım 7: Yeşili doğrula ve kabul denetimi**

Spec'in 4. bölümündeki beş ölçüt tek tek kontrol edilir.

- [ ] **Adım 8: Commit** — `refactor(queenagent): remove search, the design drops it deliberately`
