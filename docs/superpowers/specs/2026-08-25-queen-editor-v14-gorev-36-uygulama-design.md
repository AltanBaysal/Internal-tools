# v14 Görev 36 — Fotoğraf inerken karonun bekleme hâli: UYGULAMA döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Kullanıcı, 25 Ağustos
**Öncesi:** [Görev 36 test spec'i](2026-08-25-queen-editor-v14-gorev-36-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 36

## Ne yeşile döndürülüyor

İki kırmızı test: yer tutucu, çağıran ne şekil isterse istesin halkasını ortalıyor; ve bekleyen karo
sakin bir zeminde bekliyor. Yanlarındaki tutucu yeşil kalmalı: hiç gelmeyen fotoğrafın sessiz kutusu
çizgisini koruyor.

## Değişikliğin şekli

Tek bileşen: `frame_status.jsx`'in `Rendering`'i. Bugün çağıranın style'ını olduğu gibi alıyor ve
`display: block` gelirse kendi ortalamasını kaybediyor.

Yarın **çağıranın style'ı önce, kendi yerleşimi sonra** yazılıyor. Ölçü, en boy oranı, kenarlık —
hepsi çağıranın kalıyor; ortalama artık çağıranın elinden alınmış oluyor.

## Neden bileşen kendi ortalamasının sahibi

Bugünkü hatanın sebebi tek bir çağıranın yanlış bir değer geçirmesi değil. Galeri karoya doğru
style'ı veriyor: `display: block` bir `<img>` için doğru. Yanlış olan, o style'ın resim olmayan bir
şeye de verilmesi.

İki çare var. Çağıranı düzeltmek — `TileImage` yer tutucuya style'ın yalnız şekil kısmını versin.
Ya da bileşeni düzeltmek — `Rendering` kendi ortalamasını kimseye bıraktırmasın.

**İkincisi seçiliyor.** Birincisi bugünkü tek bozuk yolu kapatır ama `Rendering`'in üç çağıranı var
ve dördüncüsü aynı tuzağa yeniden düşebilir; üstelik `TileImage`'ın style'ı hangi parçalara ayırıp
hangisini geçireceğine karar vermesi, resmin biçimini iki yerde bilmek demek olurdu. Ortalayan bir
şeyin ortalamasına kendisinin sahip olması, tek satırla söylenen ve bir daha bozulmayan kural.

## Çizgi beklemeden kalkıyor

`wf-img--loading` sınıfı gidiyor ve `backgroundImage: "none"` geliyor — sınıf çıkınca `.wf-img`'in
kendi gri çizgisi ortaya çıkardı, o da kapatılıyor. Aynı yol hata karosunda zaten kullanılıyor
(`Gallery.jsx`), yani kalıp deponun kendisinden.

Sonuç: **çizgi = piksel yok** (kuyrukta, hata, gelmedi), **halka = geliyor**. Bugün ikisi bir arada
duruyor ve aralarındaki farkı tek başına halka taşıyor.

## Halkanın `zIndex`'i düşüyor

Halka bugün `position: relative, zIndex: 1` taşıyor. Bu, kaldırılan `wf-img--loading`'in kendi
`position: relative; overflow: hidden` kuralının yanında anlamlıydı. O sınıf gidince halkanın
üstünde duracağı bir şey kalmıyor: `Rendering`'in tek çocuğu o, ve kutuda çapraz çizgi öğesi
(`.wf-img-x`) yok. Kalması, olmayan bir katmana karşı alınmış bir önlem gibi okunurdu.

## Yorum düzeltiliyor

`Rendering`'in başındaki açıklama bugün "aynı sınıflar, aynı halka, kelimesiz" diyor. Sınıflardan
biri gidince o cümle yanlış olur. Kod ile çakışan yorum koda uydurulur (CLAUDE.md).

## Diğer iki çağıran

`PhotoDetail` ve galerinin üretiliyor karosu bugün doğru çiziliyor, çünkü ikisi de `display`
taşımayan bir style veriyor. Değişiklikten sonra da doğru çiziliyorlar: çağıranın style'ı önce
yazıldığı için `PhotoDetail`'in `flexDirection: column` ve `gap`'i yerinde kalıyor. İkisi de
çizgisini kaybediyor, ve bu istenen — aynı bekleme, aynı hâl.

## Kapsam dışı

- **Test dosyası değişmiyor.** Bir önceki commit'te ne yazıldıysa o kalır.
- **`vendor/styles.css`.** Elle düzenlenmiyor. `.wf-spinner` kusursuz; onu bozan, içine konduğu
  kutuydu.
- **`TileImage` ve `Gallery`.** Hiç açılmıyorlar.
- **Halkaya ayrıca `display` verilmesi.** Ortalayan kutu geri geldiğinde halka zaten blok
  seviyesinde bir flex öğesi oluyor; ikinci bir çare, ilkinin çalıştığını gizlerdi.

## Derlenmiş çıktı

Ön yüz kaynağı değiştiği için `dist` aynı commit'e girer (CLAUDE.md). Defter derlemiyor; itilmemiş
bir `dist` Colab'da görünmez.
