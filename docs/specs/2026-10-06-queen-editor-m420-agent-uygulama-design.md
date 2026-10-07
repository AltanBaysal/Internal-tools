# Madde 420 — Queen Editor'ün agent'ı, uygulama turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 420 · v9-4c · **Tur:** 2/2 — kod.
**Testler:** [m420 test turu](2026-10-06-queen-editor-m420-agent-testler-design.md) — kurallar orada;
bu belge yalnız nasıl yapıldığını söyler. Ekran yok, `dist` kurulmaz.

## Yaklaşımlar

1. **Seçilen — döngü, araçlar ve metinler domain'de; koşucu özelliğin kökünde; proje `main.py`'nin
   verdiği iki okuyucudan.** QueenAgent'ın biçimi: döngü bir use case (`stream_answer` gibi),
   araçlar ve modele söylenen her metin ayrı modüllerde (`tools.py`, `prompt.py`). Koşucu fotoğraf
   özelliğinin `PhotoRunner`'ı gibi, iş parçacığını ve durdurma işaretini tutan, `spawn`'ı verilen bir
   nesne. Agent projeyi `main.py`'nin verdiği `list_frames` ve `_photo_store.read` ile okur.
2. *Elendi —* agent'ın kendi data katmanında `photos.jsonl`, `plan.json`, `order.json`'u yeniden
   okuması: galerinin kartını kuran kural (*"boş kutu yaşamaz"*, kopya kareler, sıra) ikinci kez
   yazılır, ve iki kopya ilk değişiklikte ayrışır. `main.py`'nin bir özelliğe ötekinin yeteneğini
   vermesi zaten var: projeler özelliğine fotoğraf işçisini durdurma yetkisi böyle verilir.
3. *Elendi —* "çalışıyor"u kayda yazmak: yeniden başlayan sunucu onu silemez ve yalan söyler; 417 de
   bu yüzden dışarıda bıraktı.
4. *Elendi —* durdurmanın yalnız işaret koyup *"durduruldu"*yu agent'a yazdırması: havadaki istek beş
   denemeyle dakikalarca sürebilir, ve ■ o kadar beklemez.

## Dosyalar

Hepsi `backend/features/agent/` altında, `main.py` dışında.

### `domain/prompt.py` — modele söylenen her metin

QueenAgent'ın `prompt.py`'si gibi: hiçbir şey import etmez, yalnız metin. İngilizce; Claude yazdı,
kullanıcı sonra okur.

- `INSTRUCTION` — kim olduğu (Queen Editor'ün içindeki asistan), neye cevap verdiği (açık proje),
  karenin numarası (galerinin rozeti, en eski 1), karenin katmanları, sorudan önce verilen kartlar ve
  alanları, iki araç; kurallar: yalnız okur, başka projeyi göremez, değişiklik istenirse bunu söyler;
  yalnız gerekeni okur; görmediğini tahmin etmez; kareleri numarasıyla anar; düz yazı, markdown yok
  *(ekran cevabı düz yazı çizer)*; kullanıcının dilinde cevap verir.
- `SYSTEM_PROMPT_SUFFIX` — QueenAgent'ınkinin birebir kopyası *(prompt_writer.py'deki gibi: kopya,
  çünkü iki araç birbirine uzanmaz; test QueenAgent'ın metnine sabitler)*.
- `LAST_ROUND` — son tur olduğu, aracın koşmayacağı, eldekiyle cevap vereceği, okuyamadığını
  söyleyeceği.
- `FRAMES` — kartların başlığı, tek satır.
- `READ_FRAME`, `LOOK_AT_FRAME`, `THE_FRAME` — araçların ve argümanın açıklaması.

### `domain/tools.py` — iki araç ve modele geri söylenenler

```python
TOOLS = [_tool("read_frame", prompt.READ_FRAME), _tool("look_at_frame", prompt.LOOK_AT_FRAME)]

def card(number, frame, whole=False):        # {"frame","status","layers","owed","failed"}
    ...                                      # whole: + "errors","scene","prompts"

def run_tool(frames, picture, project, call):
    """-> (adımın iki cümlesi ya da None, modele söylenen, gösterilecek parçalar ya da None)"""
```

- Bilinmeyen ad, çözülemeyen argüman (`ValueError` — JSON değil; `AttributeError` — nesne değil),
  tam sayı olmayan ya da `bool` numara, olmayan kare: adım yok, test spec'inin cümleleri.
- `read_frame`: kartın bütünü, `json.dumps(..., ensure_ascii=False)` — Türkçe prompt modele okunur
  gelir.
- `look_at_frame`: kartın `layers["photo"]` dosyası `picture(project, dosya)` ile okunur; yoksa ya da
  `None` gelirse *"Frame N has no photo."*; varsa iki parça — *"The photo of frame N:"* yazısı ve
  `data:<tür>;base64,…` görsel. Tür dosyanın adından (`mimetypes`), istemcinin `_picture`'ı gibi; o
  servisin özel fonksiyonu, ve görselin mesaja nasıl girdiği agent'ın kararı.
- Araçlar sorunun başında okunan kartlardan cevap verir: numara bir soru boyunca aynı kareyi anlatır.

### `domain/usecases/answer_question.py` — döngü

```python
MAX_ROUNDS = 32
LOOKING = ("Projeye bakıyor…", "Projeye baktı")
NO_FRAMES = "Projede henüz kare yok. …"

def answer_question(box, frames, picture, run, project, earlier, question):
    run.add_step(*LOOKING)
    cards = numbered(frames(project))          # {numara: kart}; en alttaki 1
    if not cards:
        run.answer(NO_FRAMES); return
    messages = _conversation(cards, earlier, question)
    for index in range(MAX_ROUNDS):
        if run.stopped(): return
        last = index == MAX_ROUNDS - 1
        said = (box.converse(messages + [LAST_ROUND mesajı]) if last
                else box.converse(messages, TOOLS))
        if said.failed: run.fail(said.text); return
        if last or not said.tool_calls: run.answer(said.text); return
        messages.append(asistanın çağrıları)
        for call in said.tool_calls:
            adım, söylenen, parçalar = run_tool(cards, picture, project, call)
            if adım: run.finish_step(); run.add_step(*adım)
            messages.append(aracın cevabı)
        if gösterilecek parçalar: messages.append({"role": "user", "content": parçalar})
```

- **Projeye bakma her sorunun ilk adımı** ve hep açık: her yeni adımdan önce `finish_step` yazılır,
  yani "önceki adım açık mı" diye tutulan bir bayrak yok. Sorunun son adımını cevap ya da hata
  bitirir, durdurmak düşürür — kaydın katlaması.
- **Son turun sözleri cevaptır**, araç çağrısı gelse de: araç verilmeyen turda çağrı gelmez, ve
  gelse de koşacak tur kalmadı.
- **Durdurulduğu her turun başında sorulur**: koşucu yazıları zaten düşürür, ama havaya bir istek
  daha göndermek boşa para.
- Mesajların sırası: talimat, sohbetin önceki soruları ve cevapları, kartlar, soru; son turda
  sonuna `LAST_ROUND`.

### `domain/ports.py`

`Run` — `stopped()`, `add_step(running, done)`, `finish_step()`, `answer(text)`, `fail(text)`; bir
durdurmadan sonraki yazının hiçbir yere düşmediğini söyler. `QueenAI` — kutunun `converse`'i. Kartlar
ve görsel okuyucusu `answer_question`'ın belgesinde, çağrılabilir olarak.

### `runner.py` — `AgentRunner(record, spawn=None)`

```python
start(project, chat_id, text, at, work) -> bool   # kilit içinde: çalışıyorsa False; soruyu yaz; kaydet
stop(project, chat_id)                             # kilit içinde: çıkar, bitti işaretle, "stopped" yaz
working(project) -> list[int]                      # kilit içinde, sıralı
```

- **Tek kilit**, üç işin aynı anda olmaması için: bir koşunun bitti işareti ile yazısı birlikte —
  durdurulmuş koşu kendi durdurmasının ardına yazamaz; soru ile kayıt birlikte — iki basış iki soru
  yazamaz.
- **`_Run`** — koşunun yazıları koşucunun `_write`'ından geçer: kilit içinde, koşu bitmediyse kayda.
  `answer` ve `fail` koşuyu bitirir ve aynı kilit içinde çalışanlardan çıkarır: cevaptan sonra gelen
  ■ bir şey bulmaz.
- **`_go`** — işi koşar; fırlatırsa hatanın kendi sözleriyle `fail`; `finally` koşuyu, hâlâ
  kendisiyse, çalışanlardan çıkarır — durdurulup yerine yeni soru başlamış sohbetin yeni koşusuna
  dokunmaz.
- `spawn` kilidin dışında çağrılır: içeride koşan iş (testler) kilidi yeniden ister.
- Üretimde `threading.Thread(daemon=True)` — `PhotoRunner`'ınki gibi; süreç kapanınca iş de biter.

### `domain/usecases/chats.py` — üç yeni use case

```python
class EmptyQuestion(Exception)   # "Soru boş."
class AgentBusy(Exception)       # "Bu sohbette agent hâlâ çalışıyor."

def ask_question(record, runner, agent, now, project, chat_id, text):
    earlier = open_chat(record, project, chat_id)["questions"]       # 404'ler önce
    metin değil ya da boşsa EmptyQuestion
    runner.start(..., lambda run: agent(run, project, earlier, text)) False ise AgentBusy
    return open_chat(record, project, chat_id)

def stop_agent(record, runner, project, chat_id)   # sohbet var mı, durdur, sohbet
def working_chats(record, runner, project)          # proje var mı, çalışanlar
```

### `presentation/routes.py` — `make_agent_blueprint(ask_question, stop_agent, working_chats)`

Blueprint `agent`. `POST …/chats/<int:chat_id>/questions` gövdeden yalnız `text`'i alır (gövde
nesne değilse `None`); `POST …/chats/<int:chat_id>/stop`; `GET …/chats/working` →
`{"working": […]}`. `_answer` iki yeni hatayı da tanır: `EmptyQuestion` 400, `AgentBusy` 409.
`/chats/working` `<int:chat_id>`'le çakışmaz: `int` dönüştürücüsü sözcüğü almaz.

### `data/chat_record.py`

- **Katlama:** `answer` ve `failure` son adımı bitirir (`stepDone` ile aynı yardımcı); `stopped`
  bitmemiş adımları düşürür.
- **Kilit:** `__init__`'te bir `threading.Lock`; `_add` satırı kilit içinde ekler.
- **Klasör:** `_add` kilit içinde önce klasöre sorar; yoksa `ProjectMissing("Proje yok: <ad>")`
  *(chats.py'den — data domain'e bakabilir)*.

### `backend/main.py`

```python
# The agent (madde 420): Queen AI reading the open project ...
_agent = partial(answer_question, _queen_ai,
                 partial(list_frames, _photo_record, _photo_store, _plan_store, _order_store),
                 _photo_store.read)
_agent_runner = AgentRunner(_chat_record)
_agent_bp = make_agent_blueprint(
    ask_question=partial(ask_question, _chat_record, _agent_runner, _agent,
                         lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    stop_agent=partial(stop_agent, _chat_record, _agent_runner),
    working_chats=partial(working_chats, _chat_record, _agent_runner))
```

`create_app` listesinin sonuna `_agent_bp`. `_chat_record`'un yorumu artık iki şeyi söyler: tek nesne
olduğu için kilidi bütün yazanları kapsar.

## Bir sonuç, açıkça

- **DeepSeek'in görseli araç cevabından sonraki bir kullanıcı mesajında kabul ettiği** gerçek
  servisle denenmedi; testler istemcinin gönderdiğini gösteriyor. Kabul etmezse cevabı teknik bir hata
  olarak, DeepSeek'in kendi sözüyle sohbete düşer, ve kullanıcının Colab denemesinde görülür.
- **Silinen ya da yeniden adlandırılan projede çalışan agent** bir sonraki yazısında biter; kayıt
  reddettiği için hata da yazılamaz, ve iş parçacığının hatası sunucunun hücresine düşer. Sohbet
  yeni adda sonucusuz durur — yeniden başlamadaki gibi.
- **Agent'ın her metin cevabı iki istek** (cevap ve kontrolü), **her araç turu bir**: bir soru en çok
  33 istek ister; kutunun denemeleriyle her tur beşe kadar.

## Bilinçli olarak yapılmayan

- Ekran — 425; frontend, `dist`, yol haritası, QueenAgent'ın kodu.
- Akış, yeniden dene, silme; havadaki isteği kesmek; yeniden başlamada sonuç yazmak.
- Agent'ı yeniden adlandırılan projenin yeni adına taşımak.
- Kartları her araç çağrısında yeniden okumak: numaralar soru boyunca sabit kalsın.
