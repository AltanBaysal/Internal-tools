# Madde 418 — Kutunun ret kontrolü, test turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 418 · v9-3b · **Tur:** 1/2 — yalnız testler.
**Üstüne kurulduğu:** [m416 test turu](2026-10-06-queen-editor-m416-kara-kutu-testler-design.md),
[m416 uygulama turu](2026-10-06-queen-editor-m416-kara-kutu-uygulama-design.md).

**Kullanıcıdan gereken — yok.** Madde 5 Ekim'de hizalandı; kararları yol haritasının *Maddelerin
kararları → v9-3* bölümünde, kullanıcının sözleriyle. Kontrolün DeepSeek'e giden metnini Claude yazar
ve commit'ler, kullanıcı sonra okur *(kullanıcı, 5 Ekim — Claude'un önerisini seçti: "böyle olsun")*.
Ekran değişmez *(kullanıcı — "ui tasarımını sen yapmıyorsun bu mesjaı kullansın")*.

## Kullanıcının sözü

*"kontrol etmeyide deepseeke yaptırıcaz cevap geliyor ya gelen cevabın metnin birebir deepseek
gönder,yirouz kontrol ets,n diye ve onay verirse usera yada agentic flowa gidiyor yoksa tekrardan
istek atıyoru gecene kadar"*; *"Agenta gitmez dediğim kara kutu model red verirse şey dönsün model
hata döndü farklı şekilde dene tarzı gerçekten bir hata varsa teknik no internet veya internal erro
onlarıda direkt önderebilir"* *(5 Ekim)*.

## Bugün ne oluyor

416'nın kutusu *([box.py](../../queen-editor/backend/services/deepseek/box.py))* DeepSeek'ten gelen
ilk düzgün metni olduğu gibi döner. DeepSeek *"I'm sorry, I can't help with that."* derse o da düzgün
bir metin: yazar onu prompt diye karta yazar, ve video modeline gider.

## Kurallar

1. **Gelen metin birebir, ayrı bir istekle kontrol ettirilir** — istemcinin döndüğü metin, kutunun
   çağırana döneceği metnin ta kendisi. Kontrol isteği aynı istemciden gider: sistem mesajı kontrolün
   metni, kullanıcı mesajı yalnız cevabın metni; resim yok.
2. **Yalnız onay geçirir.** Kontrolün metni tek kelime ister: `APPROVED` ya da `REFUSAL`. Kontrolün
   cevabı tam olarak `APPROVED` ise cevap çağırana döner; başka her şey — `REFUSAL`, ya da kontrolün
   kendisinin bir cümlesi — **ret** sayılır *(kullanıcı — "onay verirse … yoksa tekrardan istek
   atıyoruz")*.
3. **Retse asıl istek aynen yeniden gider** — aynı talimat, aynı sözler, aynı resimler.
4. **Kontrol isteğinin kendi hatası** — HTTP hatası, bozuk ya da boş cevap, hiç cevap — da bir deneme
   düşürür, ve asıl istek aynen yeniden gider *(v9-3, Claude'un kararı)*.
5. **Tek sayaç, en çok 5 deneme.** Bir deneme = asıl istek + (gelirse) kontrolü. Hata da ret de aynı
   beşten düşer; yani bir sorunun en çok 10 isteği var.
6. **Beşi de olmazsa kutu yine fırlatmaz, ve son denemenin türü konuşur:** son deneme ret ise metin
   tam olarak *"Model hata döndü, farklı şekilde dene."*; son deneme teknik bir hataysa — asıl isteğin
   ya da kontrolün — o hatanın kendi metni, 416'daki gibi. İkisi de başarısız diye işaretli.
   **Neden son deneme:** kutu zaten son hatanın metnini dönüyor (416); son denemenin türü aynı kuralın
   devamı, ve çağırana en taze durumu söyler. Sayım ya da çoğunluk bir kural daha olurdu.
7. **Ret metni prompt olmaz.** Queen Editor'de başarısız cevap 416'nın yolundan gider: yazar onu
   fırlatır, döngü üç kez dener, ve üçü de olmazsa hata satırında
   `Aynı kare 3 kez denendi — üretim durduruldu` ve altında *"Model hata döndü, farklı şekilde dene."*
   yazar. Karta hiçbir şey yazılmaz, iş borçlu kalır.
8. **Anahtar yoksa** bugünkü gibi: hiçbir istek gitmez, kontrol de; istemcinin cümlesi başarısız döner.
9. **Kontrolün metni bir isteğe verilmiş bir cevaptan söz eder**, video'dan ya da prompt'tan değil:
   QueenAgent v10-1b aynı metni birebir kullanacak.

**Değişmeyen:** yazarlar ve söyledikleri; `Answer`'ın iki alanı; döngü ve `policy.py`; istemci; ekran;
QueenAgent.

## Arayüz — uygulama turunun vereceği

- `backend/services/deepseek/box.py`: `CHECK_INSTRUCTION` — kontrolün DeepSeek'e giden metni,
  İngilizce. `Box.ask(system, text="", images=())` → `Answer` aynen; içinde her düzgün cevabın
  ardından `complete(CHECK_INSTRUCTION, cevap)`.
- `Answer`'a alan eklenmez: ret mi teknik mi diyen alan 419'la gelir.

## Nasıl kanıtlanıyor

416'daki gibi: kutu **gerçek istemciyle**, `test_deepseek_box`'ın `Answers`'ı — sırayla cevap veren,
her isteği not eden sahte HTTP — ile sınanır; kontrol isteği de bu listeden cevabını alır. Böylece
kontrolün gördüğü metin istemcinin döndüğünün ta kendisi. Zincir `test_photo_usecases`'in sahteleri ve
`resume_batch`'le, `main.py` `requests.post` sahteyle değiştirilerek. `CHECK_INSTRUCTION` bugün yok:
testler onu kullandıkları yerde içe aktarır.

## Yazılacak testler

### `backend/tests/test_deepseek_box.py` — 416'nın testleri, kontrolle

416'nın düzgün cevap bekleyen testleri artık kontrolün onayını da bekler: listelerine iyi cevabın
arkasına `APPROVED` girer, ve istek sayıları birer artar. Söyledikleri aynı.

1. **İyi bir cevap kontrol edilince olduğu gibi döner** — ` she turns ` + `APPROVED`: `she turns`,
   `failed` değil, iki istek.
2. – 5. **HTTP hatası, bozuk, boş ve hiç gelmeyen cevap** — her biri, sonra iyi cevap + `APPROVED`: iyi
   cevap döner, üç istek. 2'de ikinci istek ilkinin birebir aynısı.

6, 7, 8 ve 9 aynen kalır: hiçbirinde bir cevap gelmiyor, yani kontrol isteği de yok.

### `backend/tests/test_deepseek_box.py` — yeni testler

10. **Cevap birebir, kendi isteğinde kontrol edilir** — iki bölümlü, çok satırlı bir cevap +
    `APPROVED`: kutu cevabı döner; ikinci isteğin adresi ve başlıkları ilkiyle aynı, gövdesi aynı model,
    sistem mesajı `CHECK_INSTRUCTION`, kullanıcı mesajı yalnız cevabın metni — tek metin parçası,
    resimsiz.
11. **Onaydan başka her şey isteği yeniden gönderir** — parametreli: kontrol `REFUSAL` diyor; kontrol
    kendisi bir cümle söylüyor (`I'm unable to review this content.`). Asıl cevap
    `I'm sorry, I can't help with that.`; sonra iyi cevap + `APPROVED`: `she turns` döner, dört istek,
    üçüncü istek ilkinin birebir aynısı.
12. **Kontrolün kendi hatası da bir deneme, asıl istek yeniden gider** — `she turns`, kontrol `503`;
    sonra `she turns` + `APPROVED`: `she turns` döner, dört istek, üçüncü ilkinin aynısı.
13. **Beşi de retse kutu cümleyi döner, fırlatmadan, on istekten sonra** — beş kez ret + `REFUSAL`,
    arkasında iyi cevap + `APPROVED` bekliyor: tam on istek; `failed`; metin tam olarak
    `Model hata döndü, farklı şekilde dene.`.
14. **Hata da ret de aynı beşten düşer; son deneme retse cümle** — dört `503`, sonra ret + `REFUSAL`:
    altı istek; `failed`, metin cümle.
15. **Son deneme teknik bir hataysa onun kendi metni, retlerden sonra bile** — dört kez ret +
    `REFUSAL`, sonra `she turns` ve kontrolü `503 meşgul`: on istek; `failed`, metin
    `DeepSeek HTTP 503\nmeşgul`.
16. **Kontrolün metni kutunun beklediği kelimeyi ister** — `CHECK_INSTRUCTION`'da `APPROVED` ve
    `REFUSAL` geçer.
17. **Kontrolün metni bir isteğin cevabından söz eder, Queen Editor'den değil** — metinde `video` ve
    `prompt` geçmez *(QueenAgent v10-1b aynı metni kullanacak)*.
18. **Queen AI hep reddederse üretim bugünkü yoldan durur, cümleyle** — gerçek kutu, gerçek H3
    yazarı, her soruya ret ve her kontrole `REFUSAL` diyen sahte HTTP, fotoğrafı üretilmiş bir karenin
    borçlu video işi, `resume_batch`: tam 30 istek (3 × 5 × 2); durum `error`; hata
    `Aynı kare 3 kez denendi — üretim durduruldu\nModel hata döndü, farklı şekilde dene.`; video
    üreticisi hiç çağrılmadı; yazılmış prompt yok, video satırı yok — iş borçlu.

### `backend/tests/test_composition_root.py`

19. **`main.py`'nin her yazarı kontrol eden kutudan geçer** — 416'nın testi, parametreli dört durum:
    dört `500`, sonra `she turns` + `APPROVED`: yazar `she turns` döner, ve **altı** istek gitti — beşinci
    denemenin cevabı ve onun kontrolü.

## Kırmızı beklenen

- `test_deepseek_box.py` 1 – 5: istek sayısı bir eksik — kutu kontrol etmiyor.
- 10, 16, 17: `ImportError` — `CHECK_INSTRUCTION` yok.
- 11, 12, 13, 14, 15: kutu ilk gelen metni döndüğü için yanlış metin ya da yanlış istek sayısı.
- 18: ret metni prompt oluyor, video üreticisi çağrılıyor.
- `test_composition_root.py` 19'un dört durumu: beş istek, altı değil.
- 6, 7, 8, 9 yeşil; `test_video_prompt_writer.py` ve `test_deepseek_client.py` aynen yeşil; öteki
  her şey yeşil.

## Bilinçli olarak yapılmayan

- Araçlı istek ve `Answer`'a ret mi teknik mi diyen alan — 419. Bugün o alanı okuyan yok.
- Denemeler arasında bekleme, deneme sayısının ayarı, denemelerin günlüğü yok.
- Kontrolün cevabı gevşek okunmaz (büyük-küçük harf, nokta): metin tek kelimeyi açıkça istiyor, ve
  başka her şey ret — yanlışlık prompt'a değil hata satırına çıkar.
- `policy.py`, `run_loop.py`, yazarlar, ekran, `dist` ve yol haritası değişmez.
