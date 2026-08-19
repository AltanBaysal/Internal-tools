# Madde 47 — "project file" okuyucudan kalkar · Plan (iki tur)

**Madde:** [v3 yol haritası Madde 47](2026-08-18-queenagent-v3-roadmap.md) ·
**Kaynak:** [test bulguları, bulgu 1](../research/2026-08-18-queenagent-test-bulgulari.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

Ayrı tasarım belgesi yok: kaldırılan tek şey iki kelime, ve sebebi tek cümlede duruyor.

---

## Neden

Bir dosya açıkken ekran kalabalık. Okuyucunun altındaki satır `2h ago · project file` diyor; ikinci
yarısı hiçbir soruyu cevaplamıyor. Dosya zaten proje rayından açıldı, ve bu uygulamada projeye ait
olmayan dosya yok — yani her dosyanın altında yazan bir şey, hiçbir dosya hakkında bilgi vermiyor.

**Ray satırları değişmiyor.** Orada `project file · 2h ago` listede duruyor ve bulgu onu istemiyor;
istenmeyen, dosya **açıkken** okuyucunun altındaki tekrar.

## Tur 1 — Testler (kırmızı commit)

`FilePanel.test.jsx`:

- `the footer says how long ago it was written and whose file it is` → `the footer says only how
  long ago it was written`; beklenen metin `2h ago`.
- **Yeni:** `the footer does not repeat that the file belongs to the project` — `project file`
  okuyucunun altında geçmez.

`FileRail.test.jsx` ve `FileRow.test.jsx` **dokunulmaz**: satırın metni kalıyor.

## Tur 2 — Uygulama (yeşil commit)

`FilePanel.jsx`: `${relativeTime(file.modifiedAt)} · project file` → `relativeTime(file.modifiedAt)`.
Üstündeki yorum da düzeltilir — bugün "projeye ait olduğunu söyler" diyor, artık söylemiyor.

---

## Kapanış denetimi

- Ray satırlarının testleri hâlâ `project file · 2h ago` bekliyor ve geçiyor.
