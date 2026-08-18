# Madde 28 — Tool katmanı · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m28-tool-katmani-design.md](../specs/2026-08-18-queenagent-m28-tool-katmani-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Madde tek uçlu (yalnız arka uç): **bir tur**, önce yalnız testler (kırmızı gider), sonra uygulama.

---

## Adım 1 — Testler (kırmızı commit)

### yeni `test_build_prompts.py` — saf birleştirme, store yok

- Sıra: tek karede `quality → characters → location → action → camera`.
- Aynı karakter iki karede **birebir aynı** metinle geçer; map'teki tek değeri değiştirmek ikisini
  birden döndürür.
- Bir karede iki karakter, karedeki sırasıyla.
- Karaktersiz kare, mekânsız kare, `quality`'siz yapı — üçü de üretir, boş alan yok sayılır.
- Uçlardaki virgül ve boşluk normalize edilir; `", ,"` çıkmaz.
- `solo` / sayı etiketine dokunulmaz — iki karakterli karede `1girl, solo` iki kez geçer *(kapsam
  dışı olduğunun kanıtı)*.
- Bilinmeyen karakter: hata cümlesi **kare numarasını**, **adı** ve **o map'te bilinenleri** taşır;
  mekân adları karakter listesine karışmaz.
- Bilinmeyen mekân: aynı biçim.
- İki ayrı karedeki iki eksik **tek hatada** toplanır.
- `shots` boş ya da yok → `BadStructure`.
- `PROMPTS` metni: üç tırnak, girintili satırlar, trailing comma; **ayrıştırılabilir Python** ve
  değerleri beklenen liste.
- İçinde üç tırnak / ters bölü geçen bir prompt yine ayrıştırılabilir dosya verir.

### `test_tools.py` — kabuk

- `edit_file`: tek eşleşme değişir, gerisi aynı kalır; dönen cümle dosyanın adını anar.
- `edit_file`: olmayan dosya · boş `old` · bulunamayan `old` · **iki kez** geçen `old` (kaç kez
  geçtiğini söyler) — dördünde de dosya **değişmez**.
- `edit_file` boş `new` ile siler.
- `edit_file` **dosya doğurmaz** (`created is None`).
- `build_prompts`: yapı dosyasından `<gövde>.py` doğar, adını döner, kaç prompt yazdığını söyler.
- `build_prompts` ikinci çağrıda **üstüne yazar** — numaralamaz, dosya sayısı artmaz.
- `build_prompts`: olmayan dosya · geçersiz JSON (**ayrıştırıcının kendi cümlesi** geçer) ·
  bilinmeyen ad → hiçbir dosya yazılmaz.
- Kaynağın adı `.py` ile bitiyorsa reddedilir; kaynak dosya bozulmaz.
- `TOOL_SPECS` beş aracı bildirir.

### `test_stream_answer.py`

- `build_prompts` dashed kartı yükseltir ve doğan dosyayı yayınlar; `edit_file` **hiçbirini**
  yapmaz.
- Aynı turda iki kez doğan ad, mesajın dosya listesinde **bir kez** durur.
- `MAX_ROUNDS` **16**'ya sabitlenir *(`test_tools.py`'de; mevcut sınır testi sayıyı sabitten okuduğu
  için kendiliğinden uyar)*.

---

## Adım 2 — Uygulama

`domain/errors.py` (`BadStructure`) · yeni `domain/build_prompts.py` · `domain/tools.py`
(iki spec, iki dal, `MAX_ROUNDS`, çıktı adı kuralı) · `domain/usecases/stream_answer.py`
(dosya doğuran araçların kümesi, tekilleştirme).

---

## Kapanış denetimi

- `build_prompts.py` hiçbir store'a bakmıyor (`grep file_store` boş).
- Ön uçta ve `presentation/`de değişiklik yok.
- Yönerge metni yok: `prompt.py` bu maddede **değişmiyor** — beceriler Madde 29/30.

## Risk

Yok denecek kadar az: her şey saf ve sınanabilir. Tek gözle görülecek şey `MAX_ROUNDS`'un yeni
sayısının gerçekten yettiği — Madde 30'un uzun zinciri koştuğunda belli olur.
