# Madde 90 — Durdurma tek yoldan iner ve bağlantıyı keser · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 90 ·
**Üstüne geldiği:** [Madde 89](2026-08-27-queenagent-m89-sohbetin-sekli-tek-yerde-uygulama-design.md)
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

Durdurma iki yarımdan oluşuyor ve ikisi de eksik.

Birincisi bir bayrak. `stream_answer` onu xAI'den **her kare geldiğinde** soruyor. Kare gelmiyorsa
kimse sormuyor — ve düşünen bir modelde ilk kare dakikalar sonra gelir. O dakikalar boyunca
durdurmaya basmak hiçbir şey yapmıyor: düğme hâlini değiştiriyor, cevap koşmaya devam ediyor, xAI
üretmeye ve faturalamaya devam ediyor.

İkincisi bağlantının kapanması. Bu kimsenin verdiği bir karar değil — döngüden çıkınca `with`
blokunun kapanmasının yan etkisi.

## Ne olur

**Tek iptal:** durdurma isteği, koşan cevabın xAI'ye açık duran bağlantısını doğrudan keser. Okuma
nerede blokeliyse orada uyanır — ilk kelime beklenirken de — ve üretim ile fatura o anda durur.

## Kesmek neden `close()` değil

Cevabı koşturan thread işletim sistemi seviyesinde bir okumada bloke duruyor. `response.close()` onu
uyandırmaz: tamponlu okuyucunun kilidi zaten o thread'in elinde, ve kapatmaya çalışan thread tam da
kesmek istediği okumayı beklemeye başlar. İki thread birbirini kilitler.

Uyandıran çağrı `socket.shutdown()`. Tampona hiç uğramaz, doğrudan sokete iner, ve bloke okuma
akışın bittiği bilgisiyle geri döner.

`urllib` soketi dışarı vermiyor, o yüzden istemci ona kendi iniyor: `response.fp.raw._sock`.
CPython'ın iç isimleri — söz verilmemiş bir yol *(kullanıcı kararı, 27 Ağustos)*. Zincirin herhangi
bir halkası yoksa kesme sessizce vazgeçer, ve testlerdeki sahte cevaplarda tam olarak öyle olur.

## Kesilen bağlantı hata olarak geri gelir

xAI akışı `chunked` gelir. Bir chunk'ın ortasında sokete `shutdown` çekilince `http.client` yarım
kalmış gövdeyi `IncompleteRead` diye bildirir — yani **bizim kestiğimiz bağlantı da bir hata olarak
döner.** İstemci onu kendi diliyle `XaiFailed`'e çevirir, ve Python'ın söylediğini yazar: sebep
uydurulmaz.

Bu maddenin en dikkat isteyen ayrımı burada: **bizim kestiğimiz bağlantının hatası bir durdurmadır,
ağın kendisi koptuğunda aynı hata bir arızadır.** Hatanın kendisinde ikisini ayıran hiçbir bilgi
yok. Ayıran tek şey kayıt: kesen biz miyiz, değil miyiz.

## Kayıt neyi tutar

Bugün tuttuğu şey bir not: *"istendi"*. Bundan sonra tuttuğu şey **bağlantının kendisi** — daha
doğrusu onu kesen çağrı. Yaşam kuralı aynen devralınıyor: bellekte, kilitli, cevapla birlikte doğup
ölüyor, diske hiç inmiyor.

Dört söz veriyor:

| Söz | Ne yapar |
|---|---|
| `hold(p, c, cut)` | Koşan cevap kendini kesmenin yolunu bırakır. Durdurma bu andan **önce** istenmişse hemen keser |
| `want(p, c)` | Durdurma ucu. Not düşer, ve kesecek bir şey varsa o anda keser |
| `wanted(p, c)` | Kesen biz miyiz. Durdurmayı arızadan ayıran tek bilgi |
| `clear(p, c)` | Notu da, kesme yolunu da unutur |

`hold` ile `want`'ın sırası önceden bilinemez: bağlantı açılmadan basılan durdurma gerçek bir durum,
çünkü ilk kelimeyi beklerken basmak bu maddenin varlık sebebi. İki sıra da aynı sonucu verir.

## Cevap turunda ne değişir

Bayrağı **her karede** sormak düşüyor. Kesilen bağlantı turu kendi bitiriyor; geriye tek bir soru
kalıyor: tur bittiğinde *kesen biz miydik*. O soru turun sonunda bir kere soruluyor — hem düzgün
biten turda, hem hatayla biten turda.

Araç koşarken açık bir bağlantı yok. O sırada basılan durdurma kesecek bir şey bulamaz, ama notu
düşer; bir sonraki tur bağlantıyı açıp `hold` dediğinde o not bağlantıyı doğduğu anda keser.

## Değişmeyen

Durdurulan turun diske `stopped` işaretiyle yazılması, kelimeden önce durdurulan turun boş kayıt
bırakması, `/stop` ucunun adresi ve cevabı, düğmenin iki hâli, ekranda **Stopped** yazması. 67, 79,
80 ve 81'in tamamı yerinde.

**Ön yüzde hiçbir şey değişmiyor** — ekran durdurulmuş turu zaten kayıttan çiziyor. Bu tur da,
uygulama turu da yalnız arka uca dokunuyor, ve `dist` derlenmiyor.

## Kırmızıya dönecek testler

**`test_xai_client.py` — dört**

1. Cevap açılır açılmaz, daha tek satır okunmadan, akış kesme yolunu teslim eder.
2. Soket saklamayan bir cevabı kesmek sessizdir — testlerdeki her sahte cevap böyle.
3. **Gerçek soketle:** susan bir sunucuya bağlanıp bloke kalan okuma, kesildiğinde uyanır. Sahtelenemeyecek
   tek şey bu — kesme gerçekten sokete iniyor mu. Kesme işlemezse test asılı kalmaz, süre dolar ve düşer.
4. Aynı sunucuda: o okuma `XaiFailed` olarak geri gelir, ve mesajı Python'ın kendi sözleridir.

**`test_stops.py` — dört**

5. Tutulan bağlantı, durdurma istendiğinde kesilir.
6. Bağlantı açılmadan istenen durdurma, bağlantı geldiği anda keser.
7. Unutulan kayıt kesmez: turdan sonra gelen bir durdurma eski soketi bulmaz.
8. Bir sohbetin bağlantısı kesilirken komşusununki durmaz.

**`test_xai_engine.py` — bir**

9. Motor kesme yolunu yutmaz, istemciye geçirir. Soketi tutan tek yer orası.

**`test_stream_answer.py` — iki**

10. Koşan cevap kendini kesmenin yolunu kayda teslim eder.
11. Kestiğimiz bağlantının hatası arıza değil durdurmadır: `EngineFailed` atılmaz, kayıt `stopped`
    yazılır.

Toplam **on bir kırmızı.**

## Ölçüsü değişen testler

`wanted` artık kare başına değil tur başına soruluyor, ve `StopsAfter` sahtesi bunu sayarak
çalışıyordu. Sahte, "kesen biz miyiz" sorusuna cevap veren `Cut`'a bırakıyor yerini, ve onu kullanan
altı test yeniden türetiliyor. **İddiaları değişmiyor** — hangi anda durdurulduğu değişmiyor, o anın
nasıl tarif edildiği değişiyor. Aralarında en çok değişen, kelimeden önce durdurulan turu sınayan
test: durdurma artık bağlantıyı kestiği için o an bir hatayla geliyor.

`NeverStops` de `hold`'u öğreniyor, ve dört API testindeki sahte motorlar `on_open`'ı.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `complete` yolu | Akış yok, kesilecek bağlantı yok |
| `/stop` ucu | Adresi, 404'ü, boş cevabı aynı |
| `MemoryStops`'un diske inmemesi | Aynı gerekçe, aynı ömür |
| Ön yüz | Durdurulmuş tur zaten kayıttan çiziliyor |
| `dist` | Ön yüz değişmiyor |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Ön yüz baştan sona yeşil kalır. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.
