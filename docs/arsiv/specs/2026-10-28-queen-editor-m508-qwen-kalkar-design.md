# Madde 508 · Qwen kalkar — tasarım

**Tarih:** 28 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-7),
508 · v11-7 · **Dal:** `feat/queen-editor-v11` · **Plan:**
[2026-10-28-queen-editor-m508-qwen-kalkar-plan.md](../plans/2026-10-28-queen-editor-m508-qwen-kalkar-plan.md)
· **Önce:** 499 (Qwen Image 2.1 Turbo'yu Queen Editor'e soktu, Krea'ya SNOFS + Slime'ı ve Boş'u ekledi)

## Ne, neden

Kullanıcı, 28 Ekim, koşunun sonundaki Colab denemesinde — *"qweni kaldıralım iyi bir şey üretmiyor
gereksiz kalabalık"*. Qwen Image 2.1 Turbo Queen Editor'den bütünüyle çıkar: model listesinde, LoRA
kutusunda ve defterin CONFIG'inde görünmez, defter onun dosyalarını indirmez. 499'un Qwen'le gelen her
parçası gider; Krea'nın 499'daki işi — SNOFS, SNOFS + Slime, Boş, kendi kutusu ve `lora_chain.py` —
kalır. Daha önce Qwen'le çizilmiş fotoğraflar Drive'da durur; bu madde Drive'daki hiçbir şeye dokunmaz.

## Çıkanlar

| Yer | Çıkan |
|---|---|
| `backend/features/photo_generation/domain/catalog.py` | `QWEN`, `SLIME_QWEN`, `QWEN_LORAS` ve `MODELS`'taki Qwen satırı |
| `backend/features/photo_generation/data/comfy_qwen_photo_generator.py` | dosyanın tamamı |
| `backend/main.py` | `ComfyQwenPhotoGenerator`'ın import'u ve `PhotoByModel`'e verilişi |
| `backend/config.py` | `QWEN_WORKFLOW_PATH` |
| `assets/workflow_photo_qwen_api.json` | dosyanın tamamı |
| `backend/features/producers/domain/model_groups.py` | `QWEN_FILES` ve fotoğraf grubunun `any`'sindeki yeri |
| `queeneditor.ipynb` | `PHOTO_QWEN21TURBO` kutucuğu ve assert'teki yeri; `PHOTO_MODELS`'taki satır; `HF_QWEN`, `CIVITAI_QWEN`, `INSTALL_QWEN`; `CIVITAI_PHOTO`, `HF_PHOTO`, `PHOTO_GIB` ve `FOLDERS`'taki Qwen parçaları; klon hücresinin grafik listesindeki `workflow_photo_qwen_api.json` — "beş grafik" yazısı "dört grafik" olur |
| testler | `test_comfy_qwen_photo_generator.py`'nin tamamı; öteki dosyalardaki Qwen satırları ve Qwen testleri |

Yorumlarda "Krea ve Qwen" diyen yerler yalnız Krea'yı söyler: `catalog.py`, `photo_by_model.py`,
`comfy_graph.py`, `lora_chain.py`, `comfy_krea_photo_generator.py`, `fix_photo.py`, `regenerate.py`,
`model_groups.py`, `list_producers.py`, `main.py` ve `queen-editor/BACKLOG.md`'nin 501'den kalan
maddesi.

**Kalanlar:** Krea'nın grafiği, üreticisi, kutusu ve `lora_chain.py` (Krea'nın üreticisi onu kullanıyor);
Krea'nın Qwen3-VL kodlayıcısı ve Qwen Image VAE'si (`qwen3vl_4b_fp8_scaled`, `qwen_image_vae`) ve
H3'ün Qwen3-VL'i — bunlar Qwen modeli değil, Krea'nın ve H3'ün dosyaları. Ekranın kaynağında Qwen
geçmiyor: `GeneratePanel.jsx` ve `PhotoDetail.jsx` modeli satırdan okur, kimliğiyle bilmez. Bu yüzden
yalnız iki ekran testindeki Qwen örnekleri çıkar, `dist` değişmez. Dokunulmayanlar:
`collab-toolbox/photo_experiments/qwen-image-21/` (484'ün denemesi) ve `docs/arsiv/`.

## Eski veri: `qwen21turbo` diyen satır ya da ayar

Yeni kod yazılmıyor: `qwen21turbo` artık katalogda olmayan herhangi bir değer gibi okunur, ve bugünün
kuralları bunu çökmeden ve başka bir modelle çizmeden karşılıyor. En basit güvenli yol bu; ayrı bir
"kaldırılan modeller" listesi eklenmiyor.

- **Kuyruktaki eski satır.** `PhotoByModel` kendi grafiği olmayan her değeri fotoğraf grafiğine verir.
  Qwen'in kutusu yalnız Translucent Penetration ve Boş'tu, ve 499'dan beri satır çizilenin kendisini
  yazıyor; bu yüzden eski bir Qwen satırı ya `translucent_penetration` ya `none` taşır.
  - `translucent_penetration`: ortak kutuda böyle bir satır yok, çizim
    *"Tanınmayan LoRA: translucent_penetration — …"* ile durur (238'in kuralı).
  - `none`: model kimliği dosya adı gibi checkpoint yükleyicisine yazılır, ComfyUI onu kendi sözüyle
    reddeder (*"Value not in list: ckpt_name: 'qwen21turbo' …"*).

  İkisinde de sıra üç denemeden sonra durur ve hata sıra panelinde görünür (`run_loop`'un bugünkü
  davranışı); satır borçlu kalır, kullanıcı onu sıradan çıkarır. Kare başka bir modelle çizilmez.
- **Eski bir Qwen fotoğrafında Yeniden üret / Düzelt.** Satırın modelini ve LoRA'sını taşır
  (`catalog.drawn_with`, bilmediği modelde verileni korur), yeni satır yukarıdaki gibi durur.
- **Projenin kayıtlı ayarı `qwen21turbo`.** Panel bugünkü "gitmiş model" kuralıyla açılır: model kutusu
  `qwen21turbo`'yu kimliğiyle seçili tutar ve altında *"Bu model artık kurulu değil."* yazar; LoRA kutusu
  ortak kutudur. Kullanıcıyı sessizce başka bir modele kaydırmak, o kuralın yazdığı gibi, seçmediği bir
  modelle çizmek olurdu. Kayıtlı LoRA `translucent_penetration` ise Kuyruğa ekle onu
  *"Tanınmayan LoRA: … — listeden başka bir LoRA seç."* ile reddeder; başka bir LoRA'yla gönderilirse
  satır yukarıdaki gibi ComfyUI'de durur.
- **Colab'a daha önce yüklenmiş eski defter.** Klon hücresi Qwen'in grafiğini arar ve
  *"❌ Grafik yok: …workflow_photo_qwen_api.json"* ile durur; kullanıcı yeni defteri yükler. Eski defter
  bu adımı geçseydi bile `QE_PHOTO_MODELS`'taki `qwen21turbo`'yu `list_models` bilmediği kimlik olarak
  düşürür, öteki modeller listelenir.
- **Galerideki eski Qwen fotoğrafı.** Ayrıntılarda model satırı listede olmadığı için kimliği,
  `qwen21turbo`, yazar — liste okunamadığında bugün de olan.

**Bilinen sınır:** LoRA'yla duran satırın cümlesinin ikinci yarısı, *"defter bu depodan yeni olabilir"*,
burada tersini söylüyor: yeni olan uygulama. Cümle kareyi ve LoRA'yı doğru adlandırıyor; ayrı bir cümle
ayrı bir parça isterdi, ve eski Qwen satırı yalnız bu koşudan önce kuyruğa girmiş olabilir.

## Maliyet

Yeni bir işlem yok. Model listesi, Kuyruğa ekle ve kuyruk bir isteği bugünkü kadar diske ve ağa gider:
model listesi katalogdan okunur (disk yok), bir kare tek bir ComfyUI işi. Defter Qwen işaretlenmediğinde
zaten Qwen indirmiyordu; şimdi kutucuk da yok.

## Bitti sayılır

- `catalog.MODELS` Nova, DaSiWa ve Krea; `list_models` hiçbir girdide Qwen satırı vermez.
- `main.py`'nin `PhotoByModel`'inin kendi grafiği olan tek modeli Krea; `qwen21turbo` satırı fotoğraf
  grafiğine gider ve yukarıdaki gibi durur (testli).
- Fotoğraf grubunun `any`'si checkpoint ya da Krea'nın dosyaları; `QWEN_FILES` yok.
- Defterde `PHOTO_QWEN21TURBO`, `HF_QWEN`, `CIVITAI_QWEN`, `INSTALL_QWEN` ve Qwen'in grafiği yok;
  klon hücresi dört grafiğe bakar ve "dört grafik" der.
- `queen-editor/` altında Qwen modeline giden bir satır kalmaz (Krea'nın ve H3'ün Qwen3-VL ve Qwen
  Image VAE dosyaları dışında).
- Dört test takımı yeşil; `test_notebook_clones_its_branch.py`'nin, defterin `BRANCH`'i koşunun dalını
  gösterdiği için düşen iki testi dışında.
