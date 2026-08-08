# Queen Editor — Yol Haritası v3

**Tarih:** 2026-08-08 · **Branch:** `feat/queen-editor-v1` · **Durum:** açık — tek aktif yol haritası
**Yerini aldığı doküman:** [2026-08-03-queen-editor-v2-roadmap.md](2026-08-03-queen-editor-v2-roadmap.md)
— Bölüm 1-14 orada tamamlandı ve kapandı; o belgeden kalan iki iş (Colab doğrulamasının G/H
maddeleri ve çoklu model) buraya taşındı.
**Şemsiye tasarım:** [2026-08-03-queen-editor-v2-design.md](../specs/2026-08-03-queen-editor-v2-design.md)
(davranış) · [2026-07-24-queen-editor-v1-design.md](../specs/2026-07-24-queen-editor-v1-design.md)
(mimari) — üretim akışıyla ilgili kararları bu yol haritasının Madde 2-6'sı günceller.

**Kapsam sınırı (değişmedi):** video üretiminin kendisi kapsam dışı, sınır Export dosyası. Kapsam
dışı kalanlar: bağlantı çubuğu · foto sayısı / kapak · yeniden adlandırma · referans görsel.

İlke aynı: her madde çıktı odaklı (**ne çalışır** + **nasıl görülür**), bir öncekinin üstüne birikir
ve Colab'da tek başına "evet oldu" denerek kapanır.

---

## Bu yol haritasının çekirdeği: canlı kuyruk

Madde 2-6 tek bir karardan doğuyor: **üretim tek seferlik bir iş olmaktan çıkıp sürekli açık bir
kuyruk olur.** v2, üretimi "başlat / durdur / devam et"li bir iş sayıyordu; Bölüm 13'ün paneli de o
varsayımın üstüne kuruldu. Karar 2026-08-08'de değişti: panelin işi artık kuyruğa iş atmaktan ibaret.

| v2'de (bugün çalışan hâli) | Bu yol haritasından sonra |
|---|---|
| **Üret** → kuyruk donar, panel kilitlenir | **Sıraya ekle** → kareler kuyruğun sonuna eklenir, panel açık kalır |
| Üretim sürerken yeni iş eklenemez | Sürerken eklenir, kesinti olmaz |
| **Durdur / Devam et / İptal et** | Yok — kuyruktan çıkarmanın tek yolu bekleyen kartı silmek |
| Bekleyen kare sadece görsel yer tutucu | Bekleyen kare **açılabilir kart**: prompt, negatif, seed |
| Yeni fotoğraf galerinin **en üstüne** düşer | Bekleyen kart **kendi yerinde** fotoğrafa dönüşür |
| Yarım iş → elle "Kaldığı yerden devam et" | Kuyrukta iş varsa kendiliğinden sürer; elle kart yalnız ölümcül hatada |

Bölüm 13-14'ün kodu çöpe gitmiyor: kuyruğun Drive'da kalıcı oluşu (`plan.json`), bekleyen kareler,
tekil kare hatası ve **Tekrar dene** aynen taşınıyor. Kalkan tek şey duraklat/devam/iptal paneli.

**Teknik dayanak.** Zemin hazır: `plan.json` zaten kuyruk ve Drive'da duruyor, `get_queue` "plan
eksi kayıt" diyor. Değişen iki şey var:

1. **Plan değiştirilebilir olur** — bugün her batch'te baştan yazılıyor
   ([plan_store.py](../../../queen-editor/backend/features/photo_generation/data/plan_store.py));
   sonuna ekleme ve bekleyen kareyi çıkarma gelir.
2. **Döngü planı okur** — bugün `run_loop` başlangıçta verilen dondurulmuş `frames` listesini geziyor
   ([run_loop.py](../../../queen-editor/backend/features/photo_generation/domain/run_loop.py)); her
   turda plandan "sıradaki bekleyen"i alacak hâle gelir.

Bekleyen karenin dosya adı planlandığı anda belli (`<numara>_<harf>.png`), bu yüzden `order.json`'da
yerini baştan alabilir — kare üretilince satır aynı yerde kalır, sıra hiç oynamaz. "Yerinde
fotoğrafa dönüşme" bu sayede ayrı bir mekanizma istemiyor.

---

## Madde 1 — Tasarım (claude.ai/design)

Kod yazılmadan önce ekranların tasarımı: v2'de olduğu gibi tasarım projesi kaynak, repo uygulayıcı.

- **Ne çalışır:** claude.ai/design'daki `Queen Editor` projesinde yeni akışın ekranları tasarlanır —
  **Sıraya ekle** paneli (üç buton yerine tek buton, kilitsiz hâli), galerideki **bekleyen kart**,
  bekleyen kartın **detay sayfası** (görsel yerine "bekliyor" alanı; prompt, negatif, seed) ve
  bekleyen kartın silme etkileşimi. `HANDOFF.md` bu kararlarla güncellenir — davranış kararlarının
  tek yeri orası. **Bitiş kartı** açık sorusu burada karara bağlanır.
- **Nasıl görülür:** tasarım projesinde yeni ekranlar duruyor ve DesignSync ile çekilebiliyor;
  Madde 2-6 artık "tasarımda ne varsa o" diyerek yazılabiliyor. Dosyalar repo'ya kopyalanmaz.
- **Yok:** kod dokunuşu; yeni ekran icadı (galeri, panel ve detay sayfası zaten var — değişen
  içerikleri).

## Madde 2 — Kuyruk canlı olur (backend)

Zemin: kuyruk dondurulmuş liste olmaktan çıkar, üstüne yazılabilen bir sıra olur.

- **Ne çalışır:** plana sonuna ekleme ve bekleyen kareyi çıkarma; döngü her turda plandan sıradaki
  bekleyeni alır; kuyruk boş değilse üretim kendiliğinden başlar, boşalınca kendiliğinden durur.
  Numara ayırma kuralı aynı — silinen bekleyenin numarası boşta kalır, geri kullanılmaz.
- **Nasıl görülür:** üretim sürerken ikinci bir istek at → kesinti olmadan arkaya dizilir; `pytest`
  yeşil (yeni testler: çalışırken ekleme, bekleyeni çıkarma, boşalınca durma).
- **Yok:** arayüz dokunuşu; çalışan kareyi kesme.

## Madde 3 — Panel sadeleşir: Sıraya ekle

Üç butonlu üretim paneli tek butona iner.

- **Ne çalışır:** **Üret** → **Sıraya ekle**; Durdur / Devam et / İptal et kalkar; üretim sürerken
  panel alanlarının kilidi (`wf-panel--locked`) kalkar — çalışırken prompt yazıp eklemek normal
  davranış. Format kontrolü ve boş listede pasif buton aynen kalır.
- **Nasıl görülür:** üretim sürerken prompt yaz → Sıraya ekle basılabilir; kareler sıranın sonunda
  belirir, çalışan kare kesilmez.
- **Yok:** bekleyen kartın açılması (Madde 4), silinmesi (Madde 5).

## Madde 4 — Bekleyen kare bir kart olur

Kuyruktaki iş görünür ve incelenebilir hâle gelir.

- **Ne çalışır:** bekleyen kare galeride **kendi sırasında** durur (kesikli "bekliyor" görünümü
  korunur) ve **açılabilir** — foto detay sayfasının bekleyen sürümü: prompt, negatif, seed,
  planlanan dosya adı, görsel yerine "bekliyor" alanı. Kare üretilince **aynı slotta** fotoğrafa
  dönüşür; "yeni fotoğraflar en üste düşer" kuralı kalkar.
- **Nasıl görülür:** sıraya 5 kare ekle → beşi de galerinin sonunda kart olarak durur; birini aç →
  promptunu gör; üretim ilerledikçe kartlar tek tek yerlerinde fotoğrafa döner, sıra oynamaz.
- **Yok:** bekleyen kareyi sürükleyerek öncelik değiştirme — sırayı kuyruğa ekleme sırası belirler.

## Madde 5 — Bekleyen kartı silme

Kuyruktan çıkarmanın tek yolu.

- **Ne çalışır:** bekleyen kart silinir → sırası gelince üretilmez, numarası boşta kalır. O an
  render edilen kare silinemez: sırası gelen kart "çalışıyor"a döner ve silme kapanır. Silme hem
  kartın kendi sayfasından hem galeriden (seçim modu) çalışır.
- **Nasıl görülür:** 5 karelik kuyruğun 4.'sünü sil → 3 ve 5 üretilir, 4 hiç üretilmez; çalışan
  karede silme yok.
- **Yok:** çalışan kareyi iptal etme.

## Madde 6 — Otomatik devam ve hata

Kuyruk açık kaldığı için "devam" çoğu durumda kendiliğinden olur.

- **Ne çalışır:** proje yeniden açıldığında kuyrukta iş varsa üretim kendiliğinden sürer — Bölüm
  14'ün elle **Kaldığı yerden devam et** kartı yalnızca **ölümcül hatadan sonra** kalır (otomatik
  devam olsaydı hata döngüye girerdi). Tekil kare hatası ve **Tekrar dene** aynen kalır.
- **Nasıl görülür:** üretim sürerken sekmeyi kapat, projeyi yeniden aç → kuyruk kaldığı yerden
  akmaya devam eder, kart çıkmaz; ComfyUI'ı öldür → kırmızı "Üretim durdu" kartı + elle devam.

## Madde 7 — Çoklu model

v2'den devreden bağımsız en büyük iş; hiçbir madde buna bağımlı değil, istenirse öne çekilebilir.

- **Ne çalışır:** paneldeki **Model** dropdown'ı gerçek seçim yapar — birden fazla model kurulur,
  seçilen modelle üretilir; seçim projeyle kaydedilir. Hangi modellerin ekleneceği bu maddenin ilk
  kararı.
- **Nasıl görülür:** modeli değiştir, üret → görünür şekilde farklı sonuç; projeyi yeniden aç →
  seçim durur.

## Madde 8 — Üretim süresi ölçümü

Küçük iş, bilerek sonda: hız kararlarının (T4 → L4 → A100, adım sayısı, FaceDetailer) tahminle
değil ölçümle verilmesi için. Bugün bir karenin kaç saniye sürdüğünü söyleyen tek kaynak
[config.py](../../../queen-editor/backend/config.py)'deki "~1 dk" yorumu.

- **Ne çalışır:** her kare için geçen süre ölçülür ve iki yerde görünür — **Colab hücre çıktısında**
  satır satır (`3_a.png — 62 sn`) ve fotoğrafın **kaydında** (`photos.jsonl` satırına süre alanı),
  oradan da foto detay sayfasında. Süre, render'ın kendisini kapsar; Drive'a yazma ayrı sayılır ki
  "GPU ne kadar, boru hattı ne kadar" ayrımı görülebilsin.
- **Nasıl görülür:** üretim sürerken Colab hücresi her kare bittiğinde bir satır basar; bir fotoğrafı
  aç → kaç saniyede üretildiği yazıyor. GPU'yu değiştirip aynı grafı koşunca fark rakamla görünür.
- **Yok:** ortalama/özet paneli, grafik, GPU model tespiti — tek satır ölçüm yeter.

## Madde 9 — Colab doğrulaması (toplu)

En sonda, tek dalgada: hem v2'den devreden maddeler hem bu yol haritasının getirdikleri aynı turda
denenir — kuyruk davranışı yolun ortasında değiştiği için erken test iki kere yapılırdı.

- **Ne çalışır:** [doğrulama listesinden](2026-08-05-queen-editor-colab-dogrulama.md) devreden
  **G3** (üst üste hata → kırmızı "Üretim durdu" kartı + sunucunun teknik satırı), **G4** (tekil
  kare patlarsa kırmızı kare + Tekrar dene, üretim sürer), **H1-H2** (runtime ölünce ilerleme
  soluklaşır + "Sunucuya ulaşılamıyor" kartı, runtime dönünce toparlanır); üstüne canlı kuyruğun
  kendi listesi: çalışırken sıraya ekleme, bekleyen kartın açılması, bekleyeni silme, otomatik devam
  (G1-G2'nin yerini alan hâli).
- **Nasıl görülür:** ComfyUI öldürülür → kart çıkar; runtime kapatılır → ~12 sn içinde bağlantı
  kartı; kuyruğa iş atılır, biri silinir, sekme kapatılıp açılır → kuyruk kaldığı yerden akar.
- **Yok:** **F2-F5** (Durdur / Devam et / İptal et) — Madde 3'te tamamen kalktı, test edilecek bir
  şey yok.

---

## Sıra özeti

| Madde | Görülür çıktı | Yeni kazanım |
|---|---|---|
| 1 · Tasarım (claude.ai/design) | Yeni panel, bekleyen kart ve detayı tasarımda | uygulama tasarıma bakarak yazılır |
| 2 · Kuyruk canlı olur | Çalışırken eklenen iş arkaya dizilir | kuyruk dondurulmuş liste olmaktan çıkar |
| 3 · Panel sadeleşir | Tek buton: Sıraya ekle | üretim sürerken panel açık |
| 4 · Bekleyen kare kart olur | Açılabilir "bekliyor" kartı | kuyruktaki iş görünür, sıra oynamaz |
| 5 · Bekleyen kartı silme | Silinen kare üretilmez | iptalin yerini alan tek hareket |
| 6 · Otomatik devam ve hata | Proje açılınca kuyruk akar | elle devam yalnız gerçek hatada |
| 7 · Çoklu model | Model seçimi | içerik çeşitliliği |
| 8 · Üretim süresi ölçümü | Colab log'unda ve foto kaydında saniye | hız kararları ölçümle verilir |
| 9 · Colab doğrulaması | Devreden G/H + kuyruğun kendi listesi | tek dalgada topluca kanıtlanır |

## Neden bu sıra

- **Tasarım önce (1):** v2'nin dersi — arayüz tasarımdan sapınca üstüne eklenen her eleman sapmayı
  büyüttü ve iki kere düzeltildi (v2 Bölüm 7 bu yüzden vardı). Panel, kart ve detay sayfası önce
  tasarımda netleşir.
- **Önce backend (2):** kuyruk canlı olmadan panelin tek butona inmesi yalan olur — buton basılır
  ama iş arkaya dizilemez.
- **Panel karttan önce (3):** bekleyen kartın anlamı "kuyruktaki iş"; kuyruğa iş atmanın yolu önce
  çalışmalı.
- **Silme karttan sonra (5):** silinecek şey önce ekranda bir kart olarak var olmalı.
- **Hata sonda (6):** otomatik devamın nerede durması gerektiği, ancak kuyruk sürekli akar hâle
  geldikten sonra doğru kurulur.
- **Çoklu model sonda (7):** bağımsız ve en büyük iş; sıra onu beklemez, istenirse öne alınır.
- **Süre ölçümü sonda (8):** hiçbir madde ona bağlı değil ve asıl işi doğrulama turunda başlar —
  GPU/ayar değişikliklerinin karşılığını rakamla görmek.
- **Doğrulama en sonda (9):** kuyruk davranışı yolun ortasında değiştiği için erken Colab testi iki
  kere yapılırdı — devreden G/H maddeleri de yeni akışla birlikte tek dalgada denenir. Madde 8'in
  ölçümü bu turda ilk gerçek verisini verir.

## Açık sorular (ilgili maddenin planında karara bağlanır)

- **Bitiş kartı** (Madde 1, tasarımda): kuyruk boşalınca yeşil "✓ N / M üretildi — tamamlandı" kartı
  kalsın mı, yoksa kuyruk sürekli açık olduğu için sessizce mi bitsin?
- **Model listesi** (Madde 7): hangi modeller kurulacak.

## Sıradaki adım

**Madde 1** — claude.ai/design'da yeni ekranların tasarımı + `HANDOFF.md` güncellemesi. Ardından
Madde 2'nin tasarım dokümanı (spec) → uygulama planı → TDD ile uygulama.
