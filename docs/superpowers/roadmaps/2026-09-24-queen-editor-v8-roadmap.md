# Queen Editor — Yol Haritası v8

**Tarih:** 2026-09-24 · **Koşu dalı:** `feat/queen-editor-v8` · **Durum:** 0/8
**Öncesi:** [v7](2026-09-21-queen-editor-v7-roadmap.md) — 24/24 kapandı; main'e henüz birleşmedi.
**Kaynak:** Maddelerin hepsi kullanıcının 24 Eylül'deki sözlerinden doğdu — *"There is a new version
(v2) of the queen-editor design, and I'd like you to build it into the app"* — ve kullanıcının
gösterdiği tasarımdan: `queen-design` deposu, `queen-design-v2` dalı, `fe48cc4`. Her madde
`projects/queen-editor/V2-UPDATE.md`'nin bir bölümünden geliyor; davranışta kararsız kalınan yerde
başvuru `proje-ekrani-tam/index.html`. Arayüz metni tasarımdan harfi harfine alınır *(kullanıcı —
"Take the interface text word for word from the design")*.

**Belge `feat/queen-editor-v7` dalında yazıldı** *(kullanıcı, 24 Eylül — "v7 ye yaz")*. Başlıktaki
dal koşunun dalı; yazıldığı yer başka.

**Tasarımın `Stands in for the app` bölümü kopyalanmaz** — orası sayfanın sunucuyu taklit ettiği
yerler. Sayfanın üstündeki kontrol şeridi *(galeri, kuyruk, havuz, üretici, model)* de tasarımın
kendi şalteri, uygulamanın parçası değil.

**V2-UPDATE'in 4. bölümü madde olmadı:** video panelinin Model kutusu modelin adını zaten her zaman
söylüyor — sunucu video satırına adı kurulu olsun olmasın yazıyor
*([list_producers.py:30](../../../queen-editor/backend/features/producers/domain/usecases/list_producers.py#L30))*.
Bölümün geri kalanı tasarımın şeridi.

**Koşulacak sıra bu dosyanın sırası.**

---

| # | İş | Bitti sayılır |
|---|---|---|
| v8-1 | `UNALIGNED` **Video panelinin iki sekmesi: `Kareden` · `Referanstan`.** *(V2-UPDATE §1.)* Panelin tepesinde, panel genişliğinde bir segment. Ortadaki `Üretim` satırı gidiyor. **Kareden** bugünkü kare formu, değişmeden. **Referanstan** yukarıdan aşağı: kurulum kartı *(video üreticisi eksikken)*, Model, **Referanslar**, **Prompt listesi**, Varyant, eksik satırı, `Kuyruğa ekle` ve altında cevap yuvası. Panel raydan açılınca Kareden'de başlıyor. Ses paneli değişmiyor. | — |
| v8-2 | `UNALIGNED` **Havuz ortada, kartların yerinde açılıyor.** *(V2-UPDATE §2.)* Soldaki sütun ve kapanmış hâli gidiyor; ekran iki parça: orta ve yan panel. Video paneli Referanstan'dayken orta galeri yerine havuzu gösteriyor, panel yanında açık kalıyor. Tek düğme, tek yer — sekmenin `Referanslar` bloğunda: `Referansları kapat` kartları geri getiriyor, `Referansları aç` havuzu yeniden açıyor. `Kareden`'e basmak ya da başka bir panel açmak kartları geri getiriyor; `Referanstan`'a basmak havuzu yeniden açıyor. | — |
| v8-3 | `UNALIGNED` **Havuzun sırası ne gösteriyor.** *(V2-UPDATE §3.)* Tip başına bir sıra, başlığında glif, ad ve sayı: `Fotoğraflar 3/9`, `Videolar 2/3`, `Sesler 1/3`. Her referans 144 × 108 bir kutu: sol üstte yuva numarası *(`<Picture N>`'in `N`'si)*, sağ üstte ×, altında dosya adı, klipse süresi *(`4,5 sn`)*. Son referansın ardından tek bir `+ Ekle` kartı, sıra dolana kadar. Boş havuz üç sırayı yalnız `Ekle` kartlarıyla gösteriyor; bugünkü boş hâl gidiyor. | — |
| v8-4 | `UNALIGNED` **Ekleme: sıranın kendi `Ekle` kartı.** *(V2-UPDATE §3.)* Kart yalnız o tipin seçicisini açıyor *(`image/*`, `video/*`, `audio/*`)*, tek dosya alıyor, sıranın sonuna ekliyor. Dosya yüklenirken o kart dönen işaretle `Yükleniyor…` diyor ve başka hiçbir `Ekle` kartı basılmıyor. Ret, havuzun tepesinde kırmızı bir kart; sonraki seçim ya da silme onu temizliyor. Yeni cümle, başka tipte bir dosya sıraya seçilince: `kisa-2.wav fotoğraf yuvasına giremez — bu dosya ses.` | — |
| v8-5 | `UNALIGNED` **Silme: × hemen siliyor.** *(V2-UPDATE §3.)* Pencere sormuyor. Ardındaki referanslar birer yer yukarı kayıyor, yani yuva numaraları değişiyor. Ekrana hiçbir boşluk ulaşmıyor. | — |
| v8-6 | `UNALIGNED` **Sıralama: galerinin kendi sürüklemesi, bir sıranın içinde.** *(V2-UPDATE §3.)* Taşınan kutu eğilip kalkıyor; imlecin altındaki kutu yerini kesikli bir vurgu yuvasına bırakıyor; bırakınca kutu oraya giriyor, sıranın gerisi kayıyor. Başka bir sıra ve `Ekle` kartı yer açmıyor. | — |
| v8-7 | `UNALIGNED` **Prompt listesi fotoğraf panelinin okuduğu gibi okunuyor.** *(V2-UPDATE §1.)* JSON dizisi ya da Python list/tuple, iki tırnakla da; önde isteğe bağlı `AD =`; boş öğeler düşüyor. Cümleleri fotoğraf panelininki: `Prompt listesi boş.` ve `Format hatası — liste okunamadı`. Düğmenin altındaki satır basınca ne doğacağını sayıyor: `2 prompt × 3 varyant = 6 kart`; kutu boşken satır boş. | — |
| v8-8 | `UNALIGNED` **Üretimi ne durduruyorsa basmadan söyleniyor.** *(V2-UPDATE §1.)* Düğmenin üstünde bir satır: video üreticisi kurulu ve H3 değilse `Referanstan üretim için H3 gerekiyor — bu oturumda başka bir video modeli kurulu.`; havuz boşsa `Havuzda referans yok — önce en az bir referans ekle.` Üretici kurulu değilken satır H3'ten söz etmiyor. Bir referans yetiyor. `Kuyruğa ekle` kapalı: istek yoldayken, üretici eksikken, eksik satırı bir şey söylerken, prompt kutusu boşken. Basınca sıra: varyant, prompt listesi, havuz. | — |
