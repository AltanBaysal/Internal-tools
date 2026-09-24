# Madde 323 — Prompt listesi fotoğraf panelinin okuduğu gibi okunuyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7-kol-b` *(Kol B)* · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m323 test turu](2026-09-24-queen-editor-m323-prompt-listesi-okunusu-testler-design.md),
`ba83282f`.

## Sunucu

Değişmiyor. Havuz kapısı listeyi zaten `parse_prompts`'la okuyor *(`queue_references.py`)*; iki
cümle de orada, tek yerde.

## Ekran — yalnız `LayerPanel.jsx`

- **`promptsIn` gidiyor, yerine `promptCount(text)`** — bir sayı: basış kaç prompt gönderir, ya da
  ekran söyleyemiyorsa 0. Liste değil sayı, çünkü öğeler çözülmüyor *(kaçışlar atlanıyor, açılmıyor)*;
  çözülmemiş metni "prompt'lar" diye döndürmek, bir gün onu kullanacak birini yanıltırdı. Okuyuşu
  `prompt_list.py`'ninki, sayıma yetecek kadar:
  - baştaki ve sondaki boşluk atılıyor, önde isteğe bağlı `AD =` düşüyor — sunucunun
    `_ASSIGNMENT`'ının aynı deseni;
  - gövde `[`…`]` ya da `(`…`)`;
  - içi tırnaklı öğeler, virgülle ayrılmış, sonda isteğe bağlı virgül; iki tırnak da. Ters bölü
    ardındaki karakteri yanına alıyor, yani kaçışlı bir tırnak öğeyi bitirmiyor;
  - boş öğe sayılmıyor.

  **JSON ayrı okunmuyor:** bir dizi dolusu JSON metni, Python listesinin aynı biçimi — tek döngü
  ikisini de okuyor, `JSON.parse` gerekmiyor. Başka her şey — tırnaksız metin, sayı, iç içe liste,
  çift virgül — 0.
- **Önizleme, kural değil** *(FOUNDATION 4)*. Yalnız Python'un okuduğu köşeler — üç tırnaklı öğe,
  yan yana iki metnin birleşmesi, tek öğeli `("a")`'nın tuple değil metin olması — burada ya boş satır
  ya da fazladan bir sayı. İkisi de zararsız: basış önizlemenin dediğine bakmadan gidiyor, ve kararı
  sunucu veriyor. Bu köşeleri kovalamak önizlemeyi ikinci bir ayrıştırıcıya çevirirdi.
- **Satır:** Referanstan'da `promptCount` sıfırdan büyükse `N prompt × M varyant = K kart`, değilse
  hiçbir şey — Kareden'in tahminine düşmeden. Varyant kutusu boşken bugünkü gibi `× 0 varyant`.
- **`NO_PROMPTS` ve onu kullanan her yol gidiyor:** sabit, satırdaki son seçenek, ve
  `refusalOf`'un havuz dalı. `refusalOf` artık `prompts` almıyor; havuzdan basışı hiçbir şey
  durdurmuyor — varyant kutusunun boşluğu dışında, ki o kural havuzdan önce, bugünkü yerinde
  duruyor. Havuzdan gelen ret sunucunun: `error` olarak gelip kırmızı kartta duruyor, bugünkü gibi.

## Dist

Kolda derlenmez — [yol haritası](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md), *320–324 iki
paralel kolda*: birleşme commit'i bir kez derler.

## Bitti sayılır

Dört test satırı yeşil — koordinatör koşuyor; kod, spec ve plan tek commit.
