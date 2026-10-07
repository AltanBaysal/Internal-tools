# Madde 19 — Sohbet ve dosya silme onaya geçer · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m19-silme-onayi-design.md](../specs/2026-08-18-queenagent-m19-silme-onayi-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra uygulama.

---

## Adım 1 — Testler (kırmızı commit)

**Arka uç**
- `test_files_api.py` — geri yükleme yolu `url_map`'te yok; silme hâlâ `trashed` döndürüyor.
- Geri yüklemeyi sınayan var olan testler siliniyor: sınadıkları şey artık yok.

**Ön yüz**
- `useFiles.test.jsx` — `deleting` artık `deleted`/`undo` taşımıyor; silme hâlâ listeden düşürüyor.
- `FileStrip.test.jsx` **siliniyor**, bileşenle birlikte.
- `App.test.jsx` — sohbet "×"i kutuyu açar, `window.confirm` çağrılmaz; iptal hiçbir istek atmaz;
  onay siler. Dosya "×"i kutuyu açar; onay siler; hiçbir yerde "Undo" yok.
- `workspace.css.test.js` — sohbet satırının "×"i saydam değil; `.strip` kuralları yok.

**Ölçülen kırmızı: 1 arka uç + 8 ön yüz.** `FileStrip.test.jsx` ayrıca siliniyor (5 test).

---

## Adım 2 — Uygulama

**Arka uç:** `routes.py`'den geri yükleme yolu, `restore_file.py`, `FileStore.restore` portu ve
uygulaması, kullanılmıyorsa `NameTaken`.

**Ön yüz:** `FileStrip.jsx` silinir; `useFiles.js` sadeleşir; `App.jsx` iki silmeyi de `confirming`
yuvasından geçirir; `ProjectScreen.jsx`/`FileRail.jsx` şeridi çizmeyi bırakır; `workspace.css`
şeridin kurallarını ve "×"in saydamlığını bırakır.

### Kapanış denetimi

- `grep -i undo` boş.
- `grep restore` boş.
- `grep window.confirm` boş.

---

## Risk

Silinen bir bileşenin izleri: `FileStrip` iki ekranda çiziliyor, ikisinden de çıkması gerekiyor.
