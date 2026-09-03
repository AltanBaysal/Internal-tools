# Madde 157 — Silme araçları · **test turu**

**Tarih:** 3 Eylül 2026 · **Branch:** `feat/v6` · **Kaynak:** [v7 yol haritası, Madde
157](../plans/2026-09-03-v7-roadmap.md)

Bu belge yalnız **testlerin** ne çivileyeceğini anlatır.

## Dört araç

`remove_character(file, name)` · `remove_outfit(file, name)` · `remove_location(file, name)` ·
`remove_frame(file, frame)`

Dördü ayrı, çünkü `set_`'ler zaten kaynak kaynak bölünmüş. Tek bir `remove_entry(map, …)` olsaydı
model hangi aracın `map` aldığını ayrıca hatırlardı — tahmin edilebilir adlandırma, karışık olandan
kolay *(kullanıcı kararı, 3 Eylül)*.

Araç sayısı 13'ten **17**'ye çıkar.

## Üç harita aracının kuralı

**Sıra önemli, ve testler sırayı da çiviler:**

1. **Dosya yoksa / bozuksa / `frames` listesi yoksa** — `_opened`'ın verdiği cevaplar. Silme
   kullanımı sayabilmek için kareleri okumak zorunda, yani liste bu araçların gerçek bir şartı.
2. **Olmayan ad ret.** Sessiz başarı, olmayan bir şeyi sildiğini sanan bir model demek. Cümle
   `build_prompts`'ın sözlüğüyle aynı: `ghost is not in outfits; known: gunluk, ceket.`
3. **Hâlâ kullanılan ad ret, ve cevap kareleri sayar.** `gunluk is still worn in frames 3, 7.` Bugün
   bu kitapçığın 5. kuralıydı; artık kodun cevabı.
4. Geriye kalan: siler, yazar, ne olduğunu söyler.

**Fiil kaynağa göre değişir** — karakter *karede*, kıyafet *giyilir*, mekân *oranın kendisidir*.
Üç ayrı cümle değil, tek cümlenin içinde tek bir değişen parça.

**Numaralar listedeki sıradan gelir, damgadan değil.** Madde 153 ikisini eşit tutuyor ve gerçek olan
sıra; elle bozulmuş bir damga kullanıcıya olmayan bir kareyi gösterirdi.

**Silme `set_` üstünden yapılmıyor** — boş değerin *"sil"* demesi, alanı dolduramamış bir modelin
dosyayı sessizce silmesi demek olurdu.

## `remove_frame`'in kuralı

- **Numarayla siler.** `frame` bir tam sayı.
- **Aralık dışı ret**, ve cümle kaç kare olduğunu söyler: `bar-scene.json has 4 frames; there is no
  frame 9.` Boş dosyada `has no frames`.
- **Sayı olmayan ret.** Rakamlardan oluşan bir string *(`"3"`)* kabul edilir — model bunu sıkça
  yapar ve iki okuma yok. Başka her şey reddedilir.
- **Silindikten sonra kalanlar yeniden numaralanır** *(Madde 153)*, boşluk kalmaz.
- **Cevap yeni numaraları söyler.** Model bir sonraki adımda kareyi numarasıyla anacak, ve
  numaraların kaydığını okuduğu tek yer bu cümle.
- **Dolu kare de silinir.** Promptu yazılmış olması bir engel değil; niyet açık.

## Yeni testler — `test_tools.py`

**Harita araçları** *(üçünde de koşan, parametrize edilebilir olanlar)*:

1. Kullanılmayan bir kıyafet siliniyor — dosyadan gidiyor, cevap sildiğini söylüyor.
2. Kullanılmayan bir karakter siliniyor.
3. Kullanılmayan bir mekân siliniyor.
4. Olmayan ad ret — dosya değişmiyor, cevap bilinen adları sayıyor.
5. Kullanılan kıyafet ret — cevapta `3` ve `worn` geçiyor, kıyafet dosyada duruyor.
6. Kullanılan karakter ret — cevapta kare numarası geçiyor.
7. Kullanılan mekân ret.
8. Birden fazla karede kullanılan bir ad, cevapta **bütün** numaraları sayıyor: `frames 1, 3`.
9. Dosya yok — `_opened`'ın cümlesi.
10. Bozuk JSON — `_opened`'ın cümlesi.
11. Silme yalnız kendi haritasına bakar: `remove_outfit` aynı adı taşıyan bir **karakteri**
    silmiyor. *(Adların haritalar arasında çakışması serbest.)*

**`remove_frame`**:

12. Ortadaki kare siliniyor ve kalanlar 1, 2 diye yeniden numaralanıyor.
13. Silinen karenin içeriği gidiyor — kalan iki karenin sahneleri doğru olanlar.
14. Aralık dışı numara ret, cevap kaç kare olduğunu söylüyor, dosya değişmiyor.
15. `0` ve negatif ret. *(Python'da `frames[-1]` çalışır ve sessizce sondakini silerdi — bu testin
    var olma sebebi tam olarak o.)*
16. Rakamlı string kabul.
17. Sayı olmayan *(`"iki"`, `None`)* ret.
18. Son kare silinince dosyada kare kalmıyor ve cevap bunu söylüyor.
19. Promptu yazılmış bir kare de siliniyor.

**Kayıt ve kart**:

20. Dördü de `TOOL_SPECS`'te — roster testi 17 ada çıkar.
21. Dördü de `modes.py`'nin `EDIT` listesinde, ve `ask`/`plan` modlarında soruyor.
22. Hiçbiri `WRITES_FILES`'ta değil — silme dosya doğurmaz, kart çizilmez.

## Değişen var olan testler

- `test_every_tool_is_declared_to_the_model` — dört ad ekleniyor.
- `modes.py`'nin araç listesini sayan testler varsa onlar.

## Bu turda olmayanlar

- **Yeniden adlandırma.** Henüz bir maddesi yok.
- **Zorla silme.** `force` diye bir parametre yok: kullanılan bir adı silmek isteyen önce kareleri
  düzeltir, ve o iş `update_frame`'in *(158)*.
- **Kareyi silerken haritayı temizlemek.** Kimsenin anmadığı bir ad kitapçığın 5. kuralında zaten
  *"bir not, ihlal değil"*.

## Nasıl kırmızı olacak

Araçlar yok. `run_tool` bilinmeyen ad için *"There is no tool called …"* döndürüyor, yani her test
assertion'da düşer — import hatası yok, ve suite'in geri kalanı görülebilir kalır.
