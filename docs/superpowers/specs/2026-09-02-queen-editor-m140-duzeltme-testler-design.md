# Madde 140 · Düzeltme · Tur 1 (test) — Tasarım

**Kaynak:** [v6 yol haritası](../plans/2026-09-01-v6-roadmap.md), Madde 140
**Önceki turlar:** `92e0eea` *(kırmızı)*, `8a2f88b` *(yeşil)*
**Dal:** `feat/v6`
**Bu tur yalnız test yazar.**

## Neden bir düzeltme turu var

İlk iki turda **taban modelin kutusu yoktu**. Bunu kullanıcı istemedi, ben karar verdim: kodda
üç yerin `nova3DCGXL`'i şart saydığını görüp tasarımı ona uydurdum. Kullanıcı tasarımını tekrarladı
*(2 Eylül)*, ve karar onun:

> foto seçilince modeller **boş kutu** olarak görünsün, isteyen istediğini seçsin, seçmezse **hata
> fırlatalım**.

Madde numarası kaymıyor — aynı iş, düzeltilmiş hâli.

## Ne değişiyor

| | `8a2f88b` | Bu tur |
|---|---|---|
| Taban model | kutusuz, hep iner | **kendi kutusu**, boş gelir |
| Ek modeller | kutulu, boş gelir | aynı |
| Foto açık + hiç model yok | olamıyordu | **`assert` durduruyor** |
| Disk tabanı | `8` *(grup + taban model)* | `2` *(yalnız destek dosyaları)* |
| Liste adı | `PHOTO_EXTRA` | `PHOTO_MODELS` — artık *"ek"* değil |

Destek dosyaları — LoKr, Remacri, yolov9c, SAM — kutusuz kalıyor. Onlar model değil, grafiğin
dalları: FaceDetailer açılışta dedektörü ve SAM'i yüklüyor, LoRA düğüm `27`'de sabit açık.

## Taşınan sonuç, ve neden taşınıyor

`nova3DCGXL` uygulama tarafında üç yerde şart: grafiğin export'u düğüm `45`'te onu adıyla taşıyor,
üretici model seçilmemiş kareyi onunla üretiyor, `model_groups.py` onu foto grubunun şartı sayıyor.

Kutusu boş bırakılırsa **Üreticiler paneli "kurulu değil" der, oysa üretim çalışır.**

Bu turda düzeltilmiyor, ve gizlenmiyor da. Sebebi: düzeltmesi **uygulama kodu** — ya
`model_groups.py`'nin *"şu dosya"* yerine *"herhangi bir checkpoint"* sorması, ya da grafiğin
fallback'inin kalkması. İkisi de kendi kırmızısını isteyen ayrı bir iş, ve defterin maddesine
karıştırılırsa hangi değişikliğin neyi bozduğu ayrılamaz hâle gelir.

## Kırmızıya dönecek iddialar

1. **Her modelin bir kutusu, her kutunun bir satırı var.** Bugünkü eşleşme testi ayakta ama
   `PHOTO_EXTRA` adını okuyor ve taban modeli listede görmüyor; ikisi de değişiyor.
2. **Bütün kutular boş geliyor** — taban model dahil. Bugün taban modelin kutusu hiç yok.
3. **Foto açık ama hiç model seçilmemişse defter duruyor.** Bugün böyle bir kontrol yok, çünkü
   önceki tasarımda böyle bir durum doğamıyordu.
4. **Disk tabanı yalnız destek dosyalarını sayıyor.** Bugün `8` yazıyor ve içinde taban model var;
   o model artık seçime bağlı olduğu için tabanda duramaz — tahmin **büyük** kalırsa kullanıcı boş
   yere uyarı alır, ve bu maddenin tam tersi.
5. **İki model de indirilebiliyor.** Taban modelin version id'si artık `PHOTO_MODELS` satırında.

## Assert'in şekli, ve neden testi listeden türetiliyor

Kontrol CONFIG'de duruyor — kutuların yanında, `INSTALL_PHOTO`'nun assert'iyle aynı hücrede. Ama
kutu adlarını tek tek yazmak zorunda, ve bu bir kayma yeri: yeni model eklerken assert unutulursa
*"hiç model seçilmedi"* durumu sessizce geri gelir.

Bu yüzden test **beklediği satırı kutulardan üretiyor**: CONFIG'de bulduğu her `PHOTO_*` adını
sırasıyla dizip aradığı cümleyi kuruyor. Yeni bir kutu eklenip assert güncellenmezse test kırmızı
verir, ve mesajı beklediği satırı olduğu gibi basar.

## Kapsam dışı

- **`model_groups.py`, üretici, grafik, ön yüz, `dist`** — üstteki sebeple.
- **Üçüncü model.** Kullanıcı *"3 model"* dedi; bugün Illustrious tabanlı iki modelimiz var
  *(nova3DCG, novaOrange)*. Mekanizma sayıya bağlı değil — üçüncüsünün adresi geldiğinde tek satır
  ve tek kutu ekleniyor. Bu tur ikisiyle koşuluyor.
- **Ön yüzün zaman aşımı kırmızısı** — `8a2f88b`'nin notunda; kendi maddesi.
