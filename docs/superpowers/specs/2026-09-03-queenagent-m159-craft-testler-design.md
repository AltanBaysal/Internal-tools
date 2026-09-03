# Madde 159 — Şema aracı uçar, yerine tek bir craft metni gelir · **test turu**

**Tarih:** 3 Eylül 2026 · **Branch:** `feat/v6` · **Kaynak:** [v7 yol haritası, Madde
159](../plans/2026-09-03-v7-roadmap.md)

Bu belge yalnız **testlerin** ne çivileyeceğini anlatır.

## Ne kalkıyor

`read_prompt_structure_schema` siliniyor, ve `schema.py` ile birlikte. Araç sayısı 18'den **17**'ye
iniyor.

**Neden:** şemanın yarısı dosyanın **şeklini** anlatıyordu ve o yarı artık ölü. 151 kapıyı kapattı,
154–158 yerine geçen araçları koydu, ve model dosyayı `read_file` ile zaten görebiliyor. Kalan şey
yazamayacağı bir biçimin JSON örneğiydi.

Ölmeyen yarı **craft**: promptun nasıl yazıldığı. O bir sabite taşınıyor.

## Ne geliyor — `CRAFT`

`tools.py`'de tek bir metin. İçinde:

- Etiket yazılır, cümle değil — kısa virgüllü parçalar, artikel yok.
- Tek donmuş an: hareket, geçmiş, sebep prompta girmez; sebep neye benziyorsa o yazılır.
- `action` yalnız kameranın gördüğünü taşır.
- `camera` iki karar — gövdenin ne kadarı, ve nereden bakıldığı.
- Değerin içinde `or` olmaz.
- Kalite etiketi ve kişi sayısı yazılmaz; ikisini de kod yazıyor.
- Kareyi ilk anılan karakter açar.
- Her şey İngilizce; tek istisna `scene`, kullanıcının dilinde kalır ve prompta hiç girmez.

**Tek metin, bölünmüyor** *(kullanıcı kararı, 3 Eylül)*. `set_character` de kare kurallarını görüyor
— zararı yok, bakımı kolay, ve tek kaynak olduğu için bayatlayamaz.

## Nereye giriyor

Değer yazan **dört** aracın açıklamasına: `set_character`, `set_outfit`, `set_location`,
`update_frame`. Ve alt modelin sistem promptu `WRITING`'in içine — 155'te bilerek ikinci bir kopya
olarak yazılmıştı, burada tek kaynağa dönüyor.

`add_scene` almıyor: sahne cümlesi kullanıcının dilinde ve prompta hiç girmiyor.
`write_frame_prompt` almıyor: hiçbir değer almıyor.

## Ödenen bedel, açıkça

**Araç açıklamaları da her turda gidiyor**, tıpkı sistem promptu gibi. Yani metnin dört kopyası her
isteğe biniyor — kabaca 700–900 jeton. Şema aracı bunu yalnız çağrıldığında ödetiyordu.

Kazanç jeton değil, **dikkatin yeri**: kural, yönettiği parametrenin yanında duruyor ve model onu
tam o aracı seçerken okuyor. Sistem promptunun tepesindeki bir kural uzun bir bağlamda okunmuyor.
Bir de kaybolan bir round var — şemayı çekmek bir tur harcıyordu.

*(Yol haritasının bu maddeyi yazarken verdiği sebep — "sistem promptunda her sohbet taşırdı" — araç
açıklamaları için de doğru. Gerçek sebep dikkatin yeri, ve bu belge onu böyle yazıyor.)*

## Yeni testler — `test_tools.py`

1. `TOOL_SPECS`'te `read_prompt_structure_schema` yok, ve roster 17 ad.
2. `run_tool` o adı çağırınca *"There is no tool called …"* diyor.
3. `CRAFT` dört aracın açıklamasında **birebir** duruyor.
4. `CRAFT` `add_scene` ve `write_frame_prompt`'un açıklamasında **yok**.
5. `WRITING` `CRAFT`'ı içeriyor — ikinci kopya yok.
6. `CRAFT` craft'ın kendisini söylüyor: cümle değil etiket, `or` yok, tek an, kameranın iki kararı,
   ilk karakter lider, İngilizce.
7. `CRAFT` dosyanın **şeklinden** hiç söz etmiyor — JSON örneği yok, `frames` diye bir alan adı yok.
   Ölen yarının geri sızmadığının çivisi bu.
8. `backend.features.workspace.domain.schema` import edilemiyor.

## Yeni testler — `test_modes.py`, `test_context_box.py`

9. `READS` yalnız `read_file`.
10. `context_box`'ta `schema_was_read` yok.

## Değişen var olan testler

- `test_schema.py` **siliniyor**.
- `test_tools.py`'nin şema aracı testleri siliniyor *(dördü)*.
- `test_context_box.py`'nin iki şema testi siliniyor.
- `test_stream_answer.py` şemayı "herhangi bir araç çağrısı" olarak kullanıyor — yirmiye yakın yerde.
  Yerine olmayan bir dosyanın `read_file`'ı geçiyor: bir tur harcıyor ve **kutuyu kirletmiyor**
  *(`files_opened` kaçırılmış okumayı atlıyor)*, yani o testler tur hakkında kalmaya devam ediyor.
  `test_the_schema_reaches_the_box_too` siliniyor.
- `test_chats_api.py`'nin bir testi aynı şekilde.
- `test_skills.py`'nin şema çeken testleri siliniyor; iki metin de artık şema çağırmıyor.

## Bu turda olmayanlar

- **Kitapçığın son kuralı gidiyor ve geri gelmiyor:** *"aynı ad iki yapı dosyasında farklı metin
  taşımasın"*. Dosyalar arası bir kural, hiçbir araç göremiyor, ve kopyalamak zaten serbestti.
- **`read_file` kapanmıyor.** 151'de açık bırakılmıştı ve öyle kalıyor.

## Nasıl kırmızı olacak

Yeni testler `CRAFT`'ı import ediyor — yok, ve `test_tools.py`'nin toplanması **düşmemeli**, o yüzden
import test gövdesinin içinde. Silinen testler zaten yeşilden çıkıyor. Kırmızı: `CRAFT`'ı arayanlar,
roster, ve şema aracının hâlâ var olduğunu söyleyenler.
