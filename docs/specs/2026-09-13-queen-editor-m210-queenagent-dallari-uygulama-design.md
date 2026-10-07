# Madde 210 · QueenAgent'ın dalları — uygulama turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Test turu:** [tasarım](2026-09-13-queen-editor-m210-queenagent-dallari-testler-design.md) ·
[plan](../plans/2026-09-13-queen-editor-m210-queenagent-dallari-test-plan.md) · kırmızı `5664ecb`

## Kırmızının söylediği

```
Başlığında dal adı olmayan yol haritası: 2026-09-06-queen-agent-v8-roadmap.md
Aynı dalı sahiplenen birden çok yol haritası:
  {'fix/mira': ['2026-08-15-queen-agent-v2-roadmap.md', '2026-08-18-queen-agent-v3-roadmap.md']}
```

İki kırmızı, üç iş: v7'nin ikinci dalı çiviyle tutulmuyor *(test turu bunun sebebini yazdı — `git`
referansları deponun metni değil)* ama aynı kusurun üçüncü yüzü, ve bu turda düzeliyor.

## v2 ile v3 tek belge olur

**Kalan dosya `2026-08-15-queen-agent-v2-roadmap.md`.** İki sebep: sürümün açıldığı gün onun
adındaki gün, ve gövdesi ötekinin dört katı *(37 maddeye karşı 15)* — büyük olanı yerinde tutmak
taşınan metni en aza indiriyor.

Desen queen-editor'de kurulanın aynısı: belge başlığı, dalı veren başlık bloğu, birleşmeyi anlatan
bir not, `---`, sonra her koşu kendi `# Koşu N — <gün> *(o zamanki adıyla "vN")*` başlığı altında.
Koşuların gövdesi **olduğu gibi** kalıyor; `##` ve `###` seviyeleri zaten `#`'in altına giriyor, yani
tek bir başlık bile kaymıyor.

Madde numaraları da olduğu gibi: Koşu 1 → 1–37, Koşu 2 → 38–52. v3'ün kendi cümlesi
*"Numaralar v2'den devam eder"* zaten bunu söylüyordu — birleşme onu bir belge içinde doğru kılıyor.

## v3 numarası boş kalır

Birleşince o numara kimsede durmuyor, ve **kaydırılmıyor**. Sebep dal adlarının kendisi:
`feat/queenagent-v5`, `feat/queenagent-v7`, `feat/queenagent-v8` numaralarını adlarında taşıyor, ve
aşağı kayan her belge kendi dalıyla çelişirdi — testin üçüncü çivisi de tam bunu tutuyor.

Boşluk belgenin başındaki notta yazılı duruyor; açıklanmış bir boşluk, kaymış bir numaradan iyidir.
queen-editor'ün kaydında da aynı türden bir cümle var: *"v10 diye bir yol haritası yok."*

## Yirmi iki atıf: hem yol hem metin değişir

v3'ün yol haritasına 22 spec ve plan bağlanıyor, hepsi aynı biçimde: `**Madde:**` etiketinin ardından
*"v3 yol haritası Madde 45"* yazan bir bağlantı, hedefi de `../roadmaps/2026-08-18-queen-agent-v3-roadmap.md`.

Yalnız yolu çevirmek yetmez: bağlantı **metni** de *"v3 yol haritası"* diyor, ve v3 diye bir belge
kalmayınca o metin okuyucuya olmayan bir şeyi gösterir — bağlantı çözülür, cümle yalan söyler. İkisi
birden değişiyor: metin *"v2 yol haritası Koşu 2 · Madde 45"*, hedef
`../roadmaps/2026-08-15-queen-agent-v2-roadmap.md`.

*(Bu iki yol burada bilerek bağlantı olarak değil, düz metin olarak yazıldı: bağlantı çivisi kod
bloğuna bakmıyor, parantez içinde bir yol haritası adı gördüğü her yerde onu çözmeye çalışıyor —
silinmiş bir adı örnek diye göstermek onu kırık bağlantı sayardı. Bu cümlenin ilk hâli kalıbı harfi
harfine yazdığı için kendi çivisine takıldı.)*

Koşu adının metne girmesi, birleştirilmiş bir belgede maddenin hangi bölümde olduğunu söylüyor —
queen-editor'ün birleşmesinde de bağlantı metinleri bölüm adına dönmüştü.

**Spec'lerin kendi `**Branch:** `fix/mira`` satırlarına dokunulmuyor.** O satırlar o spec'in
yazıldığı dalı söylüyor ve doğru söylüyorlar; sürüm numarasıyla ilgileri yok.

## v8 dalını söyler, v7 ikinci dalını söyler

- **v8:** başlığında hiç dal satırı yok. `feat/queenagent-v8` ekleniyor, merge commit'i `356d605` ile
  — belge zaten kapanmış bir koşunun kaydı, ve kapanışı doğrulayan şey o commit.
- **v7:** `feat/queenagent-v7`'nin yanına `feat/queenagent-v7.5` giriyor, 180–182 maddelerinin orada
  koşulduğu notuyla. Biçim v5'ten alınıyor — o belge aynı durumu *(`feat/queenagent-m123-skill-rewrite`,
  124–132)* zaten doğru yazmış, ve iki yerde iki ayrı biçim kaydı okunmaz kılar.

İkinci dal başlık satırının **sonuna** yazılıyor, başına değil: çivi satırdaki ilk dalı belgenin dalı
sayıyor, ve v7'nin dalı `feat/queenagent-v7`.

## v4'ün numara cümlesi

`2026-08-20-queen-agent-v4-roadmap.md` *"Numaralar v3'ten devam eder (52'de bitti)"* diyor. v3 artık
bir belge değil; cümle **Koşu 2**'yi gösterecek. Olgu değişmiyor — 52'de biten koşu aynı koşu — yalnız
adı bugün başka.

## Dokunulmayanlar

- **Dal adları.** `fix/mira`, `feat/queenagent-colab`, `feat/v6` oldukları gibi kalıyor. Geçmişe dönük
  düzeltilemezler, ve düzeltilmeleri gerekmiyor: kayıt dalın adından değil, belgenin dalını
  söylemesinden doğuyor.
- **v4 ile v6'nın numarasız/toolsuz dalları** kusur değil; her birinin tek yol haritası var.
- **Koşu gövdeleri.** Metinler taşınıyor, yazılmıyor.
