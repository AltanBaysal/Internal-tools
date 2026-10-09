# Madde 417 — Agent'ın sohbetlerinin kaydı, uygulama turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 417 · v9-4b · **Tur:** 2/2 — kod.
**Testler:** [m417 test turu](2026-10-06-queen-editor-m417-sohbet-kaydi-testler-design.md) — kurallar
orada; bu belge yalnız nasıl yapıldığını söyler. Ekran yok, `dist` kurulmaz.

## Yaklaşımlar

1. **Seçilen — projede tek dosya, yalnız eklenir, okurken katlanır.** `chats.jsonl`'ın her satırı
   bir olay: hangi sohbet, ne oldu. Okumak satırları sırayla katlayıp sohbetleri kurar. Fotoğraf
   kaydının yolu *(`photo_record.py`)*: ölen oturum en çok yazdığı satırı kaybeder; liste, açmak ve
   yeni sohbet tek dosyayı okur.
2. *Elendi —* sohbet başına bir JSON, her adımda baştan yazılır: yazı ortasında ölen oturum bütün
   sohbeti kaybeder *(FOUNDATION 1)*; liste her sohbetin dosyasını açar — projeler listesinin tek
   dosyayı seçme sebebi aynı *(`project_store.py`, madde 225)*.
3. *Elendi —* sohbet başına bir JSONL: güvenli, ama liste yine N dosya açar.
4. *Elendi —* boş sohbet yazılmasın, *Yeni sohbet* her seferinde bir sonraki kimliği versin: o zaman
   açmak, hiç satırı olmayan bir kimliği de kabul etmek zorunda — yalnız bir kuralda var olan bir
   sohbet.

## Satırlar

```
{"chat": 1, "event": "opened"}
{"chat": 1, "event": "question", "text": "Kaç kare var?", "at": "2026-10-06T10:00:00+00:00"}
{"chat": 1, "event": "step", "running": "3 numaralı kareyi okuyor…", "done": "3 numaralı kareyi okudu"}
{"chat": 1, "event": "stepDone"}
{"chat": 1, "event": "answer", "text": "…"}
{"chat": 1, "event": "failure", "text": "…"}
{"chat": 1, "event": "stopped"}
```

**Katlama:**
- Çözülemeyen satır ya da `chat`'i tam sayı olmayan nesne atlanır — yarım kalmış son satır önündekileri
  gizlemez.
- Bir sohbet, hakkındaki ilk satırla var olur; sohbetler ilk görüldükleri sırayla döner. `opened`
  yalnız henüz sorusu olmayan sohbetin satırı.
- `question` yeni bir soru açar: `{"text", "askedAt", "steps": [], "outcome": None}`.
- Öteki olaylar sohbetin **son sorusuna** düşer; sorusu yoksa atlanır. `step` adımı
  `finished: False` ekler, `stepDone` son adımı bitirir; `answer` ve `failure`
  `{"kind", "text"}`, `stopped` `{"kind": "stopped"}` olur.

## Dosyalar

Yeni özellik, `backend/features/agent/` — `__init__.py`'ler boş, öteki özellikler gibi.

### `data/chat_record.py` — `DriveChatRecord(storage)`

Dosyanın adını ve satırların biçimini bilen tek yer. Her yazan yöntem tek satır ekler
(`storage.append_line`); okumak `storage.read_lines` + katlama. Önbellek yok: her okuma diskten,
yeniden başlayınca kayıp yok *(FOUNDATION 2)*. `project_exists` klasöre sorar.

### `domain/ports.py` — `ChatRecord(Protocol)`

Use case'lerin ve 420'nin kayıttan beklediği: yöntemler ve sohbetin biçimi. Öteki özelliklerin
`ports.py`'si gibi, import edilmez — sözleşmeyi yazar.

### `domain/usecases/chats.py`

- `ProjectMissing` — *"Proje yok: {project}"*; `ChatMissing` — *"Sohbet yok: {chat_id}"*. Projeler
  özelliğinin sınıfı import edilmez *(özellik ↛ özellik)*; cümle aynı.
- `new_chat` — proje yoksa `ProjectMissing`, hiçbir şey yazmadan; sorusuz bir sohbet varsa o; yoksa
  `max(id) + 1` (ilki 1), `add_chat`, `{"id", "questions": []}`. Aynı anda iki istek aynı kimliği
  alırsa ikisi de aynı boş sohbete düşer — kuralın istediği.
- `list_chats` — sorulu sohbetler, satır `{"id", "firstQuestion", "lastAskedAt"}`, `lastAskedAt`'e
  göre azalan. Zamanlar aynı biçimde ISO metni, metin sırası zaman sırası.
- `open_chat` — kimliği tutan sohbet, yoksa `ChatMissing`.

### `presentation/routes.py` — `make_chats_blueprint(new_chat, list_chats, open_chat)`

Blueprint `agent_chats`. `POST` ve `GET /api/projects/<project>/chats`,
`GET /api/projects/<project>/chats/<int:chat_id>`. İki 404 kendi cümlesiyle, `OSError` 500 ve
metni — projeler kapısının üslubu. `DELETE` yok: Flask 405 verir.

### `backend/main.py`

İmportlar dosyanın başında (`from backend import config`'in hemen altında, alfabeyle de oraya
düşüyor); bağlama, `_producers_bp`'nin altında ve `create_app` listesinin sonunda — 416'nın
dokunduğu DeepSeek satırlarından uzak. Kayıt öteki özelliklerin paylaştığı `_storage`'ı kullanır;
onun yorumu *"shared by both features"* diyor, artık üçüncüsü de var — *"every feature that keeps
files"* olur (üreticiler onu kullanmıyor).

## Bilinçli olarak yapılmayan

- Soru kapısı, agent, durdurma, adım kuralları — 420. Ekran — 425.
- Kilit yok: bir satır tek bir yazma; aynı dosyaya iki iş parçacığından satır eklemek fotoğraf
  kaydının da bugünkü hâli.
- `CODE-STANDARD.md`'nin dosya tablosu örnek olarak duruyor, eksiksiz bir liste değil
  (`reference_settings.json` de orada yok); dokunulmaz.
