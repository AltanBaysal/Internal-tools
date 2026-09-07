# Madde 138 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-01-queen-editor-m138-break-testler-design.md](2026-09-01-queen-editor-m138-break-testler-design.md)
**Kırmızı commit:** `6246106` — 2 kırmızı, 724 yeşil; ön yüz 587 yeşil.
**Dal:** `feat/v6`

## Ne yeşile dönecek

İki test. `test_the_positive_encoder_understands_break` grafiğin `36`'sını, ve
`test_the_notebook_installs_the_encoder_the_graph_asks_for` defterin kurduğu paketi bekliyor.

Üçüncü bir tanesi bu turda **kırmızıya düşüp geri dönecek**:
`test_the_notebook_says_how_many_custom_nodes_it_installs`. Liste 20'ye çıkınca başlıktaki 19'la
uyuşmayacak, ve o kırmızı bekçinin işini yaptığının kanıtı — başlık aynı commit'te düzeliyor.

## İki dosya

### 1. `workflow_api.json` — `36` sınıf değiştirir

```
"class_type": "CLIPTextEncode"  →  "CLIPTextEncodeBREAK"
"_meta": { "title": "CLIP Text Encode (Positive)" }  →  "CLIP Text Encode (Positive, BREAK)"
```

Girişler ellenmiyor: `text` → `["39", 0]`, `clip` → `["27", 1]` aynen kalıyor. Aday düğümün
girişleri de `text` + `clip`, çıkışı `CONDITIONING` — bugünkü ile birebir aynı şekil, ve API
biçiminde girişler isimle tutulduğu için sıra önemsiz.

**Yerinde düzenleniyor, yeniden export edilmiyor** *(yol haritasının kararı)*. Yeniden export
grafiğin ilgisiz yerlerini de yeniden yazar ve commit'te *"ne değişti"* okunmaz hâle gelir; şekil
aynı olduğu için o tura gerek yok. Diff iki satır.

`_meta.title` de düzeliyor: bir etiket ve düğümün türünü söylüyor, tür değişince onunla birlikte
düzelir *(CLAUDE.md — çelişen açıklama koda uydurulur)*. Hiçbir test onu okumuyor; ComfyUI'de grafiği
açan okuyor.

### 2. `queeneditor.ipynb` — defter paketi kurar

`CUSTOM_NODES` listesine bir satır, **foto bloğunun sonuna** — düğüm foto grafiğinin pozitif yolunda:

```python
("ComfyUI-ppm", "https://github.com/pamparamm/ComfyUI-ppm.git"),  # CLIPTextEncodeBREAK (pozitif yol)
```

Üstündeki markdown hücresinde iki sayı düzeliyor: başlıktaki `(19)` → `(20)`, ve *"ilk sekizi foto
grafiği"* → *"ilk dokuzu"*. İkincisi testle korunmuyor ama aynı cümlenin aynı olgusu; biri düzelip
öteki kalırsa cümle yalan söyler.

## Kurallar

- **İkisi tek commit.** ComfyUI kendisine gönderilen her düğümü doğruluyor: grafik yeni sınıfı
  isteyip defter paketi kurmazsa **her üretim düşer**, üstelik kurulum ücreti ödendikten sonra.
  Kırmızı testlerden biri zaten bu bağın bekçisi.
- **Negatif yol, adaptör, `model_groups.py`, ön yüz, `dist`** — hiçbiri ellenmiyor.
- **`dist` yeniden derlenmiyor**, çünkü ön yüz değişmiyor.

## Colab'da doğrulanacaklar — bugün cevaplanamayanlar

Üçü de yalnız gerçek bir koşuda görülebilir, ve üçü de **sessiz kalamaz**: ComfyUI kendi cümlesiyle
durur.

1. **Sınıf adı gerçekten `CLIPTextEncodeBREAK` mi.** Düğümün kaynağı okunarak yazıldı,
   çalıştırılarak değil.
2. **Paketin kendi bağımlılıkları.** Deponun kökünde `requirements.txt` **yok**, yalnız
   `pyproject.toml` var — yani defterin `if os.path.exists(req)` adımı bu paket için hiç çalışmıyor.
   Paket ekstra bir Python bağımlılığı istiyorsa kurulmayacak. Beklenti istememesi *(düğümler
   torch ve comfy içi API kullanıyor)*, ama beklenti kanıt değil.
3. **Kurulumun var olan üretime dokunmaması.** Paket örnekleyiciler, NegPip ve attention couple da
   taşıyor; hepsi grafiğe **eklenmedikçe** çalışmayan düğümler, yani bugünkü render'ın değişmemesi
   gerekiyor. Aynı seed ile kurulum öncesi/sonrası tek karakterli bir kare bunu söyler.

## Kabul kriteri — madde ne zaman bitmiş sayılır

**Takım yeşil yetmiyor.** Testler dosyanın ne dediğini kanıtlıyor, düğümün ne yaptığını değil.

**İlk yazılan kriter koşulamazdı, ve düzeltildi** *(1 Eylül)*. *"Aynı prompt, aynı seed, iki
üretim"* diyordu; seed'in sabitlenebildiği varsayılmıştı, kontrol edilmeden.
[start_batch.py](../../../queen-editor/backend/features/photo_generation/domain/usecases/start_batch.py)
kare başına `new_seed()` çağırıyor ve arayüzde seed alanı yok — yani iki üretim asla aynı seed'i
paylaşmıyor. Varsayım koşuya uydurulur, tersi değil.

**Fiilen koşulan karşılaştırma:** aynı düğüm, iki prompt — biri `BREAK`'li, öteki aynı metnin
`BREAK` yerine virgül taşıyan hâli — her birinden birkaç varyant. Düğüm değiştirmeye gerek yok:
`BREAK` bilen kodlayıcı, promptta `BREAK` yokken düz kodlayıcı gibi davranıyor. Seed'ler farklı,
yani okunacak şey tek bir kare değil **dağılım**.

**Ve "gerçekten böldü mü" ayrıca test edilmiyor.** Düğümün kodu düz `text.split("BREAK")` yapıyor,
ve ComfyUI kendisine gönderilen her düğümü doğruluyor — düğüm yoksa ya da adı yanlışsa üretim hiç
başlamaz. Üretim bittiyse düğüm çalıştı. Geriye kalan tek soru faydası, ve onu gözle bakan
kullanıcı cevaplıyor.

**Sonuç — kullanıcı yargısı, 1 Eylül:** `BREAK`'li kareler daha iyi. Sayılmadı, kareler
paylaşılmadı; kayda geçen şey kullanıcının kendi okuması. Madde bu yargıyla kapanıyor.

## Bilerek yapılmayanlar

**139.** Promptun içine `BREAK`'i QueenAgent yazacak. Bu turda `BREAK` elle yazılarak denenir.

**Sıra düzeltmesinin sorgulanması.** 139'un işi.

**Attention Couple.** 141, ve şartı bu maddenin ölçüsü.
