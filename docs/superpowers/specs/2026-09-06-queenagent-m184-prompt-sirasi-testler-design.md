# Madde 184 · test turu — karakterler önde, mekân sonda

**Kaynağı:** [yol haritası, Madde 184](../plans/2026-09-06-queenagent-v8-roadmap.md).
189 `356cdf4`'te kapandı.

---

## Ne kanıtlanacak

Bugün bir kare şöyle çıkıyor:

```
kalite, lider + kıyafetleri, mekân, action, kamera BREAK karakter 2 + kıyafetleri BREAK …
```

Yarın şöyle:

```
kalite, karakter 1 + kıyafetleri BREAK karakter 2 + kıyafetleri BREAK … BREAK action, kamera, mekân
```

Üç şey değişiyor: **karakterlerin hepsi başta ve art arda**, **action/kamera/mekân kendi bloğunda**,
ve **mekân en sonda**. Kıyafet sahibinin yanında kalıyor — görüntü modeline kıyafetin kimin olduğunu
söyleyen tek şey o komşuluk, ve bu maddenin dokunmadığı kural o.

## Neden araya girme kalkıyor

Mekânı ve action'ı iki karakterin arasına koymak, iki tarifi birbirinden uzaklaştırmak içindi. Ama
ayırmayı `BREAK` zaten yapıyor — queen-editor'ün pozitif kodlayıcısı o literal string'den bölüyor
ve her parçayı ayrı kodluyor *(Madde 138/139)*. Mesafe onun yanında zayıf ikinci bir önlem, ve
karşılığında **action'ı ikinci karakter tanıtılmadan önce** okutuyor.

## Action kendi bloğunu neden alıyor

Son karakterin bloğuna binerse **ona** bağlanır, ve iki kişilik bir eylem tek kişinin eylemi olur.
Bugün action'ın lidere bağlanmasının sebebi de bu, yalnız ters yönden. Kendi bloğunda kimseye özel
bağlanmıyor.

**Bedeli tek kişilik karede görünüyor:** artık orada da bir `BREAK` var, ve CLIP her parçayı ayrı
kodladığı için action kendi parçasında **öznesiz** kalıyor. Parçalar kodlandıktan sonra birleşiyor
ve UNet hepsini görüyor; kadroda tek kişi varsa karıştırılacak kimse de yok. Kural tek kalıyor:
*"kaç kişi varsa ona göre değişir"* diyen bir düzen, **bu kare neden farklı çıktı** sorusuna cevap
veremez. Ölçülmedi, ve kayda öyle geçiyor.

## Yol haritasının kendi çelişkisi, ve hangisi bağlayıcı

Maddenin *"Nasıl görülür"* satırı *tek kişilik bir karede `BREAK` hiç geçmez* diyordu. Hemen
altındaki kullanıcı kararı — action kendi bloğunu alır — bunun tersini gerektiriyor, ve o kararın
bedeli zaten bir alt maddede yazılıydı. Çelişen cümle taslağın önceki şeklinden kalmış; kaldırıldı,
ve yerine bu düzeltmenin kaydı geçti. Bağlayıcı olan karar.

## Testler

**Yeni — maddenin kendisi:**

| Test | Ne söylüyor |
|---|---|
| kare sabit sırada kurulur | tam metin: kalite + karakter, `BREAK`, action + kamera + mekân |
| iki karakter art arda durur | aralarına ne mekân ne action giriyor |
| action, kamera ve mekân tek blokta | üçü bir arada ve aralarında `BREAK` yok |
| mekân en sonda | prompt onunla bitiyor |
| her karakter bloğu action'dan önce | üç kişilik karede üçü de |
| tek kişilik kare **bir** `BREAK` taşır | bedelin kendisi, yazılı |
| action, kamera, mekân hiç yoksa `BREAK` yok | boş blok düşer, prompt `BREAK` ile bitmez |

**Değişen — bugünkü sırayı okuyanlar.** On dördü tam metin ya da indeks karşılaştırması yapıyor ve
hepsi bugünkü sırayı pinliyor. Adları da değişiyor: *kameranın etrafında bölünmek*, *kamerayı geçmek*
diye anlatan dört testin anlattığı şey artık yok.

**Değişmeyen, ve bilerek kontrol edilenler:** kıyafet sahibinin yanında *(`test_each_characters_block_stays_together`)*,
karakterlerin kendi aralarındaki sıra karenin yazdığı sıra, `BREAK` hiçbir virgüle değmiyor, ve
`build_character_prompts` hiç `BREAK` taşımıyor — o yol tek karakter kuruyor, ikinci blok hiç
doğmuyor.

## Kırmızı turun tuzağı, ve bu turda bir kez daha yakalandı

Bu koşuda dokuz kez görüldü: **hiçbir şey olmadığı için geçen test.** *"Action, kamera ve mekân tek
blokta"* testi bu yüzden önce **bir `BREAK` olduğunu** ölçüyor, sonra bloğun içine bakıyor.

**Onuncusu ilk koşuda çıktı.** *Hiçbir şeyin olmadığı bir karede `BREAK` yok* diye yazılmış test
yeşil geçti — çünkü bugün de yok: eski düzende ayrı bir action bloğu hiç doğmuyor, yani boş bloğun
düşmesi diye bir olay yok. Ölçtüğü şey doğru ama bugün de doğru. Test, **yalnız mekânı olan** bir
kareyle yeniden yazıldı: orada eski düzen `AYLIN, {BEDROOM}` veriyor, yenisi `AYLIN BREAK {BEDROOM}`
— ve boş bloğun düşmesi ikinci bir assertion olarak yanında duruyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` **22 kırmızı** verdi: on ikisi bugünkü sırayı
pinleyen eski testler, onu maddenin kendisi. Öteki üç takım kımıldamadı — **589 · 739 · 591.**
