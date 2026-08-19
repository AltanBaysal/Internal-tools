# Madde 45 — Varsayılan model `grok-4.3` · Test Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 45](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 12](../research/2026-08-18-queenagent-test-bulgulari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Bu belge **yalnız testlerin** turuna aittir.

---

## 1 · Neden 4.3

`grok-4.3` hem ucuz ($1.25 / $2.50) hem 1M bağlam taşıyor; `grok-4.5` iki katı fiyata ($2 / $6)
500k veriyor. Bu ürünün turları uzun — yapı dosyaları, senaryo, kare listesi hep aynı sohbette
birikiyor — yani bağlam da fiyat da 4.3'ün lehine.

Kendi modelini seçmiş sohbetler etkilenmiyor: varsayılan yalnız hiç seçim yapılmamış sohbetlerin
başlangıç noktası.

## 2 · Sayı neden çivileniyor

Bir sabiti sınamak ilk bakışta totoloji görünür. Buradaki değeri, `MAX_ROUNDS == 16` pininin
değeriyle aynı: **karar** çivileniyor, davranış değil. Varsayılanı fark etmeden değiştirmek,
kullanıcının parasını fark etmeden değiştirmek demek — ve bugün bunu söyleyen tek şey `config.py`'ın
içindeki bir dize.

## 3 · Testler ne çiviliyor

| # | Durum | Beklenen |
|---|---|---|
| 1 | `config.XAI_MODEL` | `grok-4.3` |
| 2 | Menü listesi *(ön uç)* | Varsayılan, menünün tanıdığı bir kimlik — yoksa düğme ham id gösterir |

2 numaralı test iki tarafın birbirini tanımadığı yerde duruyor: Python `models.js`'i okuyamıyor,
o yüzden eşleşme `test_skills.py`'daki `ALL_SKILLS` gibi **sözle** çiviliyor.

## 4 · Kabul ölçütü — kırmızının doğru olması

1 **düşer** (bugün `grok-4.5`); 2 **geçer** (`grok-4.3` menüde zaten var, ve bu madde onu koruyor —
Madde 46 listeden bir satır silecek, yanlış olanı silmesin diye).
