# Madde 153 — Test turu tasarımı: kare kendi numarasını taşır

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** test *(kırmızı commit'lenir)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 153

---

## Ne çivileniyor

Her kare bir `frame` numarası taşıyor. **Kod basıyor, model hiç yazmıyor.**

## Neden gerekiyor

İki okuyucu için:

- **Kullanıcı** dosyayı açıp *"15. kareyi güncelle"* diyebilsin.
- **Araçlar** kareye metin alıntılamadan hitap edebilsin — 155'in promptu yazan aracı ve 158'in
  `update_frame`'i bu numarayı kullanıyor.

## Liste sırası gerçek, numara onun görünen hâli

Numara bir **damga**, bir kimlik değil. Kare eklenince ya da silinince kod **hepsini** yeniden
numaralıyor: 1, 2, 3 … boşluksuz.

Bu bilerek seçildi. Kalıcı bir kimlik olsaydı silme boşluk bırakırdı, ve model *"7 yok ama 8 var"*
hâlini yorumlamak zorunda kalırdı. Damga olunca yorumlanacak bir şey yok — numara her zaman sıradır.

**Bedeli:** kullanıcı 7'yi silince eski 8, 7 oluyor. Kabul ediliyor, çünkü dosyayı silme anında
gören de kullanıcının kendisi.

## Model onu yazamıyor, ve bunu zorlayan şey zaten var

`frame` bir parametre değil. 152'nin **kapalı küme** kuralı gereği, model onu göndermeye kalkarsa
tanınmayan alan olarak çağrının tamamı reddediliyor — ayrı bir kural yazılmıyor, var olanın sonucu.

## Ne zaman basılıyor

Kareler listesine dokunan **her yazışta**, hepsine birden. Bugün bu yalnız `add_frames`; 155 ve 157
kendi araçlarını eklerken aynı yerden geçecekler.

**Numarası olmayan eski bir dosya**, bir kare eklenene kadar numarasız duruyor. Bu bir eksiklik
değil, kapsam: hiçbir aracın dokunmadığı bir dosyayı kod kendiliğinden yeniden yazmıyor — kullanıcının
dosyası, ve dokunulmadan durması doğru olan.

## Cevap tek sayı söylüyor

Bugün: `Added a frame to scene.json; it holds 3 now.`
Bundan sonra: `Added frame 3 to scene.json.`

Numara hem **adres** hem **sayı**, çünkü boşluk yok. İki kez söylemek gürültü olurdu. İki kez
çağrılmış bir aracın görünürlüğü de duruyor: ikinci çağrı `frame 4` diyor.

## Numara başta duruyor

Kare nesnesinde `frame` ilk alan. Dosyayı açan kişi için: numarayı aramak için karenin içine bakmak
gerekmesin.

---

## Testlerin şekli

- Eklenen kare **numara taşıyor**, ve numarası listedeki sırası.
- **Var olan kareler de numaralanıyor** — numarasız bir dosyaya kare eklenince üçü birden numaralı
  oluyor.
- Numaralar **1'den başlıyor ve ardışık**.
- **İkinci ekleme ikisini de doğru numaralıyor** — damga her yazışta yeniden basılıyor, bir kez
  değil.
- Cevap **yeni karenin numarasını** söylüyor.
- Model `frame` gönderemiyor — tanınmayan alan olarak ret *(152'nin kuralı, burada sonucu
  görülüyor)*.
- `frame` kare nesnesinin **ilk** alanı.
- `build_prompts` numarayı **görmüyor** — numaralı bir kare, numarasızla aynı promptu kuruyor.

## Kırmızının şekli

Bugün hiçbir kare numara taşımıyor, ve cevap eski cümleyi kuruyor. Numara bekleyen her test düşüyor.
`frame` gönderiminin reddi **bugün de yeşil** — 152 onu zaten kapatmış durumda, ve bu testin işi
kapının 153'ten sonra da kapalı kaldığını tutmak.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```
