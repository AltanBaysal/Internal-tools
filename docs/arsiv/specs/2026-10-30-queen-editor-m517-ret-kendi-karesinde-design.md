# Madde 517 · Bir reddin cümlesi kalır, bir cevap kendi karesinde iş görür — tasarım

**Tarih:** 30 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-16),
517 · v11-16 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-30-queen-editor-m517-ret-kendi-karesinde-plan.md](../plans/2026-10-30-queen-editor-m517-ret-kendi-karesinde-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Kare sayfasında bir basış reddedilince kart sunucunun cümlesini gösteriyor, ve cümle sıra çalışırken de
silinmiyor. Ret geç gelirse ve kullanıcı o arada başka kareye geçtiyse, kart yalnız basışın yapıldığı
karede görünüyor.

Kullanıcı — *"bu hatalarıda çöz istersen"*. Madde BACKLOG'un iki işini birleştiriyor: *"Sıra çalışırken
bir reddin sunucu cümlesi bir saniyede kayboluyor"* (516'nın QA'sı) ve *"Kare sayfasında geç gelen bir
ret başka karede görünüyor"* (510'un reviewer'ı). CLAUDE.md: bir hata mesajı servisin gerçekten
söylediğini basar.

Koşu sırasında maddeye eklendi (ana ajan, 30 Ekim — aynı fonksiyonlar, aynı madde, "kendi karesinde"):
geç gelen bir **başarı** da açık karede bir şey yapmaz. Kare silme kullanıcıyı durduğu yerden
götürmez, katman silme ve Kuyruktan çıkar açık karenin sekmesini değiştirmez, Yeniden üret yanlış
karede "Kuyruğa eklendi" demez. Galeri bugünkü gibi yeniden okunur.

## Bugün

Kare sayfasının (`PhotoDetail`) beş basışı reddedilebiliyor, ve ret üç ayrı durumda tutuluyor:

| Basış | Durum | Kartın cümlesi nereden |
|---|---|---|
| Yeniden üret | `refusedAct` (başlık) | `raw={error}` — ortak hook'un `error`'ü |
| Katmanı sil | `refusedAct` | `raw={error}` |
| Kuyruktan çıkar (bekleyen katman, 516) | `refusedAct` | `raw={error}` |
| Sil / Kuyruktan çıkar / Kareyi sil (kare) | `refused` (bayrak; başlık çizimde `produced`'tan) | `raw={error}` |
| Sesi kapat / aç | `muteRefused` (`{ text, raw }`) | kendi `raw`'ı |

İki hata buradan çıkıyor:

- **Cümle siliniyor.** `useGeneration`'ın `error`'ü yoklamanın da hatası: başarılı her yoklama
  `setError(null)` yapıyor. Sıra çalışırken yoklama 2 sn'de bir geldiği için ilk dört kartın cümlesi en
  geç 2 sn'de gidiyor, yalnız başlık kalıyor. Sıra boşken yoklama zinciri durduğu için görünmüyordu.
  Sesin kartı kendi cümlesini tuttuğu için bundan etkilenmiyor.
- **Ret başka karede çıkıyor.** Oklar kareyi sayfayı sökmeden değiştiriyor; `fid` değişince bir efekt üç
  durumu da temizliyor. Ama basışın cevabı efektten sonra gelirse durumu yeniden kuruyor, ve durum
  hangi karenin olduğunu bilmediği için kart o an açık olan karede çiziliyor. Beş basışın beşi de böyle.
- **Başarı da başka karede iş yapıyor.** Aynı yoldan: geç gelen başarıda kare silme basılan karenin
  komşusuna götürüyor (`navigate(after)`), katman silme ve Kuyruktan çıkar açık karede Foto sekmesine
  döndürüyor (`setOpen("photo")`), Yeniden üret açık karenin `sent`'ine yazıyor. Cevap ne olursa olsun
  `setBusy(false)` ve `setAsking(null)` da açık karede çalışıyor: o karede kendi basışı yoldaysa
  düğmeleri yeniden açılıyor, "Siliniyor…" penceresi kapanıyor.

## Ne yapılır

Yalnız ekran; sunucu değişmez.

### Hook (`useGeneration`) — ret, cümlesiyle döner

`regenerate`, `removeLayer`, `dequeueLayer` ve `removePhotos` bugün reddedilince `null`'la dönüyor.
Artık `{ error: <sunucunun cümlesi> }` ile dönerler — `generate`'in reddinin 497'den beri taşıdığı biçim
(`GeneratePanel` onu böyle okuyor). `failureText(err)`: ilk satır sunucunun cümlesi, ardından kanıt.

- **`error`'e yazmaya devam ederler.** Galerinin seçim çubuğu `removePhotos`'u ve `removeLayer`'ı
  çağırıyor ve dönüşüne bakmıyor; reddi `ProjectScreen`'in yan panelinde, `error`'den görünüyor. O yol
  değişmez. Yoklamanın kendi hatası da `error`'de kalır.
- Sayfa söküldükten sonra gelen cevap bugünkü gibi `null`: söyleyecek kimse yok.

### Sayfa (`PhotoDetail`) — bir cevap yalnız kendi karesinde iş görür

**İki kural.** Bir basışın cevabı ekrana ancak basışın yapıldığı kare hâlâ açıksa dokunur: sekme,
`busy`, onay penceresi, `sent`, sayfanın gideceği yer. Ret ise her durumda basışın karesine yazılır
ve yalnız o karede çizilir; o kareye dönen kullanıcı onu orada bulur. Hook'un işi (galeriyi yeniden
okumak, silinen kareyi listeden çıkarmak, yoklamayı başlatmak) bugünkü gibi sürer. Sayfa söküldüyse
hook `null` döner ve cevap hiçbir şey yapmaz.

- **Hangi kare açık:** `openFrame`, bir ref. `fid` değişince `useLayoutEffect` içinde güncellenir:
  kareyi ekrana getiren commit'in içinde, yani hiçbir cevap kare ekranda değiştikten sonra ama ref
  değişmeden önce gelemez (passive `useEffect` boyamadan sonra koşar, arada bir cevap düşebilirdi).
  Ref, çünkü ekranda çizilen bir şey değil; yalnız cevapların sorduğu bir soru.
- **Basışın karesi:** her render'ın fonksiyonları o render'ın `fid`'ini kapatır; cevabın `.then`'i o
  `fid`'i `openFrame.current` ile karşılaştırır. Beş basış: `handleRemove`, `handleRegenerate`,
  `handleMute`, `handleRemoveLayer`, `handleDequeue`. `handleRetry` cevabı beklemez, değişmez.
- **Neden yalnız ret değil:** başarının da açık karede yaptıkları var — kare silmenin
  `navigate(after)`'ı, katman silme ve Kuyruktan çıkar'ın `setOpen("photo")`'u, Yeniden üret'in
  `setSent`'i — ve ikisinin ortak `setBusy(false)` / `setAsking(null)`'ı açık karede kendi basışı
  yoldaysa onun düğmelerini açar, penceresini kapatırdı.

Üç ret durumu (`refused`, `refusedAct`, `muteRefused`) tek bir duruma iner: `refusals`, kare
kimliğinden karta (`{ [fid]: { text, raw } }`). Açık karenin kartı `refusals[fid]`; tek bir
`StatusErrorCard`.

- **Cümle kartın kendisinde.** Her basış reddedilince başlığı ve sunucunun cümlesini yazar:
  `body.error` (hook'tan) ya da sesin `err.message`'ı (bugünkü gibi). Kart artık `error`'ü okumaz,
  yoklama onu silemez.
- **Ret, açık kare ne olursa olsun basışın karesine yazılır** (`refuse(fid, …)`, `openFrame`
  sorusundan önce). Başka karedeyken gelen ret o an çizilmez, açık karenin kartının yerine yazmaz,
  ve kullanıcı basışın karesine dönünce orada durur. Ret düşürülseydi kaybolurdu: bu sayfada hook'un
  `error`'ünü yalnız "Kare bulunamadı" kartı okuyor, ve galerinin yan paneli kendi `useGeneration`'ını
  taşıyor — ret o `error`'e hiç varmaz (reviewer).
- **Kareden çıkınca kart silinmez.** `fid` efekti tabloya dokunmaz; kart yalnız kendi karesinde
  çizildiği için başka karede görünmez. Kareye dönülünce son reddi hâlâ söyler.
- **Yeni basış o karenin eski kartını kaldırır.** Bir basış başlarken yalnız kendi karesinin
  satırı silinir (`unrefuse(fid)`); başka karelerin satırlarına dokunulmaz. Karede kalan tek kart her
  zaman son reddedilen basışınkidir. Bugün üç ayrı durum olduğu için bir ses reddi ile bir
  Yeniden üret reddi yan yana durabiliyordu; artık sonraki öncekinin yerine geçer. Tek kart, çünkü
  karede tek bir "son basış" vardır ve kart onun ne olduğunu söyler. Tekrar dene bugünkü gibi kartı
  kaldırmaz (hiç kart çizmiyor).
- **Kare reddinin başlığı basış anında.** Bugün "Kare silinemedi" / "Kare kuyruktan çıkarılamadı"
  çizimde `produced`'tan seçiliyor; artık `handleRemove` basıldığı an seçip yazar. Aynı seçim; yalnız
  basıştan sonra fotoğraf inse başlık basılanı söylemeye devam eder.
- Sayfanın başka yerinde `error` yalnız "Kare bulunamadı" kartında okunur; o değişmez.

## Maliyet

Ağa ve diske hiçbir yeni gidiş yok: her basış bugünkü gibi tek istek, ret sayfanın belleğinde tutulur,
ve cevabın sorusu bir ref'i okumak. Tablo, sayfa açık kaldıkça reddedilmiş kare başına en çok bir
satır taşır; sayfa sökülünce gider.

## Ne kaybolabilir, ne bozulabilir

Hiçbir şey yazılmıyor; değişen yalnız ekranın ne gösterdiği. Sıralamalar:

- A'da basış, cevap gelmeden B'ye geçiş, ret ya da başarı: B'de hiçbir şey değişmez; başarıysa galeri
  yine güncellenir (silinen kare listeden çıkar, katmanı gider), retse A'nın satırına yazılır.
- Aynısı, sonra A'ya dönüş: A'nın kartı başlığı ve sunucunun cümlesiyle orada.
- A'da basış, B'ye geçiş, B'de basış reddedildi, sonra A'nın reddi: B'nin kartı kalır.
- A'da basış, B'ye geçiş, B'de kendi basışı yolda, sonra A'nın cevabı: B'nin düğmeleri kapalı,
  penceresi "Siliniyor…" kalır.
- A'da basış, B'ye geçiş, A'ya dönüş, sonra A'nın cevabı: A açık, cevap A'da iş görür — basış bu
  karenindi. Başarılı bir kare silme o an A'nın, basış anındaki komşusuna götürür.
- Sayfa söküldü: hook `null` döner, sayfa söylemez ve hiçbir yere gitmez.
- A'dan çıkıp galeriye dönülürse sayfa sökülür; A'nın basışı sunucuda bugünkü gibi sürer.

## Sınırlar

- A'da basış yolda iken B'ye geçilirse A'nın sonucu B'de söylenmez. Ret A'nın kartında bekler ve A'ya
  dönülünce görünür. Başarının kendi sözü yok: Yeniden üret'in "Kuyruğa eklendi"si A'ya dönülünce de
  görünmez, çünkü `sent` kareden çıkınca temizleniyor (bugünkü gibi); sonucu galeri gösterir (yeni
  kare, giden katman).
- Sayfadan çıkılırsa (galeriye dönüş) tablo sayfayla birlikte gider; o arada gelen ret ekranda hiçbir
  yerde söylenmez. Bugün de böyle.
- Galerinin seçim çubuğundan gelen bir reddin fotoğraf sekmesinde görünmemesi (BACKLOG, 497'nin
  coder'ı) ayrı bir iş; burada değişmez.

## Ne zaman bitti

- **Sıra çalışırken cümle kalır** (bugün kırmızı): sıra başka bir karede çalışırken reddedilen Yeniden
  üret, katman silme, bekleyen katmanın Kuyruktan çıkar'ı ve kare çıkarma — dört kartın dördü de bir
  yoklama aralığından (2 sn) sonra başlığıyla birlikte sunucunun cümlesini gösterir.
- **Geç gelen ret yalnız kendi karesinde** (bugün kırmızı): Yeniden üret, katman silme, Kuyruktan
  çıkar, ses, kare çıkarma — basış A'da, cevap gelmeden B'ye geçilir, ret gelir: B'de ne başlık ne
  cümle; A'ya dönülünce A'da ikisi de var (geri dönüş, ret düşürülürken kırmızıydı).
- **Geç gelen ret açık karenin kartını ezmez** (bugün kırmızı): A'da Yeniden üret bekliyor, B'de
  basılan reddedildi, sonra A reddedildi: B'de B'nin cümlesi.
- **Geç gelen başarı açık karede iş yapmaz** (bugün kırmızı; A'da basış, B'ye geçiş, başarı gelir):
  - kare çıkarma: `navigate` çağrılmaz;
  - Videoyu sil ve bekleyen katmanın Kuyruktan çıkar'ı: B'nin Video sekmesi açık kalır;
  - Yeniden üret: B'de düğme basılabilir, "Kuyruğa eklendi" ve "yeniden üretilecek — kuyrukta" yok;
  - B'nin kendi Videoyu sil'i yoldayken A'nın başarısı gelir: B'nin penceresi "Siliniyor…" kalır.
- Var olan ret testleri (başlık ve cümle; başka karede kartın görünmemesi) olduğu gibi geçer.
- Galerinin seçim çubuğunun ve yan panelin testleri olduğu gibi geçer.
- `dist` yeniden derlendi; iki queen-editor takımı yeşil
  (`test_notebook_clones_its_branch.py`'nin iki testi kullanıcının Colab denemesi için kasten kırmızı).

## Aynı değişiklikte

BACKLOG'dan iki iş silinir: *"Sıra çalışırken bir reddin sunucu cümlesi bir saniyede kayboluyor"* ve
*"Kare sayfasında geç gelen bir ret başka karede görünüyor"*.
