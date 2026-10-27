# Madde 406 — Grok ve xAI anahtarı kalkar, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 6 · **Parça:** 406 · v8-3g · **Tur:** 2/2 — kırmızı testleri yeşile
çeviren kod. **Testler:** [m406 test turu](2026-10-01-queen-editor-m406-grok-kalkar-testler-design.md).

**Kullanıcıdan gereken — yok.** Kararlar test spec'inde; buradakiler neyin nasıl silineceği.

## Parçalar

### 1. xAI istemcisi — `backend/services/xai/`

Klasör bütünüyle silinir (`__init__.py`, `client.py`). 404'ten beri hiçbir yer onu içe aktarmıyor.

### 2. Ayarlar — `backend/config.py`

`XAI_API_KEY`, `XAI_MODEL`, `XAI_URL`, `XAI_TIMEOUT` ve üstlerindeki iki yorum kalkar. DeepSeek'in
model ve adres satırlarının üstündeki yorum "unlike xAI's two" sözünü bırakır; neden ortamdan
okunmadıkları — onları kimse yoklamıyor — kalır.

### 3. Yazarların dosyası — `data/xai_prompt_writer.py` → `data/prompt_writer.py`

`git mv` ile, içeriğine dokunmadan: docstring'i zaten xAI'ı anmıyor, ve metinler sahibinin. Dosya
iş bekleyen bir prompt'u yazar; hangi modelle konuştuğunu kompozisyon kökü söyler. `main.py`'nin
içe aktarması ve `services/deepseek/client.py` docstring'indeki yol yeni adı söyler. Aynı dalgada
407 bu dosyanın yazarlarına dokunuyor; içerik değişmediği için git birleştirirken yeniden adlandırmayı
tanır.

### 4. Notebook — `queeneditor.ipynb`

Kod hücrelerinde yalnız bölüm başlıkları; yorum eklenmez.

- **Giriş (markdown):** Secrets listesindeki "H3 için `DEEPSEEK_API_KEY` (H3 prompt'unu yazan Queen
  AI — QueenAgent'ınkiyle aynı secret); WAN ve ses için `XAI_API_KEY` (onların prompt'unu yazan dil
  modeli)." cümlesi "video ve ses için `DEEPSEEK_API_KEY` (prompt'larını yazan Queen AI —
  QueenAgent'ınkiyle aynı secret)." olur. 404'ten beri WAN'ı ve sesi de DeepSeek yazıyor; yalnız
  `XAI_API_KEY`'i silmek H3 dışında anahtar gerekmiyormuş gibi okunurdu.
- **CONFIG:** `XAI_API_KEY`'i Secrets'tan okuyan `try` bloğu; `# === xAI ===` bölümü bütünüyle
  (`XAI_MODEL`, `XAI_URL`, `xai_probe`); sondaki `if not XAI_API_KEY: … else: xai_probe(…)` dalı.
  Öteki satırlar ve sıraları aynı kalır.
- **Flask'ı başlatan hücre:** `flask_env`'deki `"QE_XAI_API_KEY"`, `"QE_XAI_MODEL"`, `"QE_XAI_URL"`
  satırları.

### 5. README — Secrets tablosu

`XAI_API_KEY` satırı silinir. `DEEPSEEK_API_KEY` satırı zaten bütün prompt'ları söylüyor.

## Bilinçli olarak yapılmayan

- `BACKLOG.md` ve yol haritası değişmez; `docs/`'taki eski spec'ler o günün kaydı.
- Yazarların metinlerine (`VIDEO_INSTRUCTION`, `H3_VIDEO_INSTRUCTION`, `LOOP_RULE`, `LINKED_RULE`,
  `AUDIO_INSTRUCTION`) dokunulmaz.
- Ekran değişmez; dist yok.

## Bitti sayılır

Dört satır yeşil; `queen-editor/` altında, `dist`, `node_modules`, `package-lock.json` ve `BACKLOG.md`
dışında, `grok` ve `xai` geçen tek dosya taramanın kendisi.
