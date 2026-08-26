# Madde 92 — Bağlamın tavanı olur, ve tavana çarpmak bir olaydır · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Test turu:** [testler tasarımı](2026-08-27-queenagent-m92-baglamin-tavani-testler-design.md) · kırmızı commit `c574515`
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder. Yeni test yazılmaz.

---

## Beş dosya

| Dosya | Ne olur |
|---|---|
| `domain/chat.py` | Tavan bir sabit, ve iki soru: ne kadar gönderdi, doldu mu |
| `presentation/routes.py` | Kapı dolmuş sohbeti reddeder; kayıt `context` alanını taşır |
| `ContextGauge.jsx` *(yeni)* | Oranı hesaplar, daireyi çizmeyi CSS'e bırakır |
| `Composer.jsx` | Ayağın soluna bir yuva |
| `ChatScreen.jsx` · `workspace.css` | Yuvayı doldurur; daireyi çizer |

## Alan — tavan ve iki soru

`is_owed_an_answer`'ın yanına, aynı gerekçeyle: bu sorular kaydın kendisine ait, ve bir uç onları
soruyor olmakla bir kural haline gelmiyor.

Okunan şey **sondan geriye ilk cevabın** `usage.sent`'i. Geriye yürüyor, çünkü kayıt her zaman bir
cevapla bitmiyor. Hiç cevap yoksa sıfır — ve sıfır burada "bilinmiyor"un göründüğü şey, 76'nın
verdiği kararla aynı.

Dolmak `>=` ile: tavan bir sınır, sınıra varmak da varmaktır.

## Kapı — bir bakış, iki yol

`post_message` bugün adı verilen sohbeti **yalnız metinsiz yolda** okuyor. İkisi de aynı kuralla
duracağı için okuma yukarı çıkıyor ve bir kere yapılıyor; metinsiz yol onu zaten kullanıyordu.

Sıra önemli: tavan **önce** soruluyor. Dolmuş bir sohbette tekrar denemek hem doludur hem de
cevaplanmıştır, ve kullanıcıya söylenmesi gereken hangisinin işe yaramaz olduğu değil, hangisinin
onu durdurduğu.

Ret yazmadan önce oluyor. Reddedilen cümle diske hiç inmiyor, yani sohbet cevabı beklenen bir
soruyla kalmıyor — kalsaydı tarayıcı her açılışta onu tekrar sorardı ve her seferinde aynı duvara
çarpardı.

Cümle 400 ile dönüyor, ve ne yapılacağını söylüyor: yeni bir sohbet.

## Kayıt — sayı ve paydası

`_chat_json`'a bir alan: gönderilen ve tavan. Kaydın şekli 89'dan beri tek yerde kuruluyor, burası
orası.

Tavan da gidiyor, çünkü daire bir oran çiziyor. Tarayıcıda ikinci bir 50.000 durmuyor.

Sohbet **listesinin** satırlarına girmiyor — `_chat_summary` açılmıyor, orada okuyanı yok.

## Daire — karar ve çizim ayrı

Bileşen bir şey hesaplıyor: doluluk oranı, biri bölü öteki, birde kesilmiş. Onu bir CSS
değişkenine yazıyor ve **çizmiyor**. Çizim tek bir kural: `conic-gradient` ile dolan bir daire.

Ayrılığın sebebi ölçülebilirlik değil, doğruluk: bir SVG yayının uzunluğunu sınamak dairenin ne
kadar dolu olduğunu değil, yayın nasıl çizildiğini sınar. Oran bir sayı, ve sayı sınanacak şey.

Hiçbir şey gönderilmemişse bileşen hiç çizmiyor. Boş bir daire okunacak bir şey vermiyor, yalnız
hep orada duran bir işaret veriyor.

Fare üstünde durunca oranı yazıyla söylüyor, ve aynı cümle ekran okuyucuya da gidiyor — daire
`role="img"`, çünkü çizilmiş bir şey ve adı olmalı.

Rengi `--accent`: uygulamanın kendi turuncusu. Yeni bir renk girmiyor.

## Ayak — ikinci uç

Composer bir yuva daha alıyor. İçine ne konduğunu bilmiyor, tıpkı `foot` için bilmediği gibi —
bildiği tek şey ayağın başında durduğu.

Ayrılmayı yapan `margin-right: auto`, `space-between` değil. Ayağın çocukları Skills, model adı ve
gönder düğmesi olarak **üç ayrı** öge; satırı yaymak boşluğu üçünün arasına dağıtırdı.

Yuva boşsa hiç çizilmiyor, ve ayak bugünkü hâlinde kalıyor. Taslak ekranın istediği tam bu.

## Ne değişmiyor

Cevabın altındaki sayı — 76'nın işi, yerinde; daire onu yeniden ölçmüyor. `stream_answer` — tavan
kapıda duruyor, tur hiç başlamıyor. Sohbet listesi. Composer'ın taslak hâli.

**Özetleme yok.** Bu madde yalnız tavanı ve durmayı getiriyor.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
npm run build --prefix queen-agent/frontend
```

`c574515`'in on dört kırmızısı yeşile döner, ve `ProjectScreen`'in testi yeşil kalır — daire
eklendikten sonra da taslak ekranda görünmüyor olması onun işi.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

**`dist` bu turda derleniyor ve aynı commit'e giriyor** — ön yüz değişiyor, ve defter tarafında
derlenmemiş bir değişiklik görünmüyor.
