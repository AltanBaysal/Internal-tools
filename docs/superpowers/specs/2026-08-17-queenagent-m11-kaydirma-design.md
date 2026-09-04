# Madde 11 — Kaydırma sözleşmesi · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 11](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynaklar:** fark 13 · **karar 5** · `HANDOFF.md` §2
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Kaynak düzeltmesi ve iki sınır kararı

Yol haritası bu maddeyi *"karar 10"* ile etiketliyor; karar 10 kullanıcı adı etiketini konu alıyor ve
Madde 15'e ait. Buradaki karar **karar 5**: *"Mesaj listesi kayar, composer yerinde durur ve
kaydırılınca kaybolmaz."*

**Sınır 1 — hangi composer dibe çakılı?** Fark 13 ve karar 5 sohbet ekranını anlatıyor: "kayan tek
şey mesaj listesidir". Proje ekranında tasarım composer'ı başlığın altına, iki sütunun üstüne
koyuyor — akışın içinde, dibe çakılı değil. **Sohbetin composer'ı sabit, projeninki akışta.** Ortak
olan kural ikisinde de tutuluyor: sayfanın kendisi hiçbir boyda kaymıyor.

**Sınız 2 — dar pencerede ray sınırsız kalamaz.** Bugün 1100px altında `.chat-layout` ve
`.screen-layout` sütuna dönüp **kendileri kayıyor**; sözleşmenin yasakladığı tam olarak bu. Kaldırınca
ray sohbetin altına iner ve yüksekliği sınırsız olduğu için sohbeti yukarı iter. Bir sınır gerekiyor
ve sayı tasarımın kendi sayısı: `HANDOFF.md` §8, *"Chat file rail moves below the chat (44% height)"*.

**Madde 33'e girmiyoruz:** o madde eşiğin **nasıl ölçüldüğünü** değiştiriyor (medya sorgusu yerine
`ResizeObserver`) ve 1000/780/640 basamaklarını kuruyor. Buradaki %44 o basamakların değil, kaydırma
sözleşmesinin gereği; Madde 33 onu taşır, yeniden karar vermez.

---

## 1 · Ne değişir

| Yer | Bugün | Yeni | Neden |
|---|---|---|---|
| `.app-shell` | `height: 100%` + `min-height: 600px` | `height: 100dvh` | 600px tabanı, kısa pencerede sayfayı kaydıran şeyin ta kendisi |
| `.chat__scroll` | `flex: 1; overflow-y: auto` | + `min-height: 0` | esnek bir çocuk, taşmasını sıfırlamadan kayamaz |
| 1100px bloğu: `.chat-layout`, `.screen-layout` | `overflow-y: auto` | **kaldırılır** | kayan şey zincirin dışı değil, içi olacak |
| 1100px bloğu: `.rail`, `.panel` | `overflow: visible`, `max-height: none` | `overflow-y: auto`, `max-height: 44%`, `flex: none` | alta inen ray kendi içinde kayar, sohbetin yerini yemez |

`min-height: 0` zincirin geri kalanında zaten var (`.chat-layout`, `.chat`, `.screen-layout`, ve dar
blokta `.chat`, `.screen`); eksik olan tek halka `.chat__scroll`'du.

**`100dvh` neden `100%` değil:** mobil tarayıcılarda adres çubuğu `100%`'ü değiştirmiyor ama görünür
alanı değiştiriyor; `dvh` görünür alanı takip eder. Tasarım da ölçüyü adıyla `100dvh` veriyor.

---

## 2 · Ne değişmez

- `.screen`'in kendi kayması (`overflow: hidden auto`). Sözleşme *"the page itself never scrolls —
  only inner regions do"* diyor; `.screen` bir iç bölge.
- `.rail` ve `.panel`'in geniş pencerelerdeki kendi kaymaları.
- Yatay kaydırma zaten yok ve bu maddede yeni bir genişlik doğmuyor; `min-width: 0` zinciri yerinde.

---

## 3 · Katman denetimi

Yalnız `shared/app.css` (kabuk) ve `workspace.css`. Yeni bileşen, yeni bağ yok.

---

## 4 · Kabul ölçütü

1. `.app-shell` `100dvh` yüksekliktedir ve `min-height: 600px` taşımaz.
2. `.chat__scroll` `min-height: 0` taşır.
3. 1100px bloğunda hiçbir yerleşim `overflow-y: auto` almaz.
4. O blokta ray ve panel kendi içlerinde kayar ve yükseklikleri `44%` ile sınırlıdır.
5. `.chat__composer` hâlâ `flex: none` — kaydırmayla kaybolmaz.

## 5 · Risk

Bu madde de jsdom'un göremediği bir şeyi değiştiriyor; testleri **kilit testleri** ve gerçek
doğrulama Madde 35'in elle turudur. En büyük gerçek risk `100dvh`'nin eski tarayıcılarda
desteklenmemesi — uygulama yerel çalışıyor ve tek kullanıcısı güncel bir tarayıcı, o yüzden yedek
değer yazılmıyor.
