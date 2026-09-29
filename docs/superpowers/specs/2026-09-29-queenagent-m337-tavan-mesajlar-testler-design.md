# Madde 337 — Tavan ve gösterge yalnız sohbetin mesajlarını ölçer · test turu

**Kaynak:** [yol haritasının 337'si](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) — v9-1a;
kararları *v9-1 — Sohbet sınırı*, 28 Eylül metni.

**Kullanıcıdan gereken:** hiçbir şey. Ölçünün nasıl yapılacağı teknik bir karar, aşağıda.

## Bugün

Tavan, son cevabın son isteğinin tamamını okuyor: `Usage.context`, motorun o istek için söylediği
`sent`
([chat.py](../../../queen-agent/backend/features/workspace/domain/chat.py), `last_context`). O
istekte sohbetin yanında system prompt, araç tarifleri, skill talimatı, turun araç adımları, dosya
adları ve açılan dosyalar kutusu da var. Çok araç çağıran bir tur ya da büyük bir dosya açmak
göstergeyi büyütüyor, ve sohbeti kapatabiliyor.

## Olacak

**Sohbetin ölçüsü, açık satırdaki mesajların metni.** Modele sohbetten giden de tam olarak o:
`_conversation` her mesajdan yalnız `role` ve `text` gönderiyor
([stream_answer.py](../../../queen-agent/backend/features/workspace/domain/usecases/stream_answer.py)).
Mesajın araç adımları, dosyaları ve harcadığı sayılmaz; açılan dosyalar kutusu mesaj değil, hiç
sayılmaz. Tavan 50.000 kalır.

**Ölçü bir tahmin, sayım değil.** Üç yol vardı:

1. **Metnin harf sayısından tahmin** — seçilen. DeepSeek'in kendi kaba ölçüsü: İngilizce bir harf
   yaklaşık 0,3 token. Saf bir kural: diske, ağa, motora gerek yok; test edilir; sohbet açılır açılmaz
   bilinir, bir tur geriden gelmez. v9-1b'nin *sohbet 10.000'e inene kadar kırp*'ı da aynı ölçüyle
   mesaj mesaj sayabilir.
2. **Motorun söylediği sayıdan çıkarmak** — olmaz: motor isteğin tamamını söylüyor, ve içindeki
   sohbet olmayan kısım turdan tura değişiyor; ayırmanın yolu yok.
3. **Gerçek bir tokenizer** — FOUNDATION'ın 1. kararına göre tek bağımlılık Flask; DeepSeek'in
   tokenizer'ı `transformers` ister. Tavan bir kalite sınırı, kapasite değil (pencere 256k); bir
   tahmin bu soruya yeter.

**`Usage.context` kalkar.** Tek okuyanı tavandı. Kalırsa her tur yazılan ve kimsenin okumadığı bir
alan olur — CODE-STANDARD'ın *bir soruyu cevaplamayan alan silinir* kuralı. Diskte o anahtarla
yazılmış sohbetler okunmaya devam eder: anahtar yok sayılır.

**Göstergenin sözü değişmez** — 343'ün. Ekranın anahtarı `context.sent` da değişmez; arkasındaki
sayı değişir. Ön uca dokunulmaz.

## Testler ne tutar

**`test_chat.py`** — tavanın bölümü baştan yazılır:

| # | Ne |
|---|---|
| 1 | Sohbetin ölçüsü mesajlarının metni: bin harf 300 token (`chat_size`) |
| 2 | Boş sohbetin ölçüsü 0 |
| 3 | Cevabın harcadığı (120.000), araç adımları ve dosyaları ölçüyü değiştirmez, ve sohbeti doldurmaz |
| 4 | Sohbet, mesajları tavana ulaşınca dolu, bir önce değil — 166.667 harf dolu, 166.666 değil |
| 5 | Ölçü açık satırda: bırakılmış satırdaki uzun cevap sayılmaz |
| 6 | `Usage`'da `context` alanı yok |
| — | Tavan 50.000 — bugünkü test yerinde kalır |

Kalkanlar: `last_context`'i ve *son turun büyüklüğü*nü tutan dört test (Madde 92, 133) — soruları
kalmadı. `_answered` ve `_said` yardımcıları `Usage`'ı üç sayıyla kurar.

**`test_chats_api.py`** — kapıda:

| # | Ne |
|---|---|
| 7 | Mesajları tavanı geçen sohbet yeni cümleyi reddeder, ve hiçbir şey yazılmaz |
| 8 | Aynı sohbet cevapsız denemeyi (*Try again*) de reddeder |
| 9 | Çok harcayan ama kısa konuşan bir tur sohbeti doldurmaz: sonraki cümle kabul edilir |
| 10 | Kayıt ölçüyü ve tavanı birlikte verir: `hello` ve 995 harflik cevap → `{"sent": 300, "ceiling": 50000}` |

**`test_stream_answer.py`:** cevabın harcadığı dört testte üç sayıyla tutulur (`Usage(1200, 900, 42)`,
iki turda `Usage(2500, 1800, 30)`, bir turda tekrar eden sayı, durdurulan cevap). *Son turun taşıdığı* ve *aracın isteği sohbetin büyüklüğünü değiştirmez*
testleri kalkar: ölçtükleri alan yok.

**`test_file_chat_store.py`:**

| # | Ne |
|---|---|
| 11 | Harcanan diske yazılınca `context` anahtarı yazılmaz |
| 12 | `context` anahtarıyla yazılmış eski bir sohbet okunur, ve üç sayı olduğu gibi gelir |

*Son turun büyüklüğü diske gidip gelir* testi kalkar.

## Tutmaz

- **Tahminin gerçek token sayısına ne kadar yakın olduğunu:** onu ancak motor söyler, ve bir kalite
  sınırı için kaba bir ölçü yeter.
- **Ekranı:** gösterge sunucudan geleni çiziyor; ön uç değişmiyor.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-agent -q` yeni ve değişen testlerde kırmızı
verir. queen-editor'ün arka ucu 377'nin bilinen iki kırmızısıyla kalır; ön uçlar yeşil. Kırmızı
hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m337-tavan-mesajlar-testler-plan.md).
