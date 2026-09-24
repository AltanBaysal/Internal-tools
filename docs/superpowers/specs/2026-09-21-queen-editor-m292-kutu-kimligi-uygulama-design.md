# Madde 292 — Kutu kimliği, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m292 test turu](2026-09-21-queen-editor-m292-kutu-kimligi-testler-design.md),
`6635f6d7` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## Tek dosya değişiyor

`backend/features/photo_generation/domain/usecases/list_frames.py`. Domain katmanı, saf kural
*(CODE-STANDARD: `domain/` dışarıdan hiçbir şey import etmez)*, ve bu maddenin bütün işi orada
duruyor — kayıt zaten `(kart, yuva)` ile çalışıyor, plan zaten işin tipini taşıyor.

## Kural

**Kartı açan iş, planda o kimlikle görünen ilk iştir.** Satır ondan okunur:

```
opening = {}                          # plan sırasında, kimlik başına ilk iş
for job in planned:
    opening.setdefault(job["id"], job)
```

Sonra galeri bugünkü gibi **tersten** yürünür *(galeri en yeniyi üste alır)*, ve bir iş yalnız
**kartı açan iş oysa** satır açar; sonrakiler o kartın katmanıdır. Bugünkü `type_of(frame) != PHOTO`
kontrolü bunun yerini alıyor.

Kartın **durumu** açan katmanın yuvasından okunur: `cells.get(type_of(opening))`. Bugünkü kartlarda
o katman fotoğraftır, yani hiçbir şey kıpırdamaz.

## Kıpırdamayacak üç şey

**1. `file`.** Bugünkü anlamını koruyor: fotoğraf yuvası doluysa onun dosyası, değilse kimliğin
verdiği ad. Açan katmana bakmıyor — bu alan ekranda seçimin ve saklanan sıranın anahtarı, ve kimliğin
saf bir fonksiyonu olması onu fotoğrafsız kartta da geçerli kılıyor.

**2. Satırın yeri.** Kart, açan işinin planda durduğu yerde görünür. Bugünkü kartlarda açan iş zaten
fotoğraf işi olduğu için sıra birebir aynı kalır.

**3. Planın bilmediği fotoğraflar.** İkinci döngü olduğu gibi duruyor.

## Prompt

`_words` üçüncü bir argüman alır: açan katmanın adı. Planın `prompt` alanı bugün her zaman
`prompts["photo"]`'ya düşüyor; artık **açan katmanın anahtarına** düşer. Varsayılanı `photo`, yani
onu çağıran başka bir yer olsa bile davranışı değişmez.

## Belgeler

Dosyanın başındaki açıklama bugün *"Yalnız fotoğraf yuvası bir karenin burada olup olmadığına karar
verir"* diyor — kod değiştiğinde o cümle yanlış olur, ve **çelişkide yorum koda uydurulur** *(stil
kuralı)*. Yerine kutu kuralı yazılır: kartı açan katman satırı açar, ve fotoğraf özel değildir.

## Bitti sayılır

`python -m pytest queen-editor -q` yeşil — turun beş testi dönüyor, ve 953 testin hiçbiri düşmüyor.
Dört satırın dördü de koşulur.
