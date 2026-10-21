# Madde 486 · Krea seçiliyken LoRA kutusu Krea'nın LoRA'sını gösterir, negatif gizlenir — tasarım

**Tarih:** 21 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
486 · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)
· **Önce:** [482'nin spec'i](2026-10-21-queen-editor-m482-krea2-photo-option-design.md), 3. bölüm

## Kullanıcıdan gereken

Hiçbir şey. Madde 21 Ekim'de hizalandı *("olur böyle yapalım")*.

## Ne, neden

482'de Krea seçiliyken üretim paneli bugünkü modellerin LoRA kutusunu (USNR, Slime, Boş) ve negatif
kutusunu gösteriyor, ama Krea ikisini de kullanmıyor: kendi grafiğindeki LoRA'yla çiziyor — bugün SNOFS,
`53:15` `LoraLoaderModelOnly`, `snofs_krea_v1_5.safetensors`, 0,8 — ve negatifi yok (grafiğin negatifi
`ConditioningZeroOut`, cfg 1). Kullanıcı *"şuan yüklü olan lora görünsün"* dedi; negatif için Claude'un
önerisini kabul etti.

Bu maddeden sonra Krea seçiliyken:

- **LoRA kutusu** tek bir satır gösterir, **SNOFS**, ve seçilemez (kapalı kutu).
- **Negatif kutusu** görünmez. Yön seçeneği bir satır yukarı çıkar.
- Nova ya da DaSiWa'ya dönülünce iki kutu bugünkü gibi gelir: kullanıcının seçtiği LoRA ve yazdığı
  negatif yerinde.

Krea karesinin **ayrıntı sayfası** da aynı şeyi söyler: LoRA satırında SNOFS, negatif kutusu yok.

## Bugün — koddan okunanlar

- **Model ve LoRA kutuları** tek bir cevaptan dolar, `GET /api/models` → `{"models", "loras"}`
  (`list_models`, `list_loras`). Model satırı `{"value", "label"}`; liste `catalog.MODELS`'tan,
  notebook'un `QE_PHOTO_MODELS`'ıyla süzülür.
- **Panel** (`GeneratePanel.jsx`) kutuların değerlerini kendi state'inde tutar. *Kuyruğa ekle*'de
  `ProjectScreen` önce bunları projenin `settings`'ine yazar, sonra `POST …/generate`'e gönderir.
- **`start_batch`** LoRA'yı `catalog.LORAS`'a karşı doğrular (`InvalidLora`), sonra `plan_frames`
  satıra negatifi, modeli ve LoRA'yı olduğu gibi yazar. Fotoğraf kaydı (`photos.jsonl`) negatifi
  plan satırından alır.
- **Ayrıntı sayfası** (`PhotoDetail.jsx`) modelin ve LoRA'nın adını `/api/models`'ın listelerinden
  bulur; LoRA satırı yalnız satır bir LoRA adlandırıyorsa çizilir. Negatif kutusu her fotoğrafta var,
  fotoğraf duruyorsa yazılabilir; *Yeniden üret* yazılanı `regenerate`'e gönderir.
- **Satır yazan üç yer:** `start_batch` (`plan_frames`), `regenerate` ve ajanın düzeltmesi
  `fix_photo` (481). İkisi LoRA'yı kaynak satırdan kopyalar, negatifi istekten alır.

## Kararlar

### 1. Bilgi katalogda, Krea'nın satırında

"Krea'nın LoRA'sı SNOFS; Krea negatif almaz" `catalog.MODELS`'taki Krea satırında durur:

```python
KREA2_LORA = {"id": "snofs", "label": "SNOFS", "lora": "snofs_krea_v1_5.safetensors"}

{"id": KREA2, "label": "Krea 2 Turbo", "lora": KREA2_LORA, "negative": False}
```

Nova ve DaSiWa'nın satırı değişmez: bir checkpoint'in LoRA'sı LoRA kutusunun cevabıdır (madde 238),
negatifi kutunun negatifidir. Katalogda iki fonksiyon:

- `drawn_with(model, lora, negative) -> (lora, negative)` — bir fotoğrafın çizildiği LoRA ve negatif,
  yani satırına yazılan. Satır yazan her yer bunu çağırır (4). Krea için `("snofs", "")`; bilinmeyen,
  boş, eski `recipe:…` ya da dosya adı verileni olduğu gibi alır.
- `own_lora(model)` — modelin grafiğinin kendi LoRA'sı, ya da `None`. Yalnız `start_batch`'in
  doğrulaması için: kutu çizmeyecekse kutunun LoRA'sı doğrulanmaz.

**Neden katalog:** model listesini zaten o veriyor ve kural sunucuda kalır (FOUNDATION, karar 4).
Ön yüz model kimliği bilmez; satırın ne dediğine bakar.

**`lora` dosya adı** yalnız bir test için: `test_workflow_asset` grafiğin `53:15`'inin yüklediği
dosyanın katalogdakiyle aynı olduğunu sorar. Kullanıcı workflow'undaki LoRA'yı değiştirirse test
kırılır ve panel yanlış LoRA adı söyleyemez. Güç (0,8) grafiğin; katalog onu tekrar etmez.

### 2. `/api/models` satırı söyler

`list_models` Krea satırına iki alan ekler; öteki satırlar bugünkü gibi `{"value", "label"}`:

```json
{"value": "krea2", "label": "Krea 2 Turbo",
 "lora": {"value": "snofs", "label": "SNOFS"}, "negative": false}
```

Alan yoksa bugünkü davranış: LoRA kutusu listeyi gösterir, negatif görünür. Bu yüzden eski bir cevap ya
da bir test fikstürü hiçbir şey kaybetmez. SNOFS `loras` listesine girmez: o liste Nova ve DaSiWa'nın
kutusu, ve SNOFS orada seçilebilir olsaydı SDXL'e yüklenirdi.

### 3. Panel: tek satırlık kapalı kutu, gizli negatif

`GeneratePanel` Model kutusunun tuttuğu değerin satırını listede bulur (`chosen`):

- `chosen.lora` varsa LoRA kutusu o tek satırı gösterir ve kapalıdır. Kutunun kendi state'i (`lora`)
  dokunulmadan kalır.
- `chosen.negative === false` ise negatif kutusu çizilmez. State'i (`negative`) kalır.

Nova'ya dönünce kutular state'ten çizildiği için yazılan negatif ve seçilen LoRA yerindedir.

**İstek ve projenin ayarları değişmez:** panel Krea'da da kendi `lora` ve `negative` değerlerini
gönderir, ve `ProjectScreen` onları `settings`'e yazar. Böylece sayfa yenilenip Krea'dan Nova'ya
dönülse de kullanıcının LoRA'sı ve negatifi yerindedir. Krea'nın bunlarla ne yapacağı sunucunun
kararı (4).

### 4. Krea satırı neyi kaydeder

`plan.json`'daki Krea satırı Krea'nın gerçekten çizdiğini kaydeder:

| Alan | Krea | Nova / DaSiWa |
|---|---|---|
| `lora` | `"snofs"` — grafiğin kendi LoRA'sı | kutunun seçimi, bugünkü gibi |
| `negative` | `""` | kutunun negatifi, bugünkü gibi |

- **`start_batch`:** kutunun LoRA'sı yalnız kutu çizecekse doğrulanır (`own_lora(model) is None`).
  Krea'da kutu kullanılmıyor; orada eskimiş bir seçim `InvalidLora`'yla bir Krea batch'ini durdurmaz.
  Sonra `plan_frames` satıra `drawn_with`'in cevabını yazar.
- **`regenerate`:** kaynak satırın LoRA'sı ve istekteki negatif `drawn_with`'ten geçer. 486'dan önce
  planlanmış bir Krea karesi (LoRA'sı ör. `slime`) yeniden üretilince de yeni satır `snofs` ve boş
  negatif yazar.
- **`fix_photo`:** aynı çağrı, satırın modeli ve LoRA'sıyla.

Fotoğraf kaydının negatifi plan satırından geldiği için o da boş olur. Varyantların birlikte üretilip
üretilmeyeceğine bakan `variant_batch.MADE_FROM` aynı alanları karşılaştırır; Krea satırlarının hepsi
aynı değerleri taşıdığı için grup değişmez (Krea zaten tek tek üretilir, 482).

### 5. Ayrıntı sayfası

`PhotoDetail` karenin modelinin satırını bulur (`madeBy`), ve:

- **LoRA satırı** karenin kaydettiği LoRA'nın adını önce modelin kendi LoRA'sında, sonra `loras`
  listesinde arar. Bir Krea karesi `snofs` der, sayfa **SNOFS** yazar. Kural bugünkü: bulunamazsa
  kaydedilen değer görünür, LoRA'sı olmayan satır çizilmez.
- **Negatif kutusu** `madeBy.negative === false` ise çizilmez — üretim panelinde olduğu gibi. Krea
  karesinin negatifi kullanılmadı; yazılabilir bir kutu, gönderdiği şey hiç kullanılmayacakken yalan
  olurdu.

482'yle bu madde arasında üretilmiş Krea kareleri (yalnız deneme makinelerinde; 482'nin Colab denemesi
koşunun sonunda) kaydettikleri LoRA'yla görünür, ör. USNR. Taşıma yazılmaz: gerçek bir proje yok.

## Maliyet

| İşlem | Disk / ağ |
|---|---|
| `GET /api/models` | Değişmez: katalog bellekte, Krea satırına iki alan. Disk ya da ağ yok. |
| Panelde model değiştirmek | İstek yok; listede bir arama, satır sayısıyla O(n), n = 3. |
| Krea batch'i | Değişmez: aynı plan yazımı, satıra başka değerler. Doğrulama bellekte. |
| Ayrıntı sayfası | Değişmez: `/api/models` cevabı ziyaret boyunca hatırlanıyor (`useModels`). |
| Drive | Yeni okuma ya da yazma yok. Satırın biçimi aynı; değişen yalnız Krea satırının iki değeri. |

## Neyi kırabilir

- **Ayarlar:** Krea'da da kutuların değerleri `settings`'e yazılır; Nova'ya dönüş, yenilemeden sonra
  da kayıpsız. Yeni bir alan, dosya ya da kayıt biçimi yok.
- **Bugünkü modeller:** Nova ve DaSiWa'nın satırına hiçbir alan eklenmez; doğrulama, kayıt ve ekran
  bugünkü gibi. Bilinmeyen model (notebook önde) bugünkü gibi negatif alır ve kutuyu doğrular.
- **Eski Krea kareleri:** yukarıda; kaydettiklerini gösterirler.
- **Ajan:** 481'in ajanı bir Krea karesinin negatifini "düzeltebilir"; satır boş kaydeder ve ajanın
  söylediği değişiklik olmamış olur. Ajanın talimatı Krea'yı bilmiyor — ayrı bir iş, ana ajana
  bildirildi.
- **Workflow değişirse:** kullanıcı Krea'nın LoRA'sını değiştirirse katalog testi kırılır; katalogdaki
  satır yeni dosyayla düzeltilir.

## Bitti sayılır

1. Krea seçiliyken LoRA kutusunda yalnız **SNOFS** görünüyor, kutu seçilemiyor; negatif kutusu yok.
2. Nova ya da DaSiWa'ya dönünce iki kutu bugünkü gibi; seçilen LoRA ve yazılan negatif yerinde.
3. Bir Krea batch'inin satırları `lora: "snofs"`, `negative: ""` kaydediyor; ayrıntı sayfası LoRA'yı
   SNOFS diye yazıyor, negatif kutusu göstermiyor.
4. Nova ve DaSiWa'nın paneli, kaydı ve ayrıntı sayfası değişmedi.
5. Dört takım yeşil; `dist` yeniden kuruldu.
