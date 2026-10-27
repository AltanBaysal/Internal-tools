# Madde 62 · Tur 2 (uygulama) — Tasarım

**Tur 1 tasarımı:** [2026-08-20-queenagent-m62-test-design.md](2026-08-20-queenagent-m62-test-design.md)
— anahtarın yolu, eksik anahtarın nerede söylendiği ve `/settings` tuzağı orada karara bağlandı ve
burada tekrar edilmiyor.

**Bu belgenin konusu:** silme işleminin kendi kararı olan iki şey. İkisi de "neyi sileceğim"
sorusunun cevabı değil — silinen şeye *yaslanan* şeylerin ne olacağı.

---

## 1. Madde 52'nin testleri taşıtını kaybediyor

`App.test.jsx`'te çatalın iki testi var ve ikisi de "kullanıcı başka bir yere gitti"yi **Settings ile**
canlandırıyor: biri kenar çubuğundaki Settings satırına basıyor, öteki adres çubuğuna `/settings`
yazıyor. Settings gidince ikisi de taşıtsız kalıyor.

Bu testler ölmemeli. Anlattıkları şey Madde 52 — geç gelen bir listenin, kullanıcının seçtiği adresi
ezmemesi — ve o kural yerinde duruyor. Değişmesi gereken yalnız hangi adrese gidildiği.

**Yeni taşıt: ikinci bir proje.** Çatalın kendi indiği yer listenin ilk projesi (`projects[0].id`),
yani oraya gitmek hiçbir şey kanıtlamaz: çatal ateşlense de ateşlenmese de adres aynı çıkar. Test
ancak çatalın **kendiliğinden asla seçmeyeceği** bir adresle bir şey söyleyebilir. Onun için iki
projeli bir liste kuruluyor ve gidilen yer ikincisi.

**Ama ikisinden yalnız biri yaşıyor, ve bu belge önce ikisinin de yaşayacağını yazmıştı.**
Uygulamayı okurken çıktı: iki testin ayrımı, birinin **uygulamanın içinden** gitmesiydi — React
haberdar — ötekininse adresi React'e söylemeden değiştirmesi. Ve liste gelmeden önce uygulamanın
içinden gidilecek hiçbir yer kalmıyor: kenar çubuğunda o anda proje satırı yok, `+ Yeni proje`
yönlendirmiyor, katlama düğmesi zaten bir yere gitmiyor. Settings satırı o pencerede tıklanabilen
**tek** navigasyondu.

Kaybedilen bir şey yok, ve sebebi taşıtın yokluğundan daha sağlam: uygulama içinden gidildiğinde
React'in tuttuğu adres güncelleniyor, `landing` null'a dönüyor ve **etki hiç çalışmıyor**. Yaşayan
test ise etkinin çalıştığı ve reddetmek zorunda kaldığı hâli tutuyor — yani zor olan yarısı, kolay
olanı içine alıyor.

Üçüncü bir test — kenar çubuğundaki Settings satırının ekranı açması — taşıtsız değil, **konusuz**
kalıyor. O da ölür.

## 2. `settings` bir özellikti; artık tek özellik kalıyor

`CODE-STANDARD.md` mimariyi "iki özellik: `workspace` ve `settings`" diye anlatıyor ve `settings`in
neden ayrı durduğunu gerekçelendiriyor: workspace'teki hiçbir şeyin anahtar hakkında fikri yok, ve
`feature ↛ feature` yasağı bu yüzden tutuyor.

O bölüm silinmiyor, **daralıyor.** Kalması gereken şey `workspace`in neden dört değil bir özellik
olduğu — o gerekçe (bir mesaja cevaben dosya yazmak projeye, sohbete ve dosyaya aynı anda dokunur)
`settings`ten bağımsız ve hâlâ doğru. Gitmesi gereken şey ikinci özelliğin kendisi.

Ve yerine bir cümle geliyor, çünkü bu bir belgenin söyleyebileceği, kodun söyleyemeyeceği bir şey:
**QueenAgent'ın artık kendi yapılandırması diye bir özelliği yok.** Uygulamaya dışarıdan söylenen
her şey `config.py`'de duruyor ve ortamdan geliyor. Bu, henüz yazılmamış kodu bağlayan bir kural —
bir sonraki ayar için yeniden bir özellik açmak isteyen kişinin okuması gereken şey, ve tam olarak
bu yüzden belgede.

## 3. Belgelerdeki yalanlar

Üç yer bugün doğru, yarın yanlış:

- `FOUNDATION.md` Karar 1 — *"the root travels in `QUEENAGENT_ROOT`, the key lives under it"*.
  Anahtar artık kökün altında yaşamıyor; o cümle Colab yolunun **gerekçesinin** parçasıydı, yani
  düzeltilmesi gereken bir gerekçe. Uygulamanın deftere uygun oluşu hâlâ doğru — sebebi değişiyor:
  kök de anahtar da ortamdan geliyor.
- `CODE-STANDARD.md` veri tablosu — `settings.json` diye bir satır var. Böyle bir dosya kalmıyor.
- `README.md` — "Settings'i aç ve anahtarını yapıştır" diyen bir paragraf. Yerine anahtarın
  ortamdan geldiği geçiyor.

`FOUNDATION.md`'in "parola yok, adresi eline geçiren her şeyi eline geçirir" cümlesi **duruyor** ve
zayıflamıyor. Anahtar artık okunamıyor ama dosyalar hâlâ okunabiliyor, silinebiliyor; ve anahtar
uygulamanın içinde durmasa da uygulama onunla istek atmaya devam ediyor. Kararın kendisi
değişmedi — yalnız kaybedilecek şeylerden biri listeden çıktı.

## Bilerek yapılmayan

**`XaiClient`'ın şekli.** Anahtarı bir fonksiyon olarak almaya devam ediyor. Değer artık başlangıçta
sabitlendiği için bunu bir dizgeye indirmek mümkün, ama bu madde onu gerektirmiyor ve istemcinin
sözleşmesini değiştirmek `test_xai_client.py`'nin tamamına dokunmak demek. Fonksiyon olması ayrıca
değeri istek anında okutuyor, yani kaynağın ileride değişmesi istemciye hiç uğramıyor.
