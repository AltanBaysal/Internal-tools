# QueenAgent — Yol Haritası v12

**Durum:** Hazırlanıyor · 0/4 bitti

**Önceki sürüm:** [v11](2026-10-20-queen-agent-v11-roadmap.md) — bitti.

---

| Numara | İş | Durum |
|---|---|---|
| [v12-1](#v12-1) | Düzenlenen mesajın kutusu büyüsün | `UNALIGNED` |
| [v12-2](#v12-2) | Mesaj yazma kutusu büyüsün | `UNALIGNED` |
| [v12-3](#v12-3) | SDXL start seçiliyken model sormasın | `UNALIGNED` |
| [v12-4](#v12-4) | Projeleri toplu arşivle/sil | `UNALIGNED` |

---

<a id="v12-1"></a>
### v12-1 — Düzenlenen mesajın kutusu büyüsün

**Kabul koşulu:** Uzun bir mesaj düzenlenirken yazının tamamı görünüyor; yazdıkça kutu büyüyor.

Mesaj düzenlenirken kutu yazının tamamını gösterir, yazıldıkça büyür.

<a id="v12-2"></a>
### v12-2 — Mesaj yazma kutusu büyüsün

**Kabul koşulu:** Yazı uzadıkça kutu büyüyor, sınırdan sonra kendi içinde kayıyor. Mesaj gönderilince kutu küçülüyor.

Mesaj yazma kutusu ChatGPT'deki gibi yazı uzadıkça büyür, bir sınırdan sonra kendi içinde kayar.

**Karar verilecek:**
- Kutu en fazla ne kadar büyür?

<a id="v12-3"></a>
### v12-3 — SDXL start seçiliyken model sormasın

**Kabul koşulu:** SDXL start scenario seçilip başlatılınca ajan "Krea mı, SDXL mi?" diye sormuyor.

SDXL start scenario seçilince QueenAgent model sormaz; doğrudan SDXL'le başlar.

<a id="v12-4"></a>
### v12-4 — Projeleri toplu arşivle/sil

**Kabul koşulu:** Birden fazla proje seçilip tek işlemle arşivlenebiliyor ya da silinebiliyor.

Birden fazla proje seçilip tek seferde arşivlenir ya da silinir.

**Karar verilecek:**
- Toplu arşiv mi, toplu silme mi, ikisi birden mi?
