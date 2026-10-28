# Test koşusu makineyi boğmaz · Tur 1 (test) — Tasarım

**Kaynak:** 1 Eylül'de vite 8 birleştirmesinden sonra görülen kararsızlık, ve kullanıcının sorusu:
*"neden uzun zamana ihtiyacımız var, hangi testler buna ihtiyaç duyuyor?"*
**Numarasız:** iki aracın ortak test yapılandırmasına dokunuyor.
**Dal:** `feat/test-paralelligi`.

## Sorun

queen-agent'ın ön yüz takımı kararsız: aynı kodla altı koşu, üçü kırmızı. Her kırmızı bir **zaman
aşımı**, hiçbiri iddia hatası değil, ve her seferinde farklı testler.

### İlk teşhis yanlıştı, ve kullanıcının sorusu onu düşürdü

Düşen testlerin yeşil koşularda 1.7–4.2 saniye sürdüğünü görüp *"testler ağır, 5 saniyelik sınıra
sığmıyor, sınırı yükseltelim"* dedim. Soru şuydu: **hangi test gerçekten 4 saniye sürüyor?**

Ölçüldü. `SkillPicker.test.jsx` tek başına koşturulduğunda o test **99 milisaniye**:

```
✓ with nothing selected the button says Skills and stays quiet  99ms
Duration 1.10s (transform 60ms, setup 113ms, import 58ms, tests 127ms, environment 645ms)
```

Aynı test tam takımda 4033ms, sonra 5107ms okuyor. **Test yavaşlamıyor — sıra bekliyor.**

## Gerçek sebep: aşırı paralellik

Makine 20 mantıksal çekirdek taşıyor ve vitest neredeyse hepsini işçi yapıyor. 35 test dosyasının
her biri kendi jsdom ortamını kuruyor *(tek dosyada bile `environment 645ms`)*, ve on dokuz tanesi
aynı anda bellek ile disk için yarışıyor. Test kendi 99ms'lik işini yapıyor; duvar saatinde beş
saniye geçiyor, ve `testTimeout` duvar saatini ölçüyor.

Ölçümler, hepsi aynı kodda:

| Ayar | İşçi | Duvar saati | `tests` | `import` | Sonuç |
|---|---|---|---|---|---|
| Varsayılan | ~19 | 18–22s | 94–113s | 38–58s | **2-3 kırmızı** |
| `maxWorkers=2` | 2 | 20.6s | 6.5s | 1.2s | 568 yeşil |
| `maxWorkers=50%` | 10 | **9.5s** | 14.3s | 4.0s | 568 yeşil |
| `maxWorkers=50%` | 10 | **8.3s** | 12.3s | 3.9s | 568 yeşil |

İşçiyi yarıya indirmek takımı **iki kat hızlandırdı**. Aşırı paralellik yalnız kararsızlık değil,
yavaşlık da üretiyor: on dokuz işçinin harcadığı iş on işçininkinin dört katı, ve bitirme süresi
daha uzun.

### Bunu da vite 8 yaratmadı

Vitest 3'te de aynı çekişme vardı — o koşunun `environment` toplamı 1023 saniyeydi, ve `SkillPicker`
4033ms okumuştu. Sınırın altında kalıyordu, o kadar. Vitest 4'ün havuzu yeniden yazması payı biraz
daraltmış olabilir, ama sebep yükseltme değil: **makineye kaldırabileceğinden fazla iş vermek.**

## Yol

İki `vite.config.js`'in `test` bloğu bir satır alır:

```js
maxWorkers: "50%",
```

### Neden yüzde, sabit sayı değil

Sabit bir sayı bu makineyi düzeltir ve her makineyi bağlar: 4 çekirdekli bir CI'da 10 işçi yine
aşırı olurdu, 64 çekirdekli birinde 10 işçi boşa bırakırdı. Yüzde, kuralı *"çekirdeklerin yarısı"*
olarak yazıyor — ölçtüğümüz şey de buydu.

### Neden yarısı

Ölçüldü: iki koşuda da yeşil ve en hızlı sonuç bu. `maxWorkers=2` de yeşildi ama 20.6 saniye
sürdü — kararsızlığı bitirmek için gereğinden fazla fren.

Sayının altında bir sebep de var: her işçi bir jsdom ortamı taşıyor, ve bu bellek işi — çekirdek
sayısı kadar iş parçacığı, bellek bant genişliği kadar iş yapamaz.

### Neden `testTimeout` değil

Sınırı 15 saniyeye çıkarmak kırmızıyı susturur ve sebebi bırakırdı: takım kararsız olmaktan çıkar
ama **yavaş kalırdı**, ve ilk fırsatta başka bir sınırı zorlardı. Zaman aşımının işi takılmış bir
testi yakalamak; 99ms'lik bir testin 5 saniye görünmesi zaman aşımının değil, koşunun sorunu.

## Bu turun testleri

Her ön yüzde bir kilit, `app.css.test.js`'in *"a lock, not a behaviour test"* deseninde:

- `queen-agent/frontend/src/viteConfig.test.js` — **kırmızı**
- `queen-editor/frontend/src/viteConfig.test.js` — **kırmızı**

İkisi de yapılandırmayı **içe aktarır** ve `test.maxWorkers`'ı okur. CSS kilitleri dosyayı metin
olarak okuyor çünkü jsdom stil yüklemiyor; bir JS yapılandırması için o gerekçe geçmiyor, ve içe
aktarım yürürlükteki değeri veriyor.

Her kilit iki şey söyler: sınır var, ve makineye göre ölçeklenen bir oran — çekirdeklerin tamamını
istemeyen bir değer.

## Ayakta kalması gerekenler

Dört test komutunun tamamı: 658, 720, 568, 584. `test_frontend_toolchain.py`'nin üç sürüm bekçisi.
`vite.config.js`'in öteki ayarları — `base`, `build.outDir`, `plugins`, `server.proxy`,
`test.environment`, `test.setupFiles`.

## Bilerek yapılmayanlar

- **`testTimeout`'a dokunmak.** Varsayılan 5000ms yerinde kalıyor. Koşu düzelince 99ms'lik bir test
  99ms sürüyor, ve sınırın yakınından geçmiyor.
- **Testleri hızlandırmak.** Zaten hızlılar; ölçüldü.
- **queen-editor'ü beklemek.** Orada kırmızı görülmedi *(584, dört koşuda da)*, ama yapılandırma
  aynı, dosya sayısı benzer, ve aynı makinede koşuyor. Payı bir araçta açıp ötekinde bırakmak iki
  aracın test kuralını sebepsiz ayırırdı.
- **Yüzdeyi ölçmeden değiştirmek.** %50 ölçüldü. %75 ölçülmedi ve daha hızlı olabilir; isteyen
  ölçer, ve o ayrı bir maddedir.
