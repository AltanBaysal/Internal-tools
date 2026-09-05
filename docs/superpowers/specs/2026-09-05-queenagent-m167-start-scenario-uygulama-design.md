# Madde 167 · uygulama turu — `start_scenario`

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m167-start-scenario-testler-design.md).
Commit `b1f3585` dokuz vak'ayı çiviledi; bu tur onları yeşile çevirir.

---

## `tools.py`

**Bir sabit** — dört boş harita, tek yerde:

```python
EMPTY_SCENARIO = {"characters": {}, "outfits": {}, "locations": {}, "frames": []}
```

Sabit olarak, çünkü şekil buradan başka hiçbir yerde yazılı değil ve araçlar onu okuyacak. `dict`
mutable, o yüzden yazarken kopyalanır — ya da doğrudan `json.dumps` edilir ve kimse ona dokunmaz.
İkincisi: yazılan şey metin, saklanan şey sabit.

**Bir yardımcı** — `plan_name`'in kardeşi, aynı gerekçeyle ve onun hemen yanında:

```python
def scenario_name(name):
    """A scenario is named so that Madde 171's door and this tool meet on one extension."""
    return f"{name.rsplit('.', 1)[0]}.json"
```

`safe_name`'den **sonra** koşuyor: modelden geleni temizlemek onun işi, adlandırmak bunun.

**Bir araç tanımı** — `create_file`'ın hemen ardında, tek parametre `name`. Açıklaması iki şeyi
söylüyor: neyi doğurduğunu, ve **kareleri boş doğurduğunu** *(sonraki araçlar dolduruyor)*.

**Bir dal** `run_tool`'da, `create_file`'ın yanında:

```python
if name == "start_scenario":
    wanted = scenario_name(safe_name(args.get("name")))
    if wanted in file_store.list_names(project_id):
        return ToolResult(
            f"There is already a file called {wanted}. Open it and add to it, or pick "
            "another name for a new scenario.",
            None, wanted, "Already there",
        )
    written = file_store.write(
        project_id, wanted, json.dumps(EMPTY_SCENARIO, indent=2, ensure_ascii=False)
    )
    return ToolResult(f"Started {written}.", written, written, "Started")
```

`create_file`'ın adları listeden sorma alışkanlığı burada da: soru **adın alınmış olup olmadığı**,
ve bunu öğrenmek için koca bir dosyayı geri çekmek kimsenin ihtiyacı olmayan iş.

**`WRITES_FILES`'a bir ad** — kart çiziliyor, dosya gerçekten doğuyor.

## `modes.py`

`_WITHOUT_ASKING[EDIT]`'e `start_scenario`. Ask ve plan kipleri ona dokunmuyor, yani soruyorlar —
`create_file`'ın durduğu yer.

## Neden `unique_name` değil

`create_file` alınmış ada **numara vermiyor**, reddediyor *(Madde 69)*; `unique_name` çöp ve proje
adları için. Aynı kural burada daha da sıkı: `bar-scene-2.json` diye ikinci bir senaryo, hangisinin
gerçek olduğunu bir sonraki adımın tahmin etmesi demek — ve bu koşunun bütün araçları *"dosyayı ver,
ben doldururum"* diye çalışıyor.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Beklenen: dokuz kırmızının dokuzu da yeşil**, `queen-agent` tarafında **698 yeşil**
   *(`b1f3585`'te 689 + 9)*.
3. `test_edit_mode_asks_for_nothing` `TOOL_SPECS` üstünde dönüyor: araç eklenip kip satırı
   eklenmezse **o kırmızıya düşer**. İkisi aynı turda gidiyor, yani yeşil kalmalı — düşerse
   `modes.py` unutulmuştur.
4. Öteki üç takım rakamlarını korur. `dist` derlenmez.

## Koşarken çıkan iki kırmızı, ve ikisi de test tarafındaydı

**`test_every_tool_is_declared_to_the_model` kaçırıldı.** Bütün araç adlarını tek küme olarak sayan
bir bekçi var, ve yeni bir ad onu kırmızıya düşürüyor. **Test turunda görülmeliydi** — yayılma alanı
taraması `TOOL_SPECS` üstünden yapıldı ama sonuç kesildi ve bu satır listeye girmedi. Ad burada
eklendi; doğru yeri `b1f3585`'ti.

**`test_start_scenario_says_what_it_started` kendi yazdığım tuzağa düştü.** Aynı `tmp_path` üstünde
iki kez çağırıyordu, ve ikinci çağrı birincinin yazdığı senaryoyla karşılaşıp reddi döndürüyordu.
Tek çağrı, iki yarısı da onun üstünden okunuyor.

**Bu ikisi kodun kırmızısı değildi:** `start_scenario`'nun altı testi ilk koşuda yeşil geçti.
