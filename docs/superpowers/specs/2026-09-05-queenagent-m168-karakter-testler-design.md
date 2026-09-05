# Madde 168 · test turu — karakter yönetimi

**Kaynağı:** [v7 yol haritası, Madde 168](../plans/2026-09-05-queenagent-v7-roadmap.md).
Bu tur **yalnız testleri** yazar; kod değişmez ve takım kırmızı commit'lenir.

Bu madde üç aracın yanında **iki ortak parçayı** da doğuruyor, ve 169–174 onları olduğu gibi
kullanacak. O yüzden testlerin bir kısmı karakterden çok **kalıbı** çiviliyor.

---

## Üç araç

| Araç | İmza | Reddi |
|---|---|---|
| `add_character` | `file`, `name`, `tags` | Ad zaten varsa |
| `update_character` | `file`, `name`, `tags?`, `new_name?` | Ad yoksa; ya da değiştirilecek bir şey verilmediyse |
| `remove_character` | `file`, `name` | Bir kare onu anıyorsa |

**Dosyanın parametresi `file`, girdinin `name`.** İkisi de `name` olamaz, ve dosya tarafı `file`
oluyor çünkü bu araçların konusu **girdi** — cümlenin öznesi karakter, dosya nerede durduğu.

### Neden `add` ve `update` ayrı

Kullanıcı kararı *(5 Eylül: "yazılım gibi düşün")*. `add` var olan ada reddediyor, `update` olmayana:
**sessiz üzerine yazma imkânsız hâle geliyor.** Emsali depoda: `create_file` var olan ada reddediyor,
değiştirmek `edit_file`'ın işi — ve o kural Madde 69'da bir dosyanın sessizce kaybolmasından doğdu.

Bedeli açık: tek araç yerine iki tanım, her istekte. Kazanılan, modelin adın var olup olmadığını
bilmeden çağırıp yanlış olanı yapmasının **mümkün olmaması**.

---

## İki ortak parça

### `_opened(file_store, project_id, args)`

Dört aracın aynı dört satırla başlamasını engelliyor. `(source, structure, refused)` döndürüyor;
`refused` doluysa çağıran onu olduğu gibi döndürüyor.

Üç ret, ve üçü de **tek yerde yazılıyor** ki bir dosyanın yokluğu her araçta aynı okunsun:

- *There is no file by that name.*
- *bar-scene.json is not valid JSON:* + ayrıştırıcının kendi cümlesi *(CLAUDE.md: sebebi uydurma,
  servisin dediğini yaz)*
- *bar-scene.json has no frames list to add to; a structure file carries one.*

**Kareler listesi neden şart:** silme *"bu ad hâlâ kullanılıyor mu"* diye soruyor ve cevap karelerde;
yeniden adlandırma kareleri de değiştiriyor. Yani listesi olmayan bir dosya bu araçların işini
yapamaz, ve bunu ekleme anında söylemek silme anında çökmekten iyi.

### `cast_of(frame)` — `build_prompts._worn` herkese açılıyor

Bir karenin kadrosunu `(ad, kıyafetler)` çiftleri olarak okuyan tek yer. Bugün `build_prompts`'un
özeli, ama `remove_character` ile `update_character` da **aynı iki şekli** okumak zorunda: bugünkü
harita biçimi ve kıyafetler doğmadan önceki düz ad listesi.

Kopyalamak iki kopya demek, ve ikisi ilk değişiklikte ayrışır. Alt çizgili adı başka modülden
çağırmak da bir sözleşme olmadan bağımlılık kurmak — **arşiv dalında bunun kaydı bir kusur olarak
düşülmüştü.** O yüzden ad açılıyor ve ne yaptığını söyler hâle geliyor: `cast_of`.

---

## Cevaplar

**Oldu**

> Added *aylin* to characters.
> Changed *aylin* in characters; *2 frames* name it.
> Renamed *aylin* to *ayla* in characters; *2 frames* followed.
> Renamed *aylin* to *ayla* in characters and changed its text; *2 frames* followed.
> Removed *aylin* from characters.

Kaç karenin adı andığı **her zaman** söyleniyor: modelin bir düzenlemenin nereye kadar gittiğini
dosyayı geri okumadan öğrendiği yer burası — Madde 129 ve 131'in birer birer sebep aldığı alışkanlık.

**Ret**

> A character needs a name.
> A new character needs tags.
> There is already a character called *ayla*.
> *aylin* is not in characters; known: *lara, deniz*.
> Nothing was given to change about *aylin*.
> *aylin* is already called that.
> *aylin* is still in frames *1, 3*. Nothing was removed.

*"known:"* listesi `build_prompts._looked_up`'ın cümlesiyle **aynı şekilde** yazılıyor — bir ad
bulunamadığında nerede olursa olsun aynı okunsun diye. Bilinen hiçbir ad yoksa: *known: nothing*.

---

## Testler — `test_tools.py`, yeni bölüm

### `add_character`

| Test | İddiası |
|---|---|
| `test_add_character_writes_the_name_and_its_tags` | Haritada duruyor, metni birebir |
| `test_add_character_says_what_it_added` | Cevap ve karttaki sonuç kelimesi |
| `test_add_character_refuses_a_name_that_is_already_there` | Cümle adı söylüyor, **harita değişmiyor** |
| `test_add_character_needs_a_name` | Boş ad reddediliyor |
| `test_add_character_needs_tags` | Yeni bir girdi metinsiz doğamaz |
| `test_add_character_leaves_the_other_maps_alone` | Kıyafetler, mekânlar, kareler el değmemiş |

### `update_character`

| Test | İddiası |
|---|---|
| `test_update_character_changes_the_tags` | Metin yenisiyle değişiyor |
| `test_update_character_refuses_a_name_nobody_knows` | Cümle bilinenleri sayıyor |
| `test_update_character_renames_and_the_frames_follow` | Kareler yeni adı anıyor, kıyafetleri duruyor |
| `test_update_character_says_how_many_frames_followed` | Sayı cevapta |
| `test_update_character_can_do_both_at_once` | Ad ve metin birlikte |
| `test_update_character_refuses_a_name_that_is_taken` | `ayla` varken `aylin`'i `ayla` yapmak sessiz birleştirme olurdu |
| `test_update_character_needs_something_to_change` | İkisi de verilmezse ret |
| `test_update_character_refuses_renaming_to_the_same_name` | İş yok, ve *"oldu"* demek yanlış olur |
| `test_update_character_reads_the_old_list_form_when_it_renames` | Kıyafetsiz düz ad listesi taşıyan eski kare de değişiyor |

### `remove_character`

| Test | İddiası |
|---|---|
| `test_remove_character_takes_the_name_out` | Haritadan gidiyor |
| `test_remove_character_refuses_while_a_frame_names_it` | Kare numaraları cevapta, **harita değişmiyor** |
| `test_remove_character_refuses_a_name_nobody_knows` | `_looked_up`'ın cümlesi |
| `test_remove_character_leaves_the_frames_alone` | Silinen ad hiçbir karede değilse kareler el değmemiş |

### Ortak parça

| Test | İddiası |
|---|---|
| `test_a_character_tool_says_when_the_file_is_not_there` | Üç araç da aynı cümle |
| `test_a_character_tool_says_when_the_file_is_not_json` | Ayrıştırıcının kendi cümlesi geçiyor, uydurma sebep yok |
| `test_a_character_tool_says_when_the_file_has_no_frames_list` | Neden şart olduğu cümlede |
| `test_the_cast_of_a_frame_is_read_the_same_way_everywhere` | `cast_of` iki şekli de okuyor, ve `build_prompts` onu kullanıyor |

### `test_modes.py` ve araç listesi

`WRITES`'a üç ad; `test_every_tool_is_declared_to_the_model`'in kümesine üç ad. **İkincisi 167'de
kaçırıldı ve uygulama turuna sarktı** — bu sefer test turunda.

---

## Bu turda yapılmayanlar

- **Kod açılmıyor.**
- **`SDXL_PROMPT_RULES` yazılmıyor** — etiketlerin nasıl yazılacağı 172'nin işi. Bu madde girdinin
  **yerini** kuruyor, metnini değil.
- **Kıyafet ve mekân araçları yok** — 169 ve 170. Kalıp burada doğuyor, onlar tekrarlıyor.
- **`create_file`'ın `.json` kapısı açık** — 171.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Koşan kırmızı: 31 vak'a.** Yeni testlerin hepsi, artı `test_modes.py`'nin ask kipi testi ve
   `test_every_tool_is_declared_to_the_model`. Üç ortak-parça testi araç başına parametreli, yani
   dokuz vak'a veriyor.

   **İki test ilk koşuda boşlukta doğru çıktı** ve düzeltildi:
   `test_add_character_leaves_the_other_maps_alone` ile
   `test_remove_character_leaves_the_frames_alone`. Araç yokken hiçbir şey olmuyor, dolayısıyla
   *"öteki haritalar el değmemiş"* kendiliğinden geçiyordu — hiçbir şey yapmayan bir çağrıda her
   koruma iddiası doğrudur. İkisine de **önce işin olduğunu** doğrulayan bir satır eklendi; aynı
   tuzağı `test_break_never_touches_a_comma` da kendi yorumunda anlatıyor.
3. Öteki üç takım rakamlarını korur.
4. Kırmızı commit'lenir. `skip` ya da `xfail` yok.
