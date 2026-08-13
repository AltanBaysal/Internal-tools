# Queen Editor — Yol Haritası v8

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** 3/3 bitti, push ve Colab turu bekliyor.
**Öncesi:** [v7](2026-08-13-queen-editor-v7-roadmap.md) — 12 görev kapandı.
**Kaynak:** kullanıcı kararı (2026-08-13), v7'nin Colab turundan çıktı.

## Neden bu koşu var

v7 defterin **model** indirmesini kaldırdı, ama defter hâlâ MMAudio kütüphanesini klonlayıp
kuruyor. Kullanıcı Colab'da o satırları görünce sordu ve kararını verdi: **bu kurulum da defterde
olmasın, gerektiğinde yapılsın.** Yani ses motorunun kütüphanesi, ses üreticisi kurulurken kurulur.

Bir de v7'de eklediğim "Modeller — burada inmez" hücresi kalkıyor: olmayan bir şeyi anlatan bir
hücre, defterde yer tutmaktan başka iş görmüyor.

## Kararlar (kullanıcı, 2026-08-13)

1. **Kütüphaneyi Üreticiler panelindeki "Kur" kurar.** İlk ses işinin kendi kurması elendi: kimse
   düğmeye basmadığı için kurulum üretimin ortasında olur, ve o sırada ekran ilerlemiyormuş gibi
   görünür. Ses için kural artık foto ve videoyla aynı: kurmadan iş başlamaz.
2. **Kurulumdan sonra uygulama kütüphaneyi canlı kullanmayı dener.** Olmazsa panel açıkça
   "uygulamayı yeniden başlat" der (Colab'da Flask hücresini tekrar çalıştırmak). Her kurulumdan
   sonra koşulsuz yeniden başlatma istemek elendi — çoğu turda gerekmiyor.
3. **Defterin adı "Queen Editor — Colab kurulumu".** Bölüm numarası yok; defterin işi kurmak ve
   sunucuyu açmak, üretim uygulamanın içinde.

## Kapsam sınırı

- **ComfyUI ve custom node'lar defterde kalır.** Onlar isteğe bağlı değil: ComfyUI ayağa kalkmadan
  uygulama foto da video da üretemez, ve node'lar ComfyUI'nin başlangıç şartı. MMAudio'yu ayıran
  şey, yalnız ses işi geldiğinde gerekmesi.
- **Yeni bir yetenek yok.** Kurulumun yeri değişiyor, davranışı değil.

## Kullanıcıya söylenen risk

Kütüphane kurulumu uygulamanın içine girince, kurulum hatası artık defterin fail-loud hücresinde
değil, bir isteğin içinde patlar. Kullanıcı bunu bilerek istedi; karşılığında defter yalnız
uygulamanın **koşması** için gerekli olanı kuruyor, ses motorunu kullanmayan bir tur onu hiç
kurmuyor.

## Görevler

### Görev 1 · Ses motoru gerektiğinde kurulsun

**Bulgu:** Defter MMAudio'yu her Run all'da klonlayıp `pip install -e` ediyor — sesi hiç
kullanmayan bir tur bile.

**Ne olacak:** Ses üreticisinin kurulumu kütüphaneyi de kapsar. Panelden "Kur"a basınca önce
kütüphane, sonra ağırlıklar gelir; ekran hangisinde olduğunu söyler. "Kurulu mu" sorusunun cevabı
da kütüphaneyi sayar — ağırlık dosyası yerinde ama kütüphane yoksa ses üreticisi kurulu değildir.
Kurulum bitince uygulama kütüphaneyi canlı kullanmayı dener; göremezse panel yeniden başlatmayı
ister.

**Bağımlılık:** Yok.

**Testler ne diyecek:**
- Ses kurulumu kütüphaneyi ağırlıklardan **önce** yapar; kütüphane zaten varsa tekrar kurulmaz.
- Kurulum sırası ekrana yansır: kütüphane adımındayken panel onu söyler, dosya adımındayken dosyayı.
- Kütüphane yoksa ses üreticisi "kurulu" görünmez; ağırlık dosyası dursa bile.
- Kütüphane kurulumu hata verirse ağırlıklara geçilmez ve hata panelde kendi sözleriyle görünür.
- Kurulumdan sonra kütüphane hâlâ görünmüyorsa panel yeniden başlatmayı isteyen cümleyi taşır.
- Foto ve video üreticilerinin kurulumu bugünkü davranışını aynen sürdürür.

**Test edilmeyen tek parça:** `git`/`pip` komutunu gerçekten çalıştıran sınıf — ComfyUI istemcisi
ve ffmpeg dışa aktarıcısı gibi dış dünya. Sahtesi yalnız sahteyi test ederdi
([CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)); kararlar onun üstündeki katmanda.

**Bitti sayılır:** Temiz makinede defter MMAudio'ya hiç dokunmuyor; ses üreticisi panelden tek
tıkla kuruluyor ve bir ses işi baştan sona geçiyor.

### Görev 2 · Defterden ses hücreleri ve model notu kalksın

**Bulgu:** Defterde MMAudio kurulum hücresi, onun markdown başlığı ve "Modeller — burada inmez"
notu duruyor.

**Ne olacak:** Üçü de silinir. Defterde kalan kurulum ComfyUI, custom node'lar ve ffmpeg —
uygulamanın koşması için gerekli olanlar.

**Bağımlılık:** Görev 1 — önce uygulama kurabilir olmalı, yoksa hiç kimsenin kurmadığı bir ara
durum kalır.

**Testler ne diyecek:** Defterde `MMAudio` geçen tek satır yok. Bu, v7'nin "model indirmeyi defter
yapmaz" testinin yanına aynı biçimde yazılır — bir daha eklenirse test söyler.

**Bitti sayılır:** Defteri Run all ile koşan biri ses motoruna dair hiçbir kurulum görmüyor.

### Görev 3 · Defterin ve README'nin adı bugünü anlatsın

**Bulgu:** Defterin başlığı *"Queen Editor — Tek foto (Bölüm 4)"*. Ne "tek foto" ne "Bölüm 4"
doğru: uygulama üç katman üretiyor, dizi export ediyor, üreticilerini kendi kuruyor. README aynı
eskimeyi taşıyor ("two-screen web UI", "Part 1…4").

**Ne olacak:** Başlık **"Queen Editor — Colab kurulumu"** olur; giriş paragrafı ve README uygulamanın
bugün ne olduğunu söyler; bölüm numaraları kalkar — kapanmış roadmap'lerin sırası zaten `docs/`
altında.

**Bağımlılık:** Görev 2 (aynı metinlere dokunuyor).

**Testler ne diyecek:** Buranın testi yok; değişen şey metin, ve bir başlığın doğru olup olmadığını
test değil okuyan anlar. Görev 1 ve 2'nin testleri koşuyor olacak.

**Bitti sayılır:** Defteri ilk kez açan biri ne yaptığını başlıktan doğru anlıyor.

## Nasıl çalışacağız

v7'nin aynısı: görev başına **spec → plan → full TDD → tek commit**. Test önce yazılır, kırmızı
görülür, sonra kod. Ön yüz değişirse `dist/` aynı commit'te. Komutlar:
`python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend -- --run`,
`npm run build --prefix queen-editor/frontend`.

## Koşunun sonu

Push, sonra temiz bir Colab turu: Run all → Üreticiler'den üçünü kur → foto, video, ses üret →
export.
