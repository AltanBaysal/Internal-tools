# Madde 49 — Rayda dosya silme · Plan (iki tur)

**Madde:** [v3 yol haritası Madde 49](2026-08-18-queenagent-v3-roadmap.md) ·
**Kaynak:** [test bulguları, bulgu 8](../research/2026-08-18-queenagent-test-bulgulari.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

Ayrı tasarım belgesi yok: silme yolunun tamamı zaten var, eksik olan tek bir bağlantı.

---

## Neden ve ne kadar iş

Sohbetteyken kazara doğan bir dosyayı (`bar-frames-2.json`) silmek için proje ekranına dönmek
gerekiyor. Ray satırlarının ×'i yok.

Kod okununca iş küçüldü: `App` **zaten** `deleting={{ ...deleting, remove: askToDeleteFile }}`
nesnesini `ChatScreen`'e veriyor, ve `FileRow` kendisine `onDelete` verilirse ×'i çiziyor. Eksik olan
tek şey `ChatScreen`'in bunu `FileRail`'e, `FileRail`'in de satıra iletmesi. Onay kutusu, çöp yolu,
listenin tazelenmesi — hepsi aynı yol.

## Açık dosyanın satırı

Proje ekranında okuyucu listenin sütununu kaplıyor, o yüzden açık dosyanın satırına basılamıyor ve
bunun bir testi var. Rayda ise liste okuyucunun **yanında** duruyor: açık dosyanın satırı görünür.

Aynı kural uygulanır — **seçili satır × taşımaz**. Sebebi ekran düzeni değil, kuralın kendisi:
okunan bir dosyanın altından silinmesi, kullanıcıyı boş bir okuyucuyla baş başa bırakır.
`FileRow` `selected`'ı zaten biliyor.

## Tur 1 — Testler (kırmızı commit)

`FileRail.test.jsx`:

1. `a row offers a way to delete when the rail is given one` — × var, basınca ad geçiyor.
2. `without a way to delete the rail rows carry no ×` *(bugün de geçer, kuralı tutuyor)*.
3. `the row of the file being read carries no ×`.

`ChatScreen.test.jsx`:

4. `the rail's rows can be deleted from the chat` — `deleting.remove` satırın ×'ine bağlı.

`App.test.jsx`:

5. `deleting a file from the rail asks in the app's own box` — onay kutusu açılıyor, sunucuya
   onaylanmadan bir şey gitmiyor.

## Tur 2 — Uygulama (yeşil commit)

- `ChatScreen.jsx`: `deleting`'i `FileRail`'e geçirir.
- `FileRail.jsx`: `FileList` `deleting`'i alır, seçili olmayan satıra `onDelete` verir. Dosyanın
  başındaki "Its rows do one thing: open a file. Deleting lives on the project screen" yorumu
  **düzeltilir** — artık doğru değil.

---

## Kapanış denetimi

- Proje ekranının silme testleri bozulmadı: aynı `deleting` nesnesi, aynı onay kutusu.
