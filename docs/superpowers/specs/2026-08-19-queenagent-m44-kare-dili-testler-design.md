# Madde 44 — Kare listesi konuşulan dilde ve dosyada · Test Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 44](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 11](../research/2026-08-18-queenagent-test-bulgulari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Bu belge **yalnız testlerin** turuna aittir.

---

## 1 · Liste neden İngilizce geliyordu

Madde 37 sistem yönergesindeki "in English" cümlesini kaldırdı; model artık sorulan dilde cevap
veriyor. Kare listesi yine de İngilizce geldi, çünkü sebep orada değildi: yönergenin kendisi
kareyi *"one line in **prompt language**"* diye tarif ediyordu. Prompt dili İngilizce, ve model
haklı olarak öyle yazdı.

Madde 43 o cümleyi baştan yazarken ifade düştü. Bu madde boşluğu dolduruyor: liste **konuşulan
dilde** gelir. İngilizceye çeviriyi prompt üreten beceriler yapar — JSON ve `PROMPTS` İngilizce
kalır, çünkü onları bir görüntü modeli okuyor.

Ayrım şu: **insanın okuduğu** kare listesi kullanıcının dilinde, **modelin okuduğu** prompt
İngilizce.

## 2 · Liste dosyada da yaşıyor

Senaryonun Madde 41'de kazandığı deseni kare listesi de kazanıyor: hem sohbete hem bir md dosyasına,
ad konudan türer (`bar-scene-frames.md`), ve sohbetteki düzeltme `edit_file` ile dosyaya işler.

Sebebi aynı: liste yalnız sohbette kalırsa uzun bir konuşmanın içinde kayboluyor ve bir sonraki
adım onu yeniden okumak zorunda kalıyor.

## 3 · Menü satırları — Madde 42'nin bıraktığı

Madde 42 karakter becerisini dosya yazar hâle getirdi ama **menüdeki satırını güncellemedi**: ekran
hâlâ "SDXL character tags. Stays in the chat." diyor. Bu madde onu da düzeltiyor, çünkü ürün şu an
kullanıcıya yanlış bir şey söylüyor ve bir sonraki maddeyi beklemesi için sebep yok.

Bu madde bittiğinde diske bir şey yazmayan tek beceri **Verify prompts** kalıyor — o zaten bilerek
hiçbir şey yazmıyor, işi rapor etmek.

## 4 · Testler ne çiviliyor

**`test_skills.py`:**

| # | Durum | Beklenen |
|---|---|---|
| 1 | Kare yönergesi | Listenin kullanıcının dilinde geleceğini söyler |
| 2 | Kare yönergesi | Çevirinin sonraki beceride olduğunu, promptların İngilizce kaldığını söyler |
| 3 | Kare yönergesi | `create_file` ve `edit_file` geçer |
| 4 | Kare yönergesi | Dosya adı konudan türer, `-frames` ekiyle, örneğiyle |
| 5 | Kare yönergesi | "Do not create a file" artık geçmez |
| 6 | Denetleyen yönerge | "Do not create a file" hâlâ geçer — bilerek yazmıyor |

**`skills.test.js`:**

| # | Durum | Beklenen |
|---|---|---|
| 7 | Menü | Hiçbir satır "stays in the chat" demez |
| 8 | Menü | Karakter satırı dosyadan söz eder; kare satırı da |

## 5 · Kabul ölçütü — kırmızının doğru olması

1-5 ve 7-8 **düşer**; 6 **geçer** (bugünkü davranış, korunuyor). `skip` yok, `xfail` yok.
