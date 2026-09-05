# Madde 181 · test turu — eylem satırının içi

**Kaynağı:** [yol haritası, Madde 181](../plans/2026-09-05-queenagent-v7-roadmap.md).
Madde 180 `dac361a`'da kapandı.

---

## Ne kanıtlanacak

Yazara *"kimsenin görünüşünü, kıyafetini ya da mekânı tarif etme"* deniyor, ve yazar bunu **bedenin
kendisine** de uyguluyor. Deneme 4'te cinsel karelerin hepsi örtük döndü — *bodies connected*, *deep
rear penetration* — organ hiç adlandırılmadı. SDXL yalnız **adı geçeni** çizer; adı geçmeyen bölgeyi
uydurur, ve kullanıcının 20 kareyi elle düzeltmesinin sebebi bu.

Kullanıcının kararı iki şeyle sınırlı: **organ görünürlüğü** ve **yüz ifadesi.** Kıyafete
karışılmıyor — bir karakter kadrosunda kıyafetsizse zaten çıplak, ve `nude` yazmak yazarın işi değil.

## Yedi test

Hepsi `test_tools.py`, Madde 176'nın bölümünde — yazarın sistem promptunu ölçen testler orada.

| # | Test | Ne söylüyor |
|---|---|---|
| 1 | Yazar görüneni adlandırmakla yükümlü | *"name what is visible"* |
| 2 | Terimler örnek olarak metnin içinde | `penis`, `vagina` |
| 3 | Sebebi de yazılı | örtmece → modelin uydurması |
| 4 | Yüz ifadesi isteniyor | *"expression"* |
| 5 | Çıplaklık yazarın işi değil | kadroda kıyafeti olmayan zaten çıplak |
| 6 | Kıyafet kuralı yerinde duruyor | 176'nın cümlesi kaldırılmadı |
| 7 | **`SDXL_PROMPT_RULES` bu terimleri taşımıyor** | maddenin en önemli sınırı |

7'nin ikinci yarısı araç açıklamalarının üstünden geçiyor: `SDXL_PROMPT_RULES` dört aracın
açıklamasına ekleniyor *(`add_character`, `add_outfit`, `add_location`, `build_prompts`)*, ve orada
anatomi **tam da yazılmaması gereken** şey. Metnin içinde durup durmadığına bakmak yetmez — modelin
gerçekten okuduğu yüzey araç açıklaması, ve test oradan bakıyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` **5 kırmızı** vermeli — 6 ve 7 bugünkü metinde
zaten doğru, ve öyle kalmalarını istiyoruz. İkisi nöbetçi: 181 onları bozarsa kırmızıya döner.

## Kırmızı turun tuzağı

180'de iki kez daha çıktı: **hiçbir şey olmadığı için geçen test.** Burada tuzağın şekli farklı —
`not in` ile yazılan bir test *(6 ve 7)* metin boşalsa da geçer. İkisi de önce metnin **dolu**
olduğunu ölçüyor: 6 kıyafet cümlesini arıyor, 7 kuralların araç açıklamasında bulunduğunu.
