# Madde 185 · uygulama turu — action'ı olmayan bütün kareleri dolduran araç

**Kaynağı:** [test turu](2026-09-06-queenagent-m185-toplu-eylem-testler-design.md), `4389dd7`'de
16 kırmızı.

---

## Ne yazılıyor

`tools.py`'de `_write_missing_actions`, `run_tool`'da dalı, `TOOL_SPECS`'te girişi, ve
`prompt.py`'de iki metin — açıklama ve *(dosya adı için)* zaten orada duran `THE_STRUCTURES_FILE`.
Bir de skill metninin iki cümlesi.

## Üç kapı, ucuzdan pahalıya

Sırayla, ve sırası önemli: **model yok mu**, **dosya açılıyor mu**, **hangi kareler bekliyor**.
Üçüncüsü de kendi içinde eleme yapıyor — `action`'ı olan atlanıyor, **sahnesi olmayan sorulmadan**
atlanıyor. Tek kareli araç aynı sırayı tutuyor ve sebebi aynı: hiçbir ret için para ödenmiyor.

## Paralellik: `ThreadPoolExecutor`, sekiz kişilik

`engine.write_once` bloklayan bir HTTP çağrısı, yani iş parçacığı doğru araç — burada beklenen şey
CPU değil, ağ.

**Sekiz**, ve keyfî değil: kırk kareyi kırk soket olarak açmak servisin hız sınırına koşmak demek,
ve sekizle kırk arasındaki duvar saati farkı zaten bir raunt etmiyor. Sayı bir sabit, adı
`AT_ONCE`, ve neden sekiz olduğu yanında yazılı.

**İstekten başka hiçbir şey iş parçacığına girmiyor.** `_frame_seen` çağrısı `submit`'in argümanı
olarak ana iş parçacığında koşuyor, yani yapıyı okuyan tek taraf orası; iş parçacıklarının elinde
yalnız hazır iki string var. Cevaplar da ana tarafta, gönderim sırasına göre toplanıyor — sonuçların
sırası bu yüzden kararlı, ve cevaptaki numaralar artan sırada çıkıyor.

## Dosya bir kez yazılıyor

Bütün cevaplar toplandıktan sonra, ve yalnız **bir şey yazıldıysa**. Yarısı yazılmış bir dosya diye
bir ara hâl olmuyor, ve hiçbir şey yazılmadıysa dosyaya dokunulmuyor.

## Cevap iki cümle

Ne yazıldığı — kaç kare ve **numaralarıyla**, çünkü modelin sonraki hamlesi o numaralara bakmak. Ve
yazılamayanlar, her biri **kendi sebebiyle**: servisin kendi cümlesi, *boş cevap verdi*, ya da
*yazılacak sahne yok*. Sebep uydurulmuyor.

Hiç bekleyen kare yoksa tek cümle, ve `spent` **None** — hiçbir şey ödenmedi, ve sıfırlardan oluşan
bir satır damgaya gürültüden başka bir şey koymaz.

## Fatura tek toplam

Her cevabın hesabı toplanıp tek sözlük olarak dönüyor. Düşen bir istek hesap taşımıyor; **boş cevap
veren taşıyor**, çünkü o istek gerçekten yapıldı ve ödendi.

## Skill metni: iki cümle, ve tavan

`GENERATE_PROMPTS_PLUS` bugün *"one at a time … in the frames' order"* diyor — o cümle **kalkıyor**,
yanına eklenmiyor: bir metinde aynı işin iki yolu, modelin seçmesi demek, ve pahalı olan dikkatli
olan gibi okunur. Tek kareli araç, zaten var olan *şikâyet* paragrafında adıyla anılıyor — düzeltme
onun işi.

Kelime tavanı 300, ve bu değişim metni **kısaltıyor**.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. 16 kırmızı kapanıyor; öteki üç takım kımıldamıyor.
