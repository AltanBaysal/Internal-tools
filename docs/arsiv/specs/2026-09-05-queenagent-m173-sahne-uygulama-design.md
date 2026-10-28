# Madde 173 · uygulama turu — `add_scene` geliyor, `add_frames` gidiyor

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m173-sahne-testler-design.md).
Commit `a4b50fa` 30 vak'ayı çiviledi. Dilim 2'nin ilk maddesi.

---

## Gelen

**`_add_scene`** — `_opened`'ı çağırıyor *(dosya, JSON, `frames` listesi: üç ret oradan geliyor)*,
sonra sahneleri tek tek kareye çeviriyor.

**`_frame_from(scene, number, structure, problems)`** — bir sahneyi bir kareye çeviriyor ve
bulduğu her sorunu `problems`'a bırakıyor. Cevap **`None` değil**: sorun bulunsa bile kare kuruluyor,
çünkü bir sahnenin sorunu sonrakini incelemekten alıkoymamalı. Yalnız nesne olmayan sahne `None`
dönüyor — içine bakılamayan bir şeyde ad aranmaz.

**`_made_frames(born)`** — *frame 3* ya da *frames 3-5*. Cevabın numaraları buradan.

**`_looked_for(name, known, which, number, problems)`** — `_unknown`'ın cümlesinin başına kare
numarasını koyuyor. Üç harita, `build_prompts` ve şimdi bu araç: bir ad ıskası uygulamanın her
yerinde aynı okunuyor.

## Şekil önce, ad sonra

`characters` içindeki değerler **adlar okunmadan önce** topluca sınanıyor:

```python
if not isinstance(people, dict) or not all(
    isinstance(worn, (str, list)) for worn in people.values()
):
```

Tek koşul, tek cümle. Değeri tek tek sınamak, iki bozuk değeri olan bir kareye aynı cümleyi iki kere
yazdırırdı — ve model aynı şeyi iki kere okuduğunda ikinci bir sorun arar.

`location` da yalnız string: bir liste `in` ile bir haritada aranınca `TypeError` olurdu, ve bu
araçtaki hiçbir yol çökmemeli.

## Numara ve kanonik şekil

`number = len(frames) + offset + 1` — listedeki yeri. Verilmeyen alan **yazılmıyor**: boş bir
`location` anahtarı, birinin onu seçtiğini söyler.

Kıyafet listesi kanonik hâlde diske iniyor: `"gecelik"` → `["gecelik"]`. `cast_of` iki şekli de
okuyor çünkü ikisi de zaten diskte; yazarken bu mazeret yok.

**`action` yazılmıyor, ve fazla alanlar sessizce düşüyor.** Araç yalnız bildiği üç alanı kareye
koyuyor. İmzada `action` olmadığı için modelin onu yazması beklenmiyor; 176 alanı `write_frame_prompt`
ile dolduruyor ve açıklamaya o cümleyi o zaman ekliyor — bugün var olmayan bir aracın adını
açıklamaya yazmak, modele çağıramayacağı bir yol göstermek olurdu.

## Giden

`add_frames`: `TOOL_SPECS`, `run_tool`, `_add_frames`, `modes.py`, ve `skills.py`'nin tek adı.
`_opened`'ın *"as in _build and _add_frames"* diyen yorumu da düzeliyor — 172'nin kuralı, yorum koda
uyduruluyor.

`MAX_ROUNDS`'un yorumu eski zinciri anlatıyordu *(iskeleti yaz, kareleri partiler hâlinde ekle)*;
zincir artık senaryoyu aç, haritaları doldur, sahneleri ekle, derle.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **745 yeşil**, ilk koşuda, tek kırmızı çıkmadan. 30 kırmızının hepsi döndü; 730'dan buraya
   gelen fark, `add_frames`'in 15 testinin gitmesi ve 30 yenisinin girmesi.
3. Öteki üç takım rakamlarını korudu: **586 · 739 · 591.** `dist` derlenmedi.
