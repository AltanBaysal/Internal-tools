# Madde 43 — Kare açıklaması 1-2 cümle · Test Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 43](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 10](../research/2026-08-18-queenagent-test-bulgulari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Bu belge **yalnız testlerin** turuna aittir.

---

## 1 · Sayı yazılmalı

Bugünkü yönerge "tek satır" ve "bir paragraf nesir değil" diyor. Kullanıcının turunda model yine de
uzun uzun anlattı. Sebebi anlaşılabilir: "tek satır" bir **biçim** tarifi, uzunluk değil — satır
sonu koymadan üç cümle yazmak da tek satırdır.

Kural sayıya çevriliyor: **bir ya da iki cümle**. Sayılabilir bir sınır, "kısa tut"tan farklı olarak
uyulup uyulmadığı bakışta görülüyor.

## 2 · Testler ne çiviliyor

**`test_skills.py`:**

| # | Durum | Beklenen |
|---|---|---|
| 1 | Kare yönergesi | Sayıyı açıkça söyler: bir ya da iki cümle |
| 2 | Kare yönergesi | "one line" biçim tarifi olarak geçmez — yerini sayıya bıraktı |
| 3 | Kare yönergesi | Uzun anlatım yasağı durur |

2 numaralı test kaldırılan ifadeyi kolluyor: iki kural yan yana durursa model hangisine uyacağını
seçer, ve bugün seçtiği yanlış olan.

## 3 · Testlerin bakmadığı yer

Modelin gerçekten iki cümlede kalıp kalmadığı elle turda görülür. Kare listesinin dili (Madde 44)
aynı cümleleri bir kez daha yazacak; burada yalnız uzunluk değişiyor.

## 4 · Kabul ölçütü — kırmızının doğru olması

1 ve 2 **düşer**; 3 **geçer** — uzun anlatım yasağı bugün de var ve bu tur boyunca korunuyor.
`skip` yok, `xfail` yok.
