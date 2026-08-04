# Queen Editor — Bölüm 12: Silme + onaylar

**Tarih:** 2026-08-05 · **Yol haritası:** [2026-08-03-queen-editor-v2-roadmap.md](../plans/2026-08-03-queen-editor-v2-roadmap.md) Bölüm 12
**Tasarım kaynağı:** claude.ai/design `Queen Editor Basit v1.html` — `ProjectScreen selectMode`,
`DeleteConfirmModal`, `ProjectDeleteModal`, `ExitConfirmModal`, `ProjectCard`.

## Ne çalışır

Yıkıcı işlemlerin tamamı, hepsi onaylı:

1. **Seçim modu** — karenin sol üstünde hover'da beliren ✓ ile açılır; modda kareye tıklamak seçer
   / seçimi kaldırır; altta yüzen çubuk seçili sayısını, **Tümünü seç**, **Sil**, **Vazgeç**'i
   taşır; `Esc` veya Vazgeç modu kapatır.
2. **Toplu silme** — Sil onay ister ("N fotoğraf silinsin mi?"), onaylanınca hepsi Drive'dan gider.
3. **Proje silme** — kartın sağ üstündeki kırmızı çöp → onay → klasör içeriğiyle birlikte silinir.
4. **Projeden çık onayı** — düğme artık doğrudan çıkmaz, önce sorar (yıkıcı değil: onay düğmesi
   accent renkli **Çık**).

## Kapsam dışı

- Geri alma (undo) — tasarım "bu işlem geri alınamaz" diyor; çöp kutusu kavramı yok.
- Seçim modunda sürükleyerek sıralama — modda tıklama seçimdir; sıralama normal moddadır.
- Klavyeyle çoklu seçim (Shift+tık, Ctrl+A) — tasarımda yok; **Tümünü seç** düğmesi var.

## 1. Silme uçları — tek uç, tek kural

Bölüm 11 tek fotoğraf için `DELETE /api/projects/<p>/photos/<dosya>` getirmişti. Toplu silme aynı
işi N kez yapıyor; iki ayrı uç aynı kuralın iki kopyası olurdu. Bu yüzden tek uca inilir:

`POST /api/projects/<p>/photos/delete` · gövde `{"files": [...]}` → `{"deleted": [...]}`

- Detay sayfası tek elemanlı listeyle çağırır; seçim modu N elemanlı.
- Kayıtta olmayan ad **sessizce atlanır** — cevap gerçekten silinenleri söyler. Gerekçe: onay
  kutusu açıkken başka bir sekme aynı fotoğrafı silmiş olabilir; kalanları silmemek kullanıcının
  isteğine ters olurdu.
- Gövde liste değilse **400**; proje yoksa **404**.
- Her dosya için sıra: diskten sil → kayda silme satırı ekle → `order.json`'dan çıkar (Bölüm 11'in
  kuralı, dosya başına aynen uygulanır).

**Proje silme:** `DELETE /api/projects/<ad>` → **204**; proje yoksa 404. Klasör içeriğiyle birlikte
gider (fotoğraflar, `photos.jsonl`, `plan.json`, `settings.json`, `order.json`). İşletim sistemi
hata verirse (izin, kilitli dosya) 500 + sistemin kendi metni.

## 2. Ekran (tasarımdan birebir)

**Seçilebilir kare:** sol üstte 18×18 daire (`top:6, left:6`, `borderRadius:"50%"`), seçili
değilken `border:"2px solid var(--ink-3)"` + `background:"rgba(0,0,0,.35)"` ve boş; seçiliyken
`background: var(--accent)`, `color:"#1a1625"`, `fontSize:11`, `fontWeight:700`, içinde `✓`.
Seçili karenin görsel sarmalayıcısı `outline:"2px solid var(--accent)"` + `borderRadius:4` alır ve
üstüne `rgba(167,139,250,.18)` mor bir örtü gelir. Sıra rozeti ve dosya adı satırı değişmez.

**Yüzen çubuk:** `wf-card wf-card--shadow`, `position:absolute`, `left:"50%"`, `bottom:20`,
`transform:"translateX(-50%)"`, `padding:"10px 18px"`, `gap:14`, `borderColor: var(--accent)`.
İçindekiler sırayla: `Mono size={12}` accent renkli **"N seçili"**, `Btn sm ghost` **Tümünü seç**,
`Btn sm` + `Icon.Trash` + **Sil** (`color/borderColor: var(--danger)`), `Btn sm ghost` **Vazgeç**.
Aralarında ayraç karakteri yoktur — boşluğu `gap` verir.

Galerinin altına çubuğun yüksekliği kadar ek boşluk konur: tasarımın notu "liste sonuna ekstra
padding → kaydırınca son satır barın üstünde tam görünür".

**Proje kartı çöpü:** `Btn sm ghost`, `position:absolute`, `top:10`, `right:10`,
`padding:"4px 8px"`, `color: var(--danger)`, yalnız `Icon.Trash` (metin yok). Tasarım bunu hover'a
bağlamamış — hep görünür. Kart zaten tıklanabilir; çöp düğmesi kartın üstünde durduğu için
**tıklama kartı açmamalı** (olayın yukarı çıkması durdurulur). Tasarım bu çakışmayı çözmüyor, bu
bizim kararımız.

**Onay kutuları** — üçü de aynı iskelet (`wf-scrim` → `wf-card wf-card--shadow`, `padding:18`,
`gap:10`, sağa yaslı düğme çifti):

| Kutu | Genişlik | Başlık | Gövde | Onay düğmesi |
|---|---|---|---|---|
| Toplu silme | 320 | "N fotoğraf silinsin mi?" | "Bu işlem geri alınamaz." | dolu kırmızı **Sil** |
| Proje silme | 340 | "\"ad\" projesi silinsin mi?" | "İçindeki tüm fotoğraflar kalıcı olarak silinir. Bu işlem geri alınamaz." | dolu kırmızı **Sil** |
| Projeden çık | 320 | "Projeden çıkılsın mı?" | yok | accent **Çık** (`Btn sm hl`) |

Tasarımda bu üç kutu üç ayrı blok olarak yazılmış (kopyala-yapıştır). Bizde **tek bir onay
bileşenine** çıkarılır: Bölüm 11'de "ikinci kullanımdan önce soyutlama yok" diyerek tek kullanımlık
yazmıştık; bu bölümde kullanım dörde çıkıyor, soyutlama artık hak edilmiş durumda. Bileşen
`shared/ConfirmModal.jsx`: başlık, isteğe bağlı gövde, onay etiketi, `danger` mı `accent` mi, ve
`busy` durumu.

## 3. Seçim modunun davranışı

- **Açılış:** normal modda karenin sol üstündeki ✓ dairesi yalnız hover'da görünür; tıklanınca mod
  açılır ve o kare seçili olur.
- **Modda:** kareye tıklamak seçer/kaldırır (detay sayfası **açılmaz**), sürükleyerek sıralama
  kapalıdır — aynı jest iki anlama gelemez.
- **Çıkış:** `Esc` veya **Vazgeç**; seçim temizlenir. Silme bittiğinde de mod kapanır.
- **Tümünü seç:** görünen tüm fotoğrafları seçer. Hepsi zaten seçiliyse düğme seçimi temizler
  (aynı düğmenin ikinci basışı geri alır) — tasarım bunu söylemiyor, bizim kararımız.
- Seçili sayısı sıfıra düşerse mod açık kalır (kullanıcı yeniden seçebilsin); **Sil** düğmesi
  seçim yokken pasiftir.
- Üretim sürerken seçim serbesttir; üretilmekte olan kare (spinner) seçilemez — kayıtta yoktur.

## 4. Doğrulama

1. Kareye hover → sol üstte boş halka; tıkla → mod açılır, kare seçili (mor çerçeve + örtü + ✓).
2. Başka karelere tıkla → seçim büyür, çubukta sayı güncellenir; aynı kareye tekrar tıkla → çıkar.
3. Tümünü seç → hepsi seçili; tekrar bas → seçim temizlenir.
4. Sil → "3 fotoğraf silinsin mi?" → onayla → üçü de galeriden ve Drive'dan gider, mod kapanır.
5. `Esc` ve Vazgeç modu kapatır, seçim sıfırlanır.
6. Modda kareye tıklamak detay sayfasını **açmaz**; moddan çıkıp tıklayınca açar.
7. Proje kartındaki çöp → onay → kart listeden gider, Drive'daki klasör içeriğiyle silinir; çöpe
   basmak projeyi **açmaz**.
8. Projeden çık → onay kutusu; Vazgeç ekranda tutar, Çık galeriye… (projeler ekranına) döner.
9. Silinen fotoğrafların numaraları geri kullanılmaz (Bölüm 11 kuralı toplu silmede de geçerli).

## Kararlar

- **Tek silme ucu** (`POST …/photos/delete`, liste alır) — Bölüm 11'in tekil ucu buna dönüşür.
- **Bilinmeyen ad sessizce atlanır**, cevap gerçekten silinenleri söyler.
- **`ConfirmModal` ortaklaştırılır** — dört kullanım, tasarımın üç kopyası tek yere iner.
- **Çöp düğmesi kartı açmaz** (olay durdurulur) — tasarımda çözülmemiş, bizim kararımız.
- **Tümünü seç ikinci basışta temizler** — bizim kararımız.
- **Seçim modunda sürükleme kapalı** — aynı jest iki anlama gelemez.
