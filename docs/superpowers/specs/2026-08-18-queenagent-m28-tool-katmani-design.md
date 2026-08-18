# Madde 28 — Tool katmanı: `edit_file` ve `build_prompts` · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 28](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** [beceriler tasarım kararları](../research/2026-08-18-queenagent-beceriler-tasarim-kararlari.md) §3, §4, §5, §5b
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · Bu madde yalnız araç yapar

Beceri yönergesi yok, arayüz yok. Madde 29 ve 30'un yönergeleri bu iki aracı çağıracak; onlar
yazılmadan önce araçların **kendi başlarına doğru** olması gerekiyor, çünkü bir yönerge yanlış
cevap verdiğinde suçun yönergede mi araçta mı olduğu ancak araç ayrı sınanmışsa bilinir.

İkisi de saf arka uç. Ekranda görünen tek şey, `build_prompts`'un doğurduğu dosyanın kartı.

---

## 2 · `edit_file` — güncelleme akışının eksik halkası

`create_file` **asla üstüne yazmaz**; aynı ad `plan-2.md` olur. Bu bilerek konmuş bir kural ve
duruyor: model bir dosyayı kazara silemez. Ama bedeli şu — bugün var olan bir dosyayı değiştirmenin
**hiçbir yolu yok**. Yapı JSON'unu kareler hâlinde büyütmek (§5b, beşerli partiler) ya da bir
karakter metnini güncellemek bu araç olmadan çalışmaz.

Araç **genel**, JSON'a özel değil (§3): ayrım formatta değil fiildedir.

| Argüman | Ne |
|---|---|
| `name` | dosyanın adı |
| `old` | dosyada **birebir** duran metin |
| `new` | yerine geçecek metin (boş olabilir — silmek de bir düzenlemedir) |

Kurallar, hepsi "tahmin etme" ilkesinin türevi:

1. Dosya yoksa → *There is no file by that name.*
2. `old` boşsa → reddedilir. Boş metin her yere uyar; hangi yere uyduğu belirsizdir.
3. `old` dosyada **yoksa** → *That text is not in `<ad>`.* Benzerini bulmaya çalışmaz.
4. `old` **birden çok kez** geçiyorsa → kaç kez geçtiğini söyler ve daha fazla çevre metin ister.
   Belirsiz bir eşleşmede yanlış yeri değiştirmektense hiçbir şey yapmamak doğrudur.
5. Tek eşleşme → değişir, *Edited `<ad>`.*

Dördüncü kural aracın emniyet kilidi: benzersizlik, "hangi kareyi düzenlediğini" modelin değil
metnin kanıtlamasıdır.

**Düzenleme dosya doğurmaz.** Sohbetteki dosya kartı "bu dosya doğdu" demektir; beşerli partilerle
yazılan bir yapı dosyası aynı kartı dört kez basardı. Kart yalnız doğuma kalır.

---

## 3 · `build_prompts` — metni model yazar, birleştirmeyi kod yapar

Belgenin ana ilkesi (§1): tutarlılığın garantisi modelin dikkati değil, deterministik bir komut.
Araç yapı JSON'unu okur, adları çözer, sabit sırayla birleştirir ve Python listesini yazar.

### 3.1 Okuduğu yapı (§4)

```json
{
  "quality": "score_9_up, masterpiece, best quality, absurdres",
  "characters": { "aylin": "1girl, long teal hair, ..." },
  "locations":  { "bedroom": "sunlit bedroom, morning light, ..." },
  "shots": [
    {
      "characters": ["aylin"],
      "location": "bedroom",
      "action": "sitting on the edge of the bed, holding a letter",
      "camera": "medium shot, from slightly above"
    }
  ]
}
```

`characters` liste, `location` düz string — asimetri bilerek (§4): bir karede birden çok karakter
olabilir, bir kare tek yerde geçer.

### 3.2 Birleştirme

Sıra kodda sabit ve kesin (§5.2):

**`quality → characters → location → action → camera`**

- `quality` her kareye **kod tarafından**, en başa eklenir. Baş/kuyruk ayrımı yok (§5c).
- Karakterler karedeki sırasıyla girer.
- Boş alan yok sayılır — `location`'ı olmayan kare de, karaktersiz kare de meşru.
- Metin virgülle ayrılmış etiket öbeğidir: birleştirme sonunda etiketler tek tek kırpılır, boşlar
  atılır, `", "` ile birleşir. `", ,"` sızamaz (§5.4).
- `solo` ya da sayı etiketine **dokunulmaz** (§5c): iki karakterli bir karede `1girl, solo` iki kez
  geçebilir ve yanlış söyleyebilir. Kullanıcı bunu sorun saymamayı seçti; kodda sessiz bir zekâ
  yoktur, yanlış çıktı ekranda görülür.

### 3.3 Bilinmeyen ad — isimli hata (§5.1)

Karenin andığı ad map'te yoksa araç **tahmin etmez**: hangi karede, hangi ad, ve o map'te
bilinenler ne — üçünü birden söyler.

> `shot 3: aylinn is not in characters; known: aylin, deniz`

Bilinenler yalnız **ilgili map'ten** listelenir; karakter ararken mekân adları saymak yardım değil
gürültüdür. Belgenin örneği ikisini birlikte anıyordu, burada ayrıldı.

Eksikler **toplanır**, ilkinde durulmaz: model tek turda hepsini düzeltsin. Ve **hiçbir dosya
yazılmaz** — kirli yapıdan liste üretilmez (§6'nın kapı kuralı).

Yapının kendisi bozuksa da aynı dil: geçersiz JSON ise **ayrıştırıcının kendi cümlesi** yazılır,
uydurulmuş sebep değil. `shots` boşsa ya da yoksa üretecek kare yok demektir; bu da söylenir.

### 3.4 Yazdığı dosya

```python
PROMPTS = [
    """<kare 1>""",
    """<kare 2>""",
]
```

Üç tırnak, trailing comma, değişken adı `PROMPTS` (§5.5) — kopyala-yapıştır hazır.

Bir prompt üç tırnak ya da ters bölü taşırsa dosya **import edilemez** hâle gelirdi; bunlar
kaçırılır. Etiketlerde böyle bir şeyin olması beklenmez, ama beklenti dosyayı ayakta tutan şey
değildir.

### 3.5 Çıktının adı — belgeden bir okuma

Belge çıktıyı "`prompts.py`" diye anıyor; aynı belge **bir projede aynı anda birden çok senaryonun
yaşayabileceğini** söylüyor (§4). Sabit tek ad iki senaryoyu birbirine yazdırırdı.

Karar: **çıktının adı kaynaktan türer — aynı gövde, `.py` uzantısı.** `intro-shots.json` →
`intro-shots.py`. Çarpışma imkânsız, model adı hiç düşünmez, ve dosya listesinde çift göz
tarafından okunur: yapı ve ondan doğan liste yan yana durur.

Kaynağın adı zaten `.py` ile bitiyorsa türetilen ad kaynağın kendisi olurdu; bu reddedilir — araç
okuduğu dosyayı yok etmez.

### 3.6 Üstüne yazar — ve bu bilerek

`create_file`'ın "asla üstüne yazma" kuralı **buraya geçmez**. `build_prompts`'un çıktısı türev bir
üründür: karakteri güncelle, yeniden çağır, **bütün kareler döner** — maddenin görünür kabulü bu.
Numaralasaydı her düzeltme `intro-shots-2.py`, `-3.py` bırakır, hangisinin güncel olduğu
kaybolurdu. Kaynak (yapı JSON'u) korunur, türev yenilenir.

---

## 4 · Tur sayısı yetmiyor — `MAX_ROUNDS` büyür

Bugünkü sınır 8 tur ve gerekçesi "list, read, read, write, explain" zinciri. **Generate prompts+**
zinciri bunun iki katı: liste → oku → iskelet → beşerli partiler (bir partiden fazlası) → öz-denetim
→ `build_prompts`. Otuz karelik bir senaryoda tur sayısı ondan fazla olur ve model işi **yarıda**
bırakırdı — hem de sessizce, çünkü sınıra varmak bir hata değil bir duruştur.

Sınır **16**'ya çıkar ve gerekçesi yeni en uzun zinciri anlatacak şekilde yeniden yazılır. Sınırsız
döngü hâlâ yok: sınır kaçak bir döngünün faturasını kesmek için var, işi kesmek için değil.

---

## 5 · Bir turda aynı dosya iki kez doğarsa

`build_prompts` bir turda iki kez çağrılabilir (iki senaryo, ya da bir düzeltmenin ardından yeniden
üretim). Aynı ad iki kez doğarsa mesajın dosya listesi onu iki kez taşır ve ekran aynı kartı iki kez
çizer. Doğan adlar **tekilleştirilir**: kart bir dosyanın var olduğunu söyler, kaç kez yazıldığını
değil.

---

## 6 · Katman denetimi

**Domain (saf):** yeni `domain/build_prompts.py` — yapıyı alır, dizge listesi döndürür, `PROMPTS`
metnini üretir; diski hiç görmez, bu yüzden store'suz sınanır. Yeni hata `domain/errors.py`'de:
`BadStructure` — kelimelerini kendi taşır.

**Domain (tool kabuğu):** `domain/tools.py` — iki yeni `TOOL_SPECS` girdisi ve `run_tool`'daki iki
dal; dosya okuma/yazma `file_store` üzerinden. `MAX_ROUNDS` burada.

**Use case:** `domain/usecases/stream_answer.py` — dosya doğuran araçların kümesi adlandırılır
(bugün `create_file`'a gömülü), `build_prompts` da dashed kartı yükseltir; doğan adlar tekilleşir.

**Data / presentation / ön uç:** dokunulmaz. Yeni uç nokta yok, yeni ekran yok.

---

## 7 · Kabul ölçütü

1. `edit_file` tek eşleşen metni değiştirir ve dosyanın gerisi aynı kalır.
2. Olmayan dosya, boş `old`, bulunamayan `old` ve **birden çok** eşleşme — dördü de cümleyle
   cevaplanır, hiçbiri dosyaya dokunmaz.
3. `edit_file` **dosya doğurmaz** — sohbete kart düşmez.
4. `build_prompts` her kareyi `quality → characters → location → action → camera` sırasıyla üretir.
5. Karakter metni bütün karelerde **birebir aynıdır**; map'te tek değeri değiştirmek hepsini döndürür.
6. Bilinmeyen ad: hangi kare, hangi ad, o map'te bilinenler — ve **dosya yazılmaz**.
7. Geçersiz JSON'da ayrıştırıcının kendi cümlesi geçer; `shots` boşsa söylenir.
8. Yazılan dosya **geçerli Python**'dır ve `PROMPTS` beklenen listedir.
9. Çıktının adı kaynağın gövdesi + `.py`; ikinci çağrı **üstüne yazar**, numaralamaz.
10. Uzun bir zincir 16 turda biter; aynı turda iki kez doğan ad mesajda bir kez durur.
11. Beş araç da modele bildirilir.

## 8 · Sınırlar

- **Düzenlenen dosya ekranı tazelemez.** Tazeleme "dosya doğdu" olayına bağlı; düzenleme doğum
  değil. Açık okuyucu ve dosya listesi, o turda bir dosya doğana dek (prompts+ zincirinde
  `build_prompts`) eski hâli gösterir. Bilerek bırakılıyor: kart basmadan tazeleme yapmak yeni bir
  olay türü demek ve bu maddenin işi araçlar.
- **Okuyucunun mono gösterimi burada değil** (§9). `.json`/`.py` dosyalarını Markdown çizmek
  girintiyi yutuyor; düzeltme, bu dosyaların ekranda ilk göründüğü Madde 30'a yazıldı.
- Aracın adı `build_prompts` ve **yalnız kod çalışır** — Anthropic'in üçüncü kademesindeki desen
  (§2b): script koşar, kodu bağlama girmez, yalnız çıktısı girer.
