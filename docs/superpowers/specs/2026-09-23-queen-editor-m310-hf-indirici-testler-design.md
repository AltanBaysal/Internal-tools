# Madde 310 — HF'deki modeller HF'nin kendi indiricisiyle, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Dosyalar herkese açık repolarda; deneme koşunun sonunda, Colab'da
*(kullanıcı, 23 Eylül — "sen kodun bitince test ederim çalışıyor mu diye")*.

## Bugün ne oluyor

Defterin indirme hücresi HF dosyalarını **adresleriyle** tutuyor ve iki yoldan indiriyor: H3'ün dört
dosyası `curl` ile **tek bağlantıda** *(`parallel=False`)*, fotoğrafın ikisi, WAN'ın beşi ve sesin
biri `aria2c` ile. Tek bağlantının sebebi yazılı: Xet'in imzalı adresleri paralel parçalı isteğe
403 veriyor *([NOTEBOOK-STANDARD § 3](../../../collab-toolbox/NOTEBOOK-STANDARD.md))*.

İki yol da HF'nin **köprüsünden** geçiyor, ve köprü düz indirmeyi çoğu zaman **8,7 MB/s**'de kesiyor
*([xet-core #821](https://github.com/huggingface/xet-core/issues/821), HF "düzeltilmeyecek" diye
kapattı)*. Konsol her dosya için "iniyor" ve "indirildi" diyor; **ne kadar sürdüğünü ve hangi hızla
indiğini söylemiyor**.

## Kural

**HF'deki her dosya repo adı ve repodaki yoluyla anılıyor, adresle değil, ve HF'nin kendi
indiricisiyle iniyor** — `huggingface_hub`'ın `hf_hub_download`'u, arkasında `hf_xet`. Bu yol köprüden
geçmiyor: dosyanın Xet parçalarını depodan **paralel** çekiyor ve bağlantı sayısını ağa göre kendisi
ayarlıyor. Repoda emsali var: collab-toolbox'ın MMAudio defteri NSFW fine-tune'u Colab'da böyle
indiriyor.

**Paralellik dosyanın içinde; dosyalar sırayla iniyor.** Tek dosya zaten hattı doldurur, ve konsolda
her satır tek bir dosyayı anlatır — hızlar yan yana okunabiliyor.

**Doğrulama aynı kalıyor.** İnen her dosyanın sahipsiz kuyruğu kesilip dosya yargılanıyor
*(`strip_unreferenced_tail`, sonra `check_safetensors` ya da `check_binary`)*. Bu H3 için şart: HF'den
gelen int4 metin kodlayıcı damgalı iniyor, ve kesilmeden yargılanırsa "too long" diye reddediliyor.

**Konsol her indirilen dosya için bir satır basıyor:** nereden geldiğini *(HF, ya da adresin sunucusu)*,
boyutunu, süresini ve hızını *(MB/s)* *(kullanıcı, 23 Eylül — "ama lütfen console basılsın tamam
mı?")*. Adresle inen dosyalar da aynı satırı basıyor, yani ilk denemede HF ile Civitai'nin hızı yan
yana görülüyor.

**Kapsam dışı:**
- **SAM** — `dl.fbaipublicfiles.com`'dan iniyor, HF değil; bugünkü `aria2c` yolunda kalıyor.
- **Civitai dosyaları** — 311'in işi.
- **MMAudio kütüphanesinin kendi ağırlıkları** — `download_if_needed` onları kendi indiriyor, ve
  adresleri defterde değil kütüphanenin içinde. Repo bu ağırlığı hep adressiz tuttu *(`url: None`)*;
  adres bilinen bir kaynaktan gelmeden defter onu indirmeye başlamıyor.

## Yazılacak testler — `test_notebook_installs_the_producer_groups.py`

1. **`test_no_huggingface_file_is_fetched_by_its_address`** — indirme hücresinde (`# === Target
   folders ===`) `huggingface.co` geçmiyor.
2. **`test_huggingface_files_come_down_through_hugging_face_s_own_downloader`** — `hf_fetch`'in
   gövdesi `hf_hub_download` çağırıyor, ve defter `hf_xet`'i kuruyor.
3. **`test_the_quantizer_stamp_is_cut_before_a_huggingface_file_is_judged`** — `hf_fetch`'in gövdesi
   `strip_unreferenced_tail` çağırıyor. `fetch` için olan testin ikizi.
4. **`test_every_download_prints_where_it_came_from_and_how_fast`** — `fetch`'in ve `hf_fetch`'in
   gövdesi hızı `MB/s` olarak basıyor; `hf_fetch`'inki kaynağı `HF` diye adlandırıyor.
5. **`test_an_unticked_group_costs_no_bytes` güncelleniyor** — HF listeleri kendi adlarını alıyor
   *(`HF_PHOTO`, `HF_VIDEO`, `HF_H3`, `HF_AUDIO`)*, adresle inenler `OPEN_PHOTO`'da kalıyor *(yalnız
   SAM)*; her biri yine kendi anahtarının arkasında.
6. **`test_the_h3_files_from_huggingface_come_down_over_one_connection` siliniyor** — çivilediği
   davranış bu maddeyle tersine dönüyor; yerini 1 ve 2 alıyor.

Gövdeler bölüm başlıklarıyla kesiliyor, bugünkü damga testinin yaptığı gibi: `fetch` → `# === Hugging
Face ===`, `hf_fetch` → `# === Civitai ===`.

**Bekçiler, bugün de yeşil:** her dosyanın adı defterde *(panelin grubu, H3'ün grubu)*, `fetch`'in
damga kesmesi, defterin boyut tavanı *(29.000 karakter)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız 1–5, silinen 6 dışında başka hiçbir
test kıpırdamıyor.
