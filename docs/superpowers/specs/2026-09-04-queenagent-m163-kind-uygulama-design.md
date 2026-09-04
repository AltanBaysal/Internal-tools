# Madde 163 — `kind` kalkar · **uygulama turu**

**Tarih:** 4 Eylül 2026 · **Branch:** `feat/v7` · **Kaynak:** [test turu
spec'i](2026-09-04-queenagent-m163-kind-testler-design.md) · **Yol haritası:** [Madde
163](../plans/2026-09-03-v7-roadmap.md)

Çivilenmiş 11 kırmızıyı yeşile çeviren kod. Testlerin ne dediği önceki belgede; bu belge **nereye
dokunulduğunu ve neyin geride bırakılmadığını** anlatır.

## `build_prompts.py` — sayım çıkar

- **`COUNTED`, `_kind`, `_counted` gider.** Üçü de yalnız sayımın parçasıydı.
- **`from collections import Counter` gider** — `_counted` ölünce onu okuyan kalmıyor. Kullanıcının
  turu verirken söylediği şey: *"bir de turda ölü kodları da kaldır"*.
- **Karenin okuma satırı sadeleşir:**
  `frame.get("people") or _counted(in_frame, characters)` → `frame.get("people", "")`. Yani 156
  öncesinin satırı, ama gerekçesi başka: o gün kod sayamıyordu, bugün saymıyor.
- **`_identity` kalır ve yorumu düzelir.** Harita biçimini okuyan tek yer o, ve 154–163 arasında
  yazılmış her dosya o biçimde. Yorumu bugün *"kind is what the count is worked out from"* diyor;
  artık okunmayan bir alan olduğunu söyleyecek. `_worn`, `_block`, `_looked_up`, `_tags` hiç
  değişmez.

## `tools.py` — alan, kural ve ayrıcalık çıkar

- **`KINDS` gider.** Tek okuyucusu şemadaki `enum` ile `_set_entry`'nin doğrulaması, ikisi de
  gidiyor.
- **`set_character`'ın `kind` parametresi gider.** Açıklamasından da *"and what kind of person they
  are"* ile *"a new one needs both a kind and tags"* çıkar.
- **`tags`'in açıklaması ters döner.** Bugün *"no count"* diyor; artık sayıyı **isteyecek**, ve
  örnekle: `1girl, woman in her mid 20s, long teal hair, green eyes`. Sayının sisteme girdiği tek
  kapı burası, ve modele bir kural olarak değil **yazacağı metnin ilk etiketi** olarak öğretiliyor.
- **`SDXL_PROMPT_RULES`'un cümlesi yön değiştirir**, silinmez:
  *"No quality tags and no count of people; code writes both"* →
  *"No quality tags: code writes those… A count of people belongs in a character's own tags and
  nowhere else."* Sebebi test turunun 10. maddesinde: bu metni kare yazıcısı da okuyor ve onun
  yazacağı karakter girdisi yok.
- **`_set_entry`'nin karakter ayrıcalığı biter.** `kind` yerel değişkeni, `KINDS` doğrulaması ve
  *"a kind and tags"* / *"tags"* ayrımı gider; üç araç da aynı cümleyle reddeder: *"A new … needs
  tags."*
- **`_changed` tamamen gider.** `kind` yokken üç girdi türü için de tek satıra iniyordu — `tags`
  verildiyse yaz, verilmediyse dokunma — ve o satır çağıran yerde zaten okunaklı:
  `if tags is not None: entries[key] = tags`. Yeni bir ad `tags` olmadan zaten reddedildiği için
  ikinci bir dal gerekmiyor.

## Bilerek yapılmayanlar

- **Göç yok.** Diskteki `kind` alanları silinmiyor. Onları silen bir adım, dokunulmamış bir dosyayı
  açıp yeniden yazmak demek olurdu; FOUNDATION 1'in kuralı bunun tersi.
- **`kind` argümanı reddedilmiyor.** `run_tool` hiçbir yerde tanımadığı argümanı denetlemiyor, ve bu
  madde o kuralı değiştirmiyor: eski şemayla gelen bir `kind` sessizce düşer.
- **`frame["people"]` yerinde.** Okunmaya devam ediyor; yazanı ve türeteni yok.
- **Ön yüz açılmıyor,** dolayısıyla `dist` yeniden derlenmiyor.

## Doğrulama

1. `python -m pytest queen-agent -q` → **783 yeşil + defterin 2 kırmızısı.** *(Kırmızı turda 772
   yeşil + 11 kırmızı + 2; toplam sabit kalmalı — bu tur test eklemiyor, silmiyor.)*
2. Dört sabit test satırı, sırayla, birebir.
3. `Grep` ile `KINDS`, `COUNTED`, `_counted`, `_kind`, `_changed`, `Counter`: `queen-agent/` altında
   sıfır. `kind` kelimesi yalnız eski dosyayı okuyan yorumlarda ve fikstürlerde kalır.
4. **İki commit** *(kırmızı zaten atıldı; bu tur tek yeşil commit)*, mesajda çift tırnak yok.
