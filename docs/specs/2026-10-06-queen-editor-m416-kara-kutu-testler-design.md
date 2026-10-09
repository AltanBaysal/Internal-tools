# Madde 416 — DeepSeek'in kara kutusu, test turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 416 · v9-3a · **Tur:** 1/2 — yalnız testler.

**Kullanıcıdan gereken — yok.** Madde 5 Ekim'de hizalandı; kararları yol haritasının *Maddelerin
kararları → v9-3* bölümünde, kullanıcının sözleriyle. Kutunun nasıl kurulacağı teknik bir karar,
Claude'un. Ekran değişmez *(kullanıcı — "ui tasarımını sen yapmıyorsun bu mesjaı kullansın")*.

## Bugün ne oluyor

Queen AI'ın üç yazarı — H3, WAN ve ses — DeepSeek'e tek bir istek atıyor
*([prompt_writer.py](../../queen-editor/backend/features/photo_generation/data/prompt_writer.py))*,
istemci *([client.py](../../queen-editor/backend/services/deepseek/client.py))* HTTP hatasında, bozuk
ve boş cevapta sunucunun kendi metniyle `RuntimeError` atıyor; internet yoksa `requests`'in kendi hatası
olduğu gibi çıkıyor. Hata yazarın içinden döngüye *([run_loop.py](../../queen-editor/backend/features/photo_generation/domain/run_loop.py))*
gidiyor: aynı iş üç kez deneniyor, üçüncüde de olmazsa üretim duruyor ve ekrandaki hata satırında
`Aynı kare 3 kez denendi — üretim durduruldu` ve altında hatanın metni yazıyor
*([policy.py](../../queen-editor/backend/features/photo_generation/domain/policy.py))*. Yani bugün bir
işin üç denemesi DeepSeek'e üç istek.

## Kurallar

1. **Queen AI'ın her isteği kutudan geçer** — H3'ün, WAN'ın ve sesin yazarı, `main.py`'nin kurduğu
   hâliyle.
2. **Kutu isteği aynen yeniden gönderir:** HTTP hatasında, bozuk cevapta, boş cevapta, ve hiç cevap
   gelmeyince — internet yok, zaman aşımı *(v9-3'ün (5)'i: "teknik no internet veya internal erro")*.
   Aynı talimat, aynı sözler, aynı resimler.
3. **En çok 5 deneme**, hepsi birlikte. İyi bir cevap gelince kutu durur; arkasından istek gitmez.
4. **Beşi de olmazsa kutu hata fırlatmaz:** son hatanın kendi metnini döner, başarısız diye işaretli.
   Metin servisin söylediği — `DeepSeek HTTP 503` ve gövdesi, ya da bağlantı hatasının kendi sözleri;
   sebep uydurulmaz.
5. **Anahtar yoksa hiçbir istek gitmez**, ve kutu istemcinin bugünkü cümlesini başarısız diye döner.
6. **Başarısız cevap prompt olmaz:** yazar onu bugünkü hata yoluna çevirir — kutunun metniyle bir
   hata atar; karta hiçbir şey yazılmaz.
7. **Döngünün üç denemesi bugünkü gibi** — her biri kutunun beşini içerir, yani en çok **15 istek**;
   üçü de olmazsa üretim bugünkü gibi durur, iş borçlu kalır, ve hata satırında DeepSeek'in metni
   yerine kutunun metni yazar: `Aynı kare 3 kez denendi — üretim durduruldu` ve altında kutunun
   metni.
8. **İstemcinin kendi sözleşmesi değişmez:** tek istek, hata sunucunun kendi metniyle atılır —
   bugünkü testleri aynen geçer. Kutu onun üstünde.
9. **Hiçbir test ağa çıkmaz:** istemcinin `http`'si sahte; `main.py`'nin kurduğu istemcide
   `requests.post` testin içinde sahteyle değiştirilir.

**Değişmeyen:** yazarların DeepSeek'e söyledikleri — talimatlar, suffix, sözler, resimler; döngü ve
`policy.py`; ekran; istemcinin tek isteği ve hata metinleri; QueenAgent.

## Arayüz — uygulama turunun vereceği

- `backend/services/deepseek/box.py`: `Box(client)`; `Box.ask(system, text="", images=())` →
  `Answer`. `Answer.text` cevabın metni ya da son hatanın metni, `Answer.failed` başarısızsa `True`.
- Yazarlar kutunun `ask`'ını sorar; `main.py`'de `_queen_ai` istemciyi saran kutudur.

## Nasıl kanıtlanıyor

Kutu **gerçek istemciyle** sınanır: sahte HTTP bir cevap listesinden sırayla cevap verir — bir cevap,
ya da atılacak bir bağlantı hatası — ve her isteği not eder. Böylece kutunun gördüğü hatalar
istemcinin bugün attıklarının ta kendisi. Yazarlar sahte bir kutuyla, döngü
`test_photo_usecases`'in sahteleriyle — `test_variant_batch`'in yaptığı gibi. Kutunun modülü bugün yok:
testler onu kullandıkları yerde içe aktarır, yoksa pytest toplarken bütün oturumu durdurur.

## Yazılacak testler

### `backend/tests/test_deepseek_box.py` — yeni

1. **İyi bir cevap olduğu gibi döner, tek istekle** — `failed` değil, metin kırpılmış.
2. **HTTP hatasında aynı istek yeniden gider** — `500`, sonra iyi cevap: iyi cevap döner; iki istek,
   ikisinin adresi, başlıkları ve gövdesi — resim ve sözlerle — birebir aynı.
3. **Bozuk cevapta yeniden gider** — `{"choices": []}`, sonra iyi cevap: iki istek, iyi cevap.
4. **Boş cevapta yeniden gider** — `"   "`, sonra iyi cevap: iki istek, iyi cevap.
5. **Cevap hiç gelmeyince yeniden gider** — `requests.ConnectionError`, sonra iyi cevap: iki istek,
   iyi cevap.
6. **En çok beş deneme, sonra son hatanın kendi metni** — beş ayrı `503` (gövdeleri `meşgul 1` …
   `meşgul 5`), arkasında iyi bir cevap bekliyor: tam beş istek; kutu hata atmıyor; `failed`,
   metin `DeepSeek HTTP 503\nmeşgul 5`.
7. **Son hata bağlantınınsa onun kendi sözleri** — dört `500`, sonra `ConnectionError("Max retries
   exceeded with url: /chat/completions")`: `failed`, metin o hatanın metni.
8. **Anahtar yoksa istek gitmez, istemcinin cümlesi başarısız döner** — `failed`, metinde
   `DEEPSEEK_API_KEY` ve `Colab Secrets`; sıfır istek.
9. **Queen AI hep düşerse üretim bugünkü gibi durur, 15 istekten sonra** — gerçek kutu, gerçek H3
   yazarı, hep `503 meşgul` diyen sahte HTTP, fotoğrafı üretilmiş bir karenin borçlu video işi,
   `resume_batch`: tam 15 istek; durum `error`; hata
   `Aynı kare 3 kez denendi — üretim durduruldu\nDeepSeek HTTP 503\nmeşgul`; video üreticisi hiç
   çağrılmadı; video satırı yok, yazılmış prompt yok — iş borçlu.

### `backend/tests/test_video_prompt_writer.py`

Sahte, kutunun sahtesi olur: `FakeVisionClient` → `FakeQueenAI`; `complete` yerine `ask`, ve
`Answer` döner. İstenirse başarısız bir `Answer` döner. Öteki testlerin sordukları aynen kalır.

10. **Başarısız cevap hiçbir yazarda prompt olmaz** — parametreli, H3, WAN ve ses: kutu
    `Answer("DeepSeek HTTP 503\nmeşgul", failed=True)` dönüyor; yazar `RuntimeError` atar, metni
    birebir kutunun metni.

### `backend/tests/test_composition_root.py`

11. **`main.py`'nin her yazarı kutudan geçer** — parametreli: H3 oturumunun videosu, WAN oturumunun
    videosu, iki oturumun sesi. Anahtar var; `requests.post` sahteyle değiştirilir — dört `500`, sonra
    iyi cevap: yazar iyi cevabı döner, ve beş istek gitti.

## Kırmızı beklenen

- `test_deepseek_box.py` 1–9: `ModuleNotFoundError` — `box.py` yok.
- `test_video_prompt_writer.py`: yazara soran her test — 10 dahil — kırmızı, çünkü yazar hâlâ
  `complete` soruyor ve sahtenin artık yalnız `ask`'ı var. Yalnız metinleri okuyan testler yeşil.
- `test_composition_root.py` 11'in dört durumu: ilk `500` yazarın içinden hata olarak çıkıyor. Anahtar
  yokken soran bugünkü üç test yeşil kalır: kutu da hiçbir istek göndermeden aynı cümleyi verir,
  yazar onu atar.
- `test_deepseek_client.py` aynen yeşil — istemci değişmiyor. Öteki her şey yeşil; öteki üç satır
  yeşil.

## Bilinçli olarak yapılmayan

- Ret kontrolü yok — 418. Araçlı istek, konuşma geçmişi yok — 419. `Answer`'a ret mi teknik mi diyen
  bir alan 419'la gelir.
- Denemeler arasında bekleme yok: kullanıcı "aynen yeniden gönderir" dedi, bir aralık istemedi.
- Denemeler ekrana ya da günlüğe yazılmaz; ekran değişmez.
- `policy.MAX_ATTEMPTS` ve döngü değişmez; `dist`'e ve yol haritasına dokunulmaz.
