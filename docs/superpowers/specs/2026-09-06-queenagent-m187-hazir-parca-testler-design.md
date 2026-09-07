# Madde 187 · test turu — hazır prompt parçaları

**Kaynağı:** [yol haritası, Madde 187](../plans/2026-09-06-queenagent-v8-roadmap.md).
186 `d32a5bb`'de kapandı.

---

## Ne kanıtlanacak

Bilinen şeyler — pozisyonlar gibi — her seferinde yeniden yazdırılıyor. Kullanıcı isteyince modelin
**hazır olanı doğrudan göstermesi** isteniyor.

**Rastgelelik değil.** İçlerinden biri seçilmiyor; **istenen** gösteriliyor. `SDXL_PROMPT_RULES`'un
*"model yazı tura atamaz"* kuralı yerinde duruyor, ve bu araç ona dokunmuyor.

## Nerede durur: `prompt.py`, tek bir eşleme olarak

Madde 189'un modülünde *(kullanıcı kararı)*. Bu **ortak bilgi**, projeye özel değil — aynı pozisyon
her senaryoda aynı. Depoda durunca herkeste aynı oluyor, sürüm kontrolüne giriyor, ve öteki metinler
gibi gözden geçiriliyor. 189'un *"depoda başka yerde prompt yok"* nöbetçisi bunu kendiliğinden
kapsıyor.

**Yirmi ayrı sabit değil, adla anahtarlanmış tek bir eşleme.** Araç bir parçayı **adıyla** buluyor;
ayrı ayrı sabitler yanlarında ikinci bir ad→sabit tablosu isterdi, ve o tablo bu koşunun madde madde
sildiği **kopyanın** ta kendisi olurdu. Bir eşlemede her girişin adı zaten kendi anahtarı.

## Nasıl ulaşılır: araç, prompta gömerek değil

Gömülürse **her raundda** para yakar ve liste büyüdükçe büyür — 185'in bütün dersi bu. Araç olunca
yalnız sorulduğunda ödeniyor.

**Adı `read_prompt_piece`**, ve `read_file`'ın kardeşi: ikisi de bir şey açmıyor, hiçbir şey
değiştirmiyor, ve cevabı metin olarak geri veriyor. Bunun bir sonucu var — `modes.py`'nin `READS`'i
**ikiye çıkıyor**. O listenin bugünkü yorumu *"Madde 172'den beri tek: dosya okumak, hiçbir şey
açmayan ve değiştirmeyen tek iş"* diyor; yarın yanlış olacak, ve düzeltilecek.

**Bilinmeyen bir ad bilinenleri sayıyor**, `build_prompts`'un bugünkü kalıbı gibi. Ad verilmezse de
aynı liste geliyor: modelin ne olduğunu öğrenme yolu bu, ve o yol bir raunda mal oluyor — listeyi
her isteğe bindirmek ise her raunda.

**Ad harf harf aranmıyor.** `naming.folded` ile katlanıyor: *Cowgirl* yazan bir modelin bir raundu
büyük harfe ödemesi için sebep yok.

## Gösterdiğini kareye koymaz

Göstermek göstermektir; kareye koymak `update_frame`'in işi. Bu deponun fiil ayrımı zaten böyle, ve
bir araç iki iş yaparsa hangisini yaptığı cevapta kaybolur.

## Madde 130 ile çelişmiyor

*"Derlenmiş prompt geri basılmaz"* kuralı **üretilmiş sonuç** için: `build_prompts`'un yazdığı dosya
zaten projede duruyor, ve onu sohbete basmak aynı şeyi iki yerde göstermek olur. Hazır parça bir
**referans metin** ve kullanıcının görmek istediği şeyin ta kendisi — dosyası yok, gösterilmezse
hiçbir yerde görünmüyor.

## Skill metinlerine dokunulmuyor, ve sebebi

İkisi de tavanında: akış 450'de, *Edit prompts* 200'de. Araç açıklaması zaten **her turda** gidiyor,
yani modelin bu aracı bulma yolu öteki on dokuzunkiyle aynı. Bir skill metnine ad yazmak, tavanın
altından bir cümle sildirirdi — hiçbir şey kazanmadan.

## Testler

| # | Test | Ne söylüyor |
|---|---|---|
| 1 | bilinen bir ad kendi etiketlerini geri verir | maddenin kendisi |
| 2 | bilinmeyen bir ad **bilinenleri sayar** | uydurmuyor |
| 3 | adsız çağrı da aynı listeyi verir | keşif yolu |
| 4 | büyük harf ve boşluk bir raunda mal olmaz | `folded` |
| 5 | hiçbir dosyaya dokunmaz — `created` yok, `target` boş | fiil ayrımı |
| 6 | kareye hiçbir şey yazmaz | gösterme ≠ koyma |
| 7 | `READS`'te, ve her kipte sormadan koşar | `read_file`'ın kardeşi |
| 8 | hiçbir parça sayı taşımaz *(`1girl` gibi)* | sayı karakterin girişinin işi |
| 9 | hiçbir parça kalite etiketi taşımaz | kodun yazdığı zincirin kopyası olurdu |
| 10 | araç `TOOL_SPECS`'te ve açıklaması `prompt.py`'den | 189'un nöbetçisi |
| 11 | eşleme boş değil, ve her girişi doluş | 8 ve 9'un altını dolduran |

## Kırmızı turun tuzağı, ve on üçüncüsü

Bu koşuda on iki kez görüldü. Beklenen hâli **8, 9 ve 11**'di: boş bir eşleme üzerinde 8 ve 9
hiçbir şey iddia etmeden geçer. 11 o zemini koyuyor, ve 8 ile 9 kendi içlerinde de eşlemenin boş
olmadığını ölçüyor.

**On üçüncüsü beklenmedik yerden çıktı.** *Her kipte sormadan koşar* testi ilk koşuda **yeşil**
geçti — çünkü `needs_permission` **tanımadığı bir araç için de** `False` dönüyor: *"kimsenin
bilmediği bir araç hiç sorulmaz."* Yani test, var olmayan bir araç üzerinde doğruydu. Önüne
`"read_prompt_piece" in READS` kondu; asıl iddia oydu, ve o kırmızı.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent`'ın arka yüzü **11 kırmızı** verdi; ön yüz
ve `queen-editor` kımıldamadı — **591 · 739 · 591.**
