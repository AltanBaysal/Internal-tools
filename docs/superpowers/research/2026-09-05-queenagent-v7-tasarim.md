# QueenAgent v7 — tasarım kararı

**5 Eylül 2026** · Dal: `feat/queenagent-v7` *(v6'nın ucundan)*

Bu belge bir yol haritası değil, **yol haritasının yazılacağı kaynak**. Kararlar burada, sıra ve
maddeler ayrı dosyada.

---

## 1 · İki model, iki iş

**Queen Pro / Queen Flash ana ajan** — konuşma, yapı, sahne cümlesi, ve karakter · kıyafet · mekân
etiketleri.

**Prompt yazan model tek işte** — karenin **action**'ı. Araç olarak, ajan olarak değil.

**Sebebi:** sınırlama karakteri ya da mekânı tarif etmekte değil, **action'da** başlıyor.

**Hangi model** `config.py`'de bir rol, aracın içine gömülü değil — gömülürse bir daha ölçülemez.

### Adlar

Modeller **Queen** adıyla anılıyor *(kullanıcı kararı, 5 Eylül)*: `queen-pro` ve `queen-flash`.
Sağlayıcının adı yalnız `config.py`'nin `base_url`'ünde kalıyor — arayüzde, sohbet kaydında ve bu
belgenin geri kalanında geçmiyor.

**Neden:** ürün QueenAgent, ve kullanıcının seçtiği şey bir sağlayıcı değil bir **kademe** — hızlı
olan ve güçlü olan. Sağlayıcı yarın değişebilir, kademe değişmez.

**Yalnız arayüzde** *(kullanıcı kararı, 5 Eylül)*: `config.py`'nin anahtarı sağlayıcıya giden model
adının kendisi *(`client.py`, `payload["model"]`)*, o yüzden dokunulmuyor; `models.js` "Queen Pro" ve
"Queen Flash" yazıyor. Eski sohbet kayıtları bozulmuyor.

**Besteci iki satır.** Grok bir seçenek değil, `config.py`'de bir rol — prompt yazan model. Ana ajanı
ona vermek, ajanlıkta zayıf olduğu söylenen modele bütün işi vermek olurdu.

**Varsayılan Queen Flash** *(kullanıcı kararı, 5 Eylül)*. Model seçmeyen her mesaj — 146'dan önceki
bütün kayıtlar dahil — bugün Grok'la cevaplanıyor; artık ucuz olanla başlar, Pro'yu isteyen seçer.

Nasıl çalıştığı **prompt yönetiminde** *(§2)*.

---

## 2 · Araç takımı

Kaynak başına iş, ve **ekle / güncelle / çıkar ayrı araçlar** *(kullanıcı kararı, 5 Eylül:
"yazılım gibi düşün")*. Bir ad var olduğu hâlde eklemek reddediliyor, olmadığı hâlde güncellemek de
— yanlışlıkla üzerine yazmak imkânsız hâle geliyor. Emsali depoda: `create_file` var olan ada
reddediyor, değiştirmek `edit_file`'ın işi.

### Dosya yönetimi

| Araç | Ne yapar |
|---|---|
| `read_file` | Bir dosyayı okur |
| `create_file` | Yeni belge doğurur — **`.json` hariç** |
| `edit_file` | Metin belgesini düzenler — **`.json` hariç** |
| `start_scenario` | Boş yapı dosyası doğurur *(ad önerisi)* |

`create_file` belge doğuruyor, `start_scenario` yapı dosyası. Kapının kapanabilmesinin sebebi bu:
`.json` yasaklandığında modelin elinde onu doğuracak kendi aracı kalıyor.

**Silen araç yok** *(kullanıcı kararı, 5 Eylül)*. Ajan bir dosyanın silinmesi gerektiğini düşünüyorsa
kullanıcıya söyler, kullanıcı siler. Claude Code'da da böyle bir araç yok; bir dosyanın tur
ortasında yok olması, izin kapısının bile korumasına bırakılmayacak kadar geri dönüşsüz.

### Karakter yönetimi

Bir kişi: adı ve onu çizdiren etiketler. Senaryonun tekrar eden öznesi — bir karakter birçok karede
görünüyor, ve her karede aynı kişi olması bu tek girdinin işi.

| Araç | Ne yapar |
|---|---|
| `add_character` | Yeni karakter ve etiketleri. **Ad varsa reddeder.** |
| `update_character` | Etiketleri değiştirir, ya da adı *(`new_name`)*. **Ad yoksa reddeder.** Yalnız verileni değiştirir; adı değişince onu anan kareler de değişir ve kaçı değiştiği cevapta yazar. |
| `remove_character` | Siler. **Bir kare onu anıyorsa reddeder:** *aylin hâlâ 1, 3 numaralı karelerde.* |

**Kendi kuralı:** kişi sayısı **bu etiketlerin içinde** duruyor — kaç kişiyi çizdirdiğini sayan tek
yer burası. Yaş, vücut, saç, yüz burada; kıyafet burada değil.

### Kıyafet yönetimi

Bir giysi takımı, kendi adıyla. Karakterden ayrı tutuluyor çünkü **aynı karakter karelerde farklı
şeyler giyiyor**, ve aynı giysiyi birden çok karakter giyebiliyor. Karede eşleşiyorlar: kare bir
karakteri adıyla anıyor ve ona bir ya da birkaç kıyafet veriyor.

| Araç | Ne yapar |
|---|---|
| `add_outfit` | Yeni kıyafet ve etiketleri. **Ad varsa reddeder.** |
| `update_outfit` | Etiketleri ya da adı değiştirir. **Ad yoksa reddeder.** |
| `remove_outfit` | Siler. **Bir karede giyiliyorsa reddeder:** *gecelik hâlâ 1, 3 numaralı karelerde giyiliyor.* |

**Kendi kuralı:** yalnız giysi. Kişi tarif edilmiyor, sayı yazılmıyor — o karakterin işi.

### Mekân yönetimi

Bir yer. Karakterin tersine **bir karenin tek mekânı var**, ve mekânın içinde kimse yok.

| Araç | Ne yapar |
|---|---|
| `add_location` | Yeni mekân ve etiketleri. **Ad varsa reddeder.** |
| `update_location` | Etiketleri ya da adı değiştirir. **Ad yoksa reddeder.** |
| `remove_location` | Siler. **Bir karenin yeriyse reddeder:** *bedroom hâlâ 1, 3 numaralı karelerin yeri.* |

**Kendi kuralı:** içinde insan yok, sayı yasak. Işık, zaman, mekân etiketleri.

### Kare yönetimi

Bir kare üç şey taşıyor: **sahne cümlesi**, **kadro** *(kim, hangi kıyafetle)* ve **mekân**.
Dördüncüsü `action`, o Grok'un — aşağıda. Karakterin tersine **adı yok, numarası var**, ve numarayı
kod veriyor.

**`camera` alanı yok** *(kullanıcı kararı, 5 Eylül)*. Çekim açısı `action`'ın içinde yazılıyor.
`build_prompts` zaten hepsini tek etiket dizisine çeviriyor, yani ayrı alan olması çıktıda hiçbir
şey kazandırmıyor; ve açı çoğu zaman eylemin parçası — ayrı tutmak Queen'e, Grok'un yazdığı şeyin
yarısını yazdırmak olurdu.

| Araç | Ne yapar |
|---|---|
| `add_scene` | Kare doğurur — sahne cümlesi, kadrosu ve mekânıyla, birkaçını birden. **Yalnız sahne zorunlu** |
| `update_frame` | Karenin alanlarını düzeltir |
| `remove_frame` | Kareyi siler, kalanlar 1'den yeniden numaralanır |

**Kendi kuralı:** kadroyu ve mekânı **Queen** koyuyor. Kimin sahnede olduğuna karar vermek anlama
işi, ve konuşmayı okuyan o. `add_scene` bunları doğum anında alıyor — yoksa 40 kare için 40 ayrı
düzeltme çağrısı turun raundlarını yerdi.

**Sahne listesi dosyası yok** *(kullanıcı kararı, 5 Eylül)*. Bugün *Start a scenario* sahneleri
`bar-scene-scenes.md`'ye yazıyor ve *Generate prompts+* oradan okuyor; o dosyanın tek sebebi, kareyi
o zaman doğuracak bir aracın olmamasıydı. Artık sahne cümlesi karenin içinde, tek dosya. İki skill
metni de buna göre yeniden yazılıyor.

**Argüman yapılı olabilir.** Kadro `{aylin: [gecelik]}` iç içe bir şey, ve `add_scene` bunun listesini
alıyor. Yasak olan JSON değil, modelin **dosyanın saklanma şeklini** bilmesi: bir çağrının argümanı
aracın sözleşmesi, dosyanın şekli değil. Yanlış şekil gelirse araç reddeder ve ne beklediğini söyler.

**`solo` karakterin etiketine yazılmaz.** Sayı orada durur *(`1girl`)*, ama `solo` karenin sözü —
iki kişilik bir karede yanlış olur. Kadroyu gören Grok, tek kişiyse action'a koyar.

### Prompt yönetimi

Karenin içindeki ayrı iş, ve **tek Grok'un dokunduğu yer.**

| Araç | Ne yapar |
|---|---|
| `write_frame_prompt(file, frame, note?)` | O karenin **action**'ını yazar. **Her zaman üzerine yazar** — yazmak ve düzeltmek aynı çağrı |

**Ne yazıyor:** yalnız `action`, ve çekim açısı onun içinde. Başka hiçbir alana dokunmuyor.

**Ne alıyor:**

- o karenin **kadrosu** — adlar **ve** etiketleri, kıyafetlerininkiyle birlikte
- o karenin **mekânı** ve etiketleri
- o karenin **sahne cümlesi**
- varsa **`note`** — ana ajanın kendi cümlesi

Bütün haritalar değil, **yalnız o karenin kullandıkları.** Konuşma yok, bağlam kabı yok, araç
listesi yok, skill metni yok. Senaryo büyüdükçe fark açılıyor, ve büyüyen taraf pahalı olan.

**Neden `note`:** *"3'ün action'ı pasif olmuş, daha dinamik yaz"* diyebilmek için. Notsuz yeniden
çağırmak aynı sorudan aynı cevabı üretir; düzeltme ancak yeni bir cümleyle düzeltme olur.

**Kadroyu seçmiyor.** Kim sahnede olduğuna Queen karar verdi, ve bu bir korkuluğu gereksizleştirdi:
uydurulmuş bir ad **hiç oluşamıyor**, doğrulanacak bir şey kalmıyor.

**Etiketleri görüyor ama yeniden tarif etmiyor** *(kullanıcı kararı, 5 Eylül)*. Etiketler oraya
eylem o kişiye otursun diye giriyor; kişiyi kendi kelimeleriyle anlatmak hâlâ yasak — o iş
karakterin kendi girdisinin.

**Çıktısı ana ajana dönmüyor.** Yazdığı doğrudan dosyaya gidiyor; cevap yalnız bir makbuz — yazıldı,
ya da neden yazılamadı. Metin konuşmaya girseydi kaliteyi düşürürdü.

**Tek kare, tek çağrı** *(kullanıcı kararı, 5 Eylül: önce sade olan)*. Ana ajan isterse aynı raundda
birden çok çağırır. Bütün kareleri tek çağrıda dolduran toplu araç **backlog'da**.

**Hiçbir şey yeniden denenmiyor.** İsteği düşen ya da cevabı ayrıştırılamayan kare boş kalıyor —
aynı kareyi yeniden çağırmak zaten retry'nin kendisi.

### Derlemek ve plan

| Araç | Ne yapar |
|---|---|
| `build_prompts` | Yapıdan `.py` prompt listesi derler. Promptları cevaba basmaz |
| `build_character_prompts` | Tek karakterin önizlemesi |
| `write_plan` | Plan dosyası yazar |

**Toplam 20 araç.** Arşivdeki tasarım 17'ydi; fark üç kaynağın `add`/`update` ayrımı. **Bedeli
açık:** araç tanımları her istekte gidiyor, yani üç tanım daha her raundda taşınıyor. Bilerek ödeniyor — kazanılan şey, modelin bir adın var olup olmadığını bilmeden çağırıp
sessizce üzerine yazamaması.

---

## 3 · Kalkacaklar

- **`read_prompt_structure_schema`** — şekli araçlar devraldı; şema, modelin artık yazamayacağı bir
  formu öğretiyor.
- **`add_frames`** — JSON alıyor. Yerine `add_scene`.
- **`create_file` / `edit_file`'ın `.json`'a erişimi** — kapanıyor, **istisnasız** *(kullanıcı kararı,
  5 Eylül)*. Bozuk bir dosyayı da model onarmaz: araçlar *not valid JSON* der ve durur, model
  kullanıcıya söyler, kullanıcı elle düzeltir.

**Bunun altındaki kural:** model bir **fonksiyon çağırıyor** gibi çalışır — adı, parametreleri ve ne
döndüğü bellidir; dosyanın nasıl saklandığını hiç bilmez. Bu yüzden hiçbir araç modele bir yol
*(`characters/aylin`)* ya da bir tür parametresi *(`kind`)* sormuyor: parametrenin **kendi adı** hem
nereye yazılacağını hem hangi kuralın geçerli olduğunu söylüyor.

---

## 4 · Açık kalanlar

**Maliyet ölçülmedi.** Ana ajanı ucuz modele almak günlük kullanımın tamamında gerçek tasarruf —
ana ajan her sohbette çalışıyor. Ama Grok'a giden yol **çağrı sayısı en yüksek** yol: 40 karelik bir
koşuda 40 taze istek, ve kare istekleri ortak önek paylaşmadığı için cache yok. Ana ajanın konuşması
ise büyüyen sabit önek, yani cache'li.

Yani *"ana ajanı ucuzlatmak tasarruf"* doğru; *"bu yapı toplamda ucuzlar"* ölçülmeden söylenemez.
`Usage` damgası `sent`, `cached` ve `answered` topluyor ve araç kendi harcamasını ayrıca döndürüyor
— bir senaryo üretip iki rakamı yan yana koymak yetiyor. **Denemede bakılacak.**

**Ölçülmemiş iki iddia, kayda öyle geçiyor.** Grok'un action'ı daha iyi yazdığı ve DeepSeek'in
ajanlıkta daha güçlü olduğu — ikisi de kullanıcının kendi gözlemi, bu depoda ölçüm yok. `BREAK`
denemesi de böyle kayda geçmişti.

**Okunan dosya istekte bir kere durur** *(kullanıcı, 5 Eylül: bu koşuya alındı)*. Bugün `read_file`
dosyanın tamamıyla cevap veriyor ve o cevap turun sonuna kadar konuşmada kalıyor; kap aynı dosyayı
yanına koyuyor. `read_file` makbuz döndürür, içeriği yalnız kap taşır. Yol haritasında 179.

**Bu koşuya girmeyen, bilerek:** arşivdeki 160'ın OpenRouter kaydı *(m149 depoda hiç iz bırakmadı)*,
ve yazılan promptların doğrulanması *(`BACKLOG.md`)*.
