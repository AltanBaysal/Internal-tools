# Madde 442 · Sürüm numarası V10 — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
442 (eski adı v10-5) · **Dal:** `feat/queenagent-v10` · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

## Ne, neden

Kullanıcı, 1 Ekim: *"bir de queen agentın numarsını v9 günçelemmişiz galiba dıoğru mu ?"*; 5 Ekim:
*"evet biliyorum ama roadmpı koşunda 10 için direkt 10a güncelleriz artık"*. Sürüm doğrudan `V10`
olur; `V9` hiç yazılmaz.

Bugün:

- Sürüm tek yerde yazılı: [version.js](../../queen-agent/frontend/src/shared/version.js)'in
  `VERSION`'ı, `"V8"` (Madde 209). v9 onu değiştirmedi.
- Ekranda tek yerde görünüyor: üst çubukta, adın yanında — *"QueenAgent V8"*
  ([Bar.jsx](../../queen-agent/frontend/src/features/workspace/Bar.jsx)). Kenar çubuğu onu göstermez
  (`Sidebar.test.jsx` tutuyor). Sekmenin başlığı (`index.html`'in `<title>`'ı) yalnız *"QueenAgent"*;
  defter, arka uç ve aracın belgeleri sürüm göstermiyor.
- `V8` bunun dışında yalnız üç yorumda geçiyor: `version.js`'in kendi yorumu, `version.test.js` ve
  `Bar.test.jsx`.

## Olacak

`VERSION` `"V10"` olur. Üç yorum sayıyı yazmadan söylenir (*"which run this is"*, *"the value"*,
*"a literal"*): sürüm yalnız `version.js`'in tek satırında durur, ve bir sonraki koşu yalnız onu
değiştirir. Aracın ağacında `V8` hiçbir yerde kalmaz.

## Sınırlar

- Değerin kendisini tutan test yazılmaz. `version.test.js` bunun nedenini söylüyor: sürüm elle
  verilen bir karar, onu testte de yazmak bir kararı iki yere koyar. Testler biçimi (`/^V\d+$/`) ve
  çubuğun sabiti gösterdiğini tutuyor; `V10` ikisinden de geçer. Bu yüzden kırmızı adım yok.
- Defterin `BRANCH`'ı (`feat/queenagent-v9`) sürüm değil, defterin klonladığı dal; bu maddenin işi
  değil.
- queen-editor'e ve geçmişi kaydeden roadmap ve spec'lere dokunulmaz.

## Değişen dosyalar

- `frontend/src/shared/version.js` — `"V10"`; yorum sayısız.
- `frontend/src/shared/version.test.js`, `frontend/src/features/workspace/Bar.test.jsx` — yorumlar
  sayısız.
- `frontend/dist` yeniden derlenir.

## Bitti sayılır

- Dört suite yeşil (`test_dist_is_committed` dist commit'lenene kadar hariç), `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: üst çubukta *"QueenAgent V10"* yazıyor; `V8` hiçbir yerde yok.
