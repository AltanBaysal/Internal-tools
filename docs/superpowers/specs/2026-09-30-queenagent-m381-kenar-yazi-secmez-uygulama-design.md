# Madde 381 — Panelin kenarını çekmek yazı seçmez · uygulama turu

**Kaynak:** [yol haritasının 381'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-30-queenagent-m381-kenar-yazi-secmez-testler-design.md). Kırmızı iki test:
listenin ve açık dosyanın kenarına basış, tarayıcının varsayılanını durdurmalı.

**Kullanıcıdan gereken:** hiçbir şey.

## Seçilen yol

`FileRail.jsx`'teki `Grip`'in `onMouseDown`'ı, sürüklemenin başladığı yeri tuttuktan sonra
`event.preventDefault()` çağırır. Tek satır; yorumu nedenini söyler. Aynı `Grip` hem listede hem açık
dosyada durduğu için iki test birden yeşile döner.

Neden tüm sürükleme boyunca tutar: tarayıcı yazı seçimini yalnız basışta başlatır, ve sonraki her
`mousemove` o seçimi uzatır. Basışın varsayılanı durdurulunca başlayan bir seçim yoktur; işaretçi
mesajların, kartın, yazma kutusunun üstünden geçse de, pencereden çıkıp dışarıda bırakılsa da uzatılacak
bir şey kalmaz. Sayfada hiçbir şey değiştirilmez, o yüzden sürükleme bitince yazı yine seçilebilir —
geri alınacak bir durum yok. Tasarımın tuvali (`canvas.html`) aynı çatışmayı aynı yolla çözüyor.

Yan etkisi: basış, odağı o anki öğeden (ör. yazma kutusundan) almaz. Kenar zaten odaklanabilir değil;
yazma kutusunda yazan biri kenarı çekip yazmaya devam edebilir.

## Bırakılan yollar

- **Sürükleme boyunca `body`'ye `user-select: none` yazmak.** İki parça daha — koymak ve kaldırmak —
  ve kaldırmak bırakışın duyulmasına bağlı. Basış seçimi hiç başlatmıyorsa, kilitlenecek bir şey yok.
- **Yalnız kenara `user-select: none`.** Tutmaz: seçim kenarda başlamasa da, basışın varsayılanı
  durmadıkça tarayıcı işaretçinin geçtiği öteki öğelerdeki yazıyı seçer.

## Değişmeyenler

- `mousemove` / `mouseup` dinleyicileri, genişliğin App'e gidişi, `rail--dragging` sınıfı.
- CSS değişmez.
- Sürüklemeden önce zaten seçili olan yazı: bu maddenin sorusu değil (test spec'inde yazılı).

## dist

Kaynak değişiyor, ama `dist` bu koşuda derlenmez: koşuyu birleştiren oturum derler ve kaynakla aynı
commit'e koyar (koşunun kuralı; paralel dalların `dist`'i birleşirken çakışır).

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel: dördü de yeşil. Tarayıcıda: panelin sol kenarını tutup mesajların
üstünden sola, sonra sayfanın dışına sürükleyip orada bırakmak — hiçbir yazı mavi olmaz; ardından bir
mesajın yazısı fareyle seçilebilir.

Adım adım dökümü
[uygulama turunun planında](../plans/2026-09-30-queenagent-m381-kenar-yazi-secmez-uygulama-plan.md).
