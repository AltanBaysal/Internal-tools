# v11 Görev 5 — kare köşeleri yeniden dağıtılır: TEST döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 1/2 (testler)

Bu spec **yalnız testleri** tanımlıyor. Kod bu döngüde değişmiyor.

## Hangi yerleşim sınanıyor

Kullanıcı kararı (2026-08-13): durum yazısı sol üste, ✓ seçim halkası sağ üste, ve halka
belirdiğinde sıra numarası kaybolsun.

| Köşe | Bugün | Bundan sonra |
|---|---|---|
| sol üst | ✓ halkası | **durum yazısı** ("foto bekliyor") |
| sağ üst | sıra numarası | **✓ halkası**; numara halka görünürken gizli |
| sol alt | durum yazısı | boş |
| sağ alt | sahiplik rozetleri | sahiplik rozetleri (değişmiyor) |

Yazının sol üste geçmesi tasarımın kendi kararıydı (madde 57) ve kod onu bir sebeple terk etmişti:
halka o köşedeydi ve fare gelince beliriyordu, dolayısıyla yazı yer değiştirmek zorunda kalıyordu.
Halkayı karşı köşeye almak o sebebi ortadan kaldırıyor — ve numaranın gizlenmesi, aynı sorunun sağ
üstte tekrarlanmasını önlüyor.

**Hiçbir şeyin fare gelince yer değiştirmemesi** bu görevin asıl ölçütü. Bir şeyin görünüp
kaybolması yer değiştirmek değil: numara gidince yazı ya da halka kımıldamıyor, çünkü ikisi de kendi
köşesine yapışık.

## Vakalar

| # | Vaka | Beklenen |
|---|---|---|
| J1 | Bekleyen karenin durum yazısı | Sol üstte (`top: 6px`, `left: 6px`), altta değil |
| J2 | ✓ seçim halkası | Sağ üstte (`top: 6px`, `right: 6px`), solda değil |
| J3 | Sıra numarası | Sağ üstte kalıyor, ve gizlenebilmesi için kendi sınıfını taşıyor |
| J4 | Stil sayfası | Halkayı gösterdiği her durumda numarayı gizliyor |
| J5 | Seçim modu açıkken durum yazısı | Yine sol üstte — mod açılınca kımıldamıyor |

J5 "hiçbir şey oynamıyor" ölçütünün sınanabilir hâli: yazıyı iki farklı durumda aynı yerde bulmak,
"fare gelince yerinden oynamaz" cümlesinin test edilebilir yarısı.

## Testin dürüst sınırı

Numaranın gizlenmesi ve halkanın belirmesi CSS'te; jsdom stil sayfasını uygulamıyor. J1, J2, J3 ve
J5 satır içi konumları okuyor — onlar gerçek. J4 ise **stil dosyasının metnini** okuyor: kuralın
silinmesini yakalar, kuralın doğru çalıştığını kanıtlamaz.

Bu, defterin metnini okuyan testlerle aynı türden bir güvence ve aynı sınırla söyleniyor. Alternatifi
— numarayı JavaScript'le gizlemek — bir yarısını test edilebilir yapardı ama ikizini (fare hâli) CSS'te
bırakır, yani tek davranış iki mekanizmaya bölünürdü. Halkanın kendisi zaten iki durumu da CSS'te
çözüyor; numara onun aynadaki görüntüsü olarak aynı yerde duruyor.

## Kapsam dışı

- Halkanın ne zaman **var olduğu** — Görev 4'te kapandı. Bu görev nerede durduğunu konuşuyor.
- Sahiplik rozetleri, kartın ortası, sürükleme.

## Kırmızı commit

Beş test; hepsi düşer. Mevcut *"keeps the pill in a corner of its own"* testi J1 ve J5'e dönüşüyor —
adı ve gerekçesi de değişiyor, çünkü eski gerekçe ("halka sol üstü sahipleniyor") artık doğru değil.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` beş düşen test gösteriyor; dördü konum, biri eksik CSS
kuralı. Hiçbiri bulunamayan elemandan düşmüyor — J3'ün seçicisi hariç, ki onun bulunamaması zaten
sınanan şeyin ta kendisi.
