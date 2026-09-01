# Defterin adı aracının adı olsun · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-09-01-defter-adi-testler-design.md](2026-09-01-defter-adi-testler-design.md) ve o
turun kırmızıları.
**Dal:** `feat/defter-adi` *(tur 1'in üstüne)*.

## Testlerin tarif ettiği iş

Tur 1'de 21 kırmızı duruyor ve hepsi tek bir şeyi bekliyor: `queen-editor/app.ipynb` dosyasının
`queen-editor/queeneditor.ipynb` olması. Yirmisi taşımanın kendisiyle yeşile döner *(defter testinin
tamamı, çünkü `NOTEBOOK` artık oraya bakıyor)*, biri de kullanıcıya gösterilen cümlenin yeni adı
söylemesiyle.

Ama testlerin göremediği bir iş daha var, ve asıl dikkat isteyen kısım o: **deponun her yerinde
`app.ipynb`'yi adıyla anan cümleler.** Hiçbir test onları okumuyor, ve taşımadan sonra hepsi var
olmayan bir dosyayı işaret eder hâle gelir. Bir belge yanlış dosya adı veriyorsa okuyanı boşa
gönderir — CLAUDE.md'nin *"bir yorum yalnız bugün doğru olanı söyler"* kuralının tam konusu bu.

## Adı anan yerler, ve her birinin neden ellendiği

| Yer | Ne diyor |
|---|---|
| Defterin kendi markdown hücresi | *"Bu `app.ipynb`'yi Colab'a yükle"* — kullanıcıya yükleyeceği dosyayı adıyla söylüyor |
| [useProducers.js](../../../queen-editor/frontend/src/features/producers/useProducers.js) | Kur'un bastığı cümle; ekranda görünen tek yönlendirme |
| [README.md](../../../queen-editor/README.md) | Kurulumun ilk adımı: Colab'a hangi dosyayı yükleyeceği |
| [CODE-STANDARD.md](../../../queen-editor/CODE-STANDARD.md) | Üç yerde: kurulum hücrelerinin nereye kopyalandığı, model adreslerinin nerede durduğu, `DRIVE_FOLDER`'ın hangi hücrede olduğu |
| [config.py](../../../queen-editor/backend/config.py) · [storage.py](../../../queen-editor/backend/services/drive/storage.py) | Drive kökünü kimin seçtiğini anlatan yorumlar — okuyanı defterin CONFIG hücresine yolluyorlar |

## queen-agent'ın yorumu artık yanlış

Tur 1, o yorumu bilerek bırakmıştı: taşıma olmadan hâlâ doğruydu. Taşımadan sonra
*"queen-editor's notebook is called that"* cümlesi gerçeği anlatmıyor.

Yerine geçen şey bir düzeltme değil, bir sadeleşme: **gerekçe artık testin kendi docstring'inde**
duruyor ve iki araçta da aynı. `NOTEBOOK`'un üstünde ikinci bir kopyası olması, CLAUDE.md'nin
kopya yasağının tarif ettiği durum — kopya bayatlayan taraftır, ve bugün bayatlayan da tam olarak o
oldu. Yorum kalkıyor.

## Derlenmiş ön yüz

`COLAB_INSTALL` kullanıcıya görünen bir metin, yani `frontend/dist` içine derlenmiş hâlde de duruyor
ve defter depoyu klonlayıp `dist`'i olduğu gibi servis ediyor. CLAUDE.md: **kaynak ile `dist` aynı
commit'te.** Derlemeden commit'lenirse Colab'da eski cümle görünür — ve o cümle var olmayan bir
dosya adı söyler.

## Ayakta kalması gerekenler

Dört test komutunun tamamı yeşil, ve `test_dist_is_committed.py` dahil.

## Bilerek yapılmayanlar

- **`docs/superpowers/` altındaki geçmiş plan ve spec'ler.** O günün kaydı; geriye dönük yazılmaz.
- **`git mv` yerine sil-yarat.** Taşıma `git mv` ile, ki geçmiş dosyayla birlikte gelsin.
- **Defterin içeriğine ad dışında dokunmak.** Başlığı *(`# Queen Editor — Colab kurulumu`)* zaten
  doğru; değişen tek şey kullanıcıya söylenen dosya adı.
