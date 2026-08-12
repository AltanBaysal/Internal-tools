# Görev 6 — Defter ve belgeler

**Roadmap:** [v6](../plans/2026-08-13-queen-editor-v6-roadmap.md) · Blok 2

## Sorun

Kod bitti, ama defter hâlâ v5 öncesinin dünyasını kuruyor: eski dalı klonluyor, yalnız foto
grafiğinin node'larını kuruyor, ffmpeg'i hiç kurmuyor ve MMAudio'dan haberi yok. FOUNDATION da
"ComfyUI üretim motorudur" diyor — ses artık orada üretilmiyor.

## Kararlar

1. **`BRANCH` `feat/queen-editor-v3` olur.** Defter dalı klonluyor; v2'yi klonlamak v5 ve v6'nın
   hiçbirini içermeyen bir uygulama çalıştırmak demek.
2. **Video grafiğinin custom node'ları kurulur.** Defter foto grafiğinin 8 paketini kuruyor; Görev
   1'de gelen video grafiği 11 paket daha istiyor (`comfy_mtb`, `VideoHelperSuite`,
   `WanVideoWrapper`, `GGUF`, `ComfyMath`, `Frame-Interpolation`, `VFI`, `Comfyroll`, `mxToolkit`,
   `NAG`, `adaptiveprompts`). Yoksa ilk video isteği ComfyUI'den `node_errors` ile döner.
   - **Öksüz node'ların paketi de kurulur.** `UnetLoaderGGUF` grafikte erişilemez duruyor ama
     ComfyUI gönderilen prompt'un **her** node'unu doğruluyor; paket olmadan istek reddedilir.
   - **`ComfyUI-MMAudio` kurulmaz.** Grafikte MMAudio node'u yok — ses bu süreçte üretiliyor.
     Kurmak, kullanılmayacak bir eklentiyi indirmek olurdu.
   - **Bu, roadmap'in Görev 6 tarifinin biraz dışında.** Boşluk v5'ten kalma ve ancak grafik
     repoya girince görünür oldu; defteri yarım bırakmak, Colab turunun ilk videoda durması
     demekti.
3. **`ffmpeg` apt ile kurulur.** Export videoları birleştiriyor, ses üretimi videoyu kesiyor;
   ikisi de ffmpeg çağırıyor ve defter bugün yalnız `aria2` kuruyor.
4. **MMAudio kütüphanesi kendi hücresinde kurulur** (klon + `pip install -e .`), custom node
   hücresinden sonra. Ayrı hücre, çünkü ComfyUI'nin eklentisi değil: uygulamanın kendi süreç içi
   motoru, ve bir gün ComfyUI kurulumu değişse bu onunla birlikte bozulmamalı.
   - **Ağırlıklar burada indirilmez.** NSFW fine-tune'u üretici paneli indiriyor (Görev 4),
     MMAudio'nun temel ağırlıklarını da kütüphane ilk kullanımda kendi çekiyor. Defterde üçüncü
     bir indirme, panelin sözünü ikiye bölerdi.
5. **Klon hücresi video grafiğini de arar.** Bugün yalnız `workflow_api.json`'u kontrol ediyor;
   unutulmuş bir commit ilk videoda değil, klonda görünmeli.
6. **FOUNDATION madde 6 daralır.** ComfyUI foto ve videonun motoru; ses uygulamanın kendi
   sürecinde koşuyor. Maddeye "neden iki motor" cevabı da yazılır — ilk soran o dosyaya bakacak.
7. **CODE-STANDARD'ın miras tablosuna MMAudio satırı girer.** Ayarları `mmaudio_generate.ipynb`'den
   *bilgi olarak* aldık; o defteri çalıştırmıyor, dosyasını okumuyoruz — tablo tam olarak bu ayrımı
   anlatıyor.

## Ne değişiyor

| Yer | Bugün | Yarın |
|---|---|---|
| `BRANCH` | `feat/queen-editor-v2` | `feat/queen-editor-v3` |
| apt paketleri | `aria2` | `aria2`, `ffmpeg` |
| Custom node'lar | 8 (foto grafiği) | 19 (foto + video grafiği) |
| MMAudio | yok | kendi hücresinde kurulu |
| Klon kontrolü | foto grafiği | foto + video grafiği |
| FOUNDATION madde 6 | tek motor | iki motor, gerekçesiyle |
| CODE-STANDARD miras tablosu | ComfyUI grafiği ve defter hücreleri | + MMAudio ayarları |

## Testler

Otomatik testi yok: defter Colab'da çalışıyor, belgeler metin. Doğrulama kullanıcının turunda —
Run all sonrası video ve ses üretmek. Kodun kendi takımı (`pytest`) değişmediği için yeşil kalmalı;
kalmıyorsa bu görevde kod değişmiş demektir ve bu görevde kod değişmemeli.

## Öz eleştiri

- *11 paket eklemek kurulumu ne kadar uzatır?* — Klonlar küçük, ama `requirements.txt`'leri var;
  ilk kurulum birkaç dakika uzar. Alternatif, video isteyene "önce şu paketleri kur" demekti.
- *Node listesini `photo_to_video.ipynb`'den kopyalamak bağımlılık mı?* — Değil, miras: liste bizim
  dosyamıza yazılıyor, o defter çalıştırılmıyor. CODE-STANDARD'ın izin verdiği tam olarak bu, ve
  bedeli iki listenin ayrı bakılması.
- *Roadmap'in dışına çıkmak doğru mu?* — Bu görev "defter uygulamanın yaptığını çalıştırabilsin"
  diyor; video node'ları olmadan çalıştıramıyor. Kapsamı sessizce büyütmemek için karar 2'de
  ayrıca yazıldı.
