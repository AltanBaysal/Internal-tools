# Madde 20 — Ray katlanır · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 20](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 50, 51 · `HANDOFF.md` §2, §8
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · Başlık, katlama düğmesinin kendisidir

Bugün rayın başlığı bir `<h2>` ve ray hep açık. Tasarımda başlık **denetimin kendisi** oluyor:
"Project files" + dosya sayısı + şevron.

Katlanınca ray 46px'lik dikey bir şeride iniyor — etiket döndürülmüş, sayı hâlâ okunur — ve şeride
bir kez tıklamak geri açıyor. Geçiş 220ms, yani rayın zaten sahip olduğu tek genişlik geçişi.

**Tek denetim, iki hâl.** Açıkken başlık, katlıyken şerit; ikisi de aynı düğme. Tasarım "başlık
katlama denetimidir" ve "şeride bir tıklama açar" diyor — iki ayrı düğme yazmak aynı cümleyi iki
kere söylemek olurdu.

---

## 2 · Durum nerede yaşıyor

**App'te.** Tasarım "durum oturum boyunca sohbetler ve projeler arasında korunur" diyor; ray
bileşeni her sohbet değişiminde yeniden kuruluyor, dolayısıyla durumu o tutamaz.

**Diske yazılmıyor.** "Oturum boyunca" tam olarak bunu söylüyor, ve `QUEENAGENT_ROOT` kullanıcının
verisi için — bir panelin açık olup olmadığı veri değil.

---

## 3 · Dosyayı açan her eylem rayı zorla açar

Katlı bir rayda dosya açmak, açılan şeyi görünmez bir yere koymak olurdu.

Kural **tek yerde** duruyor: App dosya açma çağrısını sarıyor, önce rayı açıyor sonra okumayı
başlatıyor. Bugün tek çağıran ray satırı; **Madde 22** transkriptteki kartı ikinci çağıran yapacak
ve kuralı yeniden yazmayacak.

---

## 4 · Dar pencerede şerit değil, tek satır

`HANDOFF.md` §8: 1000px altında ray sohbetin **altına** iniyor ve katlanınca dikey şeride değil
**tek bir başlık satırına** iniyor. Dikey bir şerit yatay bir yerleşimde anlamsız olurdu.

**Ölçü bugün 1100px.** Yerleşim kırılma noktası Madde 11'de bu değerde bırakıldı ve **Madde 33**
onu tasarımın 1000'ine taşıyacak. Burada yeni bir sayı açılmıyor; var olan blok kullanılıyor.

---

## 5 · Ne değişmiyor

- **Proje ekranının dosya sütunu katlanmıyor.** Tasarım katlamayı yalnız **sohbet ekranının rayı**
  için tanımlıyor.
- Dosya açıkken ray zaten paneli çiziyor; katlama denetimi o hâlde görünmüyor — katlanacak bir liste
  yok, okunan bir dosya var.

---

## 6 · Katman denetimi

`FileRail.jsx` (denetim ve iki hâl), `App.jsx` (durum ve zorla açma), `workspace.css` (46px, döndürme,
dar pencere). Yeni bileşen yok, arka uç yok.

---

## 7 · Kabul ölçütü

1. Ray başlığı bir düğmedir ve dosya sayısını taşır.
2. Basınca ray katlanır; liste çizilmez, etiket ve sayı kalır.
3. Katlı şeride basmak geri açar.
4. Katlı hâl sohbet ve proje değiştirince korunur.
5. Bir dosya açmak rayı zorla açar.
6. Katlı ray 46px'tir ve geçiş 220ms'dir; dar pencerede dikey şerit değil tek satırdır.

## 8 · Risk

`writing-mode` ile döndürülen etiketin dikey hizası jsdom'da ölçülemiyor; kilit testi ölçüyü, Madde
35 gözü üstleniyor.
