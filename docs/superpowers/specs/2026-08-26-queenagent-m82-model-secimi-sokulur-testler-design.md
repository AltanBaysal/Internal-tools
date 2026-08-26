# Madde 82 — Model seçme sistemi sökülür · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 4, Madde 82 ·
**Üstüne geldiği:** [Madde 72](2026-08-26-queenagent-m72-grok-build-tek-model-uygulama-design.md) —
modeli teke indirdi, makineyi bıraktı.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmaz, ve tur kırmızı
commit'lenir.

---

## Sökülen şey

72 listeyi tek satıra indirdi ama etrafındaki her şey yerinde kaldı: sohbet kaydında bir `model`
alanı, onu okuyup yazan bir PATCH, bir `GET /api/model`, bir menü bileşeni, bir liste dosyası, bir
isim çözücü, ve sunucudan ekrana kadar altı fonksiyon boyunca taşınan bir `default_model`.

Tek model varken bunların hepsi **boşa çalışıyor**: her yol aynı cevaba varıyor.

Geriye kalan: `config.XAI_MODEL`, ve yazma kutusunun ayağında tıklanamayan bir etiket.

## Etiket

`Grok Build` yazan bir `<span>`. Düğme değil, menüsü yok, prop'u yok. Skills ile gönder düğmesinin
arasında — `karar 1`'in sırası duruyor, yalnız ortadaki artık bir denetim değil.

**Adı ön yüzde yazılı.** `config.py` id'yi tutuyor (`grok-build-0.1`), etiket insan okuyan hâlini
(`Grok Build`). İkisi birlikte hareket eder ve bunu tutan şey bir test değil, iki dosyada birer
yorum — Python ile JS birbirini okuyamıyor, ve bu sınır 72'den önce de aynen buradaydı.

**Bedeli:** ortamdan `XAI_MODEL` ezilirse etiket bunu söylemez. Bu bir geliştirici işi; defter
ezmiyor, Colab ezmiyor. Alternatifi sunucudan çekmekti, ve o tam olarak sökülen makinenin kendisi.

## Eski kayıtlar

Diskteki sohbetlerin JSON'unda `"model": "grok-4.3"` duruyor. **Okuyan kalmıyor** — alan domain'den
çıkınca mağaza onu görmüyor bile, ve o sohbetler de Grok Build'e gidiyor. Göç yazılmıyor: sohbet
bir daha yazıldığında anahtar kendiliğinden düşüyor.

Bu, kullanıcının *"grok-4.3 kullanmıyoruz"* şartının gerçekten sağlandığı yer. 72 bunu yapmamıştı:
eski sohbetler kendi modelleriyle cevaplamaya devam ediyordu.

## Silinen testler

Bir davranış giderken testi de gider. Silinenler kayıp değil — sildikleri şey artık yok:

| Nerede | Ne |
|---|---|
| `test_model_api.py` | **dosya tamamen** — uç nokta yok |
| `models.test.js` | **dosya tamamen** — liste yok |
| `ModelPicker.test.jsx` | **dosya tamamen** — bileşen yok |
| `test_chats_api.py` | Modelle doğan sohbet · varsayılana düşen sohbet · orta konuşmada model değişimi · o değişimin 404'ü · sohbetin kendi modeliyle sorulan cevap |
| `test_set_chat_choices.py` | Modelle ilgili olanlar; dosya `test_set_chat_skill.py` olur |
| `test_start_chat.py` · `test_stream_answer.py` · `test_file_chat_store.py` | Model taşıyan birer test |
| `test_xai_client.py` · `test_xai_engine.py` | Çağıranın modelinin kazandığını söyleyenler |
| `App.test.jsx` · `ChatScreen.test.jsx` · `ProjectScreen.test.jsx` | Model seçmeyi sınayanlar |

## Kırmızıya dönecek testler

Silmek kırmızı üretmez. Kırmızıyı **yokluğu tutan** testler üretir:

**Arka uç — beş:**

1. `GET /api/model` artık **404**. Uç nokta gittiğinde Flask'in kendi cevabı bu.
2. Sohbetin JSON'u `model` anahtarı **taşımıyor**.
3. Yalnız model taşıyan bir PATCH **400** — kabul edilen tek alan skill, ve hata cümlesi de bunu
   söylüyor.
4. `Chat` dataclass'ında `model` diye bir alan **yok**.
5. Motor modelsiz çağrılıyor: sahte motorun `stream`'i `model` parametresi tanımıyor, ve hâlâ
   geçiliyorsa `TypeError` ile düşüyor.

**Ön yüz — dört:**

6. `ModelLabel` `Grok Build` diyor ve **düğme değil**.
7. Sohbet ekranının ayağı: `Skills⌄`, `Grok Build`, `↑` — ve **iki düğme**, üç değil.
8. Proje ekranının ayağı aynısı.
9. Uygulama `/api/model`'i **hiç sormuyor**, ve yeni sohbetin POST'u `model` **taşımıyor**.

Toplam **dokuz kırmızı**.

## Yanında gelen iki sadeleşme

**Açık menü durumu ikiliye iniyor.** Bugün `"model" | "skills" | null`; geriye tek menü kalınca
boolean yetiyor. `picker`/`onPicker` prop'ları `skillsOpen`/`onToggleSkills` oluyor.

**Escape sırası kısalıyor.** `fark 67` şunu yazmıştı: proje menüsü → onay kutusu → Skills → model →
açık panel. Model çıkınca dörde iniyor. Belgelenmiş bir karar değişiyor; sebebi o adımın
kapatacağı bir şeyin kalmaması.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `config.XAI_MODEL` ve testi | Modelin adının geçtiği tek yer o oluyor |
| `SkillPicker`, `Menu` | Skill seçimi olduğu gibi duruyor — orada gerçekten bir seçim var |
| `.picker` CSS kuralı | Skills düğmesi hâlâ kullanıyor |
| Mesaj kayıtları | Model mesajda değil sohbette duruyordu |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur** — birlikte koşturulduğunda vitest bu makinede zaman aşımına düşüyor.

Sayılar bu turda **düşüyor**, çünkü silinen test eklenenden çok. Kesin toplam koşulunca yazılır:
bir refactor'da silinen testin sayısını önden kestirmek, kestirmenin kendisini doğrulanacak bir şey
yapar.

`dist` bu turda derlenmiyor: kaynak değişmiyor, yalnız testler yazılıyor.
