# Madde 179 · uygulama turu — makbuz

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m179-makbuz-testler-design.md).
Commit `3c6c90a` 11 kırmızı bıraktı. Koşunun son maddesi.

---

## Üç satır

**`tools.py`** — `read_file` artık `numbered(content)` değil, bir cümle:

```
plan.md, 3 lines; it is in your opened files.
```

Kart *(`outcome`)* değişmedi: hâlâ `3 lines`. İki yerde de aynı sayı, ve ikisi de bu anın notu —
diskte durmuyor, dolayısıyla bayatlayamıyor.

**`stream_answer._boxed`** — başlık `BOX_LIMIT`'i söylüyor: *"The last 5 files you opened…"*.
Sabitten okunuyor, elle yazılmıyor.

**`prompt.py`** — okuma cümlesine iki satır: *okumak dosyayı basmaz, açar; geri gelen bir makbuz,
dosyanın kendisi açtıkların arasında ve diskteki hâliyle.* Bu cümle olmasa model bir makbuz alıp
dosyayı görmediğini sanır ve yeniden okurdu — düzeltilen şeyin aynısı.

## Koşarken çıkan iki kırmızı — ikisi de aynı sebepten

`test_reading_gives_the_contents` ve `test_the_runner_takes_an_engine_…` okumanın cevabının içinden
metin arıyordu. İkisi de kırmızı turda kaçtı.

**171'in dersinin aynısı, başka kılıkta:** *bir aracın cevabını değiştiren madde, o cevabı okuyan
testleri de aramak zorunda.* 171'de kapatılan yolun kullanıcıları, burada değişen cümlenin
okuyucuları. Aranacak yer aynı — `grep` ile aracın adı, ve cevabından bir parça.

İkisi de uygulama turunda döndürüldü: biri makbuzun kendisini ölçüyor, öteki karta *(`2 lines`)*
bakıyor — çünkü sorduğu şey zaten motorun öteki araçları bozmadığıydı, okumanın ne döndürdüğü değil.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **810 yeşil.** 11 kırmızının hepsi döndü, artı yukarıdaki iki tanesi.
3. Öteki üç takım rakamlarını korudu: **589 · 739 · 591.** `dist` derlenmedi.

---

## Koşu kapandı

**166–179, on dört madde, yirmi sekiz tur.** Dilim 1 modelin JSON yazmayı bırakmasıydı, Dilim 2
karenin kendi hayatı, Dilim 3 ürün yüzeyi.

**Deneme 3'ün sorusu:** iki skill baştan sona — bir senaryo kur, promptlarını üret, derle — ve
besteci. Bu kez **skill seçilerek** koşuluyor; 178 metinleri buna hazırladı.

Merge'den önce: `queenagent.ipynb`'nin `BRANCH`'i denemeler için `feat/queenagent-v7`, birleşmeden
önce `main`.
