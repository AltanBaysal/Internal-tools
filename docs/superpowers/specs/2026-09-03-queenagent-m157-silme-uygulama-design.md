# Madde 157 — Silme araçları · **uygulama turu**

**Tarih:** 3 Eylül 2026 · **Branch:** `feat/v6` · **Test turu:**
[m157 silme testler design](2026-09-03-queenagent-m157-silme-testler-design.md) ·
**Kırmızı commit:** `test(m157)`

33 test kırmızı. Bu belge onları yeşile çeviren kodu anlatır.

## `_naming` sayı yerine numara döndürür

Bugün kaç kare olduğunu sayıyor; artık **hangi kareler** olduğunu söylüyor. Ret cümlesi numaraları
istiyor, ve iki ayrı yürüyüş yazmak, aynı sorunun iki cevabının ayrışabilmesi demek.

- `_set_entry` çağrısı `len(...)` ile devam eder — çıktısı değişmiyor.
- Numara **listedeki sıradan** gelir, karenin damgasından değil. Madde 153 ikisini eşit tutuyor; elle
  bozulmuş bir damga kullanıcıya olmayan bir kareyi gösterirdi, ve gerçek olan sıra.
- Adı da değişiyor: `_naming` → `_frames_naming`. Sayı değil liste döndüren bir fonksiyonun adı
  çoğul olmalı.

## `_remove_entry(file_store, project_id, args, which)`

Üç aracın ortak gövdesi, `_set_entry`'nin tam karşılığı. Sırayla:

1. `_opened` — dosya, parse, `frames` listesi. `_set_entry` kendi önsözünü taşıyor çünkü kare
   görmeden çalışabiliyor; silme **kullanımı sayabilmek için** kareleri okumak zorunda, yani liste
   burada gerçek bir şart ve `_opened` doğru kapı.
2. Ad boşsa ret.
3. Ad haritada yoksa ret, ve cümle `build_prompts`'ınkiyle aynı:
   `ghost is not in outfits; known: gecelik, palto.`
4. `_frames_naming` boş değilse ret, ve cümle numaraları sayar.
5. Sil, yaz, söyle.

**Fiil kaynağa göre değişir**, ve tek bir tabloda durur:

```python
_STILL = {
    "characters": "is still in frames",
    "outfits": "is still worn in frames",
    "locations": "is still the place in frames",
}
```

Üç ayrı cümle değil, tek cümlenin içindeki tek değişken parça. Bir karakter *karede*, bir kıyafet
*giyilir*, bir mekân *oranın kendisidir* — aynı fiili üçüne birden yazmak modele üç ayrı ilişkiyi tek
bir şeymiş gibi okuturdu.

## `_remove_frame(file_store, project_id, args)`

1. `_opened`.
2. `_a_number(args.get("frame"))` — tam sayı ya da rakamlardan oluşan string; başka her şey `None`.
   `bool` **tam sayı sayılmaz**: Python'da `True` bir `int`'tir ve 1. kareyi silerdi.
3. `None` ise ret: *"frame is the number of the frame to remove."*
4. Aralık dışıysa ret, ve cümle kaç kare olduğunu söyler. Sıfır kare ayrı cümle — *"has 0 frames"*
   doğru ama okunmuyor.
5. Sil, `_renumber`, yaz.
6. Cevap kalan sayıyı söyler: `Removed frame 2 from scene.json; 2 frames left, renumbered from 1.`
   Sıfır kalırsa *"no frames left"*.

**Negatif ve sıfır 4. adımda düşer** — `1 <= number <= len(frames)` tek karşılaştırma, ve
`frames[-1]`'in sessizce sondakini silmesi böylece hiç doğmuyor.

## Araç tanımları

Dördü `TOOL_SPECS`'e girer, `set_`'lerin hemen ardına — model listeyi okurken ekleme ve silme yan
yana duruyor. Açıklamalar kısa: **ne sildiği, ve neyin reddedildiği.** Kullanılan bir adın
reddedildiğini açıklamada söylemek, modelin o reti bir hata sanmasını engelliyor.

`remove_frame`'in `frame` parametresi `"type": "integer"`, ve açıklaması numaraların silmeden sonra
kaydığını söyler.

## `modes.py`

Dördü `EDIT`'in listesine girer. `ask` ve `plan` onları sorar — geri dönüşü olmayan tek eylem bu, ve
kapı önlerinde duracaksa bunların önünde duracak.

`WRITES_FILES`'a **girmezler**: silme dosya doğurmaz.

## Bu turda dokunulmayanlar

- **`skills.py`.** İki metin de silmeyi anlatmıyor, ve anlatmasına gerek yok: araçların adları ne
  yaptıklarını söylüyor, ve akış silmekle başlamıyor. Metinlere cümle ancak bir cümle silinerek
  giriyor *(Madde 123)*.
- **`schema.py`.** Kitapçığın 5. kuralı — kullanılmayan bir ad *"bir not, ihlal değil"* — yerinde
  kalıyor. O kural silmeye izin veriyor, engellemiyor.
- **Zorla silme.** `force` yok. Kullanılan bir adı silmek isteyen önce kareleri düzeltir, ve o iş
  158'in.

## Nasıl yeşil olacak

33 kırmızının hepsi araçların var olmasıyla kapanır. Notebook'un iki kırmızısı yerinde kalır.
