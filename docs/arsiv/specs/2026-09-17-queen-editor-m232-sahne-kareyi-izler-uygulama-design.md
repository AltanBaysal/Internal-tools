# Madde 232 · Kare değişince sahnede eski karenin dosyası kalmayacak — uygulama turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-17-queen-editor-m232-sahne-kareyi-izler-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Ne değişiyor

**Yeni bir bileşen: `Arriving.jsx`** *(`features/photo_generation/`)*. Tek işi bir dosyanın gelişini
izlemek:

- Çocuğuna iki işleyici veriyor: `onReady` ve `onFail`. Çocuk bunları kendi medya olayına bağlıyor
  *(`<img onLoad>`, `<video onLoadedData>`)*.
- Beklerken çocuğun yanına sahnenin ortasında `yükleniyor…` koyuyor. Kelime tıklamayı almıyor, yoksa
  oynatıcıya basılamazdı.
- Gelmezse çocuğu kaldırıp `StatusErrorCard`'ı `Dosya yüklenemedi` ve adresle çiziyor.

**Anahtar `Arriving`'in üstünde:** `` key={`${frame.id}/${open}`} ``. Kare ya da sekme değişince
`Arriving` ve içindeki medya baştan kuruluyor. Durum da kendiliğinden `yükleniyor…`'a dönüyor, yani
sıfırlamak için ayrı bir kod yok.

**`PhotoDetail`'de üç yer sarılıyor:** oynatıcı, üretim sürerken üstünde kutu olan fotoğraf, ve
üretilmiş fotoğraf.

**`LayerPlayer`** `onReady` ve `onFail` alıyor ve `<video>`'ya bağlıyor. Sekme değişince oynatmayı
sıfırlayan `useEffect` **siliniyor**, çünkü artık her sekme yeni bir oynatıcı kuruyor, ve yaptığı iş
kendiliğinden oluyor.

**Ses için ayrı bir bekleme yok.** Sahneyi video çiziyor, ses onun yanında çalıyor. Eski ses ise
anahtar sayesinde gidiyor.

## Seçilmeyen yol

- **Bütün sayfaya anahtar koymak.** Açık sekmeyi de sıfırlardı, oysa o bilerek korunuyor *(madde 38)*.
- **Eski medyayı `src` değişince elle gizlemek.** Bugünkü elle temizliğin medyaya taşınmış hâli olurdu:
  üç yerde, her birinde unutulabilecek bir kod.
