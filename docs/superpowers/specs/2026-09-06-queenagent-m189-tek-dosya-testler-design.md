# Madde 189 · test turu — modele giden her metin tek dosyada

**Kaynağı:** [yol haritası, Madde 189](../plans/2026-09-06-queenagent-v8-roadmap.md).
183 `793fd38`'de kapandı.

---

## Ne kanıtlanacak

Modele giden metinler bugün dörde dağılmış: `prompt.py`, `skills.py`, `tools.py`'nin `TOOL_SPECS`'i
*(~900 satır, hacmin yarısı)*, ve `stream_answer`'ın kap başlığı. Hepsi **tek yerde**, adlandırılmış
sabitler olarak toplanacak, ve kod onları çağıracak.

## Yeni dosya açılmıyor: yer `prompt.py`

`prompt.py` zaten *"promptun durduğu yer"* — `SYSTEM_PROMPT` ve `LAST_ROUND` orada, ve her şey oradan
import ediyor. Yanına bir `prompts.py` koymak, adı bir harf ayrı iki dosya demek olurdu; hangisinin
ne tuttuğu ilk günden karışır. Metinler **oraya** taşınıyor ve dosya büyüyor — bilerek, çünkü
maddenin istediği şey tek dosyada okunabilmesi.

Döngüsel import yok: `prompt.py` bugün hiçbir şey import etmiyor, `tools.py` ve `skills.py` ondan
alacak.

## Sınır: modele **söylenen** taşınır, modele **geri söylenen** kalır

Bu ayrımı ben kararlaştırdım; itiraz yol haritasının kararını değiştirir.

**Taşınan — talimat.** Her çağrıda aynı olan, bir kez yazılmış, davranışı şekillendiren metin:
`SYSTEM_PROMPT`, `LAST_ROUND`, iki skill metni, `SDXL_PROMPT_RULES`, `WRITE_FRAME_SYSTEM_PROMPT`,
`TOOL_SPECS`'in **her** açıklaması *(araç ve parametre)*, kap başlığı, ve `refusal_text`'in metni.

**Kalan — cevap.** `ToolResult(...).text` cümleleri ve `build_prompts`'un `BadStructure` cümleleri.

**Ve kalmasının sebebi tembellik değil.** Bir cevap cümlesi, yalnız o çağrı anında var olan
değerlerin üstüne kurulmuş bir f-string:

```
f"Added {counted(len(born), 'scene')} to {source} as {_made_frames(born)}{after}."
```

Sabite çekilince **şablona** dönüşür, ve bir şablon çağrının şeklinin başka bir dosyada tutulan
**kopyasıdır**. Deponun kendi kuralı bunun ne olduğunu söylüyor: *kopya, bayatlayacak olan taraftır.*
Taşımak bir tekrarı başka bir tekrarla değişmek olurdu.

Okumanın değeri de talimat tarafında: davranışı kuran onlar, ve birbirini tekrar eden onlar.

## Üç nöbetçi, ve neden üçü birden

`hasattr` işe yaramıyor: `tools.py` metni `prompt.py`'den import edince ad yine modülün özniteliği
olur, ve `hasattr(tools, "SDXL_PROMPT_RULES")` doğru taşımadan sonra da `True` döner. Nöbetçi
**kaynağa** bakıyor — `test_notebook.py`'nin defter kaynağını taraması gibi.

| # | Test | Ne söylüyor |
|---|---|---|
| 1 | `TOOL_SPECS`'in taşıdığı **her** metin `prompt.py`'nin sabitlerinden biri | ~90 metnin tamamı, tek testle |
| 2 | Taşınan adlar eski dosyalarında **atanmıyor** | kaynak taraması; import edilmiş olması yetmez |
| 3 | `prompt.py` altı ayaklı metni de tutuyor | 1 ve 2'nin *"boş modül"*le geçmesini engelleyen |

1. test iç içe de yürüyor: `add_scene`'in `scenes`'i bir dizi, ve öğesinin alanlarının da açıklaması
var. Bir seviyede duran tarama, hacmin görmediği kısmında bırakırdı.

## Yirmi kadar import satırı

`WRITE_FRAME_SYSTEM_PROMPT` ve `SDXL_PROMPT_RULES` bugün `tools`'tan import ediliyor —
`test_tools.py`'de on beş yerde, `test_skills.py`'de ikide. Hepsi `prompt`'a dönüyor.

**Yeniden ihraç yok.** `tools.py` taşınan adı kendi üstünden de sunsaydı, tek yer iki ad olurdu ve
maddenin bütün bahsi o.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. `queen-agent` **35 kırmızı** verdi: altısı nöbetçiler,
gerisi taşınan import satırları. Çoğu **assertion değil `ImportError`** — `prompt.py` o adları henüz
tutmuyor. Çirkin ama doğru kırmızı: testin söylediği şey tam olarak metnin orada olmadığı.

Öteki üç takım kımıldamadı — **589 · 739 · 591.**

## Kırmızı turun tuzağı

v7'de altı kez, 183'te bir kez daha: **hiçbir şey olmadığı için geçen test.** Buradaki hâli 1. ve
2. testte — biri boş bir sabit kümesiyle, öteki boş bir kaynakla geçebilir. 3. test ikisinin de
altını dolduruyor, ve 1. test kümenin boş olmadığını kendi içinde de ölçüyor.
