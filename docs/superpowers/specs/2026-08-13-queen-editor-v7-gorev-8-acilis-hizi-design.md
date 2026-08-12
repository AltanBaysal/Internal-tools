# Görev 8 — Açılışta galeri hızlı dolsun

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 3

## Ölçüm

Görev 6 ve 7'den sonra açılışta iki maliyet kaldı ve ikisi aynı şey değil:

**1. Listenin kendisi.** Bir galeri isteği beş Drive dosya okuması; **üçü aynı dosya**. Kayıt
(`photos.jsonl`) üç soruya cevap veriyor — hangi katman nerede, hangi fotoğraflar duruyor, her
katman hangi sözlerden yapıldı — ve her soru dosyayı kendisi açıp satır satır yeniden ayrıştırıyor.
Üretim koşarken bu 2 saniyede bir tekrarlanıyor.

**2. Fotoğrafların kendisi.** Galeri karoları tam boy PNG çekiyor. Bir SDXL karesi ~1.5–2.5 MB;
ekranda aynı anda 8 karo varsa ilk açılış tünelden ~15 MB indiriyor. Karolar zaten görünür oldukça
yükleniyor (`loading="lazy"`) ve fotoğraflar kalıcı önbellek başlığıyla sunuluyor, yani **ikinci**
açılış bedava. Pahalı olan ilk açılış, ve pahalı olan şey baytların büyüklüğü.

## Kararlar

1. **Kayıt bir kez okunur.** Üç soru aynı ayrıştırılmış satırlardan cevaplanır.
2. **Okunan şey, dosya değişene kadar elde tutulur.** Anahtar dosyanın kendi damgası — değişme
   zamanı ve boyutu. Kendi eklememiz boyutu değiştiriyor, dışarıdan yapılan bir düzenleme de
   ikisinden birini; yani *"doğru diskte yaşar"* ([FOUNDATION madde 2](../../../queen-editor/FOUNDATION.md))
   bozulmuyor — aynı soruyu saniyede beş kez sormayı bırakıyoruz.
   Damgayı almak bir `stat` çağrısı: dosyayı açıp ayrıştırmanın yanında bedava.
3. **Önbellek veri katmanında durur, domain görmez.** Kayıt portu değişmiyor; kuyruk, galeri ve
   detay aynı üç soruyu sormaya devam ediyor.
4. **Plan ve sıra dosyalarına dokunulmuyor.** Her biri istek başına **bir** kez okunuyor; ölçülen
   fazlalık kayıttaydı. Ölçmeden aynı makineyi üç yere kurmak, kazancı olmayan üç yerde bakım
   demekti.
5. **Fotoğraf baytları bu görevde küçülmüyor — ve bu, kapatılmamış bir eksik olarak bırakılıyor.**
   Doğru cevabı belli: galeri karoları için küçük birer önizleme üretmek ve karoya onu servis
   etmek. Ama bu, bu maddenin taşıyabileceğinden büyük bir iş — önizlemenin ne zaman üretileceği,
   nereye yazılacağı, adının ne olacağı, kare değiştiğinde ne olacağı ve yeni bir bağımlılık
   (görüntü kütüphanesi) kendi tasarımını ister. Kullanıcıya karar olarak bırakılıyor; sessizce
   yarısını yapmak, "açılış hızlandı" demek ama hâlâ 15 MB indirmek olurdu.

## Testler

- Depo, bir dosyanın damgasını verir; olmayan dosya için damga yoktur.
- Kayıt, üç sorunun üçünü tek okumayla cevaplar.
- Dosya değişince kayıt yeniden okur; değişmediyse okumaz.
- Mevcut takım yeşil kalır: portun cevapları aynı.

## Öz eleştiri

- *Önbellek, iki farklı süreç varsa yalan söylemez mi?* — Söylerdi, ama damga tam da bunun için
  var: başka bir yazar dosyayı büyütürse damga değişir ve önbellek düşer. Aynı boyutta bir
  değişikliğin aynı saniyeye denk gelmesi gerekirdi; ve uygulama zaten tek süreç.
- *Asıl yavaşlık fotoğraflarsa, bu görev kullanıcının şikâyetini çözüyor mu?* — Tamamen çözmüyor
  ve öyle olduğunu söylemek yanlış olurdu. Çözdüğü şey ölçülebilir: liste artık üretim koşarken
  her iki saniyede beş dosya okumuyor. Kalan kısım yukarıda, kendi kararını bekliyor.
- *`stat` da Drive'a gitmiyor mu?* — Gidiyor, ama bir dosyanın üstverisini sormak ile dosyayı
  açıp okuyup ayrıştırmak aynı şey değil; ve üç okuma yerine bir okuma her hâlükârda daha az.
