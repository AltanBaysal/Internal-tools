# Madde 303 — Referans işi kart doğuruyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok.

## Madde ne diyor

> Kuyruğa giren referans işi yeni kartlar yaratıyor — N prompt × M varyant kadar, **fotoğraf katmanı
> olmadan**. *292 ve 293'ün üstünde duruyor; üretici bu maddede sahte, o yüzden kartlar henüz boş.*
>
> **Bitti sayılır:** Üç prompt ve iki varyantla altı kart doğuyor, hiçbirinde fotoğraf katmanı yok,
> ve galeri onları gösteriyor.

## Bu madde 292 ve 293'ün faturasını kesiyor

Kart bir kutu *(292)* ve video fotoğrafa bağlı değil *(293)*. Bu maddeye kadar o iki kural
kullanılmadı: bugüne kadar her kart bir fotoğrafla doğdu. Burada **videoyla doğan kartlar**
geliyor, ve galeri onları zaten çizebiliyor — 292'de öyle yazıldı.

## Plan nasıl yazılıyor

Fotoğraf toplu üretiminin kendi biçimi *(`plan_frames`)*, iki farkla: işin tipi **video**, ve satırda
**kip referans**. Prompt-major sıra aynen: `P0_0 P0_1 … P1_0` — numara prompt'u, varyant o prompt'un
kaçıncı denemesi olduğunu söylüyor.

Numara `next_number` ile alınıyor: aynı numara iki kez kullanılamaz, ve bu kural fotoğrafın değil
**projenin** kuralı *(silinmiş kartların adları da sayılıyor)*.

**Prompt satıra yazılıyor.** Video işleri bugüne kadar prompt'suz planlanıp sırası gelince bir dil
modeline yazdırılıyordu *(`writers`)*; referansta prompt'u **kullanıcı yazıyor**, ve satırda
duruyor — yazıcı dolu bir prompt'un üstüne yazmıyor, bugünkü kural bu.

**Tohum** planlanırken çekiliyor, fotoğraf işlerindeki gibi: plan devam eden bir koşunun geri
okuduğu şey.

## Üretici bu maddede sahte

`queue_references` kuyruğu başlatıyor, ve H3'ün referans kipi **304**'te geliyor. Bugün iş kuyruğa
giriyor, kart doğuyor, ve üretici onu bugünkü haliyle yapmaya çalışıyor — testler sahte üreticiyle
koşuyor, gerçek grafiğin ne yapacağı 304'ün konusu.

## Yazılacak testler

### `backend/tests/test_reference_usecases.py`

1. **`test_a_reference_run_makes_a_card_per_prompt_and_variant`** — üç prompt, iki varyant, altı iş.
2. **`test_every_card_a_reference_run_makes_is_a_video_job`** — hiçbiri fotoğraf işi değil.
3. **`test_the_cards_carry_the_words_the_user_wrote`** — prompt satırda.
4. **`test_the_cards_are_marked_as_made_from_references`** — kip satırda.
5. **`test_a_reference_run_takes_numbers_nobody_has_used`** — var olan plandan sonra devam ediyor.
6. **`test_a_reference_run_answers_with_how_many_it_took`**

### `backend/tests/test_reference_routes.py`

7. **`test_a_reference_run_puts_its_cards_in_the_gallery`** — galeri altı kartı gösteriyor ve
   hiçbirinde fotoğraf katmanı yok. Maddenin *"görülür"* cümlesi.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` kırmızı.
