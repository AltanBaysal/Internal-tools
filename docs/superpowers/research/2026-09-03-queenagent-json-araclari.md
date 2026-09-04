# QueenAgent — yapı dosyası ve araçları (anlaşma notu)

**Tarih:** 3 Eylül 2026 · **Durum:** ⚠️ **AŞILDI — tarihsel kayıt.** Bugün ne olduğunu
[v7 yol haritası](../plans/2026-09-03-v7-roadmap.md) söyler, ve son sözü kod söyler.

Bu belge konuşmanın ortasında yazıldı: anlaşalım diye. Anlaşıldı, ve tasarım **konuşmanın devamında
değişti** — aşağıdaki üç şey artık doğru değil:

- **`prompt` diye bir alt blok yok.** JSON'un şekli düz kaldı; kare `frame`, `scene` ve prompt
  alanlarını yan yana taşıyor. Sebep, koşunun bağlayıcı kuralı: **modele bakan imzalar donuk,
  dosyanın şekli serbest** — model dosyanın şeklini hiç bilmediği için onu gruplamanın modele bir
  faydası kalmadı.
- **Araçlar `action` parametresiyle birleşmedi.** Kaynak kaynak ayrıldılar — `set_character`,
  `remove_outfit`, `update_frame` gibi. Araştırmanın *"birleştirin"* tavsiyesi **aynı kaynak**
  üstündeki eylemler için; bunlar ayrı kaynaklar *(kullanıcı kararı, 3 Eylül: "remove_entry(file,
  map, name) ama bu saçma olmaz mı")*. Araç sayısı 9 değil **17**.
- **`copy` ve `move` yok** *(kullanıcı kararı, 3 Eylül: "sıra değiştirmeye gerek yok şimdilik")*, ve
  `read` de yok — model dosyayı `read_file` ile görüyor.

Sondaki *"cevabı seninle netleşecek üç şey"* de cevaplandı: iskeleti `create_structure` doğuruyor,
çıktının uzantısı `.py` kaldı, ve Prompt+ kare kare çalışıyor *(`write_frame_prompt`)*.

Geri kalanı — **neden** böyle olduğu — hâlâ doğru, ve belge onun için duruyor.

---

## Temel kural

**Ana agent yapı dosyasını normal araçlarla yazamaz.**

Bugün model `create_file` ve `edit_file` ile bu JSON'un içine istediğini yazabiliyor. Bundan sonra
yazamayacak: yapı dosyasına yalnız **ona özel araçlarla** dokunulacak.

Bunun iki sonucu var:

- **Dosyanın şekli garanti olur.** Bozuk JSON, uydurulmuş alan, yanlış yere yazılmış kıyafet —
  hiçbiri mümkün olmaz. Bugün bunlar 14 maddelik bir kural listesiyle *rica* ediliyor.
- **Model daha az düşünür.** Şeklin doğruluğunu kollamayı bırakır, yalnız içeriğe bakar.

Deponun kendi emsali var. `modes.py` şunu yazıyor: *"kural bir skill metnindeki cümleydi — 'dosya
oluşturma' — ve bir cümle ricadır. Sonra kural araç listesi oldu."* Aynı hamleyi bu sefer dosyanın
şekli için yapıyoruz.

---

## JSON'un yeni hâli

```json
{
  "characters": {
    "aylin": { "kind": "girl", "tags": "woman in her mid 20s, long teal hair, green eyes" },
    "deniz": { "kind": "boy",  "tags": "man in his late 20s, short black hair, stubble" }
  },
  "outfits": {
    "gunluk": "jeans, black t-shirt",
    "ceket":  "denim jacket, white t-shirt"
  },
  "locations": {
    "bedroom": "sunlit bedroom, morning light, natural light, indoors"
  },
  "frames": [
    {
      "frame": 1,
      "scene": "Aylin sabah yatağın kenarında mektubu okuyor",
      "prompt": {
        "people": "1girl",
        "characters": { "aylin": ["gunluk"] },
        "location": "bedroom",
        "action": "sitting on edge of bed, holding letter, pensive expression, looking down",
        "camera": "medium shot, from above"
      }
    }
  ]
}
```

### Kare iki gruba ayrılıyor

- **Dışarıdaki iki alan bilgidir:** `frame` karenin numarası, `scene` senin dilindeki brief.
  İkisi de prompta girmiyor.
- **`prompt` bloğuna giren her şey prompta giriyor**, üstelik **promptun sırasıyla**. Yukarıdan
  aşağı okuyunca çıkacak cümleyi görüyorsun.
- Yani *"bu alan prompta girer mi"* sorusu bir kural olmaktan çıkıp **konuma** dönüşüyor.

### Bugünden farkı

| Alan | Bugün | Bundan sonra |
|---|---|---|
| `quality` | Dosyada olabiliyor, model yazabiliyor | **Dosyadan tamamen kalkıyor** — kodda tek standart zincir |
| `people` | Model her karede elle yazıyor | **Kod yazıyor**, karakterlerin türünden sayıyor |
| `characters` girdisi | Düz metin | `kind` + `tags` — tür kodun sayabilmesi için |
| `frame` | Yok | **Kod yazıyor** — liste sırasının damgası |
| `scene` | Ayrı `-scenes.md` dosyasında | **Karenin içinde**, senin dilinde |
| Kareler | Alanlar düz duruyor | `frame` / `scene` dışarıda, gerisi `prompt` altında |

---

## Kim neyi yazıyor

- **Model** *(yalnız araçlarla)* — karakter, kıyafet, mekân girdileri; `scene`; `prompt` bloğunun
  `characters`, `location`, `action`, `camera` alanları.
- **Kod** — `frame` numarası, `people` sayısı, ve prompt kurulurken başa eklenen kalite zinciri.
- **Sen** — arayüzden dosyayı elle açıp istediğini düzeltebilirsin. Hiçbir şey bunu engellemiyor.

### Kalite zinciri

Tek bir standart zincir, kodda. Her promptun başına aynı şekilde ekleniyor, dosyada hiç görünmüyor,
ve **model onu hiç bilmiyor**.

Modele söylenen tek şey bir yasak olacak: *kalite etiketi yazma*. Bilgi değil, sınır — çünkü SDXL
modelleri alışkanlıktan `masterpiece, best quality` yazar, ve kod da başa eklediği için o etiketler
iki kez basılırdı.

Farklı bir zincir gerekirse bu bir kod değişikliği. Dosyanın alanı olmaktan çıktı.

### Neden `kind` gerekiyor

Bugün kod karede **kimin** olduğunu biliyor, **ne** olduğunu bilmiyor — çünkü karakter girdisi düz
metin. `build_prompts`'ın kendi yorumu bunu itiraf ediyor. Karakter türünü taşırsa `1girl`,
`1boy, 1girl`, `2girls` sayımını kod yapar ve o alan modelin işi olmaktan çıkar.

### Neden `scene` kareye giriyor

Bugün iki dosya var ve **sırayla eşleşiyorlar**: `bar-scene.json` ile `bar-scene-scenes.md`,
cümle 3 ile kare 3. Skill metni bu eşleşmeye koca bir paragraf harcıyor. Sahne cümlesi karenin
içinde olunca eşleştirilecek bir şey kalmıyor.

`scene` senin dilinde kalıyor *(dosyanın geri kalanı İngilizce, çünkü onu görsel model okuyor)*.
Prompta hiç girmiyor — o bir brief, çıktı değil.

### Neden `frame` numarası

Sen dosyayı açıp *"15. kareyi güncelle"* diyebilesin, araçlar da onu numarayla bulabilsin diye.

Numara **kodun bastığı damga**: liste sırası gerçek, numara onun görünen hâli. Kare eklenince ya da
silinince kod hepsini yeniden numaralar, yani ikisi hiç ayrışamaz ve boşluk hiç oluşmaz.

---

## Araçlar

Model bugün 8 araç görüyor. Yeni araçlar **iki tane** — sekiz değil, ve bunun sebebi var:
Anthropic'in ve OpenAI'nin kendi dokümanları *"her eylem için ayrı araç yerine ilgili işlemleri tek
araçta bir `action` parametresiyle birleştirin, az sayıda ve yetenekli araç seçim belirsizliğini
azaltır"* diyor.

### `frames` — karelerin tamamı

| `action` | Ne yapıyor |
|---|---|
| `add` | Sona kare ekler *(bugünkü `add_frames` bunun içine giriyor)* |
| `read` | Tek kareyi ya da bir aralığı okur — 40 kareyi baştan sona okumadan |
| `edit` | Verilen alanları yamalar. Alıntılanacak metin yok, numarayla bulunuyor |
| `copy` | Bir kareyi çoğaltır — birbirine benzeyen kareler için |
| `move` | Sırasını değiştirir |
| `remove` | Siler |

### `entries` — haritaların tamamı

`characters`, `outfits`, `locations` üstünde `set` ve `remove`.

`remove`, o adı **hâlâ kullanan bir kare varsa** reddediyor — bugün bu bir kural maddesiydi, artık
kodun cevabı.

### Değişmeyen araçlar

`read_prompt_structure_schema`, `read_file`, `create_file`, `edit_file`, `build_prompts`,
`build_character_prompts`, `write_plan`.

Yani araç sayısı **8'den 9'a** çıkıyor.

### Kapı nasıl kapanıyor

- `create_file` ve `edit_file` bir yapı dosyasına dokunmayı **reddediyor**, ve ret cümlesi doğru
  aracı söylüyor — yoksa model tahmine düşer.
- **Tek istisna:** dosya JSON olarak okunamıyorsa `edit_file` çalışıyor. Sen elle bir virgül
  bozarsan bütün yapısal araçlar düşer, ve o hâlde metin düzenlemek doğru araçtır. Bu kapı olmasa
  model dosyayı tamir edemez.

---

## `build_prompts`

- Çıktı dosyasının başındaki `PROMPTS = ` kalkıyor; düz liste basılıyor.
- queen-editor'ün okuyucusu baştaki atamayı **zaten kırpıyor** *(`prompt_list.py`)*, yani ikisi de
  çalışıyor — sade olanı seçiyoruz.
- Birleştirme kodun işi olarak kalıyor. Model prompt yazmıyor, kareyi yazıyor.
- Wildcard'lar bozulmadan geçiyor: zincirde etiket metnini normalize eden hiçbir yer olmayacak.

---

## Cevabı seninle netleşecek üç şey

1. **İskeleti kim doğuruyor?** `entries`'in ilk çağrısı dosyayı kurabilir *(araç sayısı 9'da
   kalır)*, ya da `create_structure` diye ayrı bir araç olur *(10 olur, ama daha açık)*.
2. **Çıktının uzantısı.** `PROMPTS = ` gidince dosya düz bir listeye dönüyor; `.py` kalsın mı,
   başka bir şey mi olsun.
3. **Prompt+ nasıl çalışsın?** Bugünkü gibi beşerli gruplar hâlinde mi *(`frames.add`)*, yoksa kare
   kare mi *(`frames.edit`)*. Araç ikisini de destekliyor, karar skill metninin.
