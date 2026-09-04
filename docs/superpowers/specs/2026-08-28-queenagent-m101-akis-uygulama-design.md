# Madde 101 — Start a scenario doğar · **uygulama turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [akış tasarımı](../research/2026-08-27-queenagent-akis-tasarimi.md) — ve
[v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Blok 6, Madde 101 ·
**Turun birincisi:** [test turu](2026-08-28-queenagent-m101-akis-testler-design.md) — on iki
kırmızı commit'lendi *(`cd87124`)*.
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder.

---

## Metnin kipi

`skills.py`'nin başlığındaki kural burada da geçerli, ve burada daha çok geçerli: metin *"şunu
yap"* değil, *"bu iş şöyle yapılır"* kipinde. Seçili bir skill mesajdan sonra seçili kalıyor, ve
emir kipindeki bir yönerge kullanıcı *"teşekkürler"* yazdığı anda yeni bir senaryo kurmaya başlar.

Akış metninde bu daha zor, çünkü anlattığı şey bir sıra. Çözümü: sırayı **akışın kendi tarifi**
olarak yazmak — *"beş adım, şu sırayla"* — ve her adımı *"bu adım şunu bırakır"* diye anlatmak.

## Metnin taşıdıkları

Testlerin tuttuğu sözcükler tasarımın kararları:

| Cümle | Karar |
|---|---|
| `write_plan`, `read_schema`'dan önce | İlk iş plan, kullanıcı ne yazarsa yazsın |
| *"carry on from the step it left open"* | Yarım kalan iş yeni sohbetten sürüyor |
| *"approves"* | Her adım onaya kadar döngü |
| *"placeholder"* + *"never stop the flow"* | K34 |
| *"one sentence"* | K33 — sahneler iki yerde |
| `build_prompts` + *"does not change skill"* | K32 |

Metin ayrıca **kıyafetin duyulduğu yerde yazıldığını** söylüyor: karakter adımında *"gecelikte"*
diyen kullanıcıya mekân adımı aynı şeyi bir daha sormuyor. Ve karakter denemesini
*(`build_character_prompts`)* bir yan kapı olarak anıyor — adım değil, teklif.

## Şema metne girmiyor

`read_schema` çağrılıyor, şema yazılmıyor. Madde 96'nın kuralı: yönerge her turda gidiyor, şema ise
yalnız yazma anında lazım. İki skill de aynı kapıdan geçiyor, yani tek kopya.

## Seçici

İki satır, akış önce. Sıra bir tercih değil, bir cevap: eli boş gelen kullanıcının yolu akış, elinde
yapı dosyası olanınki prompt+.

prompt+'ın açıklaması da değişiyor. Bugünkü satır — *"Build from parts, so a character never
drifts"* — **nasıl** çalıştığını söylüyor, **ne zaman** seçileceğini değil, ve iki satır yan yana
durunca ayırt edici olan ikincisi. Yeni satır koşulunu söylüyor: elde olan bir yapı dosyası.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Araçlar | Beşi de yerinde; akış yeni bir araç istemiyor |
| `prompt.py` | Nasıl çalışılacağı orada, ve her skill'e uyuyor |
| `schema.py` | Şema araçtan geliyor |
| `instruction_for` | Bilinmeyen ad hâlâ boş dönüyor |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

On iki kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` aynı commit'te derleniyor — seçicide bir satır değişiyor.
