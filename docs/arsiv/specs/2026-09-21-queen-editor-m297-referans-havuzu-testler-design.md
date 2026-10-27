# Madde 297 — Referans havuzu diskte, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Kararlar yol haritasının
[referans bölümünde](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) duruyor.

## Madde ne diyor

> Referans dosyaları projenin klasörüne yazılıyor, listeleniyor, siliniyor. Tarayıcı Drive'a
> uzanmadığı için yükleme de okuma da sunucudan geçer *(FOUNDATION 4)*, ve havuz diskte durur
> *(FOUNDATION 2)*. **Sınır yok, ekran yok — yalnız saklama.**

Adet ve süre sınırları **298**'in, ekran **299**'un, sıralama **300**'ün.

## Havuz nerede durur

`<proje>/referans/` — projenin klasöründe bir alt klasör. Export'un `foto`/`video` klasörleri gibi
Türkçe: kullanıcı bu klasörü Drive'da kendi gözüyle açıyor *(madde 283'ün kuralı)*.

Fotoğraflar projenin kökünde duruyor ve `next_number` orayı tarıyor; bir **alt klasör** dosya
sayılmadığı için havuz oraya hiç değmiyor.

## Havuzun kendisi dizindir

**Ayrı bir JSON tutulmuyor.** Havuz, o klasördeki dosyaların ta kendisi; bir dosyanın **tipi kendi
uzantısından** okunuyor. Sebebi CODE-STANDARD'ın kendi kuralı: bir dosya başkasının cevabını bayrak
olarak tekrarlamaz. Bir dizin dosyası ikinci bir doğru olurdu — ve iki doğrunun ayrıştığı gün,
kullanıcının Drive'dan elle sildiği bir referans havuzda görünmeye devam ederdi.

*(Sıra **300**'de saklanacak: o, dosyaların cevaplayamadığı ayrı bir soru — "kullanıcı bunları hangi
sırayla istiyor" — ve dördüncü soruya dördüncü dosya açılır.)*

## Kurallar

**1. Tip uzantıdan.** Tanınanlar üç öbek: resim, video, ses. H3'ün kendi etiketleri
*(`<Picture N>`, `<Video N>`, `<Audio N>`)* bu üç sözcük olduğu için havuzun sözcükleri de onlar —
kartın katmanları *(`layers`)* değil. Referans bir katman değil, ve iki kavramı tek sözlükte
toplamak ikisini de bulandırırdı.

**2. Tanınmayan uzantı reddedilir**, ve cümle neyin alındığını söyler. Bu bir *sınır* değil: tipi
okunamayan dosya referans olamaz, çünkü havuz onu hangi sıraya koyacağını bilemez.

**3. Ad kullanıcınındır, ama üstüne yazılmaz.** Dosyanın kendi adı korunur *(kullanıcı küçük resmi
ondan tanıyor)*; klasörden kaçabilecek her şey atılır *(`../` ve dizin ayıracı)*; ad doluysa
uzantıdan önce bir sayı gelir — `kedi.png`, `kedi-2.png`. Üstüne yazmak kullanıcının işini silmek
olurdu *(FOUNDATION 1)*.

**4. Liste yükleme sırasında.** Dosya sisteminin kendi sırası bir söz vermez; sıra dosyanın kendi
zaman damgasından, eşitlikte addan okunur. Kullanıcının beklediği sıra bu, ve 300 bunun üstüne
kendi saklanan sırasını koyacak.

**5. Silmek ada göre, ve iki kez silmek bir kez silmekle aynı yere varır** — depolama katmanının
kendi kuralı.

**6. Baytlar sunucudan servis edilir**, `/references/<proje>/<dosya>` üzerinden. Fotoğrafların aksine
**sonsuza kadar önbelleklenmez**: silinen bir ad yeni bir dosyaya verilebilir, ve tarayıcıda kalan
eski baytlar yanlış küçük resim demek olurdu.

## Yazılacak testler

### `backend/tests/test_references.py` — kural

1. **`test_every_known_extension_says_which_kind_it_is`** — büyük/küçük harf farketmiyor.
2. **`test_an_extension_nobody_knows_has_no_kind`**
3. **`test_a_free_name_is_the_users_own`**
4. **`test_a_taken_name_takes_the_next_number`** — `kedi.png` doluyken `kedi-2.png`; o da doluysa
   `kedi-3.png`.
5. **`test_a_name_cannot_climb_out_of_the_folder`** — `../../gizli.png` havuzun içinde kalır.

### `backend/tests/test_reference_usecases.py` — kullanım senaryoları

6. **`test_a_reference_is_written_into_the_projects_pool`** — baytlar diskte, cevap ad ve tiple.
7. **`test_a_file_nobody_can_read_is_refused`** — `.txt` reddedilir ve **hiçbir şey yazılmaz**.
8. **`test_a_reference_for_a_project_that_does_not_exist_is_refused`**
9. **`test_the_pool_lists_in_the_order_it_was_filled`** — her satır adını ve tipini söylüyor.
10. **`test_a_second_file_with_the_same_name_stands_beside_the_first`** — ikisi de havuzda.
11. **`test_removing_takes_the_file_off_the_disk`**
12. **`test_removing_something_that_is_not_there_is_not_an_error`**

### `backend/tests/test_reference_routes.py` — kapılar

Kapılar **kendi blueprint'inde**: `presentation/reference_routes.py`. Aynı özelliğin içinde ikinci
bir blueprint, çünkü yüzey ayrı *(yükle / listele / sil / servis et)* ve kartların on beş
argümanlık fabrikasını on dokuza çıkarmak onu kimsenin okuyamayacağı hale getirirdi. `create_app`
zaten blueprint listesi alıyor.

13. **`test_two_references_are_uploaded_listed_and_one_is_deleted`** — maddenin *"görülür"*
    cümlesinin tamamı, **gerçek diskle**: yükle, listele, birini sil, ve **aynı klasörün üstüne
    ikinci bir sunucu kurulunca** kalan hâlâ orada. Yeniden başlatma böyle modelleniyor — kayıt
    bir dosya, oturum değil.
14. **`test_a_reference_is_served_from_the_server`** — baytlar geliyor, ve cevap sonsuza kadar
    önbelleklenmiyor.

## Bu turda yapılmayacaklar

Adet/süre sınırları *(298)*, ekran *(299)*, sıra ve boşluk *(300)*, üretim *(301–305)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` kırmızı, sebebi bu on dört testin hepsi — henüz ne kural ne
depo ne kapı var.
