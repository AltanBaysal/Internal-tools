# Madde 155 — Test turu tasarımı: kare sahnesinden doğar, promptu ayrı yazılır

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** test *(kırmızı commit'lenir)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 155

---

## Ne çivileniyor

Kareyi doğuran ve promptunu yazan tek çağrı ikiye ayrılıyor:

- **`add_scene(file, scenes)`** — kareleri doğuruyor, her birinde yalnız sahne cümlesi.
- **`write_frame_prompt(file)`** — sahnesi olup promptu boş her kareyi dolaşıyor, her biri için
  **ayrı ve küçük bir istek** atıyor, dönen alanları o kareye yazıyor.

Ve `-scenes.md` kalkıyor: sahne karenin içinde olunca eşleştirilecek bir şey kalmıyor.

**Bölünemiyor.** `add_scene` gelip `add_frames` hâlâ kare doğursaydı kareyi doğuran iki yol olurdu;
skill metni sonraya kalsaydı model, araçlarının desteklemediği bir akışı anlatan bir metin okurdu.

---

## `add_scene`

- `scenes` düz bir **string listesi**. Modelin kurduğu bir yapı yok, ve bir çağrı birden fazla
  cümle alabiliyor — 152'nin round bedeli burada doğmuyor.
- Her cümle bir kare açıyor: içinde `frame` ve `scene`, prompt alanları yok.
- 153'ün damgası basılıyor.
- **Kendi yapay zekası yok.** Ana model çağırıyor, cümleleri ana model yazıyor; araç kaydediyor.
- `scene` **kullanıcının dilinde**. Dosyanın geri kalanı İngilizce çünkü onu görsel model okuyor;
  bu bir brief, çıktı değil, ve prompta hiç girmiyor.
- Cevap numaraları söylüyor: `Added 3 scenes to bar-scene.json as frames 4-6.` Model bir sonraki
  adımda kareye numarasıyla hitap edecek.

## `write_frame_prompt`

**İmzası tek parametre.** Ana model hiçbir prompt alanı vermiyor.

**İstek araçsız, ve kendi sistem promptu var.** Bugünkü `engine.complete` uygulamanın kendi sistem
promptunu ekliyor — bir sohbet asistanını ve araçlarını anlatan bir metin, ki bu isteğin tam
tersi. O yüzden motora **yeni bir uç** ekleniyor:

```python
Engine.write_once(system, user, model) -> {"text": str, "usage": {...} | None}
```

Bir soru, bir cevap, araç yok, sohbet yok.

**İsteğin içinde ne var:** o karenin sahnesi, ve dosyadaki karakterler, kıyafetler, mekânlar. Başka
hiçbir şey. Ana agent bağlam aktarmıyor, önceki kare bilinmiyor.

**Cevap alanlar hâlinde geliyor** — `characters`, `location`, `action`, `camera`. `update_frame`'in
alacağı alanların aynısı: tek şekil, tek sözleşme.

**Doğrulama ortak.** Alt modelin uydurduğu bir karakter ya da kıyafet adı, `add_frames`'in kullandığı
aynı kontrolden geçiyor ve geçemiyor — o kare **boş kalıyor** ve raporda görünüyor.

**Boş kalan kare tekrar denenmiyor.** Araç sonda kaç kare yazıldığını ve kaçının boş kaldığını
söylüyor. Tekrar koşmak yalnız boşları dolduruyor, ve yeni sahneler eklendiğinde de aynı çağrı
onları dolduruyor.

**Paralel, beşerli dalgalar hâlinde.** İlk istek tek başına gidiyor ve sağlayıcının ön ek
önbelleğini ısıtıyor — hepsi birden uçarsa hiçbiri onu sıcak bulmaz. Beş, çünkü sağlayıcı dolu
havuzda 429 veriyor ve uygulama 429'da tekrar denemiyor: düşen istek düşen kare.

**Bir çağrıda en fazla 100 istek.** Fazlası raporlanıyor; zaten boşları dolduran bir araç.

**Jetonu damgaya yazılıyor.** `ToolResult` bir `spent` alanı kazanıyor ve `stream_answer` onu turun
hesabına ekliyor — yoksa bu araç faturayı görünmez bir yerden harcardı.

**Durdurulursa yarım kalıyor.** Uçmakta olanlar beklenmiyor, yenisi atılmıyor; yazılmış kareler
yerinde kalıyor, rapor yine geliyor.

## `run_tool` motoru nereden alıyor

`run_tool(file_store, project_id, name, arguments, engine=None, model="")` — iki yeni parametre,
ikisi de isteğe bağlı. `stream_answer` ikisini de elinde tutuyor; var olan her çağrı olduğu gibi
çalışmaya devam ediyor.

Motoru olmayan bir çağrıda araç **reddediyor**, çökmüyor.

## `skills.py` — iki metin de değişiyor

- `start-a-scenario`'nun 4. adımı ayrı dosya yerine `add_scene`'i çağırıyor; 5. adımdaki devir
  teslim tek dosya adı söylüyor.
- `generate-prompts-plus`'ın eşleştirme paragrafı gidiyor; kareleri elle yazmak yerine
  `write_frame_prompt` çağrılıyor.
- **Komşuluk kuralı prompt yazım metninden çıkıyor.** Alt istek önceki kareyi bilmiyor, ve
  bilmediği bir şeyi ondan istemek yalan olurdu. Dosyanın tamamını gören ana model gerekirse
  düzeltir.

---

## Testlerin şekli

### `add_scene`

- Cümleler kare oluyor, her birinde `scene` ve numara, prompt alanları yok.
- Var olan karelerin arkasına ekleniyor ve hepsi yeniden numaralanıyor.
- Cevap numara aralığını söylüyor.
- Boş liste, liste olmayan bir şey, ve string olmayan bir eleman reddediliyor — hiçbiri yazmıyor.
- Olmayan dosya ve bozuk JSON, bugünkü cümleleriyle.

### `write_frame_prompt`

- Sahnesi olan boş kare doluyor; alanlar alt modelin döndürdüğü şey.
- **Dolu kareye dokunulmuyor**, ve sahnesiz kareye de.
- İstek **araçsız** gidiyor, ve içinde sahne ile haritalar var.
- Alt modelin uydurduğu ad → o kare boş kalıyor, diğerleri doluyor.
- Bozuk cevap → aynısı.
- Rapor kaç yazıldığını ve kaç boş kaldığını söylüyor.
- Tekrar koşmak yalnız boşları dolduruyor.
- **Eşzamanlılık beşi geçmiyor** — sahte motor aynı anda kaç istek gördüğünü sayıyor.
- **İlk istek tek başına** — ısınma, ikinci istek başlamadan bitiyor.
- 100'den fazla boş kare varsa 100'ü yazılıyor, gerisi raporlanıyor.
- Harcama `spent` alanına yazılıyor.
- Motor verilmemişse ret.

### `skills.py`

- İki metin de `-scenes.md`'den söz etmiyor.
- `start-a-scenario` `add_scene`'i anıyor.
- `generate-prompts-plus` `write_frame_prompt`'u anıyor, eşleştirme paragrafı yok.

### Araç listesi ve modlar

- `add_scene` ve `write_frame_prompt` listede; `add_frames` **yok**.
- İkisi de `edit`'te izinsiz, `ask` ve `plan`'da soruyor.

---

## Kırmızının şekli

Büyük. İki araç da yok, motorun yeni ucu yok, `ToolResult`'ın alanı yok, skill metinleri eski.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```
