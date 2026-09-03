# Madde 151 — Test turu tasarımı: kapı kapanır

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** test *(kırmızı commit'lenir)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 151

---

## Ne çivileniyor

`create_file` ve `edit_file` bir **yapı dosyasına** dokunmayı reddediyor. Model yapı dosyasını düz
metin olarak yazamıyor.

Bugün ikisi de her dosyaya yazabiliyor: `create_file` adı boşsa yazıyor, `edit_file` metni bulup
değiştiriyor. Yapı dosyasının şekli bunlara karşı yalnız 14 maddelik bir kural listesiyle korunuyor
— yani bir ricayla.

## Tespit `.json` uzantısıyla, büyük küçük harf ayırmadan

Uygulamanın dili zaten bu: `_build` *"a structure belongs in a .json file"* diye reddediyor.

Harf büyüklüğüne bakılmıyor. `SCENE.JSON` yazan bir model kapıdan geçebilseydi, kapı kapı olmazdı —
ve bu tam olarak modelin kapalı bir kapıyı denerken bulacağı türden bir aralık.

## Ret cümlesi ne söylüyor, ne söylemiyor

**Söylüyor:** bunun bir yapı dosyası olduğunu ve metin olarak yazılmadığını.

**Söylemiyor:** hangi aracın kullanılacağını. O araçlar henüz yok *(154 ve 155)*, ve olmayan bir
aracın adını vermek modeli boşa gönderir — üstelik uydurmaya davet eder. Araçlar geldiğinde cümleye
adları eklenir.

`outcome` — sohbette kartın üstünde görünen birkaç kelime — `Refused` oluyor; `_build` ve `_edit`
zaten reddederken bunu kullanıyor.

## `edit_file`'ın istisnası: okunamayan dosya

**Dosya JSON olarak parse edilemiyorsa `edit_file` çalışıyor.**

Kullanıcı dosyayı arayüzde elle açıp bir virgül bozarsa, bütün yapısal araçlar `json.loads`'ta
düşer. O hâlde metin düzenlemek **doğru** araçtır, ve bu kapı olmasa model dosyayı tamir edemez.

Sıra önemli: `_edit` bugün önce dosyayı okuyor ve yoksa *"There is no file by that name"* diyor. O
sıra korunuyor — olmayan bir dosya için ret cümlesi değil, yokluk cümlesi daha doğru. Yani:

| Dosya | Cevap |
|---|---|
| Yok | Bugünkü yokluk cümlesi |
| Var, JSON olarak okunuyor | **Ret** |
| Var, JSON olarak okunmuyor | **Düzenleme geçiyor** |

## `create_file`'da ret, ad kontrolünden **önce**

Bugün `create_file` önce adın dolu olup olmadığına bakıyor. Yapı dosyası reddi ondan önce geliyor:
ad dolu olsa da olmasa da cevap aynı olmalı, yoksa model *"demek ki boş bir adla yazabilirim"*
sonucunu çıkarır.

---

## Testlerin şekli

### Reddedilenler

- `create_file` `.json` adına yazmıyor, ve **dosya diskte oluşmuyor**. Ret cümlesinin yanında
  bu ikinci iddia da duruyor — cevabın ret demesi yetmez, yazmamış da olması gerekiyor.
- Aynısı **adı boş olmayan** bir `.json` için: cevap yine ret, *"already there"* değil.
- `SCENE.JSON` de reddediliyor.
- `edit_file` okunabilir bir yapı dosyasını değiştirmiyor, ve **dosyanın içeriği aynı kalıyor**.

### Geçenler

- `create_file` `.md` yazmaya devam ediyor — kapı yalnız bir dosya türüne kapanıyor.
- `edit_file` `.md` değiştirmeye devam ediyor.
- `edit_file` **bozuk** bir `.json`'u değiştiriyor — tamir yolu.
- `read_file` yapı dosyasını okumaya devam ediyor *(kullanıcı kararı: okumak kapatılmıyor)*.

### Dokunulmayanlar

- `add_frames`, `build_prompts`, `build_character_prompts`, `write_plan` — hiçbiri `create_file` ya
  da `edit_file` üstünden yazmıyor, doğrudan depoya yazıyorlar. Kapı onları ilgilendirmiyor, ve bunu
  söyleyen bir test duruyor: `add_frames` yapı dosyasını yazmaya devam ediyor.
- Araç listesi. Yeni araç gelmiyor, gideni de yok.

---

## Kırmızının şekli

Kod bugün hiçbir şeyi reddetmiyor, yani reddi bekleyen her test düşüyor. Geçmeyi bekleyenler bugün
zaten geçiyor — onlar kapının **fazla geniş** kapanmadığını tutuyorlar, ve bu turda yeşil olmaları
doğru.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```
