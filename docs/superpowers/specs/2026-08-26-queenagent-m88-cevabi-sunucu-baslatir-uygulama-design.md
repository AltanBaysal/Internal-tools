# Madde 88 — Cevabı sunucu başlatır · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 88 ·
**Turun birincisi:** [test turu](2026-08-26-queenagent-m88-cevabi-sunucu-baslatir-testler-design.md) —
on sekiz kırmızı commit'lendi *(`b39d92e`)*.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder.

---

## Arka uç

**Bir kural taşınıyor.** `is_owed_an_answer(chat)` `chat.py`'ye girer: son mesaj varsa ve rolü
`user` ise doğru. Saf bir fonksiyon, ve tarayıcıdaki `isOwedAnAnswer`'ın birebir karşılığı — orada
kendiliğinden çalışabildiği için yanlış anlarda çalışıyordu.

**Uç, kapının anlamını uygular.** `post_message` üç şeyi sırayla yapar:

1. `text` **verilmişse** mesajı yazar (`append_message`), sohbeti gerekiyorsa yaratır.
2. `text` **verilmemişse** hiçbir şey yazmaz; `chat` yoksa ya da sohbet bir cevap borçlu değilse
   400 döner.
3. Her iki yolun sonunda cevabı akıtır.

Doğrulama akıştan **önce** bitiyor, o yüzden 400 ile 404 hâlâ gerçek durum kodu olabiliyor. İlk bayt
çıktıktan sonraki her arıza `error` karesi olarak gidiyor — bu kural değişmiyor.

**`post_answer` gider.**

**`_sse` bir argüman kazanır:** akıttığı sohbetin id'si. İlk karesi `chat` olur ve onu taşır. Her
istekte, koşulsuz.

**Durum kodu ayrımı düşer.** 87'nin 201/200'ü yerine hep 200: gövde bir olay dizisi, ve hangi sohbet
olduğunu ilk kare söylüyor.

## Ön yüz

`useChat` bu maddede yeniden kuruluyor. Değişenler:

**`ask` ile `send` birleşir.** Tek fonksiyon: iyimser balonu koyar *(metin varsa)*, `/messages`'a
gönderir, akan kareleri işler. `retry` metinsiz `send` olur.

**Kendiliğinden çalışan efekt gider**, ve onunla birlikte `isOwedAnAnswer`, `stopped` durumu ve
`online` parametresi.

**Akış hangi sohbete aktığını bir ref'te tutar.** Yükleme efekti o id için erken döner — yoksa ilk
kare adresi değiştirdiğinde efekt akan cevabı silip diskten yarım bir kayıt okur.

**`chat` karesi ele alınır:** taşıdığı id elde olandan farklıysa yukarı bildirilir, ve `App` adresi
değiştirir. Taslakta bu, sohbetin adresine geçmek demek.

**`App.startChat` gider.** Taslak da `chat.send`'i çağırır; `useChat` `chatId` `null` iken de
gönderebiliyor, çünkü id artık gövdede ve boş olabiliyor. Yeni sohbet doğduğunda listeler tazelenir
— bugün `startChat`'in yaptığı iş, artık `chat` karesinin tetiklediği yerde.

## Fixture'lar kodun şeklini takip ediyor

`_started` *(test_chats_api.py)* hâlâ JSON gövde okuyor. Yeni kapıya göre yeniden yazılır: akışın
ilk karesinden id'yi alır. **Bu, o helper'ı kullanan her testin sohbetini bir cevapla birlikte
doğurur** — 88'den sonra mesaj yazmadan cevap almamak diye bir şey yok. Mesaj sayısına bakan testler
buna göre düzeltilir.

Aynı sebeple `_answered` *(test turunda yazılmıştı)* gereksizleşir ve `_started`'a katılır.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `stream_answer`'ın tur döngüsü | Cevabın nasıl üretildiği değişmiyor |
| `_sse`'nin olay ayrımı | `chunk`, `call`, `file`, `done`, `error` aynı; başına bir giriş ekleniyor |
| `/stop` ucu ve `MemoryStops` | 90'ın işi |
| Madde 81'in boş `stopped` kaydı | Ekranda "durduruldu" yazabilmek için duruyor |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
npm run build --prefix queen-agent/frontend
```

**İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` derlenir ve aynı commit'e girer.
