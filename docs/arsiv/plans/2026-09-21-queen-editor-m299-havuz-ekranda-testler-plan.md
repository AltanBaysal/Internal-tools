# Madde 299 — Havuz ekranda, test turunun planı

**Spec:** [m299 test turu](../specs/2026-09-21-queen-editor-m299-havuz-ekranda-testler-design.md)

Üç test dosyası: `shared/api.test.js` *(var)*, yeni
`features/photo_generation/ReferencePanel.test.jsx`, ve `ProjectScreen.test.jsx` *(var)*. Kaynak
koda dokunulmuyor.

## Adımlar

1. **`api.test.js`** — iki test, dosyanın kendi `fetch` sahteleme biçimiyle.

2. **`ReferencePanel.test.jsx`** — `shared/api.js` `vi.mock` ile; `PhotoDetail.test.jsx`'in yaptığı
   gibi. Panel kendi verisini kendi çekiyor, yani testler onu tek başına kuruyor.

3. **`ProjectScreen.test.jsx`** — mock'a referans çağrıları ekleniyor *(panel artık o ekranda)*, ve
   iki test panelin açılıp kapanmasını okuyor.

4. **Dört test satırı koşulur.**

## Beklenen kırmızı

`ReferencePanel.jsx` yok — o dosya toplamada düşer. `api.test.js`'in iki testi `uploadReferences`
olmadığı için düşer. `ProjectScreen`'in iki yeni testi panel olmadığı için düşer; **o dosyanın
öteki testleri yeşil kalır**, çünkü mock'a eklenen anahtarlar bugünkü ekranı bozmuyor.
