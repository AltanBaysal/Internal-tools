# Madde 173 · test turu — kare sahnesiyle doğar

**Kaynağı:** [yol haritası](../plans/2026-09-05-queenagent-v7-roadmap.md), Madde 173. Dilim 2'nin ilk
maddesi, ve Dilim 1'in açık bıraktığı çatlağı kapatıyor: `add_frames`'in açıklaması hâlâ *"each
shaped as the schema says"* diyor, oysa şema 172'de öldü. Model kare eklemeye geldiğinde şekli
öğreneceği yer yok — tahmin ediyor.

Bu tur **yalnız testleri** yazıyor ve kırmızı commit'liyor.

---

## Kapanan bahis

`add_frames` bir JSON listesi alıyordu: `items: {"type": "object"}`, içi serbest. Karenin ne
taşıdığını araç bilmiyordu, dolayısıyla **yanlış yazılmış bir kare sessizce diske giriyordu** —
olmayan bir karakter, listesiz bir kıyafet, hiç `location`. Yanlış ancak `build_prompts` çağrıldığında,
bambaşka bir raundda görünüyordu.

`add_scene` alanları imzaya çıkarıyor. Koşunun bağlayıcı kuralı bu: **model aracın imzasını bilir,
dosyanın şeklini değil.** Kare artık sahnesiyle, kadrosuyla ve mekânıyla doğuyor; adları araç
haritalarda arıyor.

## Aracın imzası

`add_scene(file, scenes)`.

- **`file`** — harita araçlarının parametre adı, ve `_opened`'ın okuduğu ad. `add_frames`'in `name`'i
  onunla birlikte gidiyor: aynı dosyayı iki farklı adla isteyen bir takım, modelin ezberleyeceği
  ikinci bir şey demek.
- **`scenes`** — liste, tek sahne için de. Her sahne `{scene, characters, location}`.
- **Yalnız `scene` zorunlu** *(kullanıcı kararı, 5 Eylül)*. Manzara karesinin kadrosu, yakın çekimin
  mekânı olmayabilir; verilmeyen alan kareye hiç yazılmıyor. `build_prompts` ikisini de kaldırıyor —
  `cast_of` boş liste veriyor, `location` boşsa satır atlanıyor.
- **`action` yok.** Onu 176'da Grok yazıyor; `add_scene`'in yazdığı kare eksik değil, yarım.

## Numara karenin yeri

Kod kareye `number` veriyor: **listedeki sırası**, 1'den. Bir sayaç değil — `_frames_naming` ve
`build_prompts` kareleri zaten `enumerate(frames, start=1)` ile sayıyor, ve ikinci bir doğruluk
kaynağı ilk silmede ötekinden ayrılırdı. 174'ün silmeden sonra yeniden numaralaması da aynı kuralı
izliyor.

Alan yine de yazılıyor: kullanıcı dosyayı elle açıp okuyor, ve modelin *"3. kareyi düzelt"* diyen
kullanıcıyı dosyada bulabilmesi gerekiyor.

Eski dosyaların karelerinde `number` yok. Sorun değil — numara yerden geliyor, alandan değil.

## Ret: hepsi birden, ve hiçbir şey yazılmadan

Her ad haritalarda aranıyor. Bulunmayanların **hepsi** tek cevapta dönüyor, `build_prompts`'ın
kuralı: *bir geçiş hepsini düzeltir.* Cevabın sonu **`Nothing was added.`** — sessiz başarısızlık
yok.

| Ne | Cümle |
|---|---|
| bilinmeyen ad | `frame 4: aylin is not in characters; known: lara, deniz.` |
| sahnesiz sahne | `frame 4: a scene needs a sentence saying what happens.` |
| `characters` harita değil | `frame 4: characters is a map from a name to the outfits they wear.` |
| sahne nesne değil | `frame 4: a scene is an object with scene, characters and location.` |

Bilinmeyen adın cümlesi `_unknown`'dan geliyor — üç haritada ve `build_prompts`'ta aynı cümle,
başına kare numarası ekleniyor. Şekli bozuk bir sahne **tek** sorun bildiriyor: içine bakılamayan
bir nesnede ad aramak, aynı hatayı iki kere saymak olur.

Numara, sahnenin **alacağı** numara: `len(frames) + sıra`. Model dosyada arayacağı şeyi değil,
elindeki listede düzelteceği şeyi görüyor.

`_opened`'ın üç reddi *(dosya yok, JSON bozuk, `frames` listesi yok)* olduğu gibi devralınıyor.

## Bir küçük bağışlama

`{"aylin": "gecelik"}` — listesiz tek kıyafet — kabul ediliyor ve diske **liste olarak** yazılıyor.
`cast_of` bu kaymayı okurken zaten bağışlıyor *(bir string'i harf harf yürümek, küçük bir kaymaya
saçmalıkla cevap vermek olurdu)*; burada da bağışlanıyor, ama **kanonik şekle çevrilerek**: okumak
iki şekle katlanır, yazmak katlanmaz — dosyaya giren şekli araç seçiyor.

## Cevap

- Çok: `Added 3 scenes to scene.json as frames 3-5.`
- Tek: `Added 1 scene to scene.json as frame 3.`
- Kart: `counted(n, "scene")` → *3 scenes*. Dosya doğmuyor, `created` `None`.
- Boş liste: `No scenes were given, so scene.json is unchanged.` — hiçbir şey yazılmıyor.
- Liste değil: `add_scene takes a list of scenes, even when there is one of them.`

## Ölen adın metinlerden çıkması

`add_frames` `TOOL_SPECS`'ten, `run_tool`'dan, `modes.py`'den ve testlerden gidiyor; `run_tool` adı
geçen eski bir turu *There is no tool called add_frames.* ile karşılıyor.

**Skill metni de dokunuluyor** — 172'nin kuralı: *ölen aracın adı metinlerden çıkar, gerisi 178'de.*
`GENERATE_PROMPTS_PLUS`'ın *"Add frames with add_frames"* satırı `add_scene` oluyor. Tek kelime,
kelime tavanı kıpırdamıyor. Metnin geri kalanı — `create_file`'ın iskeleti yazdığı, sahne listesi
dosyası — hâlâ eski takımı anlatıyor ve öyle kalıyor.

---

## Çivilenen vak'alar — 30

**Bildirim (4):** araç listesinde `add_scene` var ve `add_frames` yok; `run_tool` ölü adı tanımıyor;
`modes.py`'nin kipleri yeni adın önünde kapıyı tutuyor; **`scenes.items.required == ["scene"]`** —
kullanıcının 5 Eylül kararı, modelin okuduğu tek yerde.

**Yazdığı (12):** sona ekliyor · numarayı yerinden veriyor · çok ve tek için iki cümle · kart sahne
sayıyor · `scene`/`characters`/`location` yazıyor ve `action` yazmıyor · yalnız cümlesi olan sahne
kadrosuz ve mekânsız bir kare · listesiz kıyafet listeye dönüyor · Türkçe okunur kalıyor ·
haritalara dokunmuyor · dosya doğurmuyor · yazdığı kareden `build_prompts` prompt üretiyor.

**Reddettiği (12):** bilinmeyen karakter, kıyafet, mekân · hepsi birden · sahnesiz sahne *(boş da
sahnesiz)* · `characters` harita değil · sahne nesne değil ve **tek** sorun bildiriyor · `scenes`
liste değil · boş liste · ve üç `_opened` reddi.

**Skill (1)** ve **ikinci çağrı (1):** akış `add_scene` diyor; aynı sahne iki kere çağrılınca iki
kare oluyor ve cevabın numarası bunu gösteriyor.

## Koşarken çıkan tek şey: boşta geçen bir test

`test_add_scene_brings_no_file_into_being` ilk koşuda **yeşildi.** İddiası `added.created is None`,
ve tanınmayan bir aracın cevabında da `created` `None` — yani test, `add_scene` hiç var olmadığı
için geçiyordu. 168'in dersi, üçüncü kez: **işin olduğu önce iddia edilmezse, hiçbir şey olmayınca
da yeşil kalır.** Kareyi saydıran bir satır eklendi, kırmızıya döndü.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **30 kırmızı**, hepsi `queen-agent`'ta; hiçbiri `skip` ya da `xfail` değil.
3. Kırmızıların hepsi **yokluktan** — `There is no tool called add_scene.`, `StopIteration`, ve ölü
   adın hâlâ cevap vermesi. Başka sebeple kırmızı olan bir test, yanlış yazılmış demektir.
4. Öteki üç takım rakamlarını korudu: **586 · 739 · 591.** `dist` derlenmedi.
