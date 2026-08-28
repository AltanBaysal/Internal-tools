# Madde 115 — Action yalnız kadrajda görüneni taşır · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m115-kadrajda-gorunen-testler-design.md) —
üç kırmızı `a391286`'da.

## Değişen tek dosya: `schema.py`

**Kendi paragrafı.** Biçim paragrafı zaten yoğun ve o *nasıl yazıldığını* anlatıyor; buradaki soru
*ne yazıldığı*. 110 ve 111 gibi ayrı bir paragraf:

> An action holds only what the camera sees. A scene sentence carries why something is happening
> and what came before it; a frame carries neither, because nothing in the picture shows them. A
> cause is written as what it looks like -- turned away, downcast eyes, tense shoulders -- or it
> is left out.

Üç cümle, üç iş: yasak, nedenin ait olduğu yer, ve nedenin görünür karşılığıyla nasıl yazıldığı.
Üçüncüsü olmadan yasak modeli sahneyi boşaltmaya iter — kayıp bilgi de kusurdur.

**Kural defterine 9. kural.**

> 9. A cause or a moment outside the frame written into an action -- after the argument, later,
> again. Nothing in the picture shows it, so write what it looks like instead.

Defter avlama listesi, ve listenin kendi türü yanlış biçimi göstermek *(2. ve 8. kural da öyle
yapıyor)*. Öğreten örnek yukarıdaki paragrafta ve orada yalnız doğru biçim duruyor.

## Neden sahne listesi değişmiyor

Hikâye onun işi — kullanıcının okuduğu, onayladığı ve gerektiğinde düzelttiği şey o. Ayıklama kareyi
yazarken olur; listeyi kadraja indirgemek kullanıcının elinden okunur metni alırdı *(Madde 108, 4.
adım)*.

## Değişmeyen

- **`skills.py`.** prompt+'ın *"the sentence is a brief, never text to copy into the frame"*
  cümlesi mekanizmayı tutuyor; kural şemada tek nüsha duruyor.
- **Kod.** `build_prompts` ne yazıldıysa onu basıyor.

## Görülür hâli

Üç kırmızı yeşerir. 114'ün artikel süpürmesi yeni paragrafı taramıyor *(yalnız JSON bloğunun
değerlerine bakıyor)*, kalite ve "shot" pinleri de yerinde. Ön yüz değişmiyor, `dist` derlenmiyor.
