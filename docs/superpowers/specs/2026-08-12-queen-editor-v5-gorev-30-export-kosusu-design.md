# Queen Editor v5 · Görev 30 — Export koşusu · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 8, Görev 30 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
92, 93, 94, 96 · **Tür:** arka uç + ön yüz.

## Neden

Export ekranı duruyor ama butonları hiçbir şey başlatmıyor. Bu görev export'u gerçekten koşturur:
Drive'a tarihli klasör açar, videoları yazar, ilerlemesini butonun yerinde söyler.

## Kararlar

### 1. Videoyu ffmpeg yazar, use case ne yazılacağını söyler

Domain hangi karelerin gireceğini ve dosyaların adını bilir; kesip birleştirmeyi bir port yapar:

```python
class VideoExporter(Protocol):
    def piece(self, video: str, audio: str | None, target: str) -> None:
        """One frame's video at `target`, with its sound laid over it when there is one."""

    def merge(self, pieces: list[str], target: str) -> None:
        """The pieces, in the order given, as one file."""
```

Data katmanındaki karşılığı ffmpeg'i çağırır (Colab'da kurulu). Testler sahte port kullanır —
gerçek ffmpeg'i koşturan bir test, makinede ffmpeg olmasını şart koşardı.

### 2. Klasör tarihle açılır, dosyalar galeri sırasıyla numaralanır (madde 92)

`<proje>/export/<YYYY-MM-DD HH-MM>/`. Ayrı export `01.mp4 … 22.mp4` yazar — numara galeri
sırasındandır ve `01` dizinin başıdır (galerinin ayağı). Birleşik export proje adıyla tek dosya
yazar: `düğün.mp4`.

Aynı açılışın iki export'u aynı klasöre yazar (klasör adı dakikaya kadar iner ve zaman damgası
koşu başında alınır); adlar çakışmadığı için eskiler ezilmez.

Dosyalar kopyadır: proje klasöründeki orijinaller yerinde kalır, videosuz kareler atlanır, sesli
kareler sesiyle girer.

### 3. Koşu oturuma bağlı ve kendi işçisinde (madde 93, 96)

Export üretim kuyruğundan ayrı bir işçide koşar; ikisi birbirini beklemez ve **iki export aynı anda
koşabilir** (biri birleşik, biri ayrı). Durum bellekte tutulur — export oturuma bağlıdır, arka
planda sürmez ve sunucu ölürse yarım klasör kalmaz (silinir).

Ekran durumu `GET /api/projects/<p>/export/status` ile okur: her mod için
`{state: idle|running|done|error, written, total, target, error}`.

### 4. İlerleme butonun yerinde okunur (madde 93)

Basılan butonun yerinde canlı nokta + "7 / 22 yazıldı…" (birleştirme adımında "birleştiriliyor…").
Yüzde ve çubuk yok. Öteki buton basılabilir kalır. Bitince tam genişlikte yeşil kartta
"✓ Export tamamlandı" ve altında yazılan dosya → hedef satırı.

### 5. Hata baştan başlatır (madde 94)

Hata olunca yarım klasör silinir — arayüz bunu söylemez. Kırmızı kartta "Export başarısız" ve tek
satır teknik sebep (ffmpeg'in kendi çıktısı) okunur. Ayrı bir "Tekrar dene" yok: butonlar
yerindedir ve yeni basış yeni tarih klasörü açar.

### 6. Çıkmak export'u iptal eder (madde 96)

Export sürerken "Galeriye dön"e basınca 380 piksellik onay: "Export sürüyor — çıkılsın mı?
Çıkarsan export iptal olur, yarım kalan klasör silinir. Galerine ve karelerine dokunulmaz."
Onaylanınca koşu durur, klasör silinir. Yıkıcı sayılmadığı için buton kırmızı değil, vurgulu.

İptal isteği `POST /api/projects/<p>/export/cancel`. Koşu iki parça arasında durur: ffmpeg'in
ortasında kesmek yarım dosya bırakır, ve zaten silinecek klasörde bir parça daha yazılması bir şeyi
değiştirmez.

## Nasıl görülür

1. "Videoları ayrı export et" → buton yerinde "1 / 3 yazıldı…" → yeşil kart; Drive'da tarihli
   klasörde `01.mp4 02.mp4 03.mp4`.
2. Birleşik export → "birleştiriliyor…" → klasörde `düğün.mp4`.
3. ffmpeg patlarsa kırmızı kartta sebebi okunuyor ve klasör diskte kalmıyor.
4. Koşarken çıkışa basınca onay çıkıyor; onaylayınca export duruyor.

## Testler

**Arka uç:** ayrı export her videoyu galeri sırasıyla numaralar · sesli kare sesiyle yazılır ·
videosuz kare atlanır · birleşik export tek dosya yazar · aynı klasöre ikinci export ezmez ·
hata klasörü siler ve sebebi taşır · iptal koşuyu durdurur ve klasörü siler · durum ilerlemeyi
sayar.

**Ön yüz:** basınca ilerleme butonun yerinde · öteki buton basılabilir · bitince yeşil kart ve
hedef satırı · hata kırmızı kartta · koşarken çıkışta onay ve iptal · boş/akan kuyrukta pasiflik
bozulmaz.

## Kapsam dışı

- **Video süresinin ölçülmesi** — süre sabit (Görev 28).
- **Export'un arka planda sürmesi** — tasarımın kendi kararı: oturuma bağlı.
