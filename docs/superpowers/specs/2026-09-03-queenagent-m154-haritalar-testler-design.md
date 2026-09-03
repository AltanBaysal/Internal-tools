# Madde 154 — Test turu tasarımı: dosyayı doğuran ve haritaları dolduran araçlar

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** test *(kırmızı commit'lenir)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 154

---

## Ne çivileniyor

Dört yeni araç. 151 kapıyı kapattı, 152 kare yazmayı yerine koydu; bu madde **dosyanın doğması** ve
**haritaların dolması** için aynı şeyi yapıyor. Bu maddeden sonra yapı dosyasının her parçasının
kendi aracı var.

| Araç | İmza |
|---|---|
| `create_structure` | `(file)` |
| `set_character` | `(file, name, kind, tags)` |
| `set_outfit` | `(file, name, tags)` |
| `set_location` | `(file, name, tags)` |

Araç sayısı 8'den **12**'ye çıkıyor.

---

## `create_structure`

Boş iskeleti yazıyor: boş `characters`, `outfits`, `locations` ve boş `frames`. Başka hiçbir şey.

**Adı `.json` olmaya zorlanıyor.** `safe_name` uzantısı olmayan bir ada `.md` ekliyor — model
`bar-scene` yazarsa ortaya yapı dosyası olmayan bir dosya çıkardı. `plan_name`'in `write_plan` için
yaptığının aynısı: ad, aracın kendi kuralına uyduruluyor.

**Adı doluysa reddediyor**, `create_file`'ın yaptığı gibi. Üstüne yazmak, kullanıcının senaryosunu
sessizce silmek olurdu.

**Kart çiziyor** — dosya doğuran araçlar `WRITES_FILES` kümesinde, ve bu küme kartı belirliyor.
Girmezse dosya sessizce doğar.

## Üç `set_` aracı

**Adı varsa günceller, yoksa ekler.** Ekleme ve düzeltme aynı iş: o adın metnini yazmak.

**Üçü ayrı araç**, tek araç ve bir `map` parametresi değil. Birleştirme tavsiyesi aynı kaynak
üstündeki eylemler için; bunlar üç ayrı kaynak, ve her birinin **kendi kuralı** var — kıyafet
karakterin girdisine yazılmaz, bir kıyafet girdisi tek kişiyi giydirir, kıyafet giyene göre değil
giysiye göre adlandırılır. Bugün 14 maddelik listede duran bu kurallar, araçların açıklamalarına
dağılıyor: model onları **tam kullanacağı anda** okuyor.

**Cevap hangisinin olduğunu söylüyor** — `Added` ya da `Changed`. `set` ikisini de yapıyor, ve
hangisinin olduğunu söylemeyen bir cevap modele bir adı iki kez yazdığını göstermez.

**Değişiklikte kaç karenin etkilendiğini söylüyor.** Bir haritayı düzeltmek onu anan bütün kareleri
birden değiştiriyor — yapının var olma sebebi bu, ve model o sayıyı görmeden ne yaptığını bilmiyor.

## `kind` ve karakter girdisinin şekli

Karakter girdisi düz metin olmaktan çıkıyor:

```json
"aylin": { "kind": "girl", "tags": "long teal hair, green eyes" }
```

**Ayrı bir `kinds` haritası değil, girdinin içinde.** Paralel bir harita, `characters`'da olup
`kinds`'da olmayan bir karakteri mümkün kılardı — aynı şeyi söyleyen ikinci yer, anlaşmazlığa
düşebilen yer.

**`kind` bugünden imzada** *(koşunun bağlayıcı kuralı)*. Sayımı yapan şey bu, ve sayım 156'da
geliyor — ama sonradan eklenseydi imza değişir, modele yeniden öğretilir ve yeniden denenirdi.

**İki değer: `girl` ve `boy`.** Başkası reddediliyor. Serbest metin olsaydı 156'nın sayımı sessizce
bozulurdu; kapalı bir küme, hatayı yazıldığı anda gösteriyor. Başka bir tür gerekirse kendi
maddesini alır.

## İki okuyucu, iki şekil

`build_prompts` ve `build_character_prompts` girdiyi bugün **düz metin** sanıyor. Yeni şekil bu
maddede doğduğu için, ikisi de **iki şekli birden** okumak zorunda — yoksa aradaki her promptta
karakterin kimliği kaybolurdu.

Eski dosyalar da böylece bozulmuyor: `shots`/`frames` yedeğindeki aynı disiplin.

## Ortak reddler

Üç `set_` aracı ve `create_structure` dışındaki her şey aynı kapıdan geçiyor:

- **Dosya yok** → bugünkü yokluk cümlesi. `set_` araçları olmayan bir dosyayı **doğurmuyor**:
  `bar-scene.json` yerine `barscene.json` yazılsaydı sessizce ikinci bir dosya doğar ve kimse fark
  etmezdi. 152'nin *"hata yazarken çıksın"* kuralı.
- **JSON okunmuyor** → parser'ın kendi cümlesi.
- **Boş ad** → ret.

---

## Testlerin şekli

### `create_structure`

- Dosya doğuyor, ve içinde dört boş şey var.
- Uzantısı olmayan ad `.json` oluyor.
- Ad doluysa ret, ve var olan dosya değişmiyor.
- Kart çiziyor *(`created` dolu)*.

### `set_character`

- Yeni ad ekleniyor, `kind` ve `tags` ile.
- Var olan ad **güncelleniyor**, ikinci bir girdi doğmuyor.
- Cevap `Added` ile `Changed` arasında ayırıyor.
- Değişiklikte **kaç karenin** o adı andığı söyleniyor.
- `kind` `girl` ya da `boy` değilse ret, ve harita değişmiyor.
- Olmayan dosya → ret, dosya doğmuyor.

### `set_outfit` ve `set_location`

- Ekliyor ve güncelliyor.
- `kind` almıyorlar — araç tanımında öyle bir parametre yok.

### Kuralların araç açıklamalarında olması

- `set_character`'ın açıklaması kıyafetin oraya yazılmadığını söylüyor.
- `set_outfit`'in açıklaması bir girdinin tek kişiyi giydirdiğini ve giysiye göre adlandırıldığını
  söylüyor.

### İki okuyucu

- `build_prompts` yeni şekilli bir karakteri okuyor.
- `build_prompts` eski düz metinli bir karakteri okumaya devam ediyor.
- `build_character_prompts` için aynı ikisi.

### `modes.py`

- Dördü de `edit` modunda izinsiz koşuyor; `ask` ve `plan` modunda soruyor.

---

## Kırmızının şekli

Dört araç da yok, yani onlara dokunan her test düşüyor. İki okuyucunun yeni şekli okuduğunu söyleyen
testler de düşüyor. Eski şekli okuduğunu söyleyenler bugün de yeşil — onlar bu maddenin bir şeyi
bozmadığını tutuyorlar.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```
