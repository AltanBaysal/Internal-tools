# Madde 178 · test turu — skill metinleri yeni takımı anlatır

**Kaynağı:** [yol haritası](../plans/2026-09-05-queenagent-v7-roadmap.md), Madde 178.

Bu tur **yalnız testleri** yazıyor ve kırmızı commit'liyor.

---

## Metinler ne kadar geride

166–177 takımı baştan kurdu. İki skill metni hâlâ **eski takımı** anlatıyor:

| Metin ne diyor | Bugün ne var |
|---|---|
| `create_file` iskeleti yazar | `start_scenario` yazar, `create_file` `.json`'ı reddeder |
| kareler `add_frames` ile, beşerli | `add_scene`, kadrosuyla |
| sahne listesi `bar-scene-scenes.md` | yok — sahne cümlesi karenin alanı |
| yapı dosyasının kareleri boş kalır | 4. adım kareleri yazar |
| şikâyet `edit_file` ile düzeltilir | `.json` metin olarak açılmaz |
| action ve kamera prompt+'ın zanaatı | `write_frame_prompt`'un modelinin |

Deneme 1 ve 2 **skill seçmeden** koşuldu; tam olarak bu yüzden. Deneme 3 metinlerle koşuluyor, ve
bu madde onları o denemeye hazırlıyor.

## İki metnin yeni sınırı

**Start a scenario** artık **kareyi de yazıyor** — sahnesiyle, kadrosuyla, mekânıyla; ama
**action'sız.** Eski bölünme *(temel burada, kareler orada)* sahne listesi dosyasıyla birlikte
gidiyor: sahne cümlesi artık karenin bir alanı, ve onu ayrı bir `.md`'ye yazmak aynı şeyi iki yere
koymak olurdu.

**Generate prompts+** her kare için `write_frame_prompt`, sonra `build_prompts`. Şikâyet iki yoldan
biri: **not ile aynı kareyi yeniden yazdırmak**, ya da haritadaki girdiyi `update_*` ile düzeltmek —
o ikincisi girdiye dayanan her kareye birden ulaşıyor.

## Zanaat metinden çıkıyor

*"Komşu kareler çekimde ayrılsın"*, *"sahne cümlesi kopyalanacak metin değil"* — bunlar bugüne kadar
prompt+'ın metnindeydi çünkü action'ı ana ajan yazıyordu. Artık yazmıyor. İkisi de
`WRITE_FRAME_SYSTEM_PROMPT`'ta, ve **orada tek kopya.**

Bu, kelime tavanının altında yer açıyor: 178 metinlere yeni cümleler koyuyor, ve yerini eskilerin
gitmesinden alıyor.

## Korunanlar

Kelime tavanları *(450 ve 300)*, persona açılışları, *"prompts for an SDXL-family image model"*,
onay döngüsü, plan kuralları, delegasyon kuralları, kapanış kuralı, ve **`list_files` yasağı.**

`SYSTEM_PROMPT` **değişmiyor:** andığı dört araç *(`read_file`, `create_file`, `edit_file`,
`write_plan`)* hâlâ yerinde ve hâlâ doğru — `create_file` ve `edit_file` belge yazıyor, senaryo
değil.

---

## Çivilenen vak'alar

**Akış (6):** senaryoyu `start_scenario` açıyor · haritaları `add_character`/`add_outfit`/
`add_location` dolduruyor · sahneleri `add_scene` kadrosuyla yazıyor · kareler action'sız kalıyor ve
metin bunu söylüyor · `build_prompts` burada çağrılmıyor · sahne listesi dosyası hiçbir metinde yok.

**Yazıcı (4):** her kare için `write_frame_prompt` · sonra `build_prompts` · şikâyet not ile
yeniden yazdırmak ya da `update_*` · `add_frames`/`add_scene`/iskele hiçbir yerde.

**İki metnin ortak yasağı (2):** yapı dosyasına metin olarak dokunan cümle yok · yazıcı modelin
zanaat kuralları metinlerde tekrarlanmıyor.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **12 kırmızı**, hepsi `test_skills.py`'de; hiçbiri `skip` ya da `xfail` değil.
3. Öteki üç takım rakamlarını korudu: **589 · 739 · 591.**
4. `dist` derlenmedi — bu madde ön yüze dokunmuyor.
