# Madde 158 — `update_frame` · **test turu**

**Tarih:** 3 Eylül 2026 · **Branch:** `feat/v6` · **Kaynak:** [v7 yol haritası, Madde
158](../plans/2026-09-03-v7-roadmap.md)

Bu belge yalnız **testlerin** ne çivileyeceğini anlatır.

## Tek araç, ve 151'in son boşluğu

`update_frame(file, frame, scene?, characters?, location?, action?, camera?)`

Madde 151 `edit_file`'ı yapı dosyasına kapattığında üç iş açıkta kaldı: dosyayı doğurmak *(154)*,
haritaları doldurmak *(154)*, silmek *(157)*, ve **yazılmış bir kareyi düzeltmek**. Sonuncusu bu.

Araç sayısı 17'den **18**'e çıkar.

## Kuralı

1. **Verilen alan değişir, verilmeyen alan durur.** Aracın tamamı bu cümle.
2. **`scene` de bu araçla düzeltilir.** Güncelleme karenin üstünde tek bir eylem, hangi alan olduğu
   fark etmiyor — ayrı bir `update_scene` beşinci bir araç olur ve yeni bir şey öğretmezdi
   *(kullanıcı kararı, 3 Eylül)*.
3. **Boş bir kare reddedilir.** Promptu hiç yazılmamış bir kareye `update` değil `write` gider, ve
   ret cümlesi `write_frame_prompt`'un adını söyler. İkisinin ayrı olmasının sebebi tam olarak bu:
   niyet her çağrıda açık, ve kaza ile üstüne yazma yok.
4. **Hiç alan verilmemişse ret.** Yalnız `file` ve `frame` taşıyan bir çağrı hiçbir şey istemiyor, ve
   sessiz başarı modele bir şey yaptığını düşündürür.
5. **Tanınmayan alan varsa çağrının tamamı ret** *(152'nin kuralı)*. Bilineni yazıp bilinmeyeni yok
   saymak, modele olmayan bir kareyi yazdığını düşündürürdü.
6. **Olmayan karakter ya da kıyafet adı ret, kare hiç değişmeden** — `_unknown_names`, 152'nin
   cümlesiyle.
7. **Numara kuralları `remove_frame`'inkiyle aynı:** tam sayı ya da rakamlı string, aralık dışı ret,
   `frames[-1]` hiç doğmuyor.

**Numarayı değiştiren bir alan yok.** `frame` yalnız hangi karenin düzeltileceğini söyler; sıra
değiştirmek bu maddede yok *(kullanıcı kararı, 3 Eylül: "sıra değiştirmeye gerek yok şimdilik")*.

## Bilerek kabul edilen bir sonuç

`action` boş string ile güncellenirse kare **yazılmamış** hâle döner ve bir daha `update_frame`
kabul etmez. Bu bir tuzak değil, doğru yol: o kare artık `write_frame_prompt`'un havuzunda, ve bir
sonraki çağrı onu yeniden yazar. Ayrı bir kural yazmaya gerek yok.

## Yeni testler — `test_tools.py`

1. Yalnız kamera değişiyor, kalan alanlar yerinde duruyor.
2. Birden fazla alan aynı çağrıda değişiyor.
3. `scene` de değişiyor — ve promptun geri kalanına dokunulmuyor.
4. `characters` değişiyor, ve dosyada haritanın şekli duruyor.
5. Boş kare *(sahne var, `action` yok)* ret, ve cevap `write_frame_prompt` diyor.
6. Hiç alan verilmemiş çağrı ret.
7. Tanınmayan alan ret, ve **kare hiç değişmiyor** — tanınan alanla birlikte gönderilmiş olsa bile.
8. Olmayan karakter adı ret, kare değişmiyor, cevap bilinenleri sayıyor.
9. Olmayan kıyafet adı ret.
10. Kıyafetsiz karakter kabul — boş liste bir hata değil, bugünkü davranış.
11. Aralık dışı numara ret, cevap kaç kare olduğunu söylüyor.
12. `0` ve negatif ret.
13. Rakamlı string kabul.
14. Dosya yok / bozuk JSON — `_opened`'ın cümleleri.
15. `frame` damgası güncellemeden sonra da yerinde ve doğru.
16. Kart çizilmiyor.
17. Roster 18 ada çıkıyor, ve `modes.py`'nin `EDIT` listesinde.

## Değişen var olan testler

- `test_every_tool_is_declared_to_the_model` — bir ad ekleniyor.
- `test_modes.py`'nin `WRITES` listesi.

## Bu turda olmayanlar

- **Sıra değiştirme.** Kapsam dışı.
- **`skills.py`.** Akış metinleri düzeltmeyi zaten anlatıyor *(bir şikâyet `set_`'lere gidiyor)*; bir
  karenin kendi alanını düzeltmek araç adının söylediği şey. Metne cümle ancak bir cümle silinerek
  girer *(Madde 123)*.

## Nasıl kırmızı olacak

Araç yok; `run_tool` *"There is no tool called update_frame."* döndürür. Her test assertion'da
düşer, import hatası yok.
