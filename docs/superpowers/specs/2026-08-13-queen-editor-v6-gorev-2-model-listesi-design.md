# Görev 2 — Model listesi grafiğin istediğini söyler

**Roadmap:** [v6](../plans/2026-08-13-queen-editor-v6-roadmap.md) · Blok 1

## Sorun

`model_groups.py`'nin video grubu, Görev 1'de repoya giren grafiğin gerçekten yüklediği dosyalarla
örtüşmüyor. Üretici paneli grubu sayarak "video kurulu" diyor; graf ise olmayan bir dosya isteyip
render'ı düşürüyor. Panelin verdiği söz ile motorun gördüğü disk ayrı.

İki uyuşmazlık var, ikisi de `photo_to_video.ipynb`'in model hücresiyle karşılaştırılarak
doğrulandı — o defter bu grafiği çalıştırıyor, yani hangi dosyanın hangi adla nereden indiğini
bilen taraf o:

| Grafın yüklediği | Klasör | Grupta | Nereden |
|---|---|---|---|
| `SmoothMix_I2V_v2_High.safetensors` | diffusion_models | ✓ | Civitai (token) |
| `SmoothMix_I2V_v2_Low.safetensors` | diffusion_models | ✓ | Civitai (token) |
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | text_encoders | ✓ | HF |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` | loras | ✓ | HF |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` | loras | ✓ | HF |
| **`Wan2_1_VAE_fp32.safetensors`** | vae | **✗ yanlış ad** | HF (`wan_2.1_vae.safetensors` bu adla iner) |
| **`SmoothMix_Animations_XXX_High.safetensors`** | loras | **✗ yok** | Civitai (token) |
| **`SmoothMix_Animations_XXX_Low.safetensors`** | loras | **✗ yok** | Civitai (token) |

## Kararlar

1. **Ad, grafiğin dediğidir.** VAE girdisinin adı `Wan2_1_VAE_fp32.safetensors` olur; **URL
   değişmez**. HuggingFace'teki dosyanın kendi adı `wan_2.1_vae.safetensors`, defter de onu bu adla
   indiriyor — ComfyUI dosyayı diskteki adıyla arar, kaynaktaki adıyla değil. Kurucunun zaten
   `name` ile `url`'ü ayrı tutması bunu mümkün kılıyor.
2. **İki Animations LoRA'sı gruba girer**, `url: None` ile — Civitai'nin token'ı arkasındalar,
   tıpkı yanlarındaki SmoothMix çifti gibi. Kurucu böyle bir satıra gelince durup söylüyor; bu
   zaten tasarlanmış davranış.
3. **Liste elle değil, grafikten doğrulanır.** Test grafiği okur, adı geçen her `.safetensors`
   dosyasını toplar ve her birinin grupta olduğunu iddia eder. Elle yazılmış bir liste, grafın bir
   sonraki değişiminde yine sessizce eskir.
4. **Toplama kuralı: grafiğin içindeki, `.safetensors` ile biten her metin.** İç içe geçmiş
   yapılara da bakılır — Power Lora Loader LoRA'larını `lora_1: {on, lora, strength}` gibi
   sözlüklerin içinde taşıyor, düz bir tarama onları kaçırırdı.
5. **Öksüz node'lar kendiliğinden dışarıda kalır.** `356`/`357` GGUF yükleyicilerinin
   `unet_name`'i `null`; bir metin olmadığı için toplamaya girmiyor. Erişilebilirlik analizi
   yazmaya gerek yok — dolu olan her alan zaten gerçekten yüklenen bir dosya.
6. **`.safetensors` dışı dosyalar kapsam dışı.** Graf `flownet.pkl` de anıyor (RIFE ara kare);
   onu custom node kendi indiriyor, defter de listesine almamış. Kural burada da defterle aynı
   kalır.
7. **Foto grubu boş kalır.** `GROUPS["photo"] = []` bilinçli: foto checkpoint'ini defter kuruyor
   ve hangisi olacağı kullanıcının seçimi. Test yalnız video grafiğine bakar.

## Ne değişiyor

| Yer | Bugün | Yarın |
|---|---|---|
| VAE girdisi | `wan_2.1_vae.safetensors` | `Wan2_1_VAE_fp32.safetensors` (URL aynı) |
| Animations LoRA'ları | yok | iki satır, `url: None` |
| Grup ↔ graf tutarlılığı | kimse bakmıyor | test bakıyor |

## Testler

`queen-editor/backend/tests/test_workflow_asset.py`:

- Shipped video grafiğinde adı geçen her `.safetensors`, `GROUPS["video"]` içinde bir satırla
  karşılanır — eksik olan varsa test onu adıyla söyler.
- Toplayıcı iç içe sözlükleri de görür: sekiz dosyanın ikisi Power Lora Loader'ın içinde.

Ters yön (**grupta olup grafta olmayan**) iddia edilmez: bir dosyanın grafikte görünmeden
gerekmesi mümkün (custom node'un kendi beklentisi), ve fazladan bir indirme render'ı düşürmez.
Kırmızıya düşen taraf hep eksik olan taraftır.

## Öz eleştiri

- *URL'yi değiştirmeden adı değiştirmek karışıklık yaratmaz mı?* — Yaratır, o yüzden satıra
  nedeni yazılıyor: dosya HF'te başka adla duruyor, ComfyUI diskteki adı arıyor. Alternatif —
  grafiği düzenleyip `wan_2.1_vae.safetensors` yazmak — Görev 1'in "kendi yazmadığımız grafiği
  düzenlemeyiz" kararını bozar ve çalışan defterle arayı açar.
- *Test grafiği okuyorsa, grafiği değiştiren biri testi de kırar mı?* — Evet, ve istenen bu:
  yeni bir model ekleyen bir export, grup güncellenene kadar kırmızı kalır.
- *`url: None` satırı kullanıcıyı ortada bırakmaz mı?* — Bırakmaz; kurucu o satıra gelince durup
  dosyayı adıyla söylüyor. Civitai token'ı olmadan indirmenin başka yolu da yok.
