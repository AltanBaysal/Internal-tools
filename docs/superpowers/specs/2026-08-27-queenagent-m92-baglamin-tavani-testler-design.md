# Madde 92 — Bağlamın tavanı olur, ve tavana çarpmak bir olaydır · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 92 ·
**Şartı:** Madde 76 — sayı zaten ölçülüyor
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

Bağlam büyüdükçe hiçbir şey olmuyor. İstek gitmeye devam ediyor, cevabın kalitesi sessizce düşüyor,
ve iş sonunda pencereye sığmayan bir istekle hataya bağlanıyor. Kullanıcı bunun geldiğini görmüyor
— sayı her cevabın altında yazıyor ama bir sayı tek başına "yaklaşıyorsun" demiyor.

## Ne olur

İki şey, ve ikisi de **aynı sayıyı** okuyor:

1. **Bir tavan.** Son cevabın gönderdiği token tavanın üstündeyse o sohbet yeni istek atmıyor —
   duruyor ve neden durduğunu söylüyor.
2. **Bir gösterge.** Composer'ın ayağında dolan turuncu bir daire. Doluluk = son cevabın gönderdiği
   token ÷ tavan.

Tavan **50.000**. Gerekçe kapasite değil kalite: pencere 256k, yani tavan onun beşte biri.

## Hangi sayı

Bir turun büyüklüğü ancak cevap dönünce öğreniliyor, o yüzden ölçü **bir tur eski** — tavana çarpan
istek aslında bir önceki isteğin boyuyla durduruluyor. 50k'lık bir tavanda bu fark önemsiz; bir
turun kendisi tavanı aşacak kadar büyük değil.

Okunan şey **son cevabın** `usage.sent`'i. Sondan geriye yürüyor, çünkü kayıt her zaman bir cevapla
bitmiyor: cevabı gelmemiş bir soru sonda durabiliyor, ve o sorunun bir sayısı yok.

Hiç cevap dönmemişse sayı sıfır. Ölçülmemiş eski bir cevap da sıfır — sıfır, "bilinmiyor"un
göründüğü şey, ve 76 bu kararı zaten vermiş.

## Kural nerede duruyor

Alanda. `chat.py`'de, `is_owed_an_answer`'ın yanında: tavanın kendisi bir sabit, ve iki soru —
*bu sohbet ne kadar gönderdi* ve *doldu mu*. Uç yalnız soruyor ve cevabı bir duruma çeviriyor,
88'de `is_owed_an_answer` için yaptığının aynısı.

Kapı tek olduğu için **iki yol da** aynı kuralla duruyor: cümle gönderen de, tekrar deneyen de.
Dolmuş bir sohbette tekrar denemek aynı büyük isteği yeniden atmak demek.

Durdurma yazmadan önce oluyor. Reddedilen bir cümle diske hiç inmiyor, yani sohbet cevabı
beklenen bir soruyla kalmıyor.

## Sayı tarayıcıya nasıl gidiyor

Kaydın içinde. `GET /chats/<id>` cevabına bir alan giriyor:

```json
"context": { "sent": 41230, "ceiling": 50000 }
```

Tavan da geliyor, çünkü daire bir oran çiziyor ve oranın paydası gerekiyor. Tarayıcıda ikinci bir
50.000 durmuyor — bir kopya, eskiyecek olan şey.

Kaydın şekli 89'dan beri tek yerde kuruluyor, ve bu alan oraya giriyor. Sohbet **listesinin**
satırlarına girmiyor: orada okuyanı yok.

## Ekranda

Composer'ın ayağının **solunda**, dolan turuncu bir daire. Ayak bugün her şeyi sağa dayıyor;
daire karşı uca geçiyor, yani ayak iki uca yaslanan bir satır oluyor.

Solda, çünkü **gösterge bir denetim değil** — okunan bir şey. Skills, model adı ve gönder düğmesi
karar 1'den beri sağda; dairenin o üçlünün arasına girmesi onu tıklanacak bir şey gibi gösterirdi.

Fare üstünde durunca oranı yazıyla söylüyor. Daire yüzdeyi çiziyor, yazı onu okunur kılıyor.

Tavanı geçmiş bir sohbette daire **tam dolu** — taşmış değil. Bir daire dolduktan sonra daha fazla
dolamaz, ve fazlayı çizmeye çalışmak yalanla sonuçlanır.

**Taslak ekranda daire yok.** Composer iki ekranda da aynı bileşen, ama henüz sohbet yokken
ölçülecek bir bağlam da yok. Boş bir daire okunacak bir şey vermiyor, yalnız hep orada duran bir
işaret veriyor. Daire ilk cevap dönünce doğuyor.

## Özetleme yok

*Şimdilik.* Özet, konuşmayı sürdürmenin yolu ama kendi başına bir iş; bu madde yalnız tavanı ve
durmayı getiriyor. Özetlemeyi getirmek isteyen gün, v5'in 71'inin işi.

## Kırmızıya dönecek testler

**`test_chat.py` — üç**

1. Okunan sayı son **cevabın**: sonda cevabı beklenen bir soru dursa bile ondan bir önceki cevap
   okunuyor.
2. Hiç cevap dönmemiş bir sohbet hiçbir şey göndermemiş sayılıyor.
3. Dolma tavanda oluyor, tavanın yakınında değil: altında dolu değil, üstünde dolu.

**`test_chats_api.py` — üç**

4. Dolmuş bir sohbet yeni cümleyi reddediyor, ve o cümle diske hiç inmiyor.
5. Dolmuş bir sohbette tekrar denemek de reddediliyor.
6. Kayıt ne kadar gönderdiğini ve tavanın ne olduğunu söylüyor.

**`ContextGauge.test.jsx` — dört**

7. Daire son cevabın gönderdiği kadar doluyor.
8. Hiçbir şey gönderilmemişse daire çizilmiyor.
9. Tavanı geçmiş sohbette daire tam dolu, taşmış değil.
10. Fare üstünde durunca oranı yazıyla söylüyor.

**`Composer.test.jsx` — bir**

11. Daire ayağın gönder düğmesinin karşı ucunda duruyor.

**`ChatScreen.test.jsx` — bir**

12. Sohbet ekranı daireyi okuduğu kayıttan çiziyor.

**`ProjectScreen.test.jsx` — bir**

13. Taslak ekranda daire yok.

**`workspace.css.test.js` — bir**

14. Ayak iki uca yaslanan bir satır.

Toplam **on dört kırmızı.**

## Dokunulmayan

| Ne | Neden |
|---|---|
| Cevabın altındaki sayı | 76'nın işi, yerinde — daire onu yeniden ölçmüyor, aynı sayıyı okuyor |
| `stream_answer` | Tavan kapıda duruyor, tur hiç başlamıyor |
| Sohbet listesi | `context` orada okunmuyor |
| Özetleme | Bu maddenin işi değil |
| Composer'ın taslak hâli | Daire yok, ayak sağa dayalı kalıyor |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` bu turda derlenmiyor — uygulama turunda derlenip aynı commit'e giriyor, çünkü ön yüz
değişiyor.
