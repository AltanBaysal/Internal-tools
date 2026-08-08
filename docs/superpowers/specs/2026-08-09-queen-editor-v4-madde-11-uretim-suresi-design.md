# Madde 11 — Üretim süresi ölçümü

**Tarih:** 2026-08-09 · **Branch:** `feat/queen-editor-v2` · **Yol haritası:**
[v4, Madde 11](../plans/2026-08-08-queen-editor-v4-roadmap.md)

---

## 1 · Neden

Hız kararları (T4 → L4 → A100, adım sayısı, FaceDetailer açık mı) bugün tahminle veriliyor. Bir
kareyi üretmenin ne kadar sürdüğü hiçbir yerde yazmıyor, dolayısıyla "A100 parayı hak ediyor mu"
sorusunun cevabı yok.

Bilerek en sona bırakıldı: asıl işini Madde 12'nin Colab turunda yapacak.

## 2 · Karar özeti

| Konu | Karar |
|---|---|
| Ne ölçülür | **Render** ve **Drive'a yazma**, ayrı ayrı |
| Nereye yazılır | Sunucunun çıktısına, yani Colab'ın açık duran hücresine — kare başına **bir satır** |
| Kim yazar | Kararı döngü verir, satırı nereye basacağını **kuruluş noktası** (`main.py`) söyler |
| Detay sayfasında | **Görünmez** — tasarımın yan sütununda süre alanı yok |
| Hatalı karede | Satır basılmaz; o karenin zaten kendi hata çıktısı var |

## 3 · İki sayı, tek satır

`⏱ 3_a.png · render 42.1 sn · drive 1.3 sn`

- **render**: üretim çağrısının başından bittiğine kadar geçen süre. GPU'nun payı budur.
- **drive**: fotoğrafın diske yazılması **ve** kaydın günlüğe düşmesi. Boru hattının payı budur.

İkisi ayrı sayılıyor ki "GPU ne kadar, boru hattı ne kadar" sorusu rakamla cevaplansın. Aynı grafı
farklı GPU'da koşunca fark **render** satırında görünür; Drive yavaşladığında ise **drive**'da.

**Sadece üretilen kare satır yazar.** Patlayan karenin kendi hata çıktısı zaten var ve ona bir de
süre eklemek, aranan sayıyı gürültüye gömer.

## 4 · Satırın yolu

Sunucu Colab'da arka planda çalışır ve çıktısı bir dosyaya akar; notebook'un son hücresi o dosyayı
canlı izler. Yani `print` yeter — ama **tamponlanmadan**: Python bir dosyaya yazarken çıktıyı
biriktirir, ve biriken satır izlenen hücrede dakikalarca görünmez. Satır anında basılır.

**Kural alan katmanında, hedef kuruluş noktasında.** Döngü "şu kare şu kadar sürdü" der; bu cümlenin
nereye gideceğini `main.py` seçer. Böylece alan katmanı hiçbir şeye yazmadan test edilebilir: testte
satırlar bir listeye toplanır ve gerçek saniye beklenmez — saat de dışarıdan verilir.

Ölçüm yoksa (kuruluş noktası bir hedef vermediyse) döngü hiçbir şey yapmaz. Ölçüm bir yan çıktıdır;
olmaması üretimi etkilemez.

## 5 · Detay sayfasında süre yok

Roadmap'in açık sorusuydu, burada kapanıyor: **görünmeyecek.**

Tasarımın çizdiği yan sütunda dört alan var — Sıra, Dosya adı, Prompt, Negatif — ve süre yok
(fark belgesi 5. bölüm). Roadmap v3 oraya koymayı istiyordu, ama v3 tasarımdan **önce** yazıldı ve
kendi Madde 1'i "tasarım kaynak, repo uygulayıcı" diyor. Aynı gerekçeyle seed alanı da yok.

Ölçümün amacı da bunu gerektirmiyor: hız kararları bir koşunun toplamına bakılarak veriliyor, tek
bir fotoğrafın kartına bakılarak değil.

## 6 · Yok

- Ortalama/özet paneli, grafik, en yavaş kare listesi.
- GPU modelinin tespiti ve satıra yazılması — Colab hücresi zaten `nvidia-smi` ile GPU'yu basıyor.
- Sürenin kayda (`photos.jsonl`) yazılması: kayıt "ne oldu" sorusunu cevaplıyor, "ne kadar sürdü"
  sorusunu değil, ve bir dosya başka bir dosyanın cevabını tekrarlamaz.
- Uç nokta, arayüz alanı, dışa aktarma alanı.

## 7 · Kabul kriterleri (testler bunları kanıtlar)

1. Üretilen her kare için tam bir satır yazılır ve satır dosya adını, render süresini ve drive
   süresini taşır.
2. Render ve drive süreleri **ayrı** ölçülür: render çağrısında geçen zaman drive'a, yazmada geçen
   zaman render'a yazılmaz.
3. Patlayan kare satır yazmaz.
4. Hedef verilmediğinde hiçbir şey yazılmaz ve üretim aynen sürer.
5. Ölçüm gerçek saatle değil, dışarıdan verilen saatle yapılır — test gerçek saniye beklemez.

## 8 · Kendi eleştirim

- **Tamponlama unutulsa madde işe yaramazdı.** Satırlar doğru basılır, dosyaya düşer, ama izlenen
  hücrede dakikalar sonra toplu görünürdü — yani "üretim sürerken hücre her kare bittiğinde bir
  satır basar" kabul kriteri sessizce karşılanmazdı. 4. bölümde açıkça yazılı.
- **`print`i alan katmanına gömmek kolaydı.** O zaman döngü test edilirken çıktı yakalamak
  gerekirdi ve hedefi değiştirmek (mesela bir dosyaya yazmak) alan katmanını değiştirmek olurdu.
  Karar döngüde, hedef kuruluş noktasında.
- **Süreyi kayda yazmak cazipti** — detay sayfasında göstermek de kolaylaşırdı. İkisi de reddedildi:
  biri "bir dosya başka bir dosyanın cevabını tekrarlamaz" kuralını çiğnerdi, diğerini tasarım
  istemiyor.
- **Hatalı kareye satır yazmamak bir kayıp mı?** Zaman aşımına takılan bir render'ın süresi
  ilginç olabilir; ama o bilgi zaten hata mesajının içinde (zaman aşımı süresi yazılı) ve maddenin
  aradığı sayı üretilen karenin süresi.
