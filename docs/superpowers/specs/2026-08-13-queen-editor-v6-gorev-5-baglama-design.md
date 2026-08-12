# Görev 5 — Bağlama ve eski kodun kaldırılması

**Roadmap:** [v6](../plans/2026-08-13-queen-editor-v6-roadmap.md) · Blok 2

## Sorun

Yeni ses üreticisi yazıldı ama hiçbir yere bağlı değil: kuyruk hâlâ `ComfyAudioGenerator`'a
gidiyor, yani var olmayan bir grafiği arıyor. Eski adaptör, onun testi ve `AUDIO_WORKFLOW_PATH`
ayarı da yerinde duruyor.

## Kararlar

1. **Ses üreticisi `main.py`'de kurulur:** `MMAudioGenerator(MMAudioSampler(ağırlık yolu),
   FfmpegAudio())`. Ağırlık yolu Görev 4'ün `audio_weights` yardımcısıyla gruptan türetilir.
2. **Port değişmez.** Kuyruk, katman ve yeniden üretme tarafında hiçbir şey değişmiyor: üretici
   sözleşmesi (`generate(prompt, negative, seed, model, source)` → `(ad, bayt)`) aynı sözleşme.
   Bu görevde tek satır kullanım durumu değişmemeli — değişiyorsa ya port bozulmuştur ya da
   kapsam kaymıştır.
3. **`ComfyAudioGenerator` ve testi silinir.** İki motor arasında seçim yapılabilsin diye
   bırakmak, kurulmamış bir grafiğe geri dönüş yolu tutmak olurdu; kimse o yolu bakımda tutmaz ve
   ilk graf değişikliğinde sessizce çürür.
4. **`AUDIO_WORKFLOW_PATH` silinir.** Karşılığı olmayan bir ayar.
5. **`AUDIO_TIMEOUT` de silinir.** Bir ComfyUI işini beklerken kullanılıyordu; süreç içinde
   çalışan bir çağrının zaman aşımı yok — bırakmak, uygulanmayan bir sınır sözü vermek olurdu.
6. **`ComfyModelFiles` yukarı taşınır.** Üretici haritası ondan önce kuruluyor ama artık ağırlık
   yoluna ihtiyacı var; bileşim kökünde sıra, bağımlılığın kendisidir.
7. **Yalnız ad değil, iz de silinir.** `workflow_audio_api.json` **`queen-editor/` ağacında**
   hiçbir yerde geçmemeli — testi de bunu iddia eder, yoksa README ya da defter silinmiş bir
   dosyayı istemeye devam eder. Tarama aracın kendi ağacıyla sınırlı: `docs/` altındaki spec'ler
   ve roadmap'ler değişikliğin *tarihini* anlatıyor, o iki adı anmaları gerekiyor.

## Testler

- `queen-editor/` altında (`dist/`, `.git`, `node_modules` dışında) `workflow_audio_api` ve
  `ComfyAudioGenerator` geçen hiçbir satır kalmadı.
- `config`'de `AUDIO_WORKFLOW_PATH` ve `AUDIO_TIMEOUT` yok.
- Mevcut takım yeşil kalır: port değişmediği için kuyruk ve katman testlerinin hiçbiri
  değişmemeli.

## Öz eleştiri

- *Silmek yerine bırakıp kullanmamak daha güvenli değil mi?* — Değil. Kullanılmayan bir adaptör,
  ilk okuyana "iki seçenek var" diye yalan söyler ve testi de onu canlı gösterir. Geri dönmek
  gerekirse git'te duruyor.
- *"Repoda hiç geçmiyor" testi kırılgan değil mi?* — Kendi dosyasını sayarsa kırılır, o yüzden
  arama testin kendisini de dışarıda bırakır. Karşılığı, silinmiş bir dosyayı isteyen bir
  belgenin fark edilmeden kalması.
