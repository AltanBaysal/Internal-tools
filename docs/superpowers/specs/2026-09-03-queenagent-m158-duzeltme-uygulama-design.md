# Madde 158 — `update_frame` · **uygulama turu**

**Tarih:** 3 Eylül 2026 · **Branch:** `feat/v6` · **Test turu:**
[m158 düzeltme testler design](2026-09-03-queenagent-m158-duzeltme-testler-design.md) ·
**Kırmızı commit:** `test(m158)`

19 test kırmızı. Bu belge onları yeşile çeviren kodu anlatır.

## `_UPDATABLE`

```python
_UPDATABLE = _FRAME_FIELDS + ("scene",)
```

`_FRAME_FIELDS` prompta giren dörtlü *(152)*; `scene` prompta hiç girmiyor ama karenin bir alanı ve
düzeltilebiliyor. İkisi ayrı sabit kalıyor çünkü ayrı sorular — `write_frame_prompt` alt modelin
cevabını `_FRAME_FIELDS`'e göre süzüyor, ve oraya `scene` girmemeli.

## `_update_frame(file_store, project_id, args)`

Sırayla:

1. `_opened`.
2. **Tanınmayan alan kontrolü, en başta.** `set(args) - {"file", "frame"} - set(_UPDATABLE)` boş
   değilse ret, ve cümle yabancıları sayar. Dosyayı okumadan önce yapılamaz çünkü ret cevabı dosya
   adını taşıyor; ama **her şeyden önce** yapılıyor, yani geçersiz bir çağrı kareyi hiç görmüyor.
3. `_a_number` ve aralık — `remove_frame`'in ikisi de. **Ortak kod:** `_the_frame(structure, args)`
   numarayı çözer ve kareyi ya da reti verir; iki araç da onu çağırır, yani `frames[-1]`'e karşı tek
   bir savunma var, iki tane değil.
4. **Boş kare reddi.** `action` boşsa `write_frame_prompt`'a yönlendirilir. Ölçü
   `_write_frame_prompt`'un kendi ölçüsüyle **aynı**: o araç `action`'ı boş olan kareleri topluyor,
   bu araç tam olarak onları reddediyor. İkisi bir sabitten okumalı, yoksa aynı karenin iki araca
   göre iki hâli olur.
5. **Verilen alan yoksa ret.**
6. **`characters` verildiyse `_unknown_names`** — 152'nin cümlesi, kare hiç değişmeden.
7. Alanları yaz, dosyayı yaz.

**Cevap hangi alanların değiştiğini sayar:** `Updated frame 3 of scene.json: camera, action.` Model
bir sonraki adımda ne yaptığını buradan okuyor.

**`_renumber` çağrılmıyor:** liste kısalmıyor ya da uzamıyor, ve damga zaten yerinde. Çağırmak da
zararsız olurdu ama yapmadığı bir işi yapıyormuş gibi görünürdü.

## `_the_frame` — ortak numara çözücü

```python
def _the_frame(structure, args):
    """The frame a call names, or the answer saying why there is none."""
```

`remove_frame` bugün bunu kendi içinde yapıyor; bu madde onu dışarı alıyor ve ikisi de çağırıyor.
Kazancı tek: `1 <= number <= len(frames)` tek bir yerde duruyor, ve negatif numaranın sessizce son
kareye ulaşması iki ayrı yerde değil bir yerde engelleniyor.

Numarayı da döndürür — ret cümleleri ve `remove_frame`'in silme indeksi onu istiyor.

## Araç tanımı

`remove_frame`'in ardına. Açıklama üç şey söyler: **verilmeyen alan durur**, **boş kare
`write_frame_prompt`'un**, ve **`scene` de buradan düzeltilir**. `frame` `"type": "integer"`,
gerisi isteğe bağlı; `required` yalnız `file` ve `frame`.

`characters` şeması `write_frame_prompt`'un alt modelinden beklenen şekille aynı: ad → kıyafet
listesi.

## `modes.py`

`update_frame` `EDIT`'in listesine girer. Var olan işin üstüne yazıyor — listenin geri kalanının
kapıya olan hakkının aynısı.

## Bu turda dokunulmayanlar

- **`skills.py`.** Metinler bir şikâyeti `set_`'lere yolluyor, ve bir karenin kendi alanını
  düzeltmek aracın adının söylediği şey. Cümle ancak bir cümle silinerek girer *(Madde 123)*.
- **`schema.py`.** 159'un işi.
- **Sıra değiştirme.** Kapsam dışı.

## Nasıl yeşil olacak

19 kırmızının hepsi aracın var olmasıyla kapanır. Notebook'un iki kırmızısı yerinde kalır.
