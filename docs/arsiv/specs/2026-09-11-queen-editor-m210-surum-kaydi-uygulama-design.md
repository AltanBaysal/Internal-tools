# Madde 210 — queen-editor'ün sürüm kaydı · uygulama turu

**Kaynak:** [yol haritasının Madde 210'u](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
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

## Yol haritaları kendi klasörüne taşınır

*(Kullanıcı kararı, 13 Eylül — aynı maddenin içinde.)*

`docs/superpowers/plans/` bugün **~1000 dosya** taşıyor ve bunların **14'ü** yol haritası; gerisi
görev planları. İki ayrı tür belge aynı torbada: biri *harita*, öbürü *adım*.

Taşınma kaydın kendisini tamamlıyor. 210'un vardığı yer **"ad kayıttır"**; ad ancak bulunabildiği
kadar kayıt. `docs/superpowers/roadmaps/` klasörünü listelemek doğrudan v1…v5'i verir — bugün aynı
soruyu sormak bin dosyalık bir listeye bakmak demek.

**Abartılmıyor:** hepsi zaten `-roadmap.md` ile bitiyor, yani bir glob bugün de buluyor. Kazanç
keşfedilebilirlik, mimari değil. Aynı maddede yapılmasının sebebi de bu — ayrı bir iş değil, aynı
kaydın ikinci yarısı.

**Üç tool birden taşınıyor**, 14 belgenin hepsi: queen-editor'ün beşi, QueenAgent'ın altısı, mira'nın
biri, depo geneli v6, ve tarihsiz ilk queen-editor haritası. Yarısını taşımak iki kural bırakırdı.

### Bağlantılar bu kez ad değil yol

Ad değişmiyor, **yol** değişiyor — ve yol kaynağa göre farklı yazılmış. Derinlik aynı kaldığı için
(`docs/superpowers/<klasör>/`) değişen tek şey kardeş klasörün adı:

| Nereden | Bugün | Sonra |
|---|---|---|
| `plans/` içindeki bir görev planından | çıplak ad | `../roadmaps/<ad>` |
| `specs/`, `research/` içinden | `../plans/<ad>` | `../roadmaps/<ad>` |
| `CLAUDE.md`, `queen-editor/*.md` | `docs/superpowers/plans/<ad>` | `docs/superpowers/roadmaps/<ad>` |
| Yol haritasının kendi içinden başka bir haritaya | çıplak ad | çıplak ad *(değişmiyor)* |
| Yol haritasından bir görev planına | çıplak ad | `../plans/<ad>` |
| Yol haritasından `../specs/`, `../../../queen-editor/` | aynı | aynı *(derinlik değişmiyor)* |

Son iki satır taşınmanın asıl riski: **harita kendi içinden dışarı bakan bağlantıları da kayıyor.**
Bir öncekinde yalnız adlar değişmişti; burada iki yön birden var.

## Testler ne tutar

Kayıt dosyası kalkınca iddialar da değişiyor. Tutulan şey artık **adın kendisi**:

| # | Ne |
|---|---|
| 1 | Hiçbir sürüm numarası iki belgede birden geçmiyor — bir sürüm, bir yol haritası |
| 2 | Her yol haritasının başlığındaki dal, adındaki sürümle aynı: `v3-roadmap` → `feat/queen-editor-v3` |
| 3 | Bir yol haritasına giden her bağlantı, **yazıldığı dosyaya göre çözülüp** gerçekten bir dosyaya varıyor |
| 4 | CLAUDE.md güncel sürümü *"en yüksek vN"* diye tarif etmiyor |
| 5 | Yol haritaları `roadmaps/` altında duruyor, `plans/` altında tek bir harita kalmamış |

**Birincisi bugünkü karmaşayı tarif ediyor:** iki dosya birden v5 diyor.

**İkincisi adı dala bağlıyor.** Ad kayıtsa, yalan söyleyemediği bir şeye bağlanmalı; dal adı belgenin
kendi başlığında zaten duruyor.

**Üçüncüsü iki bedeli birden tutar, ve bu yüzden güçlendirildi.** İlk hâli yalnız *adın* bir dosyaya
denk gelip gelmediğine bakıyordu; klasör taşınmasında ad değişmiyor, **yol** değişiyor, yani o iddia
taşınmayı hiç görmezdi. Yenisi bağlantıyı yazıldığı dosyaya göre çözüyor — birleşmede silinen sekiz
dosyayı da, taşınmada kayan her yolu da aynı iddia yakalıyor.

**Beşincisi taşınmanın yarım kalmasını engelliyor.** `plans/` altında kalan tek bir harita iki kural
demek, ve ikinci kural bir sonraki koşuda yazılanın nereye gideceğini belirsiz bırakır.

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
