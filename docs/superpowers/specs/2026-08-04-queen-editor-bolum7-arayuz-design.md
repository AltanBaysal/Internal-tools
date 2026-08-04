# Queen Editor — Bölüm 7: Arayüz tasarımla birebir + akıcı

**Tarih:** 2026-08-04 · **Durum:** denetim tamamlandı, envanter kapalı — onay bekliyor
**Yol haritası:** [2026-08-03-queen-editor-v2-roadmap.md](../plans/2026-08-03-queen-editor-v2-roadmap.md) — Bölüm 7
**Şemsiye tasarım:** [2026-08-03-queen-editor-v2-design.md](2026-08-03-queen-editor-v2-design.md)
**Tasarım kaynağı:** claude.ai/design → `Queen Editor Basit v1.html` (+ `simple-screens.jsx`,
`styles.css`, `HANDOFF.md`) — repo'ya kopyalanmaz, linkten taze çekilir:
<https://claude.ai/design/p/efad1f83-69d3-4e07-89fa-3783839c81c3>

Bu bölüm **yeni özellik getirmez.** Var olan her ekranı tasarımdaki hâline çeker ve her beklemeye
ekranda bir karşılık verir. Ölçüt tek cümle: *kullanıcı bir şey bekliyorsa ekran bunu söylüyor
olmalı; bir eleman tasarımdan farklıysa fark bilinçli olmalı.*

## Kapsam dışı

- Küçük resim (thumbnail) üretimi — fotoğraflar tam boy servis edilmeye devam eder.
- Yeni ekran, yeni endpoint, yeni veri dosyası.
- Duraklat / Devam et / İptal et ayrımı (Bölüm 13) — burada Durdur hâlâ "bitir"dir, sadece
  gerçekten ve hemen biter.
- Export butonu (Bölüm 10), kart/proje çöp butonları ve onay modalları (Bölüm 12), sıra rozeti ve
  tutamak (Bölüm 9), foto detay sayfası (Bölüm 11). Envanterde görünürler, bu bölümde yapılmazlar.
- **Model dropdown (Bölüm 15)** ve **hatalı kare "Tekrar dene" (Bölüm 14)** — tasarımda var,
  bizde yok; ikisi de özellik niteliğinde (ilki backend'de model kavramı, ikincisi tekil üretim
  endpoint'i ister) ve yol haritasında evleri zaten var. Envanterde görünürler, burada yapılmazlar.
- **"Bekliyor" yer tutucuları ve prompt format-hatası deseni (Bölüm 13)** — yol haritası ikisini
  açıkça Bölüm 13'e ("üretim akışı") vermiş; B7 var olanı tasarıma çeker, yeni durum eklemez.
- Izgara ve panel genişlikleri **sabit kalır** (proje 4 sütun, galeri 5 sütun, panel 320px).
  Karar: tasarım tek genişlikte çizilmiş, artboard'la birebir kalmak tercih edildi.

## Kaynak durumu — kapalı

Tasarım kaynağının tamamı DesignSync ile çekilip `queen-editor/design/` altına kondu ve
üç bağımsız geçişli denetim koştu: **A** tasarımdan koda, **B** koddan tasarıma, **C** durum/tepki
yürüyüşü (metodoloji: [inceleme planı](../plans/2026-08-04-queen-editor-bolum7-inceleme-plani.md)).
Sonuç: 38 birleşik bulgu, **0 çelişki** — aşağıdaki envanter ve maddeler bu denetimin çıktısıdır,
`? tasarımdan doğrula` satırı kalmadı.

---

## 1. Eleman envanteri

### A · Projeler ekranı (`ProjectsScreen.jsx`)

| Eleman | Tasarımda | Bizde | Yapılacak |
|---|---|---|---|
| App bar (Queen Editor · Projeler · ＋Yeni proje) | aynı | aynı | — |
| App bar'ın kaydırmadaki davranışı | sayfayla kayar (tasarım sticky vermiyor) | sayfayla kayar | — |
| Yüklenirken | — | `return null` → boş ekran | ortalanmış spinner (§2) |
| Boş durum metni | aynı | aynı | — |
| Boş durumda **"İlk projeyi oluştur"** butonu | var (`Btn hl` + Plus) | yok | eklenecek |
| Boş durum ölçüleri | gap 8, alan ~%70 | gap 10, `60vh` | hizalama paketi (§7) |
| Hata durumu | durum hatası kalıbı | serbest yerleşim + iç içe kutu | §4 desenine + **Tekrar dene** |
| Kart ızgarası | 4 sütun | 4 sütun | — |
| Proje kartı (ad + tarih) | aynı | aynı | — |
| Kartta çöp butonu | var | yok | **Bölüm 12** (kart bu bölümde `position:relative` alır — zemin hazırlığı) |
| Kartın klavyeyle açılması | tasarımda da düz `div` | `div onClick` | buton semantiği — tasarım-ötesi bilinçli iyileştirme |

### B · Yeni proje kutusu (`NewProjectModal.jsx`)

Desen doğru: hata deseni (kırmızı çerçeve + tek satır) ve meşgul geri bildirimi ("Oluşturuluyor…"
+ pasif buton) diğer ekranların örneğidir. İki düzeltme çıktı:

- **İstek uçarken Esc/scrim kapatmaz** — bugün Vazgeç pasif ama Esc/scrim `onCancel`'ı çağırıyor;
  istek sunucuda sürüyor, proje yine oluşuyor. İptal görüntüsü varsa iptal olmalı; olamıyorsa
  kapanmamalı. Boştayken Esc/scrim kapatması kalır.
- **Uyarı görünürken Oluştur pasif** — HANDOFF: "uyarı varken Oluştur pasif kalır"; bugün ad dolu
  + hata görünürken buton aktif.

### C · Proje ekranı (`ProjectScreen.jsx`)

| Eleman | Tasarımda | Bizde | Yapılacak |
|---|---|---|---|
| App bar sol/orta | aynı | aynı | — |
| **Projeden çık** | nötr `Btn ghost` (HANDOFF: "kırmızı silmeye ayrıldı") | `color: var(--danger)` | nötre çekilecek |
| Projeden çık onayı (03a) | var | yok — direkt `navigate("/")` | **Bölüm 12** |
| Export butonu | var | yok | **Bölüm 10** |
| Galeri sol + 320px panel sağ | aynı | aynı | — |
| Ayarlar yüklenirken | — | `return null` → **beyaz ekran** | app bar + spinner (§2) |
| Ayarlar hatasında toparlanma | — | hata panelde ama tek çare F5 | **Tekrar dene** (§2) |

### D · Üretim paneli (`GeneratePanel.jsx`)

| Eleman | Tasarımda | Bizde | Yapılacak |
|---|---|---|---|
| Model dropdown | var ("MODEL" + "SDXL 1.0 ▾") | yok | **Bölüm 15** |
| Prompt listesi · negatif · varyant | aynı | aynı | — |
| Prompt kutusu placeholder'ı | yok | JSON biçim örneği | **bilinçli sapma, kalır** — biçimi öğreten tek yer |
| Varyant üst sınırı | HANDOFF "üst sınır yok" | `max=26` | **bilinçli sapma, kalır** — backend gerçeği a–z (`start_batch.py`), 27'de sunucu hatası yerine kutu sınırı |
| Üret butonu (accent, tam genişlik, ✦) | aynı | aynı | — |
| "12 prompt × 4 varyant = 48 foto" önizlemesi | aynı; **bitti kartıyla aynı anda durmaz** | done'da da görünüyor | done'da gizlenecek |
| Prompt format hatası | alan hatası deseni: textarea `--danger` çerçeve + altında "Format hatası", yazınca temizlenir | genel `{error}` satırı, textarea kızarmıyor | **Bölüm 13** (yol haritası açıkça orada) |
| Üretim sürerken panel | kilitli ve soluk (`wf-panel--locked`) | alanlar serbest | eklenecek (§2, §6) |
| İstek hatası | durum hatası kartı | çıplak kırmızı yazı | §4 |
| "Üretim durdu" kartı | danger çerçeve **+ danger zemin**, ham metin düz `Mono 10`, padding `8px 10px` | zemin yok, ham metin iç içe kutuda, padding 12 | §4 |
| Bitiş | yeşil kart: `wf-stroke` + `--ok` çerçeve + `--ok-bg` zemin, ✓ "48 / 48 üretildi — tamamlandı" | tek satır "bitti — 4/4" | eklenecek (§6) |
| Durduruldu | **nötr** `wf-stroke` kart ("Üretim duraklatıldı — 7/48") — danger yalnız kendiliğinden duruşta | tek satır mono | §4 — nötr kart |
| Başka projede üretim uyarısı | tasarımda çizilmemiş | "Üretim sürüyor: {proje} — bitmesini bekle." | **bilinçli sapma, kalır** — tek-worker/409 gerçeğinin UI'ı; metin onaylandı |

### E · İlerleme kartı (`ProgressPanel.jsx`)

| Eleman | Tasarımda | Bizde | Yapılacak |
|---|---|---|---|
| Sayaç · ilerleme çubuğu · "şimdi: …" | aynı | aynı | — |
| Kart padding'i | `8px 10px` | 12 | hizalama paketi (§7) |
| **Durdur** | kartın **üstünde**, tam genişlik (`padding: 10px 12px`, `fontSize: 14`, `color: var(--ink-2)`) | kart başlığında `Btn sm` | taşınacak |
| Durdur'a basınca | — | hiçbir görsel değişiklik | §3 |
| "N fotoğraf üretilemedi" satırı | var (`Note 12` danger, "— diğerleri devam ediyor") | birebir aynı | — |

### F · Galeri (`Gallery.jsx`)

| Eleman | Tasarımda | Bizde | Yapılacak |
|---|---|---|---|
| 5 sütunlu ızgara | `alignItems: start` | hizalama yok | eklenecek |
| Kare + dosya adı | aynı (`borderRadius: var(--r-sm)`) | `borderRadius: 3` elle | hizalama paketi (§7) |
| Üretilen kare (`ImgPH loading`) | aynı | aynı | — |
| Kuyruktaki kareler | soluk kesikli **"bekliyor"** yer tutucuları | yok — yalnız o anki spinner karesi | **Bölüm 13** (yol haritası açıkça orada) |
| Hatalı kare + "Tekrar dene" | var | yok | **Bölüm 14** |
| Fotoğraflar yüklenirken | — | **"henüz fotoğraf yok" yazıyor** | spinner (§2) |
| Kareye tıklayınca | detay sayfası | yeni sekmede ham dosya | **Bölüm 11** — yalnız `Gallery.jsx:49`'daki "tasarımın jesti" yorumu düzeltilir (yanlış iddia) |
| Sıra rozeti + tutamak | var | yok | **Bölüm 9** |

---

## 2. Geri bildirim

**Kural:** bir istek uçuşta olduğu sürece ekranda o isteğe ait bir işaret bulunur; hiçbir ekran
boş dönmez ve hiçbir ekran bilmediği şeyi söylemez.

Denetimin bulduğu dokuz düzeltme:

1. `ProjectsScreen` — `status === "loading"` iken `null`. Yerine ortalanmış `wf-spinner`.
2. `App.jsx / ProjectRoute` — ayarlar yüklenirken `null`, yani beyaz ekran. Yerine app bar +
   gövde ortasında `wf-spinner` (`ProjectLoading`).
3. `Gallery` — `useGeneration` fotoğrafları `[]` ile başlatıyor ve "yükleniyor" diye bir durumu
   yok, dolayısıyla dolu bir projeye girildiğinde ilk saniyelerde galeri **"henüz fotoğraf yok"**
   yazıyor. `useGeneration` bir yükleniyor durumu taşıyacak; galeri "boş" ile "daha bilmiyorum"u
   ayıracak ve ikincisinde ortalanmış `wf-spinner` gösterecek.
4. `GeneratePanel` — Üret'e basıldıktan sonra ayarlar kaydedilip üretim başlatılana kadar buton
   aktif ve değişmemiş kalıyor; ikinci tık 409 yiyor ve o 409 koşarken gizli kalıp batch bitince
   "bitti" özetinin yanında **bayat hata** olarak beliriyor. Buton `NewProjectModal`'daki gibi
   istek uçuştayken pasifleşip metnini değiştirecek.
5. `GeneratePanel` — üretim sürerken üç alan da yazılabilir durumda. Panel `wf-panel--locked`
   alacak (kural §6'daki vendor tazelemesiyle gelir), alanlar `disabled` olacak; galeri serbest.
6. `useGeneration` — **poll zinciri tek hatada ölüyor ve dirilmiyor**: `getStatus` bir kez
   başarısız olursa `catch` yeni timer kurmuyor; üstelik hata notu yalnız `!running` dalında
   render edildiğinden üretim sürerken görünmüyor — donmuş "sahte canlı" ilerleme çubuğu, tek
   çare F5. Timer her sonuçta yeniden kurulacak; hata `running` iken de görünecek; başarılı bir
   yoklama hatayı temizleyecek.
7. **done/stopped/error durumu projeler arasına sızıyor** — `summary` ve "Üretim durdu" kartı
   `job.project` kontrol etmiyor (yalnız `running` proje-bazlı süzülüyor); A projesinin batch'i
   bitince B projesine giren kullanıcı B'nin panelinde A'nın kartını görüyor, F5 de temizlemiyor.
   Özet ve hata kartı da projeye süzülecek.
8. `App.jsx` — ayarlar hatasında toparlanma yolu yok (ekran `EMPTY_SETTINGS` ile açılıyor, tek
   çare F5); `ProjectsScreen` yükleme hatasında da öyle. İki yere de **Tekrar dene** (§4 kartının
   içinde).
9. Sunucu/tünel boştayken ölürse: `refreshPhotos` poll zincirinin `.then`'inde olduğu için hiç
   çağrılmıyor → galeri yanlış "henüz fotoğraf yok" diyor; tünel tamamen ölünce de mesaj İngilizce
   `Failed to fetch` kalıyor. Foto listesi durumdan bağımsız istenecek; ulaşılamama hâli tek
   Türkçe cümleyle anlatılıp ham hata `Mono` satırında verilecek (sebep uydurma yok — FOUNDATION).

Yükleme göstergesi tasarımın kendi aracıdır (`wf-spinner` — üretimdeki "Çalışıyor" karesiyle
aynı), yeni bir görsel dil icat edilmez. (İlk sürümdeki kesikli iskelet kartlar kullanıcı
kararıyla spinner'a çevrildi, 2026-08-05.)

## 3. Durdur gerçekten durur

Bugün Durdur yalnız bir bayrak kaldırıyor; süren kare sonuna kadar render ediliyor (dakikalarca)
ve `/api/stop`'un döndürdüğü durum hâlâ `running` olduğu için **ekranda tek piksel değişmiyor** —
buton basılabilir de kalıyor. İki düzeltme:

- **Görsel:** basıldığı an buton pasifleşir ve "Durduruluyor…" der; üretim gerçekten bitene kadar
  öyle kalır.
- **Gerçek:** `/api/stop` bayrağı kaldırmanın yanında ComfyUI'ın `/interrupt` ucunu çağırır, süren
  render kesilir. `client.wait` `/history`'yi 5 saniyede bir yokladığı için "anında" pratikte
  birkaç saniyedir; bu kabul edilir.

**Yarım kare kaydedilmez** — `store.save` yalnız tam veri geldiğinde çağrılır, dolayısıyla
`photos.jsonl`'a satır da düşmez. Karenin numarası `plan.json`'da ayrılmış kalır ve `next_number`
onu atlar; bu Bölüm 6'nın kasıtlı davranışıdır, değişmez.

**Kritik kural — iptal bir hata değildir.** `/interrupt` sonrası `client.wait` prompt'u
`/history`'de başarısız görür ve bugünkü kod bunu `except` bloğuna sokar: `failed += 1`,
`consecutive += 1`. Bu hâliyle üst üste durdurma `policy.stop_reason` üzerinden ekrana
**"Üst üste 3 render başarısız — üretim durduruldu"** kırmızı hata kartı olarak çıkabilir —
kullanıcının kendi isteğini sistem arızası gibi gösterir. Kullanıcının isteğiyle kesilen kare
`failed` sayılmaz, `consecutive`'i artırmaz ve toplu sonucu `error` yapmaz; toplu sonuç
`stopped` olur.

## 4. Hata gösterimi — iki desen, üçüncüsü yok

Tasarımın iki hata biçimi var. Her hata bunlardan biridir.

**Alan hatası** — hatanın kaynağı belli bir kutuysa: kutunun çerçevesi `var(--danger)` olur,
hemen altında tek satır kırmızı `Note size={12}` çıkar. Örnekler: `NewProjectModal` (bugün doğru)
ve prompt format hatası (bağlanacak — §1D).

**Durum hatası** — hata bir alana değil ekranın durumuna aitse: `wf-stroke` kart,
`borderColor: var(--danger)` **ve** `background: var(--danger-bg)`, içinde `Icon.Warn` + tek
cümlelik açıklama, altında sunucunun kendi metni düz `Mono size={10}` satırı olarak — **iç içe
kutu yok.**

Ham metin her zaman sunucudan geldiği gibi basılır; sebep uydurulmaz (FOUNDATION).

Değişecek yerler:

| Yer | Bugün | Olacak |
|---|---|---|
| `GeneratePanel` istek hatası | çıplak kırmızı yazı | durum hatası kartı |
| `GeneratePanel` "Üretim durdu" | zemin yok, ham metin iç içe kutuda | zemin var, ham metin düz satır |
| `GeneratePanel` "durduruldu" özeti | tek satır mono | **nötr** durum kartı — tasarım doğruladı (04a): kullanıcının kendi isteği hata değildir, danger yalnız kendiliğinden duruşta (06) |
| `GeneratePanel` format hatası | genel hata satırı | alan hatası: textarea kızarır + "Format hatası", yazınca temizlenir |
| `ProjectsScreen` yükleme hatası | serbest yerleşim + iç içe kutu | durum hatası kartı + Tekrar dene |
| `App.jsx` ayarlar hatası | pasif hata notu | durum hatası kartı + Tekrar dene |
| `NewProjectModal` | — | desen değişmez (yalnız §1B'deki iki davranış düzeltmesi) |

Ayrıca: `summary` · `busyElsewhere` · `error` · hata kartı bugün bağımsız koşullarla **aynı anda**
görünebiliyor — aynı olay iki kez anlatılıyor. Aynı anda en fazla bir durum/hata mesajı gösterilir.

### Bağlantı kopması — bayat "üretiliyor" durumu (eklendi 2026-08-05)

Colab tamamen kapatıldığında ekran donuk bir "üretiliyor" çubuğunda kalıyor ve kırmızı kart hiç
gelmiyordu. Kök neden: `fetch`'in zaman aşımı yok; ölü tünelde Cloudflare ucu isteği dakikalarca
bekletebiliyor, istek **başarısız olmuyor, cevapsız bekliyor** — poll'un catch'i hiç tetiklenmiyor.
Kural ihlali: "hiçbir ekran bilmediği şeyi söylemez" — donuk çubuk tek başına "üretiliyor" iddiasıdır.

İki parça, ikisi de mevcut durum-hatası desenini kullanır (üçüncü desen doğmaz):

1. **Zaman aşımı** — `api.js`'teki her istek 10 sn'lik zaman aşımı taşır (`AbortController`).
   Süresi dolan istek mevcut "Sunucuya ulaşılamadı" hata kalıbına dönüşür; askıda istek en geç
   10 sn'de görünür hataya çevrilir.
2. **Bayat running görünümü** — üretim görünürken (`running` dalı) poll hatası varsa ilerleme
   kartı **soluklaşır** ve altındaki durum-hatası kartının başlığı son bilinen ilerlemeyi taşır:
   "Sunucuya ulaşılamıyor — son bilinen: X/Y". Alanlar kilitli kalır (sunucu yaşıyor olabilir,
   yazdırmak riskli), poll denemeye devam eder; ilk başarılı cevapta ekran kendini düzeltir.

## 5. Hız

İki ayrı problem, iki ayrı çözüm:

**İlk açılış** — 48 fotoğrafın tamamı aynı anda isteniyor. `<img>` elemanları `loading="lazy"` ve
`decoding="async"` alır; ekranda görünmeyen kareler istenmez.

**Sonraki açılışlar** — `serve_photo` hiçbir cache başlığı vermiyor, dolayısıyla her yenilemede
tarayıcı 48 dosyanın hepsini tünel üzerinden tekrar soruyor (304 dönse bile gidiş-dönüş yapılıyor).
Fotoğraf dosyaları değişmez: `next_number` bir numarayı asla ikinci kez kullanmaz, yani `0_a.png`
her zaman aynı dosyadır. Bu yüzden `/photos/...` uzun ömürlü ve `immutable` bir cache başlığıyla
servis edilir; yenilemede tarayıcı hiç sormaz.

Küçük resim üretimi kapsam dışı — bu iki madde ölçülür, yetmezse ayrı bir iş olarak konuşulur.

## 6. Yeni CSS nereye yazılır — karar verildi

Denetim §6'nın sorusunu kapattı: `--ok` / `--ok-bg` token'ları **ve** `.wf-panel--locked` kuralı
tasarımın `styles.css`'inde var (`design/styles.css`); vendor kopyamız tasarımın bir gün gerisinde
(`.wf-scrim`'in `z-index: 20`'si de eksik). Doğru iş birinci şık:

**`vendor/styles.css` bütünüyle `design/styles.css`'ten tazelenir** — tek dosya, tek commit.
`app.css`'e yeni tanım yazılmaz; `app.css`'teki mevcut `.wf-scrim { position: fixed }` düzeltmesi
(artboard-çerçevesi farkı) olduğu gibi kalır.

## 7. Küçük hizalama paketi

Tek commit'lik kırıntılar, hepsi tasarım değeriyle birebir: boş-durum `gap 10→8` ve alan ölçüsü;
galeri grid'ine `alignItems: start`; `<img>` çerçevesi `borderRadius: 3 → var(--r-sm)`; ilerleme
kartı `padding: 12 → "8px 10px"`; proje kartına `position: relative` (Bölüm 12'nin çöp butonuna
zemin); `Gallery.jsx:49`'daki yanlış yorumun düzeltilmesi (yeni-sekme davranışını tasarıma
dayandırıyor; tasarım detay sayfası çiziyor — davranış Bölüm 11'e kadar kalır, iddia kalkar).

---

## Doğrulama

Otomatik (pytest, ucuz ve hedefli):

1. Kullanıcı isteğiyle kesilen kare `failed` sayılmaz, `consecutive`'i artırmaz ve toplu sonuç
   `stopped` olur — art arda üç durdurma `error` üretmez.
2. `/api/stop` ComfyUI'ın `/interrupt` ucunu çağırır; hiçbir üretim sürmüyorken çağırmak
   zararsızdır.
3. `/photos/...` yanıtı uzun ömürlü ve `immutable` bir cache başlığı taşır.

Elle (Colab, tek turda hepsi):

4. 48 fotoğraflı projeye gir → galeri **hiçbir an** "henüz fotoğraf yok" demez; spinner görünür,
   sonra fotoğraflar dolar.
5. Sayfayı yenile → fotoğraflar gözle görülür şekilde daha hızlı gelir (tarayıcı önbelleği).
6. Üret'e bas → buton anında pasifleşir; panel alanları kilitlenir ve solar.
7. Durdur'a bas → buton anında "Durduruluyor…" olur, üretim birkaç saniye içinde biter;
   yarım kare galeriye düşmez.
8. Üretim bitince yeşil "✓ N / N üretildi — tamamlandı" kartı çıkar, "N × M" önizleme satırı
   gizlenir; kart yeni Üret'e kadar kalır.
9. Üretim sürerken tüneli birkaç saniye kes-aç → ilerleme çubuğu donmaz, hata görünür ve
   bağlantı dönünce kendiliğinden temizlenir.
10. A projesinde üretim bitmişken B projesine gir → B'nin panelinde A'nın "bitti"/hata kartı
    görünmez.
11. Sunucuyu durdur → projeler ekranındaki ve paneldeki hata **aynı biçimde** görünür
    (kırmızı zeminli kart + ikon + tek cümle + küçük teknik satır) ve **Tekrar dene** çalışır;
    aynı anda iki kırmızı çıkmaz.
12. Yeni proje penceresinde istek uçarken Esc/scrim'e bas → pencere kapanmaz; hata görünürken
    Oluştur pasiftir.
13. Boş projeler ekranında "İlk projeyi oluştur" butonu görünür ve çalışır.
14. Projeden çık nötr renktedir.

## Kararlar (denetim + kullanıcı onayı, 2026-08-04)

- **Varyant `max=26` kalır** — backend gerçeği (a–z adlandırması); HANDOFF'un "üst sınır yok"
  cümlesinden bilinçli sapma.
- **Model dropdown ve hatalı-kare "Tekrar dene" sonraki bölümlere** — yol haritasında evleri
  zaten varmış: Bölüm 15 (çoklu model) ve Bölüm 14 (sağlamlık); B7 yeni özellik getirmez.
- **"Bekliyor" kareleri ve format-hatası deseni Bölüm 13'te** — yol haritası açıkça atamış;
  spec'in eski "yeni satır B7 kapsamındadır" kuralına karşı yol haritası kazanır (tek kaynak).
- **Prompt placeholder'ı ve `busyElsewhere` notu kalır** — tasarımda olmayan iki bilinçli sapma;
  "Üretim sürüyor: {proje} — bitmesini bekle." metni onaylandı.
- **`vendor/styles.css` tasarımdan tazelenir** (§6).
- Denetim ayrıntıları (38 bulgu, kova ayrımı, kanıt satırları) oturum scratchpad'indeki
  `kova-tablosu.md`'de üretildi; kalıcı özeti bu spec'tir.
- **10 sn istek zaman aşımı + bayat-running soluklaştırma** (§4, 2026-08-05) — Colab testinde
  bulunan donuk-çubuk hatasının düzeltmesi; kullanıcı A yaklaşımını onayladı.
- **"Durduruldu" kartı Colab'da doğrulandı** (2026-08-05) — durdurunca Üret'in altında görünüyor;
  önceki "görünmüyor" gözlemi kapandı, değişiklik yok.
- **Frontend test altyapısı ayrı bölüm** (2026-08-05) — bağlantı düzeltmesi testsiz gider;
  vitest kurulumu yol haritasına **Bölüm 8** olarak, hemen sıraya eklendi (kullanıcı kararı:
  "yol boyunca kullanabilelim"); eski Bölüm 8-14 → 9-15 kaydı. Bu spec'teki bölüm numaraları
  kaymış hâli gösterir.
