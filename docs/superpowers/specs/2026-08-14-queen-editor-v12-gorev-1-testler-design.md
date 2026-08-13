# v12 Görev 1 — Tohumsuz iş üretimi durdurmuyor: TEST döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v12](../plans/2026-08-14-queen-editor-v12-roadmap.md) · **Döngü:** 1/2
**Bu döngüde kod yazılmıyor** — yalnız testler, ve takım kırmızı commit'leniyor.

## Ne kırıldı

Kuyruk bir katman işini planlarken tohum yazmıyor:

```
queue_layer._job()              → {"seed": None, ...}
run_loop                        → producer.generate(prompt, negative, current["seed"], ...)
MMAudioGenerator.generate       → _sound_for(..., seed=None)
MMAudioSampler.render           → rng.manual_seed(None)      ← burada patlıyor
```

`torch.Generator.manual_seed` bir tam sayı ister; `None` alınca *"manual_seed expected a long, but
got NoneType"* der. Üretim aynı kareyi üç kez deniyor ve duruyor. Yani **hiçbir ses işi geçmiyor** —
tek tük değil, hepsi.

Fotoğraf bu duruma hiç düşmüyor: her fotoğraf işi `new_seed()` ile planlanıyor. Video düşüyor ama
kaldırıyor — tohumsuzken grafiğin kendi tohumunu bırakıyor.

## Bugün hangi test bunu yakalamıyor, neden

Üç test dosyası bu yolun üç parçasını ayrı ayrı sınıyor ve **üçü de yeşil**:

| Dosya | Ne sınıyor | Neden yakalamıyor |
|---|---|---|
| `test_photo_usecases.py` | kuyruk katman işini planlıyor | işin tohumuna hiç bakmıyor |
| `test_mmaudio_generator.py` | üretici sahte sampler'ı çağırıyor | her çağrıda elle tohum veriyor (`7`, `1`, `4242`) |
| `test_producer_contract.py` | üç gerçek üretici gerçek döngü altında | planı elle yazıyor ve katman işlerine tohum koyuyor (`2`, `3`) |

Sonuncusu can alıcı: dosyanın kendi başlığı *"iki taraf da yeşilken çağrı konusunda anlaşamayabilir
— gönderilen tam olarak buydu"* diyor. Doğru teşhis, eksik uygulama — çünkü **koştuğu plan kuyruğun
yazdığı plan değil.** Kuyruk `seed: None` yazıyor, test `seed: 2` yazıyor.

İkinci delik sahte sampler'da: `render(...)` tohumla hiç ilgilenmiyor, dolayısıyla `None` da geçiyor.
Sahte, torch'un o tek noktadaki şartını taşımıyor.

## Hangi davranış doğru sayılacak

**Katman işi tohumsuz kalmaya devam ediyor.** Bu bir kaza değil, yazılı bir karar: `regenerate` da
öyle planlıyor ve kendi testi var (`test_a_layer_made_again_is_planned_with_no_seed_of_its_own`).
Bu görev o kararı değiştirmiyor — kullanıcıya sorulmayan bir sayıyı plana yazmak, planı olmadığı bir
şey yapardı.

**Tohumsuz bir işe her üretici kendi doğal cevabını veriyor.** Video'nunki "grafiğin kendi tohumu
kalsın" — bırakacak bir şeyi var. MMAudio'nun yok: `manual_seed` isteğe bağlı değil, ya tam sayı
alır ya patlar. O yüzden **ses üreticisi işin tohumu yokken bir tane seçer.**

**Seçim `MMAudioGenerator`'da, `MMAudioSampler`'da değil.** İki sebep:

1. Sampler bilerek testsiz — kendi başlığı söylüyor: *"sahte bir torch yalnız sahteyi sınardı."*
   Kararı oraya koymak, bu hatanın bir daha yakalanamayacağı yere koymak olurdu.
2. Sampler'ın başlığı zaten kararın nerede olduğunu yazıyor: *"kararlaştırılabilir olan her şey
   `mmaudio_generator`'a çıkarıldı — hangi parça, hangi kelimeler, **hangi tohum**."* Karar orada
   olacak diye yazılmış ama hiç verilmemiş. Bu görev o eksiği kapatıyor.

**Tohum enjekte edilen bir porttan gelir.** `lambda: random.randint(0, 2**31 - 1)` — `main.py`'nin
`start_batch` ve `regenerate` için zaten iki kez yazdığı ifadenin aynısı. Üreticinin içine gömülmüş
bir `random` testi zar atmaya bırakırdı; port, testin tohumu bilmesini sağlıyor.

**İş başına bir tohum, parça başına değil.** Uzun bir video parçalara bölünüyor ama çıkan şey tek
bir ses; her parçaya ayrı tohum vermek sesin karakterini ortasından değiştirirdi.

**İki tohumsuz iş aynı tohumu almaz.** Aksi hâlde aynı videonun iki ses varyantı birbirinin aynısı
olurdu — varyant istemek anlamsızlaşırdı.

**İşin kendi tohumu varsa ona dokunulmaz.** Bugün böyle bir iş yok ama port eklenince üzerine yazma
riski doğuyor; o yüzden kilitleniyor.

## Yazılacak testler

### `test_mmaudio_generator.py` — üreticinin kararı

1. **Tohumsuz iş modele yine de bir tam sayıyla gidiyor.** `generate(..., seed=None)` → sampler'ın
   aldığı tohum `isinstance(..., int)`.
2. **İki tohumsuz iş aynı tohumu almıyor.** Sayaç porta verilir; iki `generate` çağrısı iki farklı
   tohum gösterir.
3. **Bir sesin bütün parçaları aynı tohumu paylaşıyor.** 24 saniyelik video → üç render, üçünde de
   aynı tohum.
4. **İşin kendi tohumu varsa değiştirilmiyor.** `seed=4242` verilen iş modele `4242` ile gider,
   port hiç çağrılmaz.

### `test_producer_contract.py` — kuyruğun yazdığı planla koşmak

5. **Plan kuyruğun yazdığı plana çevrilir:** `FRAMES` içindeki video ve ses işleri `seed: None`
   taşır (fotoğraf kendi tohumunu korur). Yorumu bunun neden böyle olduğunu ve hangi testin bunu
   kilitlediğini söyler.
6. **Sahte sampler torch'un şartını taşır:** `render(...)` aldığı tohumun tam sayı olduğunu
   doğrular. Sahtenin gerçek motorla ayrıştığı tek nokta buydu.

Bu ikisi ayrı test değil, dosyanın zaten koşan iki testinin zeminini değiştiriyor — ve o iki testi
kırmızıya çeviren şey bu.

### `test_photo_usecases.py` — kuyruğun ne yazdığını kilitlemek

7. **Kuyruk katman işini tohumsuz planlıyor.** Bu olmadan sözleşme dosyasındaki `seed: None` bir
   iddia olarak kalır; bununla birlikte yolun iki ucu birbirine bağlanır.

## Kırmızı ne olacak

| Test | Bugün | Nasıl düşüyor |
|---|---|---|
| 1, 2, 3, 4 (üreticinin dört tohum kuralı) | **kırmızı** | `TypeError` — yapıcı henüz `new_seed` almıyor |
| `..._runs_the_three_real_producers_end_to_end` | **kırmızı** | ses işi üç kez deneniyor, koşu `status: "error"` ile duruyor |
| `..._each_layer_is_made_from_the_one_below_it` | yeşil | sese hiç varmıyor — aşağıya bak |
| 7 (kuyruk tohumsuz planlıyor) | yeşil | bugünkü davranışı kilitler |

Beş kırmızı, ama biri diğer dörtten değerli: **uçtan uca sözleşme testi Colab'da olanın aynısını
gösteriyor** — tohumsuz iş, üç deneme, duran kuyruk. 1–4 ise henüz var olmayan bir parametreyi
istediği için düşüyor; asıl hatayı değil, gelecek arayüzü tarif ediyorlar. Dördü de portu yapıcıya
verdiği için dördü de aynı `TypeError`'a düşer — "kendi tohumunu koruyor" bekçisi dahil, çünkü
portun çağrılmadığını ancak port varken kanıtlayabilir. Commit mesajı bu ayrımı söyler, yoksa beş
düşen testin hepsi aynı şeyi kanıtlıyormuş gibi okunur.

Sözleşme dosyasının ikinci testi yeşil kalıyor ve bu bir eksik değil, ne sınadığının sonucu: o test
her katmanın altındakinden yapıldığını sınıyor, yani videonun ses üreticisine **ulaştığını** — bu da
render'dan önce oluyor. Sesin çıkıp çıkmadığını söyleyen, çıktı dosyalarına bakan birinci test.

## Kapsam dışı

- **Video'nun tohumsuzken ne yaptığı.** Kendi testi var ve geçiyor; bu görev ona dokunmuyor.
- **Sesin kalitesi.** Sahte sampler wav döndürür; gerçek sesin kulağa nasıl geldiğini ancak Colab
  turu söyler.
- **Ön yüz.** Hiçbir ekran değişmiyor, `dist/` yeniden derlenmiyor.

## Bitti sayılır

`python -m pytest queen-editor/backend/tests -q` beş düşen test veriyor, hepsi tohumun plandan
üreticiye giden yolunda; geri kalan takım yeşil. Commit kırmızı gidiyor ve mesajı bunu söylüyor.
