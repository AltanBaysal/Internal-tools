# Madde 479 · Ajan karakter karışmalarını bulur — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
479 · v10-7a · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde 20 Ekim'de hizalandı. Tasarımın tek açık sorusu — kontrol ana sohbetin içinde mi,
kendi isteğinde mi yapılır — ana ajana soruldu, ana ajan 20 Ekim'de ikincisini seçti (aşağıda,
"Neden ayrı bir istek").

## Ne, neden

Kullanıcı ajandan karakter karışmalarını isteyince ajan kareleri birer birer inceler: her karenin
fotoğrafını o fotoğrafın prompt'uyla karşılaştırır. Doğru hâl karenin kendi prompt'udur. Sebep
aranmaz. Saç yalnız bir örnektir; göz, kıyafet, ten ya da başka bir özellik de karışabilir. Videosu
olan kareye dokunulmaz. Sonunda sohbete tek bir liste yazar, üç grupta:

- karışan kareler, her biri neyin karıştığıyla;
- emin olmadığı kareler, her biri kullanıcıya sorusuyla;
- atlanan kareler, her biri nedeniyle — videosu olanlar "videosu var, atlandı".

Hiçbir şey değişmez, izin sorulmaz. Ajan bugün olduğu gibi yalnız okur.

## Bugün — koddan okunanlar

- **Ajanın iki aracı var**, ikisi de yalnız okur ve yalnız bir kare numarası alır: `read_frame` ve
  `look_at_frame` (`features/agent/domain/tools.py`).
- **Kareler sırasıyla ve hangisinin videosu olduğu zaten veriliyor.** Sorudan önce modele her kare
  bir satır olarak gidiyor: numarası, durumu, `layers` (`["photo", "video"]`…), `owed`, `failed`.
  Yeni bir okuyucu gerekmiyor.
- **Bir resim modele `look_at_frame` ile gidiyor:** PNG olduğu gibi, base64, bir kullanıcı mesajında.
  O mesaj sohbette kalıyor, ve döngünün her turu bütün sohbeti yeniden gönderiyor. En fazla 32 tur.
- **Başarısız bir video da `layers`'ta görünüyor:** `layers.TAKEN` `done` ve `failed`'ı birlikte
  sayıyor. Böyle bir karenin `failed`'ında da `video` var.
- **Ekran** her adımı sunucunun iki cümlesiyle gösteriyor ve cevabı `white-space: pre-wrap` ile
  yazıyor; liste satırlarıyla görünür.

## Neden ayrı bir istek

Talimat ve bugünkü iki araçla yapılan bir kontrol, 48 karelik bir projede her kare için `read_frame`
ve `look_at_frame` demek: 96 araç çağrısı. 32 tur sınırı turda en az iki kare ister. Her tur bütün
sohbeti, görülen her fotoğrafla, yeniden gönderdiği için turda k kare bakılırsa
48 · (48/k + 1) / 2 resim gönderilir: k = 2'de 600, k = 4'te 312, k = 8'de 168. Son istek 48
fotoğrafın hepsini taşır (her biri birkaç MB'lık 1536 × 864 PNG, base64'te 4/3'ü), ki DeepSeek'in
büyük ihtimalle reddedeceği bir gövde. Küçük projede çalışır, büyükte düşer, maliyet N² ile büyür.

Bu yüzden karşılaştırma **kendi isteğinde** yapılır: yeni bir okuyan araç, `check_frame`, bir karenin
fotoğrafını ve prompt'unu Queen AI'a ayrı bir soru olarak sorar ve sohbete yalnız kararı, kelimelerle
döndürür. Sohbet hiçbir resim tutmaz; her fotoğraf bir kez gider.

## Ne değişir

### 1. `check_frame` — üçüncü okuyan araç (`domain/tools.py`)

Öteki ikisinin biçiminde: yalnız `frame` (tam sayı) alır, proje almaz, bir adım yazar —
"`N` numaralı kareyi prompt'uyla karşılaştırıyor…" / "… karşılaştırdı".

**Önce yalnız karttan, diske gitmeden** — karşılaştırılacak bir şey yoksa resim okunmaz, soru
sorulmaz, adım yazılmaz (bir şey okunmadı), ve modele nedeni döner:

1. **Videosu var** (`video` `layers`'ta ve `failed`'da değil): "Frame N has a video, so it is not
   checked." Kural yalnız kodda; talimat modele her kareyi çağırmasını ve bu cevabı alan kareyi
   "videosu var, atlandı" diye listelemesini söyler.
2. **Fotoğraf başarısız** (`photo` `failed`'da): "The photo of frame N failed, so there is nothing to
   compare." Başarısız bir katman da `layers`'ta durur (başarısız slot doludur), ama fotoğraf yok.
3. **Fotoğraf katmanı yok:** "Frame N has no photo."
4. **Fotoğrafın prompt'u yok:** "Frame N has no photo prompt to compare the photo with." Doğru hâl
   prompt'tur; o yoksa karşılaştırılacak bir şey yok.

**Sonra, adım sohbette yazılıyken:**

5. **Resim okunur.** Okunamazsa (`OSError`, ör. kopmuş bağlantı) modele "The photo of frame N could
   not be read: <işletim sisteminin cümlesi>" döner ve soru devam eder — önceki kararlar kaybolmaz.
   Diskte yoksa "Frame N has no photo."
6. **Queen AI'a sorulur**, `ask` ile, prompt yazıcılarının fotoğraf gönderdiği yoldan: talimat
   `MIXUP_RULES + MIXUP_CHECK + SYSTEM_PROMPT_SUFFIX` — önce kurallar, sonra iş ve karar biçimi, en
   sonda sahibinin suffix'i —, metin `Prompt: <fotoğrafın prompt'u>`, tek resim
   `(dosya adı, baytlar)`. Modele "Frame N: <karar>" döner.
7. **Kutu başarısız dönerse:**
   - **ret** (`refused`): o karenin satırıdır, "The check of frame N failed: <ret cümlesi>"; soru
     devam eder, başka bir kare cevaplanabilir;
   - **teknik hata:** servis düşmüştür ve sonraki her kontrol de ona çarpar. Soru, başarısız bir
     turun bittiği gibi, kutunun kendi cümlesiyle başarısız biter; o turun kalan çağrıları ve yeni
     bir tur gönderilmez *(reviewer'ın kararı, 20 Ekim)*.

Başarısız bir video bir video değildir: o kare kontrol edilir. Kullanıcının sözü "videosu var";
kırmızı bir video karesinde video yok.

**Adım işten önce, üç araçta da.** `run_tool(ask, frames, picture, project, call)` `(adım, iş)`
döner: adım yalnız karttan bilinir, iş (`work()`) okumayı ve soruyu yapar ve
`(modele dönen, gösterilecek parçalar)` verir. Döngü önce adımı yazar, sonra işi çalıştırır; yani
yavaş bir kontrol sürerken sohbet ne yapıldığını söyler. Teknik hata `QueenAIFailed` olarak
yükselir, döngü onu yakalar. `run_tool` kutunun yalnız `ask`'ini alır. Araç adları `TOOLS`'tan
okunur, elle yazılmış ikinci bir liste yok.

### 2. Kararın biçimi — 481 de okur

`MIXUP_CHECK` kararı tek satır, İngilizce ister, üç sözden biriyle başlar:

- `OK` — hiçbir özellik karışmamış.
- `MIXED: <fotoğrafta özelliği taşıyan karakter>, <özellik>, <prompt'un özelliği verdiği karakter>`
  — ör. *MIXED: the woman has white hair in the photo; the prompt gives white hair to the man and black
  hair to the woman.*
- `UNSURE: <kullanıcıya tek soru, karakteri ve özelliği adıyla>`.

Kod kararı ayrıştırmaz, modele olduğu gibi verir. Ana ajan listeyi kararlardan yazar; `UNSURE`'ların
sorusu listenin ikinci grubu, yani "emin değilse sohbette sorar" budur. 481 ilk sözle `MIXED`'leri
ayırabilir.

### 3. Talimat (`domain/prompt.py`)

- **`INSTRUCTION`** `check_frame`'i Context'e ekler, ve yeni bir bölüm: *Checking for mix-ups* —
  kullanıcı isteyince her kare için, 1'den yukarı, hepsi aynı turda `check_frame` çağır; sebep arama,
  bir şey değiştirme; sonunda üç gruplu tek liste. Atlananlar grubu aracın verdiği nedenle yazılır:
  videosu var dediği kare "videosu var, atlandı"; fotoğrafı, prompt'u olmayan, fotoğrafı başarısız
  ya da kontrolü başarısız olan kare kendi nedeniyle. Hangi karenin videosu olduğunu talimat
  tanımlamaz; kural yalnız kodda.
- **`CHECK_FRAME`** aracın açıklaması.
- **`MIXUP_CHECK`** tek kontrolün talimatı: prompt doğrudur; her karakterin prompt'taki özelliklerini
  fotoğraftakiyle karşılaştır; saç bir örnek; sebep arama; kameranın gizlediği bir özelliğin
  yokluğu karışma değildir, aynı özelliğin başka karakterde olması karışmadır; yukarıdaki karar
  biçimi.
- **`MIXUP_RULES`** QueenAgent'ın kuralları, kopya (aşağıda).

### 4. Döngü (`domain/usecases/answer_question.py`)

Her araç çağrısında sırayla: `run.stopped()` sorulur, adım varsa önceki bitirilip yenisi yazılır,
sonra iş çalışır; `QueenAIFailed` gelirse `run.fail(<kutunun cümlesi>)` ve soru biter. Her kontrol
ücretli bir istektir ve bir tur her kare için bir çağrı taşıyabilir; durdurma o turun kalanını
göndermez. Bugün yalnız tur başında soruluyordu.

### 5. Port (`domain/ports.py`)

`QueenAI` `ask(system, text, images)`'i de söyler. `Box`'ta bu zaten var (`services/deepseek/box.py`);
`main.py` ajana aynı kutuyu veriyor, kablolama değişmez.

## QueenAgent'tan kopyalanan

`queen-agent/backend/features/workspace/domain/prompt.py`, `START_A_SCENARIO`'nun Step 5, 7, 8, 9 ve
10'unun **Context** maddeleri, kelimesi kelimesine, `prompt.py`'nin `MIXUP_RULES`'ına. İçe aktarma
yok, iki aracı bağlayan bir test yok *(kullanıcı, 8 Ekim — "tammaen ayrı bir proje")*; birinde
değişen öbürüne elle taşınır.

- **Alınan:** kameranın gizlediği etiketin başka karaktere geçmesi (Step 5 ve 8); zayıf model her
  etiketi çizer, karmaşık prompt resmi bozar (5, 9); prompt tek fotoğraf anlatır (5'in Rule 4'ü, 7);
  NSFW'de beden adı açık (5'in Rule 6'sı); negatif liste — karakterin özelliği değil karşıt etiketler,
  bir etiket bütün fotoğrafa işler (10).
- **Bırakılan, Queen Editor'de karşılığı olmadığı için:** adımların senaryo dosyası üzerindeki işi
  (review dosyaları, giriş ekleme), Rule 1 – 3 (senaryonun girişleri) ve "The scenario has one
  negative list" (Queen Editor'de negatif her üretimle gider).
- **Bırakılan, nasıl düzeltileceğini söyledikleri için** — bu parça yalnız bulur: Rule 4'ün "remove
  the extra part"'ı, Rule 5'in "make the part simpler, and keep the same moment"'i ve Step 8'in
  "remove the hidden tag"'i. **481'in düzeltmesi bu üçünü geri ekler.**
- Adımların birbirini tekrar eden cümleleri bir kez yazıldı.

Bu parçada kurallar kontrolün talimatında gider: karşılaştırmayı yapan oradadır, ve kurallar ona bir
karışmanın neye benzediğini söyler (gizli bir başın saçı başka bir karakterde). 481'in düzeltmesi aynı
sabiti kullanır.

## Maliyet

Koddan sayıldı, ölçülmedi. 48 karelik bir proje; C kontrol edilen kare (fotoğrafı olan, videosu
olmayan), C ≤ 48.

| | Bir kontrol (48 kare) |
|---|---|
| Ajanın araç çağrısı | 48 `check_frame`, her kareye bir; videolu, fotoğrafsız, prompt'suz ve fotoğrafı başarısız kareler karttan, diske ve ağa gitmeden cevaplanır |
| Ana döngünün turu | talimat hepsini aynı turda ister: 2 (çağrılar, sonra liste); en çok 32 |
| Drive | başta bir galeri okuması (bugünkü `list_frames`), sonra kontrol başına bir resim okuması: C okuma, O(N) |
| DeepSeek isteği | kontrol başına 2 (resimli soru + kutunun yalnız metinli ret kontrolü; hata olursa kutunun 5 denemesine kadar), artı ana döngünün turları: ≈ 2C + R |
| Gönderilen resim | tam C — her fotoğraf bir kez; ana sohbet hiç resim taşımaz |
| Resim token'ı | C × bir fotoğrafın token'ı. **deepseek-flash'ın bir resme kaç token saydığı ölçülmedi**, depoda da yok |
| Ana sohbetin büyümesi | kare başına bir satırlık karar (birkaç on token); turda yeniden gönderilen yalnız metin |
| Süre | kontroller sırayla; her biri bir resimli istek ve bir kontrol. Ölçülmedi |

Karşılaştırma: aynı iş ana sohbette yapılsaydı 168 – 600 resim gönderimi ve son istekte 48 resim
(yukarıda, "Neden ayrı bir istek").

## Ne kaybolabilir, ne bozulabilir

- **Hiçbir şey yazılmaz.** Araç yalnız okur: galerinin kartı ve bir resim. Kayıt, plan, ayarlar,
  dosya — hiçbirine yazılmaz. İzin sorulmaz çünkü değişen bir şey yok.
- **Aynı anda iki istek:** her soru kendi kartlarıyla başlar, ortak bir durum yok.
- **Çökme:** bugünkü gibi, yarıda kalan soru sonuçsuz kalır (runner); diskte yarım bir şey olmaz.
- **Durdurma** artık her araç çağrısından önce bakılır; havadaki bir istek kesilemez (kutu onu
  bekler), sonrakiler gönderilmez.
- **Modelden gelen değer** yalnız bir kare numarasıdır ve `frames`'te aranır; yola ya da dosya adına
  hiç girmez. Resmin adı kartın kendi `layers`'ından gelir, okuma `Storage`'dan geçer.
- **Okunamayan bir resim ve reddedilen bir kontrol** o karenin satırıdır, soru düşmez ve önceki
  kararlar kalır. **Teknik bir hata** soruyu kutunun cümlesiyle bitirir: o ana kadarki kararlar
  sohbete yazılmaz — servis düşükken liste zaten tamamlanamaz, ve sonraki her kontrol boşuna
  ödenirdi.

## Bilinen sınır, bu maddenin dışında

**`look_at_frame`'in N² yeniden gönderimi:** bugün ajanın baktığı her fotoğraf sohbette kalıyor ve
sonraki her turda yeniden gönderiliyor, hangi soru olursa olsun. Bu madde ona dokunmaz — karışma
kontrolü artık oradan geçmez —, ama çok fotoğrafa bakan bir soru hâlâ aynı maliyeti öder.

## Bu maddenin kararları

1. **Kontrol kendi isteğinde** (`check_frame`, kutunun `ask`'i); sohbete yalnız karar döner
   *(ana ajan, 20 Ekim)*.
2. **Videolu kare yalnız kodda reddedilir**; başarısız video video sayılmaz. Fotoğrafı başarısız,
   fotoğrafsız ve prompt'suz kare de karttan, adımsız reddedilir.
3. **Karar tek satır, `OK` / `MIXED:` / `UNSURE:` ile başlar**; 481 de okur.
4. **QueenAgent'ın kuralları `MIXUP_RULES`'ta, kopya**; bu parçada kontrolün talimatında, en başta.
5. **Durdurma her araç çağrısından önce; adım her aracın işinden önce.**
6. **Teknik hata soruyu bitirir, ret o karenin satırıdır** *(reviewer, 20 Ekim)*.

## Sınırlar

- Frontend değişmez, `dist` yeniden kurulmaz: adımlar ve cevap bugünkü gibi görünür.
- Notebook ve `main.py` değişmez.
- Negatif prompt karta girmez ve kontrole gitmez: tespit yalnız fotoğrafı prompt'la karşılaştırır.
  Düzeltme 481'in.
- Gerçek bir modelin kararlarının kalitesi testle ölçülmez; kullanıcının denemesinde görülür.

## Bitti sayılır

1. Testler (`test_agent_answer.py`, sahte kutuyla, ağ yok) gösteriyor ki:
   - araçlar `read_frame`, `look_at_frame`, `check_frame`; üçü de yalnız `frame` alıyor;
   - `check_frame` kutuya talimatı (kurallar, iş, suffix sırasıyla), `Prompt: <prompt>`'u ve tek
     resmi soruyor; modele "Frame N: <karar>" dönüyor; sohbete resim girmiyor; bir adım yazılıyor;
   - karenin adımı Queen AI'a sorulduğu anda sohbette;
   - videosu olan, fotoğrafı başarısız, fotoğrafsız ve prompt'suz karede resim okunmuyor, soru
     sorulmuyor, adım yazılmıyor;
   - videosu başarısız olan kare kontrol ediliyor;
   - fotoğraf katmanı ve prompt'u olup dosyası diskte olmayan karede soru sorulmuyor;
   - okunamayan bir resim (`OSError`) kendi cümlesiyle modele dönüyor ve soru devam ediyor;
   - reddedilen bir kontrol o karenin satırı, soru devam ediyor; teknik bir hata soruyu kutunun
     cümlesiyle bitiriyor, başka kontrol ve tur gönderilmiyor;
   - bir turun iki çağrısı arasında gelen durdurma ikinciyi göndermiyor;
   - `main.py`'nin kurduğu hâliyle (`test_composition_root`, `requests.post` sahte): kontrol aynı
     kutudan resim ve `Prompt: …` ile gidiyor, kararı ret kontrolünden geçiyor, sohbete "Frame 1: OK"
     olarak dönüyor, sohbetteki tek resim `look_at_frame`'inki, projeye bir şey yazılmıyor.
2. İki satır yeşil: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`.
3. Kullanıcı ajandan karışmaları istediğinde ajan kareleri tek tek inceliyor ve sohbete üç gruplu
   listeyi yazıyor; hiçbir şey değişmiyor, izin sorulmuyor — v10'un sonundaki denemede görülür.
