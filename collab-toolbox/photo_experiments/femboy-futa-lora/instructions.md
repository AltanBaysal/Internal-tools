# Femboy ve futa LoRA'ları — Talimatlar

Madde 501 · v11-4 *(Queen Editor v11 yol haritası)*. Tek defter: `femboy-futa-lora.ipynb`, tek Colab
oturumu, altı aday — üç femboy, üç futa. Workflow'lar Queen Editor'ün kendi fotoğraf grafiği; adayın
LoRA'sı yükleyicide **tek başına**, tetiği prompt'un **önünde** — Queen Editor'ün bir kareyi çizdiği
gibi. Hangi dosya neden iniyor: [indirilecekler.md](indirilecekler.md).

Adaylar Civitai API'sinden, 27 Ekim. Seçim ölçüsü: Nova ve DaSiWa'nın tabanı Illustrious'a uyum,
yenilik, indirme sayısı; tek bir karakter ya da çizim tarzı değil, genel bir kavram. **Tetik:** sayfanın
eğitim sözcükleri, kare kendisi söylediği için sayılar (`1boy`, `1futa`, `2girls`) ve beden ya da eylem
etiketleri çıkarılarak. **Güç:** sayfanın önerdiği; önermeyende 1,0 (yükleyicinin kendi değeri). Yüz ya da
çizim tarzı LoRA'ya kayarsa 0,7'yi de dene.

## Femboy adayları

| | LoRA | Sürüm | Taban | İndirme | Güç | Tetik | Workflow |
|---|---|---|---|---|---|---|---|
| A | [femboysXL](https://civitai.com/models/289006) | v1.0 (324974), şubat 2024 | SDXL 1.0 — Animagine XL 3.0'da eğitilmiş | 13.573 | 1,0 | `otoko no ko, crossdressing, trap, androgynous` | `femboysXL_v1` |
| B | [Femboy illustrious](https://civitai.com/models/1738161) | v1.3 (2693790), mart 2026 | Illustrious | 6.137 | 1,0 | `Fboy` | `femboy_illustrious_v1_3` |
| C | [Femboy, Sissy, Feminine Male, Fuckboy (new ToS tags)](https://civitai.com/models/1922853) | IL (2176350), eylül 2025 | Illustrious | 2.552 | 1,0 | `1femboy, lean male chest, feminine male` | `femboy_new_tos_il` |

Aramalar: "femboy", "otoko no ko", "trap", "crossdressing", indirme sayısına göre.

- **A — femboysXL:** senin adını verdiğin aday; Civitai'deki en çok indirilen femboy LoRA'sı. Ama en
  eskisi, ve Illustrious'ta değil Animagine XL 3.0'da eğitilmiş (dosyanın kendi header'ı). İkisi de SDXL,
  yani yüklenir; Nova ve DaSiWa'da ne kadar tuttuğunu bu deneme gösterecek. Aynı yazarın "MULTI-LoRA" iki
  sürümü (128 ve 64 dim) birlikte kullanılmak için; tek dosyalık 92 dim'lik olan alındı.
- **B — Femboy illustrious:** Illustrious tabanlı femboy LoRA'larının en çok indirileni ve en yeni
  sürümü olan. v1.3'ün sayfası tetik yazmıyor; v1.2 ve V1 `Fboy` diyor. Defterin 4. bölümü dosyanın
  kendi eğitim etiketlerini basar — orada başka bir sözcük öne çıkarsa tetiği ona çevir.
- **C — Femboy, Sissy, Feminine Male:** Illustrious'ta ikinci en çok indirilen genel femboy kavramı.
  Tetiği sayfasındaki tek satır.

Seçilmeyenler: Curvy Femboy (1.534) tek bir beden tipi; Femboy Doujinshi Mix (1.878) bir çizim tarzı;
Femboys (1.623) yazarına göre Illustrious'ta denenmemiş; `男の娘、ふたなり` femboy'u futanari'yle
birlikte öğretiyor (futa'da aşağıda).

## Futa adayları

| | LoRA | Sürüm | Taban | İndirme | Güç | Tetik | Workflow |
|---|---|---|---|---|---|---|---|
| D | [Flaccid Futa](https://civitai.com/models/2063309) | v3.0 IL (2698395), şubat 2026 | Illustrious | 3.358 | **0,6** *(sayfa: 0,4 – 0,8)* | `flaccid futa` | `futa_flaccid_v3` |
| E | [Futa on Female](https://civitai.com/models/1107758) | Illustrious v2 (1457484), şubat 2025 | Illustrious | 9.850 | 1,0 | `futa with female` | `futa_on_female_il_v2` |
| F | [Futa on Male / Futa with Male / Futadom 2](https://civitai.com/models/891832) | Illustrious v2 (2066157), ağustos 2025 | Illustrious | 12.743 | 1,0 | `futa on male, futa with male, futanari` | `futa_on_male_il_v2` |

Aramalar: "futanari", "futa", "dickgirl", "newhalf", "shemale", "1futa", "futa girl", "futa on female",
indirme sayısına göre, Illustrious sürümü olanlar. İndirme sayısı modelin bütün sürümlerinin toplamı;
E ve F'nin Pony sürümleri de var (Illustrious sürümlerinin kendi sayısı 3.757 ve 5.377).

- **D — Flaccid Futa:** futa'nın **bedeni**, bir eylem değil: üçünün tek bu yüzden her kareye uyabilen.
  En yenisi; v3.0 yazarına göre *"nötr bir tarza yeniden eğitildi, stilize checkpoint'lerle daha iyi
  çalışır"* — Nova ve DaSiWa böyle. Güç önerisi olan tek sayfa: 0,4 – 0,8; ortadan, 0,6'dan açılır.
  Penis boyunu sayfaya göre `big penis` … `gigantic penis` etiketleri ve güç değiştiriyor.
- **E — Futa on Female:** Illustrious'ta bir kadınla futa kavramlarının en çok indirileni.
- **F — Futa on Male / Futadom 2:** Illustrious'ta futa LoRA'larının en çok indirileni; bir erkekle.

**E ve F eylem LoRA'ları**, beden değil: sayfalarındaki eğitim satırları bir partnerle sahneler (`sex`,
`sex from behind`, `blowjob`, …). Illustrious'ta genel bir futa beden kavramı az; D'den sonra en çok
indirilenler bu ikisi. Bu yüzden üç futa adayı da iki kare çizer: tek kişilik **Kare G** — D'nin
ölçüsü; E ve F'de tetik bir partner adlandırıyor ve karede kimse yok, partner ekleyerek mi çiziyorlar,
partnersiz bir karede kullanılabilirler mi — ve partnerli **Kare H**, E ile F'nin eğitildiği şey.

Seçilmeyenler:
- `男の娘、ふたなり/otoko no ko, futanari` ([ILL v2.0](https://civitai.com/models/1406052), 2.418; mart
  2025): güç önerisi 1,0 olan bir beden kavramı, ama tetiği `otoko no ko, futanari` iki ayrı şeyi —
  erkek bir femboy'u ve penisli bir kadını — tek LoRA'da öğretiyor; bir futa karesini femboy'a,
  bir femboy karesini futa'ya çekebilir. İki grupta da ayrı birer aday daha net.
- Shemale Form (v2.0, haziran 2026): yeni bir beden kavramı ama 417 indirme.
- Overstuffed Futanari Bottoms, Futa Tent, Futa Skirt Peak, Horse cock futanari, … (4.000 – 16.000):
  tek bir ayrıntıya (şişkinlik, eteğin kalkması, penis biçimi) bakıyorlar.
- VariVi's Futanari Styles, Futanari no Elf Style ve doujin tarzları: çizim tarzı.
- "Futanari, Ahegao and Lesbian Sex Style Concept": tarzla eylem bir arada, tetiği yok.
- En çok indirilen futa LoRA'larının çoğu (Futanari Horse Penis, big futanari penis, Realistic Futanari, …)
  SD 1.5 ya da Pony, ya da en yeni sürümleri Anima: Nova ve DaSiWa'ya yüklenmez ya da başka bir tabana
  eğitilmiş.

## Çalıştırma

1. Colab 🔑 Secrets'ta **`CIVITAI_COOKIE`** olsun (zorunlu): civitai.red → giriş → F12 → Application →
   Cookies → `__Secure-civ-token`, değere çift tıkla → Ctrl+A → Ctrl+C. `GITHUB_TOKEN` isteğe bağlı —
   queen-editor'ün defterinin sırrı; repo açıkken gerekmez.
2. Defteri Colab'a yükle (**File → Upload notebook**), **Runtime → Change runtime type → T4** (yeter;
   A100 daha hızlı), **Run all**. ~15,9 GB iner. 4. bölümün sonundaki eğitim etiketlerine bak (B'nin
   tetiği için). En alttaki linke gir.
3. Sol kenarda **Workflows** → altı aday, adları yukarıdaki tablolarda. Her biri Nova'yla ve grubunun
   karesiyle açılır — femboy'lar Kare F, futa'lar Kare G → **Run** (Ctrl+Enter).
4. Sonra her workflow'da:
   - **Checkpoint:** `Load Checkpoint`'te `nova3DCGXL_ilV90` ↔ `DasiwaIllustriousAnime_epitaphecstasy`.
   - **Prompt:** POSITIVE kutusuna aşağıdaki karelerden birini yapıştır — futa'larda **Kare H**'yi de —
     **önüne adayın tetiğini ve bir virgül** koy; Queen Editor öyle gönderiyor.
   - **LoRA'sız:** Power Lora Loader'da adayın satırını kapat; Queen Editor'deki **Boş**.
   - **Seed** hepsinde `20261027`: aynı kare, yalnız LoRA farklı. Değiştirirsen hepsinde aynı yap.

Boyut (1024 × 1536), 28 adım, cfg 6 ve FaceDetailer Queen Editor'deki gibi; dokunma.

**Negatif tek fark.** Queen Editor grafiğin kendi negatifini hiç kullanmaz: panelin negatif kutusuna
yazılanı yazar — proje başına saklanır, boşsa boş gider. Örnek senaryonun bir negatifi yok, bu yüzden
deneme grafiğin kendi negatifiyle çizer (`bad quality, worst quality, …`). Kendi projendeki negatifle
görmek istersen onu NEGATIVE kutusuna yapıştır, hepsinde aynısını.

## Ne karşılaştırılır

Her aday için, Nova'da ve DaSiWa'da:
- femboy'lar: **Kare F, Kare 1, Kare 3** — aday başına 6, üçünde 18 resim;
- futa'lar: **Kare G, Kare H, Kare 1, Kare 3** — aday başına 8, üçünde 24 resim.

Bir de F, G ve H'yi LoRA'sız, iki checkpoint'te (6 resim): LoRA'nın ne kattığını o gösterir; Illustrious
`femboy` ve `futanari` etiketlerini LoRA'sız da biliyor. **Toplam 48 resim.**

- **Kare F** *(femboy)*: femboy gibi duruyor mu — erkek bedeni, kadınsı yüz ve giyim; anatomi bozuk mu;
  Nova'nın 3DCG'si ve DaSiWa'nın animesi korunuyor mu, yoksa LoRA kendi tarzını mı getiriyor.
- **Kare G** *(futa, yalnız)*: futa gibi duruyor mu — kadın bedeni ve yüzü, penis; anatomi; tarz
  korunuyor mu. D'nin asıl karesi. E ve F'de: tek kişilik karede bir partner çıkıyor mu.
- **Kare H** *(futa ve bir erkek, yatakta)*: iki beden doğru mu ve kimin kim olduğu ayrı mı kalıyor; futa
  futa, erkek erkek mi. F'nin eğitildiği eşleşme bu; E bir kadınla eğitildi — erkeği kadına mı
  çeviriyor, yoksa onu olduğu gibi mi bırakıyor, bu da E'nin sonucu.
- **Kare 1** *(kadın, yalnız)*: o grubu istemeyen bir karede LoRA'nın ne kadar baskın olduğu — kadın
  femboy'a ya da futa'ya dönüyor mu.
- **Kare 3** *(bir kadın, bir erkek)*: LoRA kareyi paylaşan öteki karakterlere de siniyor mu. E ve F için
  ayrıca: partnerli bir karede eylem LoRA'sı kareyi bir sahneye çekiyor mu.
- **Tetiksiz:** her gruptan seçtiğin adayda tetiği silip F'yi ya da G'yi bir kez daha çiz. Tetik
  gerekmiyorsa QueenAgent'a bir şey gitmez.

**Bana söyleyeceklerin, her grup için ayrı:** hangi aday, hangi güçte; tetik gerekiyor mu; ve karakter
tarifinde ayrıca bir şey gerekiyor mu (ör. `femboy, flat chest` ya da `futanari, penis` yazılmadan
tutmuyor; E ya da F seçilirse: kare bir partner adlandırmadan kullanılamıyor). Seçilen her LoRA Queen
Editor'de Nova ve DaSiWa'nın LoRA kutusuna girer; özel bir prompt gerekiyorsa QueenAgent v12'ye bir madde
açılır.

## Prompt'lar

Kare 1 ve Kare 3 deponun örnek senaryosundan
([docs/arsiv/research/2026-08-18-ornek-yapi.json](../../../docs/arsiv/research/2026-08-18-ornek-yapi.json)),
QueenAgent'ın `build_prompts`'unun yazdığı gibi, `BREAK` dahil — Qwen denemesindekilerin aynısı.
Kare F ve Kare G aynı senaryonun kapı önü karesi (Kare 2), aynı biçimde: F'de kadın karakterin yerine bir
femboy, G'de aynı kadın futanari olarak. Kare H aynı futa ve senaryonun erkek karakteri, Kare 1'in yatak
odasında, çıplak ve sarılıp öpüşürken. Senaryonun karakter satırı `solo` taşıyor (Kare 3'te iki kişiyle
bile); iki kişilik bir karede yanlış olduğu için H'de yok. Hepsinin önüne adayın tetiği gelir.

### Kare F — femboy, kapı önü, tam boy *(femboy workflow'ları bununla açılır)*

```
score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres, 1boy, solo, femboy, young man in his early 20s, androgynous, pale skin, long black hair, green eyes, slim body, flat chest, oversized long black t-shirt, black thong BREAK standing in doorway, door opening, light blush, soft flirty smile, looking at viewer, full body, apartment doorway, daytime, natural light, indoors
```

### Kare G — futa, kapı önü, tam boy *(futa workflow'ları bununla açılır)*

```
score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres, 1girl, solo, futanari, woman in her mid 20s, goth woman, pale skin, long black hair, green eyes, slim body, oversized long black t-shirt, black thong BREAK standing in doorway, door opening, light blush, soft flirty smile, looking at viewer, full body, apartment doorway, daytime, natural light, indoors
```

### Kare H — futa ve bir erkek, yatakta *(futa'larda yapıştır)*

```
score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres, 1girl, futanari, woman in her mid 20s, goth woman, pale skin, long black hair, green eyes, slim body, nude BREAK 1boy, man in his late 20s, short black hair, stubble, athletic build, nude BREAK lying on the bed together, embracing, kissing, medium shot, side view, cozy bedroom, morning light through curtains, indoors
```

### Kare 1 — yatak odası, mektup

```
score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres, 1girl, solo, woman in her mid 20s, goth woman, pale skin, long black hair, green eyes, slim body, white nightgown, lace trim, bare shoulders BREAK sitting on the edge of the bed, holding a letter, pensive expression, medium shot, from slightly above, cozy bedroom, morning light through curtains, indoors
```

### Kare 3 — iki karakter

```
score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres, 1girl, solo, woman in her mid 20s, goth woman, pale skin, long black hair, green eyes, slim body, oversized long black t-shirt, black thong, red knit scarf BREAK 1boy, man in his late 20s, short black hair, stubble, athletic build, dark grey suit, white shirt, no tie BREAK handing over a small package, fingers touching, surprised expressions, medium shot, side view, apartment doorway, daytime, natural light, indoors
```

## Not

Hiçbir aday Nova ya da DaSiWa üstünde denenmiş olarak yazılmamış; sayfalardaki örnek resimlerin
üretim bilgisi Civitai'de girişsiz okunmuyor, yani hangi checkpoint ve güçle çizildikleri bilinmiyor.
