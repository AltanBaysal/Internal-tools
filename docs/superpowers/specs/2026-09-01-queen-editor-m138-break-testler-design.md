# Madde 138 · Tur 1 (test) — Tasarım

**Kaynak:** [v6 yol haritası, Madde 138](../plans/2026-09-01-v6-roadmap.md)
**Dal:** `feat/v6`

## Sorun

Grafiğin pozitif yolu tek zincir: `3` POSITIVE *(`ImpactWildcardProcessor`)* → `39` `RegexReplace`
→ `36` `CLIPTextEncode`. Zincirin ucundaki kodlayıcı `BREAK` bilmiyor, yani prompta yazılan bir
`BREAK` dokunulmadan geçip **kelime olarak** kodlanıyor — ayırmıyor, kirletiyor.

Bunun altında ikinci bir sorun var, ve bu koşu açılana kadar kimse görmemişti:
[test_workflow_asset.py](../../../queen-editor/backend/tests/test_workflow_asset.py) grafiği
korurken `3`, `4`, `40` ve `45`'i adıyla çiviliyor ama **`36`'dan hiç söz etmiyor.** Yani pozitif
kodlayıcının sınıfı bugün sessizce değişebilir, ve değiştiği hiçbir yerde görünmez. Backlog'un
*"grafik değişince test kırmızı verir"* cümlesi bu düğüm için doğru değildi.

## Yol

`36`'nın sınıfı `BREAK` bilen bir kodlayıcı olur — aday `CLIPTextEncodeBREAK`
*([ComfyUI-ppm](https://github.com/pamparamm/ComfyUI-ppm))* — ve defter o paketi kurar.

Kablolar değişmiyor. Aday düğümün girişleri `text` + `clip`, çıkışı `CONDITIONING`; bugünkü
`CLIPTextEncode` ile birebir aynı şekil, ve API biçiminde girişler isimle tutulduğu için sıra da
önemsiz. Değişen tek şey bir sınıf adı.

**Bu tur yalnız testleri yazıyor.** Grafiğe ve deftere dokunulmuyor; ikisi de uygulama turunun işi.

## Kurallar

- **Değişen tek düğüm `36`.** Hem `KSampler` hem `ToDetailerPipe` pozitifi onun çıkışından okuduğu
  için tek değişiklik ikisini de kapsıyor.
- **Negatif yol dokunulmuyor.** `4` → `38` kendi `CLIPTextEncode`'unda kalıyor: negatifte `BREAK`'in
  işi yok, ve dokunulmayan bir düğüm bozulmayan bir düğüm. Bu bir karar, ve bekçisi yazılıyor —
  yoksa bir dahaki export ikisini birden değiştirir ve kimse fark etmez.
- **Defter ile grafik aynı commit'te.** ComfyUI kendisine gönderilen her düğümü doğruluyor, yani
  grafiğin yeni sınıfı isteyip defterin o paketi kurmadığı bir commit'te **her üretim düşer**. Test
  turu ikisini de yazmıyor ama ikisinin bağını bir teste bağlıyor.
- **Adaptör değişmiyor.** [comfy_photo_generator.py](../../../queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py)
  promptu `3`'e yazıyor ve kontrol ettiği düğüm listesinde *(`3`, `4`, `40`, `45`)* `36` yok. O liste
  *"yamaladığım düğümler"* demek, ve bu madde `36`'yı yamalamıyor — sınıfını değiştiriyor.
- **`model_groups.py` değişmiyor.** O liste model *dosyalarını* sayıyor; custom node model değil.
- **Ön yüz ve `dist` yok.** Madde ekranda hiçbir şey çizmiyor.
- **Sınıf adının kendisi uygulama turunda doğrulanır.** Aşağıdaki kırmızı test bir literal taşıyor
  ve o literal düğümün kaynağı okunarak yazıldı, çalıştırılarak değil. Gerçek ad farklı çıkarsa
  testin literali onunla birlikte düzelir; **iddianın şekli değişmez.** Davranışın kanıtı zaten
  testte değil, Colab'da.

## Bu turun testleri

### `test_workflow_asset.py`

- `test_the_positive_encoder_understands_break` — **kırmızı**. `36`'nın sınıfı `BREAK` bilen düğüm.
  Maddenin kendisi.
- `test_the_negative_path_keeps_the_plain_encoder` — **bekçi**, yeşil. `38` `CLIPTextEncode` kalıyor.
  Kararı tutan şey: bu madde pozitifi değiştiriyor, ikisini birden değil.
- `test_the_prompt_reaches_the_encoder_through_the_chain` — **bekçi**, yeşil. `3` → `39` → `36`
  zinciri kablosuyla çivileniyor: adaptörün yazdığı düğümden kodlayıcıya kadar. Sınıf değişirken
  kabloların düşmediğini tutan şey bu, ve `39`'un aradan çıkarılmadığını da o söylüyor.

### `test_notebook_installs_the_producer_groups.py`

- `test_the_notebook_installs_the_encoder_the_graph_asks_for` — **kırmızı**. Defter, grafiğin
  istediği kodlayıcıyı veren paketi kuruyor. Yukarıdaki *"aynı commit"* kuralının bekçisi: grafik
  yeni sınıfı isteyip defter paketi kurmazsa bu test kırmızı kalır, ve kimse Colab'da öğrenmez.
- `test_the_notebook_says_how_many_custom_nodes_it_installs` — **bekçi**, bugün yeşil. Markdown
  başlığındaki sayı `CUSTOM_NODES` listesinin uzunluğuna eşit. Bugün ikisi de 19; uygulama turunda
  liste 20 olunca bu test başlığı da güncellemeye zorlar. Sayı iki yerde yazılı ve bir kopya
  bayatlar — bekçi onun için var.

## Ayakta kalması gerekenler

`test_workflow_asset.py`'nin bugünkü yedi testi: `3`, `4`, `40`, `45`'in çivileri, iki video
grafiğinin düğümleri, iki grafiğin süre üzerinde anlaşması, ve iki grafiğin yüklediği her modelin
grupta sayılması.

`test_notebook_installs_the_producer_groups.py`'nin bugünkü yirmi testi — defterin adı, üç
üreticinin kutuları, kapılı indirme, disk ölçümü, ses motoru, xAI yoklaması, tünel protokolü.

## Bilerek yapılmayanlar

**Grafik ve defter.** İkisi de uygulama turunun işi; bu tur kod dosyalarına dokunmuyor.

**`skip` / `xfail` yok.** Kırmızı kırmızı commit'lenir.

**Adaptörün `_load()` kontrolüne `36` eklenmiyor.** O liste adaptörün yamaladığı düğümleri sayıyor
ve `36` onlardan biri değil; eklemek listeye yanlış bir anlam yüklerdi. Grafiği koruyan yer
`test_workflow_asset.py`.

**Davranış testi yok, çünkü yazılamaz.** Hiçbir birim testi `BREAK`'in gerçekten böldüğünü
söyleyemez — dosyanın ne dediğini söyler. Bölmenin kanıtı Colab'da, aynı seed ile iki üretimin
karşılaştırılması *(protokol uygulama turunun spec'inde)*.
