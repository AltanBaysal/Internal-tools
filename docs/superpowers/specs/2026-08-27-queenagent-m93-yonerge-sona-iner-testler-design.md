# Madde 93 — Yönerge isteğin sonuna iner, sabit olan başta kalır · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5.5 yol haritası](../plans/2026-08-26-queenagent-v5-5-roadmap.md) — Madde 93 ·
**Üstüne geldiği:** [Madde 91](2026-08-27-queenagent-m91-kip-gelir-uygulama-design.md)
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

Yönerge konuşmanın **ortasına** konuyor — skill'in değiştiği yere. Kural şu: bir kullanıcı mesajının
skill'i bir öncekinden farklıysa, o mesajın önüne o skill'in metni giriyor.

Sonucu: skill dört kez değiştiyse istekte dört ayrı yönerge metni duruyor, ve en eskisi kırk mesaj
geride kalmış oluyor. Model bugün geçerli olan kuralı bulmak için konuşmanın içinde en yeni
kopyayı aramak zorunda, ve arada başka üç tanesi var.

## Ne olur

İstek yeniden diziliyor:

```
[ sabit yönerge ]  [ ... konuşma ... ]  [ güncel skill'in metni ]
```

Konuşmanın içinde yönerge kalmıyor. Yalnız **bir** metin gidiyor — o anki skill'inki — ve en sonda
duruyor.

## Neden en son

İki ayrı ölçü aynı yeri gösteriyor *(kullanıcı kararı, 26 Ağustos)*:

- **Dikkat.** Doğruluk bağlamın başında ve sonunda en yüksek, ortasında %30'dan fazla düşüyor. En
  sonda olmak yönergeyi yüksek dikkat bölgesine koyuyor.
- **Önbellek.** Sabit olan başta durursa önek korunuyor; değişken olan sonda durursa değiştiğinde
  yalnız kendisi geçersizleşiyor.

## Güncel olan hangisi

En yeni kullanıcı mesajının skill'i. Cevabı beklenen tur hangi skill ile gönderildiyse, o.

Eski turların skill'leri **kayıtta kalıyor** — hangi turun hangi yönergeyle konuştuğu okunmaya
devam ediyor. Değişen yalnız modele ne gönderildiği.

## Her turda taşınıyor

Bir cevap on altı tura kadar sürebiliyor, ve her tur kendi isteğini gönderiyor. Blok sonda kalmak
için **her turda** taşınıyor — yani araç sonuçları geldikçe blok onların da arkasına geçiyor.

Bedeli biliniyor ve kabul edildi: blok her turda yeniden işleniyor. On altı turluk bir cevapta bu
~8k token, yani kuruşlar — önbellekten gelen girdi 1M token başına $0.20.

Taşınmasaydı ikinci turdan itibaren blok araç yazışmalarının **gerisinde** kalırdı, ve maddenin
kendi gerekçesi ilk turdan sonra geçerliliğini yitirirdi.

## Taşınamayan tek şey

`tools` isteğin ayrı bir alanı ve her zaman en başta işleniyor. Madde 91'in kipi *araç kısıtı*
olarak başta kalıyor — ve iş zaten kısıtın kendisinde, metninde değil.

## Kırmızıya dönecek testler

**`test_stream_answer.py` — dört**

1. Yönerge isteğin **en son** parçası: konuşmanın arkasında duruyor.
2. Geçmişi ne olursa olsun **tek bir** yönerge gidiyor, ve gönderilen o anki skill'inki. Daha önce
   başka bir skill ile konuşulmuş olması bir şey eklemiyor.
3. Konuşmanın **içinde** yönerge yok: mesajların arasında sistem satırı geçmiyor.
4. Blok her turda taşınıyor: araç sonucu geldikten sonraki turda da en sonda duruyor.

**`test_xai_engine.py` — bir**

5. Motor sırayı bozmuyor: sabit olan başa geçiyor, en sonda ne varsa en sonda kalıyor.

Toplam **beş kırmızı.**

## Ölçüsü değişen test

`test_a_selected_skill_reaches_the_engine_as_an_instruction`, yönergeyi `seen[0]`'da arıyor. Artık
`seen[-1]`'de. İddiası değişmiyor — composer'dan motora giden yol tek yol, ve uçtan uca burada
sınanıyor.

## Silinen testler

Üçü de **yönergenin tekrarı** hakkında, ve tekrar diye bir şey kalmıyor:

| Test | Neden düşüyor |
|---|---|
| `test_the_same_skill_twice_running_says_it_once` | Kaç kere söyleneceği artık bir kural değil: hep bir tane gidiyor |
| `test_a_reply_in_between_does_not_bring_it_back` | Aynı sebep — geri getirilecek bir şey yok |
| `test_a_skill_left_and_taken_up_again_is_said_again` | İddiası tasarım gereği artık **yanlış**: bırakılıp geri alınan skill ikinci bir metin üretmiyor |

İlk ikisinin ayakta kalan iddiası — *"bir tane gider"* — 2 numaralı testin içinde.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `Message.skill` | Kayıt hangi turun hangi yönergeyle konuştuğunu söylemeye devam ediyor |
| `SYSTEM_PROMPT` ve nereye konduğu | Sabit olan başta kalıyor; `XaiEngine` aynı |
| Kipin araç kısıtı | 91 yerinde, ve `tools` zaten taşınamıyor |
| `skills.py` metinleri | 94'ün işi |
| Ön yüz | Bu madde isteğin şeklini değiştiriyor, ekranı değil |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Ön yüz baştan sona yeşil kalır. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` derlenmiyor — ön yüz değişmiyor.
