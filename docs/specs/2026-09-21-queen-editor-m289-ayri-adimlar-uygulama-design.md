# Madde 289 · Videolar, fotoğraflar, disclaimer — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m289-ayri-adimlar-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**Tek döngü ikiye bölünüyor**, ve ikisi de aynı listeyi aynı sırayla geziyor
*(`enumerate(frames, start=1)`)* — numaralandırmanın değişmemesi bundan: numara döngünün değil
**karenin sırası**.

- **Birinci döngü:** parçayı kes, `pieces`'a ekle, `written=index` bildir.
- **İkinci döngü:** fotoğrafı kopyala, aynı numarayla, aynı *"bir kez"* kuralıyla *(236)*.
- **Sonra:** birleşik modda birleştirme ve Drive'a kopyalama — olduğu gibi.

## İptal: iki döngü, tek çıkış

İptal kontrolü ikinci döngünün de başında duruyor, ve iki yerde aynı dört satırı tekrarlamamak
için **kendi işlevine** taşınıyor:

```
_stopped(runner, store, mode, folder, scaffolding) -> bool
```

İptal edilmişse iki klasörü de siliyor, ekrana `idle` bildiriyor ve `True` dönüyor; çağıran
`None` dönüyor. İşin neden **birimler arasında** kesildiği — yarım bir dosya, hiç olmayan bir
dosyadan kötüdür — artık bir yerde yazılı, iki yerde değil.

**Yeni bir kural değil**, bugünkü satırların adı konmuş hâli.

## Değişmeyen

- **Numaralandırma ve paylaşılan fotoğraf.** `written` kümesi ikinci döngüye taşınıyor, kuralı
  aynı: bir fotoğraf bir kez, ve ilk kullanan karenin numarasıyla *(236)*.
- **Ekran.** `written` videoları sayıyor, `total` kare sayısı. Fotoğraf evresinin kendi adı
  **yok** — 287'nin işi, ve test turunun spec'inde sebebiyle yazılı.
- **Hata yolu.** Herhangi bir adım patlarsa `_clean` iki klasörü de götürüyor *(94)*.
- **`exporter`, `store`, `runner` arayüzleri.** Bu madde hiçbirine dokunmuyor.

## Bunun getirdiği

**Çıkan dosyalar birebir aynı.** Değişen tek şey yazılma sırası — ve **287 artık mümkün:**
ölçülecek iki ayrı adım var.

**Bedeli, açıkça:** ayrı export'ta kullanıcı artık videoları bir arada görüyor ama fotoğrafları
sonra; yarıda iptal edilen bir koşuda zaten iki klasör de gidiyor, yani yarım bir set kalmıyor.

## Bu turda değişen

- `domain/usecases/run_export.py`: döngü ikiye bölünüyor, iptal kontrolü kendi işlevine geçiyor.
