# v14 · Görev 18 — Fotoğraf varyant varsayılanı 4 → 2 · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-18-varyant-varsayilani-testler-design.md) ·
kırmızı commit `1a25e1d` (478 testin 1'i kırmızı).

## Bir sayı, bir yorum

**`GeneratePanel.jsx`** — kutunun başlangıç değerindeki `"4"` `"2"` oluyor. Sayı adlandırılmış bir
sabite çıkıyor: bir başlangıç değerinin içine gömülmüş çıplak bir dize, "bu neden bu" sorusunu
sorulamaz kılıyordu, ve bu maddenin tamamı o sorunun cevabı.

Koşul olduğu gibi kalıyor: varsayılan yalnız `settings.variants === null` iken devreye giriyor,
yani kullanıcının kendi kaydettiği sayıya dokunulmuyor.

**`start_batch.py`** — son yorumdaki örnek düzeltiliyor. Cümlenin **neden**'i doğru: onay kartı
sunucunun gerçekten aldığı sayıyı yazıyor, panelin çarpımını değil. Yanlış olan, artık ekranda
olmayan bir satırı ("12 prompt × 4 varyant") o çarpıma örnek göstermesi.

## Değişmeyen

- `LayerPanel.jsx` — kendi kutusu `"1"` ile açılıyor ve bu madde ona dokunmuyor.
- `settings_store`, `start_batch`'in 1–26 kuralı, kaydedilmiş hiçbir proje ayarı.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 694 / 478. `dist` aynı commit'te derleniyor.
