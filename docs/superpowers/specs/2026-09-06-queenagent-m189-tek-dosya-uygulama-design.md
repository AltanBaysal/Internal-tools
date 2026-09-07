# Madde 189 · uygulama turu — modele giden her metin tek dosyada

**Kaynağı:** [test turu](2026-09-06-queenagent-m189-tek-dosya-testler-design.md), `42246e1`'de
kırmızı. Sınırın gerekçesi orada yazılı; burada yalnız taşımanın nasıl yapıldığı var.

---

## Ne yapılıyor

Modele giden her talimat `prompt.py`'ye, adlandırılmış sabit olarak geçiyor. `tools.py` ve
`skills.py` metni yazmayı bırakıyor, **çağırıyor**.

## Modülü adıyla import etmek, adları tek tek değil

`from ... import prompt`, sonra `prompt.ADD_CHARACTER`. Altmış küsur adı import satırında saymanın
iki bedeli var: satır her yeni araçta değişir, ve `tools.py` o adları kendi modülünün özniteliği
yapar — yani maddenin kapattığı ikinci yeri geri açar. Modül adıyla çağrıldığında metnin nerede
yazıldığı çağrının kendisinde okunuyor.

Döngü yok: `prompt.py` hiçbir şey import etmiyor, ve etmeyecek.

## Aynı cümleyi iki araç söylüyorsa, sabit de tek

Dokuz araç `"The scenario's file name."` diyor, beşi `"The structure file's name."`, üçü
`"Which frame, by its number, counting from 1."`. Bunlar araç başına ayrı sabit olmuyor —
maddenin bütün derdi *bir kural iki yerde yazılınca görünmez olması*, ve altmış sabitin içine
kopyayı gömmek onu görünmez bırakmanın yeni bir yolu olurdu.

Paylaşılanlar kendi başlığı altında, adları ne olduklarını söylüyor:
`THE_FILES_NAME`, `THE_SCENARIOS_FILE`, `THE_STRUCTURES_FILE`, `AN_ENTRYS_NEW_TAGS`,
`AN_ENTRYS_NEW_NAME`, `WHICH_FRAME`. Geri kalan her metin `ARAÇ` ya da `ARAÇ_PARAMETRE`.

## `SDXL_PROMPT_RULES` birleştirmesi de `prompt.py`'de

Altı araç açıklaması `"\n" + SDXL_PROMPT_RULES` ile bitiyor. Nöbetçi araca *gerçekten* giden metni
arıyor — yani birleşmiş hâlini — o yüzden birleştirme `prompt.py`'de yapılıyor ve `ADD_CHARACTER`
kuralları da içeriyor. `tools.py`'de artı işareti kalmıyor.

## Spec'in listesine iki satır eklendi

Kırmızı turun listesi kap başlığını sayıyordu, dosya adları satırını saymıyordu — o satır
`stream_answer` taranmadan önce yazılmıştı. `_named`'in iki cümlesi *(dolu hâli ve boş hâli)*
sınırın kendi tarifine birebir uyuyor: her istekte aynı, bir kez yazılmış, davranışı şekillendiren
metin. Bırakılsalardı maddenin iddiası — *depoda başka yerde prompt yok* — daha kapanırken yanlış
olurdu. Sınır genişliyor, daralmıyor; hiçbir test buna karşı değil.

## Şablon olan üç metin, ve neden cevap sayılmıyorlar

`OPENED_FILES`, `REFUSED`, ve dolu hâliyle dosya adları satırı bir değer alıyor — kaç dosya, hangi
araç, hangi adlar. Kırmızı turun *"cevap kalır"* kuralı bunları dışarıda bırakmıyor, çünkü o kural
**neyin ölçüldüğüne** dayanıyordu: bir `ToolResult` cümlesi o çağrının ne yaptığını anlatır, ve
şablona çekilince çağrının şeklinin kopyası olur. Bu üçü ise modele **davranış** söylüyor —
kutunun beşten fazlasını tutmadığını, kipin değişmediğini, projenin neleri tuttuğunu. Aldıkları
değer cümlenin konusu değil, içine yerleşen tek kelime.

## Dokunulmayanlar

- `_frame_seen` — `Scene:`, `In frame:`, `Place:`, `Note:`. Çağrı başına kurulan bir mesajın
  şekli; kareyi gezen döngüyle birlikte yaşıyor ve ondan koparılamaz.
- `ToolResult(...).text` ve `build_prompts`'un `BadStructure` cümleleri — kırmızı turun kararı.
- `EMPTY_SCENARIO` — modele giden bir metin değil, diske giden bir şekil.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent`'ın 35 kırmızısı kapanıyor; öteki üç takım
kımıldamıyor.
