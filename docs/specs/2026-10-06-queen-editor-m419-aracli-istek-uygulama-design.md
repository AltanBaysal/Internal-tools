# Madde 419 — Kutunun araçlı isteği, uygulama turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 419 · v9-4a · **Tur:** 2/2 — kod.
**Testler:** [m419 test turu](2026-10-06-queen-editor-m419-aracli-istek-testler-design.md) — kurallar
orada; bu belge yalnız nasıl yapıldığını söyler. **Kutunun kendisi:**
[m416 uygulama turu](2026-10-06-queen-editor-m416-kara-kutu-uygulama-design.md),
[m418 uygulama turu](2026-10-06-queen-editor-m418-ret-kontrolu-uygulama-design.md).

## Yaklaşımlar

1. **Seçilen — istemcide `send`, kutuda `converse`, ikisinin altında tek döngü.** İstemcinin yeni
   `send(messages, tools=())`'u tek isteği atar ve `(sözler, araç çağrıları)` döner; bugünkü
   `complete` mesajlarını kurup onu çağırır, yani HTTP, durum kodu ve cevabı okumak tek yerde.
   Kutunun `ask`'ı ve yeni `converse`'i aynı özel döngüden geçer — 416'nın spec'inin söylediği
   *"ikinci bir yol, aynı beşlik döngü"*. `Answer` iki alan kazanır: `refused` ve `tool_calls`.
2. *Elendi —* istemciye kendi HTTP kodu olan ikinci bir yöntem: istek, durum kodu ve cevabın okunuşu
   iki kez yazılır, ve ilk düzeltme ikisinden birini unutur.
3. *Elendi —* `failed`'ı bir türe çevirmek (`None` / `"refusal"` / `"technical"`): yazarlar ve
   testleri değişir, oysa yazarın bilmesi gereken yalnız başarısız olup olmadığı. Yanına bir
   `refused` eklemek bugünkü her okuyucuyu olduğu gibi bırakır.
4. *Elendi —* `Answer`'da DeepSeek'in asistan mesajını bütün taşımak: çağıran DeepSeek'in biçimini
   okur, ve başarısızlığın bir mesajı yok.
5. *Elendi —* agent için ayrı bir kutu sınıfı: aynı kuralın iki döngüsü.

## Kutunun biçimi — 420'nin soracağı

```python
answer = queen_ai.converse(messages, tools)   # tools verilmezse istekte yok
answer.text        # sözler (kırpılmış, yoksa "") ya da başarısızlığın metni
answer.tool_calls  # DeepSeek'in çağrıları, gönderdiği gibi; yoksa []
answer.failed      # beş deneme de olmadıysa True
answer.refused     # başarısızlıkta: son deneme retse True, teknikse False
```

- **Araç çağrısı:** `tool_calls` dolu; `text` yanındaki söz ya da `""`. 420 bir sonraki isteğe
  `{"role": "assistant", "content": answer.text, "tool_calls": answer.tool_calls}`'u ve her aracın
  `{"role": "tool", "tool_call_id", "content"}`'unu ekler — QueenAgent'ın yaptığı gibi.
- **Metin:** onaylanmış cevap; `tool_calls == []`.
- **Başarısızlık:** `failed`; `refused` ekranın hangi hata kartını çizeceğini söyler (425); metin
  cümle ya da hatanın kendi sözleri.

## Kutunun içi

```python
def ask(self, system, text="", images=()):
    return self._tried(lambda: (self._client.complete(system, text, images), []))

def converse(self, messages, tools=()):
    return self._tried(lambda: self._client.send(messages, tools))

def _tried(self, request):
    for _ in range(TRIES):
        try:
            words, calls = request()
            if calls:
                return Answer(words, tool_calls=calls)
            if self._client.complete(CHECK_INSTRUCTION, words) == "APPROVED":
                return Answer(words)
            said, refused = REFUSED, True
        except Exception as exc:
            said, refused = str(exc), False
    return Answer(said, failed=True, refused=refused)
```

- **Araç çağrısı olan cevap kontrolsüz döner**, yanındaki sözle birlikte: kontrol yalnız tek başına
  gelen sözlere bakar (v9-3). Çağrının yanındaki söz bir cevap değil, agent'ın çağrıyı yaparken
  söylediği — test spec'inin 4. kuralı.
- **Son denemenin türü konuşur:** `said` ve `refused` her denemede birlikte yeniden yazılır, yani
  beşin sonunda son denemeninkiler kalır — 418'in kuralı, bir bayrakla.
- **Anahtar yoksa** ilk istek hiçbir şey göndermeden fırlatır: teknik, `refused` `False`.

## İstemcinin içi

```python
def complete(self, system, text="", images=()):
    said = [...]                       # bugünkü gibi
    answer, _ = self.send([{"role": "system", "content": system},
                           {"role": "user", "content": said}])
    return answer

def send(self, messages, tools=()):
    # anahtar yoksa NotConfigured, bugünkü cümleyle
    body = {"model": self._model, "messages": messages}
    if tools:
        body["tools"] = tools
    # post, durum kodu ve bozuk cevap bugünkü gibi
    message = response.json()["choices"][0]["message"]
    words = (message.get("content") or "").strip()
    calls = message.get("tool_calls") or []
    # ikisi de yoksa "DeepSeek boş cevap döndü"
    return words, calls
```

- **`tools` yalnız varsa gider:** `complete`'in isteği bugünkü gövdeyle kalır, ve araç verilmeyen bir
  tur — QueenAgent'ın son turu gibi — anahtarsız gider.
- **Araç çağrısının `content`'i `null` gelir:** sözler o zaman `""`. Ne söz ne çağrı varsa cevap
  boştur, bugünkü boş cevap gibi.
- **Mesajlar ve araçlar olduğu gibi gider:** biçimleri çağıranın işi; yanlışsa DeepSeek'in kendi
  sözü teknik bir hata olarak döner.

## Dosyalar

### `backend/services/deepseek/client.py`

- Modül belgesi: bir talimat, sözler ve resimler — ya da bir konuşma ve araçlar — girer; cevabın
  sözleri ve araç çağrıları çıkar.
- `send` — yukarıdaki; belgesi ne aldığını ve ne döndüğünü söyler.
- `complete` — mesajlarını kurar, `send`'e sorar, sözleri döner. Belgesi aynen.

### `backend/services/deepseek/box.py`

- Modül belgesi 419'u anlatır: agent'ın konuşması aynı döngüden geçer, araç çağrısı kontrolsüz,
  başarısızlık ret mi teknik mi söyler.
- `Answer` — `refused: bool = False`, `tool_calls: list = field(default_factory=list)`; belgesi
  alanları söyler.
- `Box.ask`, `Box.converse`, `Box._tried` — yukarıdaki.

`CHECK_INSTRUCTION`, `REFUSED`, `TRIES` aynen.

### Değişmeyen

`prompt_writer.py` (`ask` ve `failed` aynen), `main.py` (`_queen_ai` zaten kutu; agent'ı 420 bağlar),
testler dışında her şey; ekran, `dist`, yol haritası.

## Bir sonuç, açıkça

- **`complete`'in bir hatasının metni değişir, tek bir durumda:** `content`'i `null` gelen bir cevap
  bugün Python'un kendi `AttributeError`'ını atıyor (`'NoneType' object has no attribute 'strip'`);
  artık `DeepSeek boş cevap döndü` ve gövde. Kutu ikisini de yeniden dener; prompt yazımının
  istekleri, cevapları ve testleri aynen.
- **Agent'ın her metin cevabı iki istek** (cevap ve kontrolü), **her araç çağrısı bir.** Bir soru en
  çok 10 istek, bugünkü gibi.

## Bilinçli olarak yapılmayan

- Agent, araçları, talimatı, `main.py`'de bağlanışı — 420; ekran — 425.
- Akış, denemeler arasında bekleme, ayar, günlük.
- Mesajların ve araçların biçimini denetlemek.
