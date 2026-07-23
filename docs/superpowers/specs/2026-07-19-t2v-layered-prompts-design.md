# WAN 2.2 T2V — Katmanlı prompt + aksiyon listesi (tasarım)

**Tarih:** 2026-07-19 · **Durum:** ⛔ **katmanlama geri alındı** — aksiyon listesi + resume ayakta

> **Sonuç (2026-07-20).** Bu tasarım uygulandı ve A100'de koşuldu. **Katmanlama başarısız: çıktı kötü çıktı.** Alanları `". "` ile birleştirmek modele bağlaçsız öbekler dizisi veriyor, oysa WAN'ın UMT5 encoder'ı akan cümlelerle eğitildi — yani katmanlama, bu spec'in kendi savunduğu ilkeyi ihlal ediyordu. Katmanlamanın zaten kalite iddiası yoktu (bkz. *"Katmanlama kaliteyi artırmaz"*), o yüzden kaliteye zarar verdiği anda gerekçesi tamamen düştü.
>
> **Ayakta kalan yarı:** aksiyon listesi, `NN.mp4` çıktı adlandırması, resume ve hata politikası. Bunlar katmanlamadan bağımsızdı ve korundu.
>
> Yürürlükteki tasarım: **[2026-07-20-t2v-prompt-list-design.md](2026-07-20-t2v-prompt-list-design.md)**. Aşağısı ne denendiği ve neden bırakıldığının kaydıdır; uygulama rehberi olarak okuma.

## Amaç

Stili, kamerayı, mekânı, karakteri ve kaliteyi **bir kez** tanımlayıp bir aksiyon listesi vermek; notebook listeyi gezip her aksiyon için bir video üretsin, üretilmiş olanları atlasın.

Kullanım döngüsü: PROMPTS hücresinde `STYLE` / `CAMERA` / `SCENE` / `CHARACTER` / `QUALITY` sabit durur, `ACTIONS` listesine yeni satır eklenir, render hücresi çalıştırılır — sadece eksik olanlar üretilir.

## Bağlam

### Teknik nereden geliyor

[`collab-toolbox/photo_generator/`](../../../collab-toolbox/photo_generator/) SDXL tarafında prompt'u dört katmana bölüyor: kalite, karakter, aksiyon, arka plan. Dördü ayrı `CLIPTextEncode`'dan geçip `ConditioningConcat` zinciriyle birleşiyor.

### Neden aynen taşınmıyor

SDXL'de bu ayrımın somut bir gerekçesi var: **CLIP'in 77-token penceresi.** Dört katmanı tek metinde birleştirince sondaki tag'ler kırpılıyor; ayrı encode edilince her katman kendi penceresini alıyor.

WAN'da bu gerekçe yok. Text encoder **UMT5-XXL** (`workflow_api.json`, node `38`: `clip_name: umt5_xxl_fp8_e4m3fn_scaled.safetensors`, `type: "wan"`) — T5 türevi, uzun bağlam alır. Üstelik WAN virgüllü tag listeleriyle değil **düz cümlelerle** eğitildi; grafiğin kendi negatif prompt'u (node `7`) uzun bir Çince cümle listesi.

Ayrı encode edilmiş T5 embedding'lerini `ConditioningConcat` ile birleştirmek, modelin eğitimde görmediği bir girdi biçimi üretir. SDXL'de kazanç olan şey burada risk.

**Sonuç: birleştirme Python'da string düzeyinde yapılır, grafiğe dokunulmaz.**

### Katmanlama kaliteyi artırmaz

Bu tasarımın hedefi çıktı kalitesi **değil**. Python'da birleştirilen metin, kullanıcının elle yazacağı metinle birebir aynıdır — model aradaki farkı görmez. Kazanç üç yerde:

1. **Tutarlılık** — karakter ve mekân tanımı tek yerde, her aksiyonda aynı.
2. **Yazım kolaylığı** — uzun prompt tek blok yerine dört alanda düzenlenir.
3. **Tekrarlanabilirlik** — sabit seed + sabit katmanlar, aynı liste aynı videoları verir.

Bu beklenti spec'e yazıldı ki "katmanladık ama video daha iyi olmadı" sürprizi doğmasın.

## Önceki spec'ten dönüşler

[`2026-07-18-t2v-api-design.md`](2026-07-18-t2v-api-design.md) iki kararı bu tasarımla değişiyor. Kullanıcı ikisini de açıkça onayladı:

| Eski karar | Yeni karar | Gerekçe |
|---|---|---|
| **Batch değil**, her run tek video | Aksiyon listesi → N video | Karakter/mekân/kamera sabitken tek tek çalıştırmak anlamsız. Kullanıcı: *"birden fazla aksiyon üreteceğim zaman tekrardan karakter define etmek, odayı, kamerayı define etmek pek mantıklı olmazdı."* Eski karar bilinçli bir sadeleştirmeydi: *"tek seferde basit bir şey yapman ve karmaşayı artırmaman."* |
| Çıktı adı **zaman damgası** | Çıktı adı **liste index'i** (`01.mp4`) | Resume sabit ad gerektirir; zaman damgası her koşuda değişir, "zaten üretilmiş mi" sorusu cevaplanamaz. |

## Kararlar

| Karar | Gerekçe |
|---|---|
| **Grafik değişmez** | UMT5 tek `CLIPTextEncode`'dan beslenmeye devam eder. `manual.ipynb` ile `api.ipynb` aynı grafı paylaşır, node id'leri kaymaz, UI'da açınca hiçbir şey değişmemiştir. |
| **Yeni notebook yok, `api.ipynb` evrilir** | Tek elemanlı liste zaten bugünkü "tek video" davranışıdır. Ayrı bir batch notebook'u, aynı kurulumun (16 custom node, ~33.5 GiB model, ComfyUI başlatma) ikinci kopyasını bakımda tutmak demektir. |
| **PROMPTS ayrı hücre** | Teknik ayar (mount, cookie, yollar, timeout) ile sürekli düzenlenen içerik aynı hücrede karışır. `photo_generator` da aynı ayrımı yapıyor: *1) CONFIG* / *2) PROMPTS*. |
| **Altı katman: `STYLE` · `CAMERA` · `SCENE` · `CHARACTER` · `ACTION` · `QUALITY`** | Kamera ayrı, çünkü videoda kamera hareketi zamanla değişen bağımsız bir eksen ("kamera yavaşça yaklaşır"), fotoğraftaki gibi sadece bir açı değil. Kullanıcı ayrı kalmasını istedi. Sıra da kullanıcı seçimi. |
| **`STYLE` ve `QUALITY` var** (2026-07-20'de eklendi) | İlk tasarımda ikisi de elenmişti: *"SmoothMix kendi estetiğini getiriyor; WAN'da kalite tag'leri SDXL'deki kadar iş görmüyor. Sabit bir stil cümlesi `SCENE` içine yazılabilir. YAGNI."* Kullanım bu varsayımı çürüttü — **SmoothMix kendi görünüşünü sanıldığı kadar dayatmıyor**, dolayısıyla stil kontrol edilebilir bir eksen olmalı. "`SCENE` içine yaz" çözümü de mekân ile görünümü aynı alanda birleştiriyordu: aynı odayı başka bir görünümle denemek `SCENE`'i baştan yazmayı gerektiriyordu. `QUALITY`, `photo_generator`'daki aynı adlı katmanın rolünü üstlenir. Elenme gerekçesinin **hâlâ geçerli olan kısmı**: UMT5 Danbooru tag'lerine CLIP kadar tepki vermiyor, o yüzden iki katman da betimleyici öbeklerle yazılır, `masterpiece, best quality, 8k` ile değil. |
| **Katmanlar CONFIG'de değil, notebook'ta (Drive JSON yok)** | Kullanıcı notebook'un kendi Colab kopyasını kullanıyor ve listeye zaman içinde ekliyor. Ayrı bir `prompts.json` fazladan yönetilecek bir dosya olurdu. |
| **Tek sabit seed, tüm listeye** | Kullanıcı seçimi. Aynı liste yarın aynı videoları verir; aksiyonlar aynı gürültüden başladığı için görsel his de birbirine yakın durur. |
| **Bayatlık kontrolü yok** | Sidecar prompt dosyası, hash karşılaştırması yok. Kullanıcı: *"bayat çıktılar sorun değil, o kullananın görevi kontrol etmek."* Döngü ne ürettiğini ve ne atladığını satır satır bastığı için durum ekranda görünür. |

## Mimari

Hücre sayısı 6 → 7:

| # | Hücre | Değişim |
|---|---|---|
| 1 | CONFIG | `PROMPT` değişkeni **ve onu kontrol eden `assert PROMPT.strip()`** buradan çıkar; Drive mount, cookie, yollar, timeout aynı kalır |
| 2 | **PROMPTS** | **yeni** — katmanlar + `ACTIONS` + `SEED` |
| 3 | Ortak yardımcılar | değişmez |
| 4 | ComfyUI + custom node'lar (16) | değişmez |
| 5 | Modeller (~33.5 GiB) | değişmez |
| 6 | ComfyUI'yi başlat | değişmez |
| 7 | Üret | tek üretim → döngü |

Kurulum tarafına (3–6) hiç dokunulmaz; o zincir Colab'da A100 ile doğrulandı.

`CLAUDE.md`'deki tablo satırı güncellenir: "prompt in CONFIG, one per run" artık doğru değil.

## Katmanlar ve birleştirme

PROMPTS hücresinin şekli:

```python
# Nasıl görünüyor — sabit, animasyon/film tarzı. Boş bırakılabilir.
STYLE = "anime style, 2D cel shading, clean linework"

# Kamera — sabit, kadraj + hareket
CAMERA = "medium shot, the camera slowly pushes in, shallow depth of field"

# Nerede — sabit, mekân + ışık + atmosfer
SCENE = "a sunlit bedroom with white wrinkled bedsheets and pink curtains, golden hour light streaming through a large window, warm cozy atmosphere"

# Kim — sabit, karakter kimliği
CHARACTER = "a young woman with long teal hair in twintails, green eyes, fair skin"

# Ne oluyor — değişen tek şey. SONA EKLE.
ACTIONS = [
    "she slowly turns toward the camera and smiles",
    "she sits on the edge of the bed and looks out the window",
]

# Kalite — sabit. Boş bırakılabilir.
QUALITY = "highly detailed, sharp focus, smooth natural motion"

SEED = 42
```

Değişkenler **birleşme sırasında** tanımlanır, dolayısıyla hücreyi yukarıdan aşağı okumak modele giden metni okumakla aynı şeydir.

Hücre çalıştığında **ilk aksiyonla birleşmiş prompt'u ekrana basar.** Katmanları düzenlerken modele gidecek metnin tamamı anında görünür; noktalama ve boşluk hataları render beklemeden fark edilir. Ayrıca `ACTIONS` boşsa `assert` ile durur — üretecek bir şey olmadan render hücresine geçilmez.

**Birleştirme sırası:** `STYLE. CAMERA. SCENE. CHARACTER. ACTION. QUALITY.`

Sıra kullanıcı seçimi: stil en başta çünkü çerçeveyi baştan kuruyor, kalite en sonda. `photo_generator` da aynı iskeleti kullanıyor — `workflow.json`'daki `ConditioningConcat` zinciri `QUALITY → +CHARACTER → +ACTION → +BACKGROUND` diye ilerliyor, yani kalite/stil ekseni zincirin başında. **Doğrulanmadı.** Değiştirmesi `build_prompt` içindeki tek demet satırı.

Birleştirici iki normalizasyon yapar, ikisi de sessiz bozulmayı engellemek için:

- **Sondaki noktalama ve boşluk kırpılır**, sonra `. ` ile eklenir. Katmanın sonuna nokta konsa da konmasa da çıktı aynıdır; `..` oluşmaz.
- **Boş katman atlanır.** `STYLE = ""` bırakılırsa metin baştan `. ` ile başlamaz, `QUALITY = ""` sonda `. .` bırakmaz.

Birleşmiş metin bugünkü gibi `PromptGenerator` (`230:229`) düğümünün `prompt` girdisine basılır. Düğüm yerinde kaldığı için **wildcard sözdizimi çalışmaya devam eder** — aksiyon içinde `{ kneeling | sitting | squatting }` yazılabilir. Seed sabit olduğundan seçimler her koşuda aynı çıkar, tekrarlanabilirlik bozulmaz.

**Negatif prompt'a dokunulmaz.** Grafikteki node `7` SmoothMix yazarının Çince negatif listesini taşır; katman sistemi yalnızca pozitif tarafı ilgilendirir.

## Çıktı, resume, seed

**Çıktı:** `MyDrive/TextToVideo/output/NN.mp4` — `NN` listedeki 1-tabanlı sıra, iki hane sıfır dolgulu (`01.mp4`, `02.mp4`, …).

**Resume:** her aksiyondan önce dosya varlığına bakılır; varsa atlanır. Kontrol **yalnızca varlığa** bakar, içeriğe değil.

**Sıra kuralı — listeye sondan ekle.** Çıktı adı liste index'ine bağlı olduğu için, listenin ortasına eleman eklemek veya sırayı değiştirmek altındaki tüm eşleşmeleri kaydırır: `05.mp4` artık başka bir aksiyona aittir ama dosya var diye atlanır. Yeniden sıralama gerekiyorsa etkilenen çıktılar Drive'dan silinmelidir. Bu uyarı notebook'un markdown hücresinde de yer alır.

**Seed:** `SEED` tüm listeye uygulanır — hem sampler'ın `noise_seed`'ine (node `82`) hem `PromptGenerator`'ın kendi seed'ine (`230:229`), bugünkü `set_seed` davranışıyla aynı.

**Ekran çıktısı** her aksiyon için tek satır; atlananlar da üretilenler de görünür:

```
[3/13] ⏭️  03.mp4 zaten var — atlanıyor
[4/13] Üretiliyor: she sits on the edge of the bed and looks out…
        ✓ 04.mp4  (4 dk 12 sn, 8.3 MB)
```

Sonda özet: kaç yeni üretildi, kaç atlandı, kaç başarısız — ve başarısız olanların index'leri tek tek.

## Hata yönetimi

`api.ipynb`'de `describe_comfy_error` hatanın altyapısal olup olmadığını zaten hesaplıyor (`infra=True` ⟺ patlayan düğüm bir model loader). Tek üretimde bu bilgi kullanılmıyordu; döngüde anlam kazanıyor:

| Hata | Davranış | Gerekçe |
|---|---|---|
| **Altyapı** (`infra=True`) | Tüm koşu durur | Model bozuk/eksikse listenin tamamı aynı hataya çarpar; 12 kere daha denemenin faydası yok |
| **Üretim** (`infra=False`) | Hata basılır, sıradaki aksiyona geçilir | Tek bir prompt'a özgü sorun listenin kalanını çöpe atmamalı |
| **Timeout** | Tüm koşu durur | Takılmış ComfyUI kendini toparlamaz; sonraki her aksiyon 30 dakika daha bekleyip aynı yere düşer |

Başarısız aksiyonlar için dosya yazılmaz, dolayısıyla bir sonraki çalıştırmada resume onları yeniden dener.

## Kapsam dışı

- **Grafik değişikliği** — `ConditioningConcat` zinciri, ek `CLIPTextEncode` düğümleri yok.
- **Katman başına ağırlık** — SDXL'deki gibi bir katmanı güçlendirme mekanizması yok; birleştirme düz metin.
- **Bayatlık tespiti** — sidecar dosya, hash, manifest yok.
- **Çözünürlük / süre / step kontrolü** — grafikte sabit (480×720, 6 step, cfg 1); PROMPTS hücresi bunlara dokunmaz.
- **Prompt yazım yardımcıları** — `photo_generator/prompts.json`'daki gibi katman başına LLM meta-prompt'ları bu kapsamda yok. İhtiyaç doğarsa ayrı bir iş.

## Doğrulama

Notebook'lar birim testle doğrulanmıyor; doğrulama Colab koşusudur:

1. İki aksiyonluk liste ile çalıştır → `01.mp4` ve `02.mp4` Drive'a düşer, ikisinde de aynı karakter ve aynı mekân görünür.
2. Aynı hücreyi tekrar çalıştır → ikisi de "zaten var" diye atlanır, yeni üretim olmaz.
3. Listeye üçüncü aksiyonu **sona** ekle, tekrar çalıştır → sadece `03.mp4` üretilir.
4. `STYLE = ""` ile PROMPTS hücresini çalıştır → metin doğrudan kamerayla başlar, başta `. ` artığı olmaz (birleşmiş metin ekrana basıldığı için gözle doğrulanır).
