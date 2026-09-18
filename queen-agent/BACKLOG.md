# Backlog — QueenAgent

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

## Proje oluşturma ve yönetimi geliştirilecek

*(Kullanıcı, 18 Eylül.)* İki yarısı var:

- **Oluşturma.** Bu yarı aşağıdaki *"Yeni proje ve yeni sohbet açmak karmaşık"* maddesiyle aynı
  yere dokunuyor. Sırası gelince ikisi tek maddede koşulur.
- **Yönetim.** Bugün bir proje için iki eylem var: yeniden adlandırmak ve silmek. İkisi de hem kenar
  çubuğunun menüsünde hem proje ekranında duruyor
  *([Sidebar.jsx](frontend/src/features/workspace/Sidebar.jsx),
  [ProjectScreen.jsx](frontend/src/features/workspace/ProjectScreen.jsx))*.

**Kararlaşmadı: neyin geliştirileceği.** Kullanıcı hangi eylemlerin eksik ya da zayıf olduğunu
söylemedi. Sıralama, arşivleme, arama, kopyalama gibi ihtimallerin hiçbiri kararlaşmadı. **Başlamadan
önce kullanıcıyla konuşulur**, ve varılan karar buraya yazılır.

## Compilation skill'i eklenecek

*(Kullanıcı, 18 Eylül.)* Skill seçicisine üçüncü bir satır girecek: **Compilation**. Bugün iki satır
var — *Start a scenario* ve *Edit prompts* *(Madde 101)*.

**Kararlaşmadı: skill'in ne yaptığı.** Kullanıcı yalnız adını verdi; neyi derlediği, girdisinin ve
çıktısının ne olduğu konuşulmadı. **Başlamadan önce kullanıcıyla konuşulur**, ve varılan karar buraya
yazılır.

**Değişen:** [domain/skills.py](backend/features/workspace/domain/skills.py) *(`INSTRUCTIONS`)*,
[domain/prompt.py](backend/features/workspace/domain/prompt.py) *(skill'in metni)*,
[skills.js](frontend/src/features/workspace/skills.js) *(`SKILLS`)*; ve bunları çivileyen testler —
`test_skills.py`, `skills.test.js`, `SkillPicker.test.jsx`; `dist`.

## Kare başına negatif prompt üretilecek

*(Kullanıcı, 17 Eylül.)* İş iki görevdir: negatif prompt'ları **QueenAgent üretir**, queen-editor
**alır ve kullanır**. Bu görev QueenAgent'ın yarısı. Alan yarı
[queen-editor'ün backlog'unda](../queen-editor/BACKLOG.md) *"Kare başına negatif prompt alınacak"*
başlığıyla duruyor.

QueenAgent prompt'ları yazarken negatif prompt'ları da yazacak, gerekiyorsa her kare için ayrı. Üç
katmanın her biri kendi başlığında:

### Fotoğraf

Her fotoğraf karesi için, gerekiyorsa, kendi negatif prompt'u yazılır.

### Video

Her kare için, gerekiyorsa, kendi video negatif prompt'u yazılır.

### Ses

Her kare için, gerekiyorsa, kendi ses negatif prompt'u yazılır.

**Kararlaşmadı:** "Gerekiyorsa" neye göre belirlenecek? Negatif prompt her karede mi yazılacak, yoksa
yalnız o kareye özgü bir şey olduğunda mı?

**Başlamadan önce kullanıcıyla ayrıntılı konuşulur** *(kullanıcı, 17 Eylül)*. Madde sırası gelince
koşulacak, ama ilk turun spec'i yazılmadan önce üç başlığın her biri kullanıcıyla tek tek konuşulur.
Varılan kararlar da buraya ya da maddenin satırına yazılır.

## Model menüsü DeepSeek'in 10 Eylül değişikliğine göre yenilenecek

*(DeepSeek'in [10 Eylül 2026 duyurusu](https://api-docs.deepseek.com/news/news260910), 11 Eylül'de
okundu. Menüdeki iki satır da eskidi, ve biri **14 Eylül'de** yalan söylemeye başlıyor.)*

**Üç şey değişti:**

1. **`deepseek-v4-pro` 14 Eylül 04:00 UTC'de kapanıyor.** İstekler V4.1-Flash'a yönlenecek ve Flash
   fiyatından faturalanacak. Hata dönmüyor — o yüzden *Queen Pro* seçen biri Flash alacak, ekran
   Pro yazmaya devam edecek, ve fatura da Flash gelecek. Sessizce yanlış olan bir menü satırı.
2. **Flash'ın fiyatı düştü.** Giriş $0.22 → **$0.15**, çıkış $0.66 → **$0.60** *(off-peak)*. Menüdeki
   `$0.22 / $0.66 per 1M` bugün zaten yanlış.
3. **`deepseek-v4-flash` artık eski ad** — V4.1-Flash'a yönlenen geriye dönük takma ad; modelin
   bugünkü adı `deepseek-flash`. Çağrı çalışıyor, ama ad artık bir şeyin adı değil.

**Kararlaşmadı: Pro satırı ne olacak.** İki okuma var ve ikisi de savunulabilir — *(a)* menüden
tümüyle kalkar, geriye tek model kalır ve o zaman seçicinin kendisi sorgulanır *(Madde 177 üç
satırdan ikiye inerken bu soru sorulmamıştı)*; *(b)* DeepSeek'in bir üst kademesi varsa oraya
bağlanır ve menü iki satır kalır. İkincisi ancak öyle bir model varsa mümkün, ve **bakılmadı**.

**Neden yine olacak:** [models.js:15-17](frontend/src/features/workspace/models.js#L15-L17)
fiyatı elle yazıyor ve bunu bilerek yapıyor — *"seçim bir fiyat sorusu"*. Ama elle yazılan sayı
sağlayıcı değiştirince eskir, ve **hiçbir test bunu yakalayamaz**: süit sayının doğru olduğunu
değil, orada durduğunu tutuyor. Bu maddeye bir de *"fiyat ne zaman okundu"* satırı girebilir; sayıyı
canlı çekmek ise ayrı ve büyük bir iş.

**Değişen:** [backend/config.py](backend/config.py) *(`MODELS`, `DEFAULT_MODEL`, `PROMPT_MODEL`)*,
[frontend/src/features/workspace/models.js](frontend/src/features/workspace/models.js); ve bunları
çivileyen testler — `test_config.py`, `models.test.js`, `ModelPicker.test.jsx`; `dist`.

## Sürüm adın yanında dursun, aynı boyda ve kalın

*(Kullanıcı, 11 Eylül — test geçişi. Madde 209 sürümü ekrana koydu; **nereye** koyduğu yanlış
bulundu, ve o maddenin *"adın altında"* satırı bu maddeyle reddedildi.)*

209 sürümü adın **altına**, `var(--muted)` ile **11px** koydu — deponun **not** sesiyle,
`.msg__stamp` ile `.tool-call__head`'in sesiyle. Bir dipnot gibi duruyor ve okunmuyor. Oysa
cevapladığı soru küçük değil: **hangi kuşağı çalıştırıyorum.**

**Karar verildi** *(kullanıcı, 11 Eylül)*: `V8` adın **yanında**, adla **aynı boyda** *(21px)*, ve
**kalın**. Saklanmayacak. Yani bu madde tartışılacak bir şey değil, koşacak bir yer bekliyor.

**Öne çıkaran şey ağırlık, renk değil.** Deponun kuralı: tek dolu accent **birincil eylemi**
işaretler ve başka hiçbir şeyi — bir proje satırının bile kendi rengi yok. Sürüm adın mürekkebini
taşır *(`var(--ink)`)* ve kalınlıkla ayrışır.

**Ne çalışır:** `.sidebar__version` marka satırının içinde, adın hemen yanında durur.
`.sidebar__name` sütunu **kalkar** — alt alta dizmek için açılmıştı, ve artık alt alta değiller.
Katlanma değişmez *(çubuk katlanınca marka bloğu zaten çizilmiyor)*, ve `shared/version.js`
değişmez: bu madde sürümün **nasıl göründüğü** hakkında, ne yazdığı hakkında değil.

**Değişen:** `Sidebar.jsx`, `workspace.css`; `Sidebar.test.jsx` *(sürümün marka satırında durduğu)*,
`workspace.css.test.js` *(boy, ağırlık, renk, ve `.sidebar__name`'in yokluğu)*; `dist`. Bir de
[test listesinin](../docs/2026-09-10-queenagent-v8-test-listesi.md) *"adın altında"* satırı.

## Kalem ile saat aynı mesajın altında uyuşmuyor

*(Kullanıcı, 11 Eylül — test geçişi.)*

Bir mesajın altında bugün **iki ayrı satır** var: `.msg__foot` — sürüm şeridi `‹ 1/2 ›` ile kalem
`✎` yan yana *(Madde 199)* — ve ayrıca `.msg__stamp`, saat ve jeton sayısı *(Madde 83, 194 ile
canlı hâli)*. Kullanıcı ikisinin **uyuşmadığını** söylüyor.

**Sebep yazılmadı, bilerek:** hangisinin yanlış olduğu — hizası mı, boyu mu, rengi mi, yoksa
ikisinin ayrı satırlarda durması mı — bakanın söyleyeceği şey. Buraya gözlem yazıldı, teşhis değil.

**Kararlaşmadı:** ikisi tek satırda mı buluşacak, yoksa biri ötekinin sesine mi uyacak. Madde 199
sürüm şeridi ile kalemi tek satırda buluşturmuştu ve gerekçesi *"`.msg` bir sütun, her çocuğu kendi
satırını alıyor"*du; aynı soru bir kez daha, bu kez damgayla.

## Yeni proje ve yeni sohbet açmak karmaşık

*(Kullanıcı, 11 Eylül — test geçişi.)*

Bugün üç ayrı yer var: kenar çubuğunda *Projects* başlığının yanındaki `+` *(yeni proje)*, bir proje
seçiliyken üstte duran *New chat* düğmesi, ve hiç proje yokken karşılayan ayrı ekran
*(`NoProjectsScreen`)*. Kullanıcı akışı **karmaşık** buluyor.

**Kararlaşmadı:** neyin karmaşık olduğu. Üç ihtimal ayrı ayrı duruyor — iki işin iki ayrı yerde iki
ayrı düğmesi olması, adlandırma *(191'den beri *New project 3* diye doğuyor)*, ya da yeni sohbetin
bir projeye bağlı olmasının kendisi. **Tasarım kararı verilmeden kod açılmaz:** burada kaybolan şey
bir hata değil bir yol, ve yolu değiştirmek ekranın kendi kararı.

## Dosyalar bir tur öncesine geri sarılacak

*(Kullanıcı, 8 Eylül. Madde 195'in ilk taslağında vardı, tasarım konuşulurken geri çekildi.)*

Madde 195 **sohbeti** sürümlüyor: bir mesaj düzenlenince o noktadan yeni bir çizgi açılıyor. Geri
gitmeyen şey **dosyalar** — eski bir sürümden koşan tur bugünkü `files/`'ı görüyor *(Madde 129: kap
diskten okuyor)*. Yani konuşma geri alınabiliyor, o konuşmanın **yaptığı iş** alınamıyor.

**İstenirse ne gerekir:** dosyanın eski hâli bugün hiçbir yerde durmuyor — üzerine yazılan içerik
gidiyor, yalnız silinen dosya `trash/`'e taşınıyor. Yani madde, her turdan önce projenin `files/`
klasörünü saklayan bir düzenle başlar; geri sarmak o kopyayı yerine koymak olur, ve geri sarmanın
kendisi de bir kopya alarak geri alınabilir kalır *(FOUNDATION 1)*.

**Konuşmada varılan yer:** tam kopya, fark listesinden **basit** — bir kopya kayamaz, ve dosyalar
kilobaytlarla ölçülen metin dosyaları. **Kararlaşmadı:** kapsamın bütün klasör mü yoksa yalnız o
turun dokunduğu dosyalar mı olduğu. Elle Drive'a konmuş bir dosya birinci seçenekte geri sarmayla
kaybolur — bedeli geri sarmanın geri alınabilir olması karşılıyor, ama karar verilmedi.

**Neden şimdi değil:** istenen şey *"yanlış istediğim mesajı düzeltmek"*ti, ve dosya yarısı onun
yanında büyük kaldı.
