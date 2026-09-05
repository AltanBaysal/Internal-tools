# Madde 176 · uygulama turu — `write_frame_prompt`

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m176-action-testler-design.md).
Commit `f2a030e` 21 kırmızı bıraktı.

---

## `WRITE_FRAME_SYSTEM_PROMPT`

İki parça, `+` ile birleşiyor: kendi metni, sonra `SDXL_PROMPT_RULES`. Kendi metni üç şey söylüyor:

1. **Kim olduğu** — tek bir karenin action'ını yazan biri. Ajan değil; araç yok, dosya yok, sohbet
   yok.
2. **Ne yazacağı** — olan şey ve çekim, tek bir etiket dizisi olarak. Kamera ayrı bir alan değil
   *(166'dan beri yok)*, dolayısıyla çekimin cümlenin içinde olduğu **söylenmek zorunda.**
3. **Ne yazmayacağı** — kadronun görünüşünü, kıyafetleri, mekânı. Onlar zaten haritalardan geliyor
   ve `build_prompts` onları kendi koyuyor; burada tekrar edilirse prompt aynı şeyi iki kere söyler.

## `_write_frame_prompt`

Sıra önemli: **motor → dosya → kare → sahne → istek.** Her ret bir öncekinden ucuz, ve hiçbiri
para harcamadan önce.

```
There is no model to write with.        (motor yok — sarma hatası, dosya bile açılmıyor)
_opened'ın üçü                          (dosya yok / JSON bozuk / frames yok)
_numbered'ın ikisi                      (numara değil / olmayan kare)
Frame 3 has no scene to write from.     (sahnesiz kare)
```

`_frame_seen(frame, structure)` giden mesajı kuruyor: sahne, kadro *(ad: etiket, altında `wearing`
satırları)*, mekân *(ad: etiket)*, ve varsa not. Haritadan **yalnız o karenin andığı adlar**
okunuyor; bilinmeyen ad varsa etiketi boş geçiliyor — burada reddedilmiyor, çünkü kareyi yazan
`add_scene` zaten reddetmişti ve elle bozulmuş bir dosyanın cezasını bu araç kesmiyor.

İstek `try` içinde: her istisna `The prompt model did not answer: {…}` oluyor. Servisin kendi
sözleri, uydurma sebep yok.

Boş cevap ayrı cümle: `The prompt model answered with nothing; frame 3 is unchanged.` Yazılmıyor.

Başarı: `frames[n]["action"] = text.strip()`, kaydet, `ToolResult("Wrote frame 3 of scene.json.",
None, source, "Written", spent)`.

## `stream_answer`

İki satır: `run_tool(..., engine=engine)`, ve sonucun harcaması toplama ekleniyor.

```python
if result.spent:
    spent = Usage(
        spent.sent + result.spent.get("sent", 0),
        spent.cached + result.spent.get("cached", 0),
        spent.answered + result.spent.get("answered", 0),
        spent.context,          # dokunulmuyor
    )
```

`context` olduğu gibi kalıyor. O sayı **son isteğin büyüklüğü** — sohbetin ne zaman dolduğunu
söyleyen tek şey — ve aracın isteği konuşma değil.

## İki komşu açıklamaya eklenen cümle

`add_scene` ve `update_frame` artık `write_frame_prompt`'u adıyla anıyor. 173 ve 174 susmuştu çünkü
araç yoktu; m127'nin dersi *(olmayan aracı anlatan açıklama bir turu yakar)* iki yönlü: var olanı
gizlemek de modele bir yol kapatır.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **800 yeşil**, ilk koşuda, tek kırmızı çıkmadan. 21'in hepsi döndü.
3. Öteki üç takım rakamlarını korudu: **586 · 739 · 591.** `dist` derlenmedi.

## Dilim 2 kapandı

173–176, dört madde, sekiz tur. Kare artık **doğuyor** *(`add_scene`)*, **değişiyor ve siliniyor**
*(`update_frame`, `remove_frame`)*, ve **cümlesini kendi modelinden alıyor** *(`write_frame_prompt`)*.
Araç sayısı 20.

**Deneme 2'nin sorusu** yol haritasında: bir kareyi yazdır, sonra bir notla düzelttir — Grok'un
cümlesi ana ajanınkinden iyi mi, ve not gerçekten değiştiriyor mu. Skill seçmeden koşuluyor;
metinler 178'e kadar hâlâ eski takımı anlatıyor.
