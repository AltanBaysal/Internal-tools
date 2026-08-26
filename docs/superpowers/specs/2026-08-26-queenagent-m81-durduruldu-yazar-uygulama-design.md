# Madde 81 — Durdurulan tur durdurulduğunu söyler · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [test turu spec'i](2026-08-26-queenagent-m81-durduruldu-yazar-testler-design.md) ·
**Testler:** `1bc84f5` — arka uçta 2, ön yüzde 4 kırmızı.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz.

---

## Kural bir cümleyle esniyor

`append_message` bugün şunu söylüyor: bir mesaj ya bir söz ya bir dosya taşımalı. Üçüncü bir şey
ekleniyor — **bir durdurma**:

```python
if not trimmed and not files and not stopped:
    raise EmptyMessage()
```

Neden bu üçlüye giriyor: söz de dosya da olmuş şeyler, ve kural aslında *"olmuş bir şeyin kaydı
olur"* diyor. Durdurma da olmuş bir şey. Kayıtsız kalması onu olmamış gibi gösteriyordu.

**Kullanıcının boş mesajı hâlâ reddediliyor** ve bunun için ayrı bir şart yazılmıyor: kapıyı açan
bayrak `stopped`, ve kullanıcının mesajı onu hiçbir zaman taşımıyor. Role bakan bir şart daha kesin
görünürdü ama daha az doğru olurdu — kaydı hak ettiren şey kimin konuştuğu değil, ne olduğu.

Yerindeki açıklama düzeltiliyor: bugünkü hâli iki şey sayıyor, ve artık üç.

## Erken dönüş kalkıyor

`stream_answer`'ın sonundaki şu blok siliniyor:

```python
if cut_short and not "".join(said).strip() and not born:
    yield chat_store.get(project_id, chat_id)
    return
```

Altındaki `append_message` çağrısı her yolu karşılıyor: metin varsa metinle, yoksa boş ve `stopped`
ile. Blok kalsaydı `append_message`'ın yeni kapısına hiçbir zaman ulaşılmazdı.

**Kayıt yine gönderiliyor** — o zaten `append_message`'ın dönüşü, yani okuyan hâlâ *"bitti"* ile
*"düştü"*yü ayırt edebiliyor. Silinen şey ikinci bir yol, tarayıcıya giden şey değil.

## Ekranda

`ChatScreen` iki şey öğreniyor:

- **Metin bloğu yalnız metin varken çiziliyor.** Boş bir `.msg__text`, gri sol çizgiyi hiçbir şeyin
  yanına koyardı. Bugün boş metinli bir cevap yalnız durdurulanlarda olabiliyor, yani şart oraya
  bir şey kaybettirmiyor.
- **`stopped` ise metnin altına `Stopped` düşüyor.** Dosya kartlarının ve token sayısının üstünde:
  ikisi de turun kendisi hakkında notlar, bu ise metnin nerede bittiğini söylüyor.

Yazı `<div className="msg__stopped">Stopped</div>` — kendi elemanı, çünkü kendi kaydında.

## Neden `Stopped`, ve neden yalnız o

- **İngilizce**, çünkü QueenAgent'ın arayüzü bilerek İngilizce *(CLAUDE.md)*.
- **Tek kelime.** Kim durdurduysa o bir tanedir, ve `Stopped` bunu zaten söylüyor. *"Interrupted by
  the network"* gibi bir cümle uydurulmuş bir sebep olurdu — CLAUDE.md'nin yasağı.
- **İşaretsiz.** `⎿` 78'den beri *"üstündeki çağrının sonucu"* demek; durdurma bir çağrının sonucu
  değil. Ayıran şey yazı tipi.

`.msg__stopped` `.token-count` ile aynı kayıtta: mono, `--muted`. Üstündeki adımlar, altındaki sayı
ve bu satır — üçü de metnin kendisi değil, metin hakkında notlar.

Gri çizgi duruyor. Kelime onu okunur yapıyor, yerini almıyor.

## Beraberinde kapanan delik

Bugün kelimeden önce durdurulup sayfa yenilenirse cevap kendi kendine baştan başlıyor: kayıt
yazılmadığı için sohbetin son mesajı kullanıcınınki kalıyor, yani sohbet cevap borçlu görünüyor, ve
bunu tutan tarayıcı bayrağı yenilemede sıfırlanıyor.

Boş kayıt yazılınca son mesaj cevabınki oluyor ve delik **kendiliğinden** kapanıyor. `useChat`'e
tek satır eklenmiyor; `stopped` bayrağı da duruyor, çünkü basma anıyla kaydın gelişi arasındaki
pencereyi hâlâ o tutuyor.

## Dokunulmayan

- **Durdurmanın kendisi.** 67 ve 79 nasıl bıraktıysa öyle.
- **`file_chat_store`.** `stopped`'ı zaten yalnız `True` iken yazıyor, `.get(..., False)` ile
  okuyor. Boş metin de olduğu gibi yazılıyor. Göç yok.
- **`routes.py`.** Mesaj JSON'u `stopped`'ı zaten taşıyor.
- **Kullanıcının boş mesajını reddeden test.** O kapı kapalı ve kapalı kaldığını o test söylüyor.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur.** Ön yüzde **512**, hepsi yeşil. Arka uçta **2 failed, 443 passed** — ikisi
defterin dalı, ve deneme bitip defter `main`'e çevrilince ikisi de yeşile döner.

**Bu maddenin asıl sınavı düşmeyen testler:** 67'nin gri çizgiyi soran testi, yarım metnin
saklandığını soran testi, kalan turların koşmadığını soran testi, ve kullanıcının boş mesajını
reddeden test. Dördü de dokunulmadan yeşil kalmalı — biri düşerse esneyen kural esnemesi gereken
yerden fazlasını esnetmiş demektir.

`dist` **kaynağıyla aynı commit'te** derleniyor.
