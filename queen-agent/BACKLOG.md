# Backlog — QueenAgent

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

## Bütün kareleri tek çağrıda dolduran toplu bir prompt aracı

v7 `write_frame_prompt`'u **tek kare** üzerine kurdu *(kullanıcı kararı, 5 Eylül: önce sade olan,
gerçekten sorun olursa öteki)*. Ana ajan aynı raundda birden çok çağırabiliyor, ama `stream_answer`
çağrıları **sırayla** koşuyor — yani 40 kare arka arkaya.

**Ne zaman açılır:** uzun bir senaryonun promptlarını üretmek dakikaları buluyorsa, ya da turun 16
raundu kare çağırmaya yetmiyorsa.

**Ne olurdu:** boş bütün kareleri dolduran ayrı bir araç, istekleri paralel atan. Tek kareli olan
yerinde kalır — o düzeltmenin aracı, bu koşunun.

## Yazılan promptların okunup doğrulanması

v7'de Grok'un yazdığı action dosyaya gidiyor ve ana ajana dönmüyor *(bilerek: metin konuşmaya
girse kalite düşer)*. Yani bugün yazılanı **kimse okumuyor** — kullanıcı derlenmiş `.py`'ye bakana
kadar. Kural ihlali *(kişiyi yeniden tarif etmek, ad uydurmak, kalite etiketi yazmak, iki kişilik
karede `solo`)* ancak orada görülüyor.

**Ne olurdu:** yazılan action'ları geri okuyup `SDXL_PROMPT_RULES`'a vuran bir adım. Kodla
yakalanabilenler *(bilinmeyen ad, kalite etiketi, `solo` sayımı)* kodda; gerisi için ikinci bir
model sorusu mu, hangi model, ve cevabı ana ajana dönüyor mu — **tasarlanmadı.**

**Ne zaman açılır:** Deneme 2 Grok'un ne tür hata yaptığını gösterdikten sonra. Hatanın türü,
doğrulamanın kodla mı modelle mi olacağını söyler.
