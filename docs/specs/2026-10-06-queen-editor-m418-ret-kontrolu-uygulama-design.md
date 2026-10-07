# Madde 418 — Kutunun ret kontrolü, uygulama turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 418 · v9-3b · **Tur:** 2/2 — kod.
**Testler:** [m418 test turu](2026-10-06-queen-editor-m418-ret-kontrolu-testler-design.md) — kurallar
orada; bu belge yalnız nasıl yapıldığını söyler. **Kutunun kendisi:**
[m416 uygulama turu](2026-10-06-queen-editor-m416-kara-kutu-uygulama-design.md).

## Yaklaşımlar

1. **Seçilen — kontrol kutunun `try`'ının içinde, ikinci bir `complete`.** 416'nın uygulama spec'i
   yeri önceden söylemişti: asıl isteğin cevabından sonra aynı istemciye kontrol sorulur. Kontrolün
   kendi hatası aynı `except`'e düşer, ret de aynı döngüde bir deneme harcar; sayaç tek, kural tek.
   Kontrolün metni ve ret cümlesi `box.py`'de, kutunun yanında: onları kullanan yalnız kutu.
2. *Elendi —* kontrolü ayrı bir `services/deepseek/check.py`'ye koymak (metin + karar fonksiyonu):
   üç satırlık bir iş için bir dosya ve bir arayüz daha; kutu zaten tek kullanan. Ayrı bir sabitler
   modülü de istenmedi.
3. *Elendi —* kontrolü istemcinin `complete`'ine koymak: istemci tek istek atar (416); iki istek atan
   bir `complete` istemcinin testlerini ve sözünü bozar.
4. *Elendi —* kontrolü yazarlara koymak: 420'nin agent'ı ve QueenAgent aynı kontrolü ikinci kez yazmak
   zorunda kalır; kullanıcı her isteğin **tek** kutudan geçmesini istedi.

## Kutunun içi

```python
for _ in range(TRIES):
    try:
        answer = self._client.complete(system, text, images)
        if self._client.complete(CHECK_INSTRUCTION, answer) == "APPROVED":
            return Answer(answer)
        said = REFUSED
    except Exception as exc:
        said = str(exc)
return Answer(said, failed=True)
```

- **Kontrol isteği:** sistem mesajı `CHECK_INSTRUCTION`, sözler istemcinin döndüğü cevabın kendisi,
  resim yok. Aynı istemci — aynı model, adres, anahtar, zaman aşımı.
- **Karar:** kontrolün cevabı (istemci zaten kırpıyor) tam olarak `APPROVED` ise geçer. Başka her şey
  ret: kullanıcı onayı şart koştu, ve kendisi yargılamayı reddeden bir kontrol hiçbir şeyi onaylamadı.
  Harf büyüklüğü, nokta gibi gevşeklik yok — metin tek kelimeyi açıkça istiyor; bir sapma prompt'a
  değil hata satırına çıkar.
- **Son denemenin türü konuşur:** `said` her denemede yeniden yazılır, yani beşin sonunda son
  denemeninki kalır — retse cümle, teknik hataysa hatanın kendi metni. 416'nın "son hatanın metni"
  kuralının aynısı, ek bir değişken ya da sayım olmadan.
- **Anahtar yoksa** ilk `complete` hiçbir şey göndermeden fırlatır; kontrole hiç gelinmez.

## Kontrolün metni

İngilizce, `prompt_writer.py`'nin metinleri gibi modele yazılmış; bir isteğe verilmiş **bir cevaptan**
söz eder — video, prompt, kare yok —, çünkü QueenAgent v10-1b aynısını birebir kullanacak. Kontrol
cevabı tek başına görür (kullanıcı — "gelen cevabın metnin birebir deepseek gönder"), isteği görmez;
metin bunu söyler ki model isteği tahmin etmeye kalkmasın. Yalnız ret mi değil mi sorulur: iyi mi,
doğru mu, izinli mi diye yargılamaz — yetişkin içerik ret değildir, yoksa Queen Editor'ün her cevabı
reddedilirdi.

```
You check an answer that a language model gave to a request.

Context
- You are given the answer alone, word for word. You are not given the request.
- An answer is a refusal when the model does not do what was asked: it says it cannot or will not, it apologizes instead of answering, or it gives a warning or a lecture instead of the answer.

Rules
- Judge only whether the answer is a refusal. Never judge whether the answer is good, true or allowed.
- Adult, explicit or violent content in the answer is not a refusal.
- If the answer is a refusal, write REFUSAL. Otherwise write APPROVED.
- Write only the one word. No quotes, no explanations.
```

Suffix yok: suffix yazarların (`prompt_writer.py`, bir özellik), ve servis özelliği bilmez. Kullanıcı
metni sonra okur *(yol haritası — "DeepSeek'e giden yeni metinleri Claude yazar ve commit'ler,
kullanıcı sonra okur")*.

## Dosyalar

### `backend/services/deepseek/box.py`

- Modül belgesi 418'i anlatır: her cevap kendi isteğinde kontrol edilir, yalnız onay döner, ret bir
  deneme harcar, sonda son denemenin türü konuşur.
- `CHECK_INSTRUCTION` — yukarıdaki metin, neden İngilizce ve neden genel olduğunu söyleyen bir yorumla.
- `REFUSED = "Model hata döndü, farklı şekilde dene."` — neden modelin kendi sözü değil: ret bir cevap
  gibi geçerse prompt olur.
- `Box.ask` — yukarıdaki döngü; belgesi bir denemenin ne olduğunu söyler.

`Answer`, `TRIES`, `Box(client)` aynen.

### Değişmeyen

`client.py` (tek istek; belgesi hâlâ doğru), `prompt_writer.py` (başarısız `Answer`'ı zaten
fırlatıyor; belgesi hâlâ doğru), `main.py` (`Box(DeepSeekClient(...))` aynen), `policy.py`,
`run_loop.py`, ekran, `dist`, yol haritası.

## Bir sonuç, açıkça

- **Her iyi cevap artık iki istek** — cevap ve kontrolü: Queen AI'ın her prompt'u bir istek daha, ve
  bir cevabın süresi kadar daha bekler.
- **Bir soru en çok 10 istek** (5 × 2), **bir üretim adımı en çok 30** (döngünün 3'ü × 10). Her
  istek 120 sn'de zaman aşımına düşer (`config.DEEPSEEK_TIMEOUT`); en kötü hâlde — her cevap gelir,
  her kontrol asılı kalır — bir soru 20 dakika, adım bir saat sürer. Bugün en kötüsü yarım saat.
- **Kontrolün kendisi açık içerikte yargılamayı reddederse** cevap ret sayılır, ve beş denemeden sonra
  hata satırında cümle çıkar — sessizce kötü bir prompt değil, görünür bir hata. Metin bunu önlemek
  için yetişkin içeriğin ret olmadığını söylüyor.

## Bilinçli olarak yapılmayan

- 419'un araçlı yolu ve `Answer`'a ret mi teknik mi diyen alan.
- Denemeler arasında bekleme, ayar, günlük.
- Kontrolün cevabını gevşek okumak.
