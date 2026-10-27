# WAN 2.2 T2V — LoRA takası: SmoothMix Animations seti (tasarım)

**Tarih:** 2026-07-21 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

`wan22-smooth-t2v`'nin iki notebook'unun indirdiği LoRA seti değişsin: I2V tabanlı `WAN_General_NSFW` çifti çıkar, SmoothMix yazarının **T2V-native** üç çifti girer. İki notebook'un indirme listesi hizalanır ve **hizalı kalır** — bu, kullanıcının kalıcı kuralı.

## Bağlam

Eski çift (model **1307155**, version 2073605/2083303) `Wan Video 2.2 **I2V**-A14B` tabanlı — T2V grafı için belgeli uyumsuzluk. `dependencies.md` "çıktı bozuksa önce bunu bypass et" uyarısıyla yaşıyordu ve `instructions.md` tuzağa bir kez düşüldüğünü kaydediyor. Dosya inip duruyordu ama güvenilmiyordu.

Yeni set model **2040641** ("SmoothMix Animations WAN 2.2") — çekirdek checkpoint'le **aynı yazar**. Version ID'ler ve base'ler Civitai API'sinden doğrulandı (2026-07-21):

| Çift | High / Low version ID | Base | Trigger word'ler |
|---|---|---|---|
| Style | 2318650 / 2318707 | T2V-A14B ✅ | `SmoothMixAnime`, `SmoothMixRealism` |
| Animation | 2309690 / 2309689 | T2V-A14B ✅ | `SmoothMixAnime`, `SmoothMixRealism` |
| Futanaris and Males | 2476982 / 2474616 | T2V-A14B ✅ | `futanari`, `flaccid`, `erect`, … |

Dosya başına ~300 MB; altı dosya ~1.8 GiB. Yazarın önerdiği strength 0.5–1.0.

**Koleksiyonun XXX Animations çifti (2376136/2376143) bilerek dışarıda** — setteki tek I2V tabanlı çift; eski çifti atma sebebi aynen ona da uygulanır. Kullanıcı kararı: inmesin.

## Kararlar

| Karar | Gerekçe |
|---|---|
| **Altı LoRA, iki notebook'ta birebir aynı blok** | Kullanıcı kuralı: *"api ve manuel align olsun her zaman."* Teknik getirisi somut: `api.ipynb` grafiği Drive'daki export'tan okur; kullanıcı UI'da LoRA'lı bir graf export ettiği gün dosyalar API tarafında hazırdır, notebook'a dokunmak gerekmez. |
| **Başka LoRA yok** | Kullanıcı kararı. Liste = bu altı dosya; NSFW çifti ve XXX çifti inmez. |
| **Adlandırma: `SmoothMix_<Set>_<High\|Low>.safetensors`** | Checkpoint satırlarının konvansiyonu (`SmoothMix_T2V_High_v3`). LoRA'da grafın beklediği sabit ad yok (loader'lar boş); `fetch()` hedef adla kaydeder. |
| **İndirmek ≠ uygulamak** | API grafiğinin Power Lora Loader'ları (**109**/**110**) boş. LoRA'lar videoya ancak UI'da takılıp **Export (API)** ile `workflow_api.json` güncellenince etki eder. Bu ayrım `api.ipynb` başlık hücresine yazılır ki "indirdim ama fark yok" sürprizi doğmasın. |
| **Trigger word şart** | LoRA'yı takmak yetmez: `SmoothMixAnime` ya da `SmoothMixRealism` prompt'ta geçmeli (Futanari çifti kendi kelimeleriyle). Kullanım: High → loader **109**, Low → **110**, strength 0.5–1.0'dan başla. |
| **"LoRA EKLEME" uyarısı distill'e daraltılır** | 18 Temmuz bulgusu ("sıfır LoRA en iyi") **lightx2v/distill** LoRA'sının çift uygulanması hakkındaydı — checkpoint'e merge'lü. Stil/hareket LoRA'ları o mekanizmanın dışında; uyarı genele yazıldığı için 109/110'un yeni kullanımıyla çelişiyordu, kapsamı netleştirilir. Bulgunun kendisi silinmez. |
| **`imageToVideo.ipynb`'ye dokunulmaz** | Aynı eski NSFW çiftini o da indiriyor ama o araç **I2V** — LoRA orada base'iyle uyumlu. Takas yalnız T2V klasörünü ilgilendirir. |

## Değişiklikler

| Dosya | Değişim |
|---|---|
| `manual.ipynb` cell-8 | `CIVITAI_MODELS`: 2 NSFW satırı → 6 yeni satır; üstteki I2V uyarı yorumu yeni duruma göre yazılır (İngilizce) |
| `api.ipynb` cell-10 | `LORA` klasör sabiti eklenir + aynı 6 satır; indirme özeti `loras/` klasörünü de listeler |
| `api.ipynb` cell-0 | "LoRA yok" notu → "distill LoRA yok (lightx2v merge'lü); stil LoRA'ları iner, graf export'unda etkinleşir" |
| `dependencies.md` | §2: kaynak model 2040641, tablo 6 satır (✅), trigger word + strength notu; "hangi notebook neyi indirir" tablosu "ikisi aynı seti indirir, ~35.3 GiB"e sadeleşir; hizalama kuralı bir cümleyle kayda geçer |
| `instructions.md` | LoRA blockquote'u distill'e daraltılır; kullanım adımlarına LoRA takma tarifi (109/110, strength, trigger word); Notlar'daki NSFW maddesi yeni duruma göre yazılır |

İki notebook da artık ~35.3 GiB indirir (eskiden manual ~34.7, api ~33.5).

## Doğrulama

Statik (tool ile):
1. Grep `WAN_General_NSFW|1307155` → `wan22-smooth-t2v/` altında 0 eşleşme; `imageToVideo.ipynb`'de aynen duruyor
2. Grep altı version ID → `manual.ipynb`, `api.ipynb`, `dependencies.md` üçünde de var
3. İki notebook'un LoRA blokları birebir aynı (diff ile göz kontrolü)
4. Hücre sayıları değişmemiş

Colab (kullanıcıda, A100):
1. `manual.ipynb` Run all → gated probe 8 asset geçer; özet `loras/` altında 6 dosya ~300 MB gösterir
2. UI'da Style çifti: High→109, Low→110, strength 0.5, prompt'ta `SmoothMixAnime` → üret
3. Aynı prompt LoRA'sız → karşılaştır: stil kontrolü geldi mi, kalite düştü mü?
4. Beğenilirse Export (API) → Drive'daki `workflow_api.json` güncellenir; `api.ipynb` kod değişikliği olmadan LoRA'lı üretir

## Kapsam dışı

- **Grafik değişikliği** — iki workflow JSON'una da dokunulmuyor; LoRA'ların grafa girmesi kullanıcının UI denemesi + export kararı
- **XXX Animations çifti** — inmiyor; ileride istenirse I2V riski bilinerek ayrı karar
- **`imageToVideo.ipynb`** — I2V aracı, kendi LoRA'sı kendine
- **Prompt tarafı** — trigger word'lerin PROMPTS listesine nasıl yazılacağı kullanıcının prompt içeriği, araç değişikliği değil
