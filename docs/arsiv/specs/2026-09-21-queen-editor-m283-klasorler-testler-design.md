# Madde 283 · Tekli çıktılar kendi klasörüne — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Klasör adları kullanıcının onayladığı adlar: `video/` ve `foto/`.

## Düzeltme: ortada sanıldığı kadar kalabalık yok

Kullanıcıya *"tek klasörde 44 dosya"* denmişti; **yanlıştı.** `copy_photo` fotoğrafları zaten
`photos/` alt klasörüne yazıyor *([photo_store.py:97](../../../queen-editor/backend/features/photo_generation/data/photo_store.py#L97))*.
Bugünkü gerçek durum, 22 karelik bir projede:

| Mod | Tarihli klasörün içi | Girdi |
|---|---|---|
| tekli | `01.mp4 … 22.mp4` + `photos/` | **23** |
| birleşik | `düğün.mp4` + `photos/` | **2** |

**Sonucu maddeyi küçültüyor:** birleşikte yapılacak hiçbir şey yok *(kullanıcı da öyle dedi —
"birleşiğin klasöre ihtiyacı yok tek file zaten")*, ve teklide iş videoları toplamak.

## Çivilenen olgular

**1 · Tekli export videolarını `video/` altına yazıyor.** Tarihli klasör iki isme iniyor:
`video/` ve `foto/`.

**2 · Fotoğrafların klasörü `foto/` oluyor.** Bugün `photos/`, ve kullanıcının onayladığı
isimlendirme Türkçe — Drive'da gördüğü ad, yani kullanıcıya bakan metin *(CODE-STANDARD:
kullanıcının gördüğü şey Türkçe)*. **Eski export'lar etkilenmiyor:** her export kendi tarihli
klasörüne yazıyor, eskiler `photos/` adıyla olduğu gibi duruyor.

**3 · Birleşik export'un mp4'ü kökte kalıyor**, ve fotoğrafları yine `foto/`'da.

**4 · Numaralar değişmiyor** *(236)*: `foto/03.png` hâlâ `video/03.mp4`'ün fotoğrafı.

**5 · Tekli export hiçbir şey silmiyor** — ve **bu maddenin tuzağı tam burada.** Bugün başarılı
koşunun sonunda `cutting != folder` ise o klasör siliniyor; kural birleşik modun `/tmp`'deki
parçaları için yazılmıştı *(235)*. Videolar bir alt klasöre girince koşul **tekli modda da
sağlanır**, ve o zaman kural **kullanıcının teslim edilen videolarını siler**. Koşul moda bağlanmak
zorunda. FOUNDATION 1'in tam ortası, ve bu yüzden kendi testi var.

**6 · Düşen bir tekli export yine tarihli klasörü götürüyor** *(madde 94)*, ve içindeki `video/`
onunla gidiyor.

**7 · Birleşik export parçalarını yine silip gidiyor** *(235)*.

## Kırmızı: sekiz, ve tahmin yine küçüktü

Spec üç bekliyordu, takım **sekiz** verdi. Sebebi tek: tekli export'un **yolu** değişince o yolu
okuyan her test düştü — numaralandırma, kopya karenin videosu, parçaların nereye yazıldığı,
kopyalamanın dokunulmazlığı, düşen export'un temizliği ve hatanın kendi cümlesi. Altısı aynı
değişikliğin altı yüzü, ve hepsi tek satırla dönecek.

**5. olgunun testi yeşil**, beklendiği gibi: bugün silen bir şey yok. Yazılmasının sebebi uygulama
turunda **kırmızıya dönebilmesi** — koşul moda bağlanmazsa kullanıcının videoları silinir.

**Yol haritasının kaydı:** bu koşuda tahmin beş kez tutmadı, dördünde sayı büyük çıktı. Düzeltilen
şey her seferinde spec oldu.
