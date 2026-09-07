# Madde 174 · test turu — kare değiştirilir ve silinir

**Kaynağı:** [yol haritası](../plans/2026-09-05-queenagent-v7-roadmap.md), Madde 174. 173 kareyi
doğurdu; bu madde onu değiştirmenin ve silmenin yolunu açıyor. Üçlü tamamlanıyor — haritaların
`add`/`update`/`remove`'u karede de aynı.

Bu tur **yalnız testleri** yazıyor ve kırmızı commit'liyor.

---

## Neden gerekiyor

171 `.json`'ı metin olarak kapattı, 173 `add_frames`'i emekliye ayırdı. Aradaki boşluk şu: **var
olan bir kareyi değiştirmenin hiçbir yolu yok.** `edit_file` reddediyor, `add_scene` yalnız sona
ekliyor. Model üçüncü karenin mekânını düzeltmek istediğinde elinde tek şey var — senaryoyu baştan
kurmak.

## `update_frame(file, frame, scene?, characters?, location?)`

Kareyi **numarasıyla** buluyor, ve **yalnız verileni** değiştiriyor.

- **`action`'a dokunmuyor.** O 176'nın alanı, ve onu düzeltmenin yolu yeniden yazdırmak — bir not
  ile `write_frame_prompt`. Buradan elle yazılabilseydi, kalite kapısı olan modelin yanından
  dolaşılabilirdi.
- **`number`'a da dokunmuyor.** Numara karenin yeri; yeri değiştiren tek şey silme.
- Adlar 173'ün süzgecinden geçiyor: haritalarda olmayan ad reddediliyor, cümlesi aynı cümle.
- **Boş değer alanı siliyor:** `location: ""` mekânsız bir kare demek, `characters: {}` kimsesiz.
  173'te verilmeyen alan hiç yazılmıyor; burada da temizlenen alan kalmıyor — bir kare iki farklı
  yoldan aynı şekle varmalı.
- **Boş `scene` reddediliyor.** Doğumda zorunlu olan, sonradan boşaltılabilir olamaz.
- Hiçbir şey verilmezse: *Nothing was given to change about frame 3.* — `_update_entry`'nin cümlesi,
  sessiz başarı yok.

**Cevap ne değiştiğini sayıyor:** *Changed scene and location of frame 3 in bar-scene.json.*

## `remove_frame(file, frame)`

Kareyi siliyor ve **kalanları 1'den yeniden numaralandırıyor.** Numara karenin yeriyse, silmeden
sonra yerinde durmayan bir numara yalandır — ve `build_prompts` kareleri zaten yerlerine göre
sayıyor, yani dosyadaki numara ile derlemedeki numara ayrılırdı.

*Removed frame 3 from bar-scene.json; 5 frames left, renumbered from 1.*
Sonuncusu gidince: *Removed frame 1 from bar-scene.json; no frames left.* — yeniden numaralanacak
bir şey yokken numaralamadan söz etmiyor.

Yeniden numaralama **eski dosyaları da onarıyor:** 173'ten önce yazılmış karelerin `number`'ı yok,
ve bir silmeden sonra hepsi kazanıyor.

## Kare numarası

`frame` bir tamsayı, 1'den sayılıyor.

| Ne | Cümle |
|---|---|
| olmayan kare | `bar-scene.json has 5 frames; there is no frame 9.` |
| numara değil, ya da sıfır/eksi | `A frame is named by its number, counting from 1.` |

**`"3"` bağışlanıyor** — rakamdan ibaret bir string tamsayı okunuyor. 173'ün listesiz kıyafeti gibi:
küçük bir kayma, bir raunda mal olmadan düzeltiliyor. `True` bağışlanmıyor; Python'da `bool` bir
`int`'tir ve `frame=True` kareyi 1 yapardı.

## Silme kimsenin kararı değil

`remove_frame` yalnız kareyi siliyor; haritalardaki hiçbir şeye dokunmuyor. Karesi kalmayan bir
karakter **haritada duruyor** — kullanıcının 5 Eylül kararı: *silme kalksın, agent silmek isterse
kullanıcıya söylesin.* `remove_character` zaten üstünde kare duran bir adı reddediyor, ve silme
sırası kullanıcının.

---

## Çivilenen vak'alar — 27

**Bildirim (2):** araç listesi ikisini de tanıyor; `modes.py` ikisinin de önünde kapıyı tutuyor.

**Değiştirdiği (10):** yalnız sahneyi · yalnız kadroyu · yalnız mekânı · birden fazlasını ·
`action`'a dokunmuyor · `number`'ı korumuyor değil, koruyor · cevap ne değiştiğini adlandırıyor ·
boş mekân alanı siliyor · boş kadro alanı siliyor · listesiz kıyafet burada da düzeliyor.

**Değiştirmeyi reddettiği (8):** hiçbir şey verilmedi · olmayan kare · numara değil · sıfır ·
bilinmeyen ad · kadro harita değil · boş sahne · olmayan dosya.

**Sildiği (6):** kareyi siliyor · kalanları 1'den numaralıyor · cevabı · sonuncusu gidince
numaralamadan söz etmiyor · olmayan kareyi reddediyor · haritalara dokunmuyor.

**Ve bir tane:** `"3"` bağışlanıyor.

## Koşarken çıkan tek şey: yine boşta geçen bir test

`test_update_frame_keeps_the_frames_number` ilk koşuda **yeşildi.** Dosyadaki numaralar zaten
1, 2, 3; hiçbir şey olmayınca da öyle kalıyorlar. Aynı ders üçüncü maddede üst üste: **değişmediğini
ölçen test, önce değişenin değiştiğini iddia etmek zorunda.** Sahneyi sayan bir satır eklendi.

Bu artık bir kalıp — 168, 173, 174 — ve her seferinde aynı biçimde: *"X'e dokunulmadı"* diyen bir
test, dokunulan şeyi de görmek zorunda.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **27 kırmızı**, hepsi `queen-agent`'ta; hiçbiri `skip` ya da `xfail` değil.
3. Kırmızıların hepsi **yokluktan** — `There is no tool called update_frame.` ve `remove_frame`.
   Başka sebeple kırmızı olan bir test yanlış yazılmış demektir.
4. Öteki üç takım rakamlarını korudu: **586 · 739 · 591.** `dist` derlenmedi.
