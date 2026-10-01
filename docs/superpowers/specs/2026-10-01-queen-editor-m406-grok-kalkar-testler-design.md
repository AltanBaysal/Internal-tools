# Madde 406 — Grok ve xAI anahtarı kalkar, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 6 · **Parça:** 406 · v8-3g · **Tur:** 1/2 — yalnız testler, kırmızı
commit'lenir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`, kararlar yol haritasının 406 satırında: grok kalmıyor
*(kullanıcı, 30 Eylül — "grok kalmıcak zaten")*, ve `XAI_API_KEY` notebook'tan da kalkar *(kullanıcı,
30 Eylül — "evet kalksın")*, QueenAgent'ın 383'ündeki gibi. Bir silmenin kanıtı bir yokluktur; bu
turun testleri neyin artık doğru olması gerektiğini söyler.

## Bugün ne oluyor

404'ten sonra uygulamada hiçbir şey grok'a sormuyor, ama grok'un izleri duruyor:
`backend/services/xai/` (istemci) ve onun testi `test_xai_client.py`; `config.py`'de `XAI_API_KEY`,
`XAI_MODEL`, `XAI_URL`, `XAI_TIMEOUT`; Queen AI'ın yazarlarını tutan dosyanın adı
`data/xai_prompt_writer.py`; README'de `XAI_API_KEY` satırı. Notebook `XAI_API_KEY`'i Secrets'tan
okuyor, CONFIG'de `xai_probe` ile yokluyor, Flask'a `QE_XAI_*` olarak veriyor, ve giriş hücresi onu
Secrets listesinde sayıyor. `test_notebook_installs_the_producer_groups.py`'de altı test yalnız bu
yoklama ve okuma için var. Birkaç test hata cümlesi örneği olarak `xAI HTTP 400/401` kullanıyor.

## Kurallar

1. **Queen Editor'ün yazılmış hiçbir dosyasında grok ve xAI geçmez** — kod, testler, README, notebook.
   Büyük-küçük harf fark etmez; `grok`, `xai` ve `x.ai` aranır.
2. **Hiçbir dosyanın ya da klasörün yolu onları adlandırmaz** — `services/xai/`, `xai_prompt_writer.py`,
   `test_xai_client.py` gibi.
3. **Uygulama `XAI_API_KEY` olmadan açılır.** Bu bugün de doğru (404): kompozisyon kökünün `/api/health`
   testi ortamda xAI'a dair hiçbir şey olmadan geçiyor. Testler artık ortama `QE_XAI_API_KEY`
   koymaz — o adı bilen bir test, kalkmış bir ayarı hâlâ var sayar.
4. **Notebook anahtarı ne okur, ne yoklar, ne uygulamaya verir, ne de giriş hücresinde sayar.**
   Kural 1'in notebook'a düşen hâli: tarama notebook'u da okur.

## Testler

### Tarama — `backend/tests/test_retired_provider.py` (yeni)

QueenAgent'ın 383'teki dosyasının aynısı, Queen Editor'ün klasöründe. Kelimeleri yazan tek dosya bu;
kendini taramaz.

- Queen Editor klasörü yürünür; `dist`, `node_modules`, `__pycache__` ve noktayla başlayan klasörler
  atlanır — derlenmiş, indirilmiş ya da makinede kalmış, kimsenin yazmadığı şeyler.
- `package-lock.json` atlanır: bütünlük özetinde harfler rastlantıyla yan yana gelebiliyor.
- **`BACKLOG.md` atlanır:** backlog kullanıcının sözleri ve o günkü durumun kaydı; içindeki grok
  cümleleri bir geçmişi anlatıyor, ve bu madde backlog'a dokunmaz.
- `test_the_sweep_reads_the_tool` — tarama `config.py`'yi görüyor; aşağıdaki ikisi hiçbir şey
  yürümeden geçemesin diye.
- `test_no_path_names_the_retired_provider` — hiçbir yol `grok|xai|x\.ai` içermiyor.
- `test_no_file_mentions_the_retired_provider` — hiçbir satır içermiyor; kalan her satır
  `yol:satır` olarak basılır.

### Notebook testleri — `test_notebook_installs_the_producer_groups.py`

Yalnız yoklama ve okuma için var olan altı test silinir: `xai_probe`'un varlığı, CONFIG'de çağrılması,
video kurulumuna bağlı durdurması, yalnız uyarması, xAI'ın cevabını basması, anahtarın kırpılması.
DeepSeek anahtarının testindeki "like the xAI key" sözü düşer; testin kendisi kalır. Notebook'un
anahtarı artık sormadığını tarama söyler (kural 4).

### Kompozisyon kökü — `test_composition_root.py`

İki testteki `monkeypatch.setenv("QE_XAI_API_KEY", "")` satırı ve "Both keys are empty" docstring'i
gider; testler DeepSeek'in boş anahtarıyla aynı şeyi sorar.

### xAI istemcisinin testi — `test_xai_client.py`

Silinir: test ettiği istemci kalkıyor.

### Yazarların dosyası — `test_video_prompt_writer.py`

Dosya yeni adından içe aktarılır: `backend.features.photo_generation.data.prompt_writer`. Ad,
dosyanın ne yaptığını söyler — iş bekleyen bir prompt'u yazar — ve hangi modelle konuştuğunu
söylemez: istemciyi kompozisyon kökü verir, ve model bir gün değişirse ad yine yalan söylemez.

### Hata cümlesi örnekleri

`test_photo_usecases.py`'de `xAI HTTP 401`, `ProjectScreen.test.jsx`'te ve `useGeneration.test.jsx`'te
`xAI HTTP 400` örnekleri `DeepSeek HTTP …` olur — yazar artık DeepSeek, ve testin sorduğu şey
cümlenin olduğu gibi taşınması. `ProjectScreen.test.jsx`'teki "a dead xAI key" yorumu "a dead key"
olur: olayın tarihi ve dersi kalır.

## Kırmızı beklenen

- Taramanın iki testi kırmızı: yollar ve satırlar.
- `test_video_prompt_writer.py` toplanırken `prompt_writer` modülü bulunamaz.
- Öteki her şey yeşil kalır; silinen testler ve değişen örnekler davranış sormuyor.

## Bilinçli olarak yapılmayan

- `BACKLOG.md`'ye dokunulmaz; içindeki `data/xai_prompt_writer.py` yolu dosya yeniden adlanınca
  eskir — rapora yazılır.
- Yol haritasına ve `docs/`'taki eski spec'lere dokunulmaz: onlar o günün kaydı.
- dist derlenmez: frontend'de değişen yalnız test dosyaları.
