# v14 · Görev 23 — Proje adı değiştirme · **test turu**

**Kaynak:** yol haritası 23. madde · İstek 10 · tasarım v4 fark listesi 1, 2, 3, 4 ·
40, 41, 42. kararlar.

F bölümünün ilk maddesi ve koşunun tek yeni **davranışı** — geri kalanı hep var olanı düzeltiyordu.

## İstek ne diyor

> *"Bugün proje oluşturuluyor ve siliniyor; adı değiştirilemiyor. Yanlış yazılan ya da sonradan
> anlamsızlaşan bir ad projeyle birlikte kalıyor."*
>
> *Uygulayan bilsin:* **proje bir Drive klasörü ve adı her şeyin adresi.** Adı değiştirmek klasörü
> değiştirmek demek — **üretim sürerken ne olacağı** ve **daha önce dışa aktarılmış işlerin ne
> olacağı** spec'in cevaplayacağı sorular.

İki soru da burada cevaplanıyor.

## 40 · Klasör taşınır, kopyalanmaz

Yeni bir klasör açıp içini kopyalamak değil, klasörün kendisinin adını değiştirmek. Sebep tek
cümleyle: **kopyalamak yarıda kalabilir.** Bir projede binlerce dosya olabilir ve Drive üzerinden
kopyalama dakikalar sürer; yarıda kesilirse ortada iki eksik klasör kalır ve hangisinin doğru
olduğunu kimse bilemez. Ad değiştirme dosya sisteminin kendi atomik işlemi: ya olur ya olmaz.

Sonucu: **kare adları, plan, kayıt, ayarlar ve dışa aktarımlar olduğu yerde kalıyor** — hepsi
klasörün içinde duruyor ve klasörle birlikte taşınıyorlar. Hiçbiri yeniden yazılmıyor.

## 41 · Koşan iş adı her turda yeniden okur, ve yazarken kilit tutar

Bugün koşan iş proje adını **bir kez** alıyor ve turlar boyunca aynı dizgeyi kullanıyor
(`make_job`'ın kapanışı). Klasör altından taşınırsa bir sonraki tur `plan_store.read(eski ad)` diyor,
dosya yok, iş çöküyor ve koşu "error" ile bitiyor. Yani bugünkü hâliyle ad değiştirmek üretimi
öldürür.

Çözüm iki parçalı:

**Ad bir tutamaktan okunuyor.** İş, her turun başında adı yeniden soruyor. Ad değişmişse o tur yeni
klasörde çalışıyor — kuyruk durmuyor, sıra bozulmuyor, hiçbir kare kaybolmuyor.

**Yazma anı kilitli.** Turun ortasında değişen bir ad tek bir yerde tehlikeli: `write_bytes` ve
`append_line` **eksik klasörü kendileri açıyor**. Eski adla çözülmüş bir yazma, taşınmadan sonra
düşerse yanına hayalet bir klasör açar ve tek dosyayı oraya bırakır. Bu yüzden yazma tutamağın
kilidini alıyor, ad değiştirme de aynı kilidi alıyor: bir yazma taşınmanın iki yakasına düşemiyor.

Bekleme süresi bir dosya yazma kadar — milisaniyeler. Render kilidin dışında kalıyor, yani üç
dakikalık bir video kimseyi bekletmiyor.

**İşçinin damgası da adı takip ediyor.** `PhotoRunner` durumuna proje adını basıyor ve ekran
`job.project === project` diye karşılaştırıyor. Damga güncellenmezse yeniden adlandırılmış proje
kendi koşusunu tanımaz.

## 42 · Eski dışa aktarımlar taşınır, adları değişmez

Dışa aktarım klasörü projenin **içinde** duruyor, dolayısıyla klasörle birlikte taşınıyor ve
kaybolmuyor.

Ama birleştirilmiş dosyanın adı `{proje}.mp4` — yani **eski bir dışa aktarım, yapıldığı günkü adı
taşımaya devam ediyor.** Yeniden yazılmıyor: o dosya o adla yapıldı, ve kullanıcı onu indirmiş
olabilir. Bundan sonra yapılan dışa aktarımlar yeni adı alıyor.

## Ekranda ne oluyor

| | |
|---|---|
| **Nereden** | Kartın sağ üstünde, çöp ikonunun solunda nötr bir kalem *(fark 1)* |
| **Pencere** | 380px, 20px iç boşluk, başlık "Projeyi yeniden adlandır", etiket "PROJE ADI", sağ altta "Vazgeç" ve vurgulu "Kaydet" *(fark 4)* |
| **Alan** | Mevcut adla dolu ve **seçili** — bir tuşa basmak adı baştan yazmaya başlar |
| **Çakışma** | Kaydet'e basılınca alan kırmızıya döner, altında "Bu ad zaten kullanılıyor. Başka bir ad dene." *(fark 2)* |
| **Temizlenme** | Yazmaya başlayınca uyarı gider |
| **Yıkıcı değil** | Onay penceresi yok, kırmızı düğme yok, çöp ikonu yok *(fark 3)* |

**Pencere yeni proje penceresinin aynısı.** Aynı olduğu için ikinci bir kopyası yazılmıyor:
`NewProjectModal` genelleşip `NameModal` oluyor — başlık, açılış değeri, düğme yazıları ve genişlik
dışarıdan geliyor. Yeni proje penceresi bugünkü 400 pikselinde kalıyor; 380'e inmesi 24. maddenin
işi (fark 6).

**Kaydet pasifleşmiyor.** Yol 2 bunu çizimden okumuş; tasarımın yazılı kuralı söylemiyor, ve 16.
maddenin panel hata dili de aynı yönde: buton basılmadan önce sakin durur, basınca sebep çıkar.

**Projenin kendi adını kaydetmek hata değil** — fark 2'nin kendi notu. Klasör taşınmıyor, pencere
kapanıyor.

## Kapsam dışı

- **Karttaki iki düğmenin ölçüsü ve silmenin yıkıcı standarda geçmesi** (fark 5) 24. madde.
- **Yeni proje penceresinin 380'e inmesi** (fark 6) 24. madde.
- **Kayma göstergesi ve silme onayının cümle sırası** (fark 8, 9) 24. madde.
- **Boş listenin ikinci satırı** (fark 7) 31 kararla kapanan maddeler arasında.

## Yazılacak testler

### Motor — `test_drive_storage.py` (2)

| # | Ne diyor |
|---|---|
| 1 | Klasörün adı değişiyor, içindekiler taşınıyor |
| 2 | Ad başkasındaysa taşınmıyor ve ikisi de yerinde kalıyor |

### Motor — `test_project_usecases.py` (5)

| # | Ne diyor | Fark |
|---|---|---|
| 3 | Yeniden adlandırma klasörü taşıyor | 1 · karar 40 |
| 4 | Kural kıran ad kuralın kendi cümlesiyle reddediliyor | 1 |
| 5 | Başkasının adı "Bu ad zaten kullanılıyor" diyor | 2 |
| 6 | Projenin kendi adı hata değil | 2 |
| 7 | Olmayan proje reddediliyor | — |

### Motor — `test_frame_queue.py` (2)

| # | Ne diyor | Karar |
|---|---|---|
| 8 | Koşan iş her turda adı yeniden okuyor, taşındıktan sonra yeni klasörde çalışıyor | 41 |
| 9 | İşçinin damgası da yeni adı taşıyor | 41 |

### Motor — `test_projects_routes.py` (3)

| # | Ne diyor |
|---|---|
| 10 | Yol yeni adı geri veriyor |
| 11 | Çakışma 409 ve kuralın cümlesi |
| 12 | Olmayan proje 404 |

### Ön yüz — `ProjectsScreen.test.jsx` (5)

| # | Ne diyor | Fark |
|---|---|---|
| 13 | Her kartta çöpün solunda bir kalem var | 1 |
| 14 | Kalem pencereyi mevcut adla dolu ve seçili açıyor | 1 · 4 |
| 15 | Kaydet adı değiştiriyor ve liste yeniden okunuyor | 1 |
| 16 | Kullanılan ad alanın altında söyleniyor, alan kırmızıya dönüyor | 2 |
| 17 | Yeniden adlandırmada onay penceresi yok | 3 |

### Ön yüz — `NameModal.test.jsx` (2 yeni)

`NewProjectModal.test.jsx` bu adı alıyor; dokuz testi olduğu gibi taşınıyor.

| # | Ne diyor |
|---|---|
| 18 | Pencere verilen değerle açılıyor ve alan seçili geliyor |
| 19 | Başlık, düğme yazıları ve genişlik dışarıdan geliyor |

### Ön yüz — `api.test.js` (1)

| # | Ne diyor |
|---|---|
| 20 | `renameProject` projenin kendi adresine yeni adı yolluyor |

**Motorda 12 yeni test: 697 → 709. Ön yüzde 8 yeni test: 519 → 527.** Hepsi kırmızı.

## Bitti sayılır

Dört komut da koşuyor; queen-editor'ün Python takımında **12**, frontend takımında **8** kırmızı
duruyor. Testler kırmızı commit ediliyor.
