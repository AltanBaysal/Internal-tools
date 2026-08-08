# Queen Editor — Yol Haritası v2 (KAPANDI)

**Tarih:** 2026-08-03 · **Kapanış:** 2026-08-08 · **Durum:** **Bölüm 1-14 tamamlandı**, hepsi
yazıldı ve push'landı. Bu belgede açık iş kalmadı; devam eden iş
[2026-08-08-queen-editor-v3-roadmap.md](2026-08-08-queen-editor-v3-roadmap.md)'e taşındı.

**Yerini alan doküman:** v3 yol haritası — oradaki ilk madde bu belgenin kalan Colab doğrulaması,
son maddesi ise buradaki Bölüm 15 (çoklu model).
**Şemsiye tasarım:** [2026-08-03-queen-editor-v2-design.md](../specs/2026-08-03-queen-editor-v2-design.md)
(davranış kararları) · [2026-07-24-queen-editor-v1-design.md](../specs/2026-07-24-queen-editor-v1-design.md)
(mimari kararlar)
**Tasarım kaynağı:** claude.ai/design projesi `Queen Editor` → `Queen Editor Basit v1.html` +
`HANDOFF.md`. Proje linki: <https://claude.ai/design/p/efad1f83-69d3-4e07-89fa-3783839c81c3> —
dosyalar repo'ya kopyalanmaz, her ihtiyaçta buradan taze çekilir (DesignSync `get_file`).
**Yerini aldığı doküman:** [2026-07-24-queen-editor-roadmap.md](2026-07-24-queen-editor-roadmap.md)
— oradaki Bölüm 6 buradaki Bölüm 6'ya, Bölüm 7 buradaki Bölüm 13+14'e erimişti.

---

## Tamamlanan bölümler (1-14)

| Bölüm | Görülür çıktı |
|---|---|
| 1 · Repo çekimi | Private repo token'la Colab'a klonlanır |
| 2 · Bağlantı | Sunucu + tünel; sayfa açılır, "sunucuya bağlı ✓" |
| 3 · Proje | Proje oluşturma; Drive'da klasör; kart listesi |
| 4 · Tek foto | ComfyUI ile tek prompt → tek foto |
| 5 · Çoklu foto | Prompt listesi × varyant → galeri; numaralar kaldığı yerden |
| 6 · Kalıcılık + iz | Yenileyince kutular dolu; her fotonun prompt/negatif/seed izi Drive'da |
| 7 · Arayüz: birebir + akıcı | Beş ekran tasarımla hizalandı; panel kilidi, anında Durdur, tek tip hata gösterimi |
| 8 · Frontend test altyapısı | vitest + jsdom; `api.js` ve `useGeneration` testli |
| 9 · Galeri sıralama | Sıra rozeti, sürükle-bırak, kalıcı sıra |
| 10 · Export | Tek JSON: Drive yolu + foto/prompt listesi, galeri sırasıyla |
| 11 · Foto detay | Ayrı sayfa, oranı korunan görsel, ‹ › ve klavye gezinme, tekil silme |
| 12 · Silme + onaylar | Seçim modu, toplu silme, proje silme, çıkış onayı |
| 13 · Üretim akışı | Duraklat/devam/iptal, bekliyor kareleri, format hatası |
| 14 · Sağlamlık | Tekil kare hatası + Tekrar dene, kaldığı yerden devam |

Test durumu kapanışta: backend 245, frontend 71 test yeşil. Colab doğrulaması
([2026-08-05-queen-editor-colab-dogrulama.md](2026-08-05-queen-editor-colab-dogrulama.md)) A-F ve I
maddelerinde geçti; kalan G ve H maddeleri v3 yol haritasının ilk işidir.

## Kayda değer kararlar

- **Varyant üst sınırı 26** (2026-08-04, Bölüm 13): harf tabanlı adlandırma backend gerçeği; kutu
  `max=26` ile sınırlar — HANDOFF'un "sınır yok" cümlesinden bilinçli sapma.
- **Kapsam sınırı:** video üretiminin kendisi bu yol haritasının dışındaydı, sınır Export dosyası
  (Bölüm 10). Kapsam dışı kalanlar: bağlantı çubuğu · foto sayısı / kapak · yeniden adlandırma ·
  referans görsel.

## Sıra revizyonlarının kaydı

- **2026-08-03:** Bölüm 7 olarak "Arayüz: tasarımla birebir + akıcı" eklendi, eski 7-13 birer kaydı.
  Gerekçe: Bölüm 6 Colab'da doğrulanırken arayüzün üç ayrı yerde tasarımdan saptığı ve hiçbir
  beklemenin ekranda karşılığı olmadığı görüldü.
- **2026-08-05:** Bölüm 8 olarak "Frontend test altyapısı" araya girdi, eski 8-14 birer kaydı.
  Gerekçe: Bölüm 7'nin bağlantı-kopması düzeltmesi frontend'de test edilemeden gitti; altyapı öne
  alındı ki kalan bölümler boyunca kullanılsın.
- **2026-08-05:** Bölüm 8-14 tek turda uygulandı (kullanıcı kararı: bölüm aralarında test yok, hepsi
  TDD ile yazılıp sonda toplu Colab testi yapılacak). Her bölüm kendi commit'iyle push'landı.

## Neden bu sıraydı

- **Önce zemin:** arayüz denetimi (7) sıranın başındaydı, çünkü sonraki her bölüm (rozet, seçim
  çubuğu, detay sayfası) o zeminin üstüne eleman ekliyordu.
- **Testler önde (8):** altyapı erken kuruldu ki sonraki her bölümün frontend mantığı testli gitsin.
- **Önce temel:** kalıcılık + iz (6) detay sayfasının (11) ve export'un (10) ön şartıydı; sıralama
  (9) export sırasını tanımladı.
- **Değer erken:** Bölüm 10'da video hattı beslenebilir hâle geldi — tasarımın asıl hedefi.
- **Yıkıcı işler görüntülemeden sonra:** silme (12), detay sayfasıyla (11) foto görülebilir olduktan
  sonra geldi.
- **Sağlamlık mutlu yoldan sonra:** duraklat/devam (13) oturmuş akışın üstüne, hata/devam (14) en
  sona yakın.
