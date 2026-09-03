# Madde 161 — `set_` yeniden adlandırır · **test turu**

**Tarih:** 4 Eylül 2026 · **Branch:** `feat/v7` · **Kaynak:** [v7 yol haritası, Madde
161](../plans/2026-09-03-v7-roadmap.md)

Bu belge yalnız **testlerin** ne çivileyeceğini anlatır.

## İmzalar

```
set_character(file, name, kind?, tags?, new_name?)
set_outfit(file, name, tags?, new_name?)
set_location(file, name, tags?, new_name?)
```

`required` üçünde de yalnız `file` ve `name`. Gerisi isteğe bağlı, ve neyin ne zaman gerektiği
kural: **yeni bir ad** `kind` *(karakterde)* ve `tags` ister; **var olan bir ad** verileni değiştirir.

## Kural, sırayla

1. Dosya yok / bozuk / `frames` yok — `_opened`'ın cevapları. Yeniden adlandırma kareleri yazmak
   zorunda, yani liste gerçek bir şart; `set_` bugüne kadar kendi önsözünü taşıyordu, artık aynı
   kapıdan giriyor.
2. Boş `name` ret.
3. **Ad haritada yoksa:** `new_name` verilmişse ret *(yeniden adlandıracak bir şey yok, girdi de
   doğmaz)*. `kind` *(karakterde)* ya da `tags` eksikse ret. Yoksa ekle — bugünkü davranış.
4. **Ad haritada varsa:** `new_name`, `kind`, `tags`'ten hiçbiri verilmemişse ret — *"nothing was
   given to change"*. Kullanıcının OR kuralı.
5. `new_name` verildiyse: boşsa ret; eskisiyle aynıysa ret; haritada doluysa ret. Değilse anahtar
   **olduğu yerde** değişir ve kareler takip eder.
6. `kind` verildiyse `KINDS`'ta olmalı, yoksa ret. `tags` verildiyse yazılır.
7. Yaz; cevap ne olduğunu söyler.

**Takip eden kareler, kaynağa göre:**

| Harita | Karede nerede | Nasıl değişir |
| --- | --- | --- |
| `characters` | `characters` haritasının anahtarı | Harita yeniden kurulur, anahtar **aynı sırada** |
| `characters` | eski liste biçimi `["aylin", …]` | Eleman değişir |
| `outfits` | `characters` değerlerindeki listeler | Eleman **aynı konumda** değişir |
| `outfits` | tek string değer `"aylin": "gecelik"` | String değişir |
| `locations` | `location` alanı | String değişir |

**Sıra neden önemli:** `build_prompts` haritada ilk yazılanı lider yapıyor. Anahtarı silip yeniden
ekleyen bir kod onu sona atar ve lider sessizce değişir. Testin biri tam olarak **ikinci sıradaki**
karakteri yeniden adlandırır ve ikinci sırada kaldığını okur.

**Eski dosya:** düz metin karakter girdisi + yalnız `tags` → düz metin kalır, boş `kind` yazılmaz.
Düz metin + `kind` → harita biçimi, `tags` verilmediyse eski metin taşınır.

## Cevaplar

- Eklendi: `Added lara to characters.` — bugünkü.
- Değişti: `Changed aylin in characters; 2 frames name it.` — bugünkü, hangi alan olursa olsun.
- Yeniden adlandırıldı: `Renamed aylin to ayla in characters; 2 frames followed.` Başka alan da
  değiştiyse `… and changed tags; …`. Outcome `Renamed`.

## Yeni testler — `test_tools.py`

Fikstür 157'nin `CROWDED`'ı: `aylin`/`gecelik`/`bedroom` 1. ve 3. karede; `lara`/`palto`/`rooftop`
boşta. İki karakterli kare ve iki kıyafetli liste testin içinde kurulur.

**Yeniden adlandırma**

1. Karakter: anahtar taşınır, her kare takip eder, eski ad hiçbir yerde kalmaz.
2. **İkinci sıradaki** karakter yeniden adlandırılınca ikinci sırada kalır.
3. Kıyafet: listelerdeki ad **aynı konumda** değişir.
4. Mekân: `location` takip eder.
5. Cevap kaç karenin takip ettiğini söyler.
6. Yeni ad doluysa ret, dosya değişmez — üçünde de.
7. Eski ad yoksa ret, **yeni girdi doğmaz** — `new_name` ile birlikte `kind`/`tags` gelse bile.
8. Boş `new_name` ret.
9. Eskisiyle aynı `new_name` ret.
10. Yeniden adlandırma ve `tags` aynı çağrıda — ikisi de iner.
11. Hiçbir karenin anmadığı ad da yeniden adlandırılır; cevap 0 der.
12. Eski liste biçimindeki kare takip eder.
13. Tek string kıyafet değeri takip eder.

**Kısmi güncelleme**

14. Yalnız `tags` → `kind` yerinde kalır.
15. Yalnız `kind` → `tags` yerinde kalır.
16. Var olan ad, hiçbir alan yok → ret, dosya değişmez — üçünde de.
17. Yeni karakter `kind`'sız ya da `tags`'sız → ret, doğmaz.
18. Yeni kıyafet / mekân `tags`'sız → ret, doğmaz.
19. Düz metin karakter + yalnız `tags` → düz metin kalır.
20. Düz metin karakter + `kind` → harita biçimi, eski metin `tags` olur.

**Şema**

21. Üçünde de `required == ["file", "name"]`.
22. Üçü de `new_name` sunar.

## Değişen var olan testler

Hiçbiri. Bugünkü çağrıların hepsi `kind`/`tags` veriyor ve aynı davranışı bekliyor.

## Nasıl kırmızı olacak

`new_name` bugün yok sayılıyor: yeniden adlandırma testleri anahtarı eski yerinde bulur. Kısmi
güncelleme testleri bugünkü *"kind is girl or boy; nothing is neither"* retiyle düşer. Şema testleri
`required`'ı dört elemanlı bulur. Import hatası yok.
