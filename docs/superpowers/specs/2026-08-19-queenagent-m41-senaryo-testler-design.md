# Madde 41 — Senaryo kısa ve madde madde · Test Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 41](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 7](../research/2026-08-18-queenagent-test-bulgulari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Bu belge **yalnız testlerin** turuna aittir.

---

## 1 · Senaryo neden kısalıyor

Senaryonun amacı bir eser üretmek değil, **AI'ın hikâyeyi ne anladığını görmek**. Uzun akan bir
metin bunu zorlaştırıyor: okumak vakit alıyor, ve yanlış anlaşılmış bir nokta iki paragrafın içinde
kayboluyor. Madde madde yazılan bir ana hat, aynı bilgiyi göz bir bakışta tarayabilecek şekilde
veriyor.

Bugünkü yönerge "10 ila 15 cümle, düz nesir" diyor. İkisi de düşüyor: **maddeler**, ve sayı yerine
"kısa, ana hatlar".

## 2 · Senaryo artık dosyada da yaşıyor

Bugün senaryo sabit `scenario.md` adıyla kaydediliyor. İki sorun:

- **Sabit ad.** Bir projede birden çok senaryo yaşıyor; ikincisi ya birinciyi eziyor ya
  `scenario-2.md` oluyor ve hangisinin ne olduğu kayboluyor. Ad **konudan türer**: `bar-sahnesi.md`.
- **Düzeltmeler dosyaya işlemiyor.** Kullanıcı sohbette "şurayı değiştir" dediğinde model sohbette
  düzeltiyor, dosya eskimiş hâliyle kalıyor. Düzeltme `edit_file` ile dosyaya da geçmeli.

Sohbete yazma kuralı duruyor: dosya cevabın yerine geçmez, ikisi birden.

## 3 · Testler ne çiviliyor

**`test_skills.py`:**

| # | Durum | Beklenen |
|---|---|---|
| 1 | Senaryo yönergesi | "10 to 15" ve "sentences of plain prose" geçmez |
| 2 | Senaryo yönergesi | Maddeler ister — liste biçimini adıyla söyler |
| 3 | Senaryo yönergesi | Amacı söyler: ne anlaşıldığını göstermek, kısa kalmak |
| 4 | Senaryo yönergesi | Sabit `scenario.md` geçmez; ad konudan türer ve örneği vardır |
| 5 | Senaryo yönergesi | `create_file` **ve** `edit_file` geçer — düzeltme dosyaya işler |
| 6 | Senaryo yönergesi | Sohbete de yazılacağı durur |

1 ve 4 numaralı testler **kaldırılan** cümleleri kolluyor; ikisi de bugün düşer, çünkü o cümleler
şu an orada. Böyle bir test yazmanın sebebi: eski kural sessizce geri gelmesin.

## 4 · Testlerin bakmadığı yer

Kare listesinin dosyaya yazılması (Madde 44) aynı deseni kullanacak ama ayrı bir madde. Burada
yalnız senaryo değişiyor.

Modelin gerçekten madde madde yazıp yazmadığı yönergeyle sınanamaz — bu, kullanıcının elle turunda
görülür. Test yönergenin **ne söylediğini** çiviliyor, modelin ona uyduğunu değil.

## 5 · Kabul ölçütü — kırmızının doğru olması

1-5 **düşer**: bugünkü metin ne maddelerden söz ediyor, ne konudan türeyen bir addan, ne de
`edit_file`'dan; kaldırılacak iki cümle de hâlâ orada.
6 **geçer** — "sohbete de yaz" kuralı bugün de var ve bu madde onu korumak için tutuyor: dosyaya
yazmayı eklerken cevabın sohbetten kaybolması, düzeltirken bozmanın en kolay yolu.

`skip` yok, `xfail` yok.
