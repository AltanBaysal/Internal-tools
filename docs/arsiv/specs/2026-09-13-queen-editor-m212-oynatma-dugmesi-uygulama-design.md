# Madde 212 · Oynatma düğmesi — uygulama turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Test turu:** [tasarım](2026-09-13-queen-editor-m212-oynatma-dugmesi-testler-design.md) ·
[plan](../plans/2026-09-13-queen-editor-m212-oynatma-dugmesi-test-plan.md) · kırmızı `ac6dbfa`

## Kırmızının istediği

```
× hides the button while the video plays      → opacity '' bekleniyordu '0'
× starts the video when the picture is clicked → sahneye tıklamak hiçbir şey yapmıyor
× pauses the video when the picture is clicked → aynısı
```

Üçü de tek bir cümlenin iki yüzü: **oynarken düğme çizilmez, ve yerine kare tıklanır.**

## Üç değişiklik

**1 · Düğmenin saydamlığı duruma bağlanır.** `BUTTON` sabiti olduğu gibi kalıyor; üzerine yalnız
`opacity` biniyor — `playing ? 0 : 1`. Sabiti bölmemenin sebebi, geri kalan on üç özelliğin durumla
ilgisi olmaması: değişen tek şey görünürlük.

**2 · Sahne tıklamayı alır.** `[data-scene]`'e `onClick={toggle}`. Düğme zaten onun içinde
duruyordu; artık karenin tamamı aynı işi yapıyor.

**3 · Düğmenin tıklaması kabarmayı durdurur.** Olmazsa düğmeye yapılan tıklama önce düğmeyi, sonra
sahneyi çalıştırır — durum iki kez döner, yani hiç dönmez ve düğme ölü görünür. Kırmızı turunda
yazılan dördüncü çivi tam bunu tutuyor.

## İmleç de söyler

`SCENE`'e `cursor: "pointer"` giriyor. Tıklanabilir bir yüzeyin tıklanabilir olduğunu söylemesi
gerekir, ve düğme çizilmezken bunu söyleyecek başka hiçbir şey kalmıyor. Testi yok — jsdom imleç
çizmiyor — ama eksikliği kullanıcının göreceği bir şey.

## Neden `opacity`, neden `display` değil

`display: none` ya da koşullu render düğmeyi erişilemez kılar: video oynarken odaklanacak hiçbir
denetim kalmaz ve duraklatmak yalnız fareyle mümkün olur. `opacity: 0` ile düğme yerinde — Tab ile
bulunur, Enter ile duraklatır, ekran okuyucuya *"Duraklat"* der — ve hiçbir piksel çizmez.

Görünmez düğmenin tıklamayı yakalamaya devam etmesi bir sorun değil: yakaladığında yaptığı şey,
sahnenin yapacağının aynısı.

## Geçiş yok

Saydamlık bir anda değişiyor, süzülerek değil. Oynatmaya basan biri düğmenin gitmesini bekliyor;
araya konan yarım saniye o anı geciktirmekten başka bir şey yapmaz. Madde bir hareket dili
istemiyor, örtmenin kalkmasını istiyor.

## Dokunulmayanlar

Zaman şeridi, dalga formu, döngü, sesin sürüklenme düzeltmesi ve `toggle`'ın kendi gövdesi. Bu madde
neyin **çizildiği** hakkında.

## Değişen

[LayerPlayer.jsx](../../../queen-editor/frontend/src/features/photo_generation/LayerPlayer.jsx), ve
`dist` — ön yüz değişikliği derlenmeden bitmiş sayılmıyor, çünkü defter bu depoyu klonluyor ve
kendisi derlemiyor.
