# Ön yüz vite 8 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-08-31-frontend-vite-8-testler-design.md](2026-08-31-frontend-vite-8-testler-design.md)
**Kırmızı commit:** `ea7c988` — 6 kırmızı, tabanlar yeşil *(568 + 584)*.
**Dal:** `feat/frontend-vite-8`.

## Ne yeşile dönecek

Altı bekçi, her araçta üç. Hepsi `package.json`'dan okuyor, yani yeşile dönmeleri için değişmesi
gereken tek şey o dosya — ama işin kendisi orada bitmiyor.

## Dört adım, iki araçta da aynı

### 1. `package.json` — üç satır

```
"@vitejs/plugin-react": "^6.0.0"
"vite": "^8.0.0"
"vitest": "^4.0.0"
```

`react`, `react-dom`, `jsdom`, `@testing-library/*` **ellenmiyor**. Bir yükseltmede aynı anda
değişen şeyi az tutmak, kırılanı bulmayı ucuzlatıyor.

### 2. `npm install` — kilit dosyası yenilenir

Ağaç baştan çözülüyor. queen-editor'e taban ölçümü için vite 5 kurulmuştu; oraya vite 8 iniyor ve
o kurulum amacını çoktan gördü.

### 3. Dört test komutu

Bekçiler yeşile döner, ve asıl soru şu olur: **568 + 584 ayakta mı.** Onlar bu maddenin kanıtı;
bekçiler yalnız sürümün değiştiğini söylüyor.

### 4. `dist` yeniden derlenir ve **aynı commit'te** işlenir

CLAUDE.md'nin kuralı: defter klonluyor, derlemiyor. Vite 8 farklı bundler kullandığı için çıktı
dosya adları değişiyor, ve `test_dist_is_committed.py` sayfanın istediği dosyaların commit'lendiğini
zaten kontrol ediyor — yani derleyip commit'lememek kırmızıya düşer.

## Kırılırsa muhtemelen buradan kırılır

**Vitest 4 ve `vite.config.js`'teki `test` bloğu.** Bugün `defineConfig` `vite`'tan içe aktarılıyor
ve `test` anahtarı onun içine yazılıyor. Vitest bunu uzun süredir `vitest/config`'ten alınmasını
önerdi. Kırılırsa çare bir satır: `import { defineConfig } from "vitest/config"`. Önden yapılmıyor
— çalışan bir şeyi ihtimal üzerine değiştirmek, kırmızının nereden geldiğini bulanıklaştırır.

**İkinci ihtimal `@vitejs/plugin-react` 6'nın JSX dönüşümü.** Babel'den oxc'ye geçiyor. 568 + 584
test tam olarak bunu yakalamak için orada.

Bunların dışında bir şey kırılırsa tasarıma dönülür; testler değişmez.

## Değişmeyen

`vite.config.js`'in ayarları *(`base`, `build.outDir`, `plugins`, `server.proxy`)* — göç kılavuzu
üçü için de *"remain unchanged"* diyor. Kaynak dosyalar. `test-setup.js`. React 18. Mevcut hiçbir
test.

## Nasıl görülecek

Dört komut da yeşil, ve `npm audit` iki ön yüzde de esbuild uyarısını artık vermiyor — maddenin
başladığı yer burasıydı.

**Ama testler yeterli değil, ve bu bilinçli bir sınır.** Bundler motoru değişiyor, testler kaynağı
doğruluyor. Bu yüzden:

- **queen-agent** — `python queen-agent/main.py`, tarayıcıda açılıp gezilir
- **queen-editor** — yerel koşusu yok; Colab'da defteri **kullanıcı** çalıştırır *(31 Ağustos'ta
  üstlendi)*. Bu doğrulama gelene kadar dal `main`'e alınmaz.

## Bilerek yapılmayanlar

`npm audit`'i çiviyen bir test. Zafiyet veritabanı zamanla değişiyor, yani böyle bir test bugünün
sessizliğini yarının gürültüsüyle kırmızıya çevirirdi. Sürümler çivili; denetim bir doğrulama adımı.

queen-editor'ün `requirements.txt`'indeki eksik `requests` — test turunda bulundu, kendi maddesini
bekliyor.
