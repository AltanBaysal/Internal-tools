# Madde 132 · Tur 2 (uygulama) — Tasarım

**Testler:** [2026-08-29-queenagent-m132-replace-all-testler-design.md](2026-08-29-queenagent-m132-replace-all-testler-design.md)
**Kırmızı commit:** `949bc51` · **Dal:** `feat/queenagent-m123-skill-rewrite`.

## Ne yazılıyor

Tek dosya, `tools.py`, üç dokunuş.

### 1. `_edit` bayrağı okur

`found > 1` dalı ikiye ayrılıyor: bayrak yoksa bugünkü ret, varsa hepsi. Yazma
`content.replace(old, new)` *(hepsi)* ya da `content.replace(old, new, 1)` *(tek)*.

Sıra önemli: `found == 0` kontrolü **bayraktan önce** kalıyor. Bayrak bir eşleşmeyi çoğaltır,
yokluğu bir eşleşmeye çevirmez — testin bekçisi bu.

### 2. Ret cümlesi çıkışı gösterir

Bugün *"include more of what surrounds it"* diyor, yani tek yolu söylüyor. İkinci yol da girer:
**or pass replace_all to change every one.** Deponun kendi kalıbı — `create_file`'ın reddi de
`edit_file`'ı gösteriyor, ve gerekçesi orada yazılı: *"The sentence is the instruction. Saying only
that one exists would leave the next move to a guess, and a guess is what put the model here."*

### 3. Sayı cevaba ve karta geçer

Birden çok yer değiştiyse metin `Edited plan.md in 3 places.`, `outcome` `Edited 3 places`. Tek
yer değiştiyse ikisi de bugünkü hâlinde — `Edited plan.md.` ve `Edited`. Sebebi: bir tanesi olan
bir şeyin hepsini istemek ayrı bir olay değil, ve `1 place` yazan bir kart onu ayrı gösterirdi.

### 4. Tanım bayrağı taşır

`parameters.properties`'e `replace_all` *(boolean)* giriyor, `required`'a **girmiyor** —
varsayılan ret, ve zorunlu bir bayrak modele her sıradan düzenlemede bir niyet beyan ettirirdi.
Açıklama da bayrağı anıyor: gösterilmeyen bir parametreye zayıf model uzanmıyor *(108 ve 118'in
dersi)*.

## Değişmeyen

`found == 0` ve boş `old` cevapları, 131'in numaralı okuması ve numarasız eşleşmesi, `WRITES_FILES`
*(bir düzenleme dosya doğurmuyor, kart çıkmıyor)*, `target` ve kart mantığı.

## Bilerek yapılmayanlar

Ön yüz — bayrak modelin, kullanıcının değil, dolayısıyla `dist` derlenmiyor. `add_frames` 128'in.
