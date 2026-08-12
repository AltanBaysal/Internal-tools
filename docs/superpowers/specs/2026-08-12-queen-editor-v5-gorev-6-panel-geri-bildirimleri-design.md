# Queen Editor v5 · Görev 6 — Panel geri bildirimleri ayrışır · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 2, Görev 6 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
15, 16, 17, 18 · **Tür:** yalnız ön yüz.

## Neden

Panelin butonunun altındaki tek satır bugün **iki ayrı olayı** aynı cümleyle anlatıyor. Kullanıcı
bozuk bir prompt listesiyle butona basınca ekranda aynı anda iki kırmızı beliriyor: kutunun altında
"Format hatası — liste okunamadı", butonun altında "Kuyruğa eklenemedi". Hiçbir şey kuyruğa
yazılmaya çalışılmadı — istek kapıda döndü. Kuyruk suçlanıyor, sebep başka yerde duruyor.

Kaynağı basit: panel, sunucudan sayı dönmeyen **her** isteği ayrım yapmadan "reddedildi" sayıyor.
Bu görev o ayrımı koyuyor — sunucu hangi alanın yanlış olduğunu söylediyse cevabı o alanın kendi
cümlesidir; kuyruk cümlesi yalnız kuyruk gerçekten almadığında çıkar.

## Bugün ne var

| Durum | Kutunun altı | Butonun altı |
|---|---|---|
| Format hatası | "Format hatası — liste okunamadı" | "Kuyruğa eklenemedi" (sola yaslı) |
| Varyant hatası | *(yok — kutunun hata hâli yok)* | "Kuyruğa eklenemedi" (sebep hiçbir yerde) |
| Kuyruk yazamadı | — | "Kuyruğa eklenemedi" (sola yaslı) |
| Başarılı ekleme | — | tek parça yeşil kart: "✓ 4 kare kuyruğa eklendi", 4 sn |

## Ne olacak

| Durum | Kutunun altı | Butonun altı (hepsi ortalı) | Madde |
|---|---|---|---|
| Format hatası | kısa "Format hatası" | "Format hatası — liste okunamadı" | 15 |
| Varyant hatası | *(yok — kutu temiz kalır)* | sunucunun kendi cümlesi | 15 |
| Boş liste | *(yok — kısaltılacak bir şey yok, kutu yalnız kızarır)* | "Prompt listesi boş." | 15 |
| Kuyruk yazamadı | — | "Kuyruğa eklenemedi — tekrar dene" | 16 |
| Başarılı ekleme | — | iki parça yeşil kart: ✓ · "4 kare kuyruğa eklendi", **10 sn** | 17 |

Değişmeyenler: kutunun kırmızı çerçevesi, yazmaya başlayınca hatanın silinmesi, ya hepsi ya hiçi
kuralı, alanların açık kalması, akan kuyruğun etkilenmemesi, butonun ara hâli "Ekleniyor…".

## Kararlar

### 1. Ayrım "sunucu bir alan adı verdi mi" sorusudur

Sunucu reddettiği isteğe hangi alanın suçlu olduğunu ekliyor (`prompts` · `variants`). Panel bu
alanı zaten alıyor ama yalnız kutuyu kızartmak için kullanıyor. Kural tek cümleye iniyor:

> **Sunucu bir alan adı verdiyse butonun altındaki satır o alanın cümlesidir; vermediyse "Kuyruğa
> eklenemedi — tekrar dene"dir.**

Böylece "Kuyruğa eklenemedi" gerçekten kuyruğun almadığı durumu anlatır — madde 15'in istediği
ayrım budur.

### 2. Kural bütün alanlara işler, yalnız prompt'a değil

Madde 15 format hatasını anlatıyor ama sebebi alan-bağımsız: kapıda dönen istek kuyruğu suçlamamalı.
Varyant hatasını dışarıda bırakmak, aynı yanlışı bir alan için korumak olurdu ve o özel durumun
arkasında hiçbir gerekçe kalmazdı.

Varyant **kutusunun** hata hâli yine yok (tasarımın kendi kuralı: aralık dışı değer yazılamaz, o
yüzden kutuya hata çizilmez) — değişen tek şey, sebebin artık butonun altında **söyleniyor**
olması. Bugün hiçbir yerde söylenmiyor.

### 3. Kutunun altına cümlenin başı gider, tamamı değil

Tasarım kutunun altında kısa "Format hatası", butonun altında tam "Format hatası — liste okunamadı"
istiyor. Sunucunun alan cümleleri zaten `<kısa> — <ayrıntı>` biçiminde yazılmış, dolayısıyla kısa
biçim **uzun tirenin öncesidir**; ayrı bir metin tablosu tutmaya gerek yok, sunucu tek doğru olarak
kalır.

Tirenin olmadığı cümlede (örn. "Prompt listesi boş.") kısaltılacak bir şey yoktur: kutu **yalnız
kızarır**, cümle butonun altında durur. Aynı cümleyi üst üste iki kez yazmak bilgi eklemez.

### 4. Satır, kutunun kırmızısıyla aynı anda doğar ve aynı anda ölür

Kutunun kırmızı çerçevesi bugün gönderime değil, sunucunun verdiği alan adına bakıyor — sayfa o
hatayla açılsa da kutu kırmızı olurdu. Butonun altındaki satır da aynı şeye bakar; iki işaretin
farklı anlarda doğması, aynı olayın iki kere anlatılmasının başka bir biçimi olurdu.

Ölümü de aynı: yazmaya başlamak hatayı siliyor. Bugün "Kuyruğa eklenemedi" bunun dışında —
gönderimden sonra tuşa basmak onu silmiyor. Ayrım konulduğunda bu görünür bir arızaya dönerdi
(alan hatası silinir, altından eski kuyruk cümlesi çıkar), o yüzden **yazmak her iki satırı da
siler**.

### 5. Yeşil kart iki parçadır ve 10 saniye kalır

Madde 17: kart ayrı bir onay işareti + metin olarak ikiye ayrılır. Bugün "✓" metnin içinde bir
karakter; ayrı öğe olunca kendi rengini ve boyunu alabilir ve metinle birlikte satır sonuna
sarmalanmaz.

Süre kullanıcı kararıyla **10 saniye** — tasarımın kendi iki değeri de ("birkaç saniye" ve "2 sn")
geçersiz.

### 6. Madde 18'den iş çıkmıyor

Madde 18 (`zayıf sinyal`, tek yol) model listesi hatasının "kuyruk panelindeki ölümcül hata kartıyla
aynı kalıba" girmesini istiyor. Kalıp **zaten aynı**: iki kart da aynı bileşendir
(`shared/StatusErrorCard.jsx`) — aynı kırmızı çerçeve, aynı saydam kırmızı zemin, aynı uyarı ikonu,
başlık + sunucunun ham satırı.

Geriye tek nominal fark kalıyor: kartın hangi panelde durduğu. Tasarım bunu **söylemiyor** (maddenin
kendi notu), ve kartı model kutusunun yanından almak onu anlattığı alandan koparırdı.

Davranış tarafında da iş yok: madde `görsel` damgalı, "ölümcül" sözcüğü kartın *görünümünü*
anlatıyor. Model listesi okunamazken kuyruğa eklemenin açık kalması bilinçli bir karardır (liste
düştü, kuyruk düşmedi) ve bu görevde korunur.

Yol haritasının zayıf sinyal kuralı gereği madde **"iş çıkmadı" diye kapanır**, gerekçesi burada.

## Nasıl görülür

1. Prompt kutusuna bozuk bir liste yaz, Kuyruğa ekle'ye bas: kutu kızarır, altında "Format hatası";
   butonun altında ortalı "Format hatası — liste okunamadı". **"Kuyruğa eklenemedi" hiç çıkmaz.**
2. Kutuyu boşalt ve bas: kutu kızarır (altında yazı yok), butonun altında "Prompt listesi boş.".
3. Kuyruk gerçekten yazamadığında butonun altında ortalı "Kuyruğa eklenemedi — tekrar dene".
4. Başarılı eklemede yeşil kart iki parçalı çıkar ve 10 saniye durur.
5. Yazmaya başlayınca kutunun kırmızısı da butonun altındaki satır da gider — hangi satır olursa
   olsun.

## Testler

Hepsi ön yüz; arka uca dokunulmaz.

| Dosya | Test |
|---|---|
| `GeneratePanel.test.jsx` | format hatasında "Kuyruğa eklenemedi" çıkmıyor · kutunun altı kısa, butonun altı tam cümle · tiresiz cümlede kutunun altı boş, butonun altı dolu · varyant hatası butonun altında söyleniyor ama kutu temiz · kuyruk yazamadığında satır "— tekrar dene" ile · yeşil kart iki parça ve 10 sn · 4 sn'de kaybolmuyor |

Var olan iki test yeni davranışa göre yazılır: "has no error state of its own" artık **kutunun**
temiz kaldığını söyler (panelin sustuğunu değil), ve onay kartının süresi 4 sn'den 10 sn'ye çıkar.

## Kapsam dışı

- Kuyruk panelinin kendi hata ve bitiş kartları (madde 37-39, 42, 43) — **Görev 10**.
- Kayıtlı modelin kurulu olmaması uyarısı (madde 19) — *korunanlar* listesinde, iş yok.
- Model alanının yükleme/boş hâlleri (madde 20) ve prompt örneği (madde 21) — *korunanlar*.
- Panelin başlığı, buton adı ve ikonu — **Görev 5**'te yapıldı.

## Riskler

- **Varyant hatasının artık görünmesi** (karar 2) var olan bir testin niyetini değiştiriyor. Test
  siliniyor değil, daraltılıyor: iddia "panel susar"dan "kutu temiz kalır"a iner — tasarımın
  gerçekten söylediği şey bu.
- **Kısa biçimin tireden okunması** (karar 3) sunucunun cümle biçimine bağlı. Biçim bozulursa kutu
  tam cümleyi gösterir — bilgi kaybı olmaz, yalnız kısalık kaybolur.
