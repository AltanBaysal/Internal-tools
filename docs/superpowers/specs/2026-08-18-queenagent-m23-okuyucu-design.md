# Madde 23 — Okuyucu · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 23](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 58, 59, 60 · `HANDOFF.md` §4 (belge ölçeği), §11 (kaldırılan `←`)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · Gövde belge olur (fark 58)

Bugün dosya içeriği `white-space: pre-wrap` ile düz metin: 14px, 1.75. Bundan sonra **Madde 13'ün
ayrıştırıcısı** çiziyor — yeni ayrıştırıcı yok, yeni bileşen yok, `<Markdown>` ikinci kez çağrılıyor.

Madde 13'ün belgesi bunu zaten yazmıştı: *"Madde 23 aynı bileşeni `.reader__body` altında kullanacak
ve tek satır CSS ile belge ölçeğini alacak."* Ölçek kabın işi:

| | Baloncuk *(Madde 13)* | Belge *(burada)* |
|---|---|---|
| h1 | 19.5px serif | **25px** serif |
| h2 | 17px serif | **20px** serif |
| h3 | 14.5px | **15.5px** |
| h4 | h3'ün boyu, sönük | h3'ün boyu, sönük |
| gövde | 15.5 / 1.75 | **14.5 / 1.8** |

h4 yine kendi sayısını uydurmuyor: tasarım üç seviye veriyor, dördüncüsü üçüncünün boyunu alıp
renkte geri çekiliyor. Baloncukta verilen karar burada da geçerli.

`white-space: pre-wrap` kalkıyor. Satır sonları artık ayrıştırıcının; kural yerinde kalsaydı her
boşluğu ikiye katlardı — Madde 13'te `.msg__text` için verilen kararın aynısı.

---

## 2 · Başlık tepede, alt bilgi dipte (fark 59)

Bugün okuyucu bir bütün olarak kayıyor: uzun bir dosyada başlık da alt bilgi de yukarı çıkıp
kayboluyor. Bundan sonra okuyucu üç parça bir sütun:

| Parça | Davranış | İç boşluk |
|---|---|---|
| `reader__head` | yerinde durur | 18px 28px |
| `reader__body` | **tek kayan yer** | 26px 28px |
| `reader__meta` | yerinde durur, üstünde ayırıcı çizgi | 12px 28px |

26/28 tasarımın sayısı (fark 58). Yatay 28 başlıkla ve alt bilgiyle paylaşılıyor ki **ad, metin ve
alt bilgi aynı hizada** başlasın. Dikey 18 bizim: kabın bugün verdiği 20'nin yerini alıyor.

Bu, iç boşluğun **kaptan okuyucuya taşınması** demek. Bugün `.rail` ve `.panel` 20px 18px veriyor;
gövde kendi 26/28'ini alınca ikisi üst üste binerdi. O yüzden okuyucu kabında kenardan kenara
duruyor, dolguyu ray listesi kendi üstüne alıyor.

**Alt bilginin yazısı değişiyor:** `md · 1.4 KB · 2h ago` → **`2h ago · project file`**. Uzantı ve
boyut gidiyor; uzantı zaten satırdaki çipte ve adın kendisinde yazıyor. `formatSize` bununla birlikte
ölü kod olur ve silinir.

Sıra ray satırının tersi (`project file · 2h ago`, Madde 21) — tasarımın verdiği sıra bu.

---

## 3 · İki panelin iki kapanışı (fark 60)

| Nerede | Başlık satırı |
|---|---|
| Sohbet rayı | `←` · ad · `Download` |
| Proje ekranı | ad · `Download` · `×` |

Sebebi ikisinin ne olduğu: raydaki panel rayın genişlemiş hâli, ondan **geri** dönülür; proje
ekranındaki panel yanda duran ayrı bir yüzey, o **kapatılır**. `HANDOFF.md` §11 proje ekranındaki
`←`'i açıkça kaldırılanlar arasına yazıyor.

Tek bileşen, bir `back` bayrağı: ray `back` veriyor, proje ekranı vermiyor. İki bileşene bölmek aynı
başlığı, aynı `Download`'u ve aynı indirme durumunu iki yere kopyalardı.

`×`'in erişilebilir adı `×` kalıyor — yanındaki `←` de öyle. Üzerinde `title="Close"` var; ikisinin
adlandırmasını burada ayırmak fark 60'ın istemediği bir tutarsızlık olurdu.

---

## 4 · Katman denetimi

`FilePanel.jsx` (üç parça, `back`), `FileRail.jsx` ve `ProjectScreen.jsx` (çağrı), `workspace.css`.
`Markdown.jsx` değişmiyor — yalnız ikinci kez çağrılıyor. Arka uç yok, yeni bağımlılık yok.

---

## 5 · Kabul ölçütü

1. Dosya içeriği Markdown olarak çizilir; `# Başlık` bir `h1` olur.
2. Okuyucunun başlıkları 25 / 20 / 15.5px'tir ve baloncuğun ölçeği değişmez.
3. Gövde 14.5px / 1.8'dir ve `white-space` kuralı taşımaz.
4. Uzun bir dosya kayarken başlık ve alt bilgi yerinde durur; kayan tek yer gövdedir.
5. Alt bilgi `2h ago · project file` der ve üstünde bir çizgi vardır.
6. Proje ekranının paneli `×` ile kapanır ve `←` taşımaz.
7. Sohbet rayının paneli `←` ile kalır ve `×` taşımaz.

## 6 · Risk

Başlık ve alt bilginin 18px/12px dikey dolgusu tasarımdan gelmiyor; yatay 28 ve gövdenin 26/28'i
geliyor. Kilit testi sayıları, Madde 35 gözü üstleniyor.
