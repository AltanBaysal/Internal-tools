# QueenAgent — skill problemleri

**Tarih:** 27 Ağustos 2026 · **Durum:** problem listesi, çözüm değil.

Bu belge çözülecek şeyleri **problem olarak** yazıyor. Amaç, hepsini tek tek madde madde koşmak
yerine önce ne olduklarını net görmek, sonra hepsini birden çözen bir skill yapısı kurmak.

Buradaki problemler v5 yol haritasının 70 ve 75'inden, ve 94'ün bilerek bıraktığı boşluktan geliyor.
**Bağlam yönetimi (71) buraya girmiyor** — o taşıma ve tur döngüsüyle ilgili, skill metnine hiç
dokunmuyor.

---

## Bugün ne var

Madde 94'ten sonra tek skill kaldı: `generate-prompts-plus`. Yaptığı iş, bir yapı dosyasından prompt
listesi kurmak. Yapı dosyası JSON: en üstte `quality`, `characters`, `outfits`, `locations`
haritaları, altında `frames` listesi. Kare, haritalardaki isimleri anıyor; metni tekrar taşımıyor.

Promptu kod kuruyor — `build_prompts` — ve sırası sabit:

```
quality, karakter1, kıyafet1, karakter2, kıyafet2, mekân, action, camera
```

Bu, modelin elle yazmasının yasak olduğu tek yer, ve hayatta kalan skill'i silinen düz skill'den
ayıran tek şey.

**Metinsiz kalan yol:** senaryo yazmak, karelere bölmek, karakter adayları üretmek, dosyaları
denetlemek. Dördü de silinen beş skill'in içindeydi. Bugün bunlar sıradan konuşmayla, yalnız taban
yönergenin yönetiminde yapılıyor.

---

## Problem 1 — Karede iki karakter varsa patlıyor

İki karakterin tarifi promptta **yan yana** duruyor:

```
quality, 1girl teal hair, jeans, 1girl freckles, red dress, bedroom, sitting, medium shot
```

Görüntü modeli bitişik iki kişi tarifini ayıramıyor. Nitelikler birbirine karışıyor — kimin saçı
kimin, kimin kıyafeti kimin belirsizleşiyor. Şikâyetin kendisi: *"iki karakter aynı karede
patlıyor."*

**Kullanıcının söylediği çözüm yönü** *(27 Ağustos)*: iki tarifi birbirinden uzaklaştırmak.

- Ana karakter promptun **başında** kalır.
- **Ana karakter, karenin `characters` listesinde en öne yazılan kişidir** *(kullanıcı kararı,
  27 Ağustos)*. Her karede ayrı belirlenir; şemaya alan girmez. Sebep: sıra zaten bilgi taşıyor —
  yazan model o karede kimi öne çıkarmak istiyorsa onu başa yazar, ve belirlemesi bu kadar kolay
  olur. Senaryo çapında sabit bir ana karakter alanı **düşünüldü ve seçilmedi**.
- Geri kalan herkes promptun **sonuna** gider, `camera`'dan sonra. Araya mekân, action ve camera
  giriyor; iki tarif artık temas etmiyor.
- **Kıyafet her zaman sahibiyle tek blok** taşınır. Kimin neyi giydiğini söyleyen tek şey yan yana
  durmaları.
- Üç kişi olursa ikinci ve üçüncü sonda yan yana kalır. Aralarında aynı risk sürüyor; bilerek kabul
  edildi — temiz kalması gereken ana karakter.

**Açık kalan:** sıra kararı promptun *dilinden* bağımsız mı? Etiket kalırsa evet. Cümleye dönerse
"ana karakter başta, ötekiler sonda" hâlâ aynı sebeple doğru görünüyor ama cümlede ne anlama geldiği
Problem 2'ye bağlı.

---

## Problem 2 — Kişi sayısı yanlış yerde

Bugün sayı etiketi karakter tanımının **içinde**: `"aylin": "1girl, long teal hair"`.

İki sebeple yanlış yerde:

- **Sayı kareye ait, karaktere değil.** Aynı karakter bir karede tek başına, ötekinde biriyle
  beraber. Tanımın içinde taşındığı sürece yarı yarıya yanlış.
- **İki karakterli karede iki kez yazılıyor.** Model `1girl, ..., 1girl` görüyor; iki kadın için
  beklenen tek etiket `2girls`.

**Karar** *(kullanıcı kararı, 27 Ağustos)*: sayı karakter tanımından çıkar ve **karenin kendi
alanına** girer.

```json
{ "people": "2girls", "characters": { ... }, "location": "...", "action": "...", "camera": "..." }
```

- **Yazan model.** Doğrusunu — `1girl`, `2girls`, `1boy, 1girl` — yapıyı yazan model yazar, çünkü
  karede kimin olduğunu ve ne olduklarını o anda bilen o.
- **Yerleştiren kod.** `quality`'den hemen sonra, promptun en başına. SDXL'de sayı etiketi
  kompozisyonu en çok belirleyen şey ve geleneksel yeri baş.

**Neden ayrı alan, action'ın içi değil.** İlk düşünülen yol sayıyı action cümlesine yazdırmaktı.
Bedeli: etiket promptun ortasında kalırdı — action dördüncü sırada — ve kod onu oradan öne
alamazdı, çünkü serbest metnin içinde. Ayrı alan FOUNDATION 5'in tam ayrımını koruyor: kararı model
veriyor, yerleştirmeyi kod yapıyor. Action'a gömülseydi yerleştirme de modele kalırdı ve her karede
yeniden doğru yapması gerekirdi.

**Sayma koda alınmıyor.** Kod kareye kimin girdiğini biliyor ama ne olduklarını bilmiyor — bir
karakterin kadın mı erkek mi olduğu hiçbir alanda durmuyor. Kodun kendi başına sayabilmesi için
şemaya cinsiyet alanı gerekirdi; onun yerine sayının **kendisi** alan oldu.

---

## Problem 3 — Prompt dili · **kapandı: etiket kalıyor**

Burada iki kayıt birbirine ters düşüyordu.

**v5 yol haritası, Madde 75 diyordu ki:** *"prompt dili değişir: çıkan şey etiket dizisi değil, düz
cümledir."* Yani etiketten **cümleye** geçilecek.

**Kullanıcı 27 Ağustos'ta bunun tersini söyledi:** *"promptların cümle ile çıkması problem, SDXL
promptları cümle değil."*

Backlog satırı ikisini de destekleyecek kadar belirsiz yazılmış: *"Promptlar SDXL promptu gibi
değil, cümle şeklinde çıksın."* Hem *"cümle olarak çıksın"* hem *"cümle gibi çıkıyor, oysa SDXL
promptu gibi değil"* diye okunuyor.

**Karar** *(kullanıcı kararı, 27 Ağustos)*: **etiket kalıyor.** Kullanılan model SDXL temelli, ve
SDXL etiketle çalışır. Madde 75'in yazılı hâli yanlış; geçerli olan bu satır.

**Sonucu:** `build_prompts` yaşıyor ve biçim değiştirmiyor. Hayatta kalan skill'in varlık sebebi —
karakteri kod birleştirir, model kopyalamaz — yerinde kalıyor. Problem 1 ve 2'nin kararları doğrudan
uygulanabilir.

**Tek model yok** *(kullanıcı, 27 Ağustos)*: *"birçok model için kullanıyorum, SDXL temelli."* Yani
kalite etiketleri koda gömülmez. Zaten gömülü değiller — yapı dosyasının kendi `quality` alanında
duruyorlar ve senaryo başına ayarlanıyorlar. Doğru yerde.

---

## Problem 4 — Yolun büyük kısmı metinsiz

94 beş skill'i sildi ve bu bilerek yapıldı: nasıl çalışılacağını söyleyen kısımlar taban yönergeye
inmişti, işin kendi bilgisi ya kalan metinde duruyordu ya da gitmesine karar verilmişti.

Gerçekten giden dört şey:

- **Bir karenin ne olduğu** — bir-iki cümle, paragraf değil, numaralı.
- **Kare listesinin kullanıcının dilinde yazıldığı** *(yapı dosyası ve prompt listesi İngilizce
  kalırken)*.
- **Karakter adaylarının hangi dosya biçiminde verildiği** — yapının haritalarıyla aynı şekilde,
  yapıştırılabilir JSON.
- **"Dosyalarımı denetle" yolu** — kural kitabı artık yalnız kurma anında uygulanıyor.

Bugün bir kullanıcı *"senaryoyu karelere böl"* dediğinde model yalnız taban yönergeyle çalışıyor ve
karenin ne olduğunu her seferinde yeniden kuruyor. Seçenek 2'nin kabul edilmiş bedeli buydu.

**Soru:** yeni skill yapısı bu dördünün hangilerini geri alıyor, ve nereye — kalan metnin içine mi,
yeni bir skill'e mi?

---

---

## Araştırma — SDXL promptu nasıl olmalı

*27 Ağustos'ta arandı. Kaynaklar aşağıda.*

### `BREAK` — Problem 1'in bilinen çözümü

A1111'de `BREAK` promptu parçalara bölüyor: CLIP'in bağlam penceresini sıfırlıyor, sonraki bloğu
bağımsız kodluyor, sonra birleştiriyor. Var olma sebebi tam olarak *"iki kavram birbirine
karışmasın"*.

Doğru kullanımı bizim vakamız: **karıştırılmak istenmeyen gruplar arasına** konur —
`woman in red dress BREAK man in blue suit`. Yanlış kullanımı tek bir karakteri içeriden bölmek
(`saç BREAK göz BREAK kıyafet`), çünkü onlar aynı gruba ait.

Bu, konuştuğumuz *"ikinci kişiyi promptun sonuna at"* fikrinden **daha güçlü**: mesafe karışmayı
azaltır, `BREAK` kodlamayı gerçekten ayırır. Ve blokları bozmadığı için kıyafet sahibiyle kalır.

**Şartı arayüz, model değil:**

| Arayüz | Durum |
|---|---|
| A1111, Forge | yerleşik |
| ComfyUI | **yerleşik değil** — `Conditioning (Concat)` düğümü ya da `comfyui-clip-with-break` eklentisi gerekiyor |

Desteklenmeyen bir yerde `BREAK` promptun içine **kelime olarak** kodlanır, yani zararlıdır.

**queen-editor bugün desteklemiyor** *(27 Ağustos'ta `workflow_api.json` okunarak doğrulandı)*.
Pozitif yol tek zincir — `3` POSITIVE → `39` `RegexReplace` → `36` `CLIPTextEncode` — ve grafikte
`Conditioning (Concat)` hiç yok. Yazılan bir `BREAK` zincirden dokunulmadan geçip kelime olarak
kodlanır.

**Karar: `BREAK` şimdi kullanılmıyor, sonra kullanılacak** *(kullanıcı kararı, 27 Ağustos)*. Bu
koşuda Problem 1'in ilacı sıra düzeltmesi: ana karakter başta, geri kalan `camera`'dan sonra.
Gerekçesi elde ölçüm olması — kullanıcı sıra düzeltmesini elle deneyip işe yaradığını gördü, oysa
`BREAK` için önce queen-editor'ün düğümü açması gerekiyor. `BREAK` güncellemesi bir sonraki haftaya
bırakıldı.

İş iki backlog'a birden geçti, çünkü iki depoyu birden açıyor:
[queen-editor](../queen-editor/BACKLOG.md) — açılacak düğüm ve bedeli;
[queen-agent](../queen-agent/BACKLOG.md) — düğüm açıldığında `build_prompts`'ın ne yapacağı.

**Sıra düzeltmesinin kayda geçen şüphesi:** erken jetonlar daha ağır bastığı için ikinci karakteri
sona atmak onu ayırmakla kalmayıp zayıflatabilir. Kullanıcının ölçümü işe yaradığını söylüyor, ama
şüphe `BREAK` geldiğinde yeniden sorulacak: o gün iki ilacın ikisine birden gerek olup olmadığı
karara bağlanır.

### Sıra gerçekten önemli

Öndeki token'lar dikkat mekanizmasında daha ağır basıyor. `people` alanını en başa koyma kararımız
(Problem 2) bu bulguyla örtüşüyor.

### Kalite etiketleri

Bugünkü örnek `score_9_up, masterpiece, best quality, absurdres`. Bu Pony türevi bir modelin biçimi,
ve araştırmaya göre eksik: Pony'de sıra `score_9, score_8_up, score_7_up` diye gider — **en az üç**
skor etiketi isteniyor, yalnız biri iyi sonuç vermiyor. Pony'de zorunlu, Illustrious'ta isteğe bağlı.

Kullanıcı tek modele bağlı olmadığı için bu koda girmiyor; yapı dosyasının `quality` alanında,
kullanıcının kendi kararı olarak duruyor. Ama **skill metnindeki örnek** düzeltilebilir.

### Kaynaklar

- [BREAK ve kavram karışması — krita-ai-diffusion #2292](https://github.com/Acly/krita-ai-diffusion/issues/2292)
- [Forge Couple ve BREAK sözdizimi](https://note.com/nonb0716/n/n02ce7117ac22?hl=en)
- [SDXL prompt rehberi](https://imgtoprompt.app/guide/sdxl)
- [Pony Diffusion XL prompt etiketleri](https://stable-diffusion-art.com/pony-diffusion-prompt-tags/)
- [Pony ile Illustrious karşılaştırması](https://aiofm.info/en/guides/pony-vs-illustrious)
- [comfyui-clip-with-break](https://github.com/dfl/comfyui-clip-with-break)

---

## Yeni yapı — iki skill, biri akış

*(kullanıcı kararı, 27 Ağustos)*

İki skill olacak. `generate-prompts-plus` bugünkü işini yapmaya devam ediyor; yanına **onu besleyen
bir akış skill'i** geliyor.

Bu, silinen üç skill'i geri getirmek **değil**. Fark: kullanıcı arada skill değiştirmiyor. Tek metin
çağrılıyor, ve o soruyor — anlamadığı yerleri kapatarak ilerliyor. Madde 74'ün asıl istediği de
buydu.

### Akış skill'i ne yapıyor

1. **Karakterleri sorar.** Projede var mı, yoksa kullanıcının aklında mı. **Promptu var mı diye
   sorar** — varsa alır, yoksa kullanıcı anlatır ve skill promptu kendisi kurar.
2. **Mekânları da sorar.** Karakterle aynı şekilde; ikisi de kareye bağlam veriyor.
3. **Bir karakteri tek başına denemek için Python listesi kurabilir** — kullanıcı isterse. Amaç
   karakteri işlemeden önce görmek: *"bakayım nasıl görünüyor."*
4. **Hikâyeye geçer:** karelerde ne görmek istendiğini sorar.
5. **Kullanıcı onaylayınca kareleri oluşturur ve açıklar.**
6. Kareleri **JSON'a yazar**; md ise kullanıcının okuması için açıklamadır *(karar: aşağıda)*.
7. Kullanıcı `generate-prompts-plus`'ı çağırır; o kural kitabını uygulayıp `build_prompts` çağırır.

### Kareler nerede yaşıyor

**JSON asıl kaynak** *(kullanıcı kararı, 27 Ağustos)*. Akış skill'i hem haritaları hem `frames`
dizisini yapı dosyasına yazıyor. md ise kullanıcının kendi dilinde okuduğu açıklama — *"1. kare:
Aylin barda oturuyor, kamera omuz üstü"*.

Alternatif düşünüldü ve seçilmedi: kareleri md'de tutup prompt+'ın onu JSON'a çevirmesi. Sebep aynı
bilginin iki biçimde yaşaması olurdu, ve kural kitabının 4. maddesi tam olarak bunu yasaklıyor —
kopya serbest, kaymış kopya değil.

### Yeni araç gerekmiyor

Tek karakterlik deneme mevcut makineyle çıkıyor: küçük bir yapı dosyası — kalite etiketleri, o tek
karakter, ve içinde yalnız onun olduğu tek bir kare — sonra `build_prompts`. Çıktı tek satırlık bir
`PROMPTS` listesi, yapıştırılmaya hazır.

---

## Yeni yapının cevaplaması gerekenler

1. ~~**Prompt dili nedir**~~ — **kapandı:** etiket kalıyor. `build_prompts` yaşıyor ve biçim
   değiştirmiyor.
2. ~~**`BREAK` kullanılacak mı**~~ — **kapandı:** bu koşuda hayır, düz string prompt üretiliyor.
   İş iki backlog'a geçti; şartı queen-editor'ün `36` numaralı düğümü açması.
3. **Kaç skill olacak** — tek metin mi kalıyor, yoksa senaryo/kare/karakter için yenileri mi doğuyor.
   **Açık.**
4. **Şema ne kadar değişiyor** — `people` alanı girdi *(Problem 2)*. Ana karakter için alan
   **girmiyor** *(Problem 1)*. Başka bir şey var mı, açık.
5. **Diskteki dosyalar** — bugünkü yapı dosyaları `people` alanı taşımıyor ve karakterlerinin içinde
   sayı var. Dönüştürülecek mi, iki biçim birden mi okunacak, yoksa oldukları gibi mi bırakılacak.
   **Açık.**

## Kapsam dışı

- **Madde 71 — bağlam yönetimi.** Taşıma ve tur döngüsü; skill metnine dokunmuyor.
- **Backlog'da duran "Prompt listesi karışıyor".** Bu koşuya hiç girmedi.
