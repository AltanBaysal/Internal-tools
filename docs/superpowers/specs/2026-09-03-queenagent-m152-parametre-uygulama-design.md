# Madde 152 — Uygulama turu tasarımı: `add_frames` parametre alır

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** uygulama *(yeşile götürür)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 152 ·
[test turu tasarımı](2026-09-03-queenagent-m152-parametre-testler-design.md)

---

## On yedi kırmızı, tek bir sebep

`_add_frames` bugün `args["frames"]` bekliyor. Bundan sonra `args`'ın kendisi bir kare.

---

## Araç tanımı

`frames` parametresi gidiyor, yerine dört tane geliyor:

| Parametre | Şekli | Zorunlu |
|---|---|---|
| `name` | string | evet |
| `action` | string | **evet** |
| `camera` | string | **evet** |
| `characters` | object *(ad → kıyafet listesi)* | hayır |
| `location` | string | hayır |

`people` yok. Açıklamasında da yok, `required`'ında da yok — modelin göreceği hiçbir yerde yok.

**Neden `action` ve `camera` zorunlu:** ne olduğunu ve nereden bakıldığını söylemeyen bir kare, kare
değil. Bunu bugün tutan şey *"boş liste geldi, dosya değişmedi"* cevabıydı; liste gidince yerine bu
geçiyor.

**Neden `characters` ve `location` zorunlu değil:** kimsenin olmadığı bir kare geçerli, ve
`build_prompts` boş mekânı zaten atlıyor.

**`required` yetmiyor, kod da bakıyor.** Şemadaki `required` bir tavsiye; model yine de eksik
gönderebilir. Kapıyı tutan şey kodun kontrolü.

## Ne kabul ediliyor: kapalı bir küme

Tanınan alanlar `name` ve dört tanesi. Başka bir şey gelirse **çağrının tamamı reddediliyor** ve
cevap hangi alanın tanınmadığını ve nelerin tanındığını söylüyor.

Kapalı küme, açık kümenin tersi: *"bilmediğimi yok sayarım"* diyen bir araç, modele olmayan bir kare
yazdığını düşündürür. Eski `frames` argümanı da böylece kendiliğinden düşüyor — ayrı bir kural
yazılmıyor.

## Adların kontrolü, yazmadan önce

Karakter ve kıyafet adları haritalarda aranıyor; biri yoksa kare **hiç yazılmıyor**.

Cümle `build_prompts`'ın kendi cümlesiyle aynı sözlükte: `lara is not in characters; known: aylin`.
Bilinenleri saymak, bir sonraki hamlenin tahmin olmasını engelliyor — `_looked_up`'ın zaten
tuttuğu kural.

**Sıra:** dosya var mı → JSON okunuyor mu → `frames` listesi var mı → alanlar tanınıyor mu →
`action`/`camera` var mı → adlar biliniyor mu → yaz. Her biri yazmadan önce, çünkü hepsi *"bu kare
yazılmamalı"* diyor.

## Cevap

Bir çağrı bir kare olduğu için *"kaç tane eklendi"* artık soru değil:

> `Added a frame to scene.json; it holds 3 now.`

İkinci sayı duruyor — modelin dosyayı geri okumadan durumu öğrendiği yer, ve iki kez çağrılmış bir
aracın görünür olduğu tek yer.

`outcome` = `1 frame` olarak kalıyor: kart hâlâ bir kare girdiğini söylüyor.

## Dokunulmayanlar

- Dosyanın şekli. Kare aynı alanlarla, aynı yerde duruyor — değişen yalnız çağrının biçimi.
- `WRITES_FILES` — bu araç dosya doğurmuyor, kart çizmiyor.
- `modes.py` — `add_frames` `edit` modunda izinsiz koşmaya devam ediyor.
- Türkçe'nin okunur yazılması *(`ensure_ascii=False`)* ve girintileme.
## `skills.py` — tek cümle, ve bu madde onu bırakamaz

`generate-prompts-plus` bugün *"kareleri `add_frames` ile, **beşerli gruplar hâlinde** ekle"* diyor.
Araç bir çağrıda bir kare aldığı andan itibaren bu cümle **yalan**, ve metin modelin okuduğu şey —
yalan bir talimat, modeli reddedilecek bir çağrıya yollar ve bir round harcar.

Yerine: *"her kare için bir çağrı"*.

Gruplamanın **sebebi** ölmüyor — uzun bir cevabın sonunda kalite düşüyor, ve bir seferde bir kare
yazmak zaten o ritmin kendisi. Değişen, ritmin nasıl anlatıldığı.

155'e bırakılmıyor: o madde metni baştan yazacak ama arada model elinde olmayan bir biçimi denemeye
davet edilmiş olurdu.

## Dokunulmayanlar *(devam)*

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```

707 yeşil olmalı.
