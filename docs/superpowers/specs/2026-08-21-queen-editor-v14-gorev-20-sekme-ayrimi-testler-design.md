# v14 · Görev 20 — Sekmelerin ayrılması · **test turu**

**Kaynak:** yol haritası 20. madde · İstek 4.2 · tasarım v4 fark listesi 85 · 32. karar.

> *"Bugün bitişikler, tek bir parça gibi duruyorlar. Aralarına boşluk girecek."*
> **Tasarımda çözülecek:** *"ayrılınca hangi sekmenin açık olduğu yalnız renkten anlaşılacak; buna
> bir kez daha bakmak gerekir."*

## Bugün ne oluyor

Sahnenin üstündeki üç düğme uç uca duruyor. Onları birleştiren tek şey ikinci ve üçüncü düğmenin
`marginLeft: -1` değeri: her düğmenin kendi çizgisi var, ve bu değer komşunun çizgisini kendi
çizgisinin üstüne çekiyor. Kodun yanındaki yorum niyeti açıkça yazıyor — *"üç ayrı hap değil: üç
durumu olan tek denetim."*

O niyet geri alındı. **Bitişik sekme kararı** fark listesinin geri alma kuralında adı geçen ölü
kararlardan biri (belgenin 30–35. satırları): denenmiş, vazgeçilmiş, yalnız son hâli geçerli.

Köşe yarıçapı zaten her düğmenin kendisinde — `wf-stroke` sınıfı veriyor ve kimse almadı. Yarıçapı
görünmez yapan şey çakışma: iki yuvarlak köşe bir pikselde üst üste binince ortada yarıçap değil bir
kısılma okunuyor.

## Verilen kararlar

### 1 · Araya 8 piksel giriyor *(fark 85)*

Ölçü tasarımın verdiği ölçü. Şeridin kendisi `flex`; boşluk şeridin `gap`'i, düğmelerin marjı değil
— üç düğme arasında iki boşluk var ve bir marj bunu ikisine değil üçüne yazardı.

### 2 · Yarıçap ayrıca eklenmiyor

*"Her biri kendi köşe yarıçapını alır"* cümlesinin karşılığı yeni bir yarıçap değil, çakışmanın
kalkması. Yarıçap yerinde duruyor; testin ölçtüğü şey **hiçbir sekmenin komşusunun üstüne
çekilmemesi**.

### 3 · Açık sekmenin çizgisi vurgu rengini korur *(32. karar)*

Tasarım *"açık sekme yalnız rengiyle belli olur, ek işaret yoktur"* diyor. Bugün açık sekmede iki
şey vurgu rengine dönüyor: yazı ve çerçeve. İkisi de renk.

**İşaret** tasarımın sözlüğünde *eklenen* bir şey — alt çizgi, nokta, ok, üçgen. Her sekmenin zaten
sahip olduğu çerçevenin açık sekmede vurgu rengini alması, sekmenin renklenmesidir. Bitişikken o
çerçeve yapısal iş de görüyordu (sürekli bir şeridin içinde açık parçayı kutuluyordu); ayrılınca o
işi bırakıyor ama rengi bırakmıyor.

Yani bu madde açık sekmenin görünüşünde hiçbir şey değiştirmiyor. Değişen yalnız geometri.

## Kapsam dışı

- **Şeridin ve sahnenin üst boşluğu** (fark 103) 22. madde.
- **Kuyruktaki kopya karede şeridin davranışı** (fark 112) 22. madde.
- **Sekmelerdeki ikonlar** — tasarım hiç söz etmiyor, bulgu da değil (Yol 1'in notu).
- Sekmelerin ne gösterdiği 19. maddede kapandı.

## Yazılacak testler

### `PhotoDetail.test.jsx` — 3 yeni test, "the layer tabs" bloğuna

| # | Ne diyor | Kırmızı mı | Fark |
|---|---|---|---|
| 1 | Üç sekmenin arasında 8 piksel var | **kırmızı** — bugün şeridin `gap`'i yok | 85 |
| 2 | Hiçbir sekme komşusunun üstüne çekilmiyor | **kırmızı** — ikinci ve üçüncü `-1px` taşıyor | 85 |
| 3 | Açık sekme rengiyle belli oluyor, üstüne bir şey eklenmiyor | **doğuştan yeşil** | 85 · karar 32 |

**Üçüncü test neden yazılıyor.** Maddenin "bitti sayılır" cümlesinin ikinci yarısı *"açık olan
renginden ayırt ediliyor"* ve bugün bunun hiçbir testi yok — bloğun tek ölçtüğü `aria-current`.
Test doğuştan yeşil, çünkü bu maddede kapanan tasarım kararı bir şeyi **yasaklıyor**: sekmeler
ayrılınca hangisinin açık olduğunu söylemek için bir işaret eklemek. Eklenmedi, ve testin işi
eklenmemesini korumak.

Yeşil olduğu için ölçüsü zayıflatılmıyor: kapalıdan açığa geçişi baştan sona izliyor — sekme kapalı
iken rengi ve içeriği, tıklandıktan sonra rengi değişmiş, içeriği değişmemiş.

### Şeride bir tutamak geliyor

Boşluk şeridin kendi ölçüsü, düğmelerinki değil; testin şeridi adıyla bulması gerekiyor. Evin
alışkanlığı bir `data-*` işareti (`data-corner`, `data-field`, `data-owns` aynı sebeple var), ve
şerit onu **uygulama turunda** alıyor — testler kırmızıyken tutamak henüz yok, kırmızılığın sebebi
de bu.

**Toplam 3 yeni test: 481 → 484. İkisi kırmızı.**

## Bitti sayılır

Dört komut da koşuyor; queen-editor frontend'de **2 kırmızı** duruyor. Testler kırmızı commit
ediliyor.
