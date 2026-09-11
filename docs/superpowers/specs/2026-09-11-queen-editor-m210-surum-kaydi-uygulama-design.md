# Madde 210 — queen-editor'ün sürüm kaydı · uygulama turu

**Kaynak:** [yol haritasının Madde 210'u](../plans/2026-09-11-queen-editor-v5-roadmap.md) ·
**Test turu:** [spec](2026-09-11-queen-editor-m210-surum-kaydi-testler-design.md), kırmızısı
`e820c50`.

> **Yön değişti — kullanıcı kararı, 11 Eylül.** İlk uygulama ayrı bir kayıt dosyası yazdı
> (`SURUMLER.md`, `b5eed21`). Kullanıcı onu istemedi, ve sebebi kaydın kendisini gereksiz kılıyor:
> **ad kayıt olacak.** Bir belgenin adındaki numara onun sürümü olacak, o zaman soruyu cevaplamak
> için ayrı bir dosyaya bakmaya gerek kalmıyor. Aşağısı bu karara göre yeniden yazıldı.

## Neye varılacak

**Bir sürüm, bir dal, bir yol haritası — ve o haritanın adı sürümünü söyler.**

Bugün on üç belge var, dört dala dağılmış, ve adlarının onikisi kendi sürümü olmayan bir numara
taşıyor. `queen-editor-v5-roadmap` adında **iki** dosya var. Ad kayıt olacaksa bu hâliyle olamaz.

On üç belge beşe iner:

| Sürüm | Dal | Birleşen belgeler |
|---|---|---|
| v1 | `feat/queen-editor-v1` | eski v2, v3 |
| v2 | `feat/queen-editor-v2` | eski v4 |
| v3 | `feat/queen-editor-v3` | eski v5, v6, v7, v8, v9, v11, v12, v13 |
| v4 | `feat/queen-editor-v4` | eski v14 |
| v5 | `feat/queen-editor-v5` | bu koşu — adı zaten doğru |

**Eski v2'nin dalı belgesinde yazmıyor ve ölçülemiyor.** Onu ekleyen commit `01344b0`,
`feat/queen-editor-v1`'in geçmişinde duruyor; queen-editor'ün ilk dalı da o, yani işi v1'in
kuşağında. Birleştiği yer bu; belirsizlik birleşen belgenin kendi bölümünde yazılı kalıyor.

## Metin nasıl birleşir

Her eski belge, birleştiği dosyada **kendi bölümü** olur: başlığı, tarihi, dalı ve madde tablosu
olduğu gibi iner. Koşu sınırları silinmiyor — başlığa dönüşüyor.

**Madde numaraları kaymıyor**, ve bu birleşmenin tek zor yeri: eski belgelerin her biri kendi
görevlerini 1'den saymış, yani tek dosyada aynı numara sekiz kez geçiyor. Numara bölümüne aittir ve
öyle okunur — *"v3 · koşu 4 · görev 7"*. Yazılmış spec'ler zaten belgenin adıyla birlikte atıf
yapıyor; onları taşıyan referans düzeltmesi de bölüme kadar götürüyor.

## Referanslar

Eski adlara atıf yapan **136 dosya** var — spec'ler, görev planları, araştırma belgeleri. Hepsi yeni
ada çevrilir. Kırık bir bağlantı bırakmak, kaydı düzeltmek için kaydı okunmaz yapmak olurdu.

## Testler ne tutar

Kayıt dosyası kalkınca iddialar da değişiyor. Tutulan şey artık **adın kendisi**:

| # | Ne |
|---|---|
| 1 | Hiçbir sürüm numarası iki belgede birden geçmiyor — bir sürüm, bir yol haritası |
| 2 | Her yol haritasının başlığındaki dal, adındaki sürümle aynı: `v3-roadmap` → `feat/queen-editor-v3` |
| 3 | Depoda var olmayan bir yol haritasına atıf yok — birleşmeden sonra kırık bağlantı kalmamış |
| 4 | CLAUDE.md güncel sürümü *"en yüksek vN"* diye tarif etmiyor |

**Birincisi bugünkü karmaşayı tarif ediyor:** iki dosya birden v5 diyor.

**İkincisi adı dala bağlıyor.** Ad kayıtsa, yalan söyleyemediği bir şeye bağlanmalı; dal adı belgenin
kendi başlığında zaten duruyor.

**Üçüncüsü birleşmenin bedelini tutar.** Sekiz dosya silinince onlara giden her bağlantı kırılır; test
tek tek sayar.

## Dokunulmayanlar

- **Maddelerin metni.** Birleşme kopyalamadır, yeniden yazma değil.
- **`dist`** — bu madde ön yüze hiç dokunmuyor.
- **QueenAgent'ın belgeleri.** Onun adları kendi sayacıyla tutarlı.

## Nasıl görülür

```bash
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Dördü de yeşil, ön yüz süiti değişmemiş.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-11-queen-editor-m210-impl-plan.md).
