# v11 Görev 1 — xAI anahtarı yoklaması: TEST döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 1/2 (testler)

Bu spec **yalnız testleri** tanımlıyor. İmplementasyon bir sonraki döngünün işi; bu döngü bittiğinde
takım kırmızı olacak ve kırmızılık tam olarak burada sayılan vakalar kadar olacak.

## Hangi davranış sınanıyor

Defter, dışarıya bakan her şeyi ağır işten önce yokluyor — GitHub token'ı assert'le, Civitai çerezi
1 KB'lık probe'la, disk ölçümle, GPU assert'le. **xAI anahtarı yoklanmıyor.** Bu yüzden anahtarın
ölü olduğu, kurulum + foto üretimi + kuyruğa video atma sonrasında öğreniliyor (2026-08-13 Colab
turu: `xAI HTTP 400 — Incorrect API key provided`).

Sınanacak davranış iki parça:

1. **Anahtar ilk saniyede yoklanır.** Geçersizse xAI'ın kendi cevabı basılır. Video kurulacaksa koşu
   durur — video prompt'unu yazan başka bir yol yok. Video kurulmayacaksa uyarır ve geçer.
2. **Anahtar kırpılır.** Colab'a yapıştırırken sona giren satır sonu `Bearer sk-...\n` yapıyor ve
   xAI 400 veriyor. Bugünkü hatanın olası sebeplerinden biri bu; bir daha kimseyi buraya düşürmemeli.

## Vakalar

### A · Gerçek testler — istemci (`test_xai_client.py`)

Çalışan kodu çalıştırıyorlar; kırmızı yanmaları koddaki eksikliği kanıtlıyor.

| # | Vaka | Beklenen |
|---|---|---|
| A1 | Anahtarın başında/sonunda satır sonu ve boşluk var (`"\n k-1 \n"`) | Header tam olarak `Bearer k-1` — istemci gövdeye kırpılmamış hiçbir şey koymaz |
| A2 | Anahtar yalnız boşluktan ibaret (`"   "`) | `NotConfigured` yükselir ve **hiç istek gönderilmez**; bugün gönderilir, çünkü `not "   "` yanlıştır |

A2'nin bugünkü davranışı sessiz bir tuzak: boş anahtar için özenle yazılmış "anahtar yok" mesajı
var, ama tek bir boşluk o mesajı devre dışı bırakıp kullanıcıyı xAI'ın 400'üne yolluyor.

### B · Defter testleri (`test_notebook_installs_the_producer_groups.py`)

**Bunlar doğrulama değil, kontrol listesi.** Defterin metnini okuyorlar, çalıştırmıyorlar — Colab
hücresi burada koşamaz. Yazdığımı yazdığımı doğruluyorlar; yoklamanın gerçekten çalıştığını ancak
kullanıcının Colab turu söyler. Yine de değerliler: birinin yoklamayı sessizce kaldırmasını ya da
ağır indirmeden sonraya taşımasını engelliyorlar.

| # | Vaka | Beklenen |
|---|---|---|
| B1 | Defter xAI anahtarını yokluyor | Yoklama defterde var |
| B2 | Yoklama **CONFIG hücresinde** | Yoklama, indirme hücresinde değil CONFIG'de geçiyor — "her şeyden önce" bu demek |
| B3 | Video kurulacak ve anahtar reddedildi | Koşu duruyor (video kurulumunun anahtara bağlandığı görülüyor) |
| B4 | Video kurulmayacak ve anahtar reddedildi | Uyarıp geçiyor — foto koşusu anahtarsız da çalışır |
| B5 | Yoklama başarısız | Mesaj xAI'ın **kendi cevabını** taşıyor, sebep uydurmuyor |
| B6 | Anahtar okunduğu yerde kırpılıyor | `XAI_API_KEY` secret'tan okunurken `.strip()` görüyor |

B2 bugün yazılamıyor: test dosyası bütün hücrelerin kaynağını tek metinde birleştiriyor, hangi
hücrede olduğunu ayırt edemiyor. Bu döngü **tek hücrenin kaynağını veren bir yardımcı** ekliyor —
bir testin sorabilmesi için gereken en küçük ekleme.

## Kapsam dışı

- **Yoklamanın hangi uç noktaya gideceği** implementasyon kararı; test onu değil, davranışı yazıyor
  (geçersiz anahtar → dur/uyar). Uç nokta seçimi bir sonraki spec'te gerekçesiyle veriliyor.
- **Anahtarın defterde de kırpılması.** B6 secret'ın okunduğu yeri sınıyor; istemcinin kendi
  kırpması A1 ile ayrı sınanıyor. İkisi ayrı sınır, ayrı sebep: biri yapıştırmayı temizliyor, öteki
  header'ının biçimini garanti ediyor.
- Anahtarın geçerliliği. Onu ancak xAI bilir; hiçbir test bilemez.

## Kırmızı commit

Sekiz test eklenir, hepsi düşer. Takım bu commit'te kırmızıdır ve commit mesajı bunu açıkça söyler —
aynı dalda çalışan başka bir oturum bu commit'i çekerse kırık bir takımla karşılaşacak, mesaj onun
için var. `xfail`/`skip` ile yeşile boyanmaz: kırmızılık bu döngünün ürünü.

## Bitti sayılır

`python -m pytest queen-editor/backend/tests -q` sekiz düşen test gösteriyor, düşme sebepleri
yukarıdaki tabloların beklediği sebepler — yani hiçbiri yazım hatasından ya da eksik yardımcıdan
düşmüyor.
