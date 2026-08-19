# Madde 46 — `grok-4.5` menüden kalkar · Test Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 46](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 13](../research/2026-08-18-queenagent-test-bulgulari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Bu belge **yalnız testlerin** turuna aittir.

---

## 1 · Neden kalkıyor

`grok-4.5` ile `grok-4.6` **aynı fiyatta** ($2 / $6, 500k bağlam). Aynı paraya bir alt sürümü
sunmanın kullanıcıya faydası yok; menüde durması yalnız seçilecek bir yanlış seçenek daha demek.

Menü listesi ürünün "hangi modeller var" cevabı değil, "hangilerini sunuyoruz" cevabı. Bu ayrım
listeden bir satır silmeyi meşru kılıyor: xAI onu yayınlamayı sürdürüyor, biz sunmuyoruz.

## 2 · Onu seçmiş eski sohbet

Kayıtta `grok-4.5` yazan bir sohbet çalışmaya devam eder ve düğmesi **ham kimliği** gösterir.
Bu, listenin tanımadığı her kimlik için zaten böyle — Madde 39'da beceriler için kullanılan aynı
desen. Yeni bir koruma yazılmıyor; var olan davranış, bu kimlik için de çiviliyor.

## 3 · Testler ne çiviliyor

| # | Durum | Beklenen |
|---|---|---|
| 1 | Menü listesi | Altı satır, `grok-4.5` yok |
| 2 | `modelName("grok-4.5")` | Ham kimliği döndürür — eski sohbet kırılmaz |

## 4 · Sıra neden Madde 45'ten sonra

Varsayılan hâlâ `grok-4.5` olsaydı, bu madde her yeni sohbetin düğmesini ham kimliğe çevirirdi.
Madde 45 varsayılanı taşıdı; bu madde artık kimsenin başlangıç noktası olmayan bir satırı siliyor.

## 5 · Kabul ölçütü — kırmızının doğru olması

İkisi de **düşer**. İkincisi ilk bakışta bugünkü davranışı sınıyor gibi görünüyor ama değil: satır
hâlâ listede olduğu için `modelName("grok-4.5")` bugün **"Grok 4.5"** döndürüyor, ham kimliği değil.
Ham kimliğe düşmesi ancak satır silindiğinde doğru olur — yani test, silmenin eski sohbeti
kırmadığını gösteren şey.
