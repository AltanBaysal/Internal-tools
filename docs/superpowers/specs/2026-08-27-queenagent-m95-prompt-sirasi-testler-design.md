# Madde 95 — Promptun sırası düzelir, kişi sayısı yerine oturur · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 95 ·
**Kararları:** [karar defteri](../research/2026-08-27-queenagent-skill-kararlari.md) K1–K8, K25–K27 ·
**Şartı yok** — bloğun ilk maddesi, ve 96 ile 98 bunun üstüne biniyor
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

Bir kare bugün şu sırayla kuruluyor:

```
quality, HER KARAKTER + kıyafetleri, mekân, action, camera
```

İki dert bu tek satırda duruyor.

**Birincisi sıra.** İki karakterli bir karede iki tarif yan yana geliyor, ve görüntü modeli ikisini
ayırt edemiyor — birinin saçı ötekinin üstüne geçiyor. Kullanıcı bunu elle deneyip aralarını açmanın
işe yaradığını gördü *(27 Ağustos)*.

**İkincisi sayı.** Kişi sayısı karakterin kendi tanımında taşınıyor — `aylin` haritada
`"1girl, long teal hair"` diye duruyor. Aynı karakter tek başınayken de bir kişilik sayıyı söylüyor,
biriyle beraberken de; iki karakterli bir kareye iki ayrı sayı etiketi gidiyor ve hiçbiri "iki kişi"
demiyor.

## Ne olur

Sıra ikiye bölünüyor, ve arayı mekân ile kamera dolduruyor:

```
quality, people, ANA KARAKTER + kıyafetleri, mekân, action, camera, KALANLAR + kıyafetleri
```

## Ana karakter kim

Karenin karakter haritasında **en öne yazılan** isim *(K1)*. Şemaya ayrı bir alan girmiyor: sıra
zaten bilgi taşıyor, ve ikinci bir alan aynı şeyi iki kere söylerdi.

Her karede ayrı belirleniyor *(K2)* — aynı iki kişi bir karede önde, ötekinde arkada olabilir.

## Kişi sayısı nereden geliyor

Karenin kendi `people` alanından. **Model yazar, kod yerleştirir** *(K7)* — kalite etiketlerinden
hemen sonra, promptun en başına.

Kod sayamaz *(K8)*: kareye kimin girdiğini biliyor ama ne olduklarını bilmiyor. Şemada cinsiyet alanı
yok ve bilerek açılmıyor.

`people` her karede zorunlu, tek karakterli karede bile *(K25)* — ama bu bir **metin** kuralı, kodun
zorlayacağı bir şey değil: alanı olmayan bir kare hâlâ kuruluyor.

**Açık soru burada kapanıyor.** Şema `people` dışında hiçbir şey almıyor: ana karakter için alan yok
*(K1)*, cinsiyet için alan yok *(K8)*, geri kalan her şey bugünkü hâliyle duruyor.

## Diskte duran dosyalara ne oluyor

Hiçbir şey *(K26)*. `people` taşımayan bir kare bugünkü gibi çıkıyor — kod eksik alanı atlıyor,
`quality` yokken yaptığı gibi. Karakter tanımının içinde kalmış `1girl` ya da `solo` etiketi de
silinmiyor: onu yakalayan şey kural kitabının altıncı maddesi *(K27)*, kod değil. Kod ayıklasaydı
bilerek yazılmış bir etiketi de sessizce silerdi.

## Kıyafet sahibinden ayrılmıyor

Blok bozulmuyor *(K4)*: ana karakterin kıyafetleri onunla birlikte başta, kalanlarınki onlarla
birlikte sonda. Bir görüntü modeline kimin kıyafetinin kime ait olduğunu söyleyen tek şey ikisinin
komşu durması, ve bu kural sıranın iki yakasında da geçerli.

## Bilerek kabul edilen

Üç kişilik bir karede ikinci ve üçüncü sonda yan yana kalıyor, yani aralarındaki karışma riski
sürüyor *(K5)*. Korunması gereken ana karakter; ötekiler arasındaki bulaşma kabul edildi.

## Kırmızıya dönecek testler

Hepsi `test_build_prompts.py`'de.

1. `people` kalite etiketlerinden hemen sonra, ana karakterden önce yazılıyor.
2. `people` alanı olmayan bir kare kurulmaya devam ediyor, ve sıra yine bölünüyor — eski dosyalar
   sayısız ama doğru çıkıyor.
3. Kimin başı çektiği **her karede ayrı** belirleniyor: aynı iki kişi bir karede önde, ötekinde
   arkada *(K2)*.
4. İki karakterli karede ilk yazılan başta, ikincisi kameradan **sonra** duruyor.
5. Ana karakterin kıyafeti onunla birlikte mekândan önce, ikinci kişi ise kameradan sonra — tek bir
   zincirde.
6. Sondaki karakterin kıyafeti onunla birlikte, kameranın ötesinde duruyor.
7. Üç karakterde ikinci ve üçüncü sonda, yazıldıkları sırayla yan yana *(K5)*.
8. Eski düz liste biçiminde de ilk isim ana karakter sayılıyor.
9. Karakteri olmayan bir kare `people`'ı yine de yazıyor.

**Dokuz kırmızı.** Yanlarına bir tane de **bugün yeşil olan bekçi** giriyor: boş bir `people` hiçbir
şey eklemiyor. Bugün yeşil, çünkü alan zaten hiç okunmuyor; yarın da yeşil kalması gereken şey ise
yeni kodun `", ,"` bırakmaması. Bir turu kırmızıya döndürmüyor ama koruduğu şey gerçek, ve iddiası
iki dünyada da aynı.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Var olan yirmi sekiz test | Hiçbiri yeniden yazılmıyor — üçü yeni sırayla da doğru kalıyor, gerisi sıranın dışında |
| Kıyafetin kendi iç sırası | İki kıyafet yazıldıkları sırada duruyor; bu madde ona dokunmuyor |
| Eksik ad hatası | Bilinmeyen karakter, kıyafet ve mekân aynı cümlelerle reddedilmeye devam ediyor |
| `shots` yedeği | Eski dosyalar listelerini oradan okumaya devam ediyor |
| Yazılan Python dosyası | Biçimi, tırnakları, adı — hepsi yerinde |
| Karakter tanımındaki `solo` | Kural kitabının işi *(K27)*, kodun değil; bugünkü test aynen kalıyor |
| `skills.py` metni | Şema ile kural kitabı **Madde 96**'nın işi |

**Üç test yeni sırayla da geçiyor ve kalıyor:** sabit sıra testi *(tek karakterli kare, sırası
değişmiyor)*, iki karakterin kendi sırasını koruması *(ilk yazılan hâlâ önde)*, ve karakter bloğunun
bütün kalması *(ikisi de kendi kıyafetinin yanında)*. Üçü de yeni davranışı **tarif etmiyor** — onu
tarif eden yukarıdaki on test.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi — defter bu dalı gösterdiği için
kırmızılar, ve koşunun sonunda `main`'e çevrilecekler.

Ön yüz değişmiyor, yani bu maddede `dist` derlenmiyor.
