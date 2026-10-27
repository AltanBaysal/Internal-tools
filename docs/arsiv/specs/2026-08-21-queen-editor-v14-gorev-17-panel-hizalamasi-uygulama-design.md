# v14 · Görev 17 — Panelin görsel hizalaması · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-17-panel-hizalamasi-testler-design.md) ·
kırmızı commit `f586eb6` (475 testin 10'u kırmızı).

Bir dosya çiziyor, üç dosya bir adı düzeltiyor.

## 1 · Satırın ortak kılığı

`ScopeRow` ile `ModeRow` bugün aynı biçimi iki kez yazıyor ve fark 31 ölçüyü değiştirdiğinde
ikisinden biri geride kalırdı. Ortak olan tek bir sabite çıkıyor:

```
ROW   satır · ortalanmış · 10px 12px · zeminsiz · tam genişlik
```

İki bileşen kalıyor. `ModeRow`'un kendi gerekçesi duruyor: sayısı olmayan bir satırı eksik
argümanlı bir `ScopeRow` yapmak, okuyucuya "eksik sayı ne demek" sorusunu bırakırdı.

## 2 · Seçim dairesi *(fark 31)*

`ScopeRow`'un başına 12 piksellik bir daire giriyor:

| | çerçeve | renk |
|---|---|---|
| seçili | 2px | `--accent` |
| öteki | 1px | `--ink-3` |

Kısayol değil üç uzun özellik yazılıyor (`borderWidth` · `borderStyle` · `borderColor`): içinde
`var()` geçen bir `border` kısayolunu tarayıcı geri okutmuyor, ve bu daireyi ölçen test onu geri
okuyor.

Daire yalnız kapsam satırında. Mod satırının kendi işareti 4. maddede karara bağlandı.

**Satırın soluğu daireye dokunmuyor.** Bugün seçili olmayan satırın tamamı `opacity: .4` ile
soluyor; daire de onunla soluyor ve "ince ve soluk" zaten bu. Ayrı bir soluklaştırma yazılmıyor.

## 3 · Model kutusu *(fark 32)*

Soluk metin satırı, fotoğraf panelinin `select`'ine dönüyor — aynı `wf-input`, aynı çerçeve, aynı
ok. İçinde tek `option`: katmanın kendi modeli.

Kutu hiçbir yere bir şey göndermiyor; kuyruğa giden işin model alanı zaten boş ve motor kendi
seçiyor. Değişen şey görünüm, ve gün gelip ikinci bir model çıktığında kutu yerinde duruyor.

## 4 · Kapsam satırının adı *(fark 30)*

`WORDS.video.missing` → **"Videosu olmayan kareler"**.

**Üç yerdeki yorum bu adı anıyor ve üçü de düzeltiliyor** — `queue_layer.py`'nin `frames_in_scope`
açıklaması, `test_photo_usecases.py`'nin bir satırı, `LayerPanel.jsx`'in iki satırı. Kodla çelişen
yorum kodla eşitlenir; kısa ad hiçbir yerde kalmıyor.

## 5 · Süre bloğu *(fark 33)*

Blok ve `WORDS`'ün `note` alanı gidiyor.

Kalan dört blok başlığı `data-label` alıyor — panelin neyden ibaret olduğunu DOM'dan okunabilir
kılan tek şey bu, ve maddenin "bitti sayılır"ı tam olarak o liste.

## Değişmeyen

- `GeneratePanel.jsx` — model kutusu orada zaten var.
- `eligible`, `neighbours`, `refusalOf` — 16. maddenin kuralları.
- `InstallCard` — kendi kartı, ve üretici varken hiç doğmuyor.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 694 / 475. `dist` aynı commit'te derleniyor.
