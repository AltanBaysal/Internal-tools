# Madde 94 — Tek skill kalır, beşi silinir · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası, Blok 5, Madde 94](../plans/2026-08-25-queenagent-v5-roadmap.md)
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz.

---

## İki açık soru burada kapanıyor

Yol haritası 94'e iki soru bırakmıştı. İkisi de bu spec'te kapanıyor, çünkü ikisi de 94'ün ne
sildiğini belirliyor.

### 1. v5'in 74'ü ile bu koşunun 94'ü

**94 devralıyor.** 74 *"hangi skiller düşecek"* diye açık bir soru soruyordu; 94 o sorunun cevabını
taşıyor — kullanıcı kararı, 26 Ağustos: prompt+ dışında hepsi. Bir karar, kendisini soran soruyu
kapatır; tersi olmaz. 74'ün şartlarından biri olan 75 *(prompt dili)* da düşüyor: dil sorusu tek
metnin içinde zaten cevaplı — yapı dosyası İngilizce, çünkü onu bir görsel modeli okuyor.

v5 yol haritasına bunu söyleyen bir satır giriyor. 74 silinmiyor: numaralar kaymıyor ve yazılmış
spec'ler onlara atıf yapıyor.

### 2. Kaybolan bilgiden ne nereye taşınıyor

**Hiçbiri taşınmıyor** *(kullanıcı kararı, 27 Ağustos — sunulan iki seçenekten ikincisi)*. Kalan
metin bugünkü hâliyle kalıyor; silme gerçekten siliyor. Yol haritası iki uçtan da sakınmayı
istiyordu — hepsini taşımak silmeyi anlamsız kılar, hiçbirini taşımamak modeli her seferinde
yeniden icat etmeye bırakır. İkinci uca düşmediğimizi gösteren şey, kaybın tek tek sayılması:

| Silinen metindeki bilgi | Nereye gitti |
|---|---|
| Bir kare bir-iki cümledir, paragraf değildir | **Gerçekten gidiyor.** Tek akışta ayrı bir kare listesi belgesi yok; kare, yapı dosyasında `action` ve `camera` alanları olan bir nesne, ve kalan metin şemayı gösteriyor |
| Kare listesi kullanıcının dilinde yazılır | **Gerçekten gidiyor** — yazılacak bir kare listesi dosyası kalmıyor. Tersi duruyor: kalan metin *"Everything in this file is English -- an image model reads it"* diyor |
| Karakter adayları yapının haritalarıyla aynı biçimde bir JSON dosyasına yazılır | **Ayrı dosya gidiyor**, biçim kalıyor: yapının `characters` / `outfits` haritaları zaten o biçim ve kalan metin onları gösteriyor |
| Kaç aday yazılacağı kullanıcının kararıdır, söylemediyse sorulur | **Tabanda** — 73 koydu: *"Ask rather than invent... a count, a name, a choice between two readings"* |
| Kimlik giysi taşımaz, giysi `outfits`'e gider | **Kalan metinde zaten var** |
| Uzun iş partiler hâlinde yazılır, her parti bir sonrakinden önce diske iner | **Tabanda** — 73 koydu; kalan metin kendi somut ölçüsünü *(beşerli partiler)* koruyor |
| Sohbetteki düzeltme dosyaya da iner | **Tabanda** — 73 koydu |
| Dosya konusuna göre adlandırılır | **Kalan metinde zaten var** (`intro-frames.json`) |
| *"Dosyalarımı denetle"* diye bir yol | **Gerçekten gidiyor**, bilerek. Kural kitabı duruyor ve her kurmadan önce uygulanıyor; ayrı bir denetim yolu kalmıyor |
| Promptları elle yazan yol | **Gerçekten gidiyor**, bilerek. Yapıdan kuran yolla aynı işi yapıyordu ve karakteri kopyaladığı için FOUNDATION 5 ile çarpışıyordu |

Yani taşınacak bir şey yok, çünkü taşınmaya değer olanın hepsi 73'ten sonra zaten iki yerden birinde
duruyor. Gerçekten giden dört şey var, ve dördü de bilerek gidiyor.

**Bilinen risk, açıkça:** skill seçilmeden *"senaryoyu karelere böl"* denince model yalnız tabanla
çalışır, ve karenin ne olduğunu her seferinde yeniden kurar. Seçenek 2'nin kabul edilen bedeli bu.
Ölçülüp geri gelmesi gerekirse, geri gelmesi gereken yer kalan metnin içidir — taban değil.

## Yol haritasında düzelecek iki cümle

94'ün *"nasıl görülür"* satırı iki yerde bugünkü karara uymuyor, ve bu spec'le birlikte düzeliyor:

- *"seçilecek bir skill listesi yok"* — seçici kalıyor, tek satırla. Bunu maddenin kendi *"Seçici
  kalıyor"* maddesi zaten söylüyordu; iki cümle birbiriyle çelişiyordu.
- *"bir senaryodan prompt listesine kadar olan yol tek bir metinle yürüyor"* — seçenek 2'de yol
  **taban artı tek metinle** yürüyor, ve metni olan yalnız son ayak.

## Ne siliniyor

**Arka uç** `domain/skills.py` — beş metin ve `INSTRUCTIONS`'taki beş satır:
`create-scenario`, `create-character-prompt`, `split-into-frames`, `generate-prompts`,
`verify-prompts`. `GENERATE_PROMPTS_PLUS` **tek kelimesi değişmeden** kalıyor. `RULEBOOK` kalıyor,
ama artık tek okuyucusu var.

**Ön yüz** `features/workspace/skills.js` — `SKILLS` beş satırını bırakıyor, biri kalıyor.

Seçicinin kendisi, `skill` alanı, kaydın `skill`'i, `instruction_for`'un bilinmeyen ada boş cevabı:
hiçbiri değişmiyor.

## Testler nasıl kırmızı olur

Bir silmenin kanıtı çoğunlukla **yokluk**, ve yokluğu ancak onu arayan bir test görür.

### `backend/tests/test_skills.py`

Dosya, bittiğinde son hâli tarif ediyor: silinen beşin testleri bu turda gidiyor, ve yerlerine
silmeyi arayanlar geliyor. Bir test ile konusu aynı belgede doğar; konusu olmayan test kalmaz.

| Test | Ölçü | Bugün |
|---|---|---|
| `test_a_deleted_skill_carries_nothing` × 5 | `instruction_for(<ad>) == ""` | **kırmızı** — beşi de metin taşıyor |
| `test_only_one_skill_is_offered` | `list(INSTRUCTIONS) == ["generate-prompts-plus"]` | **kırmızı** — altı |
| `test_the_rulebook_has_one_reader_now` | kural kitabını taşıyan tek skill | **kırmızı** — verify de taşıyor |

`ALL_SKILLS` tek satıra iniyor. Kalanlar — kural kitabının içeriği, yapılı metnin şeması, adı
bilinmeyen skill, yeniden adlandırmadan önceki adlar, hiçbir metnin kareye *shot* dememesi —
olduğu gibi duruyor ve yeşil kalıyor.

**Silinen testler:** beş metnin kendi testleri *(senaryo, karakter, kare listesi, düz prompt,
denetim)*, `test_verify_is_the_one_skill_that_writes_nothing`, ve
`test_the_rulebook_is_one_text_with_two_readers` — yerine yukarıdaki tek okuyucu testi geçiyor.

### `frontend/src/features/workspace/skills.test.js`

| Test | Ölçü | Bugün |
|---|---|---|
| `the one skill left is the one that builds` | `SKILLS.map(id)` tek elemanlı | **kırmızı** — altı |

Satıra özel testler *(senaryo satırı, denetim satırı, bölme satırı, dosya yazan satırlar)* gidiyor.
Her satırın ne yaptığını söylediği, adın etiket olduğu, seçilmemiş hâlin düğmenin kendi kelimesi
olduğu duruyor.

### Ölçü değişen, iddiası değişmeyen testler

Bunlar bugün de yarın da yeşil. Yalnız kullandıkları skill adı kalan skille değişiyor, çünkü
silinen bir ad artık boş yönerge döndürür ve testin iddiası ada değil davranışa bakıyor.

- `backend/tests/test_stream_answer.py` — yönergenin sonda durduğu, tur ilerledikçe sonda kaldığı,
  en yeni mesajın skill'inin geçerli olduğu, yönergenin kayda yazılmadığı.
- `backend/tests/test_chats_api.py` — bestecinin gönderdiği skill'in modele system bloğu olarak
  ulaştığı.

*"En yeni mesajın skill'i geçerlidir"* testi bugün iki ayrı skill kullanıyor; tek skill kalınca iki
değeri **skill'li ve skill'siz** olarak alıyor. İddia aynı: en sonuncusu karar veriyor.

`ChatScreen.test.jsx`'in *"canlı seçim kaydın alanını yener"* testi de aynı şekilde iki değere
ihtiyaç duyuyor, ve aynı şekilde alıyor.

**Değişmeyen ölçüler:** `test_append_message.py`, `test_file_chat_store.py` ve
`test_chats_api.py`'nin kayıt testleri silinen adları **opak dizge** olarak kullanıyor —
`instruction_for` çağırmıyorlar. Onlar olduğu gibi kalıyor, ve kalması doğru: artık gerçekten
kimsenin tanımadığı bir adı taşıyan eski bir kayıt oluyorlar.

## Beklenen kırmızı

**Arka uç 7, ön yüz 2.** Dokuz — sayım [planda](../plans/2026-08-27-queenagent-m94-test-plan.md).

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Nasıl görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

`dist` bu turda derlenmiyor: ön yüz kaynağı yalnız testte değişiyor.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `skills.py` ve `skills.js` bu turda açılmaz.
- **`prompt.py` açılmaz** — 73 bitti, taban olduğu gibi kalıyor.
- **Seçici sökülmez** — kullanıcı kararı, 26 Ağustos.
- **Eski spec'ler ve planlar düzeltilmez** — silinen adları anan belgeler o günün kaydı.
- **`docs/2026-08-26-queenagent-ai-yolu-haritasi.md`** çalışma ağacında duruyor ve kullanıcının
  kendi işi; bu madde ona dokunmuyor.
