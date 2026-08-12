# Görev 1 — Video grafiği repoya girer

**Roadmap:** [v6](../plans/2026-08-13-queen-editor-v6-roadmap.md) · Blok 1

## Sorun

`queen-editor/workflow_video_api.json` yok. Uygulama video üretmeye kalkınca üretici kendi
cümlesiyle duruyor: *"Video grafiği yok … ComfyUI'de Export (API) ile kaydet"*. Oysa dışa
aktarılacak bir şey yok — graf zaten repoda, yalnız başka bir klasörde.

## Kararlar

1. **Kaynak: `collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json`.** Üç aday arasından
   bu, çünkü `comfy_video_generator.py`'nin yamaladığı üç node'un üçü de yalnız onda var:

   | Node | class_type | Yamalanan giriş |
   |---|---|---|
   | `287` | `LoadImage` | `image` |
   | `233:240` | `PromptGenerator` | `prompt`, `seed` |
   | `210` | `Seed (rgthree)` | `seed` |

   Zaten `photo_to_video.ipynb`'in Drive'dan okuduğu dosya da bunun bir kopyası; node id'leri
   üreticiye oradan miras kaldı.
2. **Kopya, referans değil.** Dosya `queen-editor/`'e kopyalanır; çalışma anında `collab-toolbox`
   okunmaz. CODE-STANDARD'ın bağımsızlık kuralı bunu foto grafiği için zaten söylüyor, video da
   aynı kuralın altında.
3. **Export olduğu gibi taşınır, elle düzenlenmez.** İçinde öksüz node'lar var: `356` ve `357`
   (`UnetLoaderGGUF`, `unet_name: null`). Hiçbir node onlara referans vermiyor, dolayısıyla
   ComfyUI onları hiç çalıştırmaz — `null` zararsız. Kendi yazmadığımız bir grafiği "temizlemek",
   çalışan bir hattı görünmez biçimde bozmanın en kısa yolu.
4. **Grafiğin biçimi testle tutulur.** Foto grafiği için `test_workflow_asset.py` bunu zaten
   yapıyor; video onun ikizi olarak yanına yazılır. Test yalnız *varlığı* değil, **yamalanan
   girişleri** de doğrular: node duruyor ama girişinin adı değişmişse yama sessizce boşa gider ve
   hata ancak Colab'da bir render olarak görünür.
5. **Foto testinin boşluğu da kapanır.** Üretici dört node yamalıyor (`3`, `4`, `40`, `45`), test
   üçünü doğruluyor: `45` (`ckpt_name` — model seçimi) yazılmamış. Aynı dosyada, aynı görevde
   kapanır; ayrı bir görev açmak, bir satırlık boşluk için tören olurdu.
6. **Model listesi bu görevin dışında.** Grafın adını verdiği checkpoint'lerle
   `model_groups.py`'nin örtüşmesi Görev 2'nin işi.

## Ne değişiyor

| Yer | Bugün | Yarın |
|---|---|---|
| `queen-editor/workflow_video_api.json` | yok | var (arbuzai export'unun kopyası) |
| Video üretimi | "graf yok" hatasıyla durur | grafiği açar, üç node'u yamalar |
| `test_workflow_asset.py` | yalnız foto, üç node | foto (dört node) + video (üç node) |

## Testler

`queen-editor/backend/tests/test_workflow_asset.py`:

- **Video:** shipped dosya API formatında (`nodes` anahtarı yok); `287` bir `LoadImage` ve
  `image` girişi var; `233:240` bir `PromptGenerator` ve `prompt` + `seed` girişleri var; `210`
  bir `Seed (rgthree)` ve `seed` girişi var.
- **Foto:** mevcut testin sonuna `45` — `ckpt_name` girişi.

Ayrı bir üretici testi yazılmaz: `ComfyVideoGenerator`'ın yükleme ve yamalama davranışı
`test_comfy_video_generator.py`'de sahte grafiklerle zaten kapsanıyor. Buradaki soru üreticinin
davranışı değil, **gönderdiğimiz varlığın şekli**.

## Öz eleştiri

- *Kopyalamak yerine iki yerde tek dosya tutulamaz mı?* — Tutulmamalı. `collab-toolbox` ayrı bir
  araç ve kendi hızında değişiyor; oradaki bir düzenleme queen-editor'ün üretimini habersiz
  değiştirirse bunu kimse fark etmez. Kopyanın bedeli iki dosyanın ayrı bakılması, ve bu bedel
  CODE-STANDARD'da zaten kabul edilmiş.
- *Öksüz node'ları bırakmak testi yalancı yapar mı?* — Hayır: test yalnız yamaladığımız üç node'u
  iddia ediyor, grafiğin tamamının doğruluğunu değil. Grafiğin gerçekten çalıştığını söyleyecek
  tek şey Colab'daki render, ve o kullanıcının turunda.
- *`45` neden bu görevde?* — Aynı dosyada, aynı cümlenin eksik kalmış yarısı. Ayrı görev açmak
  roadmap'i şişirir, boşluğu bırakmak ise bir sonraki graf değişikliğinde model seçimini sessizce
  öldürür.
