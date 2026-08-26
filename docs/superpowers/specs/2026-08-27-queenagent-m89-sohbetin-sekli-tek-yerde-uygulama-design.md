# Madde 89 — Sohbetin şekli tek yerde kurulur · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 89 ·
**Turun birincisi:** [test turu](2026-08-27-queenagent-m89-sohbetin-sekli-tek-yerde-testler-design.md) —
yedi kırmızı commit'lendi *(`e1e16d1`)*.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder.

---

## Arka uç — bir satır

`_sse`'nin son karesi kaydı taşımayı bırakır:

```python
yield _frame("done", {})
```

`_chat_json` yerinde kalıyor; değişen tek şey artık **tek** yerden çağrılması — `get_chat`.

Karenin kendisi kalıyor, boş olarak: turun bittiğini söyleyen şey o, ve tarayıcı okumaya ne zaman
gideceğini ondan öğreniyor.

## Ön yüz — sıra

`send`'in akışı bittikten sonra, **`finally` çalışmadan önce**, kayıt okunur:

1. Akış biter *(`done` ya da `error`)*.
2. Kayıt okunur ve `chat`'e konur.
3. `finally` akan metni ve kartları temizler.

Sıra tersine dönerse ekran bir an boşalıyor — akan metin silinmiş, kayıt henüz gelmemiş olurdu.

**Hangi sohbet okunur:** `streamingInto.current`. İlk karede yazılıyor, ve yeni doğan bir sohbette
de doğru olan tek kaynak o — `chatId` prop'u henüz eski değeri taşıyor olabilir.

**Nasıl biterse bitsin okunur.** Hata karesiyle biten bir turda da kullanıcının cümlesi diske
yazılmıştı ve ekranda kalması gerekiyor.

**Okuma düşerse** `error`, okumanın kendi sözleriyle. Bir istisna var: akış zaten bir `error`
karesiyle bittiyse o mesaj korunur — turun asıl arızası odur, ve onu okuma hatasıyla değiştirmek
kullanıcıya yanlış sebebi gösterirdi.

**İstek reddedilmişse okunmaz.** POST'un kendisi 400 aldıysa ne yazılan bir şey var ne akış; o yol
bugünkü `catch` dalı ve olduğu gibi kalıyor.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `_chat_json`, `_chat_summary` | Kendileri değişmiyor |
| İlk kare ve `streamingInto` bekçisi | 88'in işi, yerinde |
| `stream_answer` | Ne ürettiği değişmiyor |
| `/stop` | 90'ın işi |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
npm run build --prefix queen-agent/frontend
```

Yedi kırmızı yeşile döner. **İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` derlenir ve aynı commit'e girer.
