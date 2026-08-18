# QueenAgent Beceriler — Kullanıcıyla Tasarım Kararları

**Tarih:** 2026-08-18 · **Durum:** konuşmada anlaşıldı; Madde 27-30 spec'leri buradan yazılacak
**Bağlam:** [yol haritası](../plans/2026-08-15-queenagent-v2-roadmap.md) Madde 27 ve Faz 7'nin başındaki
"dur ve birlikte tasarla" durağı işletildi. Karar 18'in verdiği üçlü küme bu konuşmada büyüyüp
değişti; aşağıdaki her karar kullanıcıyla varılmış anlaşmadır.

---

## 1 · Büyük resim

QueenAgent bir üretim hattının ön yüzü: **senaryo → kare listesi → yapı JSON'u → `PROMPTS`
listesi**. İlke ikiye ayrılır:

- **Ara ürünler sohbette yaşar, kullanıcı onaylar; diske yalnız onaylanmış şey iner.**
- **Metni model yazar, birleştirmeyi kod yapar.** Tutarlılığın garantisi modelin dikkati değil,
  deterministik bir komut.

## 2 · Beceri kümesi — üç değil, altı

| # | Beceri | Okur | Bırakır |
|---|---|---|---|
| 1 | Create scenario | — | `scenario.md` — **10-15 cümle**, hikâye örgüsü, detaysız (sayı yönergeye yazılır, dilek olarak değil) |
| 2 | Create character prompt | — | **sohbet** — SDXL standardında adaylar; hiçbir dosyaya yazmaz. Kullanıcı dener, beğenmezse yeniden ürettirir; yapıya girmek ayrı ve kullanıcının ağzından çıkan bir iştir ("bunu aylin olarak ekle") |
| 3 | Split into shots | `scenario.md` | **sohbet** — kare başına prompt dilinde tek satır; kullanıcı okur, düzelttirir |
| 4 | Generate prompts | sohbetteki kare listesi | `prompts.py` — her promptu model tek parça yazar; yapı yok. **Kontrol grubu** |
| 5 | Generate prompts+ | sohbetteki kare listesi + karakter/mekân promptları | yapı JSON'u → `build_prompts` → `prompts.py` |
| 6 | Verify shots | yapı dosyaları | **sohbet** — ihlal raporu; düzeltmez, düzeltme kullanıcının "düzelt" demesiyle |

4 ile 5 aynı girdiden aynı biçimde çıktı verir — "yapı kaliteyi artırıyor mu" sorusu iki
`prompts.py` yan yana üretilerek cevaplanacak. Tasarım kendi deneyini içinde taşıyor.

Kare listesi sohbette yaşadığı için **3 → 4/5 aynı sohbette akar**; başka sohbete taşımak
yapıştırmakla ya da "listeyi dosyaya yaz" demekle olur. Bilinçli tercih.

## 2b · Beceri talimatı bağlama nasıl girer

**Yol haritasının Faz 7 girişindeki "seçili beceri, o sohbetin sistem yönergesine kendi ekini koyar"
cümlesi yanlış; bu madde onun yerine geçer.** Kullanıcı itiraz etti, Anthropic'in kendi Agent Skills
mimarisi okundu (`platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`, 18 Ağustos
2026) ve kullanıcı haklı çıktı. Oradaki kademeli açılım:

| Kademe | Ne | Nerede | Ne zaman |
|---|---|---|---|
| 1 | yalnız ad + açıklama (~100 token) | sistem yönergesinde, hep | başlangıçta |
| 2 | `SKILL.md` gövdesi | **konuşmaya girer**, orada kalır | tetiklendiğinde, **bir kez** |
| 3 | ek dosyalar / scriptler | dosya okunursa bağlama; script ise **yalnız çıktısı** | gerektiğinde |

Talimat gövdesi her istekte sistem yönergesine enjekte edilmiyor — bir kez konuşmaya düşüyor.

**QueenAgent'ın uyarlaması:**

- Her mesaj **hangi beceriyle gönderildiğini kendinde taşır** (`message.skill`). Kayıt dürüst olur:
  hangi turu hangi kural yönetmiş, geriye dönük değişmez. Sistem yönergesi yaklaşımında beceriyi
  değiştirmek geçmiş turların kuralını da değiştirmiş gibi görünürdü.
- Konuşma xAI için kurulurken, bir becerinin talimatı **o beceriyle gönderilen ilk mesajın hemen
  önüne** `system` rolüyle konur; aynı beceriyle art arda giden mesajlarda **tekrarlanmaz**. Beceri
  değişirse yenisi bir kez girer.
- Talimat **görünür bir mesaj değil** — transkriptte yalnız kullanıcı ve model cümleleri durur.

Sonuç: bir kez gider, birikmez, kayıt dürüst kalır, ekran temiz kalır. Ayrıca önceki adımların
kuralları bağlamda kaldığı için `Create scenario → Split into shots → Generate prompts+` zinciri
akarken model önceki adımın kuralını da görür.

**Yan onay:** Anthropic'in 3. kademesi "scriptler koşar, kodu bağlama girmez, yalnız çıktısı girer"
diyor — `build_prompts` kararı tam olarak bu desen.

**Beceri seçimi mesajdan sonra seçili kalır.** Düzeltmeler ("3. kareyi düzelt") aynı beceriyle
devam ediyor; her mesajda yeniden seçmek yorar. Güvenli olmasının şartı yönerge dili: talimatlar
**"bu işi şöyle yaparsın"** diye yazılır, **"şunu yap"** diye değil — ne yapılacağını kullanıcının
mesajı söyler. Böylece seçili bir beceri, istenmeyen bir üretimi kendiliğinden tetiklemez.

## 3 · Tool katmanı

Düz küme; hiçbir tool bir becerinin malı değil, her beceri hepsini çağırabilir. Format başına tool
yok (`json_read` vs. açılmadı) — ayrım formatta değil fiildedir; JSON da md de dosyadır ve
`read_file` ikisini de okur.

| Tool | Durum | Not |
|---|---|---|
| `list_files` · `read_file` · `create_file` | var | |
| `edit_file` | **yeni** | hedefli değişiklik; genel, JSON'a özel değil. Şart, çünkü `create_file` asla üstüne yazmaz (aynı ad `-2` alır) — güncelleme akışı bunsuz hiç çalışmaz |
| `build_prompts` | **yeni** | kullanıcının cümlesiyle: "sadece bir command çağırmak olsun, kod yapsın." Saf kod, aşağıda |

**Karar 18'in "yeni araç gerekmiyor" cümlesi düştü** — Madde 31 belgelere işleyecek. Beceri sayısı
da üçten altıya çıktı; aynı maddede güncellenir.

## 4 · Yapı JSON'u — son hâl

Senaryo başına bir dosya, adı senaryodan türetilir (`intro-shots.json`). Projede aynı anda birden
çok senaryo yaşayabilir. Proje seviyesinde ortak `library.json` **istenmedi** (aşağıda, reddedilenler).

```json
{
  "quality": "score_9_up, score_9, score_8_up, masterpiece, best quality, raw, 4k, absurdres",
  "characters": { "aylin": "1girl, long teal hair, ..." },
  "locations":  { "bedroom": "sunlit bedroom, morning light, ..." },
  "shots": [
    {
      "characters": ["aylin"],
      "location": "bedroom",
      "action": "sitting on the edge of the bed, holding a letter, pensive expression",
      "camera": "medium shot, from slightly above"
    }
  ]
}
```

**Tek alan: `quality`.** Kalite ve stil etiketleri ayrılmadı — kullanıcı kararı. Bir stil
tetikleyicisi kullanılacaksa aynı dizginin içinde durur; ayrı `style` alanı yok.

- Üstte **tekrar edenler** kendi map'lerinde; kareler metni değil **adı** taşır. Karakteri
  güncellemek = map'te tek değer; bütün kareler döner.
- Kare alanları ayrı ayrı (`action` / `camera`), böylece model düzenlerken yalnız ilgili alana
  dokunur — alan izolasyonu kullanıcının bu yapıyı seçme sebebidir.
- **`characters` liste, `location` düz string — bilerek asimetrik:** bir karede birden çok karakter
  olabilir, bir kare tek yerde geçer. Biçimin kendisi kural anlatır. Karaktersiz kare boş liste.
- Kıyafet değişimi gibi durumlar şemayı büyütmez: ikinci map girdisi açılır (`"aylin_gecelik"`).
- Kare çıkarmak = listeden silmek; numaralar kayar, bilinir ve kabul edilir.

## 5 · `build_prompts` kuralları

1. Ad çözümü **kodda**: `characters`/`location` alanları kendi map'lerinde aranır; bilinmeyen ad =
   **isimli hata** ("aylinn yok; bilinenler: aylin, bedroom"). Tool tahmin etmez; model bakıp
   düzeltir ya da kullanıcıya sorar.
2. Birleştirme sırası kodda sabit ve kesinleşti:
   **`quality → characters → location → action → camera`**.
3. `quality` her kareye **kod tarafından**, en başa eklenir: değişmeyeni kod garanti eder, değişeni
   alan taşır. Baş/kuyruk ayrımı yok — hepsi başta.
4. Uçlardaki virgül/boşluk normalize edilir (`", ,"` sızamaz).
5. Çıktı `prompts.py`, kopyala-yapıştır hazır — üç tırnak, trailing comma, değişken adı `PROMPTS`
   (yol haritası Madde 30'un "çıktı bir Python listesidir" cümlesi geçerli):

```python
PROMPTS = [
    """<kare 1>""",
    """<kare 2>""",
]
```

6. **Çıktının adı kaynaktan türer** (Madde 28 spec'inde çözüldü): aynı gövde, `.py` uzantısı —
   `intro-shots.json` → `intro-shots.py`. Yukarıdaki "`prompts.py`" o dosyanın **türünü** anlatıyor;
   sabit tek ad, §4'ün "bir projede birden çok senaryo yaşayabilir" cümlesiyle çelişir ve iki
   senaryoyu birbirine yazdırırdı. Ve bu tek dosya **üstüne yazılır**: türev üründür, yeniden üretmek
   maddenin bütün amacıdır; numaralasaydı hangisinin güncel olduğu kaybolurdu.

## 5b · Çalışma kuralı — küçük parçalar, asla tek nefeste

Kare listesi uzayabilir; model **hiçbir beceride** hepsini tek üretimde yazmaya çalışmaz. Kural
yönergelere dilek olarak değil, mekanik olarak girer:

- **prompts+:** önce iskelet (`style` + map'ler + boş `shots`) `create_file` ile; sonra kareler
  `edit_file` ile **beşerli partiler** hâlinde eklenir. Her parti diske iner, sonra sıradakine
  geçilir. Uzun tek üretimde kalite sona doğru düşer ve kesinti her şeyi götürür; partili yazımda
  en çok bir parti gider.
- **Split into shots:** sohbette aynı ritim — sahne sahne dökülür, tek cevapta boca edilmez;
  kullanıcının aralarda düzelttirmesine doğal olarak yer açılır.

## 5c · Örnek prompttan çıkanlar

Kullanıcının kendi çalışan promptu (18 Ağustos) alanlara bölündü:

| Alan | Örnekteki karşılığı |
|---|---|
| kalite | `score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres` |
| stil | `morimee_style` (LoRA tetikleyicisi) |
| `characters.X` | `1girl, solo, woman in her mid 20s, goth woman, ... , oversized long black t-shirt, black thong, bare shoulders` |
| `locations.X` | `apartment doorway, daytime, natural light, indoors` |
| `action` | `standing in doorway, door opening, light blush, soft flirty smile, self-aware teasing, slight sweat sheen, looking at viewer` |
| `camera` | `full body` |

**Kalite etiketleri promptun iki ucunda duruyordu** (`score_*` başta, `raw, 4k, absurdres` sonda);
kullanıcı "hepsi başa yazılabilir" dedi — **baş/kuyruk ayrımı yok**. Sıra kesinleşti:

`kalite + stil → characters → location → action → camera`

**Adlandırma düzeltmesi:** önceki taslakta `style` denen şeyin çoğu aslında **kalite** etiketiydi;
gerçek stil yalnız `morimee_style`. Alan adları buna göre düzeltildi (ayrı mı birleşik mi — açık).

**`solo` / sayı etiketi: kural yok — kapsam dışı.** İki karakterli bir karede karakter girdilerinin
içindeki `1girl, solo` iki kez geçer ve yanlış söyler. Kullanıcı bunu **bir sorun olarak ele almamayı
seçti**: `build_prompts` sayı ya da `solo` etiketine hiç dokunmaz, girdiler ne yazıyorsa aynen
geçer. İhtiyaç doğduğunda kullanıcı çözecek. Spec'te bu böyle yazılır; kod tarafında sessiz bir
zeka **yoktur** — o yanlış çıktı ekranda görülür ve düzeltilir.

**Uyarı (karar değil):** kullanıcının negatifi kıyafete bağlı etiketler taşıyor (`white t-shirt,
jeans, skirt, bra` — karakterin kıyafetini koruyan negatifler). Negatif JSON'un dışında olduğu için
kıyafet değişince (`aylin_gecelik` gibi) negatif elle güncellenmeli; kod bunu göremez. İstenirse
verify defterine "kıyafet değişti mi, negatifi kontrol et" diye bir **not** maddesi eklenir.

## 6 · Verify defteri

Kodun göremediğini model görür. Kurallar "şu varsa ihlaldir" dilinde:

1. Map'te karşılığı varken `action`/`camera` içinde **düz metin** karakter/mekân tarifi → ihlal.
   Asıl av: sessiz kopyanın geri dönüşü.
2. `style` etiketlerinin karede tekrarı → ihlal (kod zaten ekliyor; çift basar).
3. Aynı adın iki senaryo dosyasında **farklı metni** → ihlal. `library.json`'suz yaşamanın bedelini
   ödeyen kural: kopya serbest, **sapmış kopya** yakalanır.
4. Tanımlı ama hiç anılmayan ad → not, ihlal değil.

İki kapı: prompts+/düzenleme yönergelerinin **son adımı** (öz-denetim `build_prompts`'tan **önce**
koşar — kirli yapıdan liste üretilmez) ve menüden istendiği an. **Verify düzeltmez, rapor eder** —
hangi dosya, hangi kare, ne ihlali. Özellikle 3. kuralda "hangisi doğru kopya" kararı modelin değil
kullanıcınındır.

## 7 · Reddedilenler — yeniden önerilmesin

| Fikir | Neden düştü |
|---|---|
| `negative` alanı | kullanıcı negatifi ayrıca veriyor; normal prompta karışmıyor |
| `"skip": true` | kullanıcı istemedi; kare çıkarmak silmektir |
| Proje seviyesinde `library.json` | kullanıcı istemedi; sapma riski verify kural 3 ile yakalanır |
| Placeholder'lı şablon dizgiler (`"{aylin}, {bedroom}, ..."`) | denendi, alanlı yapıya çevrildi: yerleşim özgürlüğü veriyordu ama düzenleme izolasyonu vermiyordu; kullanıcının önceliği ikincisi. Alanlarla ad denetimi de tamamen koda geçti |
| Format başına tool (`json_read`, `md_read`) | aynı işi yapan iki kapı; ayrım fiildedir, formatta değil |
| Kare başına `description` alanı | `action` zaten prompt dilinde ve okunur; ikinci alan zamanla sapardı |

## 8 · Sınırlar ve bir düzeltme

- **Bu yapı prompt tutarlılığını garanti eder, görsel tutarlılığı değil.** SDXL aynı tarife her
  seed'de aynı yüzü çizmez; o cephe pipeline'ın işidir.
- **WAN'ın "parçalardan birleştirme" yasağı buraya geçmez.**
  [2026-07-20 spec'inin](../specs/2026-07-20-t2v-prompt-list-design.md) kuralı UMT5-XXL'e (akan
  cümlelerle eğitilmiş video encoder'ı) özgüdür. Nova 3DCG bir SDXL/Illustrious modelidir, Danbooru
  etiketleriyle eğitilmiştir — virgülle ayrılmış etiket öbekleri orada yerel dildir. Ters modelde
  ters teknik; alanlardan birleştirme burada o negatif sonucun tekrarı değildir.

## 9 · Yan iş — okuyucunun mono gösterimi

Okuyucu (Madde 23) her dosyayı Markdown çizer; `.json`/`.py` için yanlış — girintiyi yutar. Beceri
fazının spec'ine girecek: `.md` Markdown, gerisi **mono, biçimi korunmuş**. JSON'ları arayüzde
gerçekten görebilmek buna bağlı.

## 9b · Dil

Uygulamanın kendi kuralı sürüyor: **QueenAgent'ın arayüzü ve kodu İngilizce.** Buna beceri
**yönergelerinin metni** de dahil — talimatlar İngilizce yazılır.

**Zorunlu İngilizce olanlar:** üretilen promptlar, yapı JSON'unun içeriği (`quality`, `characters`,
`locations`, `action`, `camera` — hepsi etiket dili), ve `prompts.py`'deki liste. Bunlar SDXL'e
gidiyor; başka dil olamaz.

**Senaryonun dili belirtilmiyor** — kullanıcı hangi dilde isterse. Türkçe bir senaryodan kare
açıklaması üretilirken model İngilizceye geçer; bu bilerek ve sorun değil.

> **Güncelleme (18 Ağustos, Madde 37).** Bu artık senaryoya özel bir kural değil, **uygulamanın
> kuralı**: sistem yönergesindeki "in English" düştü, model sorulan dilde cevap veriyor. Senaryo
> yönergesindeki dil cümlesi de kalktı — tekrarlanan kural sapar. Zorunlu İngilizce olanlar aynen
> duruyor (promptlar, yapı JSON'u), çünkü onları okuyan bir görüntü modeli.

## 10 · Açık kalan yok

Konuşma kapandı; spec'ler bu belgeden yazılabilir. Kapanma sırası: örnek prompt alındı (§5c) ·
karakter girdisi şimdilik örnekteki gibi, sorun çıkarsa çözülür · `quality` tek alan (§4) · dil
(§9b) · kare sayısı sohbette birlikte (§11) · beceri seçimi seçili kalır (§2b) · `solo` kapsam dışı
(§5c).

Sonradan çıkacak sorular bu belgeye eklenir; **spec'ler bunun türevi**, tersi değil.

## 11 · Yol haritasına etkisi

Madde 27-31 bu belgeye göre yeniden dilimlendi: **28** tool katmanı (`edit_file`, `build_prompts`),
**29** üreten üç beceri (senaryo · karakter · kareler), **30** prompt üreten üç beceri (düz · yapılı
· denetleyen), **31** belgeler. Faz 8'in numaraları **korundu** — kaydırmak yazılmış spec'lerdeki
otuza yakın çapraz referansı ("gözle doğrulama Madde 35") yanlış hâle getirirdi. Madde 35'in elle
turu altı beceriye ve okuyucunun mono gösterimine göre genişletildi. Madde 31, karar 18'in iki
eskiyen cümlesini (üç beceri; yeni araç gerekmiyor) belgelere işler.

**Faz 7 girişindeki cümle yanlış ve düzeltilecek:** "seçili beceri, o sohbetin sistem yönergesine
kendi ekini koyar" — §2b'deki mekanizma geçerlidir (talimat konuşmaya bir kez girer, mesaj hangi
beceriyle gönderildiğini kendinde taşır).

Ayrıca **kare sayısı** yol haritasında soru olarak duruyordu: sohbette **kullanıcı ve model birlikte
kararlaştırır** — ne kullanıcı dayatır ne model tek başına seçer.
