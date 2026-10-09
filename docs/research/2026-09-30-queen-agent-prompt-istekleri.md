# QueenAgent — prompt istekleri, kullanıcının sözleriyle

**Tarih:** 2026-09-30 · **Maddeler:** [v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md)'un 391 – 394'ü

v9'un prompt maddeleri — 367 – 374, 385, 388 ve 390 — 30 Eylül'de geri alındı (`c75dd524`), ve modele
giden metinler v9'dan önceki hâline döndü. Prompt'lar 391 – 394'te kullanıcıyla birlikte
yazılacak. Bu belge o iş için: kullanıcının prompt'lar için söyledikleri, madde madde, kendi sözleriyle.
Nasıl yazılacağı birlikte konuşulacak.

Metinler [prompt.py](../../queen-agent/backend/features/workspace/domain/prompt.py)'de:
`START_A_SCENARIO`, `EDIT_PROMPTS`, `WRITE_FRAME_SYSTEM_PROMPT`, `SDXL_PROMPT_RULES` ve araçların
açıklamaları.

## Neden geri alındı *(30 Eylül)*

- "abi bensiz promptları güncellemişsiz ben onları inceleycektim"
- "abi yeni fieldlar açamı bepenemdim lütfen düzelt doğru yetlere ekle promtplarda ayrı fiedlar açma
  extra yazma şeklidne ai in çok ynalış anlyacağı uçu açık şekilde böyle yazarsan patlarız ekstra
  compelx çizemez dersen geçkten gider olabilcek en basit şeyleri çizer lütfen promptlarını repodaki
  gibi yaz"
- "fotoğraf modeli bunu bilmesine gerek yok, 4 saniyelik video"
- "bence şöyle yapalım abi sen prompt değişilerini geri al direkt ve taskı aç ve ne yapacğaımı ben
  sana madde madde söylemiştim onuda bir bir md ye yaz ben senle berabe ypaıcam bu maddeyi"

## 1. Sorun *(28 Eylül)*

- "queen agent şey ekledik mi promtplar güçlendirlekcek kısmını ve düzenlenecek"
- Hangisi olduğu sorulunca: "QueenAgent'ın prompt yazarken kullandığı talimatlar güçlendirilsin,
  yani modele giden metinler"
- "abi bugun model promptların zayıf modele gittiğini bilmiyor sdxl için ve modlei nyapamayığı kadar
  komplex şeyleri yazıyor ve sıkıntı yaşıyoruz"
- "ama ben yapay zekaya belirtlp kontrol ettiğimde düzeltiyor"
- "ben sana yapay zeka 6 yda 4 soru soruyoum dedim her biri 1 madde olsun savsaklama"
- "bu dğeişikler bütün skilleri kapsasın"

## 2. Kullanıcının elle sorduğu dört soru *(28 Eylül)*

1. **Zayıf model** — "fotoğra üretene yapay zeka modeli çok zayıf sence yazdığın promptu bu
   yapayzeka üretevbilir"
2. **Görünen parçalar** — "bu pov olayını var on ukaldırıyorum ve diyorumki ypatığın açıda o hangi
   karakterin hangi parçaları görünüuorsa onları yaz prompta yoksa model zayıf olduğu için o
   özellikleri öteki karakterler eklyior"
3. **Negatif** — "senaryoya ve karakterlere özel negatic promtplar yazıdıyıroum karakterlerin
   özeliklkerinin karışmaması için"
4. **Tek an** — "model çok zayıg ve tek bir anın fotoğrafının yapıyorum promptun veya senaryonun 1den
   fazla sahneyi analyıyorsa lütfen güncelle diyorum basit ve tek bir anı gösteicek şekilde yada bir
   kaç sahneye böl"

## 3. Zayıf model ve 4 saniye

- *28 Eylül:* "burdada biliyor abi zayıf bir model yazdığını"
- *28 Eylül:* "h3 e de şey bilgisini vermemiz lazım her video 4sn oluyor"
- *30 Eylül:* "fotoğraf modeli bunu bilmesine gerek yok, 4 saniyelik video"
- *30 Eylül, 391 yazılırken:* "abi senaryoa vs sahne video da oluşturdağı için bir frame olmaz
  fotoğraf promptu bir frame olmalı? ve o sahnenin ilk karesi olmalı"
- *30 Eylül, 391 yazılırken:* "bu işte 4 video onun ilk frame olayı bence yukarda anlatılacak sonrak i
  tasklarda orayı karıştırmaylaım ama unutmama için bir md ye yaz bunu" — Start a scenario'nun
  açılışına, sonraki bir maddede. 391'in kontrolleri bunu kendi içinde anlatmaz.

## 4. Negatif

- *28 Eylül:* "senaryo başına", "en son negatifide yazsın"
- *28 Eylül:* "abi negatif ayrı dursun queen agentta user manuel kopyala yapıştır yapsın"
- *28 Eylül, kullanıcının bu konuşma için verdiği not, roadmap'teki hâliyle:* negatif kişiye özel
  çalışmaz, asıl çözüm pozitif tarafta; koyu ten negatife yazılmaz — yazılınca adam beyaz çıktı,
  yerine adama özel karşıt etiketler girer (`pale male`, `white man`); karakterin kendi özellikleri
  negatife girmez.

## 5. Akış, Improve ve onay

- *28 Eylül:* "abi bence şuank akış aynı sırada kalsın Sonra h3 gelsin sonra kontrol adımalrı
  başlasın" — H3 kısmı 29 Eylül'de düştü, aşağıda 8.
- *28 Eylül:* "plan bitince tek bir yer olsun improveu direkt çağırsın", "olur böyle yapalım"
- *28 Eylül:* Improve ayrı bir skill, kullanıcı istediğinde seçer *(kullanıcı kararı)*.
- *28 Eylül:* "sorun değil onay olsun görmek istiyorum ypaılan şeyi", "her kontrol eadımın sonunda abi"
- *28 Eylül:* "edit prompt bitince de improvu çağır desin"
- *28 Eylül:* Edit prompts'tan sonraki kontroller yalnız değiştirdiği karelere bakar, ve kadro
  değiştiyse negatif liste de yeniden yazılır *(kullanıcı kararı)*.
- *28 Eylül:* Uzun bir senaryoda kontroller birkaç tura yayılır; kalınan yeri plan dosyası tutar,
  kullanıcı "devam" der *(kullanıcı kararı)*.
- *28 Eylül:* Skill metinlerinin kelime tavanı yazılı bir kararla yükselir *(kullanıcı kararı)*.
- *29 Eylül:* Improve'un seçicideki açıklaması tasarımcının önerisi, kullanıcı kabul etti: *Run four
  checks on a scenario's frames and prompts, and say yes after each one.*

## 6. Elbise çıkarma sahnesi

- *28 Eylül:* "queen agent promtplarımn bir madde daha elbise çıkarma sahnesei senaryoya aksi
  söylenmediği sürece eklenmez"
- *29 Eylül:* "abi bazen queen agent elbisesin değiştiği sahnelerde elbisesni çıktıüı framler yazmaya
  çalışıyor", "çıkaraıldığı ara sahneleri çizemiyor mesla bi sahnede var sonkirnde farklı bir elbise
  var yapar ama değiştiröe karaleri yaoamıtor"
- *29 Eylül:* "senrayoda olsa yeter sahnleri yzan madede satart senearyoda senaryoların yazıldığı madde"

## 7. Konuşma

- *29 Eylül:* "ekstra queen agetn konuşam vs varsa sceneroyunun içinde yazması lazım ki queen
  editordeki deepsek görük eklesin anlaştırkm ı"
- *29 Eylül*, başka bir ekstra sorulunca: "başka yok gibi"
- *30 Eylül*, Edit prompts'a da eklensin mi sorulunca: "olur eklensin"

## 8. H3 prompt'unu queen-editor yazar *(29 Eylül)*

- "abi aklıma şey geldi h3 promptlarını direkt agentta oluşturmak yerine direkt queen editor ai ksımına
  deepsek alalım hem senaryoyu hem fotoğrafı görürü ve düzgün bir prompt yazar ne diyorsun?", "daha
  kaliteli sonuç verir", "ve videoları beğenemzsek bir agenta yazarız ve çözülür"

Bu kararla listenin biçimi değişti (366): her kare `scene` ve `photo` kaydı. **366 geri alınmadı**,
çünkü queen-editor'ün v8-3'ü bu biçimi okuyor. Modele giden tek cümlesi `BUILD_PROMPTS`'un ilk satırı,
birlikte okunacak:

- v9'dan önce: `Build the prompt list from a structure file.`
- Bugün: `Build the prompt list from a structure file: for each frame, its scene sentence and its prompt.`

## 9. Koşuda çıkan iki istek *(30 Eylül)*

- **Olmayan negatif dosya:** Edit prompts'un kapanışı negatif dosyayı adıyla anıyordu, ve eski
  senaryolarda o dosya yok. Kullanıcı: "bunlarıda düzelt", "bunu yap ben en son okurum".
- **Biçim:** "promtplar önceki promtplarla aynı formatta yazılmış mı bu kontrol et yazılmadıysa
  düzeltbir task sonra ben okuycam onları"
