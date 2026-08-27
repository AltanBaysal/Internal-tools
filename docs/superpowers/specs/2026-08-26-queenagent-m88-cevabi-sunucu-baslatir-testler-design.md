# Madde 88 — Cevabı sunucu başlatır, tarayıcı değil · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 5, Madde 88 ·
**Üstüne geldiği:** [Madde 87](2026-08-26-queenagent-m87-mesaj-tek-kapidan-uygulama-design.md) —
kapıyı birleştirdi; bu madde o kapıdan **geri ne geldiğini** değiştiriyor.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

Mesaj diske yazılıyor, bağlantı kapanıyor. Cevap ancak tarayıcı **ikinci** bir istek attığı için
doğuyor, ve o isteği atan şey bir kural: *"son mesaj kullanıcınınsa bu sohbet bir cevap borçlu."*

Kural yalnız gönderimden sonra değil, **sayfa yenilenince ve bağlantı geri gelince de** çalışıyor.
Yani kullanıcının istemediği bir anda cevap kendiliğinden baştan başlıyor — kapatılmış bir sekmeye
geri dönmek bir tur başlatıyor.

## Ne oluyor

Cevap, mesajı yazan isteğin **içinde** üretilir ve aynı bağlantıdan akar. Tek istek, tek bağlantı.

Kapının anlamı da netleşiyor: **`POST .../messages` "bu sohbeti ilerlet" demek.** Gövdesinde metin
varsa önce o yazılır, sonra cevap akar. Metin yoksa hiçbir şey yazılmaz ve bekleyen soru
cevaplanır.

| Gövde | Ne olur |
|---|---|
| `{text}` | Sohbet doğar, mesaj yazılır, cevap akar |
| `{chat, text}` | Mesaj eklenir, cevap akar |
| `{chat}` | Hiçbir şey yazılmaz, bekleyen soru cevaplanır — **tekrar deneme** |
| `{}` | 400: ilerletilecek bir şey yok |

**Metnin yokluğu ile boşluğu ayrı şeyler.** `{"text": "   "}` boşluk tuşuna basmış bir kullanıcı ve
reddediliyor; `text` alanının hiç olmaması "mesaj göndermiyorum" demek. Bu ayrım kasıtlı ve
yazılıdır, çünkü sessizce karıştırılırsa boş bir kutuya basmak cevap üretmeye başlar.

## Tekrar deneme kalıyor

*(kullanıcı kararı, 26 Ağustos: "hata olursa tekrar dene olmalı")*

Ekrandaki **"Try again"** düğmesi duruyor ve artık aynı kapıya, metinsiz gidiyor. Kalkan şey düğme
değil, **kendiliğinden basılması**.

Bunun bir bedeli var ve ödeniyor: kural *"bu sohbet bir cevap borçlu mu"* diye sormak zorunda, yoksa
cevabı bitmiş bir sohbete ikinci bir cevap yazılabilir. O soru bugün tarayıcıda duruyor
(`isOwedAnAnswer`) ve yanlış yerde durduğu için yanlış anlarda çalışıyor. **Sunucuya iner:**
`is_owed_an_answer(chat)`, `chat.py`'de, saf bir fonksiyon. Uç ona bakıp 400 döner.

Yani 88 kuralı silmiyor, **doğru yere taşıyor** — ve orada kendiliğinden çalışamıyor, çünkü onu
çağıran bir efekt yok.

## Akışın ilk karesi

İlk kare `chat` olayıdır ve sohbetin id'sini taşır. **Her istekte gönderilir**, sohbet yeni olsun ya
da olmasın: sunucuda koşul olmaz, tarayıcı yalnız elindekinden farklıysa adresi değiştirir.

Sunucu id'yi mesajı yazmadan önce zaten üretiyor, yani ilk model tokenından önce söyleyebilecek
durumda. Adres akış sürerken değişiyor — cevap doğru sohbetin içinde akıyor, ve yarıda durdurulsa
bile sohbet görünür kalıyor.

**Durum kodu artık ayrım yapmıyor.** 87 yaratmaya 201, eklemeye 200 diyordu; cevap bir akışa
dönünce bu ayrım hem gereksiz hem yanıltıcı oluyor — 201 gövdesinde bir kayıt vaat eder, oysa gövde
bir olay dizisi. Hepsi 200, ve hangi sohbet olduğunu ilk kare söylüyor.

## Adres değişince akış silinmemeli

Bir tuzak var ve tasarımın çözmesi gerekiyor.

`useChat`'in yükleme efekti `[projectId, chatId]`'e bağlı ve ilk işi `setChat(null)`. Taslakta
gönderim yapılınca ilk kare bir id getiriyor, tarayıcı adresi değiştiriyor, `chatId` `null`'dan
`c1`'e dönüyor — ve efekt akan cevabı **siliyor**, sonra diskten yarım bir kayıt okuyor.

Çözüm: kanca hangi sohbete aktığını bir ref'te tutar, ve yükleme efekti o id için erken döner.
Zaten elinde olan bir şeyi okumaya gitmiyor.

## Yanında düşenler

| Ne | Nerede |
|---|---|
| `isOwedAnAnswer` ve onu koşturan efekt | `useChat.js` |
| `stopped` durumu | `useChat.js` — tek okuyanı o efektti |
| `online` parametresi | `useChat.js` ve `App.jsx` — yalnız o efekt için vardı |
| `post_answer` ucu | `routes.py` |
| `ask`'in ayrı bir fonksiyon olması | `send` ile birleşir; `retry` metinsiz `send` olur |
| `App.startChat`'in ayrı gönderme yolu | Taslak da `chat.send`'e gider |

Madde 81'in yazdığı boş `stopped` kaydı **kalıyor**, ama sebebi teke iniyor: ekranda "durduruldu"
yazabilmek. Kendiliğinden yeniden başlamayı önleme işi, önleyecek bir şey kalmadığı için düşüyor.

## Kırmızıya dönecek testler

**Arka uç — dokuz:**

1. Mesaj gönderen istek **akışla** cevaplıyor: `text/event-stream`, ve gövdesinde modelin metni ile
   kapanış `done` karesi var.
2. İlk kare `chat` ve yeni sohbetin id'sini taşıyor.
3. Var olan bir sohbete gönderilen mesajda da ilk kare `chat` ve aynı id'yi taşıyor.
4. `POST .../answer` **yok** → 405.
5. Metinsiz ama sohbetli bir istek yeni mesaj yazmadan cevaplıyor: mesaj sayısı bir artıyor
   *(cevabın kendisi)*, kullanıcının cümlesi ikilenmiyor.
6. Ne metin ne sohbet → **400**.
7. Metinsiz, ve cevabı zaten yazılmış bir sohbet → **400**, hiçbir şey yazılmıyor.
8. Boşluktan ibaret metin → **400**, akış hiç başlamıyor.
9. `is_owed_an_answer`: son mesaj kullanıcınınsa doğru, cevapsa yanlış, sohbet boşsa yanlış.

**Ön yüz — beş:**

10. Bir cümle göndermek **tek** istek atıyor; `/answer` diye bir çağrı hiç yok.
11. Cevap borçlu bir sohbet açmak kendiliğinden tur **başlatmıyor**.
12. Bağlantı geri gelmek kendiliğinden tur **başlatmıyor**.
13. "Try again" aynı kapıya, sohbetiyle ve **metinsiz** gidiyor.
14. Taslaktaki ilk cümle akıyor ve ilk kare id'yi getirince uygulama yeni adrese geçiyor — akan
    metin **silinmeden**.

Toplam **on dört kırmızı**.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `stream_answer`'ın tur döngüsü | Cevabın nasıl üretildiği değişmiyor, yalnız nereden çağrıldığı |
| `_sse`'nin olay sözlüğü | `chunk`, `call`, `file`, `done`, `error` aynı; başına bir giriş ekleniyor |
| `/stop` ucu | 90'ın işi |
| Madde 66, 78, 84, 85'in görünürlük işi | Akış aynı akış |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` bu turda derlenmiyor.
