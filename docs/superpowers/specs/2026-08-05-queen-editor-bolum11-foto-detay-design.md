# Queen Editor — Bölüm 11: Foto detay sayfası

**Tarih:** 2026-08-05 · **Yol haritası:** [2026-08-03-queen-editor-v2-roadmap.md](../plans/2026-08-03-queen-editor-v2-roadmap.md) Bölüm 11
**Tasarım kaynağı:** claude.ai/design projesi `Queen Editor` → `Queen Editor Basit v1.html`
(<https://claude.ai/design/p/efad1f83-69d3-4e07-89fa-3783839c81c3>), `PhotoDetailScreen` +
`DeleteConfirmModal`.

## Ne çalışır

Galeride bir fotoğrafa tıklayınca ayrı bir sayfa açılır: fotoğraf olabildiğince büyük ve **orijinal
oranında** (dikey/yatay/kare — kırpılmaz), iki yanında ‹ › okları, sağda 300px'lik bilgi sütunu
(sıra · dosya adı · prompt). Klavye ← → ile gezilir, **Esc** galeriye döner. **Sil** onay ister,
onaylanınca fotoğraf Drive'dan kalkar ve **sonraki fotoğraf** açılır (sonuncuysa önceki, hiç
kalmadıysa galeri).

Bu sayfa galerideki "yeni sekmede ham dosya" geçici çözümünün yerini alır (Bölüm 7'den beri duran
yer tutucu).

## Kapsam dışı

- **Toplu silme ve seçim modu** (Bölüm 12) — burada tek fotoğraf, detay sayfasından silinir.
- **Proje silme, Projeden çık onayı** (Bölüm 12).
- **Yakınlaştırma/kaydırma (zoom/pan), tam ekran, slayt gösterisi** — tasarımda yok.
- **Dokunmatik kaydırma hareketleri** — masaüstü aracı; klavye ve ok tıklaması var.

## 1. Adres

Detay sayfasının kendi adresi olur: `/projects/<proje>/photos/<dosya>` (her iki parça da
yüzde-kodlu). Neden: yenileme aynı fotoğrafta kalsın, geri tuşu galeriye dönsün, bağlantı
paylaşılabilsin — Flask zaten bilinmeyen yolları `index.html`'e düşürüyor (Bölüm 2).

Bugünkü `projectFromPath` deseni (`^/projects/(.+)$`) bu yolu **proje adı** sanır; yol çözümlemesi
tek bir yerde `{ project, photo }` döndürecek şekilde düzeltilir. Tasarımda adres kavramı yok
(pano artboard'ları) — bu bizim uygulama kararımız.

Tasarımın notu galeri tarafını söylüyor: "fotoya tıkla → detay sayfası açılır". Kare hem sürükleme
hem tıklama taşıyor; sürükleme sonrası tarayıcı zaten tıklama üretmez, ikisi çakışmaz. Bağlantı
gerçek bir `<a href>` olarak kalır (orta tıkla yeni sekme çalışsın), tıklama `preventDefault` ile
uygulama içi geçişe çevrilir — sayfa baştan yüklenmez.

## 2. Ekran (tasarımdan birebir)

- **App bar** proje ekranıyla aynı: solda `Queen Editor` (accent), ortada proje adı, sağda
  `<Btn ghost><Icon.Left /> Galeriye dön</Btn>`.
- **Gövde:** solda fotoğraf alanı (`flex:1`, `padding:24`, zemin `var(--bg)` — sayfanın en koyu
  tonu), sağda `300px` bilgi sütunu (`borderLeft`, `padding:16`, `gap:14`).
- **Oklar:** düz `‹` / `›` karakterleri (SVG değil), fotoğraf alanının iki ucunda sabit —
  `position:absolute`, `left/right:20`, `top:50%`, `translateY(-50%)`, `fontSize:44`,
  `fontWeight:300`, `color:#fff`,
  `textShadow:"0 0 4px rgba(0,0,0,.9), 0 2px 8px rgba(0,0,0,.7)"` (her fotoğrafın üstünde okunsun
  diye).
- **Bilgi sütunu**, yukarıdan aşağı: `SIRA` / `DOSYA ADI` etiket-değer çifti yan yana
  (`gap:24`; etiketler `Mono size={10}`, `var(--ink-3)`, `letterSpacing:.08em`, büyük harf;
  değerler `Mono size={13}`, `var(--ink)`), altında `PROMPT` etiketi ve `wf-stroke` kutusu
  (`flex:1`, `overflowY:auto`, `padding:10`) içinde `Note size={12}`, `var(--ink-2)`,
  `lineHeight:1.6`; en altta **Sil** düğmesi:
  `<Btn sm style={{ color: "var(--danger)", borderColor: "var(--danger)", justifyContent: "center" }}><Icon.Trash /> Sil</Btn>`.

**Fotoğrafın sığdırılması — uyarlama.** Tasarım gerçek bir görsel değil yer tutucu kullanıyor ve
oranı `aspectRatio` ile veriyor; bizde gerçek dosyanın oranını sunucu bilmiyor. Aynı sonuç
görselin kendisiyle alınır: `max-width: calc(100% - 120px)`, `max-height: 100%`,
`object-fit: contain`, `width/height: auto`. 120px, tasarımın oklara ayırdığı payın aynısıdır.
Böylece dikey/yatay/kare fark etmeksizin kırpılmaz ve oran korunur.

**Pasif ok görünümü — bizim kararımız.** Tasarım "ilk/son fotoda ok pasif, sarmaz" diyor ama pasif
hâli çizmiyor. Pasif ok `opacity: .25` ile ve tıklanamaz olarak çizilir; başa sarma yoktur.

## 3. Gezinme

- `‹` bir önceki, `›` bir sonraki fotoğrafa gider; sıra **galeri sırasıdır** (Bölüm 9).
- Klavye: `←` / `→` aynı işi yapar, `Esc` galeriye döner. Dinleyici sayfa kapanınca kaldırılır.
- İlk fotoğrafta `‹`, son fotoğrafta `›` pasiftir — liste başa sarmaz.
- Adresteki dosya listede yoksa (silinmiş fotoğrafın bağlantısı, elle yazılmış ad): sayfa hata
  kartı gösterir ("Fotoğraf bulunamadı") ve galeriye dönüş düğmesi kalır. Boş ekran gösterilmez.

## 4. Silme ve verinin gerçeği

Akış: **Sil** → onay kutusu → onay → sunucu siler → sonraki fotoğraf açılır (sonuncuysa önceki,
hiç kalmadıysa galeri).

**Onay kutusu** tasarımın silme onayıyla aynı biçimdedir (`wf-scrim` → `wf-card wf-card--shadow`,
`width:320`, `padding:18`, `gap:10`): başlık `Note size={14}`, altında `Note size={12}`
`var(--ink-2)` ile "Bu işlem geri alınamaz.", sağa yaslı `Vazgeç` (`Btn sm ghost`) ve dolu kırmızı
`Sil` (`Btn sm`, `background/borderColor: var(--danger)`, `color:#fff`). Tasarımdaki metin çoklu
seçim için yazılmış ("3 fotoğraf silinsin mi?"); tekil hâli **"Bu fotoğraf silinsin mi?"**.
Tasarımda bu üç onay kutusu üç ayrı blok olarak yazılmış; biz de şimdilik tek kullanımlık yazarız —
Bölüm 12 üç onay daha getirdiğinde ortak bir bileşene çıkarılır (ikinci kullanımdan önce soyutlama
yok).

**Kayıt yalnız-ekleme kalır.** `photos.jsonl` "hangi fotoğraflar var" sorusunu cevaplıyor ve
CODE-STANDARD gereği asla baştan yazılmıyor (yarım kalan oturum en fazla son satırı kaybetsin
diye). Silme bu dosyayı yeniden yazmaz: **silme satırı eklenir** —
`{"file": "3_a.png", "deletedAt": "…"}`. Okuma kaydı bir günlük gibi katlar: bir dosya adının **son**
satırı geçerlidir, silme satırıyla biten dosya listeye girmez. Böylece hem galeri doğrudur hem de
tek bir yazma hatası tüm izi riske atmaz.

**Silinen numara geri kullanılmaz.** Bugün `next_number` iki kaynağa bakıyor: diskteki dosyalar ve
planın ayırdığı numara; dokümantasyonu "kayda bakmaya gerek yok, kayıt diskin bilmediği numarayı
tutamaz" diyor. **Silme bu varsayımı bozar** — dosya diskten kalkınca numara serbest görünür, aynı
ad ikinci bir prompt'a bağlanır ve dahası tarayıcı `immutable` önbelleği yüzünden eski görseli
gösterir. Bu yüzden `next_number` üçüncü bir kaynağa daha bakar: **kaydın gördüğü en büyük numara**
(silinenler dâhil). Kaydın eski dokümantasyonu da düzeltilir — yorum koddan sapamaz.

**Sıra dosyası budanır.** Silinen ad `order.json`'dan çıkarılır. Zaten kalsa da zararsızdı (Bölüm
9'un uzlaştırması kayıtta olmayan adı yok sayıyor), ama dosyanın ölü ad taşıması yanlış olur.

**Silme sırası:** önce diskteki dosya, sonra kayda silme satırı, sonra sıra dosyası. Gerekçe: dosya
silinemezse (izin, bağlantı) hiçbir şey değişmemiş olur ve hata dürüsttür. Zaten olmayan dosyayı
silmek hata değildir — aynı isteğin ikinci kez gelmesi (çift tık, tekrar) aynı sonucu verir.

**Sunucu arayüzü:** `DELETE /api/projects/<p>/photos/<dosya>` → **204**. Proje yoksa 404; dosya
kayıtta yoksa 404 ("Fotoğraf yok: …"). Cevap gövdesiz: istemci galeri sırasını zaten biliyor,
sonraki fotoğrafı kendisi açar.

## 5. Doğrulama

1. Galeride bir fotoğrafa tıkla → detay sayfası açılır, adres `/projects/…/photos/…` olur; yenile
   → aynı fotoğraf durur; geri tuşu → galeri.
2. Dikey, yatay ve kare fotoğraflarda: fotoğraf kırpılmadan, oranı bozulmadan sığar.
3. ‹ › ve ← → ile gez: sıra galeriyle aynı; ilk/son fotoda ilgili ok soluk ve tıklanamaz, başa
   sarmaz. Esc galeriye döner.
4. Sil → onay → fotoğraf gider, sonraki açılır. Son fotoğrafı sil → önceki açılır. Tek fotoğrafı
   sil → galeriye döner.
5. Silinen fotoğraf galeriden ve Drive'dan kalkar; `photos.jsonl` **kısalmaz** (silme satırı eklenir).
6. Silmenin ardından Üret → yeni fotoğraf **silinen numarayı kullanmaz**.
7. Silinmiş fotoğrafın adresine elle git → "Fotoğraf bulunamadı" kartı, galeriye dönüş çalışır.

## Kararlar

- **Detay sayfası gerçek bir adrestir** (`/projects/<p>/photos/<dosya>`) — tasarımda adres kavramı
  yok, bu bizim kararımız; yenileme ve geri tuşu bunu gerektiriyor.
- **Silme, kaydı yeniden yazmaz; silme satırı ekler** — yalnız-ekleme güvencesi korunur (§4).
- **`next_number` artık kaydı da dinler** — silinen numara asla geri kullanılmaz; eski dokümantasyon
  düzeltilir.
- **Fotoğraf `object-fit: contain` ile sığdırılır** — tasarımın `aspectRatio` yer tutucusunun gerçek
  görseldeki karşılığı.
- **Pasif ok `opacity:.25`** — tasarımda çizilmemiş, bizim kararımız.
- **Onay kutusu tek kullanımlık yazılır**, ortak bileşen Bölüm 12'de çıkarılır.
