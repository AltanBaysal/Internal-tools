# QueenAgent — Yol Haritası v12

**Durum:** Hazırlanıyor · 0/4 bitti

**Önceki sürüm:** [v11](2026-10-20-queen-agent-v11-roadmap.md) — bitti.

---

| # | İş | Durum |
|---|---|---|
| v12-1 | Düzenlenen mesajın kutusu büyüsün | `UNALIGNED` |
| v12-2 | Mesaj yazma kutusu büyüsün | `UNALIGNED` |
| v12-3 | SDXL start seçiliyken model sormasın | `UNALIGNED` |
| v12-4 | Projeleri toplu arşivle/sil | `UNALIGNED` |

---

### v12-1 — Düzenlenen mesajın kutusu büyüsün

**Kabul koşulu:** Uzun bir mesaj düzenlenirken yazının tamamı görünüyor; yazdıkça kutu büyüyor.

Mesaj düzenlenirken kutu yazının tamamını gösterir, yazıldıkça büyür.

### v12-2 — Mesaj yazma kutusu büyüsün

**Kabul koşulu:** Yazı uzadıkça kutu büyüyor, sınırdan sonra kendi içinde kayıyor. Mesaj gönderilince kutu küçülüyor.

Mesaj yazma kutusu ChatGPT'deki gibi yazı uzadıkça büyür, bir sınırdan sonra kendi içinde kayar.

**Karar verilecek:**
- Kutu en fazla ne kadar büyür?

### v12-3 — SDXL start seçiliyken model sormasın

**Kabul koşulu:** SDXL start scenario seçilip başlatılınca ajan "Krea mı, SDXL mi?" diye sormuyor.

SDXL start scenario seçilince QueenAgent model sormaz; doğrudan SDXL'le başlar.

### v12-4 — Projeleri toplu arşivle/sil

**Kabul koşulu:** Birden fazla proje seçilip tek işlemle arşivlenebiliyor ya da silinebiliyor.

Birden fazla proje seçilip tek seferde arşivlenir ya da silinir.

**Karar verilecek:**
- Toplu arşiv mi, toplu silme mi, ikisi birden mi?
