# Queen Editor v9 · Görev 1 — Kurulum uygulamadan kalksın

**Tarih:** 2026-08-13 · **Yol haritası:** [v9](../plans/2026-08-13-queen-editor-v9-roadmap.md) · Görev 1
**Karar sahibi:** kullanıcı (2026-08-13).

## Problem

Colab turunda üç üreticinin üçü de kurulamadı. Uygulamanın indiricisi Civitai'nin yönlendirmesinde
403 alıyor, ses motorunun kütüphanesi kurulup süreçte görünmüyor. `collab-toolbox`'ta yıllardır
çalışan bir indirme hücresi varken, uygulamaya ikinci bir indirici öğretmeye çalışıyoruz.

## Karar

**Uygulama artık hiçbir şey indirmez.** İndirme, kurulum ve iptal ile ilgili ne varsa backend'den
ve arayüzden silinir. Kurulum Colab defterinin işi olur (Görev 2).

Bu, v7 ve v8'in yönünü tersine çeviriyor. Sebebi kayda geçsin: v7/v8 panelin yalan söylemesini
çözmek için kurulumu tek yere topladı, ve o tek yer çalışmadı. Kullanıcı çalışmayan yeri düzeltmek
yerine çalışan yöntemi kullanmayı seçti.

## Ne kalıyor

**Tek soru kalıyor: "bu üretici kurulu mu?"** Cevabı da bugünkü gibi diskteki dosyalara bakmak.
Panel bunu göstermeye devam eder — kullanıcı neyin hazır olduğunu uygulamadan görebilmeli, yoksa
üretime basıp kapalı kapıya çarpar.

**Cevap uygulama açılırken verilir** (kullanıcı kararı): defter modelleri Flask'tan önce kurar, yani
uygulama ayağa kalktığında her şey zaten yerindedir. Uygulama açıkken defterde kurulum yapılmaz, o
yüzden panelin durumu tazelemesi gerekmez — ne yoklama, ne yenile düğmesi. Durum bir kez okunur.

**Arayüz tasarımı değişmiyor** (kullanıcı kararı): satırlar, kart, "Kur" düğmesi — hepsi yerinde
durur. Değişen tek şey düğmenin ne yaptığı: artık kurulum başlatmaz, sunucuya istek bile atmaz;
şunu söyler:

> Bu üretici Colab defterinden kurulur — app.ipynb'yi çalıştır.

Cümle, bugün hatanın göründüğü yerde görünür; yeni bir kutu, yeni bir yerleşim yok.

Aynısı üretim panellerindeki kurulum kartı için de geçerli: kart ve düğmesi durur, basınca aynı
cümleyi söyler.

Kaldırılan tek parça, panelin "Kurulum uzun sürebilir, arkada sürer" onay penceresi: onaylanacak
bir kurulum kalmadı, ve o pencerenin "Kur"una basmak "burada kuramazsın" cümlesine çıkardı.

## Ne gidiyor

| Ne | Neden |
|---|---|
| İndirme servisi | Uygulama indirmiyor |
| Kurulum ve iptal kullanımları, kurulum işçisi | Kurulacak bir şey yok |
| Ses kütüphanesini kuran sınıf | Aynı |
| Kurulum ve iptal uçları | İstemci artık çağırmıyor |
| Civitai çerezi ayarı | Uygulamanın anahtara ihtiyacı kalmadı |
| Model adresleri (`url`, `auth`) | Adresi bilen tek yer defter olmalı; uygulamada kalan bir adres, kimsenin kullanmadığı ikinci bir doğru olur |

Model **adları** kalıyor: "kurulu mu" sorusunun cevabı onlarla veriliyor.

## Değişen kural

[FOUNDATION 9](../../../queen-editor/FOUNDATION.md) tersine dönüyor: *uygulama kendi üreticilerini
kurar* değil, **defter kurar, uygulama yalnız ne olduğunu söyler.** Maddenin kendisi ve onu
koruyan test ("defter model indirmez") kalkar — bir kuralı tersine çevirirken onu bekleyen testi
bırakmak, ilk koşuda kırmızıya basmak demek.

Bunun bedeli açıkça yazılsın: v7'nin çözdüğü sorun geri geliyor. Panel "kurulu mu" sorusuna bakarak
cevap veriyor, kurulumu ise başka bir yer yapıyor. İkisi ancak temiz makinede ayrışır. Fark şu: v7
öncesinde panel *boş bir listeye* bakıp "kurulu" diyebiliyordu; bundan sonra hep gerçek dosyalara
bakacak, yani yanlış cevap veremeyecek — sadece cevabı düzeltme gücü olmayacak.

## Kullanıcının kaybettiği

- Uygulamadan kurulum yok: temiz makinede önce defter koşar, sonra üretim.
- İlerleme ve iptal yok.
- Bir eksik dosyayı uygulamadan tamamlamak yok — defter baştan koşar, olan dosyaları atlar.

## Test

Kalan davranış test edilir: panel üç satırı doğru sırayla veriyor, her satır kendi grubuna bakarak
kurulu olup olmadığını söylüyor, grubu tanımsız olan kurulu görünmüyor. Ön yüzde: kurulu olan "✓
kurulu" diyor, kurulu olmayanın "Kur" düğmesi duruyor, ve ona basınca **sunucuya istek gitmeden**
Colab cümlesi çıkıyor.

Silinen her şeyin testi de silinir; kalan testler sahte dosyalarla koşar, ağ yok.

## Dokunulan dosyalar

**Silinecek:** `services/download/`, `features/producers/runner.py`,
`domain/usecases/install_producer.py`, `domain/usecases/cancel_install.py`,
`data/pip_libraries.py`, `tests/test_fetcher.py`, `tests/test_model_install_is_the_apps_job.py`

**Yeniden yazılacak:** `domain/model_groups.py` (adlar kalır, adresler gider),
`domain/ports.py` (tek port), `domain/usecases/list_producers.py` (yalnız kurulu mu),
`presentation/routes.py` (tek uç), `backend/config.py`, `backend/main.py`,
`tests/test_producers.py`, `tests/test_producers_routes.py`

**Ön yüz:** `InstallCard.jsx`, `ProducersPanel.jsx`, `useProducers.js`, `shared/api.js` ve testleri

**Belgeler:** `FOUNDATION.md` (madde 9), `CODE-STANDARD.md`, `CLAUDE.md`, `README.md`
