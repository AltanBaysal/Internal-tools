# Madde 13 — Markdown ve balon ölçeği · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 13](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 39, 40 · `HANDOFF.md` §4
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Verilen karar: çiziciyi kendimiz yazıyoruz

Kullanıcıya soruldu, seçim **kendi ayrıştırıcımız** oldu. Gerekçe: Madde 14 akan metni her parçada
yeniden ayrıştırmayı ve **kapanmamış kod çitini çizim sırasında kapatmayı** istiyor, Madde 15 bekleme
bloğunu metnin ucuna dikiyor. Kendi ayrıştırıcımızda bunlar birkaç satır; hazır bir kütüphanede onun
etrafından dolaşmak olurdu. Bedeli tablo ve iç içe listenin bize kalması.

İki kural bu maddeden sonra da geçerli:

- **HTML üretilmez.** `dangerouslySetInnerHTML` yok; ayrıştırıcı veri döndürür, bileşen React öğesi
  kurar. Böylece XSS kapısı hiç açılmaz.
- **Desteklenen sözdizimi `HANDOFF.md` §4'ün saydığı listeden ibarettir.** Sayılmayan bir işaret ham
  metin olarak kalır; tahmin edilmez.

---

## 1 · Bu madde neyi kapsar

Kapsam **sohbetteki cevaplar**: hem kayıtlı mesajlar hem akmakta olan metin. Akan metin de ilk
karesinden itibaren biçimli çizilir — önce ham görünüp sonra biçime atlaması bir kusur olurdu.

**Kullanıcı mesajı ham kalır.** `**test**` yazan biri yıldızlarını görür. Bu bir eksiklik değil,
tasarımın kendi cümlesi: kullanıcının yazdığı şey neyse ekranda o durur.

**Dosya paneli bu maddede değişmez.** Belge ölçeği ve okuyucunun gövdesi **Madde 23**'ün işi
(fark 58). Bu yüzden burada yalnız **balon ölçeği** tanımlanır.

---

## 2 · Ayrıştırıcı — `shared/markdown.js`

React'i tanımayan saf bir modül; `time.js` gibi metin işleyen bir yardımcı. İki dışa açık işlev:

`parseBlocks(text)` → blok dizisi:

| Blok | Sözdizimi | Veri |
|---|---|---|
| `heading` | `#` … `####` + boşluk | `level`, `inline` |
| `code` | ``` ``` ``` çiti, dil adı seçimlik | `lang`, `text` |
| `list` | `-` `*` `+` · `1.` | `ordered`, `items[]` — her madde `inline` ve seçimlik `blocks` |
| `table` | `\|` satırı + `\|---\|` ayırıcısı | `head[]`, `rows[][]` |
| `quote` | `>` | `blocks` (özyineli) |
| `rule` | `---` veya `***` | — |
| `paragraph` | geri kalan | `inline` |

`parseInline(text)` → belirteç dizisi: `text`, `code`, `strong`, `em`, `del`, `link`, `break`.

Kurallar:

1. **Satır içi kod her şeyi yener.** Ters tırnakların arası harfi harfine metindir; içindeki `**`
   yıldız olarak kalır.
2. **İç içe geçme özyinelidir** — `**kalın *ve eğik***` çalışır. Kod bunun dışındadır (kural 1).
3. **Paragraf içindeki tek satır sonu bir satır sonudur** (`break`), boşluk değil. Markdown'ın kendi
   kuralı onu boşluğa çevirir; sohbette bu yanlış olur — model listelemeden alt alta yazdığında
   metin tek bloğa yapışırdı. GitHub yorumları da böyle davranır.
4. **Bağlantının hedefi denetlenir.** Yalnız `http://`, `https://` ve `mailto:` kabul edilir; başka
   bir şey — `javascript:` dahil — bağlantı sayılmaz, `[şu](javascript:…)` ham metin olarak kalır.
5. **Çit kapanmadan metin biterse blok orada biter.** Ayrıştırıcının doğal davranışı bu; fark 41'in
   istediği emniyet bedavaya geliyor. Akış davranışının kendisi Madde 14'te sınanır.
6. **Tablo hizalama satırı okunur ama hizalama uygulanmaz.** `:---:` tabloyu tanımaya yarar; sütun
   hizası tasarımın hiçbir yerinde geçmiyor.

**İç içe liste destekleniyor.** İki boşluk girintili bir madde bir öncekinin altına iner. YAGNI'ye
rağmen: model iç içe madde üretiyor ve düz çizilirse `- alt madde` maddenin *içinde* ham metin
olarak görünür — bozuk görünen bir çıktı, eksik bir özellik değil.

---

## 3 · Bileşen — `features/workspace/Markdown.jsx`

`<Markdown text={…} />` → `<div className="md">` ve altında bloklar. Ayrıştırıcının belirteçlerini
React öğesine çeviren tek yer burası.

- Kod bloğu `<pre><code>`; dil adı bugün çizilmiyor (tasarım göstermiyor), ayrıştırıcı yine de
  saklıyor.
- Bağlantı `target="_blank" rel="noreferrer"` — uygulama yerelde çalışıyor, dış bağlantı yeni sekmede
  açılır.
- Tablo `<thead>`/`<tbody>` ile gerçek bir `<table>`, çevresinde `.md__table-scroll` sarmalayıcısı.
  Madde 11'in kuralı: sayfa hiçbir boyda yatay kaymaz, geniş bir tablo kendi içinde kayar. Uzun bir
  kod satırı için aynı iş `.md pre`'nin kendisinde.

Ölçek bileşenin sorusu değil. Sarmalayıcı hep `.md`; boyutu kabı verir (`.msg__text .md h1`). Madde
23 aynı bileşeni `.reader__body` altında kullanacak ve tek satır CSS ile belge ölçeğini alacak.

---

## 4 · Balon ölçeği

| Öğe | Değer | Kaynak |
|---|---|---|
| h1 | 19.5px Newsreader | `HANDOFF.md` §4 |
| h2 | 17px Newsreader | §4 |
| h3 | 14.5px DM Sans 600 | §4 |
| h4 | 14.5px DM Sans 600, sönük renk | **boşluk dolduruldu** |

Tasarım dört başlık düzeyi sayıyor ama üç boyut veriyor. h4 üçüncünün ölçüsünü alıp renkte geri
çekiliyor: yeni bir sayı uydurulmuyor, hem h3 zaten gövdeden (15.5px) küçük olduğu için altında yer
de kalmıyor. Madde 35'te göze bakılır.

Blok stilleri paletin kendi değişkenlerinden kuruluyor (`--surface`, `--line`, `--radius-control`,
`--font-mono`); `HANDOFF.md` kod bloğu ya da tablo için ölçü vermiyor, bu yüzden ölçü icat edilmiyor,
uygulamanın var olan belirteçleri kullanılıyor.

`.msg__text`'ten **`white-space: pre-wrap` kalkıyor**. Satır sonlarını artık ayrıştırıcı biliyor;
kural yerinde kalsaydı bloklar arası boşluk ikiye katlanırdı. `pre-wrap` yalnız iki yerde kalıyor:
kullanıcı balonu (`.msg__bubble`) ve kod bloğu (`.md pre`).

---

## 5 · Katman denetimi

`shared/markdown.js` hiçbir şeyi içe aktarmaz. `Markdown.jsx` yalnız onu içe aktarır. Yeni servis
yok, özellik sınırı geçilmiyor.

FOUNDATION karar 4 — "kurallar arka uçta, ön yüz görünümdür" — çiğnenmiyor: bir metnin nasıl
çizileceği sunum sorusudur, kararın kendisi "biçimlendirme, ne gösterilir" diyerek bunu ön yüze
bırakıyor. Sunucu ham metni göndermeye devam ediyor.

---

## 6 · Kabul ölçütü

1. `# Başlık`, `**kalın**`, `~~üstü çizili~~`, `` `kod` ``, ``` ``` ``` bloğu, `-`/`1.` listeler,
   tablo, `>` alıntı, `---` ve `[bağlantı](https://…)` cevapta çizilir.
2. Aynı metin kullanıcı balonunda ham görünür.
3. `[x](javascript:alert(1))` bağlantı olmaz.
4. Ters tırnak arasındaki `**` kalın olmaz.
5. Akan metin de biçimli çizilir.
6. Balon ölçeği CSS'te yazılıdır; sayfa başlığı ölçüleri balonun içine sızmaz.

## 7 · Risk

Ayrıştırıcı bizim, dolayısıyla kenar durumları da bizim. Riski sınırlayan şey kapsamın kapalı
olması: listede olmayan sözdizimi ham metin olarak kalır, yani en kötü ihtimalle bugünkü davranış
sürer — bozulma değil, çizilmeme olur.
