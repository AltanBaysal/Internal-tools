# Madde 62 · Tur 1 (test) — Tasarım

**Madde:** yeni — kullanıcı kararı, 20 Ağustos: "Colab Secret'ta xAI anahtarımız zaten var, onu
kullanalım, Settings'i uçuralım."
**Bu belgenin konusu:** anahtarın nereden geldiğini ve Settings'in gittiğini **ne tutacak**.

---

## Sorun

İki tane, ve biri diğerinden ağır.

**Bir: anahtar okunabiliyor.** `GET /api/settings` anahtarı düz metin döndürüyor
(`presentation/routes.py`). Kodun kendi yorumu gerekçesini de yazıyor: *"this is the user's own
machine and their own key"*. O varsayım yazıldığı gün doğruydu — yerel tek yüzeydi. Madde 53–58
ikinci bir yüzey ekledi: Colab, parolasız açık bir tünelin arkasında. Linki eline geçiren
`curl <link>/api/settings` der ve xAI anahtarını okur. Varsayım kodun içinde durmaya devam ederken
altındaki dünya değişti.

**İki: aynı değerin iki kaynağı olacaktı.** Colab Secrets'ta anahtar zaten var — `GITHUB_TOKEN` ile
aynı panelde, queen-editor'ün yıllardır okuduğu yerde. Defter onu okuyup uygulamaya geçirseydi ve
Settings ekranı da kalsaydı, hangisinin kazandığını söyleyen bir öncelik kuralı doğardı. Bir değerin
iki kaynağı, ikisinden hangisinin geçerli olduğunu kimsenin bilmediği bir üçüncü durum demek.

## Karar

Anahtar **`XAI_API_KEY` ortam değişkeninden** gelir. Settings — ekran, rota, uç nokta, depo,
`settings.json` dosyası — tamamen kalkar.

Bu, deliği kapatmanın yan ürünü değil, kendisi: okunacak bir uç nokta kalmayınca okunacak bir şey de
kalmaz.

## Anahtarın yolu

| Yüzey | Nereden | Nasıl |
|---|---|---|
| Colab | Secrets → `userdata.get("XAI_API_KEY")` | CONFIG hücresi okur, Serve hücresi `env` içinde uygulamaya geçirir — `QUEENAGENT_ROOT` ile aynı yoldan |
| Yerel | Kabuktaki `XAI_API_KEY` | `backend/config.py` başlangıçta okur |

Uygulama tarafında tek bir okuma noktası var: `config.XAI_API_KEY`. `XaiClient` anahtarı bir
**fonksiyon** olarak almaya devam eder — bugünkü şekli bu ve bu madde onu değiştirmeyi gerektirmiyor;
ayrıca değeri istek anında okumak, kaynağın ileride değişmesini istemciye haber vermeden mümkün
kılıyor.

## Anahtar yoksa ne söylenir

Ekran gidince "anahtarını Settings'e yaz" cümlesi de gider — gidilecek yer kalmıyor. Yerine iki ayrı
cevap geçiyor, çünkü iki yüzeyde eksik anahtar iki ayrı anda fark ediliyor:

- **Colab'da: baştan durur.** CONFIG hücresi `assert XAI_API_KEY` der ve ne yapılacağını yazar —
  `GITHUB_TOKEN` ile birebir aynı şekil. Gerekçesi Colab'a özel: orada anahtarı sonradan girmenin
  yolu yok, yani anahtarsız açılan uygulama hiçbir şey yapamayan bir uygulama. Yola çıkmadan durmak,
  ilk mesajda çuvallamaktan iyidir.
- **Yerelde: sunucunun kendi cümlesi.** `XaiNotConfigured` bugün de *"No API key is set."* diyor ve
  bu, hata kartında zaten görünüyor. Deponun kuralı da bu: servisin ne dediğini bas, sebep uydurma.

Bugünkü `missingKey` bayrağı ve hata kartındaki **Add your API key in Settings** düğmesi kalkar.
Kartın yanındaki yorum *"whether a key is set is something the app knows for itself"* diyordu — o
bilgi bir **düğme çizip çizmemeye** karar vermek için gerekliydi. Düğme olmayınca karar da yok:
kart sunucunun söylediğini gösterir, o kadar.

## Tuzak: `/settings` adresi ölü kalıyor

Rota silinince `parsePath("/settings")` yakalanmayan adreslerin düştüğü yere, `view: "root"`a düşer.
Ama Madde 52'de çatal etkisine konan koruma **harfi harfine** `window.location.pathname === "/"`
diye soruyor. `/settings` bu koşulu geçmez: çatal yönlendirmez, hiçbir ekran da çizilmez —
kullanıcı boş bir sayfaya bakar.

Yani bu madde çatalın sorusunu da değiştirmek zorunda: *"adres tam olarak `/` mi"* değil,
**"tarayıcının şu andaki adresi bir çatala mı çözülüyor"**. Madde 52'nin kazandığı şey korunuyor —
soru hâlâ tarayıcının o anki adresine soruluyor, render'ın kurulduğu ana değil; değişen yalnız
sorunun genişliği.

Bu, tasarımın en kolay atlanacak yeri: her iki parça tek başına doğru, birlikte bir boşluk açıyorlar.

## Testin sorması gerekenler

**Yapılandırma** — `config.XAI_API_KEY` ortamdan geliyor mu; değişken yokken boş mu (`None` değil:
boş, uygulamanın anahtarsız açılan ordinaryen hâli).

**Birleştirme kökü** — `main.py` anahtarı `config`ten mi alıyor; settings özelliğini artık bağlıyor
mu; `features/settings` ağacı yerinde mi.

**Defter** — xAI anahtarı Secrets'tan okunuyor mu; yokken ne yapılacağı söyleniyor mu; `env` ile
uygulamaya geçiyor mu; defter hâlâ bir Settings ekranını işaret ediyor mu; anahtar hiç basılıyor mu.

**Arayüz** — `/settings` artık kendi yeri değil mi; kenar çubuğunda Settings satırı var mı; hata
kartı hangi bayrak verilirse verilsin Settings düğmesi çiziyor mu; uygulama sunucuya hiç ayar soruyor
mu.

## Bu turda dokunulmayanlar

`test_settings.py`, `test_settings_api.py`, `SettingsScreen.test.jsx`, `useSettings.test.jsx` ve
App/Sidebar/ChatScreen içindeki eski Settings testleri **yerinde kalır ve yeşil kalmaya devam eder.**
Onlar var olan kodu doğru anlatıyorlar; yanlış oldukları an kod silindiği an. Anlattıkları şeyle
birlikte, ikinci turda ölürler.

Bunun görünür sonucu: bu commit'te bazı dosyalar kendi kendisiyle çelişir — Sidebar'ın testi hem
"Settings satırı var" hem "Settings satırı yok" der. Kırmızı commit'in tanımı bu; çelişkiyi kaldıran
şey ikinci turda kodun kendisi.
