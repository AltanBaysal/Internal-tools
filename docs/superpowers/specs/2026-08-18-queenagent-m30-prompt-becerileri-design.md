# Madde 30 — Prompt üreten üç beceri: düz, yapılı, denetleyen · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 30](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** [beceriler tasarım kararları](../research/2026-08-18-queenagent-beceriler-tasarim-kararlari.md) §2, §4, §5, §5b, §6, §9, §9b
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · Bu madde deneyi kuruyor

Üç yönerge geliyor, ama ikisi aynı girdiden aynı biçimde çıktı veren **iki yol**: biri promptu modele
tek parça yazdırır, öteki koda birleştirtir. "Yapı kaliteyi artırıyor mu" sorusu tahminle değil iki
dosya yan yana konarak cevaplanacak (§2). Tasarım kendi deneyini içinde taşıyor ve bu madde onu
kurar.

Üçüncü yönerge kodun göremediğine bakar. Ve yan iş olarak okuyucu, ürettiklerini gerçekten
gösterebilir hâle gelir (§9).

---

## 2 · Generate prompts — kontrol grubu

- Kare listesini sohbetten alır. **Yapı dosyası yok, `build_prompts` yok**: promptu model kendi
  yazar, baştan sona.
- Etiket sırası yapılı yolunkiyle **aynı** söylenir (`kalite → karakter → mekân → aksiyon → kamera`).
  Deneyin dürüstlüğü buna bağlı: tek değişken **kimin birleştirdiği** olmalı, hedef biçim değil.
- Çıktı `PROMPTS` listesi — `build_prompts`'un yazdığıyla aynı şekil, çünkü ikisi de aynı yere
  gidiyor (yol haritası Madde 30: "çıktı bir Python listesidir").
- Adı senaryodan türer ve **`-plain`** ile biter (`intro-plain.py`). Sebep tek: yapılı yolun çıktısı
  `intro-shots.py`; ikisi yan yana durabilsin diye adları çarpışmıyor.
- **Tek nefeste değil** (§5b): ilk kareler `create_file` ile, gerisi `edit_file` ile azar azar. Bu
  kural bu beceriye de işliyor — belgedeki cümle "hiçbir beceride" diyor.
- Promptlar **İngilizce**, sohbetin dili ne olursa olsun (§9b): onları bir görüntü modeli okuyor.

## 3 · Generate prompts+ — yapıdan üretim

Yapı §4'ün son hâli, yönergenin içinde **örnekle** verilir; şemayı kelimeyle anlatmak yerine
göstermek, modelin alan adlarını uydurmasını engelliyor.

- Tekrar edenler üstteki map'lerde, bir kez yazılır; kare **adı** taşır, metni asla. Karakteri
  güncellemek kırk yerde değil tek yerde değişmek demek — yapının bütün sebebi bu.
- `characters` liste, `location` düz string: bir karede birden çok karakter olabilir, bir kare tek
  yerde geçer. Karaktersiz kare boş liste.
- Karakter ve mekân etiketleri **sohbette kararlaştırılandan** alınır. Kararlaştırılmamış bir ad
  gerekiyorsa **sorulur**, uydurulmaz.
- **İki aşamalı yazım** (§5b): önce iskelet (`quality` + map'ler + boş `shots`) `create_file` ile,
  sonra kareler `edit_file` ile **beşerli partiler** hâlinde. Her parti diske iner, sonra sıradakine
  geçilir.
- **Öz-denetim `build_prompts`'tan önce** koşar (§6'nın ilk kapısı): kirli yapıdan liste
  üretilmez.
- Sonra `build_prompts` çağrılır. Yönerge **açıkça** promptu elle birleştirmeyi ve Python dosyasını
  elle yazmayı yasaklar; yoksa becerinin bütün anlamı kaybolur.
- JSON'un içeriği **İngilizce** (§9b): etiket dili.

## 4 · Verify shots — rapor eder, düzeltmez

- `list_files`/`read_file` ile yapı dosyalarını okur ve kural defterini uygular.
- **Hangi dosya, hangi kare, hangi kural** — üçü birden. Temiz dosya için de açıkça "temiz" der;
  sessizlik bir cevap değil.
- **Düzeltmez, dosya yazmaz.** Özellikle 3. kuralda "hangisi doğru kopya" kararı kullanıcınındır.
  Düzeltme, kullanıcının ayrı bir cümlesiyle olur.

### Kural defteri tek metin, iki okuyucu

Defter (§6) hem prompts+'ın öz-denetiminde hem Verify'da geçerli. **Tek sabit** olarak yazılır ve
iki yönerge onu içine alır; iki kopya ilk değişiklikte birbirinden ayrılırdı.

| # | Ne aranıyor | Ne |
|---|---|---|
| 1 | Map'te karşılığı varken karede **düz metinle** karakter/mekân tarifi | ihlal — asıl av: sessiz kopyanın geri dönüşü |
| 2 | Kalite etiketlerinin karenin alanlarında tekrarı | ihlal — kod bir kez ekliyor, çift basar |
| 3 | Aynı adın iki yapı dosyasında **farklı metni** | ihlal — `library.json`'suz yaşamanın bedeli: kopya serbest, **sapmış** kopya yakalanır |
| 4 | Tanımlı ama hiç anılmayan ad | **not**, ihlal değil |

**Adlandırma düzeltmesi:** §6'nın 2. kuralı "`style` etiketleri" diyor; aynı belgenin §4 ve §5c'si o
alanı **`quality`** olarak kesinleştirdi (gerçek stil yalnız LoRA tetikleyicisiydi). Kural burada
`quality` diye yazılıyor — kodda `style` diye bir alan yok.

**Eklenmeyen bir madde:** §5c negatif promptun kıyafete bağlı etiketleri için "istenirse" bir not
maddesi öneriyordu. İstenmedi; deftere girmiyor. Bir gün istenirse yeri belli.

---

## 5 · Yan iş — okuyucu `.json` ve `.py`'yi gösterebilsin (§9)

Okuyucu (Madde 23) her dosyayı Markdown çiziyor. Bir JSON'da bu **girintiyi yutar**, `PROMPTS`
listesinde satır sonlarını birleştirir, `#` ile başlayan bir Python yorumunu **başlığa** çevirir.
Yapı dosyalarını arayüzde gerçekten okuyabilmek buna bağlı — ve bu maddede ilk kez gerçekten JSON ve
`.py` doğuyor.

Kural: **`.md` Markdown, gerisi mono ve biçimi korunmuş.** Karar dosyanın **adından** verilir
(`.md` ile bitiyor mu), çip için hesaplanan üç harften değil — çip `jso` diyor ve bu bir uzantı adı
değil.

Mono gövde `.md pre`'nin ölçülerini ödünç alır (12.5px, satır yüksekliği 1.6, `white-space: pre`,
`overflow-x: auto`): kod bloğu neye benziyorsa kod dosyası da ona benzer, ve yeni bir ölçü
uydurulmaz. Kutu ve çerçeve **yok** — okuyucunun gövdesi zaten bir yüzey; blok içinde blok çizmek
kâğıda kâğıt koymak olurdu.

---

## 6 · Katman denetimi

**Arka uç:** `domain/skills.py` — üç metin daha ve paylaşılan kural defteri sabiti. Başka hiçbir
dosya değişmiyor: mekanizma Madde 29'da kuruldu, araçlar Madde 28'de.

**Ön uç:** `FilePanel.jsx` (adına göre iki gövde), `workspace.css` (`.reader__code`). Yeni istek
yok — dosyanın adı ve metni okuyucuda zaten var.

---

## 7 · Kabul ölçütü

1. Altı becerinin **hepsi** yönerge taşır; tanınmayan kimlik yine hiçbir şey eklemez.
2. Düz yönerge `PROMPTS` şeklini, `-plain` adını ve İngilizceyi söyler; yapıdan söz etmez.
3. Düz yönerge de partili yazımı söyler.
4. Yapılı yönerge şemayı **örnekle** verir; adı taşımayı, beşerli partileri, iskeleti ve
   `build_prompts`'u söyler; elle birleştirmeyi yasaklar.
5. Yapılı yönergede kural defteri **`build_prompts`'tan önce** geçer.
6. Kural defteri **tek metindir** ve hem yapılı yönergede hem Verify'da birebir aynı geçer.
7. Verify düzeltmemeyi ve dosya yazmamayı açıkça söyler; 3. kuralı kullanıcıya bırakır.
8. Okuyucu `.md`'yi Markdown çizer; `.json`/`.py`'yi mono ve **birebir** gösterir — girinti durur,
   `#` başlık olmaz.
9. Mono gövde kaydırılabilir ve kod bloğunun ölçülerini taşır.

## 8 · Risk

Yönergelerin modele gerçekten uyduğu Madde 35'in elle turunda görülür (Madde 29'un aynı sınırı).
Deneyin kendisi de oradadır: iki `PROMPTS` dosyasını yan yana koyup bakmak bir testin yapabileceği
iş değil.
