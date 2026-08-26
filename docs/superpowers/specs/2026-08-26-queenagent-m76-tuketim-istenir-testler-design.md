# Madde 76 — Token gerçekten görünür · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 76 ·
**Tur:** ikiden birincisi — bu belge yalnız **testleri** tarif eder.

---

## Ne kanıtlanacak

Madde 68 tüketimi okuyup saklayan yolun tamamını kurdu ve testleri yeşil. Ekranda yine de hiçbir
sayı çıkmadı. İki iddia:

1. Sayı **isteniyor** — bugün istenmiyor, o yüzden gelmiyor.
2. Sayıyı taşıyan kare **cevabı düşürmüyor** — bugünkü okuyucu o kareyi görse patlardı.

İkincisi maddenin sessiz yarısı, ve daha tehlikeli olanı: eksik bir sayı bir eksikliktir, düşen bir
cevap bir arıza.

## Neyin yanlış olduğu

68'in belgeleri şunu söylüyor: *"Akan cevapta tüketim her parçada geliyor. Ayrıca istenmesi
gerekmiyor."* Bu cümle xAI'nin akış **kılavuzundan** alınmıştı. **API referansı tersini söylüyor**,
ve asıl kaynak o:

> `stream_options.include_usage` — "Set an additional chunk to be streamed before the `data: [DONE]`
> message. **The other chunks will return `null` in `usage` field.**"

Üç sonuç, üçü de tasarımı belirliyor:

- **İstenmeden gelmiyor.** İstekte `stream_options: {"include_usage": true}` yoksa her karenin
  `usage` alanı `null`. Kodumuz doğru yere bakıyor; bakacak bir şey yok.
- **Bir kez geliyor, en sonda.** Kümülatif bir dizi değil, tek bir kapanış karesi.
- **O kare boş.** İçinde konuşacak bir şey yok — `choices` listesi boş geliyor. Bugünkü
  `_spoken` `choices[0]` diyor: o kareyi gördüğü an `IndexError`, ve `stream_answer` bunu
  `EngineFailed`'a çevirip cevabın tamamını çöpe atar.

## Karara bağlananlar

**Yalnız akan istekte isteniyor.** `complete` bir akış değil; ona `stream_options` göndermek
anlamsız, ve desteklemeyen bir uç noktada 400 sebebi. Alan `stream` bayrağıyla aynı yerde,
aynı koşulda doğuyor.

**Her zaman açık.** Ayarlanabilir yapılmıyor: kapatmak isteyen yok, ve FOUNDATION'ın 3. ilkesi
kanıtlanmamış ihtiyaç için soyutlama yasaklıyor.

**Boş kare sessizce geçiliyor.** Konuşulacak bir şey yoksa `_spoken` `None` döner — bugün de
`delta` boşken böyle davranıyor. Değişen tek şey, `choices`'ın **hiç olmaması** da bir boşluk
sayılıyor.

**Durdurulan cevabın tüketimi artık sıfır, ve bu yazılıyor.** 68 "durdurulan cevap da harcadığını
söyler" diyordu; o söz sayının her parçada geldiği varsayımına dayanıyordu ve varsayım düştü. Sayı
en sonda geldiği için kesilen cevap ona ulaşmıyor. **Kod değişmiyor** — kesilmeden önce ölçülmüş
bir şey varsa hâlâ saklanıyor, sadece pratikte olmuyor. Değişen söz, ve bir test o sözü tutuyor.

## Yazılacak testler

### `test_xai_client.py` — üç test

**Akan istek sayıyı istiyor:** gövdede `stream_options` var ve `include_usage` doğru.

**Akmayan istek istemiyor:** `complete`'in gövdesinde `stream_options` yok. Bugün de yok, yani bu
bir bekçi — ikinci tur alanı yanlış yere koyarsa kırmızıya döner.

**Kapanış karesi cevabı düşürmüyor:** `choices` listesi boş gelen bir kare okunuyor, üç sayı
çıkıyor, ve hiçbir metin parçası doğmuyor.

### `test_stream_answer.py` — bir test ve bir düzeltme

**Sayı gelmeden durdurulan cevap sıfır taşıyor.** Bu maddenin getirdiği tek davranış testi, ve
kaydı: gerçek bir akışta durdurulan cevabın tüketimi bilinmiyor.

**Var olan `test_a_stopped_answer_still_says_what_it_spent` kalıyor**, gerekçesi düzeltilerek. Neyi
tuttuğu değişmedi — kesilmeden önce ölçülen saklanıyor — ama bunun **neden** mümkün olduğu
değişti: artık "sayı her parçada geliyor" diye değil, "kapanış karesiyle durdurma arasına düşen dar
bir an var" diye. Testi silmek, doğru olan bir davranışı korumasız bırakırdı.

## Kapsam dışı

Ön yüz *(zaten çiziyor ve testleri yeşil — eksik olan sayının kendisiydi)* · sohbet toplamı ·
kırılımın ekrana çıkması · 68'in spec'lerinin geriye dönük düzeltilmesi *(onlar o günün kaydı;
düzeltme yol haritasında ve bu belgede duruyor)* · `stream_options` desteklemeyen bir uç nokta
ihtimali *(bugünkü referans destekliyor; reddederse hata servisin kendi sözleriyle geliyor ve
tahmin edilmiş bir sebep basılmıyor)*.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Defterin dalı yüzünden bugün zaten iki kırmızı var *(`test_the_notebook_clones_main` ve
`test_the_notebook_ships_pointing_at_no_feature_branch`)* — kullanıcının kendi isteği, denemesi
bitince geri çevrilecek. Bu maddenin kırmızıları onlara **eklenir**; sayılırken ayrılır.

Yeni ad doğmuyor: `Usage` 68'de doğdu, ve bu tur var olan fonksiyonların davranışına dokunuyor. O
yüzden toplama hatası riski yok.
