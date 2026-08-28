# QueenAgent — skill işinin kararları

**Tarih:** 27 Ağustos 2026 · **Durum:** açık kayıt, konuştukça büyüyor.

Bu belge **karar defteri**. Gerekçeler burada değil — her kararın altında nerede tartışıldığı yazıyor.
Amaç tek: konuşma uzadıkça verilmiş bir kararın kaybolmaması.

Kararlar numaralı ve **numaralar kaymaz**; sonradan gelen sondan numara alır. Bir karar değişirse
satırı üstü çizilir ve yerine yenisi yazılır — silinmez, çünkü ona atıf yapan yerler olur.

**Kardeş belgeler:**
[problemler ve gerekçeleri](2026-08-27-queenagent-skill-problemleri.md) ·
[akış tasarımı](2026-08-27-queenagent-akis-tasarimi.md)

---

## A · Prompt nasıl diziliyor

| # | Karar | Nerede tartışıldı |
|---|---|---|
| K1 | **Ana karakter, karenin `characters` listesinde en öne yazılan isimdir.** Şemaya ayrı bir alan girmiyor — sıra zaten bilgi taşıyor. | Problem 1 |
| K2 | **Ana karakter her karede ayrı belirlenir.** Aynı iki kişi bir karede önde, ötekinde arkada olabilir. | Problem 1 |
| K3 | **Ana karakter promptun başında, geri kalan herkes `camera`'dan sonra** durur. Araya mekân, action ve camera giriyor. | Problem 1 |
| K4 | **Kıyafet her zaman sahibiyle tek blok.** Sahibi önde de olsa arkada da olsa ikisi komşu kalır. | Problem 1 |
| K5 | **Üç kişide ikinci ve üçüncü sonda yan yana kalır.** Aralarındaki karışma riski **bilerek kabul edildi**; korunması gereken ana karakter. | Problem 1 |
| K6 | **Kişi sayısı karakter tanımından çıkar, karenin kendi `people` alanına girer.** | Problem 2 |
| K7 | **`people`'ı model yazar, kod yerleştirir** — `quality`'den hemen sonra, promptun en başına. | Problem 2 |
| K8 | **Sayma koda alınmıyor.** Kod kareye kimin girdiğini biliyor ama ne olduklarını bilmiyor; şemada cinsiyet alanı yok ve açılmıyor. | Problem 2 |
| K9 | **Prompt dili etiket kalıyor.** Kullanılan modeller SDXL temelli. | Problem 3 |
| K10 | **`build_prompts` yaşıyor ve biçim değiştirmiyor.** Karakteri kod birleştirir, model kopyalamaz. | Problem 3 |
| K11 | **Kalite etiketleri koda gömülmez** — yapı dosyasının `quality` alanında, senaryo başına ayarlanır. Kullanıcı tek modele bağlı değil. | Problem 3 |
| K25 | **`people` her karede zorunlu**, tek karakterli karede bile. Sayı karakter tanımından çıkınca `people` onun tek evi oluyor; olmadığı karede sayı etiketi büsbütün kayboluyor. `action` ve `camera` ile aynı sınıfta. | 27 Ağustos, K6'nın sonucu |
| K26 | **Diskte duran yapı dosyaları olduğu gibi kalıyor.** Ne toplu dönüştürme ne açılışta düzeltme; `people` taşımayan kare bugünkü gibi çıkar — kod eksik alanı atlar, `quality` yokken yaptığı gibi. Bir dosyayı elden geçirmek kullanıcının kendi kararı. | Kullanıcı kararı, 27 Ağustos |

**K26'nın gerekçesi:** dosyalar kullanıcının emeği ve FOUNDATION 1 onları dokunulmaz sayıyor. Üstelik
bozulan bir şey yok — eski dosyalar bugün çalışıyor, yarın da çalışacak. Bedeli biliniyor: bir süre
iki biçim yan yana yaşayacak, ve `build_prompts` ikisini de okumak zorunda. Bu yeni bir yük değil,
`shots`/`frames` ve düz karakter listesi zaten aynı şeyi yapıyor.

| # | Karar | Nerede tartışıldı |
|---|---|---|
| K27 | **Karakter tanımında kalan sayı ve `solo` etiketi kural kitabına girer, koda değil.** Kural kitabı altıncı maddesini alıyor: kişi sayısı ya da `solo` bir karakterin kendi tanımındaysa yanlış yerde — yeri `people`. | Kullanıcı kararı, 27 Ağustos |

**K27'nin gerekçesi kullanıcının kendi cümlesi:** *"kural kitabı yeterli, biraz kullanıcıya özgürlük
vermek lazım."* Kod ayıklasaydı bilerek yazılmış bir etiketi de silerdi ve sildiğini söylemezdi —
üstelik hangi etiketin sayı olduğunu ancak bir adlar listesiyle tahmin edebilirdi, ve o liste hiçbir
zaman tamamlanmıyor. Kural kitabı tutmayabilir; bedeli biliniyor ve kabul edildi. Ayrımı şu:
Madde 91 bir **yetki** kuralını koda aldı, bu ise bir **içerik** kuralı — kodun elinde etiketin
anlamı yok.

## B · BREAK

| # | Karar | Nerede tartışıldı |
|---|---|---|
| K12 | **`BREAK` bu koşuda kullanılmıyor.** Problem 1'in ilacı sıra düzeltmesi *(K3)*. | Problem belgesi, araştırma bölümü |
| K13 | **Sebebi elde ölçüm olması:** kullanıcı sıra düzeltmesini elle deneyip işe yaradığını gördü. `BREAK` için önce queen-editor'ün düğümü açması gerekiyor. | Kullanıcı, 27 Ağustos |
| K14 | **`BREAK` güncellemesi haftaya**, ve iş iki backlog'a birden geçti. queen-editor'de açılacak düğüm `36`. | [queen-editor](../queen-editor/BACKLOG.md) · [queen-agent](../queen-agent/BACKLOG.md) |
| K15 | **Kayda geçen şüphe:** erken jetonlar daha ağır bastığı için sıra düzeltmesi ikinci karakteri ayırmakla kalmayıp zayıflatabilir. `BREAK` geldiğinde iki ilaca birden gerek olup olmadığı yeniden sorulacak. | Problem belgesi |

## C · Skill yapısı

| # | Karar | Nerede tartışıldı |
|---|---|---|
| K16 | **İki skill olacak.** `generate-prompts-plus` bugünkü işini sürdürüyor; yanına **onu besleyen bir akış skill'i** geliyor. | Yeni yapı |
| K17 | **Akış tek metin, ve kullanıcı arada skill değiştirmiyor.** Bu, silinen üç skill'i geri getirmek değil — Madde 74'ün asıl istediği buydu. | Yeni yapı |
| K18 | **Akış sorarak ilerler:** karakterler, mekânlar, ve her ikisi için *"promptun var mı"*. Varsa alır, yoksa kullanıcı anlatır ve akış kurar. | Yeni yapı |
| K19 | ~~**Akış tek karakterlik deneme kurabilir** — küçük bir yapı dosyası artı `build_prompts`; yeni araç gerekmiyor.~~ **Değişti — K36:** deneme kendi aracını alıyor. | Yeni yapı |
| K20 | **JSON asıl kaynak.** Akış hem haritaları hem `frames`'i yapı dosyasına yazar; md kullanıcının kendi dilinde okuduğu açıklamadır. | Yeni yapı |
| K21 | **Akış bir plan yazar ve kendisi takip eder.** Kullanıcının onaylaması gereken bir kapı değil; dosyada durmasının sebebi kullanıcının görebilmesi. | [Akış tasarımı](2026-08-27-queenagent-akis-tasarimi.md) |

## D · Kararların açığa çıkardığı iş

Bunlar karar değil, kararların **şartı** — koda bakarak bulundu.

| # | İş | Nereden çıktı |
|---|---|---|
| K22 | **`write_plan` `edit` kipine eklenecek.** Akış `edit` kipinde çalışıyor ve o kipte `write_plan` elinde yok. Turu bitirme kuralı sorun çıkarmıyor: `ends_the_turn` yalnız `plan` kipinde tetikleniyor. | K21 |
| K23 | **`GENERATE_PROMPTS_PLUS` metni güncellenecek:** sayı karakter tanımından çıkıyor *(K6)*, ilk ismin ana karakter olduğu yazılıyor *(K1)*, şema örneği buna göre düzeliyor, ve kural kitabı altıncı maddesini alıyor *(K27)*. **K28'den sonra bu işin çoğu metnin değil şemanın:** şema ve kural kitabı araca taşındığı için prompt+ metni ikisini de taşımıyor. | K1, K6, K27, K28 |
| K24 | **Skill seçicide ikinci satır doğacak.** Bugün tek satır var; akış skill'i ikinciyi getiriyor. Madde 94 seçiciyi tam da bunun için bırakmıştı. | K16 |

## E · Akışın kendisi

Hepsi 27 Ağustos, ve tasarımın anlatıldığı yer
[akış tasarımı](2026-08-27-queenagent-akis-tasarimi.md).

| # | Karar | Nerede tartışıldı |
|---|---|---|
| K28 | **Şema ve kural kitabı skill metinlerinde durmaz.** `read_schema` aracı ikisini birden döndürür; iki skill de yazmadan önce onu çağırır. Sebebi: yönerge her turda yeniden gönderiliyor *(Madde 93)*, oysa şema yalnız yazma anında lazım. | Kullanıcı kararı |
| K29 | **Akış dallanmaz.** Her adımın tek çıktısı var, ve o çıktı kullanıcının ne kadar anlattığına göre değişmez — değişen yalnız adımın kaç tur sürdüğü. | Kullanıcı kararı |
| K30 | **Her adım kendi içinde döngü.** Kullanıcı onaylayana kadar bir sonrakine geçilmez. | Kullanıcı kararı |
| K31 | **Madde 94'te silinen dört bilginin hiçbiri geri gelmiyor.** Gerekçe kullanıcının kendi ölçümü: *"çok kötü çalışıyorlardı."* Problem 4 böylece kapandı. | Kullanıcı kararı |
| K32 | **Promptları akış kendisi kurar.** Kullanıcı sonda prompt+'a geçmiyor. prompt+ yerinde: elinde yapı dosyası olanın **var olanı güncelleyen** yolu. *(28 Ağustos'ta K40 ile devrildi.)* | Kullanıcı kararı |
| K33 | **Sahneler iki yere birden yazılır** — `frames`'e etiket olarak, md'ye cümle olarak. Kayma bedeli biliniyor ve kullanıcıya bırakıldı. | Kullanıcı kararı |
| K34 | **Anlatılmayan karakter ve mekân için yer tutucu yazılır** — `1girl, long hair, plain clothes`, `plain background`. Akış tarif bekleyerek durmaz. | Kullanıcı kararı |
| K35 | **Skill'in adı `Start a scenario`.** Çıkan şey tek sahne değil, senaryo: karakterler, mekânlar, N sahne, prompt listesi. | Kullanıcı kararı |
| K36 | **`build_character_prompts` aracı gelir.** Karakter × kıyafetler, düz bir `PROMPTS` listesi, `build_prompts` ile aynı kurucu. İçinde model yok. K19'un yerine geçiyor. | Kullanıcı kararı |

## F · Yetki ve seçim

| # | Karar | Nerede tartışıldı |
|---|---|---|
| K37 | **Yazma araçları her kipte modele verilir; kip artık *sormadan çalışabilenlerin* listesi.** Kipin izin vermediği bir çağrı **tur ortasında** kullanıcıya sorulur, ve akış cevabı bekler. | Kullanıcı kararı, 27 Ağustos |
| K38 | **Onay kipi değiştirir, red turu bitirmez.** Red modele bir açıklamayla döner — kip değişmedi, bu araç bu kipte yok, yazmadan devam et — ve **kullanıcı kendi sebebini de yazabilir**. | Kullanıcı kararı, 27 Ağustos |
| K39 | **Skill seçimi tarayıcıda hatırlanır.** Madde 86 bunu bilerek dışarıda bırakmıştı; beş adımlık bir akış gerekçeyi değiştiriyor — yenilemeden sonra yönergesiz giden bir tur akışı sessizce bozuyor. | Kullanıcı kararı, 27 Ağustos |

**K37'nin Madde 91 ile ilişkisi:** yetki hâlâ kodda. Model izin almadan yazamıyor; değişen tek şey
kapının araç listesinden değil çalıştırma anından geçmesi. Yönergeye *"yazma"* diye bir cümle
girmiyor.

## G · Bölünme düzeltmesi (28 Ağustos)

| # | Karar | Nerede tartışıldı |
|---|---|---|
| K40 | **K32 devrildi: akış temeli bırakır, işçiliği prompt+ yazar.** Akış yapı dosyasını karakter ve mekânlarla, sahneleri de yapı dosyasının adını taşıyan tek cümlelik bir listeyle bırakır *(`bar-scene.json` ↔ `bar-scene-scenes.md`)*; `frames` bilerek boş kalır ve `build_prompts`'ı akış çağırmaz. prompt+ çifti adıyla bulur, cümleleri sırayla detaylı frame'lere çevirir ve kurar — cümleden az frame, kalan iştir, kaldığı yerden sürer. Sebep: aksiyon/kamera yazmak detay işçiliği, akışın soru temposuna ağır. **K33'ün yönü de döndü:** md artık kopya değil kaynak, `frames` ondan türüyor; kayma bedeli build'den sonrasına kaldı. | Kullanıcı kararı, 28 Ağustos |

---

## Yol haritasıyla çelişenler

Bu kararlar koşulmuş maddelerin yazılı hâlini yanlışlıyor ya da genişletiyor. **Numaralar kaymıyor**;
maddelerin üstüne düzeltme notu düşüyor — 74'ün 94'e devredilmesinde olduğu gibi.

**Madde 70'in yazılı hâli:** *"Kaç kişi olduğunu artık kod söyler: kareye giren karakterler sayılır."*
**Yanlış** — K8. Kod sayamaz, çünkü bir karakterin ne olduğu hiçbir alanda durmuyor. Sayıyı model
yazar, kod yerleştirir *(K7)*. Ayrıca maddenin kendisi de eksik anlatılmıştı: derdi yalnız sayı
değil, **sıra** *(K3)*.

**Madde 75'in yazılı hâli:** *"Prompt dili değişir: çıkan şey etiket dizisi değil, düz cümledir."*
**Yanlış** — K9. Etiket kalıyor.

**Madde 86'nın yazılı hâli:** *"Tarayıcı hafızasına da yazılmaz: sildiğimiz karmaşıklığı başka bir
yere taşımak olurdu."* **Değişti** — K39. Gerekçe yanlış değildi, ama beş adımlık bir akış onu
geçersiz kılıyor: yenilemeden sonra yönergesiz giden bir tur akışı sessizce bozuyor. 86'nın asıl
korktuğu şey — ekranın bir şey deyip isteğin başka bir şey taşıması — geri gelmiyor, çünkü
hatırlanan değer ikisinin de okuduğu tek değer.

**Madde 91'in kip tanımı genişliyor** — K37. Kip artık modele *hangi araçların verildiğini* değil,
*hangilerinin sormadan çalışabildiğini* söylüyor. 91'in kuralı yerinde: yetki koda bağlı, yönergeye
değil.

---

## Hâlâ açık

| Soru | Durum |
|---|---|
| Şema `people` dışında başka ne alıyor | Açık — 95'in spec'inde kapanır |
| ~~Diskteki yapı dosyaları ne olacak~~ | **Kapandı — K26:** oldukları gibi kalıyorlar |
| ~~Karakter tanımının içinde kalan sayı ve `solo` etiketi ne olacak~~ | **Kapandı — K27:** kural kitabının altıncı maddesi |
| ~~Akış skill'inin metni ne diyecek, ve nereye kadar soruyor~~ | **Kapandı — K28-K35:** beş adım, her biri onaya kadar döngü, şema metinde değil araçta |
| ~~Madde 94'ün sildiği dört bilgiden hangisi geri geliyor, hangi metnin içine~~ | **Kapandı — K31:** hiçbiri |
| ~~Bu iş kaç maddeye bölünüp hangi sırayla koşulacak~~ | **Kapandı:** yol haritası, maddeler 95'ten başlıyor |

## Kapsam dışı

- **Madde 71 — bağlam yönetimi.** Taşıma ve tur döngüsü; skill metnine dokunmuyor.
- **Backlog'daki *"Prompt listesi karışıyor"*.** Bu işe hiç girmedi.
