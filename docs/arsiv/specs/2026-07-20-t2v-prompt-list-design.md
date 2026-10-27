# WAN 2.2 T2V — prompt listesi (tasarım)

**Tarih:** 2026-07-20 · **Durum:** onaylandı, uygulandı, Colab doğrulaması bekliyor

Önceki tasarımın ([2026-07-19-t2v-layered-prompts-design.md](2026-07-19-t2v-layered-prompts-design.md)) yerini alır. O spec'in **katmanlama yarısı geri alındı**, **aksiyon listesi + resume yarısı** buraya taşındı.

## Amaç

`PROMPTS` düz bir liste olsun ve her elemanı elle yazılmış, eksiksiz bir prompt olsun; notebook listeyi gezip her prompt için bir video üretsin, üretilmiş olanları atlasın.

Kullanım döngüsü: PROMPTS hücresine yeni bir prompt eklenir, render hücresi çalıştırılır — sadece eksik olanlar üretilir.

## Bağlam: katmanlama denendi ve düştü

**Bu spec'in var olma sebebi bir negatif sonuç.** Yazılmazsa aynı fikir altı ay sonra yeniden denenir.

19 Temmuz'da prompt altı alana bölünmüştü (`STYLE` / `CAMERA` / `SCENE` / `CHARACTER` / `ACTION` / `QUALITY`) ve bunlar Python'da `". "` ile birleştirilip tek `PromptGenerator` düğümüne basılıyordu. Uygulandı, **20 Temmuz'da A100'de koşuldu, çıktı kötü çıktı.**

Sebep sonradan bakınca açık: birleştirici modele şuna benzer bir metin veriyor —

```
anime style, 2D cel shading. medium shot, the camera slowly pushes in. a sunlit
bedroom with white bedsheets. a young woman with long teal hair. she slowly turns
toward the camera and smiles. highly detailed, sharp focus.
```

Bu düz cümle değil, noktayla ayrılmış bağlaçsız öbekler dizisi. WAN'ın text encoder'ı **UMT5-XXL** ve eğitim altyazıları akan, bağlaçlı betimlemeler. Yani katmanlama tam da spec'in *"WAN düz cümlelerle eğitildi"* diye savunduğu şeyi ihlal ediyordu.

Katmanlamanın zaten kalite iddiası yoktu — [önceki spec](2026-07-19-t2v-layered-prompts-design.md) bunu açıkça yazıyordu: kazanç tutarlılık, yazım kolaylığı ve tekrarlanabilirlikti. Kaliteye **zarar verdiği** anda gerekçesi tamamen düşüyor.

Kullanıcı kararı: *"tek prompt tutalım, hazırlayan ona göre düzgün hazırlasın."*

**Kayda geçen kural:** WAN'a giden metni parçalardan otomatik birleştirme. Prompt tek elden, bağlaçlarıyla birlikte yazılır.

## Kararlar

| Karar | Gerekçe |
|---|---|
| **`PROMPTS` düz liste, her eleman tam prompt** | Katman birleştirme yok. Karakter, mekân, kamera ve stil aynı metnin içinde, yazan kişinin kurduğu cümlelerle. |
| **Üç tırnaklı elemanlar, trailing comma** | Video prompt'ları çok satırlı olur ve içlerinde `"` geçer; tek tırnak ikisinde de `unterminated string literal` verir. Trailing comma diff'te tek satır ekleme sağlar. |
| **Boş eleman o numarayı atlar** | Düz listede delik açmanın tek yolu. Bir prompt'u devre dışı bırakmak için silersen altındaki bütün numaralar kayar; boşaltırsan kaymaz. Kontrol `.strip()` ile, çünkü boş bırakılmış bir `"""` bloğu newline tutar, boş string değil. |
| **Çıktı adı `NN.mp4`, 1-tabanlı iki hane** | Resume sabit ad gerektiriyor. `wan22-arbuzai` 0-tabanlı ama orada numara `input/N.*` fotoğrafıyla eşleşmek zorunda; burada eşleşecek girdi yok ve Drive'da bu adla üretilmiş videolar var. |
| **"Zaten var" kontrolü `exists` + `getsize > 0`** | Yarıda kesilmiş sıfır baytlık dosya "üretilmiş" sayılırsa o numara sonsuza kadar atlanır. `wan22-arbuzai`'den alındı. |
| **Tek sabit seed, tüm listeye** | Kullanıcı seçimi, önceki spec'ten değişmedi. Aynı liste yarın aynı videoları verir. |
| **Birleşmiş prompt'u ekrana basan kod yok** | Katmanlı sürümde modele giden metin görünmüyordu, o yüzden basılıyordu. Artık kullanıcı metni doğrudan yazıyor; basılacak gizli bir şey yok. |
| **Grafik değişmez** | Prompt yine tek `CLIPTextEncode`'u besleyen `PromptGenerator` **230:229**'a basılıyor. Düğüm yerinde kaldığı için **wildcard sözdizimi çalışmaya devam ediyor** (`{ kneeling | sitting | squatting }`). |
| **Plan tablosu yok** | `wan22-arbuzai` üretimden önce ATLA/ÜRET tablosu basıyor çünkü orada prompt'ların girdi fotoğraflarıyla yanlış eşleşme riski var. Burada eşleşecek girdi yok; döngünün satır satır çıktısı yeterli. |

## Mimari

Hücre sayısı **15**, yapı önceki spec'ten devralındı. Değişen iki hücre:

| # | Hücre | Değişim |
|---|---|---|
| 2 | **PROMPTS** | altı katman sabiti ve `build_prompt` silindi; yerine `PROMPTS` listesi + `SEED` + boşluk sayan `assert` |
| 7 | **Üret** | döngü `PROMPTS`'u tüketiyor, `build_prompt` çağrısı yok; boş eleman atlama ve `getsize > 0` eklendi |

Kurulum hücreleri (3–6: ortak yardımcılar, custom node'lar, modeller, ComfyUI başlatma) ve render altyapısı (`ComfyClient`, `load_workflow`, `set_prompt`, `set_seed`, `render`) **değişmedi**.

`wan22-arbuzai/api.ipynb` ile paylaşılan konvansiyon: düz liste, index = çıktı numarası, üç tırnak, `.strip()` tabanlı boş kontrolü, `getsize > 0` idempotans.

## Çıktı, resume, seed

**Çıktı:** `MyDrive/TextToVideo/output/NN.mp4` — `NN` listedeki 1-tabanlı sıra, iki hane sıfır dolgulu.

**Resume:** her prompt'tan önce dosya varlığına ve boyutuna bakılır; doluysa atlanır.

**Sıra kuralı:** çıktı adı index'e bağlı olduğundan listenin ortasına eleman eklemek ya da sırayı değiştirmek altındaki eşleşmeleri kaydırır. Bir numarayı kapatmanın doğru yolu prompt'u **boşaltmak**, silmek değil.

**Seed:** `SEED` tüm listeye uygulanır — hem sampler'ın `noise_seed`'ine (node `82`) hem `PromptGenerator`'ın kendi seed'ine (`230:229`).

**Ekran çıktısı** prompt başına tek satır; atlananlar da üretilenler de görünür. Çok satırlı prompt'lar ilerleme satırında tek satıra düzleştirilip 70 karaktere kırpılır — ham basılsa ilerleme log'u dağılırdı.

## Hata yönetimi

Önceki spec'ten değişmedi:

| Hata | Davranış | Gerekçe |
|---|---|---|
| **Altyapı** (`infra=True`) | Tüm koşu durur | Model bozuk/eksikse listenin tamamı aynı hataya çarpar |
| **Üretim** (`infra=False`) | Hata basılır, sıradakine geçilir | Tek bir prompt'a özgü sorun listenin kalanını çöpe atmamalı |
| **Timeout** | Tüm koşu durur | Takılmış ComfyUI kendini toparlamaz |

Başarısız prompt için dosya yazılmaz, dolayısıyla bir sonraki çalıştırmada resume onu yeniden dener.

## Kapsam dışı

- **Katman/alan sistemi** — bu spec'in tamamı onun geri alınması; yeniden önerilmeden önce yukarıdaki bulgu okunmalı
- **Video başına rastgele seed** (`SEED = None`) — `wan22-arbuzai` destekliyor, burada kapsamda değil
- **Prompt yazım yardımcıları** — `photo_generator/prompts.json`'daki gibi LLM meta-prompt'ları yok
- **Çözünürlük / süre / step kontrolü** — grafikte sabit (480×720, 6 step, cfg 1)
- **Grafik değişikliği** — `workflow_api.json`'a dokunulmuyor

## Doğrulama

Notebook'lar birim testle doğrulanmıyor; doğrulama Colab koşusudur:

1. Listeye iki tam prompt yaz → Run all → `01.mp4` ve `02.mp4` düşer. **Asıl soru: çıktı katmanlı sürümden iyi mi?**
2. Aynı hücreyi tekrar çalıştır → ikisi de "zaten var" diye atlanır
3. Üçüncü prompt'u **sona** ekle, tekrar çalıştır → sadece `03.mp4` üretilir
4. İkinci prompt'u boşalt, hücreyi çalıştır → `02` "boş — atlanıyor" der, `01` ve `03` etkilenmez
