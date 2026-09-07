# Backlog — QueenAgent

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

## Promptlar baştan sona okunacak ve geliştirilecek

*(Kullanıcı, 6 Eylül.)*

Modele giden her metin, tek oturumda ve arka arkaya: `prompt.py`'nin `SYSTEM_PROMPT`'u ve
`LAST_ROUND`'u, `skills.py`'nin iki metni, `tools.py`'deki 20 araç açıklaması ile parametre metinleri,
`SDXL_PROMPT_RULES`, `WRITE_FRAME_SYSTEM_PROMPT`, ve araçların cevap cümleleri.

Bugüne kadar hepsi **madde madde** yazıldı — her biri kendi turunda doğruydu, ama hiçbir tur ötekinin
yanında nasıl okunduğuna bakmadı. Aranacak olan da bu: çelişen iki cümle, iki yerde anlatılan aynı
kural, ve bir metnin ötekinin işini yapması.

## Skill'ler yeniden düzenlenecek

*(Kullanıcı kararı, 6 Eylül.)*

**Generate prompts+ kalkacak.** Yaptığı iş — her karenin action'ını yazmak, sonra derlemek — **Start
a scenario**'nun içine giriyor, ve o akışın yapısı da baştan elden geçiyor. Yerine **prompt
düzenleme** için ayrı bir şey geliyor: var olan promptları düzeltmek kendi başına bir iş.

**Çözülmesi gereken tek şey:** Deneme 3'te 23 karenin action'ı **tek tura sığmadı**, araya bir saat
girerek ikiye bölündü. Akışın kuralı *"bir adım kullanıcı onaylayınca biter"* — sığmayan bir aşama
o kuralın içinde yaşayamaz. Birleştirme bunun cevabıyla birlikte tasarlanır.

## Promptlar daha etiket hâline getirilecek

*(Kullanıcı, 6 Eylül.)* Kural `SDXL_PROMPT_RULES`'ta zaten yazılı — *cümle değil, kısa virgüllü
parçalar; artikel etiket değil* — ama çıkan metin hâlâ cümleye kayıyor. İki üretici var ve ikisi de
bakılacak: haritaların etiketlerini yazan ana ajan, ve eylem satırını yazan Grok.

Kuralı sıkılaştırmak mı, örnek çoğaltmak mı, yoksa yazılanı geri okuyup ölçmek mi — **kararlaşmadı.**

## Koşan tur mesajın altında canlı görünecek

*(Kullanıcı, 6 Eylül.)* Tur beklerken mesajın altında tek bir şerit, üç parça yan yana: **ne
yapıldığı**, **kaçıncı raund** *(`MAX_ROUNDS` 16)*, ve **şu ana kadar harcanan jeton** — hepsi anlık
artarak. Tasarım bugünkü damganın aynısı; damga turun **sonunda** düşüyor, yani uzun bir tur boyunca
ekranda ilerlemeyi gösteren hiçbir şey yok.

**Kelime Claude Code'daki gibi olacak** *(kullanıcı kararı, 6 Eylül)*: dönen, ilginç, ve ne
yapıldığını söylemeye çalışmayan. Araç adından türetilen bir metin **istenmedi** — beklerken okunacak
bir şey olması yeter, ve şeridin bilgi taşıyan iki parçası zaten yanında duruyor.

`stream_answer` raundları zaten tek tek koşuyor ve her birinin harcamasını topluyor; eksik olan
bunun akış sırasında ön yüze **ulaşması.**

**Kararlaşmadı:** hangi sayı gösterilecek *(toplam mı, sadece `sent` mi)*, ve tur bitince şeridin
damgaya dönüşüp dönüşmediği.

## Hazır prompt parçaları

*(Kullanıcı, 6 Eylül.)* Bilinen şeylerin — pozisyonlar gibi — **yazılı hâli bir yerde dursun**, ve
kullanıcı isteyince model onu doğrudan göstersin. Her seferinde yeniden yazdırmak yerine hazır olanı
getirmek.

**Rastgelelik değil.** İçlerinden biri seçilmiyor, istenen gösteriliyor — `SDXL_PROMPT_RULES`'un
*"model yazı tura atamaz"* kuralı yerinde duruyor.

**Kararlaşmadı:** nerede duracağı *(depoda mı, projede mi)*, modelin nasıl ulaşacağı *(araç mı,
metnin içinde mi)*, ve gösterdiğini kareye koyup koymadığı.

## Prompt yazan model Grok 4.3'e çevrilecek

*(Kullanıcı kararı, 6 Eylül.)* `config.PROMPT_MODEL` bugün `grok-build-0.1`. Yeni kimlik hem
`PROMPT_MODEL`'e hem `MODELS` sözlüğüne yazılır — o satırdaki string **doğrudan xAI'a gidiyor**
(`client.py`'nin `payload["model"]`'i), yani takma ad değil.

**Yazılmadan önce doğrulanacak:** kimliğin tam yazılışı. Yanlış bir string çalışma anında xAI'ın
kendi hatasına dönüşür, ve bu depoda o adı doğrulayan bir şey yok.

**Bugünkü Grok'un kalması gereken tek yer yok:** bestecide görünmüyor, yalnız `write_frame_prompt`
kullanıyor. Değişiklik tek satır artı bir sözlük satırı.

## Yeni proje adı numaralanacak

*(Kullanıcı, 6 Eylül.)* Her yeni proje **"New project"** adıyla doğuyor
*(`create_project.py`'nin `NEW_PROJECT_NAME`'i)*, ve aynı adı taşıyan üç proje kenar çubuğunda
birbirinden ayırt edilemiyor. Sıradaki boş numarayı alacak: *New project 2*, *New project 3*.

Dosya adlarında bunun karşılığı zaten var — `safe_name` alınmış bir ada numara ekliyor. Aynı kural
projelere de gelecek.

## Prompt sırası değişecek: karakterler önde, mekân sonda

*(Kullanıcı kararı, 6 Eylül.)*

**Bugün** *(`build_prompts.py`)*: kalite, lider karakter ve kıyafeti, **mekân**, action, kamera —
sonra `BREAK` ve her ek karakter kendi bloğunda. Yani mekân ve action **iki karakterin arasına**
konuluyor, bilerek: tarifleri birbirinden uzaklaştırmak için.

**Olacak:**

```
kalite, karakter 1 + kıyafetleri BREAK karakter 2 + kıyafetleri BREAK ... , action, kamera, mekân
```

Karakterlerin hepsi başta ve her biri kendi `BREAK` bloğunda; sonra action ve kamera; en sonda mekân.

**Neden:** araya sokarak ayırmaya gerek yok — ayırma işini `BREAK` zaten yapıyor
*(Madde 138/139: encoder o literal string'den bölüyor)*. Mesafe onun yanında ikinci ve zayıf bir
önlemdi, ve karşılığında action'ı ikinci karakter tanıtılmadan önce okutuyordu.

**Kararlaşmadı:** action/kamera/mekân kendi `BREAK` bloğunu mu alıyor, yoksa son karakterin bloğuna
mı biniyor.

**Not:** Madde 166'dan beri karenin `camera` alanı yok — bugün de okunuyor ama yeni dosyalarda boş,
ve çekim eylem satırının içinde. Sırada yerini koruması eski dosyalar için.

## Üretilen prompta kopyala düğmesi

*(Kullanıcı, 6 Eylül.)* `build_prompts` promptları bir dosyaya yazıyor ve sohbete basmıyor
*(Madde 130, ve bu kural yerinde kalıyor)*. Dosyayı görüntüleyen yerde **kopyala** düğmesi olacak —
bugün prompt'u almanın tek yolu elle seçmek.

**Kararlaşmadı:** dosyanın tamamı tek düğmeyle mi, yoksa her prompt kendi düğmesiyle mi.

## Dosyalara refresh eklenecek

*(Kullanıcı, 6 Eylül.)* Dosya listesi kendi kendine tazelenmiyor. Düğme mi yoksa kendiliğinden mi
olacağı **kararlaşmadı.**

## Action'ı olmayan bütün kareleri dolduran ayrı bir araç

*(Kullanıcı kararı, 6 Eylül: ayrı araç. 5 Eylül'ün "gerçekten sorun olursa" koşulu doldu.)*

v7 `write_frame_prompt`'u **tek kare** üzerine kurdu. Deneme 4'te bedeli görüldü: 21 kare, 21 ana
ajan raundu, **277.6k jeton**. Asıl fatura Grok çağrıları değil — her raunt sistem promptunu, skill
metnini ve **bağlam kabını** baştan gönderiyor, ve kaptaki yapı dosyası her yazımda büyüyor. 21.
raunt 1. raunttan daha ağır.

**Ne olacak:** `action`'ı olmayan bütün kareleri dolduran ayrı bir araç — ana ajan tarafında **tek
raunt**, istekler paralel. Tek kareli olan yerinde kalır; o düzeltmenin aracı.

**Kapsam dışı, ve kararı ayrı:** **dolu** kareleri toplu yeniden yazmak. Deneme 4'ün pahalı işi
aslında buydu *(20 karenin eylem satırı elle düzeltildi)*, ve "boş olanları doldur" onu karşılamıyor.
Madde 181 o düzeltmenin sebebini ortadan kaldırdı; yine de gerekirse ayrı iş.

