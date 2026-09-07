# Madde 182 · test turu — POV ayrı bir karakter

**Kaynağı:** [yol haritası, Madde 182](../plans/2026-09-05-queenagent-v7-roadmap.md).
Madde 181 `ba20e72`'de kapandı. Koşunun son maddesi.

---

## Ne kanıtlanacak

Bir karenin kadrosunda olmak **ya hep ya hiç**: derleyici kadrodakinin bütün etiketini yazıyor.
POV'da o kişinin hiçbiri kadrajda yok, ve SDXL etiketleri asacak beden bulamayınca **görünen kişiye**
asıyor — kadın adamın saçını alıyor, ve prompt kadrajda tek kişi varken `1girl` ve `1boy` diyor.

Kullanıcının kararı **kod değil kural**: `pov_kyle` diye ikinci bir karakter, kısa ve sayısız,
kıyafetsiz. Ve **karakter doğarken** açılıyor, POV karesi gelince değil.

## Beş test, iki de düzeltme

`test_skills.py`:

| # | Test | Ne söylüyor |
|---|---|---|
| 1 | Akış her karakterle birlikte `pov_` sürümünü açar | 2. adımda, karakteri kuran yerde |
| 2 | O girdide sayı da kıyafet de yok | girdinin kendisi |
| 3 | Prompt skill'i POV karede o girdiyi adlandırır | düzeltme turu burada geçiyor |

`test_tools.py`:

| # | Test | Ne söylüyor |
|---|---|---|
| 4 | `SDXL_PROMPT_RULES` sayımın istisnasını taşır | bugün *her* girdi sayı taşır diyor |
| 5 | **Nöbetçi:** sayım kuralının kendisi yerinde | metin boşalırsa 4 sessizce geçmesin |

## Çarpışma: `pov_` bir araç adı gibi görünüyor

`test_no_instruction_names_a_tool_that_is_gone` skill metnindeki **alt çizgi taşıyan her kelimeyi**
alıp `TOOL_SPECS`'te arıyor — ve testin kendi gerekçesi bunun elle tutulan bir listeye
dönüşmemesi. `pov_` o süzgece takılıyor.

Testin gerekçesi *"sonradan silinen bir araç, birinin adını eklemeyi hatırlamasıyla değil bu testin
var olmasıyla yakalansın"*. Muafiyet o gerekçeyi bozmuyor: silinen bir araç hâlâ yakalanıyor,
muaf olan tek şey **bir adlandırma kuralı**, ve metinde `pov_kyle` değil `pov_` geçiyor — yani muaf
tutulan şey bir ad değil, önekin kendisi. Test bunu söyleyerek yapıyor.

İkinci düzeltme yok; sayılan tek şey bu.

## Kelime tavanı

`START_A_SCENARIO` ≤ 450, `GENERATE_PROMPTS_PLUS` ≤ 300 kelime — *"buradan sonra bir cümle ancak bir
cümle silinerek girer"*. İki metin de büyüyor, ve tavan uygulama turunda kırmızı verirse **eklenen
cümle kısalır, tavan değil.** Tavanı yükseltmek, tavanı olmamakla aynı şey.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` **4 kırmızı** vermeli — 5. nöbetçi bugün de
doğru. Kelime tavanı testi bu turda yeşil kalmalı: metinler henüz büyümedi.

## Kırmızı turun tuzağı

180 ve 181'de üç kez çıktı. Buradaki hâli 5. testte: *"sayım kuralı yerinde"* diyen bir nöbetçi,
metin bomboşsa da... hayır, `in` ile yazıldığı için boş metinde kırmızıya döner. Asıl tuzak 4'te —
`"no count"` gibi bir parça metnin **başka bir yerinde** de geçebilir. 4 bu yüzden istisnanın
kendi cümlesini arıyor, tek bir kelimeyi değil.
