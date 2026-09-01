# Test koşusu makineyi boğmaz · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-01-test-paralelligi-testler-design.md](2026-09-01-test-paralelligi-testler-design.md)
**Kırmızı commit:** `fa0de30` — 4 kırmızı, geri kalan yeşil.
**Dal:** `feat/test-paralelligi`.

## Ne yeşile dönecek

Dört kilit, iki satırla. Her `vite.config.js`'in `test` bloğu bir alan alır:

```js
maxWorkers: "50%",
```

`environment` ve `setupFiles`'ın yanına, aynı bloğa. Yeri orası çünkü bu bir koşu ayarı, derleme
ayarı değil — `base`, `build` ve `server` bloklarının hiçbiriyle ilgisi yok.

## Yorum ne söyleyecek

Sayının kendisi hiçbir şey anlatmıyor, ve *"neden yarısı"* koddan okunamaz — yani yorumun işi
tam olarak bu (CLAUDE.md: *bir yorum NEDEN'i söyler*).

Söyleyeceği üç şey var, ve üçü de ölçüm:

1. **Neden bir sınır var:** işçi başına bir jsdom, ve çekirdek başına bir işçi verilince otuz beş
   ortam aynı belleği bekliyor. Tek başına 99ms okuyan bir test kalabalıkta 5107ms okudu, ve zaman
   aşımı duvar saatini ölçtüğü için onu takılmış saydı.
2. **Neden yarısı:** ölçüldü — varsayılan 18-22s ve kırmızı, iki işçi 20.6s ve yeşil, yarısı 8.3s
   ile 9.5s ve iki kez yeşil.
3. **Neden oran:** sabit sayı bu makineyi düzeltip her makineyi bağlardı.

Yorum bu üçünü kısa tutar; uzun gerekçe spec'te durur ve yorum onu tekrarlamaz.

## Değişmeyen

`testTimeout` — varsayılan 5000ms yerinde kalıyor, ve koşu düzelince 99ms'lik test onun yakınından
geçmiyor. `base`, `build.outDir`, `plugins`, `server.proxy`, `test.environment`, `test.setupFiles`.
Hiçbir test dosyası. `dist` derlenmiyor: bu ayar yalnız test koşusunu ilgilendiriyor, üretilen
paketi değil.

## Nasıl görülecek

Dört komut da yeşil: 658, 720, **570**, **586** *(568 + 2 ve 584 + 2 kilit)*.

**Ama asıl kanıt sayıda değil, tekrarda.** Bu madde bir kararsızlığı kapatıyor, ve kararsızlık tek
bir yeşil koşuyla kapanmış sayılmaz — bugün üç kez yeşil koştuktan sonra kırmızıya düştü. O yüzden
queen-agent'ın ön yüz takımı **arka arkaya üç kez** koşulur, ve üçünde de yeşil olması aranır.

Yükseltmeden önceki hâlde arka arkaya üç yeşil hiç görülmemişti; görülürse fark ayara aittir.
