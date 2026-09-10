# Madde 190 — okumanın kod geçişi · uygulama turu

**Kaynak:** [test turunun tasarımı](2026-09-10-queenagent-m190-kod-gecisi-testler-design.md),
[okuma kopyası](../../2026-09-09-queenagent-modele-giden-metinler.md) *(§1, §3, §4, §5, §6 — hedef
metinler)* ve [düzeltme log'u](../../2026-09-09-queenagent-metin-duzeltmeleri.md) *(35 kayıt)*.

**Test turu:** `1a4cbf3` — 34 kırmızı, iki bekçi yeşil.

## Ne yapılacak

`prompt.py`'yi okuma kopyasına **eşitlemek**. Belge kodun ne demesi gerektiğinin tanımıdır; bu tur
o tanımı koda indiriyor, ve indirdiği anda belgenin *"kodda hâlâ eski"* notları düşüyor.

Metin kararı verilmiyor. Her cümle 9 Eylül ile 10 Eylül arasında kullanıcıyla karara bağlandı ve
log'da gerekçesiyle duruyor. Bu turun elinde tek bir karar var, ve onu da okuma önceden verdi
*(aşağıda, kelime tavanı)*.

## Altı blok

| Blok | Sabit | Ne oluyor | Log |
|---|---|---|---|
| A | `SYSTEM_PROMPT` | 2. ve 4. paragraf yeniden yazılır | 1–6, 29 |
| B | `START_A_SCENARIO` | tamamı: beş adım, başlık + madde biçimi | 7–18 |
| C | `EDIT_PROMPTS` | tamamı: üç adım, başlık + madde biçimi | 19–24 |
| D | `WRITE_FRAME_SYSTEM_PROMPT` | dört paragraf → açılış + sekiz madde | 25–28, 33 |
| E | `SDXL_PROMPT_RULES` | dört paragraf → açılış + yedi madde | 16, 30, 34 |
| F | §6'nın 18 araç tarifi | emir başa, bir madde bir kural | 30–32, 34, 35 |

`mark_step_done` elden geçmiyor: 203 aracı kaldırıyor, ve bugün yazılan metin silinecek metin olur.

## Üç yeni sabit, ve `tools.py`'nin teli

34 numara üç `update_*` aracının `tags` alanını büyüttü: alan artık **kendi** kategorilerini sayıyor
ve şekil cümlesini arkasına alıyor. Bugün üçü de ortak `AN_ENTRYS_NEW_TAGS`'i gösteriyor, yani üçü
de aynı cümleyi okuyor.

```python
UPDATE_CHARACTER_TAGS = f"{ADD_CHARACTER_TAGS} {AN_ENTRYS_NEW_TAGS}"
```

Üçü de bu şekilde kurulur, ve `tools.py`'nin üç `"tags"` satırı `AN_ENTRYS_NEW_TAGS` yerine yeni
sabiti gösterir. `AN_ENTRYS_NEW_TAGS` duruyor — artık **ortak kuyruk**, tek başına bir alanın
tarifi değil.

Bu, `test_every_text_a_tool_carries_comes_from_the_prompt_module`'ün şartı: bir aracın taşıdığı her
dizge `prompt.py`'de büyük harfli bir adla yazılı olmalı. Birleştirme çağrı yerinde yapılamaz.

## Test turunun kaçırdığı üç test

Testler okunurken çıktı, ve **kod yazılmadan** çıktı. Üçü de bugün kırmızı; üçü de bu turun kodu
inmeden önce, kendi commit'inde iner.

**1 · `test_the_flow_opens_a_pov_entry_beside_each_character`** — `"2. The characters"` dizgesini
elle tutuyor. Test turu `STEPS`'i yeniden yazdı ve indeksle ölçen **altı** testi çevirdi; bu
yedincisi, çünkü `STEPS`'i kullanmıyordu. İddia değişmiyor: `pov_` girdisi karakter adımında
açılıyor. `STEPS[1]` okur.

**2 · `test_a_pov_entry_carries_neither_a_count_nor_an_outfit`** — `no count` ile `no outfit`'i
**akış metninde** arıyor. 34 numara ikisini de `ADD_CHARACTER_TAGS`'e indirdi *(ve 12 numara akıştan
sildi: akış kuralı değil zamanlamayı söyler)*. Testin baktığı yer değişir, iddiası değil — girdiyi
yazan araç orada.

**3 · `test_where_the_work_stopped_is_read_off_the_files`** — küçük harfli bir cümleyi
`_flow()`'un **küçültülmemiş** hâlinde arıyor. Belgedeki cümle *"The project's files are what say
how far it got"* diye, büyük harfle başlıyor: test bu hâliyle kod insin ya da inmesin kırmızı kalır.
`.lower()` ekleniyor.

Üçü de **test turunun işi**, geç bulundu. Ayrı bir kırmızı commit'e girmelerinin sebebi bu:
CLAUDE.md testi koddan önce ister, ve üçü de kod inmeden kırmızı verir.

Süitin sayısı **34 → 36**, üç değil iki: üçüncüsü zaten kırmızıydı — cümle metinde yok, ve
karşılaştırma da yanlış. Düzeltilmeseydi kod indikten sonra da kırmızı kalacaktı, ve sebebi
kodda aranacaktı.

## Kelime tavanı — okumanın önceden verdiği karar

Yeni akış metni elle sayınca **~480 kelime**; bugünkü kod 420, tavan **450**
*(`test_the_texts_stay_short_enough_to_be_read`)*. Adım biçimi ile 10, 11, 12, 13 ve 17 numaranın
bindirdiği kelimeler tavanı aşıyor.

Okuma bu ihtimali gördü ve kararı 9 numaraya yazdı:

> Kodda uygulanırken `test_the_texts_stay_short_enough_to_be_read` bunu söyleyecek; **aşarsa tavan
> yükselmez, iki yerde aynı şeyi söyleyen bir cümle silinir.**

Yani tavan 450'de kalır, ve kesilecek yer keyfî değil: **başka bir metinde zaten duran** cümle.
Kesme sırası da yazılı — 10 numara *"üçüncü maddenin son cümlesi"*, 11 numara *"birinci maddenin
ikinci cümlesi"* diyor. İkisi de 1. adımın maddeleri.

Sıra, ölçü kırmızı verdikten sonra şu şekilde uygulanır:

1. **1. adım, 3. madde: `If there is more than one plan, ask which.`** *(8 kelime)* — taban metin
   *"Ask rather than invent… a choice between two meanings -- is worth one question"* diyor ve o
   metin her istekte gidiyor. 10 numaranın kendi nominasyonu.
2. **4. adım, 3. madde: `A frame is born without one, and the model kept for writing them fills it
   in Step 5.`** *(16 kelime)* — `ADD_SCENE`'in tarifi *"A frame is born without its action.
   write_missing_actions writes every frame that is still without one"* diyor, ve 5. adım zaten
   aracı çağırıyor. Yasağın kendisi *(`Write no actions here.`)* duruyor, çünkü onu tutan test var.
3. **2. adım, 1. madde: `every step after it writes into a file that exists`** *(9 kelime)* —
   `START_SCENARIO`'nun tarifi *"A scenario is opened once and added to, never started a second
   time"* diyor. `once` duruyor, gerekçesi düşüyor.

Üçü 33 kelime; ilk ikisi yetmezse üçüncü gelir. **11 numaranın nominasyonu uygulanmaz** — 1. adımın
birinci maddesinin ikinci cümlesi *(`Later turns carry on from where the chat already is.`)*
`test_the_opening_moves_belong_to_the_first_turn`'ün tuttuğu `later turns carry on` dizgesidir, ve
Madde 107'nin dersi başka hiçbir yerde yazmıyor. İki yerde söylenen bir cümle değil; tek yerde
söylenen bir cümle.

Kesim olursa **belgeye ve log'a da iner:** §3'ün metni ile **36** numaralı kayıt. Kod ile okuma
kopyası arasında fark bırakmak, bu maddenin kapatmak için koştuğu şeyin ta kendisi.

## Bu turda yapılmayanlar

- **Yeni test yazılmıyor.** Üç düzeltme dışında test dosyaları açılmaz, ve o üçü yeni iddia
  getirmiyor.
- **`mark_step_done`** metnine dokunulmaz *(203)*.
- **Araçların cevap cümleleri** kapsam dışı: `tools.py`'de, modele *geri* söylenen metinler.
- **Yol haritası ile belgelerin kapanışı** ayrı bir commit'e kalır — kod yeşil olmadan yazılacak
  bir kapanış yok.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Süitin tamamı yeşil.** Test turunun 34 kırmızısı ve bu turun üç kırmızısı — otuz yedi — kapanır,
başka hiçbir test kırmızıya dönmez. Ön uç 648 yeşilde kalır: bu madde ön uca dokunmuyor.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-10-queenagent-m190-impl-plan.md).
