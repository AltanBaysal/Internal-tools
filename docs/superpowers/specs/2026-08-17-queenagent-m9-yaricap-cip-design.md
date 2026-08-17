# Madde 9 — Yarıçaplar, çip, dosya satırı · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 9](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynaklar:** fark 15 (rozet ayağı), 38, 54, 56, 77 · sapma 88, 89 · `HANDOFF.md` §10
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 0 · Açık soru yok; iki şey bilerek ertelenmiş sayılıyor

Fark 77 yarıçap kümesini üçe topluyor — **denetim 8px, kart 12–14px, hap 20px** — ve kümenin içinde
beş ayrışma sayıyor: menüler 12px, satır menüsü 11px, onay kutusu 14px, geri alma şeridi 10px,
alttaki koyu şerit 11px.

**Beşinin dördü henüz var olmayan yüzeyler.** Menüler Madde 25'te, satır menüsü Madde 18'de, onay
kutusu Madde 17'de doğuyor; her biri kendi maddesinde bu yarıçapla çizilecek. **Geri alma şeridi ise
var ama gidiyor** — karar 16 geri almayı tümüyle kaldırıyor ve Madde 19 onu söküyor. 10px'e çekmek,
iki madde sonra silinecek bir yüzeyi boyamak olurdu; dokunulmuyor.

Bu maddede yapılan şey: **bugün yanlış yarıçapta duran yüzeyleri düzeltmek** (sapma 88 ve 89) ve
tasarımın adıyla verdiği iki biçimi kurmak (çip, dosya satırı).

---

## 1 · Yarıçaplar

| Yüzey | Bugün | Yeni | Neden |
|---|---|---|---|
| `.sidebar__new-chat` | 9px | `var(--radius-control)` | denetim |
| `.sidebar__row` | 9px | `var(--radius-control)` | denetim |
| `.composer__send` | 9px | `var(--radius-control)` | denetim |
| `.composer` | 16px | **14px**, dolgu `14px 16px 10px` | kart bandının üst ucu (fark 38) |

Sapma 88 kenar çubuğu denetimlerinin yan yana duran sohbet/dosya satırlarıyla eşleşmemesiydi; üçü de
`--radius-control`'e bağlanınca köşeler eşleşiyor ve sayı tek yerde duruyor.

**Composer artık tek değere sahip.** Fark 38 Home'unkini 16px'te bırakıyordu, ama Home Madde 3'te
silindi; geriye kalan iki kutu (proje ve sohbet) aynı 14px'i alıyor, dolayısıyla ekrana göre ayrım
diye bir şey kalmıyor. Bu da sapma 89'u kapatıyor: composer artık kart bandının içinde.

---

## 2 · Uzantı çipi (fark 56)

Metne göre daralıp genişleyen küçük etiket, **sabit 30×30px bir kareye** dönüşüyor: 7px yarıçap,
`#F0E7DE` zemin, ortalanmış 9.5px mono büyük harf.

Sabit olmasının sebebi tasarımın kendi gerekçesi: **uzantı ne kadar uzun olursa olsun satırın hizası
kaymaz.** Çipin metni bugünkü gibi uzantının üç harfi (`extension_of`), yani içerik değişmiyor —
değişen kabın ölçüsü.

`#F0E7DE` yeni bir renk ve `app.css`'te bir değişkeni yok. **Değişken yapılmıyor:** palet
değişkenleri görsel dilin adlandırılmış rolleridir (vurgu, yıkıcı, çizgi, mürekkep); çipin zemini tek
bir bileşenin yüzeyi, ikinci bir kullanıcısı yok. Rol doğduğunda değişkene çıkar.

---

## 3 · Dosya satırı iki satıra açılıyor (fark 54)

Bugün: çip · ad · zaman, hepsi tek satırda, zaman sağa yaslı.
Yeni: çip solda; sağında **ad üstte** (13.5px), **altında mono 11px ikincil satır**.

İkincil satırın metni tasarımın kendi cümlesi: **`project file · 2h ago`**.

**Dosyanın kime ait olduğunu satırın kendisi söylüyor** — sohbet rayında da, proje sütununda da aynı
metin. Proje sütununda "project file" fazlalık gibi durur ama tasarım satırı tek biçim olarak
tanımlıyor ve dosya her iki yerde de aynı şeydir: sohbetin değil, projenin dosyası. Bu, kaldırılan
öğüt satırının (fark 23) söylediğini satırın kendisine taşıyor.

`.file-row__when` yerini `.file-row__meta` alır; sağa yaslı zaman diye bir öğe kalmaz.

---

## 4 · Kenar çubuğu rozeti (fark 15'in rozet ayağı)

Bugün dosya sayısı sıfırken rozet **hiç yazmıyor** (`{project.files || ""}`) ve satırın sağ ucu
boşalıyor. Tasarımda rozet sıfırken de yerini koruyor, yalnız yazısı saydamlaşıyor.

Yeni: sayı her zaman çiziliyor; sıfırken `.sidebar__row-badge--none` saydamlaştırıyor. Böylece bir
projeye ilk dosya düştüğünde satırdaki hiçbir şey yana kaymıyor — hareket kuralının ("yerleşmiş
hiçbir öğe yana kaymaz", karar 3) satır ölçeğindeki karşılığı.

*(Fark 15'in diğer ayağı — kartlardaki "1 chat · 3 files" tekil/çoğul kuralı — Madde 3'te kartlarla
birlikte konusuz kaldı. Aynı kuralın silme onayındaki cümleye uzanan ayağı **Madde 18**'in işi.)*

---

## 5 · Katman denetimi

Değişenler: `workspace.css`, `FileRow.jsx`, `Sidebar.jsx`. Yeni bağ, yeni port, yeni uç nokta yok;
bağımlılık yönü ve üç yasak anılmıyor. `shared/app.css` renk ve yarıçap değişkenlerinin tek evi
olarak kalıyor — bu maddede üç yüzey elle yazdığı sayıyı bırakıp `var(--radius-control)`'e geçiyor,
yani kural gevşemiyor, sıkışıyor.

---

## 6 · Kabul ölçütü

1. Kenar çubuğunun iki denetimi ve Send düğmesi `var(--radius-control)` kullanır; dosyada
   `border-radius: 9px` kalmaz.
2. Composer 14px yarıçaplı ve `14px 16px 10px` dolguludur; `border-radius: 16px` kalmaz.
3. Çip 30×30px sabit karedir; 7px yarıçap, `#f0e7de` zemin, 9.5px mono.
4. Dosya satırı iki satırlıdır ve ikincil satırı `project file · 2h ago` yazar — hem rayda hem proje
   sütununda.
5. Kenar çubuğu rozeti sıfırken `0` çizer ve saydamlaşır; satırın hizası dosya doğunca kaymaz.

## 7 · Risk

Dosya satırının metni testlerde iki yerde aranıyor (`2h ago` tek başına aranan yerler var). İkincil
satır tek bir düğüm olduğu için `2h ago` artık `project file · 2h ago`'nun içinde geçiyor; bu tür
testler tam eşleşmeden parça eşleşmeye geçirilir.
