# Madde 412 · Uygulama V8 diyecek — test turunun tasarımı

**Tarih:** 1 Ekim 2026 · **Madde:** [v8 yol haritası](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Değer maddenin satırında: `V8`.

## Bugün ne var

`frontend/src/shared/version.js` `VERSION = "V6"` diyor; v7 ve v8 koşuları onu değiştirmedi. Dört
ekran onu başlığında `Queen Editor ${VERSION}` olarak çiziyor: proje listesi
(`ProjectsScreen.jsx`), proje ekranı (`ProjectScreen.jsx`), karenin sayfası (`PhotoDetail.jsx`) ve
export ekranı (`ExportScreen.jsx`). `queen-editor/` altında `dist/` dışında başka hiçbir yer bir
sürüm numarası çizmiyor — `index.html`'in başlığı yalnız `Queen Editor`, notebook ve backend sürüm
yazmıyor.

## Bu madde kırmızı veremez, ve sebebi bir kural

248'in kararı, 285'te de aynen uygulandı: **sayı elle yazılan bir karardır**, ve `"V8"`i bir
teste yazmak o kararı iki yere koymak olur. `version.test.js` o yüzden yalnız biçimi tutuyor
(`/^V\d+$/`). Kullanıcı da sayıyı yol haritalarına bağlayan, sayı unutulunca kırmızıya dönen testi
bu maddeye almadı *(yol haritası, 412)*.

Yani `V6`'yı `V8` yapmak hiçbir testi düşürmez, ve düşürecek bir test yazmak 248'i çiğner. **Bu tur
bu yüzden kırmızı vermiyor**; bu `skip`/`xfail` ile gizlenmiyor, olduğu gibi yazılıyor. Turların
sırası korunuyor: test önce, kod sonra.

## Ama maddenin "her ekranında" dediği bugün tutulmuyor

*Bitti sayılır:* "Queen Editor'ün sürümü gösteren **her ekranında** `V8` yazıyor." Sayı tek yerde
olduğu için bu, iki olgunun toplamı: `version.js` `V8` diyor, **ve her ekran tam olarak
`version.js`'in dediğini çiziyor**.

İkinci olguyu bugün yalnız bir ekran tutuyor. 285 export ekranının başlık testini modülün değerine
bağladı; öteki üçü — proje listesi, proje ekranı, karenin sayfası — hâlâ 248'deki kalıpla bakıyor:
`/^Queen Editor V\d+$/`. 248'de kalıbın sebebi modülün henüz olmamasıydı (içe almak dört test
dosyasını toplanamaz yapardı); o sebep artık yok. Bugün bu üç ekrandan birine elle `"V6"`
yazılsa, ya da biri modülü okumayı bıraksa, **hiçbir test düşmez** — ve `V8` o ekranda hiç
görünmez.

## Seçenekler

1. **`version.test.js`'te `"V8"`i çivilemek.** Bugün kırmızı verir, ama 248'i çiğner ve kullanıcının
   almadığı korumanın bir eşi olur. **Alınmadı.**
2. **Mevcut testlere güvenmek, hiçbir şey yazmamak.** Dört ekrandan üçü maddenin "her ekranında"sını
   tutmuyor. **Alınmadı.**
3. **Üç ekranın başlık testini modülün değerine bağlamak**, 285'in export için yaptığı gibi.
   Değer hiçbir teste yazılmıyor, sayı yine tek yerde; ama dört ekranın dördü de artık modülün
   dediğini çizmeye bağlı. **Seçilen bu.**

## Çivilenen olgu

**Dört ekranın başlığı `Queen Editor ${VERSION}` diyor**, `version.js`'ten okunan değerle:

| Test dosyası | Test | Bugün |
|---|---|---|
| `ProjectsScreen.test.jsx` | `puts the version next to the name` | kalıp → modülün değeri |
| `ProjectScreen.test.jsx` | `puts the version next to the name` | kalıp → modülün değeri |
| `PhotoDetail.test.jsx` | `puts the version next to the name` | kalıp → modülün değeri |
| `ExportScreen.test.jsx` | `puts the version next to the name` | zaten modülün değeri *(285)*, değişmiyor |

Her değişen test `VERSION`'ı `../../shared/version.js`'ten içe alıyor, ve ekranda tam
`` `Queen Editor ${VERSION}` `` metnini arıyor. Testin yanındaki yorum 285'in export testindeki
gerekçeyi söylüyor: kalıp, elle yazılmış bir sayıyı da geçirirdi.

## Beklenen sonuç

**Kırmızı yok, dört satır yeşil kalıyor** — ekranlar bugün de modülü okuyor. Sayının `V8` olması
uygulama turunda, ve orada da yeşil kalacak: testler sayıyı değil **bağı** tutuyor.
