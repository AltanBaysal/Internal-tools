# Madde 70 — Karede iki karakter varsa prompt onları ayırır · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası, Madde 70](../plans/2026-08-25-queenagent-v5-roadmap.md)
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz.

---

## Ne bozuk

Bugün bir kare şu sırayla kuruluyor
*([build_prompts.py:31-42](../../../queen-agent/backend/features/workspace/domain/build_prompts.py#L31-L42))*:

```
quality, karakter1, kıyafet1, karakter2, kıyafet2, mekân, action, camera
```

İki karakterin tarifi **yan yana**. Görüntü modeli bitişik iki kişiyi ayıramıyor: nitelikler
birbirine karışıyor, kimin saçı kimin olduğu belirsizleşiyor. Şikâyetin kendisi bu — *"iki karakter
aynı karede patlıyor"*.

## Karar: ana karakter başta, geri kalan herkes sonda

*(kullanıcı kararı, 27 Ağustos)*

```
quality, [ana karakter + kıyafetleri], mekân, action, camera, [2. kişi + kıyafetleri], [3. kişi + ...]
```

Araya mekân, action ve camera giriyor; iki tarif artık temas etmiyor. Somut hâli:

```
bugün:  quality, 1girl teal hair, jeans, 1girl freckles, red dress, bedroom, sitting, medium shot
sonra:  quality, 1girl teal hair, jeans, bedroom, sitting, medium shot, 1girl freckles, red dress
```

Üç kural, üçü de kullanıcının:

- **Ana karakter, karenin `characters` haritasındaki ilk isim.** Ayrı bir alan yok — yazan model
  sırayı zaten seçiyor, ve ilk yazdığı kişi kastettiği kişi.
- **Kıyafet her zaman sahibiyle tek blok.** Kimin neyi giydiğini söyleyen tek şey yan yana
  durmaları; blok bölünürse çözülen sorun geri gelir.
- **Üçüncü ve sonrası da sona.** İkinci ve üçüncü orada yan yana kalıyor, ve aralarında aynı karışma
  riski sürüyor. Bilinerek kabul edildi: temiz kalması gereken ana karakter.

## Karar: sayı etiketi action'a geçer

*(kullanıcı kararı, 27 Ağustos)*

Bugün `1girl` karakter tanımının içinde: `"aylin": "1girl, long teal hair"`. Bu iki sebeple yanlış
yerde. Sayı **kareye** ait, karaktere değil — aynı karakter bir karede tek başına, ötekinde biriyle
beraber. Ve iki karakterli bir karede `1girl` iki kez yazılıyor.

Yeni yeri action. Doğrusunu — `1girl`, `2girls`, `1boy, 1girl` — yapıyı yazan model yazıyor, çünkü
karede kimin olduğunu o anda bilen o.

**Sayma koda alınmıyor.** Kod kareye kimin girdiğini biliyor ama ne olduklarını bilmiyor: bir
karakterin kadın mı erkek mi olduğu hiçbir alanda durmuyor, yalnız o `1girl` dizesinde ima ediliyor.
Kodun sayabilmesi için şemaya cinsiyet alanı eklemek gerekirdi, ve bu maddenin sorduğu soru o değil.
Bu bir FOUNDATION 5 esnetmesi ve bilerek yapılıyor — kod bilmediği bir şeyi kurallaştıramaz.

## Karar: diskteki eski dosyalar temizlenmiyor

Yol haritasının açık sorusuydu. Temizlemek, kullanıcının dosyalarını bizim yeniden yazmamız olurdu.
Eski dosya bugünkü gibi çalışmaya devam ediyor — sayısı karakterin içinde kalıyor ve iki kişilik
karede çift yazılıyor — ve model o dosyaları düzenledikçe kendiliğinden yeni biçime geçiyorlar.

**Sıra düzeltmesi eski dosyalarda da çalışıyor:** ayıran şey nerede durdukları, ne yazdıkları değil.

## Testler nasıl kırmızı olur

### `backend/tests/test_build_prompts.py`

| Test | Ölçü | Bugün |
|---|---|---|
| `..._puts_everyone_after_the_first_at_the_end` | iki karakterli karenin tam dizesi | **kırmızı** |
| `..._three_characters_leave_only_the_first_at_the_front` | üçüncü de camera'dan sonra | **kırmızı** |

Bir de **yeşil doğan iki bekçi**, çünkü değişmemesi gereken yarıyı tutuyorlar: tek karakterli kare
eskisi gibi çıkıyor, ve ana karakter mekândan önce duruyor.

**Yeşil kalan iki test**, iddiaları hâlâ doğru olduğu için: `test_each_characters_block_stays_together`
*(bloklar hâlâ bütün, yalnız araları açıldı)* ve `test_two_characters_keep_the_frames_own_order`
*(ilk yazılan hâlâ önce)*. İkisi de sıralamayı `index` ile ölçüyor ve yeni sıra o sıralamayı bozmuyor.

### `backend/tests/test_skills.py`

| Test | Ölçü | Bugün |
|---|---|---|
| `..._keeps_the_count_out_of_the_character` | şema örneğinde `"aylin": "1girl` yok | **kırmızı** |
| `..._shows_the_count_in_the_action` | örnekte `"action": "1girl`, ve metinde `2girls` | **kırmızı** |
| `..._says_which_character_comes_first` | metin ilk karakterin ana karakter olduğunu söylüyor | **kırmızı** |

Üçüncüsü metinde olmak zorunda: sırayı kod kuruyor ama **haritayı model yazıyor**, ve hangi ismi
önce yazacağını bilmesi gerekiyor.

## Beklenen kırmızı

**Beş.** İkisi kurucuda, üçü metinde.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Nasıl görülür

```
python -m pytest queen-agent -q
```

Ön yüz açılmıyor, `dist` derlenmiyor.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `build_prompts.py` ve `skills.py` bu turda açılmaz.
- **Şemaya cinsiyet alanı eklenmez.**
- **Diskteki yapı dosyaları dönüştürülmez.**
- **`shots` yedeği kaldırılmaz** — kendi kararı, kendi günü.
- **Prompt dili tartışılmaz** — etiketten cümleye geçiş 75'in işi, ve bu maddenin sıra kararı o
  geçişten bağımsız: cümleye dönse de ana karakterin başta, ötekilerin sonda durması aynı sebeple
  doğru kalır.
