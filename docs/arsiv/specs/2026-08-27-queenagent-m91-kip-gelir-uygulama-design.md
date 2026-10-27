# Madde 91 — Kip gelir: plan, sor, düzenle · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Test turu:** [testler tasarımı](2026-08-27-queenagent-m91-kip-gelir-testler-design.md) · kırmızı commit `de61402`
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder. Yeni test yazılmaz.

---

## Yedi dosya, iki katman

| Dosya | Ne olur |
|---|---|
| `domain/tools.py` | Altıncı araç: `write_plan`, ve adı zorlayan `plan_name` |
| `domain/modes.py` *(yeni)* | Üç kip, hangi araçları koyduğu, ve turu neyin bitirdiği |
| `domain/usecases/stream_answer.py` | Kipi alır: araçları ondan seçer, turu ondan bitirir |
| `presentation/routes.py` | Gövdedeki `mode`'u aşağı geçirir |
| `modes.js` *(yeni)* · `ModePicker.jsx` *(yeni)* | Üç kip, ve onları seçtiren düğme |
| `App.jsx` · iki ekran | Kip oturumun; hangi seçicinin açık olduğu tek değer |

## Altıncı araç

`write_plan(name, content)` yaratır ya da üstüne yazar. `create_file`'ın aksine numaralamıyor:
bir planın ikinci sürümü `x-plan-2.md` olsaydı hangisinin güncel olduğu kaybolurdu.

Adı `plan_name` zorluyor: uzantı atılıyor, gövde zaten `-plan` ile bitmiyorsa ekleniyor, sonuna
`.md` konuyor. `safe_name`'den **sonra** çalışıyor — temizlik onun işi, adlandırma bunun.

Kart yalnız ilk yazışta çıkıyor. İkinci yazış var olan bir dosyayı değiştiriyor, ve `edit_file`
aynı sebeple kart çıkarmıyor. Bu yüzden `WRITES_FILES`'a giriyor: ilk yazışta bir dosya doğuyor ve
kesikli kart onun için çıkıyor.

Aracın açıklaması plan kipinin tek yönergesi. Ayrı bir kip metni yok: bir aracın nasıl
kullanılacağı zaten açıklamasında duruyor, ve Madde 93 yönergenin isteğin neresine gireceğini
yeniden düzenliyor — bu madde oraya yeni bir metin bırakmıyor.

## `modes.py`

Üç ad, bir varsayılan, ve iki soru. `tools.py`'den `TOOL_SPECS`'i okuyor; tersi olmuyor, yani
döngü yok.

Tanımadığı kip **düzenle** sayılıyor. Eski bir tarayıcı ya da boş bir alan araçları sessizce
düşürmüyor — düşürseydi model karar vermiş gibi görünürdü, ki teşhis edilmesi en zor hâl bu.

`ends_the_turn(mode, tool)` tek bir çifti tanıyor: plan kipindeki `write_plan`. Bir sayaç değil bir
eşleşme, çünkü kural "bir kere yaz" değil "planı yazdıysan tur bitti".

## Cevap turu

`stream_answer` son parametre olarak kipi alıyor, varsayılanı düzenle — retry yolu ve bu maddeden
önce yazılmış her çağıran olduğu gibi çalışıyor.

İki yerde kullanılıyor: araç listesi `tools_for(mode)`'dan geliyor, ve bir araç koştuktan sonra
`ends_the_turn` soruluyor. Bittiyse kalan çağrılar da koşmuyor — planı yazdıktan sonra ikinci bir
çağrı, turun bitmesi gereken yerin ötesi.

Bitirme `cut_short`'tan ayrı bir bayrak. İkisi aynı şey değil: durdurulan tur diske `stopped`
yazıyor, planını yazıp biten tur bitmiş bir tur.

## Kapı

`post_message` gövdedeki `mode`'u okuyup `stream_answer`'a veriyor. Yazmıyor.

Skill mesaja yazılıyor çünkü sonraki turlarda konuşma yeniden kurulurken yönergesi ondan okunuyor.
Kipin böyle bir okuyucusu yok: o anda hangi araçların konduğuna karar veriyor, ve karar verilmiş
oluyor.

## Ekranda

`ModePicker` skill seçicinin eşi, tek farkla: **seçili kipe basmak temizlemiyor.** Skill'in
olmaması olağan hâl; kipin olmaması diye bir şey yok. Düğme de bu yüzden `picker--on` almıyor —
o sınıf "bir şey seçilmiş" demek, ve burada hep seçili.

Ayakta: **Mode · Skills · model · Send.** Kip skill'i yönetiyor, ve satır dıştan içe okunuyor.

Hangi seçicinin açık olduğu App'te **tek bir değer**: `null`, `"skills"` ya da `"mode"`. İki ayrı
boolean ikisi birden doğru olabilirdi, ve o zaman iki menü ekranın aynı köşesinde üst üste
dururdu. Escape hangisi açıksa onu kapatıyor — fark 67'nin sırası aynı, yalnız "Skills → model"
yerine "açık olan seçici" var.

Kip oturumun, `lastSkill` gibi: diske inmiyor, ve iki ekran aynı değeri alıyor.

## Ne değişmiyor

Beş aracın kendisi. Skill metinleri — 94'ün işi, ve bu madde onların yerine geçecek mekanizmayı
kuruyor. Yönergenin isteğin neresine gireceği — 93'ün işi. `Message.skill`. Tavan ve daire.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
npm run build --prefix queen-agent/frontend
```

`de61402`'nin on dokuz kırmızısı yeşile döner, ve o turda yazılıp bugün de yeşil olan ikisi
*(kip kayda yazılmıyor; kipsiz tur beş araç taşıyor)* yeşil kalır.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

**`dist` bu turda derleniyor ve aynı commit'e giriyor** — ön yüz değişiyor.
