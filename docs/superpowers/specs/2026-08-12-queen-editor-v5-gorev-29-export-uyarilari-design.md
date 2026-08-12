# Queen Editor v5 · Görev 29 — Export uyarıları ve pasiflik · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 8, Görev 29 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
89, 90, 91 · **Tür:** arka uç + ön yüz.

## Neden

Export ekranı bugün yalnız kaç video olduğunu söylüyor. Oysa export'un sessiz bıraktığı, diziye
hiç girmeyen ve daha üretilmemiş kareler var; kullanıcı bunları export'tan sonra fark ederse iş
zaten yazılmış olur.

## Ne olacak

Özet kartında koşul oluştukça kırmızı satırlar doğar. Kuyruk akarken export engellenir: iki buton
pasifleşir ve butonların hemen üstünde kendi kırmızı kartında sebep okunur. Kuyruk duraklatılınca
export serbest kalır ve bekleyen videolar yalnız bilgi satırı olur.

## Kararlar

### 1. Sayılar özetin, kuyruğun hâli işin

`export_summary` iki sayı daha söyler: **sesi olmayan video sayısı** ve **videosu olmayan kare
sayısı**. İkisi de galeriden çıkar, tek geçişte.

Kuyrukta kaç video beklediğini özet söylemez — onu ekran zaten `useGeneration`'dan okuyor
(kuyruk paneliyle aynı kaynak). Aynı sayıyı iki yerden sormak, bir gün ayrışacak iki cevap demek.

### 2. Satır ancak koşulu varsa doğar (madde 89)

Sayı sıfırsa satır hiç çizilmez — "0 videonun sesi yok" diye bir satır yoktur. Metinler tasarımın:

- "⚠ 16 videonun sesi yok"
- "⚠ 3 videosuz kare diziye girmeyecek"
- (kuyruk duraklatılmışken) "⚠ 5 karenin videosu kuyrukta bekliyor — diziye girmeyecek"

### 3. Üretim akarken export engel (madde 90, kullanıcı kararı)

Kuyruk akarken iki buton pasif olur ve butonların hemen üstünde **kendi kırmızı kartında** sebep
durur: "⚠ Üretim sürüyor — 5 video kuyrukta. Kuyruğun bitmesini bekle veya duraklat."

Kuyruk duraklatılınca export serbest kalır; bekleyen videolar o zaman kart değil, özetteki kırmızı
bilgi satırı olur (madde 89'un üçüncü satırı). Bu, fark belgesindeki çelişkinin kullanıcı kararıyla
kapanmış hâli.

Neden akarken engel: export dosyaları kopyalar; tam o sırada bir video yazılıyorsa export yarım bir
dosyayı da kopyalayabilir. Duraklatılmış kuyrukta yazan kimse yoktur.

### 4. Pasiflik kuralları (madde 91)

İki buton da şu hâllerde pasif: **export edilecek video yok** ya da **kuyruk akıyor**. Üçüncü koşul
("öteki buton çalışıyorsa") Görev 30'un işi — bu görevde hiçbir export koşmuyor.

### 5. Özet galeri değiştikçe tazelenir

Ekran açıkken kuyruk akmaya devam edebilir; sayılar donmuş kalırsa uyarılar yalan olur. Ekran
galerinin her tazelenişinde özeti yeniden sorar — istek küçük ve ekran başka bir iş yapmıyor.

## Nasıl görülür

1. Sesi olmayan videolu projede kartta kırmızı "⚠ N videonun sesi yok" satırı var; hepsi sesliyse
   satır yok.
2. Kuyruk akarken butonlar pasif ve üstlerinde kırmızı sebep kartı duruyor; duraklat → butonlar
   canlanıyor, sebep kartı yerini özetteki bilgi satırına bırakıyor.

## Testler

**Arka uç:** özet sessiz videoları sayar · videosuz kareleri sayar · sesi hatalı video sessiz
sayılır · videosuz kare sayısında bekleyen kareler de var.

**Ön yüz:** koşul yoksa satır yok · sessiz video satırı sayıyla · videosuz kare satırı · kuyruk
akarken iki buton pasif ve kırmızı kart okunur · duraklatılmışken butonlar serbest ve satır bilgi
olarak duruyor · video yokken pasiflik bozulmaz.

## Kapsam dışı

- **Export'un koşması, ilerleme, hata, çıkış onayı** — Görev 30.
- **"Öteki export çalışıyor" pasifliği** — Görev 30 (o zamana kadar koşan bir export yok).
