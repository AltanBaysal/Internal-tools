# Madde 381 — Panelin kenarını çekmek yazı seçmez · test turu

**Kaynak:** [yol haritasının 381'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) — 356
tarayıcıda denenirken bulundu, 29 Eylül. Karar kullanıcının, 30 Eylül: kenar çekilirken sayfada
hiçbir yazı seçilmez ("bu da evet"). Bitti sayılır: "Panelin kenarı çekilirken sayfada hiçbir yazı
seçilmiyor."

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı; ne istendiği ve nasıl görüleceği yazılı.

## Bugün ne oluyor

Kenar, `FileRail.jsx`'in `Grip`'i: rail'in sol kenarında 6px'lik bir şerit, `onMouseDown`'da sürüklemenin
başladığı yeri tutar; `window`'un `mousemove`'u genişliği sorar, `mouseup`'ı sürüklemeyi bitirir. Aynı
`Grip` hem listede hem açık dosyada durur (356).

Tarayıcının bir fare basışına kendi cevabı yazı seçmeye başlamaktır, ve `onMouseDown` bu cevabı
durdurmuyor: basış şeritte başlar, işaretçi şeritten ilk karede çıkar, ve tarayıcı üstünden geçtiği her
yazıyı — mesajlar, kart, yazma kutusu — seçime katar.

Tasarım aynı çatışmayı kendi tuvalinde (`canvas.html`) basışın varsayılanını durdurarak çözüyor:
"The browser's own answer to a press-and-drag is to select text; the canvas's answer is to pan, and
the two cannot both happen."

## Ne kanıtlanacak

1. **Listenin kenarına basış, tarayıcının varsayılanını durdurur.** Test `fireEvent.mouseDown`'ın
   dönüşüne bakar: olay iptal edildiyse `false` döner. Bugün `true`: kırmızı.
2. **Açık dosyanın kenarına basış da durdurur** — 356'dan beri aynı kenar, aynı hata. Bugün `true`:
   kırmızı.

Seçim yalnız basışta başlar; basışın varsayılanı durdurulunca tarayıcı o sürüklemede hiç seçim
başlatmaz — işaretçi neyin üstünden geçerse geçsin, sayfadan çıksa da, bırakış nerede olursa olsun.
Sayfada hiçbir şey değiştirilmediği için, sürükleme bitince yazı yine seçilebilir. Bu yüzden basışı
tutan iki test yetiyor: jsdom fareyle yazı seçmez, ve seçimin sürüklemenin ortasında başlamadığını
tarayıcının kendisi söyler.

Testler `FileRail.test.jsx`'e, Madde 356'nın bloğunun altına girer — kenarın öteki testleri orada.

## Testler ne tutmaz

Sürüklemeden önce zaten seçili olan bir yazı: madde sürüklemenin seçtiği yazı hakkında; basış önceki
seçimi temizlemiyor, ve bu maddenin sorusu değil.

## Bu turda yazılmayanlar

- `FileRail.jsx` değişmez; uygulama turunda.
- `dist` derlenmez: kaynak değişmiyor, yalnız testler ve belgeler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` iki yeni testte kırmızı
verir; öteki üç süit değişmez. Kırmızı hâliyle commit edilir.

Adım adım dökümü
[test turunun planında](../plans/2026-09-30-queenagent-m381-kenar-yazi-secmez-testler-plan.md).
