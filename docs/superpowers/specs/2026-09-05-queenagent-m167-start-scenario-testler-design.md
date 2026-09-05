# Madde 167 · test turu — `start_scenario` yapı dosyasını doğurur

**Kaynağı:** [v7 yol haritası, Madde 167](../plans/2026-09-05-queenagent-v7-roadmap.md).
Bu tur **yalnız testleri** yazar; kod değişmez ve takım kırmızı commit'lenir.

---

## Ne doğacak *(uygulama turunun işi, burada yalnız tarif)*

`start_scenario(name)` — boş bir yapı dosyası doğurur:

```json
{ "characters": {}, "outfits": {}, "locations": {}, "frames": [] }
```

- **Adı araç koyar.** `safe_name`'den sonra yeni bir `scenario_name` uzantıyı `.json`'a çevirir.
  Emsali `plan_name`: *"bir plan plan gibi okunsun diye adlandırılır, ve araç başka bir şey
  yazamasın diye."* Aynı gerekçe: model `bar-scene` ya da `bar-scene.md` dese bile senaryo `.json`
  olur, ve 171 kapıyı `.json`'a kapattığında **doğuran araç ile kapanan kapı aynı uzantı üstünde**
  buluşur. İkisi ayrı uzantı bilseydi kapı kendi doğurduğu dosyayı korumazdı.
- **Alınmış adı reddeder.** `create_file`'ın kuralı, kendi cümlesiyle: *There is already a file
  called bar-scene.json. Open it and add to it, or pick another name for a new scenario.* Cümle
  ne yapılacağını söylüyor, çünkü *"var"* demek bir sonraki hamleyi tahmine bırakır ve modeli
  buraya getiren zaten tahmindi.
- **Kart çizilir.** `WRITES_FILES`'a girer ve `created` adı taşır — dosya gerçekten doğuyor.
- **Kiplerde `create_file`'ın yanında:** edit sormadan, ask ve plan sorarak.

## Neden ayrı bir araç, `create_file`'ın bir kipi değil

`create_file` **belge** doğuruyor — kullanıcının saklamak istediği bir yazı. Bu **yapı** doğuruyor,
ve içeriğini model yazmıyor: dört boş harita kodun bildiği bir şekil. İçerik parametresi olmayan bir
araç, modelin şekli hiç görmediği anlamına geliyor — koşunun bağlayıcı kuralı.

Ve 171'in kapatacağı kapı ancak bu araç varsa kapanabilir: yoksa `.json` yasaklandığında modelin
senaryo başlatacak hiçbir yolu kalmaz.

---

## Testler

### `test_tools.py` — yeni bölüm

| Test | İddiası |
|---|---|
| `test_start_scenario_writes_the_empty_maps_and_no_frames` | Dosya tam olarak dört anahtar taşıyor, hepsi boş |
| `test_start_scenario_names_the_file_after_the_scenario` | `bar-scene` · `bar-scene.md` · `bar scene` üçü de `bar-scene.json` |
| `test_start_scenario_refuses_a_name_that_is_taken` | Cümle adı ve iki çıkışı söylüyor; dosya **değişmiyor** |
| `test_start_scenario_says_what_it_started` | Cevap metni ve karttaki sonuç kelimesi |
| `test_start_scenario_hands_the_name_back_so_a_card_is_drawn` | `created` dolu, ve `WRITES_FILES` onu tanıyor |
| `test_start_scenario_writes_the_file_for_a_person_to_read` | Girintili ve kendi dilinde — `_add_frames`'in kuralı, aynı dosyayı açan aynı kullanıcı |

**Hepsi kırmızı olacak:** bugün böyle bir araç yok, `run_tool` *There is no tool called
start_scenario.* diyor.

`test_start_scenario_refuses_a_name_that_is_taken`'in ikinci yarısı — **dosya değişmiyor** — bugünkü
kodda da doğru *(hiçbir şey yazılmıyor)*, ama tek başına vakumda doğru: araç yokken dosya elbette
değişmez. Nail'in kendisi ilk yarısı, ve ikincisi onunla birlikte anlam kazanıyor.

### `test_modes.py` — bir satır

`WRITES` listesine `start_scenario` eklenir. Bu, `test_ask_mode_asks_before_it_writes`'ı **kırmızıya
düşürür**: bilinmeyen bir araç hiç sorulmuyor *(`needs_permission` `False` döndürüyor)*, yani ask
kipi onu sessizce koşardı.

`test_edit_mode_asks_for_nothing` `TOOL_SPECS` üstünde dönüyor, yani araç eklenene kadar **yeşil**
kalıyor ve uygulama turunda da yeşil kalır — çünkü o tur aracı ve kip satırını birlikte ekliyor.

---

## Bu turda yapılmayanlar

- **Kod açılmıyor.**
- **`create_file`'ın `.json` kapısı kapanmıyor** — o 171. Bu maddeden sonra iki yol birden var, ve
  bilerek: kapı ancak alternatifi hazırken kapanır.
- **Şema aracı duruyor** — 172. Şu an modele hâlâ *"yapı dosyasını `create_file` ile yaz"* diyen bir
  metin var; Dilim 1'in sonunda gidiyor.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Koşan kırmızı: 9 vak'a, 7 testten.** `test_tools.py`'de altı yeni test — ama adlandırma testi
   üç adla parametreli, yani sekiz vak'a — artı `test_modes.py`'de
   `test_ask_mode_asks_before_it_writes`. *(Spec önce 7 demişti; parametreyi saymamıştı, ve koşan
   rakam buraya yazıldı.)*
3. Öteki üç takım rakamlarını korur: bu madde `tools.py` ile `modes.py`'ye bakıyor, ön yüze değil.
4. Kırmızı commit'lenir. `skip` ya da `xfail` yok.
