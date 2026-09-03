# Madde 156 — Kod `people`'ı türetir · **uygulama turu**

**Tarih:** 3 Eylül 2026 · **Branch:** `feat/v6` · **Test turu:**
[m156 sayım testler design](2026-09-03-queenagent-m156-sayim-testler-design.md) ·
**Kırmızı commit:** `test(m156)`

Testler yazıldı ve düştü. Bu belge onları yeşile çeviren kodun ne olduğunu anlatır.

## `build_prompts.py` — sayan iki küçük fonksiyon

### `_kind(entry)`

`_identity`'nin kardeşi ve tam olarak onun kadar küçük: girdi harita şeklindeyse `kind`'ını, düz
metinse hiçbir şeyi verir. Düz metin girdinin türü **yok**, ve bu bir eksiklik değil — Madde 154
öncesi yazılmış her dosya böyle, ve kodun bilmediği şeyi tahmin etmesi sayının kendisinden kötü.

İkisi ayrı fonksiyon çünkü ayrı sorular: biri prompta giren metni, öbürü prompta **hiç girmeyen**
türü veriyor. Tek bir fonksiyonun iki değer döndürmesi, her çağıranın istemediği yarıyı atmasıyla
biterdi.

### `_counted(people, characters)`

Karedeki `(ad, kıyafetler)` çiftlerini alır — yani `_worn`'un zaten ürettiği listeyi, ikinci bir
yürüyüş yok — ve haritadaki girdilerinden türleri sayar.

- Sayım `Counter`. `COUNTED = ("boy", "girl")` **sabit sırayla** dolaşılır: sayının sırası karenin
  sırası değil. Bu sıra booru etiket düzeni, ve şemanın örneği de bunu söylüyordu.
- `COUNTED`'da olmayan bir tür döngüye hiç girmez. Sayaç onu tutar, çıktı onu görmez — yani
  tanınmayan tür ile türsüz girdi **aynı kapıdan** düşer, iki ayrı kontrol yazmadan.
- Tekil/çoğul tek harf: bir tanesi `1girl`, fazlası `2girls`. SDXL'in okuduğu biçim bu.
- Sayacak kimse yoksa boş string. `_tags` boş parçayı zaten atıyor, yani virgül kalmıyor —
  `people` alanı boş bırakıldığında bugün olan şeyin aynısı.

### `build_prompts` içinde iki satır yer değiştirir

Bugün `lead` kuruluyor, sonra `in_frame` hesaplanıyor. Sayım `in_frame`'e dayandığı için sıra
tersine döner: önce kimlerin karede olduğu bulunur, sonra `lead` kurulur.

Sayının kendisi:

```python
frame.get("people") or _counted(in_frame, characters)
```

**Yazılı olan kazanır**, ve `or` bunu tek satırda söylüyor. Boş string ya da eksik alan düşer, sayım
koşar; yazılı bir şey varsa sayım hiç koşmaz. Boşluk taşıyan bir `people` *(`" "`)* yazılı sayılır ve
`_tags` onu siler — bugünkü davranış, ve testi duruyor.

### Yorumlar düzelir

`build_prompts`'ın *"the count is placed, never worked out: the code knows who entered the frame but
not what they are, and no field says so"* cümlesi artık yanlış. **Bir yorum yalnız bugün doğru olanı
söyler** — silinmiyor, doğrusuyla değiştiriliyor.

`build_character_prompts`'ın *"how many people are in a picture is a frame's own field"* cümlesi de
öyle: artık bir alan değil, karenin sorusu. Cevabı değişmiyor — önizlemede kare yok, sayı da yok.

`_identity`'nin *"for the count code works out rather than asks for"* cümlesi 154'te gelecek zaman
yazılmıştı; artık geçmiş.

## `schema.py` — modelin artık yazmadığı alan metinden çıkar

1. **`people` paragrafı siliniyor.** *"people says how many are in the frame…"* diye başlayan blok.
2. **JSON örneğindeki iki `"people"` satırı siliniyor.** Paragraf gidip örnek kalsaydı model
   örnekten kopyalardı — Madde 110'un karışık kalite zinciri tam olarak böyle gerçek dosyalara
   ulaşmıştı. Örnek öğretmen, ve öğrettiği şey doğru olmalı.
3. **Kitapçıktan 6. kural siliniyor**, numarası boş bırakılıyor. 3'ün emsali: numaralar testlerde,
   yorumlarda ve commit mesajlarında anılıyor, ve kaydırmak hepsini başka bir kurala yöneltir.

Kuralın ikinci yarısı — *"karakterin kendi girdisindeki solo etiketi"* — kayıtsız düşüyor, ve bu
bilerek. Model artık girdiyi `set_character` ile yazıyor ve kural karenin `people` alanını işaret
ediyordu; işaret ettiği yer yoksa kural okunamaz. Zararı da küçük: fazladan bir `solo`, sayının
yanında duran bir etiket, ve 159 craft metnini toparlarken oraya girebilir.

## Bu turda değişmeyenler

- **`tools.py`'ye dokunulmuyor.** Sayı dosyada bir alan değil, derleme anında çıkan bir etiket —
  hiçbir araç onu yazmıyor, `write_frame_prompt` de yazmıyor.
- **Göç yok.** Elde duran dosyalardaki yazılı `people` yerinde kalıyor ve okunmaya devam ediyor.
- **`build_character_prompts`'ın çıktısı aynı.** Kare yok, sayı yok.

## Nasıl yeşil olacak

12 kırmızının hepsi `_counted`'ın varlığıyla ve şemanın kısalmasıyla kapanır. Notebook'un iki
kırmızısı yerinde kalır — `BRANCH` hâlâ `feat/v6`, ve o kırmızılık hatırlatmanın kendisi.
