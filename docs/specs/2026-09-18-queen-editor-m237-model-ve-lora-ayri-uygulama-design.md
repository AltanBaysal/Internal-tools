# Madde 237 · Model ve LoRA ayrı iki kutu — uygulama turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-18-queen-editor-m237-model-ve-lora-ayri-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Tasarım

**Katalog.** `domain/recipes.py` gidiyor, yerine `domain/catalog.py` geliyor: `MODELS` *(kimlik,
ad, checkpoint, standart LoRA dizilimi)* ve `LORAS` *(kimlik, ad, dosya, güç, tetik)*. Eski
`recipe:*` değerleri `LEGACY`'de modele ve LoRA'ya çevriliyor; elenen iki Nova da burada Nova 3DCG'ye
düşüyor, madde 226'nın `RETIRED`'ı bunun içine eridi.

**Render** *(`comfy_photo_generator.py`)*. Önce eski değer çevriliyor, sonra model ve LoRA ayrı
ayrı çözülüyor. LoRA varsa yükleyicinin yuvaları yalnız onunla doluyor ve tetiği prompt'un başına
geçiyor; yoksa modelin standart dizilimi yazılıyor. Katalogda olmayan bir model adı bugünkü gibi
çıplak dosya adı sayılıyor. Tanınmayan bir LoRA ya da eski bir tarif render'ı kendi cümlesiyle
durduruyor.

**Üreticinin çağrı şekli** `model`'in ardına `lora=""` alıyor. Döngü planın satırından okuyup
geçiriyor. Video ve ses üreticileri parametreyi alıyor ama kullanmıyor — `end` için zaten böyle.

**Plan.** `plan_frames` her kareye `lora` yazıyor; `start_batch` onu anahtar kelimeyle alıyor, çünkü
`model`'den sonraki konum `log`'a ait. Okurken bir LoRA'sı olmayan ya da yanlış tipte LoRA'sı olan
kare Standart okunuyor. Yeniden üretilen fotoğraf kaynağının LoRA'sını da taşıyor.

**Uç nokta.** `/api/models` tek cevapta iki listeyi veriyor: `{models, loras}`. `list_loras` defterden
bir liste almıyor, `Standart` + katalogdaki bütün LoRA'lar. Kuyruk isteği `lora`'yı taşıyor, yanlış
tipte gelen Standart sayılıyor.

**Yapılandırma.** `config.PHOTO_RECIPES` → `config.PHOTO_MODELS`, `QE_PHOTO_MODELS`'ten.

**Defter.** CONFIG'de başlık *Fotoğraf modelleri*, kutular `PHOTO_NOVA3DCG` ve `PHOTO_DASIWA`;
Slime'ın kutusu gidiyor. `PHOTO_CHECKPOINTS`'e DaSiWa satırı *(3012006)*, `PHOTO_RECIPES` yerine
`PHOTO_MODELS`, Flask hücresinde `QE_PHOTO_MODELS`. Gated probe'a madde 222'de manuel defterde
yapılan düzeltme taşınıyor: DaSiWa'nın deposu `Range`'i görmezden geliyor ve eski probe bu defteri de
aynı yerde durdururdu.

**Ön yüz.** `listModels` cevabın tamamını döndürüyor, `useModels` ikisini ayrı veriyor. Panelde Model
kutusunun altına LoRA kutusu geliyor; iki `select` artık `aria-label` taşıyor, çünkü panelde iki tane
var. LoRA seçimi projenin ayarlarına yazılmıyor, yalnız ziyaretin taslağında duruyor. Kare detayı
fotoğraf sekmesinde modelin altına `LoRA` satırını koyuyor; boş LoRA *Standart* yazıyor.

## Bu turda değişen

Uygulama, defter ve derlenmiş `dist/`. Testlerden iki satır: `test_photo_usecases.py`'de planlanan
karenin anahtarlarını birebir çivileyen iki eski test *(`progress_is_reported_before_each_frame`,
`the_plan_is_appended_before_the_first_frame_renders`)* test turunda gözden kaçtı; satır artık
`lora` taşıdığı için beklenen sözlüklerine `"lora": ""` eklendi. Bir de `test_photo_routes.py`'nin
`make_client`'ı yeni `list_loras`'ı bağlıyor — `main.py`'nin aynası.
