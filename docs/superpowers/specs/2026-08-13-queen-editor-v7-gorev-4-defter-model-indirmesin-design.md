# Görev 4 — Defter model indirmeyi bıraksın

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 2

## Sorun

Görev 2 ve 3'ten sonra uygulama on modelin hepsini kendi indirebiliyor, ama defter hâlâ indiriyor:
foto grafiğinin beş dosyası defterin model hücresinde, gated probe ve doğrulama makinesiyle
birlikte. Kullanıcının kuralı net — **defter hiçbir model indirmemeli**, uygulama kurulmamış
modellerle açılmalı ve kurulum ekrandan yapılmalı.

## Kararlar

1. **Defter kod kurar, model kurmaz.** Model indirme hücresi tamamen kalkar. Defterde kalan
   kurulum işi: ComfyUI, 19 custom node, ffmpeg/aria2 ve MMAudio kütüphanesi — hepsi kod.
2. **Yalnız indirmeye hizmet eden yardımcılar da gider:** dosya doğrulama, insan okur boyut ve
   yanıt gövdesi basma. `log` ve `run` kalır, custom node ve MMAudio hücreleri onları kullanıyor.
3. **Hedef klasörleri defter açmaz.** İndirici zaten yazacağı klasörü kendisi oluşturuyor; boş
   klasör açmak, kurulmamış bir modeli kurulmuş gibi gösteren bir iz bırakmaktan başka bir şey
   yapmıyor.
4. **`CIVITAI_COOKIE` şartı kalır.** Çerez artık defterin değil uygulamanın işine yarıyor, ama
   yokluğunu CONFIG hücresinde duymak, kurulum ekranında Kur'a bastıktan sonra duymaktan iyidir.
5. **"Bunu defter kurar" cümlesi ölür.** Artık kuran bir defter hücresi yok; cümlenin kendisi de
   kalkar. Yerine kalan tek koruma, dosya listesi tanımlı olmayan bir tür için: karşılığı yok
   diye sessizce "kuruldu" demek yerine durup söyler.
6. **`url: None` kavramı da ölür.** Hiçbir satırda yok ve tek varlık sebebi "bunu defter indirir"
   idi. Gelecekte adresi olmayan bir dosya çıkarsa o zaman geri gelir — bugün tutmak,
   kullanılmayan bir yolu bakımda tutmak olur.
7. **İki yaşayan belge değişir.**
   - **FOUNDATION** yeni bir karar kazanır: *modelleri uygulama kurar, defter yalnız kod kurar.*
     Bu, ürün şeklinden bağımsız bir mimari karar — sebebiyle birlikte oraya yazılır.
   - **CODE-STANDARD**'ın bağımsızlık tablosundaki "kurulum hücreleri — custom node'lar, 5 model,
     indirme/doğrulama/401 işleyişi" satırı daralır: miras alınan şey artık yalnız custom node ve
     headless ComfyUI kurulumu. Model kurulumu kimseden miras alınmıyor, uygulamanın kendi işi.
8. **README'nin yanlış cümleleri düzeltilir.** Belge genel olarak eski (hâlâ "Part 4" anlatıyor),
   ama bu görevin yanlışladığı iki cümle — "~7.5 GiB model indirir" ve "çerez iki gated indirmeyi
   yetkilendirir, model hücresi durunca yenile" — burada düzeltilir. Belgenin geri kalanının
   tazelenmesi bu görevin işi değil; yanlışını bırakmak ise olurdu.

## Testler

- `queen-editor/` ağacında (`dist/`, `.git`, `node_modules` ve testin kendisi dışında) `CIVITAI_MODELS`,
  `OPEN_MODELS` ve `civitai_probe` geçen tek satır kalmaz.
- Kurulumun hiçbir hata metninde "defter" geçmez.
- Dosya listesi olmayan bir tür kurulmaya çalışılınca koşu durur ve türün adını söyler.
- Mevcut takım yeşil kalır.

## Öz eleştiri

- *Defterin doğrulama makinesi (safetensors başlığından beklenen boyutu çıkarma) değerliydi;
  atmak kayıp değil mi?* — Kayıp, ama yanlış yerde duran bir değerdi. Uygulamanın indiricisi
  yarım dosyayı `.part` adıyla tutuyor ve ancak tamamlanınca gerçek ada geçiriyor; sunucunun
  sayfa döndürdüğü durumu da reddediyor. Eksik olan, boyut doğrulaması. Bunu istersek indiriciye
  ekleriz — defterde tutmak, iki yerde iki ayrı kurulum yolu tutmak demekti.
- *Kullanıcı artık her temiz makinede on dosyayı elle mi kuracak?* — Elle değil, üç tıkla:
  kurulum ekranındaki her üretici satırının kendi Kur'u var. Karşılığında kazandığı şey, neyin
  kurulu olduğunu gerçekten gösteren bir ekran ve kurulumun yarıda kalmasının artık görülebilir
  olması.
- *`CIVITAI_COOKIE` şartını korumak, foto üretmeyecek kullanıcıyı da durdurmaz mı?* — Durdurur,
  ve bu bugünkü davranışın aynısı. Değiştirmek ayrı bir karar; bu görevde bir şeyi
  değiştirmemenin gerekçesi, değiştirmenin gerekçesinden güçlü.
