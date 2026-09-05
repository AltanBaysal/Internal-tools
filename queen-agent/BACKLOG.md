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

