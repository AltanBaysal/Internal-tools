# Madde 48 — Seçim menüyü kapatır · Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 48](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 14](../research/2026-08-18-queenagent-test-bulgulari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · Sebep tahmin değil

Kullanıcının gördüğü: model ya da beceri menüsünden bir satır seçince menü açık kalıyor, kapatmak
için ikinci bir tıklama gerekiyor.

İlk bakışta "kapatma kodu eksik" gibi duruyor. Değil — **iki tane var**, ve birbirini bozuyorlar:

1. `Menu` her satır tıklamasında sırayla `item.onChoose?.()` ve `onClose?.()` çağırıyor.
   Seçicilerde `onClose` `onToggle`'a bağlı, yani "menüyü çevir".
2. `App`'in `chooseModel` / `chooseSkill`'i de `setPicker(null)` yapıyor.

İkisi aynı React toplu güncellemesinde çalışıyor. Önce `setPicker(null)` uygulanıyor; sonra
`togglePicker` **o yeni değerden** başlıyor: `null === "model"` yanlış, dolayısıyla `"model"`
döndürüyor. Menü kapanıp **aynı anda yeniden açılıyor**.

Kullanıcının ikinci tıklaması bu yüzden gerekiyor: menü hiç kapanmıyor değil, kapanıp geri geliyor.

## 2 · Düzeltme: kapatmak tek yerin işi

Fazlalık olan `App`'teki `setPicker(null)`'lar. `Menu` zaten kendini kapatıyor ve bu doğru yer:
bir satıra basıldığında menünün işi biter, **seçim bir şeyi değiştirsin ya da değiştirmesin**.

Dördü de siliniyor: `chooseModel`, `chooseSkill`, ve taslak hâlindeki iki satır içi karşılığı.

Bunun bir yan faydası var. Model menüsünde **zaten kullanılan satırın** `onChoose`'u tanımsız —
seçim bir değişiklik değil, sunucuya bir şey sorulmuyor. Kapatma `onChoose`'un içinde olsaydı o
satır menüyü hiç kapatmazdı. `Menu`'de olduğu için kapatıyor.

## 3 · Neden `togglePicker` yerine bir "kapat" yazmıyoruz

Yazılabilirdi ve daha açık olurdu: "kapat" ile "çevir" farklı niyetler. Ama menü **yalnız açıkken**
`onClose` çağırabiliyor, ve açıkken çevirmek kapatmaktır — yani bugünkü bağlantı doğru, yanlış olan
onunla yarışan ikinci güncelleme. İkinci bir prop eklemek, olmayan bir sorunu çözerdi.

## 4 · Testler

`App.test.jsx` — durum orada yaşıyor, ve iki güncellemenin yarışı ancak orada görülür:

| # | Durum | Beklenen |
|---|---|---|
| 1 | Model menüsünden başka bir model seç | Menü kapanır |
| 2 | Model menüsünden **zaten seçili** satıra bas | Menü kapanır, sunucuya bir şey gitmez |

2 numaralı test **bugün de geçiyor**, ve bu teşhisin kanıtı: o satırın `onChoose`'u tanımsız olduğu
için `App`'in `setPicker(null)`'ı hiç çalışmıyor, geriye yalnız `Menu`'nün kapatması kalıyor ve menü
düzgün kapanıyor. Yarış, yalnız bir şeyi gerçekten değiştiren satırlarda çıkıyor. Test tutuluyor
çünkü düzeltme o satırı da bozmamalı.
| 3 | Beceri menüsünden bir beceri seç | Menü kapanır |
| 4 | Taslak sohbette model seç | Menü kapanır |

## 5 · Kabul ölçütü

1. Dört test de yeşil; menüyü açan, kapatan ve birbirini kapatan bugünkü testler bozulmadı.
2. İki komut da yeşil.
3. Elle: seç → menü yok, ikinci tıklama gerekmiyor.
