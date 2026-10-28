# Madde 104 — Yeni sohbet kendi adresinde kalır · Tur 2 (uygulama) tasarımı

**Test turu:** [testler tasarımı](2026-08-28-queenagent-m104-taslak-isinlanmasi-testler-design.md) —
kırmızı `bf72a0d`'de. Kök neden orada; bu belge yalnız düzeltmeyi söylüyor.

## Düzeltme — `useChat.js`, tek yer

Yükleme etkisinin erken dönüşü **tutulanı bırakarak** döner: adreste sohbet yokken *(taslak, ya da
sohbet ekranı hiç yokken)* `chat`, `error` ve `missing` temizlenir. Böylece:

- Taslağın ilk mesajı bayat kayda eklenmek yerine kendi kaydını ayağa kaldırır
  *(`send`'in var olan `{ id: null, ... }` dalı — kod değişmiyor, artık gerçekten o dala giriyor)*.
- Doğum adresi taşıdığında ekran o ayağa kalkan kaydı gösterir: kullanıcının cümlesi + akan cevap.
- Tur sonunda Madde 89'un okuması her zamanki gibi diskteki kaydı giydirir.

Başka hiçbir şey değişmez: `born` navigasyonu *(Madde 88)*, `streamingInto` koruması, tur sonu
okuması yerinde.

## Neden bu kadar küçük

Işınlanmanın üç parçasından *(bayat kayıt · balonun ona eklenmesi · doğumun onu giydirmesi)* ilkini
kesmek üçünü birden kesiyor — balonun ekleneceği bayat kayıt kalmıyor. Akış durumunun sohbete
anahtarlanması bilerek dışarıda: o Madde 106'nın işi ve kendi testleriyle gelecek.

## Görülür hâli

Test turunun kırmızısı yeşerir; iki suite başka kırmızı vermez *(defter çifti hariç)*. `dist` aynı
commit'te derlenir — kaynak değişti.
