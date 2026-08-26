# Madde 68 — Token tüketimi okunur · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 68 ·
**Tur:** ikiden birincisi — bu belge yalnız **testleri** tarif eder.

---

## Ne kanıtlanacak

Yol haritasının cümlesi: *"bir soru soruluyor ve cevabın yanında tüketim okunuyor; aynı sohbette
ikinci soruda önbellekten gelen payın büyüdüğü görülüyor."* Üç iddia:

1. Servisin söylediği sayı **alınıyor** — bugün geliyor ve yere düşüyor.
2. Sayı **saklanıyor** — sohbeti yarın açan da ne harcandığını okuyor.
3. Sayı **görünüyor**, her cevabın altında *(kullanıcı kararı, 26 Ağustos — seçenek A)*.

Üçüncüsünde ekranda **tek sayı** duruyor *(kullanıcı kararı, 26 Ağustos)*: bu cevabın kaç token
harcadığı. Kırılım ekrana çıkmıyor.

Bu madde hiçbir şeyi optimize etmiyor. Ölçüyü kuruyor, çünkü
[FOUNDATION](../../../queen-agent/FOUNDATION.md)'ın 3. ilkesi ölçülmemiş bir sorunu optimize etmeyi
yasaklıyor ve Madde 71 tam olarak o optimizasyon.

## Servisin gerçekte ne söylediği

Ezberden yazılmadı; xAI dokümanından doğrulandı (26 Ağustos):

- Akan cevapta tüketim **her parçada** geliyor. Ayrıca istenmesi gerekmiyor — `stream_options` ya da
  `include_usage` diye bir şey göndermek gerekmiyor, sayı kendiliğinden düşüyor.
- Alan adları: `usage.prompt_tokens`, `usage.completion_tokens`,
  `usage.prompt_tokens_details.cached_tokens`.
- **Bir parçadaki sayı o akışın başından beri toplamı**, o parçanın payı değil: `completion_tokens`
  parça parça büyüyor.
- **`cached_tokens`, `prompt_tokens`'ın içinde** — üstüne eklenen ayrı bir sayı değil. Yeniden
  ödenen kısım ikisinin farkı.

Bu dördü tasarımın tamamını belirliyor, o yüzden burada yazılı.

## Karara bağlananlar

**Üç sayı saklanır, dördüncüsü hesaplanır.** Diske `sent` (isteğin taşıdığı her şey), `cached`
(bunun servisin zaten elinde olan kısmı) ve `answered` (modelin yazdığı) gider. *Yeniden ödenen*
sayı `sent - cached` olduğu için saklanmaz — CODE-STANDARD'ın kuralı: diskte duran bir cevabı
tekrar eden alan silinmek ister.

**Toplam turda, tur içinde en son söylenen geçerli.** Bir cevap on altı tura kadar dönüyor ve her
tur ayrı bir akış. Akışın içinde sayı kümülatif olduğu için **en yenisi öncekini siler**; turlar ise
gerçekten ayrı harcamalar olduğu için **toplanır**. İki cümlelik tek bir kural.

**Sayı akarken gösterilmez.** Tüketim, cevabın *neye mal olduğu* — bu ancak cevap bittiğinde
bilinir. Kayıt zaten akışın sonunda iniyor ve sayıyı taşıyor; ayrı bir canlı olay kazanç getirmezdi.

**Durdurulan cevap da harcadığını söyler.** Kullanıcı kesse bile o turun girdisi çoktan gönderilmiş
ve ödenmiş. Sayının her parçada gelmesi bunu mümkün kılıyor: kesildiği anda okunmuş olan son sayı,
o ana kadarki harcamanın doğru resmidir. Sayı yalnız akışın sonunda gelseydi durdurulan turun
tamamı ölçüden düşerdi — ve pahalı olan kısım tam da girdi.

**Ölçmeyen bir akış sıfır yazar.** Motor tüketimden hiç söz etmezse mesaj sıfır taşır ve ekranda
hiçbir şey çıkmaz. Sıfır burada "bilinmiyor" demek, ve bu bilerek: eski sohbetler de sıfır okunur,
yani hiçbir kaydın dönüştürülmesi gerekmiyor. `model` ve `calls` alanları da aynı yoldan geldi.

**Ekranda tek sayı, kayıtta üç sayı** *(kullanıcı kararı, 26 Ağustos)*. Satır `13.2k tokens` yazar
ve o kadar; harcanan `sent + answered`'dır. Kırılım yine de diske gider, çünkü bu maddenin var olma
sebebi önbellek: Madde 71 "önbellekten ne kadar geldi" sorusuna bakarak yol seçecek, ve ekrana
çıkmayan bir sayı kaydedilmezse o soru cevapsız kalır. Servis üçünü tek bir nesnede gönderdiği için
saklamak fazladan iş değil, ve satırı sonra açmak yalnız ön yüze dokunur.

## Sözleşmede değişen ne

`Engine.stream` bugün iki tip parça veriyor: `{"text": ...}` ve `{"tool_calls": [...]}`. Üçüncüsü
geliyor: `{"usage": {"sent": n, "cached": n, "answered": n}}`.

Adlar xAI'nin değil bizim: alan adını çeviren yer, bugün `delta.content`'i `text` yapan yerle aynı
yer — `services/xai/client.py`. Domain'in xAI kelimesi öğrenmesi gerekmiyor.

**Var olan sahte motorlar değişmiyor.** Tüketimden söz etmeyen bir akış üçüncü parçayı hiç
üretmiyor, o yüzden bugünkü testlerin hiçbiri bu yüzden kırmızıya düşmemeli. Düşerse bu bir
bulgudur, uygulama turunda not edilir.

## Yazılacak testler

### Arka uç

**`XaiClient` — dört test.** Tüketim taşıyan bir kare tüketim parçası veriyor ve üç sayıyı
çeviriyor. Hem içerik hem tüketim taşıyan bir kare ikisini birden veriyor. `prompt_tokens_details`
hiç yoksa önbellek sıfır okunuyor. Tüketimsiz bir akış hiç tüketim parçası vermiyor.

**`stream_answer` — beş test.** Cevap harcadığını hatırlıyor. İki turun sayıları toplanıyor. Tek
turda tekrarlanan sayı iki kez sayılmıyor — en sonuncusu geçerli. Hiç ölçülmemiş bir cevap sıfır
taşıyor. Ortasında durdurulan cevap o ana kadar ölçüleni saklıyor.

**Depo — üç test.** Sıfır olmayan tüketim diske yazılıyor. Tamamen sıfırsa alan hiç yazılmıyor.
Alanı taşımayan eski bir sohbet okununca mesajlar sıfır tüketimle geliyor.

**Rotalar — iki test.** Mesajın JSON'u tüketimi taşıyor. Sıfır olduğunda da taşıyor — tarayıcı
eline verilen şeyi çiziyor, ve yokluğu her okuyucuya bir kontrol yazdırırdı.

### Ön yüz

**`ChatScreen` — dört test.** Cevabın altında tek sayılık tüketim satırı çiziliyor ve sayı
`sent + answered`. Tüketimi olmayan mesaj satır çizmiyor. Büyük sayılar `k` ile kısalıyor.
Kullanıcının kendi mesajı hiç satır taşımıyor.

## Kapsam dışı

Paraya çevirmek *(fiyat modele göre değişiyor, ve bu madde ölçü kuruyor)* · sohbet toplamı
*(seçenek B — kullanıcı A'yı seçti; A'dan toplanabilir)* · kırılımı ekranda göstermek
*(kullanıcı kararı — diske yazılıyor, satırı açmak sonra tek bir ön yüz işi)* · akarken canlı sayaç · bağlamı
küçültmek *(Madde 71 — ve bu maddenin var olma sebebi)* · bir uyarı eşiği · `complete` yolunun
tüketimi *(akış yolu her cevabı taşıyor; `complete` bu uygulamada bir cevabı akıtmıyor)*.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Hepsi kırmızı: bugün ne `Usage` tipi var, ne istemci tüketime bakıyor, ne diskte alan var, ne de
ekranda satır.

Testlerin konuşabilmesi için gereken **ad** — `Usage` — bu turda doğar. Madde 66'da öğrenildi:
içe aktarılamayan bir ad `pytest`i toplama hatasına düşürüyor, ve o zaman suite kırmızı değil
**bozuk** oluyor; geri kalan testlerin durumu da görünmüyor.
