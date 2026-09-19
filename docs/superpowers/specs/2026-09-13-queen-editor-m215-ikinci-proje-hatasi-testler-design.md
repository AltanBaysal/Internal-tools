# Madde 215 · İkinci projede üretme hatası — test turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken ve nereden geldiği

Yol haritası iki şey istiyordu: *o anın kendisi* — ekranda duran cümle ve sunucunun ham cevabı — ve
bir karar: **ikinci projede üretmek yasak mı olmalı, yoksa çalışması mı gerekiyordu.**

İkisi de koddan okundu, o yüzden kullanıcıya sorulmadı:

- **Karar zaten verilmiş ve yazılı.** *"Only another project's run is a refusal, because there is one
  worker"* — [run_queue.py](../../../queen-editor/backend/features/photo_generation/domain/usecases/run_queue.py).
  Tek işçi var; ikinci proje beklemek zorunda. *Çalışması gerekiyordu* okuması bu maddeyi değil,
  ikinci bir işçiyi isterdi — bambaşka bir iş.
- **Ekranda duran cümle, hiç.** Aşağıdaki sebep bunu gösteriyor: basılan yerde hiçbir şey
  görünmüyor.

## Sebep — iki eksik prop

**Bu davranışın doğrusu depoda zaten var, yalnız başka panelde.** Fotoğraf paneli aynı durumu
karşılıyor: düğme **kapalı**, ve altında *"Üretim sürüyor: balo — bitmesini bekle."* — projenin adıyla
*([GeneratePanel.jsx:266-269](../../../queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx))*.

Video ve ses paneli bunların hiçbirini almıyor
*([SidePanel.jsx:180-183](../../../queen-editor/frontend/src/features/photo_generation/SidePanel.jsx))*:

| Prop | GeneratePanel | QueuePanel | LayerPanel |
|---|---|---|---|
| `busyElsewhere` | ✓ | ✓ | **yok** |
| `error` | ✓ | ✓ | **yok** |

Sonucu iki katlı:

1. **Düğme kapanmıyor**, yani basılabiliyor ve istek gidiyor; sunucu 409 ile *"Zaten bir üretim
   sürüyor."* diyor — hangi projede sürdüğünü söylemeyen bir cümle.
2. **O cümle hiçbir yere düşmüyor.** Yan panel bir seferde **tek** panel çiziyor; video paneli
   açıkken hata `error`'a yazılıyor ama onu çizen iki panelin ikisi de o an ekranda değil. Kullanıcı
   basıyor ve **hiçbir şey olmuyor**.

"Hata veriyor ama düzgün mesaj vermiyor"un altı bu: mesaj düzgün değil değil — mesaj **yok**.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Başka proje üretirken video panelinin *Kuyruğa ekle*'si kapalı | **kırmızı** |
| 2 | Panel o sırada üretimin **hangi projede** olduğunu söylüyor | **kırmızı** |
| 3 | Ses paneli de aynı | **kırmızı** |
| 4 | Bir yine de gelen red, **basılan panelde** görünüyor | **kırmızı** |
| 5 | Kimse meşgul değilken düğme açık ve hiçbir uyarı yok | yeşil, ve öyle kalmalı |

Dördüncüsü yarışın karşılığı: `busyElsewhere` yoklamayla geliyor, yani öteki koşu iki yoklama
arasında başlarsa düğme hâlâ açık olabiliyor. O durumda basılan yerde bir cümle durmalı — maddenin
kabul cümlesi *"ekranda çıkan cümle ne olduğunu söylüyor"* diyor, ve hiç görünmeyen bir cümle bunu
karşılamıyor.

Beşincisi düzeltmenin paneli sürekli kilitlemesine karşı.

## Sunucunun cümlesine dokunulmuyor

*"Zaten bir üretim sürüyor."* olduğu gibi kalıyor. Panelin söylediği cümle projenin adını taşıyor
çünkü paneli **bilen** taraf o: hangi projede durduğunu ve hangisinin koştuğunu ön yüz biliyor.
Sunucu ise isteği kimin gönderdiğini bilmiyor, ve ona uydurtmak
*"never invent a cause in an error message"*ın tam tersi olurdu.

## Bu turda değişen

Yalnız testler:
[LayerPanel.test.jsx](../../../queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx)
ve [SidePanel.test.jsx](../../../queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx)
*(propun gerçekten geçtiği)*. Bileşenler ve `dist` uygulama turunun işi.
