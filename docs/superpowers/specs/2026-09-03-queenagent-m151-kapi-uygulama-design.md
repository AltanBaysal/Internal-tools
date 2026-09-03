# Madde 151 — Uygulama turu tasarımı: kapı kapanır

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** uygulama *(yeşile götürür)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 151 ·
[test turu tasarımı](2026-09-03-queenagent-m151-kapi-testler-design.md)

---

## Kırmızıda duran yedi test

Beşi `create_file`'ı, ikisi `edit_file`'ı bekliyor. Üç test de yeşilde duruyor ve orada kalmalı:
okuma, tamir, ve `add_frames`.

---

## Bir soru, bir cevap: "bu bir yapı dosyası mı"

Tek bir yerde cevaplanıyor, çünkü iki araç aynı soruyu soruyor ve iki kopya ilk değişiklikte
ayrışır.

```python
def is_structure(name):
    return name.lower().endswith(".json")
```

`safe_name`'den **sonra** çağrılıyor. Model `notes/scene.JSON` yazarsa `safe_name` onu
`scene.JSON`'a indiriyor; soru temizlenmiş ada soruluyor, yoksa kapı yolun şekline bakmış olurdu.

## Ret cümlesi

Tek bir yerde yazılıyor, ikisi de oradan alıyor:

> `scene.json is a structure file; it is not written or changed as text.`

Adı taşıyor — model hangi dosyayı denediğini görüyor. Ne yapması gerektiğini **söylemiyor**, çünkü o
araçlar henüz yok; 154 ve 155 geldiğinde cümleye adları eklenecek.

`outcome` = `Refused`. `target` = dosyanın adı: çağrı o dosya hakkındaydı, ve kart hangisi olduğunu
söylüyor. `created` = None: hiçbir şey doğmadı, kart çizilmiyor.

## `create_file` — ret en başta

Bugünkü sıra: adı temizle → ad dolu mu → yaz.

Yeni sıra: adı temizle → **yapı dosyası mı** → ad dolu mu → yaz.

Ret, ad kontrolünden önce. Sonra olsaydı dolu bir ad *"already there"* cevabı alırdı ve model bunu
*"demek ki boş bir adla yazabilirim"* diye okurdu — kapının varlığını dosyanın varlığından çıkarmak.

## `edit_file` — ret, okumadan **sonra**, parse denemesinden sonra

Bugünkü sıra: adı temizle → oku → yoksa cevapla → `old` boş mu → eşleşme say → yaz.

Araya tek bir adım giriyor, ve yeri önemli:

1. **Oku.** Dosya yoksa bugünkü yokluk cümlesi — olmayan bir dosya için ret cümlesi yanlış olurdu.
2. **Yapı dosyası mı, ve içeriği JSON olarak okunuyor mu.** İkisi birden doğruysa **ret**.
3. Değilse bugünkü akış aynen sürüyor.

İkinci adımın iki yarısı da gerekli. Yalnız uzantıya bakılsaydı bozuk dosya da reddedilirdi ve model
onu tamir edemezdi; yalnız içeriğe bakılsaydı `.md` içinde duran geçerli bir JSON de kapanırdı.

**Parse denemesi burada bir kontrol, veri kaynağı değil** — sonucu atılıyor, yalnız başarıp
başarmadığına bakılıyor. Dosyayı okumanın maliyeti zaten ödenmiş durumda, çünkü `_edit` onu bir
satır önce okuyor.

## Dokunulmayanlar

- `read_file` — tek satır değişmiyor.
- `add_frames`, `build_prompts`, `build_character_prompts`, `write_plan` — hiçbiri bu iki araçtan
  geçmiyor, doğrudan depoya yazıyorlar.
- `modes.py` — hangi aracın izin istediği değişmiyor. Kapı *"ne yapabilir"* sorusunun cevabı, *"ne
  zaman sorar"* sorusunun değil.
- Araç açıklamaları. `create_file`'ın metni bugün *"bir belgeyi projeye kaydet… .json bir yapı
  dosyası için"* diyor — bu **değişiyor**, çünkü artık yalan. Uzantı listesinden `.json` çıkıyor.

## Kabul edilen ara hâl

Bu madde koştuktan sonra yapı dosyası **hiç oluşturulamıyor**: `create_file` kapalı,
`create_structure` henüz yok. Kullanıcı kararı *(3 Eylül: "sıkıntı yok, test ederiz işte yazabiliyor
mu diye")*, ve duraktaki denemenin sorusu tam olarak bu.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```

Yedi kırmızı yeşile döner, 698 olur. Üç yeşil testin hâlâ yeşil olması kapının fazla kapanmadığının
kanıtı.
