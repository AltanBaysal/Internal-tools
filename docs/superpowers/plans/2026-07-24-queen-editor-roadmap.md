# Queen Editor — Yol Haritası

**Tarih:** 2026-07-24 · **Durum:** yol haritası onay bekliyor
**Şemsiye tasarım (kararların tamamı):** [2026-07-24-queen-editor-v1-design.md](../specs/2026-07-24-queen-editor-v1-design.md)

Tek kaynak: bütün bölümlerin dökümü burada. İlke **önce çalıştır, sonra sağlamlaştır** — en riskli/en belirsiz parçalar önce, tek tek kanıtlanır; her bölüm bir öncekinin üstüne birikir, hiçbirinin çıktısı çöpe gitmez. Bölümler küçük tutuldu; her biri Colab'da "evet oldu" denerek kapanır. Sırası gelen bölümün detaylı planı o an yazılır.

Her bölüm çıktı odaklı: **ne çalışır** + **nasıl görülür**. Kod/dosya değil, gözlemlenebilir sonuç.

---

## Bölüm 1 — Repo çekimi

En riskli bilinmeyen tek başına: private repo + token ile klon Colab'da çalışıyor mu.

- **Ne çalışır:** minik notebook Run all → repo `/content`'e iner.
- **Nasıl görülür:** hücre çıktısında `queen-editor/` dosyaları listelenir. Token **ekrana basılmaz**.
- **Yok:** sunucu, site, tarayıcı, Drive, ComfyUI.

## Bölüm 2 — Bağlantı (backend ↔ frontend)

Arayüz derleniyor mu, tünel açılıyor mu, ve sayfa sunucuya gerçekten **konuşuyor mu**.

- **Ne çalışır:** notebook repoyu çeker → arayüzü derler → sunucu servis eder → tünel linki basar. Sayfa açılınca sunucuya bir istek atıp cevabı gösterir.
- **Nasıl görülür:** linke gir → koyu temalı sayfa, üstünde sunucudan gelen işaret ("sunucuya bağlı ✓"). Scroll/tıklama akıcı, donma yok.
- **Yok:** Drive, proje, gerçek özellik. Tek "Queen Editor" başlığı + bağlantı kanıtı.

## Bölüm 3 — Proje

İlk gerçek özellik: Drive'a yazıp okumak. Proje = Drive klasörü.

- **Ne çalışır:** "Yeni proje" → ad gir → `photoGenV2/<ad>/` klasörü oluşur → kart listede belirir.
- **Nasıl görülür:** kart ekranda; Drive'da klasör; aynı ad / geçersiz karakter → kırmızı uyarı; sayfa yenile → projeler duruyor.
- **Yok:** proje ekranı (kart tıklanamaz), ayar/prompt kaydı.

## Bölüm 4 — Tek foto

ComfyUI devreye girer: tek prompt → tek foto. En küçük gerçek üretim.

- **Ne çalışır:** projeyi aç → tek prompt kutusu + Üret → ComfyUI çalışır → bir foto Drive'a düşer, ekranda görünür.
- **Nasıl görülür:** Üret'e bas → biraz sonra bir foto beliriyor; Drive'da o dosya var.
- **Kanıtladığı:** modeller iner, ComfyUI kalkar, grafiğe prompt/seed enjekte edilir, foto Drive→tarayıcı döner.
- **Yok:** varyant, liste, galeri ızgarası, hata kartı, prompt kaydı.

## Bölüm 5 — Çoklu foto (tam ekran, mutlu yol)

Tasarımın asıl proje ekranı: solda prompt **listesi** (Python list) + negatif + varyant + Üret, sağda 5 sütunlu galeri, en yeni üstte, foto tıklanınca yeni sekme.

- **Ne çalışır:** listeyi yapıştır, varyant seç, Üret → 12×4 = 48 foto galeride belirir.
- **Nasıl görülür:** galeri dolar; foto tıkla → yeni sekme; tekrar Üret → numaralar sona eklenir, üstüne yazma yok.
- **Yok (bilinçli, sonraki bölümlere):** hata yönetimi, prompt kaydı, devam etme.

## Bölüm 6 — Promptla eşleştirme (kalıcılık + iz)

Prompt'lar ve foto↔prompt ilişkisi Drive'a yazılır.

- **Ne çalışır:** prompt/negatif/varyant `prompts.json`'a kaydedilir; her foto hangi prompt'tan üretildi `runs.json`'da tutulur.
- **Nasıl görülür:** projeyi başka sekmede/cihazda aç → prompt'lar dolu geliyor; sayfa yenile → prompt kutusu boşalmıyor; bir fotonun hangi prompt'tan geldiği bulunabiliyor.
- **Yok:** hata kartları, devam etme (Bölüm 7).

## Bölüm 7 — Sağlamlık (hata + devam)

Mutlu yolu üretime hazırlar. Yeni ekran yok; altına dayanıklılık girer.

- **Ne çalışır:** tekil kare atlanır; altyapı hatası veya üst üste 3 hata durdurur; **Tekrar dene** patlayan kareyi aynı adla yeni seed'le üretir; **Kaldığı yerden devam et** tünel kopsa/sekme kapansa/Colab oturumu ölse bile eksik kareleri baştan üretmeden sürdürür.
- **Nasıl görülür:** ComfyUI'ı öldür → hata kartı (artboard 05/06); runtime'ı yeniden başlat → devam kartı, yalnız eksikler üretilir.
- **Kanıtladığı:** v1'in tam hâli — şemsiye spec'teki her davranış.

---

## Sıra özeti

| Bölüm | Görülür çıktı | Yeni risk kanıtı |
|---|---|---|
| 1 · Repo çekimi | Colab'da repo dosyaları | private klon + token |
| 2 · Bağlantı | Sayfa açılır, "sunucuya bağlı ✓" | derleme · tünel · front↔back · akıcılık |
| 3 · Proje | Proje oluştur, Drive'da klasör | Drive yaz/oku |
| 4 · Tek foto | Bir foto üretilir, görünür | ComfyUI + enjeksiyon |
| 5 · Çoklu foto | 48 foto, tam ekran + galeri | toplu üretim + numaralandırma |
| 6 · Eşleştirme | Prompt kaydı + foto↔prompt izi | Drive kalıcılık |
| 7 · Sağlamlık | Hata kartı + kaldığı yerden devam | dayanıklılık |

## Neden bu sıra

- **En riskli önce:** klon (1), bağlantı (2), ComfyUI (4) — her biri üstüne özellik binmeden, tek değişkenle kanıtlanır.
- **Değer erken:** Bölüm 4'te gerçek foto, Bölüm 5'te asıl ekran elinde.
- **Zor iş sonda:** kalıcılık (6) ve hata/devam (7) en az "görünür", en çok uğraştıran kısım; mutlu yol kanıtlandıktan sonra gelir.
- **Her bölüm bağımsız denenir:** Colab'da aç, gözünle gör, "devam" de.

## İki bilinçli bedel (Bölüm 5 sonunda, Bölüm 6-7'ye kadar)

1. **Sayfa yenilenince prompt kutusu boşalır** (fotolar Drive'da kalır). Bölüm 6 çözer.
2. **ComfyUI takılırsa ekran "donmuş" görünebilir** — hata kartı Bölüm 7'de. Bölüm 5'te mutlu yol test edilir.

## Sıradaki adım

Yol haritası onaylanınca **Bölüm 1** (repo çekimi) için detaylı planı yazıp başlarım.
