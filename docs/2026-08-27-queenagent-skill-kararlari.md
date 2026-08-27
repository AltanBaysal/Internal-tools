# QueenAgent — skill işinin kararları

**Tarih:** 27 Ağustos 2026 · **Durum:** açık kayıt, konuştukça büyüyor.

Bu belge **karar defteri**. Gerekçeler burada değil — her kararın altında nerede tartışıldığı yazıyor.
Amaç tek: konuşma uzadıkça verilmiş bir kararın kaybolmaması.

Kararlar numaralı ve **numaralar kaymaz**; sonradan gelen sondan numara alır. Bir karar değişirse
satırı üstü çizilir ve yerine yenisi yazılır — silinmez, çünkü ona atıf yapan yerler olur.

**Kardeş belgeler:**
[problemler ve gerekçeleri](2026-08-27-queenagent-skill-problemleri.md) ·
[akış nasıl yaşanır](2026-08-27-queenagent-akis-nasil-yasanir.md)

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
| K19 | **Akış tek karakterlik deneme kurabilir** — kullanıcı görmek isterse. Küçük bir yapı dosyası artı `build_prompts`; **yeni araç gerekmiyor**. | Yeni yapı |
| K20 | **JSON asıl kaynak.** Akış hem haritaları hem `frames`'i yapı dosyasına yazar; md kullanıcının kendi dilinde okuduğu açıklamadır. | Yeni yapı |
| K21 | **Akış bir plan yazar ve kendisi takip eder.** Kullanıcının onaylaması gereken bir kapı değil; dosyada durmasının sebebi kullanıcının görebilmesi. | [Akış belgesi](2026-08-27-queenagent-akis-nasil-yasanir.md) |

## D · Kararların açığa çıkardığı iş

Bunlar karar değil, kararların **şartı** — koda bakarak bulundu.

| # | İş | Nereden çıktı |
|---|---|---|
| K22 | **`write_plan` `edit` kipine eklenecek.** Akış `edit` kipinde çalışıyor ve o kipte `write_plan` elinde yok. Turu bitirme kuralı sorun çıkarmıyor: `ends_the_turn` yalnız `plan` kipinde tetikleniyor. | K21 |
| K23 | **`GENERATE_PROMPTS_PLUS` metni güncellenecek:** sayı karakter tanımından çıkıyor *(K6)*, ilk ismin ana karakter olduğu yazılıyor *(K1)*, şema örneği buna göre düzeliyor, ve kural kitabı altıncı maddesini alıyor *(K27)*. | K1, K6, K27 |
| K24 | **Skill seçicide ikinci satır doğacak.** Bugün tek satır var; akış skill'i ikinciyi getiriyor. Madde 94 seçiciyi tam da bunun için bırakmıştı. | K16 |

---

## Yol haritasıyla çelişenler

Bu kararların ikisi v5 yol haritasının yazılı hâlini yanlışlıyor. **Numaralar kaymıyor**; maddelerin
üstüne düzeltme notu düşüyor — 74'ün 94'e devredilmesinde olduğu gibi.

**Madde 70'in yazılı hâli:** *"Kaç kişi olduğunu artık kod söyler: kareye giren karakterler sayılır."*
**Yanlış** — K8. Kod sayamaz, çünkü bir karakterin ne olduğu hiçbir alanda durmuyor. Sayıyı model
yazar, kod yerleştirir *(K7)*. Ayrıca maddenin kendisi de eksik anlatılmıştı: derdi yalnız sayı
değil, **sıra** *(K3)*.

**Madde 75'in yazılı hâli:** *"Prompt dili değişir: çıkan şey etiket dizisi değil, düz cümledir."*
**Yanlış** — K9. Etiket kalıyor.

---

## Hâlâ açık

| Soru | Durum |
|---|---|
| Şema `people` dışında başka ne alıyor | Açık |
| ~~Diskteki yapı dosyaları ne olacak~~ | **Kapandı — K26:** oldukları gibi kalıyorlar |
| ~~Karakter tanımının içinde kalan sayı ve `solo` etiketi ne olacak~~ | **Kapandı — K27:** kural kitabının altıncı maddesi |
| Akış skill'inin metni ne diyecek, ve nereye kadar soruyor | Açık |
| Madde 94'ün sildiği dört bilgiden hangisi geri geliyor, hangi metnin içine | Açık — Problem 4 |
| Bu iş kaç maddeye bölünüp hangi sırayla koşulacak | Açık |

## Kapsam dışı

- **Madde 71 — bağlam yönetimi.** Taşıma ve tur döngüsü; skill metnine dokunmuyor.
- **Backlog'daki *"Prompt listesi karışıyor"*.** Bu işe hiç girmedi.
