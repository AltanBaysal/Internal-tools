# Madde 65 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-25-queenagent-m65-acilis-uygulama-design.md](../specs/2026-08-25-queenagent-m65-acilis-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Dosya

`queen-agent/frontend/src/App.jsx` — çatalın `navigate` çağrısı. Tek satır, artı bir yorum.
Başka kaynak dosyaya dokunulmaz. Ardından `queen-agent/frontend/dist` yeniden derlenir.

## Adımlar

**1. Çatalın hedefi değişir.**
Çatalın etkisi bugün `/p/<landing>` adresine `replace` ile gidiyor; `/p/<landing>/c/new` adresine
gidecek. `replace` ve etkinin koruması (`parsePath(window.location.pathname).view === "root"`)
aynen kalır — ikincisi tarayıcının o anki adresini soruyor ve bu maddenin konusu değil.

**2. Yorum, hedefi değil sebebi anlatır.**
Yeni satırın yanına: proje ekranının yazma kutusunda skill ve model seçici yok, o yüzden oraya
inen kullanıcı bir mesaj göndermeden seçicilere ulaşamıyor. Taslak ekranı ikisini de taşıyor.
Adresin ne olduğu koddan zaten okunuyor; yorumun söyleyeceği şey neden orası olduğu.

**3. Ön yüz suite'i koşulur.** Beş kırmızının yeşile döndüğü görülür.

**4. Arka uç suite'i koşulur.** 384 yeşil; değişmediği doğrulanır.

**5. `dist` derlenir.**
`npm run build --prefix queen-agent/frontend`. Derlenmiş çıktı kaynağıyla **aynı commit'e** girer.

**6. Commit.** `App.jsx`, `dist`, bu plan ve uygulama tasarımı birlikte.

## Beklenen yeşil

`npm test --prefix queen-agent/frontend` → 476 yeşil (bugün 471 + kırmızı beş).
`python -m pytest queen-agent -q` → 384 yeşil, değişmeden.

Yeşil kalması gereken iki gerileme kalkanı: **proje yokken `/`'da kalınması** ve **çatalın geçmişe
yazılmaması.** Bu maddenin sessizce kırabileceği şeyler bunlar.

## Turda çıkan: on test açılışa yaslanıyormuş

Kod değişince beş kırmızı yeşile döndü ama **on test kırıldı** — proje silme ve menü testleri, artı
ayarlar testi. Hiçbiri silme davranışı bozulduğu için değil: hepsi `render(<App />)`'in ardından
`/p/p1`'e inilmesini bekliyordu, ve çatal artık oraya inmiyor.

Düzeltme, konularını korumak: dokuzu artık proje adresine kendisi giderek başlıyor
(`pushState("/p/p1")`), ayarlar testi de çizilen ekranı taslak sohbetin başlığından bekliyor. Hiçbir
iddia zayıflatılmadı; yalnız testin başlangıç ekranı, konusunun gerektirdiği ekran oldu.

**Bu, test turunun kaçırdığı bir şeydi.** Test planı yalnız açılışı doğrudan iddia eden testleri
saymıştı; açılışı bir *önkoşul* olarak kullanan testler görülmemişti. Doğrusu, bu on uyarlamanın da
kırmızı commit'te olmasıydı.

## Bu turda yapılmayan

Proje ekranının yazma kutusuna seçici eklenmez · "+ New chat" düğmesine dokunulmaz · proje yokken
açılış değişmez · arka uçta hiçbir şey.
