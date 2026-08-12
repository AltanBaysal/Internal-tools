# Görev 2 — Civitai anahtarı uygulamaya geçsin

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 2

## Sorun

Uygulamanın indiricisi düz bir `urlopen` çağrısı: hiçbir başlık göndermiyor, dolayısıyla kimlik
isteyen hiçbir kaynaktan indiremiyor. Video üreticisinin dört SmoothMix dosyası Civitai'de kimlik
arkasında duruyor; bu yüzden model listesinde `url: None` ile işaretliler ve kurulum ekranı onlara
gelince "bunu defterin kurulum hücresi kurar" deyip duruyor.

Anahtar zaten var: defter `CIVITAI_COOKIE` adlı Colab Secret'ı **şart koşuyor** ve kendi indirme
hücresinde kullanıyor. Yani eksik olan anahtar değil, anahtarın uygulamaya ulaşması.

## Kararlar

1. **Anahtar ortam değişkeniyle geçer:** `QE_CIVITAI_COOKIE`. Defter onu Colab Secret'tan okuyup
   Flask sürecine verir — `QE_XAI_API_KEY` için bugün yapılanın birebir aynısı. Kullanıcıdan
   fazladan bir adım istenmez, anahtar hiçbir dosyaya yazılmaz ve hiçbir yerde basılmaz.
2. **`config.CIVITAI_COOKIE`** o değişkeni okur, varsayılanı boş dize. Boş olması uygulamanın
   açılmasını engellemez: anahtarsız da foto üretilir, yalnız Civitai'den inen kurulum düşer —
   `XAI_API_KEY`'in bugünkü davranışının aynısı.
3. **İndirici genel kalır.** `fetch` bir `headers` argümanı alır ve **verileni gönderir**; hangi
   başlık, neden, kimin için — bunların hiçbirini bilmez. Bir servis ne üretici ne model tanır
   (CODE-STANDARD); indiriciye "civitai ise şu çerezi ekle" yazmak tam da bu kuralı bozardı.
4. **Kaynağın bilgisi model listesinde durur.** `model_groups` hem indirme adresini
   (`https://civitai.red/api/download/models/<version_id>`) hem çerezin adını
   (`__Secure-civ-token`) bilir; `civitai_headers(cookie)` yardımcısı ikisini bir arada tutar.
   `main.py` yalnız **değeri** verir. Adres ve çerez adı yan yana durursa, kaynak değiştiğinde tek
   dosya değişir.
5. **Satır kimlik gerektirdiğini kendi söyler:** `"auth": CIVITAI`. Dört SmoothMix satırı gerçek
   adreslerini alır ve `url: None` video grubundan tamamen kalkar.
6. **Anahtarsız kurulum sessizce başlamaz.** Kimlik isteyen bir satıra gelindiğinde anahtar yoksa
   kurulum durur ve nedenini söyler: hangi dosya, hangi kaynak. Bugünkü "bunu defter kurar"
   cümlesi bu satırlar için artık yanlış — yerini bu alır. Cümlenin kendisi silinmez: foto grubu
   hâlâ boş, ve boş grup o cümleyi kullanıyor. İkisi de Görev 3 ve 4'ten sonra ölür; oradan
   kalkarlar.
7. **Model olmayan bir cevap model adıyla diske yazılmaz.** Süresi dolmuş bir çerezle gelen cevap
   dosya değil sayfa olabilir; onu `.safetensors` adıyla yazmak, modeli sonsuza kadar "kurulu"
   gösterir — kullanıcının işini kaybettirmeyen ama kaybettiğini de söylemeyen tam o durum
   (FOUNDATION madde 1). İndirici cevabın türü HTML ise dosyayı yazmaz, hata verir.
   Bu, "sebebi uydurma" kuralına da uyar: hata metni sunucunun ne söylediğini taşır, neden öyle
   söylediğine dair bir tahmin taşımaz.
8. **Defterin indirme hücresi bu görevde kalır.** Kaldırmak Görev 4'ün işi; burada değişen tek
   şey, defterin anahtarı uygulamaya da geçirmesi. Bir görev boyunca ikisinin de indirebiliyor
   olması zararsız — indirilmiş dosya yeniden indirilmiyor.

## Testler

- İndirici, verilen başlıkları isteğe koyar; başlık verilmediğinde hiçbir şey eklemez (bugünkü
  davranış aynen sürer).
- İndirici, HTML cevabını reddeder ve geriye ne dosya ne yarım dosya bırakır.
- Kurulum, `auth` taşıyan satır için o kaynağın başlıklarını indiriciye geçirir.
- Kurulum, anahtar verilmemişken kimlik isteyen satıra gelince durur ve dosyanın adıyla secret'ın
  adını söyler.
- Model listesinde video grubunda `url: None` satır kalmaz; dört SmoothMix satırının dördü de
  `auth` taşır ve adresleri sürüm numaralarını içerir.
- `civitai_headers` çerezi kendi adıyla tek bir `Cookie` başlığına koyar.

## Öz eleştiri

- *Çerez yerine API anahtarı daha temiz olmaz mıydı?* — Olurdu, ama bugün elimizde olan bu:
  defter aylardır bu çerezle indiriyor ve çalıştığı biliniyor. Anahtar tipini değiştirmek, bu
  görevin işi olmayan bir doğrulama turu gerektirir. Değişirse değişecek tek yer `model_groups`.
- *Anahtarı ortam değişkeniyle geçirmek güvenli mi?* — Colab'da GitHub token'ı ve xAI anahtarı
  zaten böyle geçiyor; süreç aynı makinede, aynı kullanıcının. Alternatif — anahtarı Drive'a
  yazmak — sırrı kalıcı hale getirirdi ve daha kötü.
- *HTML kontrolü kırılgan değil mi?* — Sunucu bir gün `text/html` yerine başka bir şey dönerse
  kaçırır, evet. Ama yanlış tarafa kırılıyor: kaçırdığında bugünkü davranışa düşer, yanlış
  reddettiğinde ise gerçek bir model asla HTML olarak sunulmaz. Karşılığı, sessizce "kurulu"
  görünen bir giriş sayfası.
- *Neden `auth` bir sözcük, doğrudan başlık sözlüğü değil?* — Çünkü sır alan taşımamalı. Satır
  "bu kaynak kimlik ister" der; sırrı bileşim kökü verir. Satıra başlık yazmak, sırrı domain'e
  taşırdı.
