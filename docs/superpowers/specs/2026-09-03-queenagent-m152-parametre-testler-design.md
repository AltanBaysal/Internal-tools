# Madde 152 — Test turu tasarımı: `add_frames` parametre alır

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** test *(kırmızı commit'lenir)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 152

---

## Ne çivileniyor

`add_frames` bugün `frames` diye bir **nesne listesi** alıyor — yani modelin dosyanın şeklini
kendisi kurması gerekiyor. Bundan sonra **düz parametreler** alıyor ve nesneyi kod kuruyor.

151 kapıyı kapattı; kapının anlam kazanması için yerine geçen şeyin modele JSON kurdurmaması
gerekiyor. Aksi hâlde kapı yalnız aynı işin başka bir yoldan yapılmasını istiyor olurdu.

## Yeni imza

```
add_frames(name, characters, location, action, camera)
```

- **Bir çağrı bir kare.** Liste gitti, `frames` diye bir parametre yok.
- **`people` yok, ve hiç olmayacak** *(koşunun bağlayıcı kuralı)*. Model onu bugün yazıyor; bundan
  sonra hiç yazmıyor. Kodun onu türetmesi 156'da — arada yeni karelerde alan **hiç bulunmuyor**, ve
  `build_prompts` bunu zaten kaldırıyor *(yazılı bir `people` varsa kullanır, yoksa geçer)*.
- **`characters` iç içe kalıyor** — `{"aylin": ["gecelik"]}`. Karede kimin ne giydiği doğası gereği
  bir eşleşme, ve mesele iç içelik değil modelin **dosyayı** öğrenmemesi.

## Aracın parametreleri kendi sözleşmesi

Bugün parametre dosyanın şeklini taşıyordu; bundan sonra taşımıyor. İkisi şu an birbirine benziyor
ama aynı şey değil — dosyanın şekli ileride değiştiğinde *(kare numarası, `prompt` bloğu)* modelin
çağrıları değişmeyecek. Bunu çiviyen tek şey, bu maddeden itibaren aracın **alan alan** parametre
alması.

## Reddedilenler

**Tanınmayan bir alan varsa çağrının tamamı reddediliyor, kare hiç yazılmıyor.** Bilineni yazıp
bilinmeyeni yok saymak, modele olmayan bir kare yazdığını düşündürürdü; yarım yazılmış bir kare de
kimsenin istemediği bir şey. Eski `frames` argümanı da böylece reddediliyor — ayrı bir kural
gerekmiyor, tanınmayan bir alan olarak düşüyor.

**Olmayan bir karakter ya da kıyafet adı reddediliyor, kare hiç yazılmıyor.** Bugün bu ancak
`build_prompts` koştuğunda fark ediliyor — kare yazılmış oluyor, hata sonra geliyor. Cümlesi
`build_prompts`'ın kendi cümlesiyle aynı: `aylin is not in characters; known: …`

**`action` ya da `camera` olmadan çağrı reddediliyor.** Karenin ne yaptığını ve nereden bakıldığını
söylemeyen bir kare, kare değil. Bugün bunu tutan şey *"boş liste geldi, dosya değişmedi"* cevabıydı;
liste gidince yerine bu geçiyor.

**Kıyafetsiz karakter hata değil.** Reddedilen şey **var olmayan** bir ad; **hiç ad vermemek** değil.
`characters` hiç verilmemiş olabilir — kimsenin olmadığı bir kare bugün de geçerli.

---

## Testlerin şekli

### Yeni

- Düz parametrelerle kare ekleniyor ve dosyada doğru şekliyle duruyor.
- Eklenen karede **`people` alanı yok**.
- Araç tanımında **`people` parametresi yok**, ve `frames` de yok.
- Tanınmayan alan → ret, dosya değişmemiş.
- Eski `frames=[…]` biçimi → ret, dosya değişmemiş.
- Olmayan karakter adı → ret, dosya değişmemiş, cümle bilinenleri sayıyor.
- Olmayan kıyafet adı → ret, dosya değişmemiş.
- `action` yok → ret; `camera` yok → ret.
- Kıyafetsiz karakter → geçiyor.
- `characters` hiç verilmemiş → geçiyor.

### Çevrilenler

Bugünkü on iki `add_frames` testinin hepsi `frames=[FRAME]` çağırıyor. Ölçtükleri şey duruyor,
yalnız çağrı biçimi düz parametreye dönüyor: sona ekleme, sayıların cevabı, kartın kelimesi,
haritalara dokunmama, Türkçe'nin okunur kalması, olmayan dosya, bozuk JSON, `frames` listesi olmayan
yapı, kart çizmemesi.

### Gidenler

- **`frames` bir liste değilse ret** — `frames` diye bir parametre kalmıyor; yerini tanınmayan alan
  reddi alıyor.
- **Boş liste dosyayı değiştirmiyor** — boş liste diye bir şey kalmıyor; yerini `action`/`camera`
  reddi alıyor.

### Dokunulmayanlar

`FRAME` sabiti duruyor: `add_frames`'e artık verilmiyor ama başka testler dosyaya doğrudan kare
yazmak için kullanıyor.

---

## Kırmızının şekli

Kod bugün düz parametreleri tanımıyor, `frames` bekliyor. Yani çevrilen on iki test de, yeni testler
de düşüyor. Bu maddenin kırmızısı büyük — ve büyük olması doğru, çünkü değişen şey aracın imzası.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```
