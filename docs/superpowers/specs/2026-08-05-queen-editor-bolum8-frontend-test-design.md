# Queen Editor — Bölüm 8: Frontend test altyapısı

**Tarih:** 2026-08-05 · **Yol haritası:** [2026-08-03-queen-editor-v2-roadmap.md](../plans/2026-08-03-queen-editor-v2-roadmap.md) Bölüm 8
**Önceki bölüm:** [Bölüm 7 — arayüz](2026-08-04-queen-editor-bolum7-arayuz-design.md)

## Neden bu bölüm var

FOUNDATION §4 kural taşıyan kodu backend'de tutar ve orada 181 pytest testi var. Ama frontend'in
kaçınılmaz olarak sahiplendiği bir avuç karar birikti — istek zaman aşımı, poll zinciri, hangi
durumda hangi kartın çıktığı — ve bunların hepsi bugüne kadar yalnız Colab'da gözle doğrulandı.
Bedeli iki kez ödendi:

- Bölüm 7'nin incelemesi `useGeneration`'da **ölümsüz poll zinciri** buldu (unmount sonrası
  zamanlayıcı yeniden kuruluyordu) — testle saniyede yakalanırdı, incelemeyle ancak dikkatli
  okumayla yakalandı.
- Ölü sunucuda **donuk çubuk** hatası Colab'da elle bulundu; düzeltmesi (10 sn zaman aşımı + soluk
  çubuk) yine testsiz gitti.

Bu bölüm o boşluğu kapatır. Yeni kullanıcı özelliği yok; çıktısı **`npm test` yeşil** ve bundan
sonraki her bölümün frontend mantığının testle gelebilmesi.

## Kapsam

**Var:** vitest + jsdom + @testing-library/react kurulumu; `npm test` / `npm run test:watch`
betikleri; `api.js`, `useGeneration`, `useProjectSettings` için davranış testleri; Bölüm 7'nin
bağlantı düzeltmesini kanıtlayan bir bileşen testi.

**Yok (bilinçli):**

- **E2E / tarayıcı otomasyonu** (Playwright vb.) — gerçek Colab + tünel + GPU ister; bizim
  doğrulama yolumuz zaten kullanıcının Colab turu.
- **Görsel regresyon / snapshot testleri** — tasarım `vendor/`'dan geliyor ve elle düzenlenmiyor;
  snapshot yalnız gürültü üretir, her yerleşim değişikliğinde güncellenmesi gereken bir bakım borcu
  olur.
- **`vendor/kit.jsx` testleri** — verbatim tasarım dosyası, bizim kodumuz değil.
- **Kapsam (coverage) eşiği** — sayı hedefi testin amacını kaydırır; testler karar taşıyan koda
  yazılır, orana değil.
- **Backend testlerine dokunuş** — pytest tarafı olduğu gibi kalır.

## 1. Araç seçimi

| Karar | Seçim | Neden |
|---|---|---|
| Koşucu | **vitest** | Projede zaten Vite var; aynı `vite.config.js`'i, aynı ESM çözümlemesini ve aynı JSX dönüşümünü kullanır. Jest ayrı bir dönüştürücü zinciri (babel/ts-jest) ve ayrı ESM ayarı ister — bizim kurulumda net bir bakım borcu, karşılığında kazanç yok. |
| DOM | **jsdom** | Hook'lar ve bileşenler tarayıcı olmadan koşar; `happy-dom` daha hızlı ama daha az uyumlu — hız burada darboğaz değil. |
| Hook/bileşen sarmalayıcı | **@testing-library/react** | `renderHook` ve `render` React 18'in `act` kurallarını doğru uygular; elle `act` sarmalamak kırılgan olur. |
| Test dosyası yeri | Kaynağın yanında: `src/**/<ad>.test.js(x)` | Frontend zaten özellik-öncelikli (CODE-STANDARD §Frontend): birlikte değişen dosyalar birlikte durur. Backend'in `tests/` klasörü Python paket düzeninin gereği, frontend'e taşınacak bir kural değil. Test dosyaları hiçbir yerden import edilmediği için `dist/` çıktısına girmez. |
| Kurulum dosyası | `src/test-setup.js` | `@testing-library/jest-dom` **kullanılmaz** (ekstra bağımlılık, ekstra sözlük); kurulum dosyası yalnız her testten sonra DOM'u ve global sahtelerini temizler. |

Bağımlılıkların hepsi `devDependencies`'e girer. Colab hiçbir zaman `npm install` çalıştırmaz —
sadece commit edilmiş `dist/`'i servis eder (FOUNDATION §3), yani bu paketler çalışma zamanına
dokunmaz.

## 2. Test edilen davranışlar

Testler **davranışı** doğrular, iç yapıyı değil: girdi olarak sahte `fetch`, çıktı olarak hook'un
döndürdüğü durum ya da ekrandaki metin. Hiçbir test bir iç değişkenin adına bakmaz.

### A · `shared/api.js`

| Davranış | Neden önemli |
|---|---|
| Proje adı URL'de kodlanır (`ü`, boşluk, `/`) | Türkçe proje adları normal; kodlama unutulursa istek yanlış yola gider |
| Sunucunun reddettiği istek → `body.error` metni aynen fırlatılır | FOUNDATION: sebep uydurulmaz, sunucunun kendi cümlesi gösterilir |
| Gövdesi olmayan/JSON olmayan hata → `"<kod> <statusText>"` | Tünel hata sayfası JSON döndürmez; ekran yine de bir şey söylemeli |
| Ağ reddi → `"Sunucuya ulaşılamadı — bağlantıyı kontrol et.\n<tarayıcı metni>"` | `GeneratePanel.describeError` bu ön eke bakarak başlığı seçiyor — ön ek sözleşmedir |
| **10 sn cevapsız istek iptal edilir** → `"…\nZaman aşımı (10 sn)"` | Bölüm 7'nin düzeltmesinin ta kendisi; donuk çubuğun kök nedeni |
| Başarılı cevapta zamanlayıcı temizlenir (istek sonradan iptal edilmez) | `finally`'siz bir sürüm testte yakalanmalı |

### B · `features/photo_generation/useGeneration.js`

| Davranış | Neden önemli |
|---|---|
| Açılışta `photos === null`, ilk poll hem durumu hem fotoğrafları ister | `null` = "henüz bilinmiyor"; `[]` ile karıştırılırsa galeri yalan söyler |
| `running` iken 2 sn'de bir yeni poll; `running` değilken zincir durur | Boşta sonsuz poll tüneli yorar |
| Poll patlarsa `error` dolar **ve zincir denemeye devam eder** | Tek kötü poll ekranı sonsuza dek dondurmamalı |
| Sonraki başarılı poll `error`'ı temizler | Tünel dönünce ekran kendini toparlar |
| `running` → `done` geçişinde fotoğraflar bir kez daha istenir | Son fotoğraf Drive'a durum değiştikten sonra düşüyor; yoksa elle yenilemeye kadar görünmez |
| Unmount sonrası ne `setState` ne yeni zamanlayıcı | İncelemede bulunan **ölümsüz zincir** hatası; regresyon kilidi |
| `generate()` başarılı → yerel `running` job (projesiyle birlikte) + zincir kurulur | Panel 202'den sonra anında kilitlenir |
| `stop()` basıldığı an `stopping === true` | Anında geri bildirim; sunucu cevabı beklenmez |
| Sunucudan gelen `stopping: true` de aynı sonucu verir | Yenilemede buton yine pasif kalır |

### C · `features/projects/useProjectSettings.js`

| Davranış | Neden önemli |
|---|---|
| `loading` → `ready` (ayarlar gelir) | Temel akış |
| Hata → `status: "error"` + sunucunun metni | Ekran hata kartını buradan besliyor |
| **Proje hızlı değiştirilirse eski cevap yutulur** | İncelemede bulunan yarış durumu; yanlış projenin ayarları ekrana düşerse kaydedilebilir |

### D · `features/photo_generation/GeneratePanel.jsx` (tek bileşen testi)

Bölüm 7'nin testsiz giden düzeltmesi burada kanıtlanır — harness'ın bileşen tarafının çalıştığını da
gösterir (sonraki bölümler bunun üstüne yazacak):

- `running` + `error` → ekranda **"Sunucuya ulaşılamıyor — son bilinen: 7/48"** yazar ve ilerleme
  kartı soluktur (`opacity` uygulanmış bir sarmalayıcı içinde).
- `running` + hata yok → aynı kart soluk **değildir** ve o metin ekranda yoktur.

Bu testte sahte `fetch` yok; bileşen prop alır. `settings` ve `job` düz nesnelerdir.

## 3. Testlerin uyacağı kurallar

- **Kırmızıdan başla:** her test önce mevcut kodla koşturulup gerçekten geçtiği (karakterizasyon)
  ya da düzeltme öncesi düştüğü görülür. Testin ne zaman düştüğü bilinmiyorsa test değildir.
- **Zaman sahte, ağ sahte:** `vi.useFakeTimers()` ve `vi.stubGlobal("fetch", …)`. Hiçbir test
  gerçek bir saniye beklemez; tüm paket saniyeler içinde biter.
- **Bir test bir davranış.** İsimler ne yaptığını söyler (`"10 sn cevapsız kalan istek zaman
  aşımına uğrar"`), `test1` gibi adlar yok.
- **Sahteler testin yanında durur** — ortak bir "test utils" katmanı kurulmaz; ihtiyaç doğmadan
  soyutlama yazılmaz (YAGNI). Aynı sahte üçüncü kez tekrarlanınca ortaklaştırılır, önce değil.
- **Dil:** test adları ve açıklamaları **Türkçe** (ekranda görünen metinlerle aynı dil, okuyan
  kullanıcının dili), kod yorumları İngilizce — repo sözleşmesi.
- **`dist/` etkilenmez:** bu bölüm `src/` dışında yalnız `package.json` ve `vite.config.js`'e
  dokunur; yine de bölüm sonunda `npm run build` koşulup `dist/` tazeliği doğrulanır.

## 4. Doğrulama

1. `npm test` (queen-editor/frontend/) — tüm paket yeşil, saniyeler içinde biter.
2. Kasıtlı bozma turu (her biri geri alınır): `TIMEOUT_MS`'i devre dışı bırak → zaman aşımı testi
   düşer; `useGeneration`'daki `alive.current` kontrolünü kaldır → unmount testi düşer;
   `GeneratePanel`'in soluklaştırma sarmalayıcısını çıkar → bileşen testi düşer. Düşmeyen test
   yanlış yazılmıştır.
3. `npm run build` temiz; `dist/` değişmemiş olmalı (test dosyaları paketlenmez).
4. `pytest` (queen-editor/) hâlâ yeşil — bu bölüm backend'e dokunmadı.

## Kararlar

- **vitest + jsdom + @testing-library/react**, hepsi `devDependencies`; Colab etkilenmez.
- **Test dosyaları kaynağın yanında** (`src/**/<ad>.test.js`), ayrı `tests/` klasörü yok.
- **jest-dom yok, coverage eşiği yok, snapshot yok, E2E yok** — gerekçeleri §Kapsam'da.
- **Test adları Türkçe.**
- Bu bölüm mevcut davranışı **dondurur**; test yazarken bulunan gerçek hatalar düzeltilmez, kayda
  geçer ve ilgili bölüme yazılır (kapsamı şişirmemek için). Tek istisna: testin kendisi yanlışsa.
