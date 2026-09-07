# Deneme 3 · bulgular — v7 baştan sona koştu

**Ne koşuldu:** `feat/queenagent-v7` *(166–179)*, Colab, tek sohbet. Sıfırdan bir senaryo: üç
karakter, üç kıyafet, bir mekân, 23 kare, ve 23 karenin action'ı + derleme.

Bu belge **konuşmanın kendisini taşımıyor** — taşıdığı şey neyin beklendiği gibi olduğu, neyin
olmadığı, ve her birinin hangi maddeye dokunduğu.

---

# Beklendiği gibi olanlar

## 1 · Model şemasız kurdu *(Madde 172'nin bahsi tuttu)*

Dilim 1'in bütün bahsi buydu: **model dosyanın şeklini hiçbir yerden okuyamadan, yalnız araç
imzalarıyla senaryo kurabilir mi.**

Kurdu. Tek bir *"şema nerede"* denemesi olmadı, tek bir `.json` yazma girişimi olmadı — yani 171'in
kapısı hiç çalınmadı bile, çünkü modelin elinde alternatif vardı.

Dahası: kullanıcı *"promptlar tag tag mi yoksa cümle gibi mi"* diye sorduğunda model **doğru
cevapladı** — haritalar etiket, sahne cümlesi kullanıcının dilinde ve prompta girmiyor, son prompt
tamamen etiket. Bunu hiçbir yerden okumadı; `SDXL_PROMPT_RULES`'un altı araç açıklamasında duran
kopyalarından biliyordu.

## 2 · Yeniden adlandırma karelere yürüdü *(Madde 168)*

Kullanıcı *"isimleri İngilizce yap"* dedi. Üç `update_character` çağrısı, üçü de `new_name` ile.
Karelerde henüz kimse yoktu ama harita düzgün yeniden kuruldu ve kıyafet adları da aynı turda
İngilizceye döndü. **Altı adım, tek turda, tek soru sormadan.**

## 3 · Yirmi üç kare tek çağrıda doğdu *(Madde 173)*

En büyük tasarruf burada: `add_scene` 23 sahneyi **bir çağrıda** aldı, hepsinin adını haritalarda
buldu, hiçbirini reddetmedi. Eski `add_frames` beşerli partiler istiyordu; bu, beş yerine bir raund.

Ve kadro kareye doğarken girdi — sonradan eklenen bir alan değil.

## 4 · Plan tek `edit_file` ile işaretlendi *(Madde 126)*

Adımlar bitince plan dosyasındaki satırlar `edit_file` ile işaretlendi, `write_plan` ile yeniden
yazılmadı. 126'nın tam istediği şey.

## 5 · Dil ayrımı kusursuz tuttu

- Kullanıcıya konuşma: **Türkçe**
- Harita girdileri ve action: **İngilizce**
- Sahne cümleleri: **Türkçe** *(prompta girmiyorlar, girmediler de)*
- Plan dosyası: **Türkçe**

Tek bir sızıntı yok. `CLAUDE.md`'nin *"dil okuyucuya göre ayrılır"* kuralı, üç ayrı yazarın
*(ana ajan, kod, yazıcı model)* elinde bozulmadan durdu.

## 6 · Yarım kalan iş dosyadan devam etti *(Madde 178)*

Kullanıcı *"aksiyonları yazar mısın"* dedi; tur 1–18'i yazıp bitti. **Bir saat sonra** aynı cümle
tekrar yazıldı ve model kaldığı yerden — 19. kareden — devam etti.

178'in metnine koyduğum cümle tam bunun içindi: *"action'ı olmayan kare bekleyen iştir."* Model
dosyayı okudu, nerede kaldığını gördü, oradan sürdürdü. Hiçbir şey iki kere yazılmadı.

## 7 · Derlenen liste sohbete basılmadı *(Madde 130)*

23 prompt `.py` dosyasına gitti, cevaba değil. Model yalnız ne yaptığını özetledi.

---

# Beklendiği gibi olmayanlar

## A · Yazıcı model karakter **adlarını etiket olarak** yazdı

**En net hata bu.** İki karenin action'ında karakterlerin adları geçiyor:

> `... nicole kneeling ... on standing kyle ...`
> `over the shoulder from kyle, ...`

Bir SDXL modeli *"nicole"* diye bir şey bilmez. Bu etiketler ya gürültü ya da rastgele bir yöne
çekiyor.

**Sebebi tasarımda:** `_frame_seen` yazıcıya adları **bilerek** veriyor — kullanıcının kararıydı,
*"etiket ve adlarını görsün"*, ki nottaki ad ile haritadaki etiket eşleşebilsin.
`WRITE_FRAME_SYSTEM_PROMPT` ise adların **ne için** verildiğini hiç söylemiyor. Model de en doğal
şeyi yaptı: eline verilen adı kullandı.

**Çözüm bir cümle:** adlar notu eşleştirmek için; yazdığın satıra hiçbiri girmez.

## B · *"Komşu kareler çekimde ayrılsın"* kuralı, göremediği bir şeyi istiyor

`WRITE_FRAME_SYSTEM_PROMPT` şunu diyor: *neighbouring frames should not repeat the same framing and
angle.* Ama yazıcı model **yalnız o kareyi** görüyor. Komşusunun ne yaptığını bilmiyor.

Sonuç, çıktıda açıkça duruyor — 4'ten 8'e kadar beş kare üst üste:

> `close-up from side angle` · `side view close-up` · `close-up from the side` ·
> `side angle close-up` · `side view close-up`

Kural metinde, gözlem imkânı yok. **Bir modele göremeyeceği bir şeyi emretmek, kuralı yazmamakla
aynı şey** — hatta daha kötü, çünkü yerine getirildiğini sanıyoruz.

**Üç yol var:**
1. Yazıcıya **bir önceki karenin action'ını** da ver *(tek satır, en ucuz)*.
2. Çeşitliliği ana ajana bırak — o dosyanın tamamını görüyor, notla yönlendirebilir.
3. Kuralı sistem promptundan çıkar.

Birincisi doğru geliyor: yazıcı zaten o karenin kadrosunu görüyor, bir satır daha görmesi bedava.

## C · *"Kimse bir şey giymiyor"* diye bir etiket yok

Sevişme karelerinde kıyafet listesi boş — niyet çıplaklık. Ama:

- `build_prompts` boş listeden hiçbir etiket üretmiyor *(doğru davranış)*
- yazıcı da action'a `nude` benzeri bir şey yazmadı

Sonuç: **19 karenin promptunda çıplaklığı söyleyen tek bir etiket yok.** Görüntü modeli ne çizeceğine
kendi karar verecek — büyük ihtimalle giydirecek.

Bu bir hata değil, bir **boşluk**: boş kıyafet listesi *"bilmiyorum"* ile *"hiçbir şey"* arasında
ayrım yapmıyor, ve yazıcıya bu ayrım anlatılmıyor. Yazıcı kadroyu `wearing` satırı olmadan görüyor
ve bunun ne demek olduğunu bilmiyor.

**En temiz çözüm yazıcıda:** kadroda `wearing` satırı olmayan biri giyinik değildir, ve bunu
söylemek senin satırının işidir.

## D · Araya kare eklemenin yolu yok — ve kuyruğun action'ını yakıyor

İki yerde çıktı, ikincisi ağır.

**Hafif hâli:** kullanıcı 6 karelik öneriyi beğenmeyip kendi 23 karelik yapısını verdi → **6 ayrı
`remove_frame`**, sonra tek `add_scene`.

**Ağır hâli:** action'lar yazıldıktan **sonra** kullanıcı 2. ile 3. karenin arasına bir sahne
istedi. `add_scene` yalnız sona eklediği için modelin tek yolu kuyruğu sökmekti — **21
`remove_frame`**, sonra yeniden kurma. Tek turda **27 adım, 103.8k jeton.** Model bunu kendisi de
söyledi: *"ara ekleme aracı yok, bu yüzden o bölümü yeniden inşa ediyorum."*

**Asıl bedel raundlar değil.** `add_scene` `action` almıyor *(onu 176 yazıyor)*, dolayısıyla geri
eklenen 21 kare **action'sız** döndü ve bir saat önce yazdırılmış **21 Grok cümlesi çöpe gitti.**
İkinci kez ödendi, ve aynı cümleler bir daha gelmeyecek.

Teşhisi ilk yazışımda *"toplu silme lazım"* diye koymuştum — **yanlıştı.** Toplu silme yalnız
raundları düşürürdü; kaybolan action'ları kurtarmazdı. Gereken şey **araya ekleme**.

**Kararı verildi:** `add_scene`'e isteğe bağlı `before` — [Madde 180](../plans/2026-09-05-queenagent-v7-roadmap.md).

## E · Uzun yazma turu sessizce bitti

21:21'de *"aksiyonları yazar mısın"* dendi. **Ekranda hiçbir cevap görünmüyor.** Kullanıcı bir saat
sonra aynı cümleyi tekrar yazdı, ve o tur *"1–18 arası önceden hazırdı"* diyerek 19'dan devam etti.

Yani ilk tur **gerçekten çalıştı, 18 kare yazdı, ve tek kelime etmeden kapandı.**

En olası sebep `MAX_ROUNDS = 16`: tur sınıra dayandı, kapanış raundu bir şey söyleyemedi ya da
söylediği ekrana ulaşmadı. Ne olduğu **kayıttan bakılmalı** — turun damgası ve adımları duruyor.

Kurtarma tarafı çalıştı *(F6)*, ama kullanıcının bunu bilmesinin hiçbir yolu yoktu: bir saat bekledi.

## F · Akışın ilk turu planı yazmadı

Metin şöyle diyor: *"A chat's first turn opens with write_plan… This step alone waits for no
approval; the first question follows at once."*

Gerçekte olan: `başla` → **hiç araç çağrılmadı**, model beş adımı listeleyip konu sordu. Plan bir
tur sonra, konu belli olunca yazıldı.

Savunulabilir *(konusu belli olmayan bir planın ne yazacağı belirsiz)* ama metnin dediği bu değil.
İkisinden biri düzelmeli: ya metin *"konu belli olunca"* desin, ya model ilk turda yazsın.

## G · Maliyetin şekli: kap büyüdükçe her raund tam fiyat

Damgalar: 6.3k → 7.6k → 19.2k → 36.6k → 32.3k → 22.9k → 18.9k → **40.4k** → **69.6k** → 37.4k.

İki zirve, ikisi de kare işleri. Sebep basit: `.json` bağlam kabında, ve kap **her raund diskten
okunup tam fiyat gönderiliyor** — 23 kareli bir yapı dosyası artık küçük bir doküman değil.

179 bunu zaten yazmıştı: *"kaldırılan kopya cache'li olandı; kap tam fiyat gitmeye devam ediyor."*
Deneme bunu rakamla gösteriyor. Kap büyüdükçe **hangi dosyanın kaba girdiği** bir soru hâline
geliyor — bugün kaba giren şey, okunmuş olan her dosya.

---

# Sıraya girecek olanlar

Aciliyet sırasına göre, hepsi birer madde adayı:

| # | Ne | Nerede | Büyüklük | Durum |
|---|---|---|---|---|
| 1 | **Araya kare eklemek** | `add_scene`'e `before` | küçük madde | **Madde 180** |
| 2 | Adlar etiket değildir | `WRITE_FRAME_SYSTEM_PROMPT` | bir cümle | konuşuluyor |
| 3 | Kıyafetsiz kadro çıplaktır | `WRITE_FRAME_SYSTEM_PROMPT` | bir cümle | konuşuluyor |
| 4 | Yazıcı bir önceki karenin action'ını görsün | `_frame_seen` | bir satır + test | konuşuluyor |
| 5 | Uzun yazma turu neden sessiz kapandı | `stream_answer` / kayıt | önce **teşhis** | konuşuluyor |
| 6 | Akışın ilk turu ile metni uyuşsun | `skills.py` ya da metin | bir cümle | konuşuluyor |

**1, 2 ve 3 tek maddede birleşebilir** — üçü de yazıcının gördüğü ve okuduğu şeyle ilgili, ve
üçünün de kanıtı bu denemede.

**4 önce teşhis ister**, düzeltme değil: `MAX_ROUNDS`'a mı dayandı, akış mı koptu, yoksa kapanış
raundu boş mu döndü — üçünün ilacı üç ayrı yer.

---

# Ve cevaplanan bir soru

Denemeden önce sorulmuştu: **Generate prompts+ kalksın, her şey Start a scenario'nun parçası olsun
mu?**

Deneme buna kendi cevabını verdi: **action yazma işi tek bir tura sığmıyor.** 23 kare, 16 raundluk
bir turda bitmedi — ikiye bölündü, ve arada bir saat geçti. Bu işi senaryo kurma akışının 5. adımı
yapmak, onay ritmiyle koşan bir akışın içine **sığmayan** bir faz koymak olurdu.

İki skill ayrı kalsın; ayıran şey artık zanaat değil, **ritim**.
