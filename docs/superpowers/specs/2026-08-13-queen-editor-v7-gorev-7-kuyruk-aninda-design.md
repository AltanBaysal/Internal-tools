# Görev 7 — Kuyruğa eklenen kare anında görünsün

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 3

## Sorun

Kuyruğa ekle'ye basınca panel "eklendi" diyor ama kareler ekrana düşmüyor; kullanıcı bir daha
basıyor. Sebep, ekranın **iki tur** atması: önce ekleme isteği gidiyor, cevabı yalnız kaç kare
alındığını söylüyor; sonra ekran galeriyi baştan istiyor. İkinci tur, Görev 6'da ölçülen listedir —
beş Drive dosya okuması — ve kareler ancak o dönünce görünüyor.

## Kararlar

1. **Ekleme isteği, ürettiği galeriyle cevap verir.** Sunucu kareleri plana yazdıktan hemen sonra
   galeriyi zaten hesaplayabiliyor; ekranın birazdan soracağı şeyi aynı cevaba koymak, iki turu
   bire indirir. Toplam maliyet de artmaz: eklenen okuma, kaldırılan turun ta kendisi.
2. **Kural sunucuda kalır.** Alternatif — tarayıcının eklenen kareleri kendi kurup listeye
   sokması — kare adlandırmasını, numaralandırmayı ve galerinin sırasını ikinci kez, ön yüzde
   yazmak demekti. Bunlar sunucunun kuralları
   ([FOUNDATION madde 4](../../../queen-editor/FOUNDATION.md)); ikinci kopya ilk değişiklikte
   ayrışırdı.
3. **Aynı şey katman kuyruğu için de geçerli.** Video ve ses panelindeki düğmenin adı da "Kuyruğa
   ekle"; ikisini farklı davranışa bırakmak, aynı düğmenin iki anlamı olması demekti.
4. **Cevabı taşıyan yol, ikinci isteği atmaz.** Ekran, koşuyu başlatırken galeriyi elinde
   tutuyorsa onu kullanır; tutmuyorsa (devam et, tekrar dene) eskisi gibi sorar. Aynı listeyi iki
   kez istemek, düzeltmeye çalıştığımız maliyetin kendisi.
5. **"Kaç kare eklendi" cevabı kalır.** Panel onu kullanıcıya söylüyor; galeriyi saymakla
   bulunabilirdi ama o, sunucunun verdiği bir sayıyı ön yüzde yeniden türetmek olurdu.

## Testler

Sunucu:

- Ekleme cevabı, eklenen kareleri içeren galeriyi taşır ve kaç kare alındığını da söylemeye devam
  eder.
- Katman ekleme cevabı da galeriyi taşır.
- Reddedilen bir istek (hatalı prompt, meşgul kuyruk) galeri taşımaz — hata cevabı olduğu gibi
  kalır.

Ön yüz:

- Kuyruğa ekle'den sonra kareler ekranda, ve galeri ikinci kez istenmemiş.
- Devam et gibi galeri taşımayan bir yol hâlâ galeriyi ister.

## Öz eleştiri

- *Ekleme isteği ağırlaşmıyor mu?* — Ağırlaşıyor, tam olarak kaldırdığımız isteğin ağırlığı kadar.
  Kullanıcının beklediği süre iki turdan bire iniyor; toplam iş aynı kalıyor.
- *Galeriyi cevaba koymak, uç noktanın işini karıştırmıyor mu?* — Karıştırmıyor: uç nokta hâlâ tek
  şey yapıyor, sonucunu anlatırken istemcinin bir sonraki sorusunu da cevaplıyor. İki kuralı bir
  araya getirmiyor, iki cevabı bir araya getiriyor.
- *Asıl sorun listenin pahalı olması değil mi?* — Öyle, ve o Görev 8. Bu görev, bir turu tamamen
  ortadan kaldırıyor; Görev 8 kalan turu ucuzlatacak. İkisi farklı şeyler ve ayrı ölçülebilmeleri
  gerekiyor.
