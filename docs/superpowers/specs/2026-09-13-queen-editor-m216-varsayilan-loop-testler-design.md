# Madde 216 · Varsayılan mod Loop — test turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Değişen bileşen:** [LayerPanel.jsx](../../../queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx)

## İstenen

*(Kullanıcı, 11 Eylül.)* Video panelindeki *Üretim modu* seçicisi bugün **Standart** ile açılıyor;
bundan sonra **Loop** ile açılacak. Yalnız varsayılan değişiyor — üç seçenek de yerinde kalıyor.

## Bir tuzak var, ve ses panelini kırıyor

Panel iki katman için de aynı bileşen, ve mod durumu **ikisinde de** tutuluyor: satırı yalnız video
paneli çiziyor ama isteği ikisi de aynı biçimde gönderiyor *(bugünkü yorumun sebebi: sunucu isteğin
nereden geldiğini sormasın)*.

Sunucu tarafında ise [production_mode.validate](../../../queen-editor/backend/features/photo_generation/domain/production_mode.py)
şunu diyor:

> `mode != STANDARD` ve katman video değilse → **InvalidMode: "Üretim modu yalnız video işine
> verilebilir."**

Yani `useState(STANDARD)`'ı düz `useState(LOOP)` yapmak **her ses işini reddettirir**. Varsayılan
katmana bağlı olmak zorunda: video → Loop, ses → Standart.

Bu, maddenin tek satırlık görünen ama tek satır olmayan yeri, ve kendi çivisini istiyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Video paneli **Loop** işaretli açılıyor | **kırmızı** — Standart işaretli |
| 2 | Hiçbir şeye dokunmadan kuyruğa giren video işi `loop` taşıyor | **kırmızı** — `standard` |
| 3 | **Ses paneli hâlâ `standard` gönderiyor** | yeşil, ve öyle kalmak zorunda |
| 4 | Video panelinin tahmin cümlesi açılışta loop'un sözleriyle konuşuyor | **kırmızı** |

Üçüncüsü bugün de geçiyor; yazılma sebebi, bu maddenin onu kırmanın en kolay yolu olması. Sunucunun
reddi ön yüzde görünmez — kullanıcı yalnız *"ses üretilmedi"* der.

## Tahmin cümlesi kendiliğinden değişiyor

Butonun altındaki cümle zaten moda göre konuşuyor: `nounOf` ile *"loop video"*, `MODE_TAIL` ile
*"her video kendine döner."* Yani bu maddede yazılacak yeni bir cümle yok — ama **açılıştaki cümle
değişiyor**, ve video panelini kuran altı eski test onu harfi harfine bekliyor.

O altı test kapsamı sayıyor, modu değil; beklenen metinleri loop'unkiyle güncelleniyor, kurdukları
şey aynı kalıyor. Ses panelinin cümleleri *(`1 ses üretilecek — her kare kendi sesini alır.`)*
değişmiyor, çünkü orada varsayılan Standart.

## Değişmeyenler

- **Detay sayfasındaki *Yeni mod* kutusu.** Onun varsayılanı `newMode = null`, yani *"bu videonun
  kendi modu"* — LayerPanel'in varsayılanından bağımsız, ve öyle kalıyor. Orası yeni bir iş açmıyor,
  var olan bir videoyu yeniden üretiyor *(madde 94)*.
- **Ses paneli seçici çizmiyor.** Bugün de çizmiyordu; değişen tek şey, artık çizmemesinin bir bedeli
  olması — o yüzden 3 numaralı çivi.
- **Üç seçenek, sıraları, ve bağlamanın kapanma kuralı.**

## Bu turda değişen

Yalnız [LayerPanel.test.jsx](../../../queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx):
iki test yeniden yazılır, bir test eklenir, altı beklenen metin güncellenir. Bileşen ve `dist`
uygulama turunun işi.
