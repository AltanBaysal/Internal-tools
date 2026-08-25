# Madde 67 — Çalışan cevap durdurulur · **test turu**

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 67 ·
**Tur:** ikiden birincisi — bu belge yalnız **testleri** tarif eder.

---

## Ne kanıtlanacak

Yol haritasının cümlesi: *"uzun bir cevabın ortasında durduruluyor; sohbet olduğu yerde kalıyor,
geri dönüldüğünde kendi kendine yeniden başlamıyor."* Üç iddia:

1. Durdurma **gerçekten kesiyor** — sunucudaki tur da bitiyor, yalnız ekran susmuyor.
2. Okunan yarım metin **kalıyor** *(kullanıcı kararı, 25 Ağustos — seçenek A)*.
3. Cevap **kendi kendine yeniden başlamıyor**.

Üçüncüsü kolay atlanır ve maddeyi tek başına açık bırakır: bu uygulamada, son sözü kullanıcının
olan bir sohbet cevap borçlu sayılıyor ve tarayıcı o cevabı **kendiliğinden** istiyor. Bir şey
yapılmazsa durdurulan cevap saniyesinde yeniden başlar.

## Bu maddenin getirdiği yeni şey

Bugüne kadar bu uygulamada **istekler arası paylaşılan bellek durumu yoktu.** Durdurma onu
gerektiriyor: "dur" ayrı bir istek olarak geliyor ve akmakta olan isteğe ulaşması gerekiyor.

**FOUNDATION ile çelişmiyor, ve sebebi yazılmalı.** *Gerçek diskte durur* kuralı **kalıcı olması
gereken** şey için: mesajın kendisi diske yazılıyor ve orada kalıyor. Durdurma isteği kalıcı bir
şey değil — tam olarak bir cevabın ömrü kadar yaşıyor. Süreç ölürse cevap da ölür, yani geride
durdurulacak bir şey kalmaz. Diske yazılan bir "durdur" bayrağı, sahibi çoktan ölmüşken bir sonraki
koşuyu durdururdu.

**Sunucunun aynı anda iki isteği alabildiği doğrulandı** (25 Ağustos): Flask'ın geliştirme sunucusu
varsayılan olarak çok iş parçacıklı çalışıyor. Bu doğrulanmasaydı "dur" isteği sıraya girer ve
düğme hiçbir işe yaramazdı. İki iş parçacığı aynı kaydı okuyup yazacağı için kayıt bir kilit taşır.

## Karara bağlananlar

**Kesme noktası: parçaların arası.** Döngü her parçadan önce bakar. Sınıra gelmek nasıl bir hata
değil bir son ise, durdurmak da öyle.

**Saklanan: o ana kadar söylenen her şey**, doğan dosyalar ve yapılan çağrılarla birlikte. Mesaj
**durdurulmuş olarak işaretlenir** — bu benim kararım, kullanıcının değil: yarım bir cümle işaretsiz
durduğunda, düşünmesi biten bir modelden ayırt edilemiyor ve sohbeti sonra okuyan yanlış okuyor.
İşareti düşürmek tek satırlık bir iş.

**Hiç konuşmadan durdurulduysa mesaj yazılmaz.** Saklanacak bir şey yok; sohbet olduğu gibi kalır.
Boş mesaj kuralı zaten bunu söylüyor ve değişmiyor.

**Bayrak cevap bittiğinde temizlenir.** Kalırsa bir sonraki cevap doğar doğmaz kesilir.

**Otomatik istek durdurulunca susar.** Tarayıcı bir "durduruldu" hâli tutar ve kullanıcı yeni bir
şey söyleyene kadar kendiliğinden cevap istemez — bugün hata hâlinin yaptığının aynısı, aynı
sebeple: kırık bir motora sonsuza kadar sormamak.

## Yazılacak testler

### Arka uç

**Durdurma kaydı — üç test.** Sorulmadan istenmemiş sayılıyor; istendikten sonra isteniyor;
temizlendikten sonra yine istenmiyor. Bir sohbete konan bayrak **başka bir sohbeti** etkilemiyor.

**`stream_answer` — dört test.** Akışın ortasında durdurma istenirse motor bir daha çağrılmıyor ve
üretim bitiyor. O ana kadar söylenen diske yazılıyor. Yazılan mesaj durdurulmuş olarak
işaretleniyor. Hiç konuşulmadan durdurulduysa hiçbir mesaj yazılmıyor ve sohbet olduğu gibi kalıyor.
Ayrıca: cevap bittiğinde bayrak temizlenmiş oluyor.

**Rotalar — üç test.** Durdurma isteği kabul ediliyor; olmayan sohbet için 404; sohbetin JSON'u
mesajın durdurulmuş olduğunu taşıyor.

**Depo — iki test.** `stopped` yalnız doğruyken diske yazılıyor; taşımayan eski bir sohbet okununca
mesajlar durdurulmamış geliyor.

### Ön yüz

**`ChatScreen` — üç test.** Cevap akarken durdurma düğmesi var; boştayken yok; basıldığında
kendisine verilen yolu çağırıyor.

**`App` — iki test.** Durdurulan sohbet **kendiliğinden yeniden istemiyor.** Kullanıcı yeni bir
mesaj gönderdiğinde otomatik istek yeniden çalışıyor — "durduruldu" hâli o sohbeti sonsuza kadar
sessizleştirmiyor.

## Kapsam dışı

Durdurulan cevaba devam etmek · durdurmanın geri alınması · sohbetten çıkmanın turu bitirmesi
*(ayrı bir davranış; bu madde düğmeyi getiriyor)* · düğmenin görünümü *(tasarım sonra gelecek —
koşunun kaydına bakılsın)* · token sayacı *(Madde 68)*.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Hepsi kırmızı: bugün ne durdurma kaydı var, ne uç nokta, ne `stopped` alanı, ne de düğme. Kırmızı
görüldükten sonra **kırmızı hâliyle commit'lenir**; `skip` ve `xfail` yok.

Testlerin konuşabilmesi için gereken **adlar** — durdurma kaydının kendisi ve `stopped` alanı — bu
turda doğar. Madde 66'da öğrenildi: içe aktarılamayan bir ad `pytest`i toplama hatasına düşürüyor
ve o zaman suite kırmızı değil **bozuk** oluyor, geri kalan testlerin durumu da görünmüyor.
