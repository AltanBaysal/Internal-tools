# Queen Editor — Yol Haritası v11

**Durum:** Hazırlanıyor · 0/4 bitti

**Önceki sürüm:** [v10](2026-10-20-queen-editor-v10-roadmap.md) — bitti.

---

| Numara | İş | Durum |
|---|---|---|
| [v11-1](#v11-1) | Translucent Penetration (Krea ve Qwen) | `UNALIGNED` |
| [v11-2](#v11-2) | Boşta Colab'ı kapat | `UNALIGNED` |
| [v11-3](#v11-3) | Drive dolunca iş kaybolmasın | `UNALIGNED` |
| [v11-4](#v11-4) | Femboy LoRA'sı | `UNALIGNED` |

---

<a id="v11-1"></a>
### v11-1 — Translucent Penetration (Krea ve Qwen)

**Kabul koşulu:** Krea fotoğrafı üretirken Translucent Penetration kullanılabiliyor. Qwen sürümünün test sonucu yazılı.

Translucent Penetration LoRA'sı Krea fotoğraflarında da kullanılır; Qwen sürümü de denenir.

**Karar verilecek:**
- Krea sürümü SNOFS'un yanına mı girer, yerine mi?
- Hep mi açık olur, seçilerek mi?

<a id="v11-2"></a>
### v11-2 — Boşta Colab'ı kapat

**Kabul koşulu:** Sırada iş yokken ekranda "orada mısın?" çıkıyor. Cevap verilmezse Colab kapanıyor, verilirse açık kalıyor.

Sırada iş yokken Queen Editor "orada mısın?" diye sorar; cevap gelmezse Colab'ı kapatır.

**Neden:** Colab boşta açık kalınca A100 boşa para yiyor.

**Karar verilecek:**
- Sıra ne kadar boş kalınca sorulur?
- Sorudan sonra ne kadar beklenir?
- Süren export ya da ajan sohbeti iş sayılır mı?
- Sekme kapalıyken ne olur?

<a id="v11-3"></a>
### v11-3 — Drive dolunca iş kaybolmasın

**Kabul koşulu:** Drive dolduğunda üretilen fotoğraf ve videolar kaybolmuyor.

Drive dolunca üretilen iş kaybolmaz.

**Karar verilecek:**
- Drive dolmadan önce uyarı mı, yer açılınca yeniden yazma mı, ikisi birden mi?

<a id="v11-4"></a>
### v11-4 — Femboy LoRA'sı

**Kabul koşulu:** LoRA'nın test sonucu yazılı. İyi çıktıysa Queen Editor'de kullanılabiliyor.

femboysXL ya da benzeri bir LoRA test edilir, iyi çıkarsa Queen Editor'e eklenir. Özel prompt istiyorsa QueenAgent'a bilgisi eklenir.
