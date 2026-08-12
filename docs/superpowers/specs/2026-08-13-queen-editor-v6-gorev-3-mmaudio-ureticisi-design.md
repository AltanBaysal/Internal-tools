# Görev 3 — MMAudio üreticisi

**Roadmap:** [v6](../plans/2026-08-13-queen-editor-v6-roadmap.md) · Blok 2

## Sorun

Ses üreticisi olmayan bir ComfyUI grafiğine yazıldı. Kullanıcı kararı (2026-08-13): o graf
kurulmayacak, `mmaudio_generate.ipynb` ne yapıyorsa birebir aynısı yapılacak — MMAudio süreç
içinde koşacak.

## Kararlar

### Ne taşınır, ne taşınmaz

1. **Taşınan: ses üretiminin kendisi.** Videoyu 720p/25fps'e indirme, süreye göre parçalama,
   `generate` çağrısı ve onun bütün ayarları, parçaların crossfade ile birleştirilmesi.
2. **Taşınmayan: defterin iş yönetimi.** Drive tarama, batch, "zaten var" atlaması, dosya adından
   seed türetme, sesi videoya mux etme. Bunların hepsi queen-editor'de zaten var ve başka türlü
   çalışıyor: kuyruk işleri sıraya koyuyor, her işin kendi seed'i var, ses ayrı bir `.wav` olarak
   duruyor ve videoyla birleşmesi export'un işi.
3. **Çıktı `.wav`.** Katman dosyası bugün de `.wav` (`P11_3_V1_0_S1_0.wav`); defterin FLAC'ı
   ara adımdı, mux'a gidiyordu.

### Ayarlar — defterle birebir

| Ayar | Değer | Neden bu değer |
|---|---|---|
| Mimari | `large_44k` | NSFW fine-tune bu mimariyi kullanıyor |
| Ağırlık | `mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors` | defterin kullandığı |
| Adım | 40 | defterin override'ı (varsayılan 25) — daha temiz ses |
| CFG | 5.5 | defterin override'ı (varsayılan 4.5) — negatifi daha iyi tutar |
| Çözücü | `euler` | sabit adım |
| dtype | `float16` | T4 bfloat16 desteklemiyor |
| Negatif | `music, speech, voices, singing, talking, vocals` | müzik ve konuşma engellenir |
| Video girdisi | 25 fps, 720p, sessiz | Synchformer 25 fps bekliyor |
| Parça sınırı | 10 sn üstü parçalanır, hedef 8 sn | model 8 saniyede eğitilmiş |
| Crossfade | 100 ms | parça sınırındaki tıklamayı yumuşatır |

### Açık soruların cevapları

4. **Model ilk ses işinde yüklenir ve bellekte kalır.** Yükleme dakikalar sürüyor; iş başına
   yüklemek her sesi o bedelle vergilendirirdi. Kuyruk zaten tür sırasıyla akıyor (foto → video →
   ses), yani ses işleri arka arkaya geliyor ve tek yükleme hepsine yetiyor. Foto-yalnız çalışan
   bir kullanıcı hiç ödemez.
   - **GPU paylaşımı:** MMAudio fp16 kabaca 5 GB; ComfyUI aynı kartta WAN'ı tutuyor. Video zaten
     A100 istiyor (40 GB), ikisi birden sığar. ComfyUI'ye "modellerini bırak" dedirtecek bir
     dans **eklenmiyor**: gerçek bir ComfyUI'ye karşı denenemeyecek bir kurtarma, çözdüğünden çok
     yeni hata yolu açar. Sığmazsa bunu Colab turu gösterir.
5. **Parçalama taşınır, bu sürümde çalışmasa bile.** Video süresi grafikten geliyor, bizim
   kodumuzdan değil; yarın 12 saniyelik bir export gelirse ses sessizce bozulur ve kimse
   parçalamanın kaldırıldığını hatırlamaz. Otuz satırlık bir kural, sessiz bir kalite kaybından
   ucuz.
6. **Negatif prompt: defterin sabiti varsayılan, işin kendi alanı kazanır.** İş bugün boş negatif
   taşıyor, yani pratikte sabit kullanılıyor; ama boş olmayan bir negatif geldiğinde onu yok
   saymak, kullanıcının yazdığını çöpe atmak olurdu.

### Yapı

7. **Dört parça, çünkü üçü test edilebilir biri edilemez.** Torch'suz makinede koşacak testler
   isteniyorsa, torch'a dokunan yüzey mümkün olduğunca ince olmalı:

   | Dosya | Ne yapar | Test |
   |---|---|---|
   | `domain/audio_chunks.py` | süreyi parçalara böler — saf kural | tam |
   | `data/ffmpeg_audio.py` | süre okuma, 720p'ye indirme, parça kesme, crossfade birleştirme | tam (komut çalıştırıcı enjekte) |
   | `data/mmaudio_generator.py` | üretici portu: geçici dosya, parçalar, örnekleyici çağrıları, birleştirme | tam (örnekleyici sahte) |
   | `data/mmaudio_sampler.py` | torch + mmaudio; ağırlıkları yükler, `generate` çağırır | yok — dış dünya |

8. **`torch` ve `mmaudio` import'u fonksiyonun içinde.** Modül yüklenirken import edilirse
   torch'suz makinede tüm takım çöker. Örnekleyici ilk çağrıda import eder, aynı çağrıda modeli
   yükler ve saklar.
9. **Port bayt veriyor, MMAudio dosya istiyor.** Adaptör videoyu geçici bir dosyaya yazar, işi
   bitince siler — başarısız olsa da siler.
10. **Ses `generate`'in verdiği bayt olarak döner**, diske yazan taraf üretici değil kuyruk —
    bugünkü portun sözü bu ve değişmiyor.

## Testler

- `audio_chunks` — 8 sn tek parça; 10 sn tek parça (sınır dahil); 24 sn üç parça, hepsi 8'er sn;
  20 sn iki eşit parça; süre parçalara tam bölünmediğinde toplam korunur.
- `ffmpeg_audio` — her komut beklenen argümanlarla çalışır; tek parçada birleştirme yerine kopya;
  ffmpeg patlarsa kendi son satırıyla `RuntimeError`.
- `mmaudio_generator` — kaynak yoksa Türkçe hata; örnekleyiciye doğru prompt, negatif ve seed
  gider; boş negatif sabiti kullanır, dolu negatif kazanır; kısa video tek çağrı, uzun video
  parça sayısı kadar çağrı; çıktı `.wav`; geçici dosyalar hata hâlinde de silinir.

## Öz eleştiri

- *Dört dosya bir görev için fazla değil mi?* — Alternatifi tek dosyada torch'a bağlı bir sınıf,
  ve o zaman parçalama kuralının da ffmpeg argümanlarının da testi olmaz. Bölme testin nerede
  duracağına göre yapıldı, süsleme için değil.
- *Örnekleyici test edilmiyorsa oradaki hata nasıl yakalanır?* — Yakalanmaz; Colab turunda
  görünür. Diğer dış dünya adaptörleri de (ComfyUI istemcisi, ffmpeg export'u) aynı sınırda
  duruyor, ve bu bilinçli: sahte bir torch yazmak, torch'u test etmek değil kendi sahtemizi test
  etmek olurdu.
- *"Birebir aynısı" sözü tutuluyor mu?* — Üretim ayarlarında evet, tablodaki her satır defterden.
  Tutulmayan yer iş yönetimi, ve orası zaten queen-editor'ün kendi işi — defterin batch döngüsünü
  taşımak iki kuyruk demek olurdu.
