# Madde 90 — Durdurma tek yoldan iner ve bağlantıyı keser · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Test turu:** [testler tasarımı](2026-08-27-queenagent-m90-durdurma-baglantiyi-keser-testler-design.md) · kırmızı commit `ef57801`
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder. Yeni test yazılmaz.

---

## Dört dosya, dört ayrı iş

Zincir yukarıdan aşağı: durdurma ucu kayda söyler, kayıt bağlantıyı keser, kesilen bağlantı cevabı
bitirir, cevap kaydı okuyup kesenin biz olduğunu anlar.

| Dosya | Ne öğrenir |
|---|---|
| `services/xai/client.py` | Cevabı açar açmaz kesme yolunu teslim etmeyi, ve sokete inmeyi |
| `data/xai_engine.py` | Onu yutmadan aşağı geçirmeyi |
| `data/memory_stops.py` | Not yerine bağlantıyı tutmayı |
| `domain/usecases/stream_answer.py` | Bayrağı kare başına değil tur başına sormayı |

`ports.py` iki protokolün sözünü güncelliyor; `routes.py` ve ön yüz açılmıyor.

## İstemci — kesmek

`stream` bir parametre alıyor: `on_open`. Cevap açılır açılmaz, **daha tek satır okunmadan**,
elindeki kesme yolunu ona veriyor. Sıra önemli: bu maddenin varlık sebebi ilk kelimeden önceki
bekleme, ve kesme yolu o beklemenin içinde lazım.

Kesme `response.close()` değil — gerekçe test turunun tasarımında: kapatmak tamponun kilidini
bekler, ve o kilit tam da kesilmek istenen okumanın elindedir. Kesme tamponu atlayıp sokete iniyor.

**Sokette ne yapacağı ölçülerek bulundu, tahmin edilerek değil** *(27 Ağustos)*. Test turunun
tasarımı `shutdown` diyordu; ölçüm iki yolun iki farklı çağrıyla uyandığını gösterdi:

| Platform | `shutdown` | Handle'ın gerçekten kapanması |
|---|---|---|
| Windows — yerel yol | uyandırmıyor | uyandırıyor: `ConnectionAbortedError` |
| Linux — Colab yolu | uyandırıyor | tek başına güvenilir değil |

Kesme ikisini de yapıyor: önce `shutdown`, sonra handle'ı gerçekten kapatmak. İkincisi `detach`
üzerinden, çünkü soketin kendi `close`'u hiçbir şey kapatmıyor — cevabın okuduğu dosya soketin
üstünde bir sayaç tutuyor ve handle çağrıdan sağ çıkıyor.

Sokete inen yol `response.fp.raw._sock`. CPython'ın iç isimleri; zincirin herhangi bir halkası
yoksa kesme sessizce vazgeçiyor, ve soket zaten ölmüşse `OSError` yutuluyor — cevabın kendi
kendine bitmesiyle durdurmaya basılması arasındaki yarış gerçek bir yarış.

Kesilen okumanın **iki şekilde** geri geldiği de buradan çıkıyor: yarım kalmış gövde, ve altından
handle'ı çekilmiş okuma. İkisi de `XaiFailed` oluyor.

İki yeni hata dalı, yukarıdaki iki şekil için: `IncompleteRead` ve `OSError`. İkisi de `urllib`'in
hata ailesinden değil, ve istemcinin sözleşmesi tek: dışarı `XaiFailed` çıkar. Mesajı Python'ın
kendi sözleri — kimin kestiği bu katmanın bilgisi değil, ve bilmediği bir şeyi uydurmuyor.

## Kayıt — tutulan şey bağlantı

`MemoryStops` iki sözlük değil, iki şey tutuyor: kimin durdurulması istendiği *(bugünkü küme)* ve
her koşan cevabın kesme yolu. Yeni söz `hold`.

Sıra ikisi arasında serbest, ve iki sıra da aynı yere varıyor:

- **Önce `hold`, sonra `want`** — olağan hâl. `want` kesme yolunu bulur ve keser.
- **Önce `want`, sonra `hold`** — bağlantı açılmadan basılan durdurma. `hold` kendisi için bir
  istek beklediğini görür ve bağlantıyı doğduğu anda keser.

`clear` ikisini birden unutuyor. Unutmazsa turdan sonra gelen bir durdurma çoktan başkasının olmuş
bir soket numarasına iniyor.

Kesme çağrısı kilidin **içinde** yapılıyor. `shutdown` tek bir sistem çağrısı, ve okuyan thread
bloke olduğu sürece bu kilide hiç dokunmuyor — yani beklemeye kimse girmiyor. Dışarıda yapılsaydı
`clear` ile `want` arasına girip ölmüş bir sokete inebilirdi.

## Cevap turu — tek soru

Bayrağı **her karede** sormak düşüyor. Kesilen bağlantı turu kendi bitiriyor; geriye tek soru
kalıyor: *bu turu bitiren biz miydik.*

O soru iki yerde soruluyor, çünkü kesilen bir tur iki şekilde geri gelebiliyor:

1. **Hatayla.** Motorun akışı `IncompleteRead`'den doğmuş bir `XaiFailed` atıyor. Kaydı sormadan
   önce hiçbir şeye inanılmıyor: kesen bizsek bu bir durdurma, değilsek arıza ve `EngineFailed`.
2. **Sessizce.** Tur düzgün bitmiş ama durdurma tam o sırada gelmiş. Turun sonunda bir kere
   soruluyor.

Bunun için akış döngüsünün etrafına ikinci bir `try` giriyor. İçteki `except` kararı veriyor; kesen
biz değilsek olduğu gibi yukarı bırakıyor, ve dıştaki mevcut `except` onu her zamanki gibi
`EngineFailed`'e çeviriyor. İki `try`'ın işi ayrı: içteki bağlantıya bakıyor, dıştaki turun geri
kalanına — araç koşturmak da dahil.

Harcamanın toplanması içteki `except`'ten **sonra** duruyor. Hatayla biten bir turun ölçülmüş
sayısı da gerçekten harcanmıştı, ve orayı atlayan bir düzen onu çöpe atardı.

Araç koşarken açık bağlantı yok. O sırada basılan durdurma kesecek bir şey bulamıyor ama notunu
düşüyor, ve bir sonraki turun `hold`'u bağlantıyı doğduğu anda kesiyor.

## Ne değişmiyor

`/stop` ucunun adresi, 404'ü ve boş cevabı. `stopped` işaretinin diske yazılması. Kelimeden önce
durdurulan turun boş kayıt bırakması. Düğmenin iki hâli, ekrandaki **Stopped**. `complete` yolu —
akışı yok, kesilecek bağlantısı yok.

**Ön yüz hiç açılmıyor**, ve `dist` derlenmiyor.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

`ef57801`'in on beş kırmızısı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un
ikisi.

Yeşilin kendisinden daha çok şey söyleyen bir test var: `test_a_cut_wakes_a_read_that_is_blocked_on_the_socket`.
Gerçek bir soket, gerçek bir bloke okuma. Yeşile döndüğünde kanıtlanan şey maddenin tamamı —
durdurma gerçekten xAI'ye iniyor.
