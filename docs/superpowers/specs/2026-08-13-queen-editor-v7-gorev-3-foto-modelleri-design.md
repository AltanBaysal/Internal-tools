# Görev 3 — Foto modelleri kurulum listesine girsin

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 2

## Sorun

Foto üreticisinin kurulum listesi boş. Uygulama "foto kurulu mu" sorusunu ComfyUI'ye soruyor —
"ortada bir checkpoint var mı" — ve kuramıyor: kurulum ekranındaki Kur, foto satırında
"bunu defterin kurulum hücresi kurar" diyor. Foto grafiğinin ihtiyacı olan beş dosyanın beşini de
defter indiriyor.

## Kararlar

1. **Beş dosyanın beşi de listeye girer**, ikisi değil. Foto grafiği checkpoint ve lora dışında üç
   dosya daha okuyor: varsayılan açık FaceDetailer dalı yüz dedektörünü ve SAM'i açılışta yüklüyor,
   bypass edilmiş Ultimate SD Upscale dalı da Remacri'yi kullanıcı açtığı anda. İkisini alıp üçünü
   defterde bırakmak, "foto kurulu" cevabını yalan yapardı.

   | Klasör | Dosya | Kaynak |
   |---|---|---|
   | `checkpoints` | `nova3DCGXL_ilV90.safetensors` | Civitai (kimlik ister) |
   | `loras` | `USNR_STYLE_ILL_V1_lokr3-000024.safetensors` | Civitai (kimlik ister) |
   | `upscale_models` | `4x_foolhardy_Remacri.pth` | Hugging Face |
   | `ultralytics/bbox` | `face_yolov9c.pt` | Hugging Face |
   | `sams` | `sam_vit_b_01ec64.pth` | fbaipublicfiles |

2. **"Kurulu mu" artık dosyalara sorulur.** Grubu olan üretici dosyalarıyla yargılanıyordu zaten;
   foto grubu dolunca foto da o yola girer.
3. **Kendi kendine cevap veren üretici kavramı ölür.** Üç üreticinin üçünün de grubu olduğuna göre
   `list_producers`'ın "grubu yoksa üreticinin kendisine sor" dalı hiçbir zaman koşmaz. Kalırsa
   ilk okuyana iki yol varmış gibi görünür ve testi onu canlı gösterir. Dal, `producers`
   argümanı ve `ComfyPhotoGenerator.installed()` birlikte silinir.
4. **Model listesi kısıtlanmıyor.** Hangi checkpoint'lerin seçilebildiği hâlâ ComfyUI'ye
   soruluyor (`models()`); kullanıcının kendi eklediği checkpoint listede görünmeye devam eder.
   Değişen tek soru "foto üreticisi kurulu mu" — cevabı artık "uygulamanın kurduğu takım burada
   mı".
5. **Defterin indirme hücresi bu görevde de durur.** Kaldırmak Görev 4'ün işi; iki tarafın da
   indirebiliyor olması bir görev boyunca zararsız, inmiş dosya yeniden inmiyor. Kurulum
   ekranındaki "bunu defter kurar" cümleleri de bu yüzden bu görevde doğru kalır ve
   dokunulmaz — onlar Görev 4 ile ölür.

## Testler

- Foto grubu beş satır taşır; her satırın klasörü, adı ve adresi vardır.
- Civitai'den inen iki satır `auth` taşır, diğer üçü taşımaz.
- Grubu olan bir üretici, dosyalarının hepsi yerindeyken kurulu sayılır — foto dahil.
- `list_producers` artık üretici haritası almaz; üç satırı da yalnız dosyalardan çıkarır.
- `ComfyPhotoGenerator`'ın `installed()`'ı yok; `models()` duruyor ve hâlâ sunucuya soruyor.

## Öz eleştiri

- *Kendi checkpoint'ini kuran kullanıcı ne olacak?* — Foto üreticisi "kurulu değil" görünür ve
  panelde Kur kartı çıkar. Rahatsız edici ama doğru: grafiğin varsayılanı bu checkpoint, ve
  dedektör ile SAM olmadan render zaten düşer. Kendi checkpoint'i listede durmaya devam eder.
- *Beş dosya çok değil mi, `installed()` daha esnekti?* — Esnek değildi, belirsizdi: "bir
  checkpoint var" cevabı, dört dosyası eksik bir makinede de evet diyordu. Kurulum ekranının
  amacı tam olarak bu soruyu kesin cevaplamak.
- *Fallback'i silmek geri dönüşü zorlaştırmaz mı?* — git'te duruyor. Kullanılmayan bir dal,
  bakımda tutulmadığı için ilk değişiklikte sessizce çürür; testi de onu canlı gösterdiği için
  çürüdüğü fark edilmez.
