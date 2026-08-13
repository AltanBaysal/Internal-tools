# v11 Görev 2 — seçili kare sayısı: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-13-queen-editor-v11-gorev-2-testler-design.md) ·
commit `03c5f77` (beş test kırmızı)

## Karar: panel kimliğe uyar, galeri olduğu gibi kalır

Uyumsuzluk iki uçlu, dolayısıyla iki yönden kapatılabilirdi:

- **Panel kimlikle eşlesin** — tek satır, galeriye dokunulmaz.
- **Galeri dosya adı yayınlasın** — bu da tek satır, ama **yanlış**: galeri seçimi bilerek kimlikle
  tutuyor. Bir kareye ikinci video istendiğinde kopya kare doğuyor ve iki kare aynı fotoğrafı
  gösterebiliyor; dosya adı o ikisini ayırt edemiyor. Galeriyi dosya adına çevirmek, panelin sayısını
  düzeltip yerine sessiz bir hata koymak olurdu — iki kareden birini seçtiğinde ikisi birden
  sayılırdı.

Seçilen yol birincisi. `03c5f77`'deki ikiz kare testi zaten bunu çiviliyor: ikinci yol o testi
geçemez.

## Çeviri nerede yapılır

Panel seçimi **kimlikle** eşler, kuyruğa **dosya adı** gönderir. İkisi de aynı yerde, üç satır
arayla — biri düzeltilip öteki unutulamasın diye:

```
kimlikle eşle:   can.filter((frame) => chosen.includes(frame.id))
dosya adı gönder: inSelection.map((frame) => frame.file)
```

İkinci satır bugün de doğru; değişen yalnız birincisi. Sunucunun gördüğü şey değişmiyor.

**ProjectScreen'in araya girip kimlikleri dosya adına çevirmesi düşünülmedi:** panelin elinde zaten
kareler var, eksik olan tek şey doğru anahtardı. Çeviriyi yukarı taşımak, bilgiyi ihtiyaç duyulan
yerden uzağa koymak olurdu.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx` | `inSelection` kimlikle filtrelenir; yorum ikisinin farkını söyler |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

## Kapsam dışı

- Galeri, ProjectScreen, SidePanel: hiçbiri değişmiyor.
- Ses panelinin ayrıca ele alınması: iki panel tek bileşen, düzeltilen satır ikisinin de satırı.
- EKSIKLER'deki maddenin silinmesi: kullanıcının turu kapatır.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 309 geçen, 0 düşen. Beş testin hiçbiri değiştirilmemiş
olur ve `dist/` aynı commit'te yeniden derlenmiş olur.
