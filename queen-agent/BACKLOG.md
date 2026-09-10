# Backlog — QueenAgent

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

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
