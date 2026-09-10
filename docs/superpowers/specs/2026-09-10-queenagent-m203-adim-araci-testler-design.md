# Madde 203 — adımı işaretleyen araç kalkar · test turu

**Kaynak:** [yol haritasının Madde 203'ü](../plans/2026-09-06-queenagent-v8-roadmap.md), ve
[düzeltme log'unun 11 numarası](../../2026-09-09-queenagent-metin-duzeltmeleri.md) — kutuların
*"yalnız bir not"*a inmesi.

## Ne kanıtlanacak

`mark_step_done` bir kutuyu dolduruyor, ve o kutuyu okuyan kimse kalmadı.

Aracın kuruluş gerekçesi *(Madde 198)* şuydu: model her turda kendi işaretini uyduruyor, sonraki
tur tanımıyor. **Onu çözen şey kutu biçimiydi, araç değil** — biçim `- [ ] 1.` diye sabitlendiği
anda ne yazıldığı da sabitlendi. Geriye aracın kendi kazancı kaldı: dört ayrı cevap cümlesi, ve tek
satırdan fazlasına dokunamaması.

**11 numara o kalanı da aldı.** Nerede kalındığını artık **dosyalar** söylüyor, kutular değil:
akış metni *"The project's files are what say how far it got; the plan's boxes are only a note"*
diyor. Bir notu dolduran araç, her istekte tarifini ve iki parametresini ödüyor.

## Akışın kapatma maddesi düşer — yeniden yazılmaz

Yol haritası *"kapanış maddesi `edit_file`'ı anar"* diyordu. **Kullanıcı kararı, 10 Eylül:** madde
tümüyle düşer.

Gerekçe 11 numaranın kendi cümlesi: kutu bir not, ve notu dolduran bir madde akış metninde yer
tutuyor — az önce 36 numarada üç cümle kesilen bir metinde. Plan `- [ ]` biçiminde yazılmaya devam
eder, **insan okusun diye**; onu dolduran bir tur artık yok.

Yani bu madde tek araç kaldırmıyor: bir **kuralı** da geri çekiyor. İkisi ayrı ayrı test edilir.

## Kaldırma kuyruğu: `plan_name`

`plan_name` bugün tek yerden çağrılıyor — `mark_step_done`'ın dalındaki geri düşüş *(207'nin
bıraktığı)*. Araç gidince fonksiyonun **hiç çağıranı kalmıyor**, ve 206'nın `folded`'ı gibi o da
gider. `scenario_name`'in docstring'i onu *"kardeşim"* diye anıyor; o cümle de düzelir.

## Kırılan ve doğan testler

**A — `test_tools.py`** *(4 kırmızı, 7 test gider)*

`test_every_tool_is_declared_to_the_model`'ün kümesi `mark_step_done`'ı bırakır — küme eşitliği
olduğu için **bugün kırmızı verir**, ve bu maddede kırmızının doğru sebebi budur.

İki yeni iddia, ötekilerin kalkışında yazıldığı biçimde: araç `TOOL_SPECS`'te yok ve `run_tool`
adını tanımıyor *(eski bir kayıt onu çağırırsa cevap alır, çökme değil)*; metinleri `prompt.py`'de
yok. Bir üçüncüsü kuyruk için: `plan_name` artık `tools.py`'de yok.

`_ticked`'in yedi davranış testi ile `PLAN`/`_planned` yardımcıları **gider** — yol haritasının
kendi cümlesi: *"`_ticked` ve testleri gider."* Konusu olmayan bir testin tutacağı bir şey yok.

**B — `test_modes.py`** *(1 kırmızı)*

`WRITES` listesi adı bırakır. Bu **tek başına kırmızı vermez**, ve sebebi bu koşunun iki kez
kaydettiği tuzak: `needs_permission` tanımadığı araca `False` diyor, yani kalkmış bir ad üstünde
dönen döngü hiçbir şey iddia etmeden yeşil geçer. Bu yüzden iddia `_WITHOUT_ASKING`'in kendisinden
okunur — 206 ve 207'nin testleri gibi.

**C — `test_skills.py`** *(1 kırmızı, 3 test → 1)*

Üç test aynı çekilen kuralı tutuyor:

| Test | Tuttuğu | Nereye gitti |
|---|---|---|
| `test_a_finished_step_reaches_the_plan` | taze sohbet devam edebilsin | 11 numara ile **dosyalara** — `test_where_the_work_stopped_is_read_off_the_files` orada |
| `test_an_approved_step_is_ticked_by_the_tool_that_ticks_one` | işareti model uydurmasın | kural çekildi; yerine **yokluk** |
| `test_a_finished_step_is_closed_without_rewriting_the_plan` | kapatmak planı yeniden yazmasın *(126)* | kapatma yok |

İkincisi kalır, adını ve iddiasını değiştirir: akış artık **ne aracı ne de `edit_file`'ı** adım
kapatmak için anıyor. Öteki ikisi gider, ve dersleri kaybolmuyor — birincisininki taşındığı testin
yorumuna yazılır, ikincisininki *(126)* kalan testin yorumunda durur.

**Ağ zaten kurulu:** `test_no_instruction_names_a_tool_that_is_gone` her alt çizgili kelimeyi
`TOOL_SPECS`'e karşı ölçüyor. Araç kalkar da madde metinde kalırsa o test kırmızı verir — yani
bu iki iş birbirini tutuyor.

## Kod yorumları: iki sayı

`run_tool`'un docstring'i *"the other eighteen"* diyor ve **bugün doğru** *(19 araç, motoru alan
bir tane)*. 203'ten sonra 18 araç kalır, yani cümle **on yediye** iner. Aynı sayı bir test yorumunda
ters yönde duruyor: `test_the_runner_takes_an_engine_and_the_tools_that_do_not_need_one_carry_on`
*"the other seventeen"* diyor, yani bugün yanlış, bu maddeden sonra doğru.

Kod tarafı uygulama turunun; **test yorumu bu turun**.

## Bu turda yazılmayanlar

- **Kod açılmıyor.** `tools.py`, `modes.py` ve `prompt.py` uygulama turunda değişir.
- **Kip kapısı tartışılmıyor:** araç da `edit_file` de yalnız EDIT'te sormadan koşuyordu, yani
  kalkmasıyla hiçbir kipin yetkisi değişmiyor.
- **Plan biçimi duruyor.** `- [ ]` yazımı akışın 1. adımında, ve `test_a_plan_is_written_as_boxes_to_tick`
  onu tutuyor. Bu madde kutuyu değil **kutuyu dolduran turu** kaldırıyor.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Altı kırmızı** — A'nın dördü *(envanter kümesi, ve üç yokluk iddiası)*, B'nin biri, C'nin biri —
ve yedi test ile iki yardımcı silinmiş olur. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-10-queenagent-m203-test-plan.md).
