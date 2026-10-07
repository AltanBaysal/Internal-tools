# Madde 428 · Başlıkta sürüm V9 yazar — test turunun tasarımı

**Tarih:** 6 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
428 · **Dal:** `feat/queen-editor-v9` · **Tur:** 1/2 — yalnız testler ·
**Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md) ·
**Öncesi:** [412'nin test turu](2026-10-01-queen-editor-m412-surum-v8-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey. Değer maddenin satırında: `V9` *(Claude sordu, 6 Ekim; kullanıcı — "olsun evet")*.

## Bugün ne var

`frontend/src/shared/version.js` `VERSION = "V8"` diyor; v9 koşusu onu henüz değiştirmedi. Dört ekran
onu başlığında `Queen Editor ${VERSION}` olarak çiziyor: proje listesi (`ProjectsScreen.jsx`), proje
ekranı (`ProjectScreen.jsx`), karenin sayfası (`PhotoDetail.jsx`) ve export ekranı
(`ExportScreen.jsx`). `queen-editor/` altında `dist/` dışında başka hiçbir yer `V8` yazmıyor.

Testler 412'den beri:

| Test dosyası | Test | Neyi tutuyor |
|---|---|---|
| `version.test.js` | `the version reads as a run number` | biçim: `/^V\d+$/` *(248)* |
| `ProjectsScreen.test.jsx` | `puts the version next to the name` | başlıkta tam `` `Queen Editor ${VERSION}` `` *(412)* |
| `ProjectScreen.test.jsx` | `puts the version next to the name` | aynı *(412)* |
| `PhotoDetail.test.jsx` | `puts the version next to the name` | aynı *(412)* |
| `ExportScreen.test.jsx` | `puts the version next to the name` | aynı *(285)* |

## Bu madde kırmızı veremez, ve sebebi bir kural

248'in kuralı, 285'te ve 412'de de aynen uygulandı: **sayı elle yazılan bir karardır**, ve `"V9"`u
bir teste yazmak o kararı iki yere koymak olur. Kullanıcı da sayıyı yol haritalarına bağlayan, sayı
unutulunca kırmızıya dönen testi 412'de almadı *(v8 yol haritası, 412 — "istenirse ayrı bir madde
olur")*; 428'in satırı da onu istemiyor: *"başka bir şey değişmez"*.

Yani `V8`'i `V9` yapmak hiçbir testi düşürmez, ve düşürecek bir test yazmak 248'i çiğner. **Bu tur
bu yüzden kırmızı vermiyor**; bu `skip`/`xfail` ile gizlenmiyor, olduğu gibi yazılıyor. Turların
sırası korunuyor: test önce, kod sonra.

## Maddenin "bitti sayılır"ı bugün testle tutuluyor

*Bitti sayılır:* "Projeler sayfasının ve proje ekranının başlığında 'Queen Editor V9' yazıyor."
Sayı tek yerde olduğu için bu, iki olgunun toplamı: `version.js` `V9` diyor, **ve bu iki ekran tam
olarak `version.js`'in dediğini çiziyor**.

412'de ikinci olgunun yarısı eksikti — üç ekran yalnız kalıba bakıyordu, ve 412 onları modülün
değerine bağladı. **Bugün eksik yok:** dört ekranın dördünün testi de modülün değerini arıyor. Bu
ekranlardan birine elle bir sayı yazılsa, ya da biri modülü okumayı bıraksa, testi düşer.

## Seçenekler

1. **`version.test.js`'te `"V9"`u çivilemek.** Bugün kırmızı verir, ama 248'i çiğner ve kullanıcının
   almadığı korumanın bir eşi olur. **Alınmadı.**
2. **Sayıyı yol haritasının dosya adına bağlayan yeni bir test.** Kullanıcının 412'de almadığı
   koruma; ayrı bir madde olarak istenmedi. **Alınmadı.**
3. **Hiçbir test yazmamak, mevcut beş testin tuttuğunu yazıya geçirmek.** Bağ zaten dört ekranda
   da tutuluyor, biçim `version.test.js`'te; eklenecek bir olgu yok. **Seçilen bu.**

## Bu turda değişen

Hiçbir test dosyası. Bu tasarım ve planı commit'lenir; mesaj kırmızı olmadığını ve sebebini söyler.

## Beklenen sonuç

**Kırmızı yok, dört satır yeşil** — ekranlar bugün de modülü okuyor. Sayının `V9` olması uygulama
turunda, ve orada da yeşil kalacak: testler sayıyı değil **bağı** tutuyor.
