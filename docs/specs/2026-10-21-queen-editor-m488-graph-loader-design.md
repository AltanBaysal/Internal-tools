# Madde 488 · Grafik dosyasını okuyan kodun üç kopyası tek yerde — tasarım

**Tarih:** 21 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
488 · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde `ALIGNED`; kullanıcı kararı mimara bıraktı (21 Ekim — *"architect ne diyorsa o"*),
mimarın tasarımı aşağıda uygulanan.

## Ne, neden

482'nin reviewer'ı buldu: fotoğraf, Krea ve H3 üreticileri ComfyUI grafiğini her biri kendi
`_load`'unda okuyor — dosyayı açıp `json.load`, UI formatını (`"nodes"` anahtarı) reddetme, node
id'lerini denetleme. Kopyalar ayrışmış:

| | Eksik dosya | UI formatı mesajı | Eksik node mesajı |
|---|---|---|---|
| Fotoğraf | çıplak `FileNotFoundError` | sabit `workflow_api.json` adı | ilk eksik id |
| Krea | çıplak `FileNotFoundError` | "Krea grafiği" | ilk eksik id |
| H3 | cümleli `RuntimeError` | dosyanın gerçek adı | ilk eksik id |

## Ne değişir

1. **Yeni modül** `queen-editor/backend/features/photo_generation/data/comfy_graph.py`, tek fonksiyon:
   `load_graph(path, nodes)` — *`path`'teki API biçimli grafiğin taze bir kopyası, `nodes`'taki her
   id'yi taşıyan.* H3'ün sürümünden genelleştirildi, `name = os.path.basename(path)`:
   - dosya yoksa: `RuntimeError("Grafik yok: {path} — ComfyUI'de 'Workflow → Export (API)' ile
     kaydet ve repoya commit'le")`, `from None` — H3'ün cümlesi, "Video" kelimesi düşmüş;
   - UI formatındaysa: `"{name} UI formatında — ComfyUI'de 'Workflow → Export (API)' ile kaydet"`;
   - eksik node'lar varsa: tek mesaj, eksik id'lerin hepsi `nodes` sırasıyla —
     `"{name} grafiğinde {id, id} node yok — graf değişmiş, node id'lerini güncelle"`.

   Dosyanın okunamaması (`FileNotFoundError` dışındaki `OSError`) ve bozuk JSON bugünkü gibi
   olduğu gibi yükselir: yalnız "yok" bir cümleye çevrilir.
2. **Fotoğraf ve Krea:** `_load` silinir; `_graph` / `generate` `load_graph(self._workflow_path,
   NODES)` çağırır. `NODES` her modülde, H3'teki gibi, o üreticinin her render'da yazdığı node'lar:
   fotoğrafın `"3"`, `"4"`, `"40"`, `"45"`; Krea'nın `"53:19"`, `"53:3"`, `"53:5"`. Fotoğrafın
   koşullu denetimleri (Width/Height, Batch Size, LoRA node'ları) yerinde kalır — onlar yalnız o
   seçenek istenince aranır. İki modülde `json` importu artık kullanılmadığından düşer.
3. **H3:** `_load(path, happy_ending)` kalır, ince bir sarmalayıcı olarak: `load_graph(path, NODES)`,
   sonra `happy_ending` ise HMCumshot adımı.

## Hata mesajları değişir

Davranış ve ekran değişmez; değişen yalnız üç hata cümlesi:

- **Fotoğraf**, UI formatı ve eksik node mesajında sabit `workflow_api.json` / "Workflow'da" yerine
  dosyanın gerçek adını söyler.
- **Krea**, "Krea grafiği" yerine `workflow_photo_krea2_api.json` der.
- **Eksik fotoğraf ya da Krea grafiği**, çıplak `FileNotFoundError` yerine cümleli bir
  `RuntimeError` olur. Kuyruk ikisini aynı yakalar (`run_loop`'un `except Exception`'ı); değişen
  yalnız ekrana düşen satır — bugün `[Errno 2] No such file or directory: '…'`.
- Eksik node mesajı, birden çok id eksikse hepsini birden sayar (bugün ilk eksiği).

## Maliyet

Değişmez. `load_graph` çağrı başına bir `open` ve bir okuma — her üreticinin `_load`'unun bugün
yaptığı kadar; render başına bir okuma (H3'ün `seconds()`'ı bir tane daha, bugünkü gibi). Ağ yok.
Grafik dosyaları repodaki `assets/`'ten okunur, Drive'dan değil.

## Ne bozulabilir, sınırlar

- Okuma salt okumadır, hiçbir şey yazılmaz; kopya her çağrıda tazedir, yamalar dosyaya dönmez.
- `path` yapılandırmadan (`config`) gelir, URL'den değil.
- Mesajlardaki `path`, repodaki bir asset yoludur; sır taşımaz.

## Test

- Yeni `queen-editor/backend/tests/test_comfy_graph.py`: eksik dosya (cümle ve yol), UI formatı
  (dosya adı ve "Export (API)"), eksik node'lar (hepsi tek mesajda), tam grafiğin olduğu gibi
  dönmesi ve her çağrının taze kopya vermesi.
- Üreticilerin bugünkü UI formatı ve eksik node testleri (`test_comfy_photo_generator.py`,
  `test_comfy_krea_photo_generator.py`, `test_comfy_h3_video_generator.py`) değişmeden geçer.

## Bitti sayılır

- `load_graph` üç üreticinin grafiği okuduğu tek yer; `json.load` ile grafik okuyan başka kopya yok.
- `python -m pytest queen-editor -q` yeşil.
