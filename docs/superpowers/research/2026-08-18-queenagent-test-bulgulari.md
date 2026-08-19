# QueenAgent — Test Bulguları

**18 Ağustos** · kullanıcının kendi turu · liste açık, tur sürdükçe eklenir.

---

**1.** Bir dosya açıldığında ekran kalabalık görünüyor. Okuyucunun altında duran "project file"
yazısı istenmiyor — dosyanın projeye ait olduğunu orada tekrar söylemeye gerek yok.

**2.** Sohbetin sağındaki dosya bölümü şu an sabit genişlikte. Kenarından tutulup sürüklenerek
yatayda genişletilebilmeli ve daraltılabilmeli. Bugünkü kapanıp açılma da yerinde kalmalı.

**3.** Soldaki proje bölümü sürüklenerek ayarlanmasın. Tek düğmeyle sola doğru toplanıp tamamen
kapansın, aynı düğmeyle geri açılsın — claude.ai'ın kenar çubuğundaki davranış.

**4.** "Generate prompts+" her kullanıldığında ekranda "Couldn't get a response. network error"
çıkıyor. Ağ hatası değil: model o turda hiç konuşmadan yalnız tool çağırıyor, boş metinli cevap
`EmptyMessage` ile reddediliyor ve hata akışın ortasında patlıyor. Dosyalar diske yazılmış oluyor,
ama cevap kaydedilmiyor ve tur hatayla bitiyor. Kullanıcının gözlemi: üretim ve güncelleme gerçekten
çalışıyor, görünen tek şey yanlış hata kartı.

**5.** Karakter promptu becerisi değişiyor. Kaç aday üreteceğini kullanıcı söylemediyse model
**sorsun**; söylediyse o kadar üretsin (bugünkü "2-3 aday" kuralı düşüyor). Çıktı sohbete değil,
**tool ile dosyaya** yazılsın — yapı dosyasındaki `characters` haritasıyla aynı şekilde bir JSON,
doğrudan yapıştırılabilsin. Kullanıcı beğendiği bir promptu yapıştırırsa onu biçim örneği alsın ve
içinden kareye ait olanları (poz, mekân, kamera, kalite etiketleri) ayıklasın. Dosyanın adı
**karakterin adını taşısın** (`aylin.json`); genel bir ad denemeler biriktikçe hangisinin kim
olduğunu kaybettiriyor.

**6.** Yapı JSON'una kıyafet giriyor. İlke: **kalıcı olan `characters`'ta, değişebilen
`outfits`'te.** `outfits` üst seviyede, `characters`'ın kardeşi — kıyafetler karakterler arasında
ortak kullanılır ve giyene göre değil giysiye göre adlandırılır:

```json
"characters": { "aylin": "1girl, mid 20s, long teal hair" },
"outfits":    { "gecelik": "white nightgown", "gunluk": "jeans, black t-shirt" }
```

Karede karakter alanı harita olur — anahtar karakter, değer kıyafet listesi:

```json
"characters": { "aylin": ["gecelik", "atki"], "deniz": ["takim"] }
```

Kıyafetsiz karakter `"aylin": []`, karaktersiz kare `{}`. Birleştirmede her karakterin bloğu bitişik
kalır (kimlik + kıyafetleri yan yana). Bilinmeyen ad isimli hata verir. Kıyafet etiketi
`characters`'a ya da `action`'a yazılırsa verify ihlal der. Eski dosyalardaki liste hâli
(`["aylin"]`) "adlar, kıyafetsiz" diye okunur — kırılmaz.

**Karar verildi**; dolu örnek: [2026-08-18-ornek-yapi.json](2026-08-18-ornek-yapi.json).

**7.** Senaryo becerisi değişiyor. Senaryonun amacı AI'ın hikâyeyi **ne anladığını görmek** — o
yüzden kısa kalsın, ana hatlar yetsin, detaya girmesin. Düz nesir yerine **madde madde** yazsın,
okuması kolaylaşıyor (bugünkü "10-15 cümle, akan metin" kuralı düşüyor). Sohbete ve dosyaya
aynı anda yazsın; sohbette düzeltilince **dosya da güncellensin** (`edit_file`). Dosyanın adı sabit
`scenario.md` olmasın, **konusundan türesin** (`bar-sahnesi.md`) — bir projede birden çok senaryo
yaşıyor, genel ad karıştırıyor.

**8.** Sohbetin sağındaki dosya listesinden de dosya silinebilsin. Bugün satırların ×'i yalnız proje
ekranında; sohbetteyken kazara doğan bir dosyayı (`bar-shots-2.json`) silmek için proje ekranına
dönmek gerekiyor. Aynı ×, aynı onay kutusu — rayda da.

**9.** "Shot" kelimesi düşüyor, yerine **frame**: Türkçe konuşurken zaten "kare" deniyor, üretilen
şey de tek durağan görüntü — "shot" süre ve kamera hareketi çağrıştırıyor. Değişenler: beceri adı
**Split into frames**, JSON alanı `"frames"`, hata mesajları ("frame 3: …"), dosya eki
(`bar-frames.json`), sohbetteki liste başlıkları. Eski `"shots"` alanı okunmaya devam eder.
Denetleyen beceri kare adı taşımaz — promptların malzemesine bakıyor: adı **Verify prompts** olur,
menü açıklaması "Check the structure files against the rules."

**10.** Split into frames'te her karenin açıklaması **1-2 cümle** — uzun uzun anlatmasın. Bugünkü
yönerge zaten "tek satır" diyor ama model uymuyor; sayı yönergeye açıkça yazılır.

**11.** Kare listesi hep İngilizce geliyor — **konuşulan dilde** gelsin; İngilizceye çeviriyi
prompt üreten beceriler yapar, JSON ve `PROMPTS` İngilizce kalır. Liste yalnız sohbette de kalmasın:
senaryo gibi **hem sohbete hem md dosyasına** yazılsın (ad konudan türer, `bar-sahnesi-frames.md`),
düzeltmeler dosyaya da işler.

**12.** Varsayılan model `grok-4.5` yerine **`grok-4.3`** olsun (ucuz ve 1M bağlam; model zaten
menüde var). Kendi modelini seçmiş sohbetler etkilenmez.

**13.** `grok-4.5` menüden kalksın — fiyatı bir üst sürümü `grok-4.6` ile aynı, aynı paraya eski
sürümü sunmanın anlamı yok. Onu seçmiş eski sohbet varsa düğme ham id'yi gösterir ve çalışmaya devam
eder (menüde olmayan id zaten böyle davranıyor).

**14.** Model ya da beceri menüsünden bir satır seçince menü **kendiliğinden kapansın** — bugün açık
kalıyor, ikinci bir tıklama gerekiyor. Seçim yapıldı, menünün işi bitti.
