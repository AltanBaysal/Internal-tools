# Madde 93 — Yönerge isteğin sonuna iner, sabit olan başta kalır · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Test turu:** [testler tasarımı](2026-08-27-queenagent-m93-yonerge-sona-iner-testler-design.md) · kırmızı commit `a3ea28a`
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder. Yeni test yazılmaz.

---

## Tek dosya

`domain/usecases/stream_answer.py`. `xai_engine.py` açılmıyor — sabit olan zaten başta, ve motor
sırayı bugün de bozmuyor.

## `_conversation` sadeleşiyor

Bugün iki iş yapıyor: mesajları çeviriyor, ve skill'in değiştiği yerlere yönerge serpiyor. İkincisi
düşüyor. Geriye kalan, adının söylediği şey: konuşma.

`active` takibi, karşılaştırma, "bir cevap skill taşımaz" kuralı — üçü de yönergenin **nereye**
serpileceğini hesaplamak içindi. Serpilecek bir şey kalmayınca hiçbirinin okuyanı kalmıyor.

## Güncel skill

Sondan geriye ilk kullanıcı mesajının skill'i. `last_sent`'in yürüdüğü yolun aynısı, ve aynı
sebeple: kayıt her zaman cevaplanacak soruyla bitmeyebilir.

`stream_answer`'ın yanında duruyor, `chat.py`'de değil: bu soru "bu sohbetin durumu nedir" değil,
"bu isteği nasıl kuruyorum" — ve isteği kuran burası.

## Blok her turda ekleniyor

Kritik nokta. `conversation` tur boyunca **büyüyor**: her tur kendi `assistant` ve `tool`
satırlarını sonuna ekliyor. Yönerge bir kere `conversation`'a konsaydı ikinci turdan itibaren
onların gerisinde kalırdı.

O yüzden yönerge `conversation`'ın **içine girmiyor**. İsteğe çıkarken ekleniyor, her turda
yeniden:

```
engine.stream(konuşma + [yönerge], ...)
```

Bedeli biliniyor ve kabul edildi: blok her turda yeniden işleniyor, on altı turluk bir cevapta ~8k
token.

Skill yoksa eklenecek bir şey de yok, ve liste olduğu gibi gidiyor.

## Ne değişmiyor

`Message.skill` — kayıt hangi turun hangi yönergeyle konuştuğunu söylemeye devam ediyor. `skills.py`
metinleri — 94'ün işi. Kipin araç kısıtı — `tools` ayrı bir alan ve taşınamıyor, ve iş zaten
kısıtın kendisinde. Ön yüz.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

`a3ea28a`'nın beş kırmızısı yeşile döner. Test turunda yazılıp bugün de yeşil olan bekçi —
*motor sırayı bozmuyor* — yeşil kalır.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` derlenmiyor — ön yüz değişmiyor.
