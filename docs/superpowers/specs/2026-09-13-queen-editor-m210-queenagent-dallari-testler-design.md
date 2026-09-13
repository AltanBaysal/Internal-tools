# Madde 210 · QueenAgent'ın dalları — test turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Öncesi:** [sürüm kaydı, test turu](2026-09-11-queen-editor-m210-surum-kaydi-testler-design.md) ·
[uygulama turu](2026-09-11-queen-editor-m210-surum-kaydi-uygulama-design.md)

## Neden bir tur daha

210 queen-editor'ün kaydını düzeltip kapanacaktı. Kapanmadan önce kullanıcı *"bu değişikliklerden
kırılan bir şey var mı"* diye sordu; bakınca kırılan bir şey çıkmadı — dört takım yeşil, yok olan 21
yolun hiçbirine atıf kalmamış — ama **bu koşunun yol haritasına yazdığım bir cümle yanlıştı**:
*"QueenAgent tarafında hiç kaymamış."* Kaymış. Cümle dört dala bakıp sekizi hakkında konuşuyordu.

Kullanıcı kararı *(13 Eylül)*: **backlog'a yazma, düzelt.** Gerekçesi maddenin kendi tanımı — 210
sürüm kaydının temizlenmesi, ve kaydın yarısını erteleyip maddeyi kapatmak onu bitirmek olmaz.

## Bakınca ne çıktı

Sekiz QueenAgent belgesinin dalları, başlıklarından ve `git branch`'ten:

| Yol haritası | Başlığının verdiği dal | Durum |
|---|---|---|
| v1 | `feat/mira-v1` | tek |
| v2 | `fix/mira` | **v3 ile aynı** |
| v3 | `fix/mira` | **v2 ile aynı** |
| v4 | `feat/queenagent-colab` | tek |
| v5 | `feat/queenagent-v5` *(+ `feat/queenagent-m123-skill-rewrite`)* | tek |
| v6 | `feat/v6` | tek |
| v7 | `feat/queenagent-v7` | tek |
| v8 | **hiç** | `feat/queenagent-v8` var, `356d605` ile merge |

**Üç kusur, ve kusur sandığım iki şey.**

1. **v2 ile v3 tek dalın iki belgesi.** v3 bunu kendi ağzıyla söylüyor: *"Numaralar v2'den devam
   eder"*, ve dal satırı da `fix/mira`. queen-editor'de on üç belgeyi dört dala dağıtan hastalığın
   aynısı, daha küçük ölçekte.
2. **v8 başlığında hiçbir dal adı yok.** Dal duruyor ve merge edilmiş; yazılmamış olan kayıt.
3. **v7 iki dala yayıldı, başlığı birini yazıyor.** 180–182 maddeleri `feat/queenagent-v7.5`'te
   koşuldu ve metinleri v7'nin yol haritasında duruyor. v5 aynı durumu doğru yazmış
   *(`feat/queenagent-m123-skill-rewrite`, 124–132)*; v7 yazmamış.

Kusur **olmayan** ikisi, çünkü ikisi de tek yol haritalı tek dal: `feat/queenagent-colab` numara
taşımıyor, `feat/v6` tool adı taşımıyor. Dal adı tarihî bir olgudur — geçmişe dönük düzeltilemez, ve
düzeltilmesi de gerekmiyor: kayıt dalın adından değil, belgenin dalını söylemesinden doğuyor.
`feat/queenagent-v7.5` de kayıp bir sürüm değil, v7'nin ikinci dalı.

## Çivilenecek üç olgu

Bugünkü `test_the_name_says_the_branch_the_roadmap_ran_on` yalnız `feat/queen-editor-v(\d+)` arıyor,
yani **tek tool'a kilitli** — QueenAgent'ın dördü tam o boşlukta duruyordu. Yerine üç çivi geliyor ve
üçü de **her iki tool'un** belgelerine bakıyor:

| # | Ne tutuyor | Bugün |
|---|---|---|
| 1 | Her yol haritası başlığında bir dal adı veriyor | **kırmızı** — v8 vermiyor |
| 2 | Hiçbir dalı iki yol haritası sahiplenmiyor | **kırmızı** — `fix/mira` ikide |
| 3 | Dal adı bir sürüm numarası taşıyorsa, belgenin numarasıyla aynı | yeşil, ve genişliyor |

Üçüncüsü eskinin yerini alıyor: eski çivi queen-editor'ün dal adlarının numara taşımasına
yaslanıyordu, yenisi numara taşıyan her dal adına bakıyor — `feat/mira-v1`, `feat/v6`,
`feat/queenagent-v5` dahil. Numara taşımayanlar *(`fix/mira`, `feat/queenagent-colab`)* muaf, çünkü
söyleyecek numaraları yok; onları 2 numaralı çivi tutuyor.

## Dal başlıktan nasıl okunacak

İki tuzak var ve ikisi de yanlış kırmızı üretirdi:

- **İlk backtick'li dal, dalın kendisi değil.** queen-agent v1'in 5. satırında `fix/mira` geçiyor —
  13 Eylül'de eklenen, adın neden değiştiğini anlatan notun içinde. Asıl dal 12. satırda. Satır
  sırasına bakan bir okuma onu `fix/mira` sanar ve v2/v3 ile sahte bir çakışma üretir.
- **Birleştirilmiş belgeler etiketi tekrar eder.** queen-editor v3'ün içinde dokuz `**Koşu dalı:**`
  var, her *Koşu N* bölümünde bir tane. Hepsini toplamak bir belgeye dokuz dal yazdırır.

O yüzden okuma **etiketten** gider: dosyadaki **ilk** `**Branch:**` / `**Dal:**` / `**Koşu dalı:**`
satırı belgenin kendi başlığıdır, ve o satırdaki **ilk** backtick'li `feat/…` ya da `fix/…` belgenin
dalıdır. Üç etiketin üçü de kabul ediliyor çünkü üçü de kullanımda; hangisinin yazıldığı değil,
hangi dalın söylendiği soruluyor.

Aynı satırda ikinci bir dal geçebilir ve iki sebebi olur — *"şunun üzerinden açıldı"*
*(queen-agent v1: `feat/queen-editor-v2`)* ya da sürümün gerçekten yayıldığı ikinci dal
*(queen-agent v5)*. İkisi ayırt edilmiyor, ikisi de **sahiplenme sayılmıyor**: yalnız ilk dal
belgenindir. Bu, açıldığı dalı yazan bir belgenin başka bir belgeyle sahte çakışma üretmesini de
önlüyor.

## Neyin çivisi yok, ve neden

**v7'nin ikinci dalı.** Bir sürümün kaç dala yayıldığını tutmak, deponun metnini değil `git`'in
referanslarını okumak demek. Bunlar klondan klona değişiyor — bu depoda `feat/queenagent-v7.5`
yalnız `origin/` altında duruyor, remote'suz bir klonda hiç durmuyor — yani çivi ortama göre
kırmızı/yeşil olurdu. Kusur uygulama turunda düzeliyor, ama tutanı **2 numaralı çivi**: ikinci dal
yazıldığı anda birinci dalın sahipliği değişmiyor, ve o dal başka bir belgede geçerse çakışma
görünür.

## Bu turda değişen

Yalnız [test_version_record.py](../../../queen-editor/backend/tests/test_version_record.py). Belgelere
dokunulmuyor — v2/v3 birleşmesi, v8'in dal satırı ve v7'nin ikinci dalı **uygulama turunun** işi.
Testler kırmızı commit'leniyor.

Dosya queen-editor'ün süitinde kalıyor, adı da öyle. Sorusu büyüdü *(artık iki tool'un kaydını
soruyor)* ama sorunun çıktığı yer burası, ve `queen-agent` tarafına ikinci bir kopya koymak aynı
olguyu iki yerden tutmak olurdu — biri değişince öteki eskir.
