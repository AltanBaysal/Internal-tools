# Madde 140 · Tur 1 (test) — Tasarım

**Kaynak:** [v6 yol haritası](../plans/2026-09-01-v6-roadmap.md), Madde 140
**Dal:** `feat/v6`
**Bu tur yalnız test yazar.** Defter bu turda ellenmez.

## Ne çalışacak

Defter foto grubunun yanına **ek checkpoint'ler** indirebilir. Hangilerinin ineceğine kullanıcı
CONFIG'deki kutulardan karar verir; işaretlenmeyen hiç denenmez, ve disk tahmini seçime göre
büyür.

İlk ek model seçildi: **Nova Orange XL REX v1.0**, Civitai version id `2945776`, dosya
`novaOrangeXL_rexV10.safetensors`, 6.46 GiB. Illustrious tabanlı — yani bugünkü grafik, bugünkü
yükleyici, bugünkü CLIP, ve 138'in `BREAK` düğümü ile USNR LoRA'sı dokunulmadan çalışıyor.

## Tasarımın düzeltilen yeri: taban modelin kutusu yok

Yol haritasına *"her checkpoint kendi kutusunu alır"* diye girmişti. Kod okununca yanlış olduğu
görüldü ve **"her ek checkpoint"** olarak daralıyor. Sebebi iki yerde birden yazılı:

- [comfy_photo_generator.py](../../../queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py)
  model seçilmemiş bir kareyi **grafiğin kendi checkpoint'iyle** üretiyor *(`if model:` — boşsa
  export'un `ckpt_name`'i kalıyor)*. `workflow_api.json` düğüm `45`'te yazan ad
  `nova3DCGXL_ilV90.safetensors`.
- [model_groups.py](../../../queen-editor/backend/features/producers/domain/model_groups.py)
  aynı dosyayı foto grubunun şartı sayıyor — **Üreticiler** paneli onu göremezse *"kurulu değil"*
  diyor.

Yani taban modele kutu takmak iki şeyi birden bozardı: kapatan kullanıcının panelinde foto
üreticisi kurulu görünmezdi *(oysa ek modelle üretim çalışıyor olurdu)*, ve model seçilmeden
kuyruğa giren her kare yok bir dosyayı isterdi.

**Bunun güzel yan etkisi:** *"foto açık ama hiç model seçilmedi"* diye bir durum doğmuyor, yani o
assert'e gerek kalmıyor. Taban her zaman iniyor; kutular yalnız üstüne ekliyor.

## Şekli

**CONFIG'de** — üç üretici kutusunun altında, ek model başına bir satır:

```python
PHOTO_NOVAORANGE = False  #@param {type:"boolean"}
```

**İndirme hücresinde** — satır, kendi anahtarını ve kendi boyutunu taşıyor:

```python
# (switch, gib, version_id, filename, label)
PHOTO_EXTRA = [
    (PHOTO_NOVAORANGE, 7, 2945776, "novaOrangeXL_rexV10.safetensors", "Nova Orange XL REX v1.0"),
]
```

ve seçilenler `CIVITAI_PHOTO`'nun **kendi tanımında** ona ekleniyor. Bu bir üslup tercihi değil,
bir bekçiyi ayakta tutuyor: `test_an_unticked_group_costs_no_bytes` kaynakta
`CIVITAI_PHOTO if INSTALL_PHOTO else []` cümlesini birebir arıyor. Ekleme `civitai_jobs` satırında
yapılsaydı o cümle bozulur ve bugün yeşil olan bir test, ilgisiz bir sebeple kırmızıya dönerdi.

Disk tahmini de aynı listeden toplanıyor; `SIZES`'ın foto satırındaki `8` sabiti yerine taban artı
seçilenler.

## Kırmızıya dönecek altı iddia

1. **Her ek modelin bir kutusu, her kutunun bir satırı var.** İki listenin birbirinden kayabildiği
   tek yer burası — kutu CONFIG'de olmak zorunda *(Colab `#@param`'ı yalnız yazıldığı yerde
   çiziyor)*, satır indirme hücresinde. Test ikisini isimle eşleştiriyor.
2. **Ek modeller kapalı geliyor.** Hiçbir kutuya dokunmayan bir koşu bugünküyle bayt bayt aynı
   çalışmalı. Bu, maddenin geri kalanını güvenli kılan iddia.
3. **İşaretlenmemiş model bayt harcamıyor.** Satırlar kendi anahtarlarıyla süzülüyor — grubun
   kutularında zaten geçerli olan kuralın bir alt kademesi.
4. **Foto tahmini seçime göre büyüyor.** `SIZES` artık foto için sabit bir sayı taşımıyor.
   Tahmin küçük kalırsa disk kontrolü yalan söyler ve indirme ortasında yer biter — kontrolün var
   olma sebebi tam olarak bu.
5. **Yeni model gerçekten indiriliyor.** Dosya adı ve version id defterde geçiyor.
6. **Giriş hücresindeki custom node sayısı listeyle uyuşuyor.** Bugün *"(19 custom node)"* diyor,
   liste 20 — **138'in bıraktığı hata.** Alttaki başlık düzeltilmişti, giriş hücresi
   kaçmıştı, çünkü bugünkü test yalnız başlığa bakıyor. Bu maddeye giriyor çünkü 140 zaten aynı
   hücreyi *(`~8 GiB` rakamı yüzünden)* değiştirmek zorunda, ve aynı hücreye iki ayrı commit'te
   dokunmanın bir faydası yok.

## Yeşil kalması gerekenler

- `test_every_file_the_panel_counts_is_fetched_by_the_notebook` — taban modelin adı yerinde
  duruyor, çünkü taban `CIVITAI_PHOTO`'dan çıkmıyor.
- `test_an_unticked_group_costs_no_bytes` — yukarıda anlatılan sebeple; ekleme tanımda yapılıyor.
- `test_every_producer_has_a_checkbox_of_its_own` — üç üretici kutusu yerinde, yeni kutular
  onların yerine değil altına geliyor.
- `test_the_notebook_says_how_many_custom_nodes_it_installs` — başlık zaten doğru; kırmızı olan
  giriş hücresi.
- **Bütün video ve ses testleri** — madde onlara dokunmuyor.

## LoRA'nın kutusu yok, ve testi de yok

USNR grafikte düğüm `27`'de sabit açık ve foto grubunun şartı; madde yalnız Illustrious tabanlı
model alıyor *(kullanıcı kararı, 2 Eylül)*. Ayrı bir bekçi yazılmıyor: 1. iddia her `PHOTO_EXTRA`
satırının bir kutusu olmasını zorunlu kıldığı için LoRA o listeye zaten giremiyor.

## Kapsam dışı

- **`model_groups.py`** — o liste *"foto üreticisi kurulu mu"* sorusunu cevaplıyor, ve ek bir
  checkpoint o sorunun şartı değil. Gruba yazılsaydı, onu indirmemiş kullanıcıya panel *"kurulu
  değil"* derdi.
- **Uygulamanın tek satırı.** Model listesi ComfyUI'ye soruluyor; `checkpoints/`'a inen her
  `.safetensors` **Model** açılır listesinde kendiliğinden beliriyor.
- **Grafiğin örnekleyici ayarları.** Grafik 28 adım / CFG 6 ile sabit, yeni modelin kendi önerisi
  20 adım / CFG 4.5. Örnekleyici tutuyor *(`euler_ancestral`)*, CFG tutmuyor — ama arayüzde CFG
  alanı yok ve değeri modele göre değiştirmek bu maddenin işi değil. Karşılaştırma okunurken
  hatırlanacak, yol haritasına yazıldı.
- **Anima** — [Madde 142](../plans/2026-09-01-v6-roadmap.md). Başka bir mimari, başka bir grafik.

## Colab'da görülecek

Takım yeşil, defterin **ne dediğini** söyler — indirdiğini değil. Onu söyleyen tek şey koşunun
kendisi: foto kutusu ve yeni modelin kutusu işaretli bir Colab koşusu, indirme özetinde
`checkpoints/` altında iki dosya, ve arayüzün **Model** listesinde iki satır. Sonra aynı prompt iki
modelle üretilip yan yana konuyor — o karşılaştırma aynı zamanda 141'in kapsamını belirleyecek
ölçünün parçası.
