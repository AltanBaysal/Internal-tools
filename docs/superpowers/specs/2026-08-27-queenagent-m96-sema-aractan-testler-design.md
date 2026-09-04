# Madde 96 — Şema ve kural kitabı araçtan gelir · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 96 ·
**Kararları:** [karar defteri](../research/2026-08-27-queenagent-skill-kararlari.md) K27, K28 ·
**Şartı:** Madde 95 — şemanın anlattığı `people` alanını kod zaten yerleştiriyor *(`1e11e78`)*
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

Yapı dosyasının şeması `GENERATE_PROMPTS_PLUS` metninin ortasında duruyor: örnek JSON, hangi
haritanın ne tuttuğu, karenin karakter alanının biçimi. Kural kitabı da onun sonuna gömülü.

Metin her turda modele gidiyor — Madde 93'ten beri isteğin en sonunda, ve her turda yeniden
işleniyor. Oysa şema yalnız **yazma anında** lazım: bir sohbetin çoğu turunda dosya yazılmıyor.

Bir de ikinci okuyucu geliyor: Madde 101'in akış skill'i de yapı dosyasını yazacak. Şema metinde
kalırsa iki metne birden kopyalanır, ve kural kitabının dördüncü maddesi tam olarak bunu yasaklıyor.

## Ne olur

Şema ile kural kitabı kendi yerine iner ve **çağrılınca** gelir: `read_schema`.

- Araç **hiçbir şey almıyor** — dosya adı yok, parametre yok. Tek bir metin döndürüyor.
- Metin ikisini birden taşıyor: yapının biçimi, ve kurmadan önce tutulacak kurallar *(K28)*.
- Araç **her kipte** elde. Okuyan bir araç, ve okumanın izne bağlanmadığı yer bugün de öyle.
- Dosya yaratmıyor: sohbete kart düşmüyor.

`GENERATE_PROMPTS_PLUS` şemayı ve kural kitabını kaybediyor, yerine bir cümle alıyor: yazmadan
önce şemayı oku. Metnin geri kalanı — iskeleti önce yazmak, kareleri beşerli eklemek, promptu elle
kurmamak — olduğu gibi duruyor.

## Kural kitabı altıncı maddesini alıyor

*(K27)* Kişi sayısı ya da tek başınalık bir karakterin kendi tanımındaysa yanlış yerde; yeri karenin
`people` alanı. Kod bunu ayıklamıyor — ayıklasaydı bilerek yazılmış bir etiketi de sessizce silerdi,
ve hangi etiketin sayı olduğunu ancak hiç tamamlanmayan bir adlar listesiyle tahmin edebilirdi.

## Şema `people`'ı ve ana karakteri anlatıyor

Madde 95 kodu yerine oturttu; bu madde onu **söyleyen** yeri getiriyor:

- Sayı karenin kendi alanında, tek karakterli karede bile *(K25)*.
- Karenin karakter listesinde **en öne yazılan** isim promptu açan kişidir *(K1)* — ayrı bir alan
  yok, sıra bilgiyi taşıyor.

## Kırmızıya dönecek testler

**Yeni dosya — `test_schema.py`**

Bugün `test_skills.py`'de duran sekiz iddia buraya taşınıyor *(alanların şemada olması, karenin
karakter haritası, neyin nereye ait olduğu, dosyanın adı, adı taşıyıp metni taşımaması, ve kural
kitabının üç iddiası)*. Taşınırken iddiaları değişmiyor, yalnız baktıkları yer değişiyor.

Yanlarına dört yeni iddia giriyor:

1. Şema `people` alanını da gösteriyor.
2. Şema en öne yazılan ismin promptu açtığını söylüyor.
3. Şema sayının karakterin tanımında değil karenin alanında olduğunu söylüyor.
4. Kural kitabının altıncı maddesi var, ve sayı ile tek başınalıktan söz ediyor.

Bir de aracın döndürdüğü metnin ikisini birden taşıdığı, ve hiçbir yerde `shot` demediği.

**`test_tools.py`**

5. `read_schema` modele tanıtılan araçlar arasında — bugünkü küme testi yedinci adı bekliyor.
6. Çağrıldığında şema metnini döndürüyor, ve hiçbir parametre istemiyor.
7. Hiçbir dosya doğurmuyor.
8. Sonucu tek kelimeyle söylüyor.

**`test_modes.py`**

9. Üç kipin üçü de `read_schema`'yı veriyor.

**`test_skills.py`**

10. Metin artık şemayı taşımıyor — alan adları orada değil.
11. Metin artık kural kitabını taşımıyor.
12. Metin şemayı okumayı söylüyor, ve bunu `build_prompts`'tan önce söylüyor.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `build_prompts` | Madde 95 bitirdi; bu madde yalnız metni taşıyor |
| Silinen beş skill'in testleri | 94'ün kaydı, yerinde |
| `write_plan`, `create_file`, `edit_file` | Kendi kiplerinde, kendi kurallarıyla |
| Tur sayısı `MAX_ROUNDS` | Zincire bir okuma ekleniyor ama on altı hâlâ geniş |
| Ön yüz | Bu maddede hiçbir şey değişmiyor, `dist` derlenmiyor |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.
