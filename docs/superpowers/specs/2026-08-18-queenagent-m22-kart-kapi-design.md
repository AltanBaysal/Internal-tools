# Madde 22 — Dosya kartı kapı olur · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 22](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 44, 45'in kart yarısı, **53** · `HANDOFF.md` §2, §3
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 0 · fark 53 bu maddeye katıldı

Yol haritası fark 53'ü ("dosya açılınca ray listesinin yerinde kalması") hiçbir maddeye yazmamış.
Kullanıcıya soruldu, **Madde 22'ye katılmasına** karar verildi.

Gerekçe: bu maddenin kendi ölçütü zaten "panelin hangi dosyada olduğu hem karttan **hem ray
satırından** okunur" diyor. Ray satırı bir dosya açıkken çizilmiyorsa o cümlenin yarısı yerine
gelemez. İkisi tek iş.

---

## 1 · Kart bir kapıdır (fark 44)

Cevabın altındaki kart bugün bir `<div>`: çip, ad ve "✓ saved to project". Tasarımda **düğme**
oluyor ve sağında mono bir ipucu duruyor: `Open ›`.

Basınca dosya panelde açılıyor. Ray katlıysa önce açılıyor — bu kural Madde 20'de tek yere
yazılmıştı ve **burada yeniden yazılmıyor**, kart App'in aynı `openFile`'ını çağırıyor.

Kart en çok 340px, 12px yarıçap — "creating file…" kutusuyla aynı iskelet, çünkü o kutu bu kartın
doğmadan önceki hâli.

---

## 2 · Açık dosya iki yerden okunur (fark 45)

| Nerede | Kapalıyken | Açıkken |
|---|---|---|
| Transkriptteki kart | yüzey rengi, ipucu `Open ›` | `#F4EFE7` zemin, `#CFC3B2` çerçeve, ipucu `open` |
| Raydaki satır | düz | `#EFEBE4` zemin *(Madde 21'de kondu)* |

İpucu **`Open ›`den `open`a** düşüyor: açık olan bir şey için "aç" demek yanlış olurdu, ve tasarım
ok işaretini de kaldırıyor — gidilecek bir yer kalmadı.

---

## 3 · Ray, okurken listeyi bırakmıyor (fark 53)

Bugün sohbette bir dosya açılınca ray 320'den 560'a genişliyor ama içindeki liste **bütünüyle**
okuyucuyla değişiyor: paneli kapatmadan başka bir dosyaya geçilemiyor.

Bundan sonra ray genişlerken satırlar yerinde kalıyor. İki sütun:

| Sütun | Genişlik | Neden |
|---|---|---|
| liste | 200px | ad + çip için yeterli; ikincil satır sararsa sarar |
| okuyucu | kalanı (~340px) | okunan şey ekranın asıl işi |

**200px tasarımın verdiği bir sayı değil.** `HANDOFF.md` yalnız 320→560 geçişini yazıyor, bölünmeyi
yazmıyor. 200 seçildi çünkü 560'ın kalanı okuyucuya kapalı rayın kendi genişliğine yakın bir alan
bırakıyor; Madde 35'te göze bakılacak.

**Katlama denetimi okurken yok.** Madde 20'nin kuralı duruyor: ray bir belge gösterirken katlanacak
bir şey yok. Liste sütununun başlığı o hâlde düğme değil, etiket ve sayı.

Her iki sütun kendi içinde kayıyor; ray bir bütün olarak kaymıyor. Madde 11'in kuralı.

---

## 4 · Proje ekranı bu maddede değişmiyor

Proje ekranında panel açıkken **dosyalar sütununun hiç çizilmemesi** ayrı bir fark (61) ve **Madde
24**'ün işi. Burada yalnız sohbetin rayı konuşuluyor.

---

## 5 · Katman denetimi

`ChatScreen.jsx` (kart), `FileRail.jsx` (iki sütun), `workspace.css`. Yeni bileşen yok, arka uç yok.
Rayı açan kural App'te kalıyor — kart onu çağırıyor, kopyalamıyor.

---

## 6 · Kabul ölçütü

1. Kart bir düğmedir ve sağında `Open ›` yazar.
2. Basınca o dosya panelde açılır; ray katlıysa açılır.
3. Açık dosyanın kartı `#F4EFE7` zemin ve `#CFC3B2` çerçeve alır, ipucu `open` olur.
4. Kart en çok 340px ve 12px yarıçaplıdır.
5. Bir dosya açıkken ray listesi yerinde durur ve açık olanın satırı seçilidir.
6. Panel kapatılmadan başka bir dosyaya geçilebilir.
7. Ray okurken katlama denetimi göstermez.

## 7 · Risk

200px'lik bölünme tasarımdan gelmiyor. Kilit testi sayıyı, Madde 35 gözü üstleniyor.
