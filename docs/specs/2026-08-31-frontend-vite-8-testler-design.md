# Ön yüz derleme zinciri vite 8'e çıkar · Tur 1 (test) — Tasarım

**Kaynak:** kullanıcının isteği *(31 Ağustos)* ve `npm audit --prefix queen-agent/frontend`
çıktısı. Yol haritası açılmadı *(kullanıcı kararı, 31 Ağustos — bkz. Madde 137)*.
**Numarasız, bilerek:** Madde sayacı QueenAgent'ın ürün yol haritasının; queen-editor'ün kendi
`gorev` sayacı var. Bu iş **ikisinin ortak derleme zincirini** değiştiriyor, yani hiçbirinin ürün
maddesi değil. Kullanıcı isterse numara verilir.
**Dal:** `feat/frontend-vite-8`.

## Sorun

`npm audit` iki açık bildiriyor, ve ikisinin kökü tek:

> `esbuild <=0.24.2` — **moderate** — [GHSA-67mh-4wv8-2f99](https://github.com/advisories/GHSA-67mh-4wv8-2f99)
> *esbuild enables any website to send any requests to the development server and read the response*

`vite` esbuild'i bağımlılık olarak taşıdığı için o da listeye giriyor; "2 açık" bundan. İki ön yüz
de `vite ^5.4.0`'da, yani ikisi de kapsamda.

**Kullanıcıyı etkilemiyor.** Yayınlanan şey `dist`, ve içinde ne esbuild var ne vite — derlenmiş düz
JavaScript. Defteri çalıştıran birinin bu açıkla teması yok.

**Geliştiriciyi etkiliyor.** `npm run dev` çalışırken açılan sunucu, hangi siteden gelirse gelsin
isteklere cevap veriyor. O sırada aynı tarayıcıda kötü niyetli bir sayfa açıksa kaynak kod
okunabiliyor. Ayakta bir zarar yok; kapatılmayı bekleyen bir kapı var.

## Yol

Üç paket birlikte yükselir, iki ön yüzde de aynı sürümlere:

| Paket | Bugün | Sonra |
|---|---|---|
| `vite` | `^5.4.0` | `^8.0.0` |
| `@vitejs/plugin-react` | `^4.3.1` | `^6.0.0` |
| `vitest` | `^3.2.7` | `^4.0.0` |

**Üçü birden, çünkü matris başka seçenek bırakmıyor** *(npm kayıt defterinden okundu, 31 Ağustos)*:

- `@vitejs/plugin-react@6` yalnız `vite ^8.0.0` kabul ediyor
- `vitest@3.2.7` vite'ı **peer değil doğrudan bağımlılık** olarak taşıyor, aralığı
  `^5.0.0 || ^6.0.0 || ^7.0.0-0`. Vite 8'in yanında bırakılsa kendi vite 7'sini ayrıca kurardı, ve
  testler derlemeden **başka bir motorda** koşardı
- `vitest@4.1.11` `vite ^6 || ^7 || ^8` kabul ediyor
- `vite@8` Node `^20.19.0 || >=22.12.0` istiyor; cihazdaki Node **24.19.0**

**Neden 7 değil 8** *(kullanıcı kararı, 31 Ağustos)*: açık aslında vite 6.2'den beri kapalı —
esbuild `^0.25.0`'a geçmiş — yani 7 de yeterdi. 8 seçildi çünkü kaynak kodda hiçbir değişiklik
gerektirmiyor *(aşağıda ölçüldü)* ve bir kez yapmak, önce 7'ye sonra 8'e diye iki kez yapmaktan
ucuz.

## Ne değişmiyor — ve bu tahmin değil, bakıldı

- **Kaynak dosyalar.** Vite'ın göç kılavuzunun kendi cümlesi: *"Application source files require no
  changes. Breaking changes affect tooling and configuration only."*
- **`vite.config.js`, iki ön yüzde de.** Kullanılan ayarlar `base`, `build.outDir`, `plugins`,
  `server.proxy` ve `test` — kılavuz ilk dördü için *"remain unchanged"* diyor. Kırılan ayarlar
  (`build.rollupOptions` → `rolldownOptions`, `esbuild` → `oxc`, `optimizeDeps.esbuildOptions`)
  hiçbirinde geçmiyor.
- **Vitest 4'ün en büyük tuzağı geçerli değil.** Kılavuz, `@testing-library/react` kullananları
  otomatik cleanup'ın `globals`'a bağlı olması konusunda uyarıyor. `test-setup.js` bunu zaten kendi
  yorumunda yazmış: *"Testing Library only auto-cleans when vitest runs with globals; we keep
  globals off, so unmount between tests by hand."* Hiç güvenilmemiş bir davranış kırılamaz.
- **Snapshot yok.** İki ön yüzde de `toMatchSnapshot` / `toMatchInlineSnapshot` geçmiyor, yani
  `[MockFunction spy]` → `[MockFunction]` değişikliği ilgisiz.
- **`vi.restoreAllMocks` iki yerde** *(queen-agent: `useRoute.test.js`, `useFile.test.jsx`)*,
  **`vi.resetModules` queen-editor'de üç yerde**. İkisi de duruyor; 4'te daralan şey
  `restoreAllMocks`'un automock'lara uzanması, ve buralarda automock yok.

## Bu turun testleri

Yeni bir bekçi, aracının kendi test klasöründe:

- `queen-agent/backend/tests/test_frontend_toolchain.py` — **kırmızı**
- `queen-editor/backend/tests/test_frontend_toolchain.py` — **kırmızı**

Her biri kendi `frontend/package.json`'ını okur ve üç sürüm aralığını çiviler. Bugün `^5.4.0`,
`^4.3.1`, `^3.2.7` yazdığı için kırmızı; yükseltmeden sonra yeşil.

**Deseni `test_dist_is_committed.py`'den alıyor:** bir alt sistemi değil **repoyu** inceleyen,
ama `pytest` onu oradan topladığı için aracının test klasöründe duran Python testi. Hata mesajları
Türkçe, o dosyadaki gibi — bir test hatasını okuyan insandır.

**Neden bekçi gerekiyor:** bu bir karar, ve ev kararları teste çiviliyor — `MAX_ROUNDS == 16`,
varsayılan modelin Grok Build olması. Çivilenmeyen sürüm, birinin `npm install` sırasında sessizce
geri düşürebileceği bir sürümdür.

## Asıl güvenlik ağı, ve yazılmıyor

queen-agent'ta **568**, queen-editor'de kendi sayısı kadar mevcut ön yüz testi. Bu turda onlara
dokunulmuyor; uygulama turunda **hepsinin yeşil kalması** maddenin gerçek kanıtı. İki yeni bekçi
sürümün değiştiğini söylüyor, mevcut testler değişimin bir şeyi bozmadığını.

## Ayakta kalması gerekenler

`test_dist_is_committed.py`, iki taraftaki `test_static.py`, ve dört test komutunun tamamı.

## Bilerek yapılmayanlar

- **React 18 → 19.** İstenmedi, ve açıkla ilgisi yok. Ayrı iş.
- **`jsdom`, `@testing-library/*`.** Yükseltilmiyor; bir yükseltmede aynı anda değişen şeyi az
  tutmak, kırılan şeyi bulmayı ucuzlatıyor.
- **Bundle'ın kendisini doğrulayan bir test.** `test_dist_is_committed.py` bunu neden yapmadığını
  zaten yazmış: *"whether it was built from the source it sits next to cannot be asked cheaply or
  certainly."* Aynı sınır burada da geçerli.

## Doğrulama testlerin bittiği yerde bitmiyor

Vite 8 bundler motorunu değiştiriyor (Rollup+esbuild → Rolldown+Oxc), ve **testler kaynağı
doğruluyor, paketi değil**. Bütün testler yeşil olsa bile bundle'da bir gerileme yakalanmaz.

O yüzden uygulama turu iki ön yüzü de yeniden derleyip `dist`'i aynı commit'te işler *(CLAUDE.md)*,
ve gözle doğrulama şart:

- **queen-agent** — `python queen-agent/main.py` ile yerelde açılır
- **queen-editor** — yerel koşusu yok; Colab'da defteri **kullanıcı** çalıştırır *(kullanıcı 31
  Ağustos'ta bunu üstlendi)*

Ayrıca queen-editor'ün `node_modules`'ü bu cihazda henüz kurulmadı; uygulama turu oradaki
`npm install` ile başlar.
