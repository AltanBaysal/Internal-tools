# Madde 155 — Uygulama turu tasarımı: kare sahnesinden doğar, promptu ayrı yazılır

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** uygulama *(yeşile götürür)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 155 ·
[test turu tasarımı](2026-09-03-queenagent-m155-sahne-testler-design.md)

---

## Otuz bir kırmızı, altı dosya

`ports.py` bir uç, `xai_engine.py` onun karşılığı, `tools.py` iki araç ve bir alan,
`stream_answer.py` harcamanın toplandığı yer, `modes.py` iki ad, `skills.py` iki metin.

---

## `ports.py` — `Engine.write_once`

```python
def write_once(self, system: str, user: str, model: str = "") -> dict:
    """One question, one answer. No tools, no conversation, no memory of another call."""
```

`{"text": str, "usage": {...} | None}` döndürüyor.

**`complete` neden yetmiyor:** `XaiEngine._for_xai` her mesaj dizisinin başına uygulamanın kendi
`SYSTEM_PROMPT`'unu koyuyor — bir sohbet asistanını, projesini ve araçlarını anlatan bir metin. Bu
isteğin istediği tam tersi: yalnız prompt yazmayı bilen, başka hiçbir şeyi olmayan bir model.

## `xai_engine.py` — karşılığı

Aynı istemciyi kullanıyor, mesajları kendisi kuruyor: `system` ve `user`, araç yok.

Harcama istemcinin döndürdüğü `usage`'dan geliyor; yoksa `None`.

## `tools.py` — `_add_scene`

- `scenes` düz bir string listesi. Boş liste, liste olmayan bir şey, ve string olmayan bir eleman
  reddediliyor — hiçbiri yazmıyor.
- Her cümle `{"scene": …}` diye bir kare açıyor, sonra `_renumber` damgayı basıyor.
- Cevap numara aralığını söylüyor: `Added 2 scenes to scene.json as frames 3-4.` Tek cümlede
  `as frame 3.`

## `tools.py` — `_write_frame_prompt`

**Hangi kareler:** `scene` dolu ve `action` boş olanlar. En fazla 100'ü.

**Her biri için bir istek:**

- `system` — prompt yazım metni, kodda bir sabit *(`WRITING`)*.
- `user` — haritalar ve o karenin sahnesi. **Değişmeyen kısım başta**, sahne sonda: sağlayıcının ön
  ek önbelleği ilk istekten sonra isabet etsin.

**Cevap:** JSON metni, `characters` / `location` / `action` / `camera`. Ayrıştırılamıyorsa o kare
boş kalıyor.

**Doğrulama ortak.** `_unknown_names` — `add_frames`'in kullandığı aynı fonksiyon. Alt modelin
uydurduğu ad geçemiyor, ve o kare boş kalıyor.

**Dalgalar:** ilk istek tek başına, sonrası `ThreadPoolExecutor(max_workers=5)`.

- İlk istek tek başına, çünkü hepsi birden uçarsa hiçbiri ön eki sıcak bulmaz.
- Beş, çünkü sağlayıcı dolu havuzda 429 veriyor ve bu uygulama 429'da tekrar denemiyor: düşen istek
  düşen kare.

**Yazma sırası:** dönen sonuçlar kare numarasına göre yerleşiyor, tamamlanma sırasına göre değil.
Paralellik dosyanın içeriğini değiştirmemeli — yalnız ne kadar beklendiğini.

**Dosya bir kez yazılıyor**, hepsi bittikten sonra. Her istekten sonra yazmak, iki iş parçacığının
aynı dosyayı çiğnemesi demek olurdu.

**Rapor:** `Wrote 12 frames; 3 left empty.` Hepsi yazıldıysa ikinci yarısı yok. Yüz sınırına
takılmışsa kaçının beklediği de söyleniyor.

**Harcama:** her isteğin `usage`'ı toplanıp `ToolResult.spent`'e yazılıyor.

**Motor yoksa ret**, çökme değil — bu modülün her ıskası gibi.

## `tools.py` — `ToolResult.spent`

Beşinci alan, varsayılanı `None`. Var olan her `ToolResult(...)` çağrısı olduğu gibi çalışmaya devam
ediyor.

## `stream_answer.py` — harcamanın toplanması

Araç koştuktan sonra `result.spent` varsa turun toplamına ekleniyor. Motorun kendi `usage`'ı gibi,
ama **eklenerek**: bunlar ayrı isteklerin bedeli, aynı çağrının yeni bir toplamı değil.

## `run_tool` imzası

`run_tool(file_store, project_id, name, arguments, engine=None, model="")` — ikisi de isteğe bağlı,
yani var olan her çağrı ve her test olduğu gibi kalıyor.

## `skills.py`

- `start-a-scenario` 4. adım: `add_scene`. 5. adım: tek dosya adı.
- `generate-prompts-plus`: kareleri yazmıyor, `write_frame_prompt` çağırıyor. Eşleştirme paragrafı
  ve beşerli grup gitti.
- **Komşuluk kuralı prompt yazım metnine girmiyor.** Alt istek önceki kareyi bilmiyor; bilmediği bir
  şeyi ondan istemek yalan olurdu.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```
