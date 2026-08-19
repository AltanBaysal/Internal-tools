# Madde 38 — Sessiz tur meşru · Uygulama Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 38](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Test turu:** [2026-08-19-queenagent-m38-sessiz-tur-testler-design.md](2026-08-19-queenagent-m38-sessiz-tur-testler-design.md) — kırmızı commit `bd4cef1`
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Testler yazıldı ve kırmızı duruyor. Bu belge onları yeşile çeviren **kodu** tarif ediyor.

---

## 1 · Kuralın yeri değişmiyor, kapsamı değişiyor

Bugünkü kural `append_message` içinde ve şöyle okunuyor: *bir mesajın metni olmalı.*

Doğru kural: *bir mesaj bir şey taşımalı.* Söz ya da dosya. Kullanıcının mesajı hiçbir zaman dosya
taşımadığı için — uçlar `files` göndermiyor — kullanıcı tarafında hiçbir şey gevşemiyor: boş bir
mesaj hâlâ reddediliyor ve uç hâlâ 400 diyor. Gevşeyen tek şey modelin cevabı, ve yalnız bir dosya
ürettiği hâlde.

Kuralın `append_message`'ta kalmasının sebebi: mesajın ne zaman meşru olduğu mesajın kendi kuralı.
`stream_answer`'a taşımak, aynı kuralın ikinci bir kopyasını doğururdu — `post_message` yolunda bir
tane, akış yolunda bir tane.

## 2 · İstisna akışı koparmıyor

Bugün `append_message` çağrısı `stream_answer`'ın `try` bloğunun dışında ve `_sse` yalnız
`EngineFailed` yakalıyor; `EmptyMessage` üretecin dışına çıkıp Flask yanıtını ortasından kopartıyor.
Kullanıcının gördüğü "network error" tam olarak bu kopmanın tarayıcıdaki adı.

Düzeltme `_sse`'de: `EmptyMessage` de yakalanır ve kendi çerçevesiyle çıkar.

```
except EmptyMessage:
    yield _frame("error", {"error": "The model returned nothing."})
```

Cümle olanı söylüyor. "Sebep uydurma" kuralı burada kritik: bugünkü hâl, ağla ilgisi olmayan bir
şeye ağ hatası diyor — düzeltmenin kendisi o kuralın gereği.

`stream_answer`'ın kendi `try`'ına almak **yanlış olurdu**: o blok `EngineFailed` üretiyor ve
"motor bozuldu" demek, boş cevabı motorun arızası saymak olurdu. İki ayrı olay, iki ayrı cümle.

## 3 · Yarım cevap yine saklanmıyor

`append_message` reddettiğinde diske hiçbir şey yazılmıyor — bugünkü davranış, ve testler bunu
tutuyor. Dosyalar diske yazılmış olabilir; bu bir çelişki değil, tool zaten çalışmıştır. Sohbete
yazılmayan şey **cevaptır**, dosya değil.

## 4 · Değişen dosyalar

| Dosya | Ne |
|---|---|
| `domain/usecases/append_message.py` | Koşul `not trimmed` → `not trimmed and not files`; yorum kuralı söyler |
| `presentation/routes.py` | `_sse` `EmptyMessage`'ı da yakalar ve `error` çerçevesi verir |

Başka hiçbir yer değişmiyor. `stream_answer` olduğu gibi kalıyor: `said` boşken de `append_message`
çağırıyor, ve artık `born` doluysa cevap kaydediliyor.

**Ön yüz değişmiyor.** `useChat` `error` çerçevesini zaten `setError` ile işliyor, dosya olaylarını
zaten biliyor. Akış düzgün kapandığı anda bugünkü kart doğru olanı gösteriyor.

## 5 · Kabul ölçütü

1. Test turunun dokuz testi de yeşil.
2. Başka hiçbir test düşmüyor — özellikle `post_message` ve `post_chat`'in boş mesaj 400'leri.
3. `python -m pytest queen-agent -q` ve `npm test --prefix queen-agent/frontend` yeşil.
4. Elle: "Generate prompts+" turu hata kartı göstermeden bitiyor, dosya kartları duruyor.

## 6 · Bu maddenin kapsamadığı

Boş metinli bir cevabın ekranda nasıl durduğu — `msg__text` boş bir div olarak çiziliyor, altında
dosya kartları. Kırık değil, ama tasarlanmış da değil. Görülüp rahatsız ederse kendi maddesi olur;
bu madde hata kartını düzeltiyor, yeni bir görünüm icat etmiyor.
