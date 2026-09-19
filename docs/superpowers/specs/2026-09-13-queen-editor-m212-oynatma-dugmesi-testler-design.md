# Madde 212 · Oynatma düğmesi — test turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Değişen bileşen:** [LayerPlayer.jsx](../../../queen-editor/frontend/src/features/photo_generation/LayerPlayer.jsx)

## Şikâyet

*(Kullanıcı, 6 Eylül.)* Video başlayınca başlat/durdur düğmesi kaybolmuyor, **görüntünün üzerinde
kalıyor** ve karenin ortasını örtüyor. Bugün düğme koşulsuz çiziliyor: `BUTTON` mutlak konumlu,
karenin tam ortasında, 64px, `zIndex: 2`.

Beş saniyelik bir klipte örtülen yer karenin göbeği — yani bakılmak istenen yer.

## Karar: oynarken düğme görünmez, kareye tıklamak duraklatır

*(Kullanıcı kararı, 13 Eylül.)* Düğme oynarken çizilmez. Duraklatmak için **görüntünün herhangi bir
yerine tıklanır**; durunca düğme geri gelir.

Seçilmeyen okuma, farenin kareye gelmesiyle düğmenin geri dönmesiydi *(masaüstü oynatıcılarının
klasik davranışı)*. İki bedeli vardı: fare karenin üstündeyken düğme yine görüntüyü örtüyor — yani
şikâyet yarı yarıya sürüyor — ve dokunmatikte `hover` diye bir şey yok.

## Düğme DOM'da kalır, yalnız çizilmez

Görünmezlik `opacity` ile, koşullu render ile değil. Sebep **klavye**: düğme DOM'dan çıkarsa video
oynarken odaklanacak hiçbir denetim kalmaz, ve duraklatmanın tek yolu fareyle kareye tıklamak olur.
`opacity: 0` ile düğme yerinde durur — Tab ile bulunur, Enter ile duraklatır, ekran okuyucuya hâlâ
*"Duraklat"* der — ama **hiçbir piksel çizmez**, ki maddenin istediği tam bu: kare tamamen görünüyor.

Kabul cümlesindeki *"düğme görüntünün üstünde değil"* buradaki ölçüyle karşılanıyor: üstünde duran
bir şey yok, çünkü görünen bir şey yok.

## İki tıklama, tek dönüş

Düğme sahnenin **içinde**. Sahneye tıklama durumu çevirecekse, düğmeye yapılan tıklama da yukarı
kabarıp sahneye ulaşır ve durum **iki kez** döner — yani hiç dönmemiş gibi olur. Düğmenin kendi
tıklaması bu yüzden kabarmayı durdurur.

Bu, bugün olmayan bir hatanın çivisi: tek başına bugünkü kodda da yeşil geçiyor. Yazılma sebebi, tam
da bu maddenin getirdiği şeyin onu kolayca kırabilmesi.

## Çivilenecek dört olgu

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Video oynarken düğme çizilmiyor, durunca geri geliyor | **kırmızı** — her zaman çiziliyor |
| 2 | Duruyorken kareye tıklamak videoyu başlatıyor | **kırmızı** — sahne tıklanabilir değil |
| 3 | Oynarken kareye tıklamak duraklatıyor | **kırmızı** — aynı sebeple |
| 4 | Düğmenin kendi tıklaması durumu bir kez çeviriyor | yeşil, ve öyle kalmalı |

Ölçü `opacity`: oynarken `"0"`, duruyorken `"1"`. jsdom'da çizim yok, o yüzden ölçülebilen şey stil
değerinin kendisi — dosyadaki öteki çiviler de *(`data-track`'in `position`'ı, bar renkleri)* aynı
yerden ölçüyor.

## Değişmeyenler

- **Zaman şeridi** *(`data-track`)*: saat, çizgi ve dalga formu görüntünün içinde kalmaya devam
  ediyor. Kullanıcı onlardan şikâyet etmedi, ve Fark 114 onları bilerek oraya koydu.
- **Var olan on bir test.** *"plays and pauses from the one round button"* düğmeyi `aria-label` ile
  buluyor; düğme DOM'da kaldığı için o test olduğu gibi geçmeye devam ediyor.
- **Ses tarafı, döngü, sürüklenme düzeltmesi.** Bu madde neyin çizildiği hakkında, ne çaldığı
  hakkında değil.

## Bu turda değişen

Yalnız [LayerPlayer.test.jsx](../../../queen-editor/frontend/src/features/photo_generation/LayerPlayer.test.jsx).
Bileşene dokunulmuyor, `dist` de derlenmiyor — ikisi de uygulama turunun işi.
