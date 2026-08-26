# Madde 87 — Mesaj tek kapıdan girer · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 87 ·
**Turun birincisi:** [test turu](2026-08-26-queenagent-m87-mesaj-tek-kapidan-testler-design.md) —
on üç kırmızı commit'lendi *(`4c8de91`)*.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder.

---

## Kural yaratmayı devralıyor

`append_message` iki adlandırılmış parametre kazanır, ikisi de sonda ve varsayılanlı:
`project_store=None` ve `new_id=""`. Boş bir `chat_id` yaratma dalını açar.

Yaratma dalı bugünkü `start_chat`'in yaptığını yapar: projeyi doğrula, metni kırp, boşsa reddet,
başlığı cümleden al, kaydı yaz. Ekleme dalı bugünkü yolunda kalır.

Sıra önemli: **boş metin, sohbet doğmadan reddedilir.** Aksi hâlde reddedilen bir istek arkasında
boş bir sohbet bırakırdı, ve test bunu diskte arıyor.

`start_chat.py` silinir.

## Uç

`post_chat` gider. `post_message` adres değiştirir:

```
POST /api/projects/<project_id>/messages
```

Yolda sohbet id'si yok; gövdedeki `chat` alanı taşıyor ve boş olabiliyor. Uç id'yi **mintler** —
`_new_id("c")` — ve kurala verir. Kural id üretmez: hangi id'nin verileceği kurulumun kararı, ve
kural bugün de öyle çalışıyor.

**Durum kodu yaratmaya bakar:** sohbet doğduysa 201, eklendiyse 200. Bunu anlamanın yolu isteğin
`chat` alanının boş olup olmadığı — sunucunun zaten baktığı şey.

Üç hata olduğu gibi kalır: bilinmeyen proje 404, bilinmeyen sohbet 404, boş metin 400.

## Ön yüz

`startChatInProject` adresini ve gövdesini değiştirir: `/messages`, ve `{ text, skill }` — `chat`
alanı yok, çünkü henüz sohbet yok.

`useChat.send` de aynı adrese gider ve `{ chat: chatId, text, skill }` yollar.

**İki çağıran kalıyor.** `startChat` gönderdikten sonra listeleri tazeleyip yeni adrese gidiyor,
`send` iyimser balonu koyup cevabı bekliyor — farklı işler. Tek fonksiyona 88'den sonra inerler.

## Fixture'lar kodun şeklini takip ediyor

Test turunda bilerek bırakılan üç yer şimdi taşınır:

| Nerede | Ne |
|---|---|
| `test_chats_api.py` `_started` | Yeni kapıya gider |
| `test_append_message.py` `_chat` | `start_chat` yerine `append_message`'ın yaratma dalını çağırır; modül importu düşer |
| `test_chats_api.py`'de eski kapıya doğrudan giden testler | Silme, listeleme ve sıralama testleri; adresleri yeni kapıya döner |

Bunlar davranış değişikliği değil: sınadıkları şey aynı, yalnız sohbeti kurma yolu değişti.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `/answer` ve `/stop` | Sohbet id'sini yolda taşımaya devam ediyorlar; 88 ile 90'ın işi |
| `stream_answer` | `append_message`'ı gerçek bir id ile çağırıyor; yaratma dalına girmiyor, çağrısı değişmiyor |
| Taslak ekran | Duruyor |
| `chat_title` ve 42 karakterlik kesme | Aynı kural, başka bir fonksiyonun içinde |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
npm run build --prefix queen-agent/frontend
```

On üç kırmızı yeşile döner. **İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi,
defterdeki `BRANCH` yüzünden.

`dist` derlenir ve aynı commit'e girer: ön yüz değişiyor.
