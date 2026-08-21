# v14 · Görev 5 — Sonrakine bağla ardışık seçim istiyor · **test turu**

**Kaynak:** [Yol haritası v14, 5. madde](../plans/2026-08-20-queen-editor-v14-roadmap.md) ·
[4. maddenin uygulama turu](2026-08-21-queen-editor-v14-gorev-4-mod-secicisi-uygulama-design.md)

Bu tur yalnız testleri yazar. Takım kırmızı biter ve kırmızı commit edilir; kodu ikinci tur yazar.

## Neyi kilitliyoruz

4. madde üç modu da her koşulda kabul eden bir seçici bıraktı. Bağlamanın anlamı bir **zincir**:
her karenin videosu bir sonrakinin fotoğrafında bitiyor, ve o sonraki karenin videosu da kendi
sonrakine bağlanıyor. Zincir ancak seçilen kareler galeride bitişikse kapanıyor; arada seçilmemiş
bir kare varsa, iki ayrı parça çıkıyor ve ikisi de seçimin dışındaki karelere bağlanıyor.

Bu tur o kuralı ekrana koyuyor: dağınık seçimde seçenek kapanıyor ve altında neden kapandığı tek
satır yazıyor.

## Kararlar

**1. Kural kapsama bağlı, seçime değil.** Panel "Seçili kareler" kapsamındayken seçilen karelerin
bitişikliği kural. "Videosu olmayanlar" kapsamındayken seçenek açık kalıyor: o küme doğası gereği
dağınık — aradaki kareler zaten videosu olanlar — ve orada her karenin kendi sonrakine bağlanması
anlamlı bir iş.

Kuralı seçime bağlamak, kullanıcı dağınık seçip sonra kapsamı "Videosu olmayanlar"a çevirdiğinde
seçeneği hâlâ kapalı tutmak olurdu — kuyruğa gidecek kümeyle ilgisi olmayan bir sebeple.

**2. Bitişiklik galerinin tamamına göre ölçülüyor.** Üretilebilir karelere göre değil: motor da
hedefi galerinin sırasından okuyor, ve arada duran fotoğrafsız bir kare zincirin gerçek boşluğu.

**3. Tek kare bitişiktir.** Atlanacak bir şey yok.

**4. Yön önemsiz.** Bitişiklik simetrik: galerideki konumları kesintisiz bir dizi oluşturuyorsa
bitişiktir. Filmin hangi yöne aktığı (2. maddede kararlaştırıldı: galerinin dibinden tepesine) bu
kuralı değiştirmiyor.

**5. Kapanan seçenek seçili kalamaz.** Bağla seçiliyken seçim dağılırsa mod Standart'a düşüyor.
Yoksa tıklanamayan bir satır kuyruğa girmeye devam ederdi — ve galeri, panelin ikinci bir tıklama
duymadan haberdar olduğu tek yer.

**6. Sebep tek satır, seçeneğin altında.** Metin: **"Zincir ancak bitişik karelerde kapanır —
arada seçilmemiş kare var."** Ne olduğunu değil neden olduğunu söylüyor; "ardışık seç" tek başına
kullanıcının zaten gördüğü şeyi tekrar ederdi.

## Yazılacak testler

`frontend/src/features/photo_generation/LayerPanel.test.jsx`, yeni bir öbek:

| # | Test | Ne diyor |
|---|---|---|
| 1 | `closes the option when the chosen frames are not neighbours` | Satır tıklanamıyor |
| 2 | `says why, in one line, under the option it closed` | Sebep görünüyor |
| 3 | `opens the option again when the hole is closed` | Bitişik seçimde açık, sebep yok |
| 4 | `leaves the option open when the scope is every frame with no video` | Seçimsiz kapsamda açık |
| 5 | `counts one frame as neighbours of itself` | Tek kare açık |
| 6 | `drops back to the plain mode when the selection breaks apart under it` | Kuyruğa `standard` gidiyor |

## Kırmızının biçimi

Satır bugün her koşulda açık: 1. ve 6. test `disabled` yerine `false`, `standard` yerine `linked`
buluyor; 2. test sebebi hiç bulamıyor. **3, 4 ve 5 yeşil doğuyor** — kuralın fazla geniş
yazılmamasını onlar tutuyor, ve bir kuralın nerede *durmadığını* söyleyen test kırmızı doğmak
zorunda değil.
